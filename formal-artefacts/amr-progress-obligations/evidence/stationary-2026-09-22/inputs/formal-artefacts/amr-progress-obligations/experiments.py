"""Fixed profile comparisons and one constructed non-progressing plant witness."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
import sys
from types import FunctionType

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
BINDING = BASE.parent/'amr-runtime-binding'
sys.path.insert(0, str(BINDING))
from binding import SOURCE_ID
from binding_conformance import HOLTable
from physical_binding import run_episode
from physical import effective_parameters
from source_check import language
from source_link_audit import SourceLinkAudit
from profiles import RobotPlant, StationaryPlant, route
from plant import MotionPiece
from trace_obligations import inspect as inspect_trace


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')


def load_trace(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def verify_retained():
    counts = {}
    for name in ('amr-runtime-binding', 'amr-extraction-faithfulness'):
        parent = BASE.parent/name
        manifest = json.loads((parent/'evidence-manifest.json').read_bytes())
        for file, value in manifest['files'].items():
            assert sha(parent/file) == value['sha256'], ('retained artifact drift', name, file)
        counts[name] = len(manifest['files'])
    return counts


def compare_profile(points, speed, accel, brake, turn_rate):
    predicted = route(points, speed, accel, brake, turn_rate)
    plant = RobotPlant(points, speed_limit=speed, accel=accel, brake=brake, turn_rate=turn_rate)
    pieces = plant.advance(predicted['upper_bound']+.25, 'Proceed')
    moving_duration = sum(p.duration for p in pieces if p.initial_speed != 0 or p.acceleration != 0 or p.angular_velocity != 0)
    distance = sum(p.initial_speed*p.duration + .5*p.acceleration*p.duration**2 for p in pieces)
    assert plant.finished and plant.speed == 0.
    assert math.dist(plant.pose[:2], points[-1]) < 1e-8
    assert abs(moving_duration-predicted['duration']) < 1e-8
    assert abs(distance-predicted['total_length']) < 1e-8
    assert moving_duration <= predicted['upper_bound']+1e-8
    for s in predicted['segments']:
        assert s['duration'] <= s['upper_bound']+1e-8
        assert abs(s['integrated_distance']-s['length']) < 1e-8
        assert s['peak'] <= speed and s['peak'] > 0
        assert s['cruise_distance'] == 0 or s['peak'] == speed
    return dict(predicted=predicted, actual_moving_duration=moving_duration,
                actual_distance=distance, actual_terminal_pose=plant.pose, actual_terminal_speed=plant.speed,
                pieces=[p.to_dict() for p in pieces], passed=True)


def profile_matrix(params):
    cases = []
    for length, accel, brake, speed in itertools.product((.01,1.625,4.),(.25,.5,1.),(.4,.8),(.5,1.)):
        cases.append(compare_profile([(0,0),(length,0)], speed, accel, brake, math.pi/2))
    defaults = {k: v.default for k,v in inspect.signature(RobotPlant).parameters.items()
                if k in ('speed_limit','accel','brake','turn_rate')}
    assert defaults == dict(speed_limit=1., accel=.5, brake=.8, turn_rate=math.pi/2)
    nominal = {r: compare_profile(params['map']['route_'+r][1:], defaults['speed_limit'],
                      defaults['accel'], defaults['brake'], defaults['turn_rate']) for r in 'AB'}
    # Fixed rational ceiling certificate: segment lengths 2, sqrt(8), 8, sqrt(8), 4.
    ceiling_lengths = (2.,3.,8.,3.,4.)
    for r in 'AB':
        lengths = [s['length'] for s in nominal[r]['predicted']['segments']]
        assert all(x <= b for x,b in zip(lengths, ceiling_lengths))
        assert nominal[r]['predicted']['turn_time'] <= 2.+1e-10
        assert nominal[r]['predicted']['upper_bound'] < 30.125 < 31.
    return dict(passed=True, straight_cases=cases, nominal_routes=nominal,
                comparisons=len(cases)+len(nominal), exact_reference_defaults=defaults,
                rational_route_ceiling=30.125, diagnostic_route_budget=31.,
                warning='accel is exact reference acceleration; an upper bound alone is insufficient')


def nominal_obligations(params):
    old = BINDING/'evidence/run-2026-09-22'
    summary = json.loads((old/'summary.json').read_bytes())
    reports = []
    for run in summary['results']:
        path = old/run['trace']
        assert sha(path) == run['trace_sha256']
        report = inspect_trace(load_trace(path), params)
        reports.append(dict(name=run['name'], trace_sha256=sha(path), **report))
    return reports


def witness_audit(path, result, params):
    from binding import SourceController
    source = SourceController.from_selected()
    source_audit = SourceLinkAudit(params, language.parse_program(source.raw.decode('utf-8')))
    table = HOLTable()
    ref = {r: RobotPlant(params['map']['route_'+r][1:]) for r in 'AB'}
    starts = {r: p.pose for r,p in ref.items()}
    intents = dict.fromkeys('AB','Brake')
    counts = Counter()
    previous, first_mismatch = None, None
    advances, proceed_times = 0, []
    last_motion = 0.
    last_time = -1.
    for row in load_trace(path):
        counts[row['kind']] += 1
        assert row['time'] >= last_time
        last_time = row['time']
        source_audit.observe(row)
        if row['kind'] == 'adapter':
            assert table.check(row)
            if previous is not None:
                assert row['before'] == previous
            previous = row['after']
        elif row['kind'] == 'command_applied':
            assert row['current_check_verdict']
            r = row['command']['robot']
            intents[r] = row['command']['intent']
            if intents[r] == 'Proceed':
                proceed_times.append(dict(robot=r, time=row['time']))
        elif row['kind'] == 'observation_sample':
            packet = row['packet']
            assert tuple(packet['pose']) == starts[packet['robot_id']] and packet['speed'] == 0.
        elif row['kind'] == 'motion':
            assert abs(row['time']-last_motion) < 1e-7 and row['duration'] == .01
            last_motion = row['time']+.01
            for r,pieces in row['robots'].items():
                duration = 0.
                for raw in pieces:
                    p = MotionPiece.from_dict(raw)
                    assert p.start_pose == starts[r]
                    assert p.initial_speed == p.acceleration == p.angular_velocity == 0.
                    assert p.sample(p.duration) == starts[r]
                    duration += p.duration
                assert abs(duration-.01) < 1e-10
                advances += 1
                if first_mismatch is None:
                    replay = ref[r].advance(.01, intents[r])
                    if any(p.initial_speed != 0 or p.acceleration != 0 or p.angular_velocity != 0 for p in replay):
                        first_mismatch = dict(time=row['time'], robot=r, intent=intents[r],
                           exact_reference_pieces=[p.to_dict() for p in replay], actual_stationary_pieces=pieces)
    source_audit.finish()
    assert last_motion == 120. and last_time == 120.
    assert result['grant_order'] == ['A'] and result['completed_robots'] == []
    assert result['termination'] == 'horizon' and result['time'] == 120.
    assert proceed_times and first_mismatch is not None
    assert not result['collision_pairs'] and not result['unresolved_pairs']
    assert not result['early_releases'] and not result['reference_violations']
    assert not result['completion_mismatches'] and not counts['complete'] and not counts['release']
    return dict(expected_outcome_observed=True, counts=dict(counts), zero_motion_intervals=advances,
                applied_proceed=proceed_times, first_exact_plant_refinement_failure=first_mismatch,
                upper_speed_acceleration_envelope=True, completed_robots=[],
                scope='constructed stationary mutation; HOL adapter/source-link checks pass; exact reference plant replay rejects')


def run():
    evidence = BASE/'evidence'
    evidence.mkdir(exist_ok=True)
    retained = verify_retained()
    params = effective_parameters()
    write(evidence/'profiles.json', profile_matrix(params))
    write(evidence/'nominal-obligations.json', nominal_obligations(params))
    out = evidence/'stationary-2026-09-22'
    out.mkdir(exist_ok=False)
    # Freeze loaded module dependencies, including the actual accepted source.
    dependencies = {}
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.is_file() and path.is_relative_to(REPO):
                dependencies[path.relative_to(REPO).as_posix()] = sha(path)
    parameter_file = REPO/'literature/scholar_search_2026-09-10/followup/research_amr_parameters_2026-09-15.json'
    dependencies[parameter_file.relative_to(REPO).as_posix()] = sha(parameter_file)
    for spec in ('specs/2026-09-22-amr-progress-obligations-design.md', 'plans/2026-09-22-amr-progress-obligations.md'):
        p = REPO/'docs/superpowers'/spec
        dependencies[p.relative_to(REPO).as_posix()] = sha(p)
    write(out/'pre-run.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
          case='stationary positive-progress assumption removed', horizon=120., advice_events=[], pedestrian='none',
          source_id=SOURCE_ID, dependencies=dependencies, previous_manifests_verified=retained,
          expected='A granted and Proceed applied; no motion or completion; exact reference replay rejects',
          substitution='same function code object, shallow copy of globals, RobotPlant -> StationaryPlant', api_calls=0))
    write(out/'effective-parameters.json', params)
    original_plant = run_episode.__globals__['RobotPlant']
    clone = FunctionType(run_episode.__code__, {**run_episode.__globals__, 'RobotPlant':StationaryPlant},
                         name='stationary_witness', argdefs=run_episode.__defaults__, closure=run_episode.__closure__)
    clone.__kwdefaults__ = dict(run_episode.__kwdefaults__)
    path = out/'trace.jsonl.gz'
    with gzip.open(path, 'xt', encoding='utf-8') as stream:
        def emit(row):
            stream.write(json.dumps(row, separators=(',',':'))+'\n')
        result = clone(advice_events=(), pedestrian='none', horizon=120., emit=emit)
    assert run_episode.__globals__['RobotPlant'] is original_plant is RobotPlant
    result.update(trace_sha256=sha(path), constructed_mutation='StationaryPlant')
    write(out/'summary.json', result)
    write(out/'audit.json', witness_audit(path, result, params))
    assert verify_retained() == retained
    print(json.dumps(dict(profiles=38, retained_runs=4, witness=result['termination'],
                         granted=result['grant_order'], completed=result['completed_robots'], api_calls=0)))


if __name__ == '__main__':
    run()
