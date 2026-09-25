"""Execute accepted SOURCE supervisors in the frozen reference physical world.

Only plant, observations, actuators and independent scoring are reused from the
previous stage. Reservation actions and modes now come from the new supervisor.
No runtime target evaluation substitutes for the checked source program.
"""
from dataclasses import asdict
import hashlib
import math
from pathlib import Path
import sys

BASELINE = Path(__file__).resolve().parents[1]/'amr-corridor'
sys.path.insert(0,str(BASELINE))
from controller import Observation, Command, Actuator, Reservation, usable, body_clear, braking_distance
from plant import RobotPlant
from oracle import rectangle, polygon_distance
from simulation import parameters, clock_multiple, pedestrian_present, assess_interval, score_completion

from .language import parse_program, eval_select, eval_step
from .assurance import assess_source, selection_violations, step_violations, obligation


class SourceSupervisor:
    def __init__(self, text):
        self.assessment = assess_source(text)
        if not self.assessment['accepted']:
            raise ValueError('Source candidate rejected before deployment: ' + str(self.assessment['source_sha256']))
        self.program = parse_program(text)
        self.identity = self.assessment['source_sha256']

    def select(self, facts):
        return eval_select(self.program, facts)

    def step(self, mode, facts):
        return eval_step(self.program, mode, facts)


class HandwrittenSupervisor:
    """Calibration baseline for this same mode/action interface, not an LLM."""
    identity = 'handwritten-obligation-reference/v1.1'
    assessment = None

    def select(self, f):
        if not f['OwnerFree']:
            return 'Defer'
        if f['RequestA'] and (not f['RequestB'] or f['PreferA'] or not f['PreferB']):
            return 'SelectA'
        return 'SelectB' if f['RequestB'] else 'Defer'

    def step(self, mode, facts):
        return obligation(mode, facts)[1]


def pedestrian_stopping_evidence(obs, name, now, p):
    """Label the observed geometric domain of the straight stopping calculation.

    This diagnostic never changes control. Applicability uses only the received
    pose and the frozen map; it does not establish actual physical alignment.
    """
    if name not in ('A','B'):
        raise ValueError('Unknown robot for stopping evidence')
    x,y,heading=obs.pose
    robot=p['robot']
    extent=(robot['length']*abs(math.cos(heading))+
            robot['width']*abs(math.sin(heading)))/2
    h_min,h_max,_,_=p['map']['pedestrian_strip_H']
    n_min,n_max,y_min,y_max=p['map']['narrow_corridor_N']
    distance=h_min-x-extent if name=='A' else x-extent-h_max
    target_heading=0. if name=='A' else math.pi
    heading_error=abs(math.atan2(math.sin(heading-target_heading),math.cos(heading-target_heading)))
    reasons=[]
    if heading_error>1e-9:
        reasons.append('observed_heading_not_forward_along_N')
    if abs(y-(y_min+y_max)/2)>1e-9 or not n_min<=x<=n_max:
        reasons.append('observed_pose_not_on_straight_N_centerline')
    if distance<0.:
        reasons.append('observed_footprint_not_before_H')
    applicable=not reasons
    required=braking_distance(obs.speed,now-obs.sample_time,p) if applicable else None
    return dict(observation_pose=obs.pose,observation_speed=obs.speed,
                observation_sample_time=obs.sample_time,world_x_footprint_extent=extent,
                observation_distance_to_H=distance,required_distance=required,
                straight_approach_applicable=applicable,
                straight_approach_condition=distance>=required if applicable else None,
                scope_reason='observed_straight_N_approach_before_H' if applicable else ';'.join(reasons))


def run_supervised_episode(text=None, *, handwritten=False, preference='A',
                           pedestrian='none', sensor_blackout=None, dt=.01, horizon=120., emit=None):
    if handwritten and text is not None:
        raise ValueError('Choose handwritten baseline or a source candidate, not both')
    # Validation precedes all plant construction and all output events.
    supervisor = HandwrittenSupervisor() if handwritten else SourceSupervisor(text)
    if preference not in ('A','B') or pedestrian not in ('none','temporary','permanent'):
        raise ValueError('Unsupported frozen scenario')
    if not math.isfinite(dt) or dt <= 0 or dt > .01:
        raise ValueError('dt must be positive and no larger than .01')
    p = parameters()
    period = clock_multiple(.05,dt)
    lag, delivery, steps = clock_multiple(.05,dt),clock_multiple(.1,dt),clock_multiple(horizon,dt)
    if period < 1:
        raise ValueError('dt must divide monitoring interval')
    robots = {name:RobotPlant(p['map']['route_'+name][1:]) for name in ('A','B')}
    goals = {name:tuple(p['map']['route_'+name][-1]) for name in robots}
    actuators = {name:Actuator(name) for name in robots}
    observations = {name:None for name in robots}
    modes = {name:'Idle' for name in robots}
    observations_in_flight, commands_in_flight = {},{}
    reservation = Reservation()
    requested,released,completed = set(),set(),set()
    last_sent = {name:None for name in robots}
    serial = {name:0 for name in robots}
    stopped_for_person = set()
    events=[]
    stats=dict(collision_pairs=[],collision_witnesses=[],unresolved_pairs=[],distance_lower_bound_m=math.inf,
               continuous_intervals_checked=0,early_releases=[],grant_order=[],completion_times={},
               runtime_rejections=[],pedestrian_brakes=0,resumes_after_pedestrian=0,
               assumption_violated=[],assumption_detected=[])

    def record(kind,time,**data):
        row=dict(kind=kind,time=round(time,10),**data)
        if kind!='observation':events.append(row)
        if emit:emit(row)

    halt_bound=(1+.05+.5*.25)/.8
    for tick in range(steps+1):
        t=round(tick*dt,10)
        if tick % period == 0:
            for name,robot in robots.items():
                obs=Observation(name,t,robot.pose,robot.speed,pedestrian_present(t,pedestrian),1,1)
                observations_in_flight.setdefault(tick+lag,[]).append(obs)
                record('observation',t,packet=asdict(obs),receive_time=round(t+.05,10))
        for obs in observations_in_flight.pop(tick,[]):
            if sensor_blackout and obs.robot_id=='A' and sensor_blackout[0]<=t<sensor_blackout[1]:
                record('observation_dropped',t,robot='A',sample_time=obs.sample_time)
            else:
                observations[obs.robot_id]=obs
        if tick % period == 0:
            for name in robots:
                if name in completed:
                    continue
                obs=observations[name]
                fresh=usable(obs,name,t,p)
                halted=actuators[name].intent=='Brake' and t-actuators[name].brake_since>=halt_bound
                facts=dict(ObservationUsable=fresh,PedestrianBlocked=bool(obs.blocked) if fresh else False,
                           OwnReservation=reservation.owner==name,Released=name in released,
                           BodyClearOfZ=body_clear(obs,name,t,p),Halted=halted,
                           AtGoal=fresh and math.dist(obs.pose[:2],goals[name])<=.01,TaskActive=True)
                prior_mode=modes[name]
                raw_action,raw_next=supervisor.step(prior_mode,facts)
                violations=step_violations((raw_action,raw_next),prior_mode,facts)
                action,next_mode=raw_action,raw_next
                if violations:
                    action,next_mode='Brake','Stopped' if halted else 'BrakeRequested'
                    rejection=dict(time=t,robot=name,raw_action=raw_action,raw_next=raw_next,reasons=violations)
                    stats['runtime_rejections'].append(rejection)
                # Inputs to p were immutable bool values. Plant truth below is
                # used only for scoring, never as a replacement for these gates.
                movement='Brake'
                if action=='Request':
                    requested.add(name)
                elif action=='Release':
                    if reservation.release(name,'mission-'+name,facts['BodyClearOfZ'] and fresh):
                        released.add(name)
                        actual_occupied=polygon_distance(rectangle(robots[name].pose,.8,.6),rectangle((12,0,0),12,5.2))<=1e-9
                        if actual_occupied:stats['early_releases'].append(dict(time=t,robot=name,pose=robots[name].pose))
                        record('release',t,robot=name,actual_body_still_in_Z=actual_occupied,source_id=supervisor.identity)
                        movement=last_sent[name] or 'Brake'
                    else:
                        raise RuntimeError('Accepted Release did not satisfy current manager state')
                elif action=='Finish':
                    if not (fresh and facts['Released'] and facts['AtGoal'] and halted):
                        raise RuntimeError('Accepted Finish lacks execution preconditions')
                    completed.add(name)
                    stats['completion_times'][name]=t
                    record('complete',t,robot=name,source_id=supervisor.identity,goal=goals[name])
                elif action=='Proceed':
                    movement='Proceed'
                elif action=='Resume':
                    # This intent changes logical mode; a new Proceed on a
                    # later monitor tick is still required for physical motion.
                    if name in stopped_for_person:
                        stats['resumes_after_pedestrian']+=1
                        stopped_for_person.remove(name)
                        record('resume',t,robot=name,source_id=supervisor.identity)
                elif action!='Brake':
                    raise RuntimeError('Unexpected accepted action')
                modes[name]=next_mode
                record('supervisor_step',t,robot=name,source_id=supervisor.identity,prior_mode=prior_mode,
                       facts=facts,raw_action=raw_action,raw_next=raw_next,applied_action=action,next_mode=next_mode,
                       physical_intent=movement,sample_time=obs.sample_time if obs else None,
                       reservation_id=reservation.serial if reservation.owner==name else None)
                if action=='Brake' and facts['PedestrianBlocked'] and last_sent[name]!='Brake':
                    stats['pedestrian_brakes']+=1
                    stopped_for_person.add(name)
                    evidence=pedestrian_stopping_evidence(obs,name,t,p)
                    record('pedestrian_brake',t,robot=name,**evidence)
                    if evidence['straight_approach_applicable'] and evidence['straight_approach_condition'] is False:
                        stats['assumption_violated'].append(dict(time=t,robot=name,condition='viable_straight_approach_at_first_blocked_observation'))
                if movement!=last_sent[name]:
                    serial[name]+=1
                    command=Command(name,serial[name],movement,1,1,t,round(t+.1,10),round(t+.3,10))
                    commands_in_flight.setdefault(tick+delivery,[]).append(command)
                    record('command_issued',t,command=asdict(command),source_id=supervisor.identity,
                           raw_action=raw_action,reservation_id=reservation.serial if reservation.owner==name else None)
                    last_sent[name]=movement
            selection_facts=dict(OwnerFree=reservation.owner is None,
                                 RequestA='A' in requested and 'A' not in released and usable(observations['A'],'A',t,p),
                                 RequestB='B' in requested and 'B' not in released and usable(observations['B'],'B',t,p),
                                 PreferA=preference=='A',PreferB=preference=='B')
            selected=supervisor.select(selection_facts)
            selection_errors=selection_violations(selected,selection_facts)
            if selection_errors:
                stats['runtime_rejections'].append(dict(time=t,function='select',raw_action=selected,reasons=selection_errors))
            record('supervisor_select',t,facts=selection_facts,raw_action=selected,
                   applied_action='Defer' if selection_errors else selected,source_id=supervisor.identity)
            if not selection_errors and selected in ('SelectA','SelectB'):
                name=selected[-1]
                if not reservation.acquire(name,'mission-'+name):
                    raise RuntimeError('Accepted selection did not acquire reservation')
                requested.discard(name)
                stats['grant_order'].append(name)
                record('grant',t,robot=name,mission_id='mission-'+name,reservation_id=reservation.serial,source_id=supervisor.identity)
        for command in commands_in_flight.pop(tick,[]):
            status=actuators[command.robot_id].accept(command,t)
            record('command_delivered',t,command=asdict(command),status=status,source_id=supervisor.identity)
        if len(completed)==2 or tick==steps:break
        pieces={name:robot.advance(dt,actuators[name].intent) for name,robot in robots.items()}
        assess_interval(t,dt,pieces,pedestrian,stats)
        if emit:emit(dict(kind='motion',time=t,duration=dt,robots={name:[piece.to_dict() for piece in sequence] for name,sequence in pieces.items()}))
    scoring=score_completion(completed,{name:(robot.pose,robot.speed) for name,robot in robots.items()},goals)
    done=scoring['completed_robots']
    stats.update(completed_robots=done,controller_completed_robots=sorted(completed),physical_completion_score=scoring,
                 completion_mismatches=scoring['completion_mismatches'],independent_goals=goals,
                 time=t,termination='complete' if len(done)==2 else 'completion_mismatch' if len(completed)==2 else 'horizon',
                 reservation_owner=reservation.owner,final_poses={name:robot.pose for name,robot in robots.items()},
                 safe_and_complete=len(done)==2 and not any(stats[k] for k in ('collision_pairs','unresolved_pairs','early_releases','runtime_rejections')),
                 source_id=supervisor.identity,assessment=supervisor.assessment,events=events,
                 config=dict(handwritten=handwritten,preference=preference,pedestrian=pedestrian,
                             sensor_blackout=sensor_blackout,dt=dt,horizon=horizon))
    return stats
