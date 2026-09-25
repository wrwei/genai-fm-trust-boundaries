"""Additive physical driver derived from v2; see physical-driver.diff for exact changes.
Runtime receives replies on serial simulation ticks. No real-time network claim.
"""
from dataclasses import asdict
import math
from binding import Runtime, Core, SourceController, reference_accepts
from physical import (effective_parameters, empty_stats, overlaps, RobotPlant, Observation,
                      usable, body_clear, braking_distance, assess_interval, sweep_check,
                      score_completion)

def run_episode(*,advice_events=(),pedestrian='none',horizon=120.,emit=None):
    p=effective_parameters(); source=SourceController.from_selected(); stats=empty_stats()
    robots={r:RobotPlant(p['map']['route_'+r][1:]) for r in 'AB'}
    goals={r:tuple(p['map']['route_'+r][-1]) for r in 'AB'}
    intent={r:'Brake' for r in 'AB'}; since={r:0. for r in 'AB'}; last={r:None for r in 'AB'}
    modes={r:'Idle' for r in 'AB'}; obs={r:None for r in 'AB'}
    sensor={}; commands={}; released=set(); completed=set(); stopped=set()
    runtime=Runtime('req','ctx',source=source)
    s=runtime.core; generation=0; permission_version=0; trigger=None; seq=0
    deliveries={}
    for at,req,ctx,payload in advice_events:
        if at < 0 or abs(at/.01-round(at/.01)) > 1e-7:
            raise ValueError('advice times must be nonnegative 10ms ticks')
        deliveries.setdefault(round(at/.01),[]).append((req,ctx,payload))
    def record(kind,t,**data):
        if emit: emit(dict(kind=kind,time=round(t,10),**data))
    def transition(inp,t):
        nonlocal s,generation
        before=s; bound=runtime.local(inp); s=runtime.core; events=bound['events']
        record('adapter',t,**bound)
        actual_input=bound['event'][1]
        if bound['source'] is not None:
            record('source_select',t,**bound['source'],mailbox=bound['source']['latch'])
        accepted=reference_accepts(before,events)
        row=dict(before=asdict(before),input=actual_input,after=asdict(s),events=events,reference_accepted=accepted,
                 permission_version=permission_version,reservation_generation=generation)
        if not accepted:stats['reference_violations'].append(dict(time=t,**row))
        for event in events:
            if event[0]=='Grant':
                generation+=1; stats['grant_order'].append(event[1])
        record('protocol',t,**row)
        return events
    transition(('RequestAdvice',),0)
    transition(('Observe',False,False),0)
    for r in 'AB':transition(('Register',r),0)
    halt_bound=(1+.05+.5*.27)/.8
    def present(t):return trigger is not None and t>=trigger and (pedestrian=='permanent' or t<trigger+7)
    stats.update(pedestrian_trigger=None,pedestrian_brakes=0,resumes_after_pedestrian=0,pedestrian_brake_evidence=[])
    for tick in range(round(horizon/.01)+1):
        t=round(tick*.01,10)
        for req,ctx,payload in deliveries.pop(tick,[]):
            record('adapter',t,**runtime.receive(req,ctx,payload))
        if pedestrian!='none' and trigger is None and s.owner:
            r=s.owner; x,y,h=robots[r].pose
            aligned=abs(math.atan2(math.sin(h-(0 if r=='A' else math.pi)),math.cos(h-(0 if r=='A' else math.pi))))<1e-9
            if abs(y)<1e-9 and 8<=x<=16 and aligned and (x+.4<11.5 if r=='A' else x-.4>12.5):
                trigger=t; stats['pedestrian_trigger']=dict(time=t,robot=r,pose=robots[r].pose,speed=robots[r].speed,domain='straight_N_before_H')
                record('pedestrian_trigger',t,**{k:v for k,v in stats['pedestrian_trigger'].items() if k!='time'})
        if tick%5==0:
            for r in 'AB':
                packet=Observation(r,t,robots[r].pose,robots[r].speed,present(t),1,1)
                sensor.setdefault(tick+5,[]).append(packet)
                record('observation_sample',t,packet=asdict(packet),receive_time=t+.05)
        changed=False
        for packet in sensor.pop(tick,[]):
            obs[packet.robot_id]=packet; changed=True
            record('observation_received',t,packet=asdict(packet))
        if changed:
            blocked=any(o is not None and o.blocked for o in obs.values())
            fresh=all(usable(obs[r],r,t,p) for r in 'AB')
            if (s.blocked,s.fresh)!=(blocked,fresh):permission_version+=1
            transition(('Observe',blocked,fresh),t)
        for command in commands.pop(tick,[]):
            r=command['robot']; verdict=command['delivery']-1e-9<=t<=command['expiry']+1e-9; events=[]
            if command['intent']=='Proceed' and command['scope']=='reservation_zone':
                binding=verdict and s.owner==r and command['generation']==generation and s.command==r and command['mission']=='mission-'+r
                if binding: events=transition(('Apply',),t)
                verdict=binding and ('Proceed',r) in events
            elif command['intent']=='Proceed':
                verdict=verdict and r in released and usable(obs[r],r,t,p) and not obs[r].blocked
            if verdict:
                if command['intent']=='Brake' and intent[r]!='Brake':since[r]=t
                intent[r]=command['intent']
            else:last[r]=None
            record('command_applied',t,command=command,current_check_verdict=verdict,current_state=asdict(s),
                   permission_version=permission_version,reservation_generation=generation,actual_pose=robots[r].pose,
                   actual_speed=robots[r].speed,actuator_intent=intent[r])
        if tick%5==0:
            for r in 'AB':
                if r in completed:continue
                o=obs[r]; fresh=usable(o,r,t,p)
                clear=body_clear(o,r,t,p)
                facts=dict(ObservationUsable=fresh,PedestrianBlocked=bool(o.blocked) if fresh else False,
                           OwnReservation=s.owner==r,Released=r in released,BodyClearOfZ=bool(clear),
                           Halted=intent[r]=='Brake' and t-since[r]>=halt_bound,
                           AtGoal=fresh and math.dist(o.pose[:2],goals[r])<=.01,TaskActive=True)
                prior=modes[r]; action,nxt=source.step(prior,facts); modes[r]=nxt
                movement='Brake'
                if action=='Proceed':movement='Proceed'
                elif action=='Release':
                    events=transition(('Release',r,bool(clear)),t)
                    if ('Released',r) not in events:raise RuntimeError('source Release rejected')
                    released.add(r); occupied=overlaps(robots[r].pose)
                    row=dict(time=t,robot=r,pose=robots[r].pose,actual_speed=robots[r].speed,actual_body_still_in_Z=occupied)
                    if occupied:stats['early_releases'].append(row)
                    record('release',t,**{k:v for k,v in row.items() if k!='time'})
                    movement=last[r] or 'Brake'
                elif action=='Finish':
                    completed.add(r); stats['completion_times'][r]=t
                    record('complete',t,robot=r,actual_pose=robots[r].pose,actual_speed=robots[r].speed,goal=goals[r])
                elif action=='Resume' and r in stopped:
                    stats['resumes_after_pedestrian']+=1; stopped.remove(r)
                elif action not in ('Brake','Request','Resume'):raise RuntimeError(action)
                if action=='Brake' and facts['PedestrianBlocked'] and last[r]!='Brake':
                    stats['pedestrian_brakes']+=1; stopped.add(r)
                    x,y,h=o.pose; err=abs(math.atan2(math.sin(h-(0 if r=='A' else math.pi)),math.cos(h-(0 if r=='A' else math.pi))))
                    distance=11.5-x-.4 if r=='A' else x-.4-12.5
                    domain=abs(y)<1e-9 and err<1e-9 and 8<=x<=16 and distance>=0
                    bound=braking_distance(o.speed,t-o.sample_time,p) if domain else None
                    evidence=dict(time=t,robot=r,observation=asdict(o),age=t-o.sample_time,domain=domain,distance=distance,bound=bound,condition=distance>=bound if domain else None)
                    stats['pedestrian_brake_evidence'].append(evidence); record('pedestrian_brake',t,**{k:v for k,v in evidence.items() if k!='time'})
                record('source_step',t,robot=r,source_id=source.identity,prior_mode=prior,facts=facts,raw_action=action,raw_next=nxt,physical_intent=movement)
                if movement!=last[r]:
                    scope='outside_zone_after_release' if r in released else 'reservation_zone'
                    allowed=True
                    if movement=='Proceed' and scope=='reservation_zone':allowed=('Issued',r) in transition(('Issue',r),t)
                    if allowed:
                        seq+=1
                        command=dict(robot=r,mission='mission-'+r,sequence=seq,intent=movement,scope=scope,
                                     issued=t,delivery=round(t+.10,10),expiry=round(t+.30,10),generation=generation,
                                     permission_version=permission_version)
                        commands.setdefault(tick+10,[]).append(command); last[r]=movement
                        record('command_issued',t,command=command)
            if s.owner is None:
                transition(('Validate',),t);transition(('Commit',),t)
        if len(completed)==2 or tick==round(horizon/.01):break
        pieces={r:robots[r].advance(.01,intent[r]) for r in 'AB'}
        assess_interval(t,.01,pieces,'none',stats)
        if present(t+.005):
            # Continuous oracle with the same trigger-relative exogenous pedestrian.
            def person(tau):
                y=-3.5+max(0,t+tau-trigger)
                return (12,min(0 if pedestrian=='permanent' else 3.5,y),math.pi/2)
            for r,sequence in pieces.items():
                offset=0
                for piece in sequence:
                    result=sweep_check(piece.sample,lambda tau,off=offset:person(off+tau),.8,.6,.5,.5,piece.duration,piece.point_speed_bound,1.)
                    stats['continuous_intervals_checked']+=1
                    stats['distance_lower_bound_m']=min(stats['distance_lower_bound_m'],result['distance_lower_bound'])
                    pair=r+':pedestrian'
                    if result['status']=='collision' and pair not in stats['collision_pairs']:
                        stats['collision_pairs'].append(pair);stats['collision_witnesses'].append(dict(pair=pair,time=t+offset+result['witness_time']))
                    if result['status']=='unresolved' and pair not in stats['unresolved_pairs']:stats['unresolved_pairs'].append(pair)
                    offset+=piece.duration
        record('motion',t,duration=.01,robots={r:[piece.to_dict() for piece in v] for r,v in pieces.items()},
               actual_pedestrian_present=present(t+.005),pedestrian_trigger=trigger,pedestrian_mode=pedestrian)
    score=score_completion(completed,{r:(robots[r].pose,robots[r].speed) for r in 'AB'},goals)
    stats.update(**score,termination='complete' if len(score['completed_robots'])==2 else 'horizon',time=t,
                 final_poses={r:robots[r].pose for r in 'AB'},final_speeds={r:robots[r].speed for r in 'AB'},source_id=source.identity,
                 config=dict(advice_events=advice_events,pedestrian=pedestrian,horizon=horizon))
    return stats
