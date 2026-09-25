"""Offline trace audit: HOL steps, raw source, command causality and independent geometry.
Shares the established source interpreter and reference plant, not the driver or its geometry.
"""
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from binding import HERE, V2, SOURCE_ID
from binding_conformance import HOLTable
from source_check import language, ROOT
from source_link_audit import SourceLinkAudit

spec = importlib.util.spec_from_file_location('independent_v2_geometry', V2/'physical-audit.py')
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
from plant import RobotPlant


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    out = HERE/'evidence/run-2026-09-22'
    plan = json.loads((out/'pre-run.json').read_bytes())
    summary = json.loads((out/'summary.json').read_bytes())
    params = json.loads((out/'effective-parameters.json').read_bytes())
    from physical import effective_parameters
    assert params == effective_parameters()
    assert sorted(r['name'] for r in summary['results']) == sorted(c[0] for c in plan['cases'])
    assert len(summary['results']) == len(plan['cases']) == 4
    for path, digest in plan['identities'].items():
        assert sha(ROOT/path) == digest, ('changed dependency', path)
    selected = json.loads((V2/'evidence/source/summary.json').read_bytes())['selected']
    source_bytes = (ROOT/selected['path']).read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == SOURCE_ID
    program = language.parse_program(source_bytes.decode('utf-8'))
    table = HOLTable()
    results = []
    for result in summary['results']:
        assert json.loads((out/(result['name']+'.summary.json')).read_bytes()) == result
        path = out/result['trace']
        assert sha(path) == result['trace_sha256']
        counts = Counter()
        source_link = SourceLinkAudit(params, program)
        robots = {r: RobotPlant(params['map']['route_'+r][1:]) for r in 'AB'}
        intents = {r: 'Brake' for r in 'AB'}
        previous = None
        latest_adapter = None
        issued = {}
        samples, received = {}, {}
        grants, releases, finishes, deliveries = [], [], [], []
        last_time = -1.
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                kind, t = row['kind'], row['time']
                assert t >= last_time
                last_time = t
                counts[kind] += 1
                source_link.observe(row)
                if kind == 'adapter':
                    assert table.check(row), ('HOL correspondence', result['name'], t, row)
                    if previous is None:
                        assert row['before'] == dict(core=dict(req_a=False, req_b=False, owner=None,
                            blocked=False, fresh=True, pending=None, command=None), requested=False, slot=None)
                    else:
                        assert row['before'] == previous
                    previous = row['after']
                    latest_adapter = row
                    if row['event'][0] == 'Provider':
                        deliveries.append([t] + row['raw_input'][1:])
                    if row['source'] is not None:
                        source = row['source']
                        assert language.eval_select(program, source['facts']) == source['raw_action']
                        assert source['source_id'] == SOURCE_ID
                        assert source['latch']['advice'] == row['before']['slot']
                elif kind == 'protocol':
                    assert latest_adapter['event'][0] == 'Trusted'
                    assert row['before'] == latest_adapter['before']['core']
                    assert row['after'] == latest_adapter['after']['core']
                    assert row['input'] == latest_adapter['event'][1]
                    assert row['events'] == latest_adapter['events']
                    for event in row['events']:
                        if event[0] == 'Grant':
                            grants.append(event[1])
                elif kind == 'source_step':
                    assert list(language.eval_step(program, row['prior_mode'], row['facts'])) == [row['raw_action'], row['raw_next']]
                    assert row['source_id'] == SOURCE_ID
                elif kind == 'source_select':
                    assert language.eval_select(program, row['facts']) == row['raw_action']
                elif kind == 'observation_sample':
                    packet = row['packet']; r = packet['robot_id']
                    assert geometry.close(packet['pose'], robots[r].pose)
                    assert geometry.close(packet['speed'], robots[r].speed)
                    assert packet['blocked'] is False
                    samples[(r, packet['sample_time'])] = packet
                elif kind == 'observation_received':
                    packet = row['packet']; r = packet['robot_id']
                    assert packet == samples[(r, packet['sample_time'])]
                    assert geometry.close(t-packet['sample_time'], .05)
                    received[r] = packet
                elif kind == 'command_issued':
                    c = row['command']; issued[c['sequence']] = c
                    assert geometry.close(c['delivery']-t, .10)
                elif kind == 'command_applied':
                    c = row['command']; r = c['robot']
                    assert c == issued[c['sequence']]
                    assert geometry.close(robots[r].pose, row['actual_pose'])
                    assert geometry.close(robots[r].speed, row['actual_speed'])
                    valid = c['delivery']-1e-9 <= t <= c['expiry']+1e-9
                    if c['intent'] == 'Proceed' and c['scope'] == 'reservation_zone':
                        assert latest_adapter['raw_input'] == ['Apply']
                        before = latest_adapter['before']['core']
                        valid &= (before['owner'] == r and before['command'] == r
                                  and c['generation'] == row['reservation_generation']
                                  and c['mission'] == 'mission-'+r and before['fresh'] and not before['blocked'])
                        assert (['Proceed', r] in latest_adapter['events']) == bool(valid)
                    elif c['intent'] == 'Proceed':
                        valid &= r in releases and t-received[r]['sample_time'] <= .1+1e-9 and not received[r]['blocked']
                    assert bool(valid) == row['current_check_verdict']
                    if valid:
                        intents[r] = c['intent']
                    assert intents[r] == row['actuator_intent']
                elif kind == 'release':
                    r = row['robot']
                    assert geometry.close(row['pose'], robots[r].pose)
                    assert geometry.gap(row['pose'], (.8, .6), (12, 0, 0), (12, 5.2)) > 0
                    assert row['actual_body_still_in_Z'] is False
                    releases.append(r)
                elif kind == 'complete':
                    r = row['robot']
                    assert geometry.close(row['actual_pose'], robots[r].pose)
                    assert abs(robots[r].speed) < 1e-9
                    assert math.dist(robots[r].pose[:2], params['map']['route_'+r][-1]) <= .01
                    finishes.append(r)
                elif kind == 'motion':
                    assert row['actual_pedestrian_present'] is False
                    for r, pieces in row['robots'].items():
                        replay = [p.to_dict() for p in robots[r].advance(row['duration'], intents[r])]
                        assert geometry.close(replay, pieces), ('actuator/plant mismatch', t, r)
                        counts['plant_intervals'] += 1
                    bodies = {r: (lambda u, ps=ps: geometry.at(ps, u), (.8, .6), geometry.speed_bound(ps))
                              for r, ps in row['robots'].items()}
                    pairs = [(bodies['A'], bodies['B'])]
                    for body in bodies.values():
                        for x in (9.75, 14.25):
                            for y in (-.87, .87):
                                pairs.append((body, (lambda u, x=x, y=y: (x, y, 0), (3.5, .14), 0)))
                    for a, b in pairs:
                        geometry.sweep(a[0], a[1], a[2], b[0], b[1], b[2], row['duration'], counts)
                        counts['continuous_pair_intervals'] += 1
        expected_case = next(c for c in plan['cases'] if c[0] == result['name'])
        source_link.finish()
        assert deliveries == expected_case[1]
        assert len(finishes) == 2 and set(finishes) == {'A', 'B'}
        assert grants == result['grant_order'] and grants[0] == expected_case[2]
        assert len(releases) == 2
        for r in 'AB':
            assert geometry.close(robots[r].pose, result['final_poses'][r])
            assert geometry.close(robots[r].speed, result['final_speeds'][r])
        results.append(dict(name=result['name'], counts=dict(counts), grants=grants,
                            replies=deliveries, finishes=finishes, trace_sha256=sha(path)))
        print(result['name'], 'audit passed', flush=True)
    mechanisms = json.loads((out/'mechanisms.json').read_bytes())
    from run_experiments import mechanisms as recompute_mechanisms
    # Retained JSON uses arrays where the executable protocol uses tuples.
    assert mechanisms == json.loads(json.dumps(recompute_mechanisms()))
    assert len(mechanisms) == 11 and all(r['expected_outcome_observed'] for r in mechanisms)
    report = dict(passed=True, runs=results, totals=dict(sum((Counter(r['counts']) for r in results), Counter())),
                  mechanism_outcomes=11, dependencies_verified=len(plan['identities']),
                  audit_sha256=sha(Path(__file__)), independent_geometry_sha256=sha(V2/'physical-audit.py'),
                  source_link_audit_sha256=sha(HERE/'source_link_audit.py'),
                  scope='HOL transition table, exact source and reference-plant replay; independent geometry; no hardware or continuous refinement theorem')
    (out/'execution-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['totals']))
    return report


if __name__ == '__main__':
    audit()
