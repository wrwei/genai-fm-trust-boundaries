"""Timing diagnostics on already audited nominal executions, not a refinement proof."""
import math
from profiles import RobotPlant
from plant import MotionPiece

GRANT, START, TRAVEL, FINISH = .1, 2., 31., 2.
TOL = 1e-7


def close(a, b):
    return abs(a-b) < TOL


def inspect(rows, params):
    goals = {r: params['map']['route_'+r][-1] for r in 'AB'}
    plants = {r: RobotPlant(params['map']['route_'+r][1:]) for r in 'AB'}
    poses = {r: p.pose for r,p in plants.items()}
    speeds = dict.fromkeys('AB', 0.)
    intents = dict.fromkeys('AB', 'Brake')
    source_clocks, sample_clocks = {}, {}
    grants, starts, arrivals, releases, finishes = {}, {}, {}, {}, {}
    commands, delivered = {}, set()
    grant_order = []
    motion_clock, previous = 0., -1.
    samples = {}
    received_samples = set()
    max_age, max_delivery, controller_steps = 0., 0., 0
    for row in rows:
        kind, t = row['kind'], row['time']
        assert t >= previous, ('chronology', t, previous)
        previous = t
        if kind == 'protocol':
            for event in row['events']:
                if event[0] == 'Grant':
                    r = event[1]
                    assert r not in grants
                    grants[r] = t
                    grant_order.append(r)
        elif kind == 'source_step':
            r = row['robot']
            expected = source_clocks.get(r, -.05) + .05
            assert close(t, expected), ('control clock', r, t, expected)
            source_clocks[r] = t
            controller_steps += 1
            if t >= .05:
                assert row['facts']['ObservationUsable'] and not row['facts']['PedestrianBlocked']
        elif kind == 'observation_sample':
            packet = row['packet']; r = packet['robot_id']
            expected = sample_clocks.get(r, -.05) + .05
            assert close(t, expected), ('sample clock', r, t, expected)
            assert not packet['blocked']
            sample_clocks[r] = t
            samples[(r, packet['sample_time'])] = packet
        elif kind == 'observation_received':
            packet = row['packet']; r = packet['robot_id']
            key = (r, packet['sample_time'])
            assert key not in received_samples, ('duplicate sensor delivery', key)
            received_samples.add(key)
            assert packet == samples[key]
            age = t-packet['sample_time']
            assert close(age, .05), ('sensor delivery', age)
            max_age = max(max_age, age)
        elif kind == 'command_issued':
            c = row['command']
            assert c['sequence'] not in commands
            commands[c['sequence']] = c
        elif kind == 'command_applied':
            c = row['command']; r = c['robot']
            assert commands[c['sequence']] == c and c['sequence'] not in delivered
            assert close(t-c['issued'], .1) and close(t, c['delivery']), ('command delivery', t, c)
            assert row['current_check_verdict']
            delivered.add(c['sequence'])
            max_delivery = max(max_delivery, t-c['issued'])
            intents[r] = c['intent']
            if c['intent'] == 'Proceed' and r not in starts:
                assert r in grants
                starts[r] = t
        elif kind == 'release':
            r = row['robot']
            assert r not in releases and not row['actual_body_still_in_Z']
            releases[r] = t
        elif kind == 'complete':
            r = row['robot']
            assert r not in finishes and r in releases and r in arrivals
            assert (close(row['actual_speed'], 0.) and close(speeds[r], 0.)
                    and math.dist(poses[r][:2], goals[r]) <= .01
                    and all(close(a,b) for a,b in zip(poses[r], row['actual_pose']))), ('finish physical', r)
            finishes[r] = t
        elif kind == 'motion':
            assert close(t, motion_clock) and close(row['duration'], .01), ('motion clock', t, motion_clock)
            assert not row['actual_pedestrian_present']
            for r, raw_pieces in row['robots'].items():
                offset = 0.
                for raw in raw_pieces:
                    piece = MotionPiece.from_dict(raw)
                    assert all(close(a,b) for a,b in zip(piece.start_pose, poses[r]))
                    assert close(piece.initial_speed, speeds[r])
                    poses[r] = piece.sample(piece.duration)
                    speeds[r] = piece.initial_speed + piece.acceleration*piece.duration
                    offset += piece.duration
                    if r not in arrivals and math.dist(poses[r][:2], goals[r]) < TOL and abs(speeds[r]) < TOL:
                        arrivals[r] = t+offset
                assert close(offset, row['duration'])
                # This obligation is empirically true in these four nominal traces.
                # It is not assumed for arbitrary interruptions or early goal braking.
                if r in starts and r not in arrivals:
                    assert intents[r] == 'Proceed', ('held Proceed before arrival', r, t)
            motion_clock = t+row['duration']
    assert len(grant_order) == 2 and set(grant_order) == set('AB')
    assert set(starts) == set(arrivals) == set(releases) == set(finishes) == set('AB')
    assert delivered == set(commands)
    due_samples = {key for key in samples if key[1]+.05 <= previous+TOL}
    assert received_samples == due_samples, ('sensor delivery completeness',
                                             len(received_samples), len(due_samples))
    assert all(close(source_clocks[r], finishes[r]) for r in 'AB')
    assert all(close(sample_clocks[r], max(finishes.values())) for r in 'AB')
    first, second = grant_order
    assert grants[first] <= GRANT+TOL
    assert grants[second] <= releases[first]+GRANT+TOL
    tasks = {}
    for r in 'AB':
        assert starts[r]-grants[r] <= START+TOL
        assert arrivals[r]-starts[r] <= TRAVEL+TOL
        assert releases[r] <= arrivals[r]+TOL
        assert 0 <= finishes[r]-arrivals[r] <= FINISH+TOL
        tasks[r] = dict(grant=grants[r], start=starts[r], arrival_at_rest=arrivals[r],
                        release=releases[r], finish=finishes[r], start_delay=starts[r]-grants[r],
                        travel_duration=arrivals[r]-starts[r], finish_delay=finishes[r]-arrivals[r])
    budget = round(2*(GRANT+START+TRAVEL+FINISH), 10)
    assert max(finishes.values()) <= budget
    return dict(passed=True, grant_order=grant_order, tasks=tasks, controller_steps=controller_steps,
                max_observation_delivery=max_age, max_command_delivery=max_delivery,
                last_completion=max(finishes.values()), conditional_two_task_budget=budget,
                scope='local obligation checks on retained traces; universal discharge remains open')
