"""Bounded source-driven physical adapter. No historical globals are modified."""
from dataclasses import asdict
from pathlib import Path
import hashlib, json, math, sys
from protocol import Core, SourceController, step, reference_accepts
from advice_mailbox import AdviceMailbox
BASE=Path(__file__).resolve().parents[1]/'amr-corridor'
sys.path.insert(0,str(BASE))
from plant import RobotPlant
from controller import Observation, usable, body_clear, braking_distance
from oracle import rectangle, polygon_distance, sweep_check
from simulation import parameters, assess_interval, score_completion, FROZEN_PARAMETERS_SHA256

def effective_parameters():
    p=parameters()
    p['scenario_id']='AMR-advisory-v2-physical'
    p['timing']['brake_delivery_and_onset_upper_bound']=.10
    p['timing']['total_reaction_upper_bound']=.27
    return p

def identity():
    p=effective_parameters()
    return dict(original_parameters_sha256=FROZEN_PARAMETERS_SHA256,
                effective_parameters_sha256=hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),
                source_sha256=SourceController.from_selected().identity,
                files={str(f.relative_to(BASE.parent)):hashlib.sha256(f.read_bytes()).hexdigest()
                       for f in [Path(__file__),BASE/'plant.py',BASE/'oracle.py',BASE/'controller.py',BASE/'simulation.py']})

def empty_stats():
    return dict(collision_pairs=[],collision_witnesses=[],unresolved_pairs=[],distance_lower_bound_m=math.inf,
                continuous_intervals_checked=0,early_releases=[],reference_violations=[],grant_order=[],completion_times={})

def overlaps(pose):
    return polygon_distance(rectangle(pose,.8,.6),rectangle((12,0,0),12,5.2))<=1e-9

def run_episode(*,advice=None,center_clear=False,wait_advice=False,pedestrian='none',horizon=120.,emit=None):
    p=effective_parameters(); source=SourceController.from_selected(); stats=empty_stats()
    robots={r:RobotPlant(p['map']['route_'+r][1:]) for r in 'AB'}
    goals={r:tuple(p['map']['route_'+r][-1]) for r in 'AB'}
    intent={r:'Brake' for r in 'AB'}; since={r:0. for r in 'AB'}; last={r:None for r in 'AB'}
    modes={r:'Idle' for r in 'AB'}; obs={r:None for r in 'AB'}
    sensor={}; commands={}; released=set(); completed=set(); stopped=set()
    s=Core(fresh=False); generation=0; permission_version=0; trigger=None; seq=0
    mailbox=AdviceMailbox('physical-request','fixed-A-B-v1')
    if advice is not None: mailbox.receive('physical-request','fixed-A-B-v1',json.dumps({'prefer':advice}))
    latched=mailbox.latch()
    def record(kind,t,**data):
        if emit: emit(dict(kind=kind,time=round(t,10),**data))
    def transition(inp,t):
        nonlocal s,generation
        before=s; s,events=step(s,inp)
        accepted=reference_accepts(before,events)
        row=dict(before=asdict(before),input=inp,after=asdict(s),events=events,reference_accepted=accepted,
                 permission_version=permission_version,reservation_generation=generation)
        if not accepted:stats['reference_violations'].append(dict(time=t,**row))
        for event in events:
            if event[0]=='Grant':
                generation+=1; stats['grant_order'].append(event[1])
        record('protocol',t,**row)
        return events
    for r in 'AB':transition(('Register',r),0)
    record('mailbox',0,**latched)
    halt_bound=(1+.05+.5*.27)/.8
    def present(t):return trigger is not None and t>=trigger and (pedestrian=='permanent' or t<trigger+7)
    stats.update(pedestrian_trigger=None,pedestrian_brakes=0,resumes_after_pedestrian=0,pedestrian_brake_evidence=[])
    for tick in range(round(horizon/.01)+1):
        t=round(tick*.01,10)
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
                clear=(fresh and (o.pose[0]>18 if r=='A' else o.pose[0]<6)) if center_clear else body_clear(o,r,t,p)
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
            if s.owner is None and not (wait_advice and latched['advice'] is None):
                selected,decision=source.select(s,latched['advice'])
                record('source_select',t,**decision,mailbox=latched)
                transition(('Validate',selected),t);transition(('Commit',),t)
            elif wait_advice and s.owner is None:record('wait_advice',t,source_select_called=False,current_state=asdict(s))
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
                 config=dict(advice=advice,center_clear=center_clear,wait_advice=wait_advice,pedestrian=pedestrian,horizon=horizon))
    return stats

def run_gap(gap,*,bad=False,emit=None):
    if gap not in ('commit','apply'):raise ValueError(gap)
    source=SourceController.from_selected();p=effective_parameters();robot=RobotPlant(p['map']['route_A'][1:])
    s=Core();rows=[];generation=0;version=0;intent='Brake';stats=empty_stats();other=RobotPlant(p['map']['route_B'][1:]);fault=('cached_commit_permission' if gap=='commit' else 'cached_apply_permission') if bad else None
    def record(kind,t,**data):
        row=dict(kind=kind,time=t,**data);rows.append(row)
        if emit:emit(row)
    def transition(inp,t):
        nonlocal s,generation
        before=s;s,events=step(s,inp,fault=fault)
        if any(e[0]=='Grant' for e in events):generation+=1
        record('protocol',t,before=asdict(before),input=inp,after=asdict(s),events=events,
               reference_accepted=reference_accepts(before,events),permission_version=version,
               reservation_generation=generation,actual_pose=robot.pose,actual_speed=robot.speed)
        return events
    record('snapshot',0,pose=robot.pose,speed=robot.speed,overlaps_zone=overlaps(robot.pose),intent=intent)
    assert robot.speed==0 and not overlaps(robot.pose)
    transition(('Register','A'),0);transition(('Register','B'),0)
    selected,decision=source.select(s,None);record('source_select',0,**decision,mailbox_advice=None)
    transition(('Validate',selected),0)
    if gap=='apply':
        transition(('Commit',),0)
        # Actual raw source step selects Proceed from a legal owned snapshot.
        facts=dict(ObservationUsable=True,PedestrianBlocked=False,OwnReservation=True,Released=False,
                   BodyClearOfZ=False,Halted=True,AtGoal=False,TaskActive=True)
        action,nxt=source.step('Waiting',facts)
        record('source_step',0,prior_mode='Waiting',facts=facts,raw_action=action,raw_next=nxt,source_id=source.identity)
        if action!='Proceed':raise RuntimeError('gap prefix did not legally Issue source Proceed')
        transition(('Issue','A'),0)
        command=dict(robot='A',mission='mission-A',intent='Proceed',generation=generation,permission_version=version,issued=0,delivery=.10)
        record('command_issued',0,command=command)
    version+=1;transition(('Observe',True,True),.05)
    if gap=='commit':transition(('Commit',),.10)
    else:
        events=transition(('Apply',),.10)
        accepted=('Proceed','A') in events
        if accepted:intent='Proceed'
        record('command_applied',.10,command=command,current_check_verdict=accepted,intent=intent,
               current_state=asdict(s),permission_version=version,reservation_generation=generation,actual_pose=robot.pose,actual_speed=robot.speed)
    # Entire prefix is a halted Brake interval; the only possible movement follows Apply.
    for tick in range(20):
        t=tick*.01;active=intent if tick>=10 else 'Brake';pieces=robot.advance(.01,active)
        other_pieces=other.advance(.01,'Brake')
        assess_interval(t,.01,{'A':pieces,'B':other_pieces},'none',stats)
        record('motion',t,duration=.01,intent=active,robots={'A':[v.to_dict() for v in pieces],'B':[v.to_dict() for v in other_pieces]})
    return dict(gap=gap,constructed_fault=fault,source_id=source.identity,
                reference_violations=[r for r in rows if r['kind']=='protocol' and not r['reference_accepted']],
                grant_order=[e[1] for r in rows if r['kind']=='protocol' for e in r['events'] if e[0]=='Grant'],
                final_pose=robot.pose,final_speed=robot.speed,final_intent=intent,overlaps_zone=overlaps(robot.pose),
                termination='bounded_witness',collision_pairs=stats['collision_pairs'],unresolved_pairs=stats['unresolved_pairs'],continuous_intervals_checked=stats['continuous_intervals_checked'],early_releases=[],completed_robots=[])

def run_braking(*,inside=True,emit=None):
    p=effective_parameters();bound=braking_distance(1,.05,p);distance=bound+(.01 if inside else -.01)
    x=11.5-.4-distance
    robot=RobotPlant([(x,0),(16,0)],initial_speed=1.)
    observed=Observation('A',0,robot.pose,robot.speed,True,1,1)
    rows=[];crossed=False;unresolved=[];collisions=[];min_margin=math.inf
    def record(kind,t,**data):
        row=dict(kind=kind,time=t,**data);rows.append(row)
        if emit:emit(row)
    record('observation_sample',0,packet=asdict(observed))
    for tick in range(501):
        t=round(tick*.01,10)
        if tick==5:record('command_issued',t,intent='Brake',delivery=.15,observation=asdict(observed),age=.05,bound=bound,distance=distance)
        if tick==15:record('command_applied',t,intent='Brake',actual_pose=robot.pose,actual_speed=robot.speed)
        if tick>=15 and robot.speed==0:break
        active='Brake' if tick>=15 else 'Proceed';pieces=robot.advance(.01,active)
        for piece in pieces:
            front=lambda tau:piece.sample(tau)[0]+.4
            margin=11.5-max(front(0),front(piece.duration));min_margin=min(min_margin,margin);crossed|=margin<0
            result=sweep_check(piece.sample,lambda tau:(12,0,0),.8,.6,1,7,piece.duration,piece.point_speed_bound,0.)
            if result['status']=='collision':collisions.append(t)
            if result['status']=='unresolved':unresolved.append(t)
        record('motion',t,duration=.01,intent=active,pieces=[v.to_dict() for v in pieces])
    return dict(inside=inside,condition=distance>=bound,bound=bound,observed_front_distance=distance,
                observation_age=.05,delivery_delay=.10,total_actual_observation_to_brake=.15,heading=observed.pose[2],
                observed_pose=observed.pose,actual_brake=.8,standstill_margin=11.5-robot.pose[0]-.4,
                min_trajectory_margin=min_margin,crossed_boundary=crossed,final_speed=robot.speed,final_pose=robot.pose,
                halted_time=t,collision_pairs=['A:H'] if collisions else [],unresolved_pairs=['A:H'] if unresolved else [],
                reference_violations=[],early_releases=[],completed_robots=[],termination='standstill')
