"""Deterministic reference episodes, separate sensor/controller and scoring paths.

Events on the fixed output clock: sample -> receive -> monitor/reservation ->
deliver -> continuous plant interval. Commands become effective after 0.10 s.
This synthetic closed loop is not a robot-stack or LLM evaluation.
"""
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from controller import (Observation, Command, Actuator, Reservation, body_clear,
                        braking_distance, reference_decision, usable)
from plant import RobotPlant, MotionPiece
from oracle import rectangle, polygon_distance, sweep_check

PARAMETER_PATH = Path(__file__).resolve().parents[2] / 'literature/scholar_search_2026-09-10/followup/research_amr_parameters_2026-09-15.json'
FROZEN_PARAMETERS_SHA256 = 'ce4e5058052d8f87e6187254ab42e870c37197176dc8ea20c59aa5aa442630a6'


def parameters(path=PARAMETER_PATH):
    # This first fixture has fixed geometry/constants, not arbitrary map support.
    # Refuse drift instead of hashing a new config but executing old constants.
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_PARAMETERS_SHA256:
        raise ValueError('This fixture requires the frozen AMR-Corridor-v0.1 parameters; adapt and revalidate code before changing them')
    return json.loads(raw)


def clock_multiple(value, dt):
    count = round(value / dt)
    if count < 0 or abs(count * dt - value) > 1e-9:
        raise ValueError('Event times must be integral multiples of output dt')
    return count


def pedestrian_pose(t, mode):
    # Exogenous schedule frozen before comparative runs: enter at t=10;
    # cross south to north at 1 m/s, or remain at the lane centre.
    y = -3.5 + max(0, t - 10)
    if mode == 'permanent':
        y = min(0, y)
    return (12.0, min(3.5, y), math.pi / 2)


def pedestrian_present(t, mode):
    return mode != 'none' and t >= 10 and (mode == 'permanent' or t < 17)


def pedestrian_speed(t, mode):
    return 0 if mode == 'permanent' and t >= 13.5 else 1


def wall_rectangles():
    # Inner wall faces y=+/-0.8; opening x=11.5..12.5.
    return [((x, y, 0), 3.5, .14) for x in (9.75, 14.25) for y in (-.87, .87)]


def piece_at(pieces, relative_t):
    offset = 0.0
    for piece in pieces:
        if relative_t <= offset + piece.duration + 1e-10:
            return piece, offset
        offset += piece.duration
    raise ValueError('Motion pieces do not cover interval')


def assess_interval(t, dt, pieces, pedestrian, stats):
    """Independent oracle consumes physical trajectories, never safety predicates."""
    boundaries = {0., dt}
    for sequence in pieces.values():
        total = 0.
        for piece in sequence:
            total += piece.duration
            if 1e-10 < total < dt - 1e-10:
                boundaries.add(total)
    cuts = sorted(boundaries)
    for lo, hi in zip(cuts, cuts[1:]):
        moving = {}
        for name, sequence in pieces.items():
            piece, offset = piece_at(sequence, (lo + hi) / 2)
            moving[name] = (lambda tau, p=piece, start=lo-offset: p.sample(start+tau),
                            .8, .6, piece.point_speed_bound)
        pairs = [('A:B', moving['A'], moving['B'])]
        for name, body in moving.items():
            for number, (pose, length, width) in enumerate(wall_rectangles()):
                pairs.append((name + ':wall' + str(number), body,
                              (lambda tau, p=pose: p, length, width, 0)))
            if pedestrian_present(t + (lo + hi) / 2, pedestrian):
                pairs.append((name + ':pedestrian', body,
                              (lambda tau, start=t+lo: pedestrian_pose(start+tau, pedestrian),
                               .5, .5, pedestrian_speed(t+lo, pedestrian))))
        for name, a, b in pairs:
            result = sweep_check(a[0], b[0], a[1], a[2], b[1], b[2], hi-lo, a[3], b[3])
            stats['continuous_intervals_checked'] += 1
            stats['distance_lower_bound_m'] = min(stats['distance_lower_bound_m'], result['distance_lower_bound'])
            if result['status'] == 'collision' and name not in stats['collision_pairs']:
                stats['collision_pairs'].append(name)
                stats['collision_witnesses'].append({'pair': name, 'time': t+lo+result['witness_time']})
            if result['status'] == 'unresolved' and name not in stats['unresolved_pairs']:
                stats['unresolved_pairs'].append(name)


def score_completion(controller_completed, physical_states, goals):
    """Score reported Done against actual goal position and standstill.

    Inputs are scoring-only snapshots. No observation, controller predicate or
    logical mode can supply the physical goal/velocity check.
    """
    validated, mismatches = [], []
    for name in sorted(controller_completed):
        pose, speed = physical_states[name]
        distance = math.dist(pose[:2], goals[name])
        at_goal = math.isfinite(distance) and distance <= .01
        stopped = math.isfinite(speed) and abs(speed) <= 1e-9
        if at_goal and stopped:
            validated.append(name)
        else:
            reasons = []
            if not at_goal:
                reasons.append('actual_position_outside_goal_tolerance')
            if not stopped:
                reasons.append('actual_speed_not_halted')
            mismatches.append(dict(robot=name, reason=reasons,
                                   goal_distance_m=distance, speed=speed))
    return dict(completed_robots=validated, completion_mismatches=mismatches)


def run_episode(*, preference='A', pedestrian='none', always_stop=False,
                front_only=False, sensor_blackout=None, dt=.01, horizon=120., emit=None):
    if preference not in ('A', 'B') or pedestrian not in ('none', 'temporary', 'permanent'):
        raise ValueError('Unsupported scenario')
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError('dt must be positive and finite')
    p = parameters()
    period = clock_multiple(p['timing']['safety_monitor_period'], dt)
    sensor_delay = clock_multiple(.05, dt)
    command_delay = clock_multiple(.10, dt)
    steps = clock_multiple(horizon, dt)
    if period < 1 or dt > .01:
        raise ValueError('dt must divide 0.05 s and be at most 0.01 s')
    robots = {name: RobotPlant(p['map']['route_' + name][1:]) for name in ('A', 'B')}
    independent_goals = {name: tuple(p['map']['route_' + name][-1]) for name in robots}
    actuators = {name: Actuator(name) for name in robots}
    observations = {name: None for name in robots}
    sensor_queue, command_queue = {}, {}
    reservation = Reservation()
    released, completed = set(), set()
    last_sent = {name: None for name in robots}
    sequence = {name: 0 for name in robots}
    pedestrian_stopped = set()
    last_mode = {name: 'Waiting' for name in robots}
    events = []
    stats = dict(collision_pairs=[], collision_witnesses=[], unresolved_pairs=[],
                 distance_lower_bound_m=math.inf, continuous_intervals_checked=0,
                 early_releases=[], grant_order=[], pedestrian_brakes=0,
                 resumes_after_pedestrian=0, completion_times={},
                 assumption_violated=[], assumption_detected=[])

    def record(kind, time, **data):
        row = dict(kind=kind, time=round(time, 10), **data)
        if kind != 'observation':
            events.append(row)
        if emit:
            emit(row)

    # Conservative standstill evidence based on effective sustained Brake,
    # bounded speed/acceleration and the declared braking lower bound.
    r = p['robot']
    halt_bound = (r['speed_limit'] + r['speed_error_bound'] +
                  r['forward_acceleration_upper_bound'] * p['timing']['total_reaction_upper_bound']) / r['braking_deceleration_lower_bound']
    t = 0.
    for tick in range(steps + 1):
        t = round(tick * dt, 10)
        if tick % period == 0:
            for name, robot in robots.items():
                obs = Observation(name, t, robot.pose, robot.speed,
                                  pedestrian_present(t, pedestrian), 1, 1)
                sensor_queue.setdefault(tick + sensor_delay, []).append(obs)
                record('observation', t, packet=asdict(obs), receive_time=round(t+.05, 10))
        for obs in sensor_queue.pop(tick, []):
            if sensor_blackout and obs.robot_id == 'A' and sensor_blackout[0] <= t < sensor_blackout[1]:
                record('observation_dropped', t, robot='A', sample_time=obs.sample_time)
            else:
                observations[obs.robot_id] = obs
        if tick % period == 0:
            owner = reservation.owner
            if owner and body_clear(observations[owner], owner, t, p, front_only):
                actual = rectangle(robots[owner].pose, .8, .6)
                zone = rectangle((12, 0, 0), 12, 5.2)
                occupied = polygon_distance(actual, zone) <= 1e-9
                if occupied:
                    stats['early_releases'].append({'time': t, 'robot': owner, 'pose': robots[owner].pose})
                reservation.release(owner, 'mission-'+owner, True)
                released.add(owner)
                record('release', t, robot=owner, actual_body_still_in_Z=occupied)
            if reservation.owner is None:
                for name in (preference, 'B' if preference == 'A' else 'A'):
                    if name not in released and usable(observations[name], name, t, p):
                        reservation.acquire(name, 'mission-'+name)
                        stats['grant_order'].append(name)
                        record('grant', t, robot=name, mission_id='mission-'+name, reservation_id=reservation.serial)
                        break
            for name in robots:
                obs = observations[name]
                goal = p['map']['route_'+name][-1]
                permitted = reservation.owner == name or name in released
                action, reason = reference_decision(obs, name, t, p, permitted, goal, always_stop)
                actuator = actuators[name]
                halted = (actuator.intent == 'Brake' and t-actuator.brake_since >= halt_bound)
                if name in released and usable(obs, name, t, p) and math.dist(obs.pose[:2], goal) <= .01 and halted:
                    if name not in completed:
                        completed.add(name)
                        stats['completion_times'][name] = t
                        record('complete', t, robot=name, goal=goal)
                if action == 'Brake' and reason == 'pedestrian_blocked' and last_sent[name] != 'Brake':
                    stats['pedestrian_brakes'] += 1
                    pedestrian_stopped.add(name)
                    distance = 11.5 - obs.pose[0] - .4 if name == 'A' else obs.pose[0] - .4 - 12.5
                    required = braking_distance(obs.speed, t-obs.sample_time, p)
                    condition = distance >= required
                    record('pedestrian_brake', t, robot=name, observation_distance_to_H=distance,
                           required_distance=required, straight_approach_condition=condition)
                    if not condition:
                        stats['assumption_violated'].append({'time': t, 'robot': name, 'condition': 'viable_straight_approach_at_first_blocked_observation'})
                if action == 'Proceed' and name in pedestrian_stopped and last_sent[name] == 'Brake':
                    stats['resumes_after_pedestrian'] += 1
                    pedestrian_stopped.remove(name)
                    record('resume', t, robot=name)
                mode = 'Done' if name in completed else ('Stopped' if action == 'Brake' and halted else ('BrakeRequested' if action == 'Brake' else 'Traversing'))
                if mode != last_mode[name]:
                    record('mode', t, robot=name, mode=mode)
                    last_mode[name] = mode
                if action != last_sent[name]:
                    sequence[name] += 1
                    command = Command(name, sequence[name], action, 1, 1, t, round(t+.1, 10), round(t+.3, 10))
                    command_queue.setdefault(tick+command_delay, []).append(command)
                    record('command_issued', t, command=asdict(command), reason=reason,
                           reservation_id=reservation.serial if reservation.owner == name else None,
                           sample_time=obs.sample_time if obs else None)
                    last_sent[name] = action
        for command in command_queue.pop(tick, []):
            accepted = actuators[command.robot_id].accept(command, t)
            record('command_delivered', t, command=asdict(command), status=accepted)
        if len(completed) == 2 or tick == steps:
            break
        pieces = {name: robot.advance(dt, actuators[name].intent) for name, robot in robots.items()}
        assess_interval(t, dt, pieces, pedestrian, stats)
        if emit:
            emit(dict(kind='motion', time=t, duration=dt,
                      robots={name: [piece.to_dict() for piece in motions] for name, motions in pieces.items()}))
    physical_score = score_completion(
        completed, {name: (robot.pose, robot.speed) for name, robot in robots.items()},
        independent_goals)
    validated = physical_score['completed_robots']
    stats.update(completed_robots=validated, controller_completed_robots=sorted(completed),
                 independent_goals=independent_goals, physical_completion_score=physical_score,
                 completion_mismatches=physical_score['completion_mismatches'],
                 termination=('complete' if len(validated) == 2 else
                              'completion_mismatch' if len(completed) == 2 else 'horizon'),
                 time=t, reservation_owner=reservation.owner, events=events,
                 final_poses={name: robot.pose for name, robot in robots.items()},
                 config=dict(preference=preference, pedestrian=pedestrian, always_stop=always_stop,
                             front_only=front_only, sensor_blackout=sensor_blackout, dt=dt, horizon=horizon),
                 safe_and_complete=(len(validated) == 2 and not stats['collision_pairs'] and
                                    not stats['unresolved_pairs'] and not stats['early_releases']))
    return stats


def geometry_witness():
    p = parameters()
    obs = Observation('A', 0, (18.1, -2, 0), 0, False, 1, 1)
    return dict(pose=obs.pose, front_x=18.5, rear_x=17.7,
                front_only_clear=body_clear(obs, 'A', 0, p, True),
                whole_body_clear=body_clear(obs, 'A', 0, p),
                actual_body_intersects_Z=polygon_distance(rectangle(obs.pose, .8, .6), rectangle((12, 0, 0), 12, 5.2)) <= 1e-9)


def run_stopping_witness(*, omit_reaction=False, actual_brake=.8, dt=.01, emit=None):
    """C07 straight fixed-boundary paired closed-loop witness, not an episode.

    Initial front distance=3.6 m; both policies start from the same viable state.
    First threshold crossing is held Brake; actual plant does not use its bound.
    """
    p = parameters()
    period, lag, delivery = (clock_multiple(value, dt) for value in (.05, .1, .1))
    robot = RobotPlant([(0, 0), (50, 0)], initial_speed=1, brake=actual_brake)
    packets, latest = {}, None
    brake_tick = None
    issued_time = delivered_time = halted_time = None
    rows = []
    for tick in range(clock_multiple(10, dt)+1):
        t = round(tick*dt, 10)
        if tick % period == 0:
            packets[tick+lag] = (t, robot.pose[0], robot.speed)
        latest = packets.pop(tick, latest)
        if tick % period == 0 and latest and brake_tick is None:
            observed_at, x, speed = latest
            distance = 4 - x - .4
            required = braking_distance(speed, t-observed_at, p, omit_reaction)
            rows.append(dict(time=t, observed_at=observed_at, observed_front_distance=distance, required_distance=required))
            if distance <= required:
                brake_tick = tick+delivery
                issued_time, delivered_time = t, round((tick+delivery)*dt, 10)
        braking = brake_tick is not None and tick >= brake_tick
        if braking and robot.speed == 0:
            halted_time = t
            break
        pieces = robot.advance(dt, 'Brake' if braking else 'Proceed')
        if emit:
            emit(dict(kind='motion', time=t, duration=dt, intent='Brake' if braking else 'Proceed', pieces=[piece.to_dict() for piece in pieces]))
    clearance = 4 - robot.pose[0] - .4
    return dict(initial_state=dict(pose=[0, 0, 0], speed=1, forbidden_boundary_x=4),
                omit_reaction=omit_reaction, actual_brake=actual_brake, dt=dt,
                brake_issued=issued_time, brake_delivery=delivered_time, halted_time=halted_time,
                final_front_x=robot.pose[0]+.4, clearance=clearance,
                required_margin=p['robot']['clearance_margin'],
                margin_violation=clearance < p['robot']['clearance_margin']-1e-9,
                crossed_boundary=clearance < -1e-9, decisions=rows,
                assumption_violated=(['braking_lower_bound'] if actual_brake < .8 else []),
                assumption_detected=[], scope='synthetic fixed-boundary witness; no LLM or hardware')
