"""Run the fixed, exploratory reference suite and retain replayable evidence."""
import argparse
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
from contextlib import contextmanager

from simulation import run_episode, run_stopping_witness, geometry_witness, PARAMETER_PATH

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


@contextmanager
def trace_writer(path):
    # Fixed gzip header for identical event streams on the same implementation.
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding='utf-8', newline='\n') as output:
                def emit(row):
                    output.write(json.dumps(row, separators=(',', ':'), allow_nan=False)+'\n')
                yield emit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New evidence directory; existing directories are not overwritten')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source_before = {p.name:digest(p) for p in sorted(HERE.glob('*.py'))}
    parameter_before = digest(PARAMETER_PATH)
    cases = [
        ('C01_A_first', {}),
        ('C01_B_first', dict(preference='B')),
        ('C10_temporary_pedestrian', dict(pedestrian='temporary')),
        ('C12_permanent_pedestrian', dict(pedestrian='permanent')),
        ('C12_always_stop', dict(always_stop=True)),
        ('C05_front_only_release', dict(front_only=True)),
        ('C08_observation_blackout', dict(sensor_blackout=(10., 15.))),
    ]
    episodes = {}
    for case_id, config in cases:
        with trace_writer(args.output/(case_id+'.trace.jsonl.gz')) as emit:
            result = run_episode(**config, emit=emit)
        write_json(args.output/(case_id+'.json'), result)
        episodes[case_id] = {key: value for key, value in result.items() if key != 'events'}
        print(json.dumps(dict(case=case_id, completed=result['completed_robots'], time=result['time'],
                              collisions=result['collision_pairs'], unresolved=result['unresolved_pairs'],
                              early_releases=len(result['early_releases'])), ensure_ascii=True), flush=True)
    stopping = {}
    for case_id, config in [('C07_full_bound', {}), ('C07_omit_reaction', dict(omit_reaction=True)),
                            ('C12_weak_brake', dict(actual_brake=.4))]:
        with trace_writer(args.output/(case_id+'.trace.jsonl.gz')) as emit:
            result = run_stopping_witness(**config, emit=emit)
        write_json(args.output/(case_id+'.json'), result)
        stopping[case_id] = {key: value for key, value in result.items() if key != 'decisions'}
        print(json.dumps(dict(case=case_id, clearance=result['clearance'], margin_violation=result['margin_violation'],
                              crossed_boundary=result['crossed_boundary']), ensure_ascii=True), flush=True)

    # New runs, not fixed-action replay: monitor/event periods remain the same.
    refinements = {}
    for case_id, config in cases:
        if case_id not in ('C01_A_first', 'C10_temporary_pedestrian', 'C05_front_only_release'):
            continue
        with trace_writer(args.output/(case_id+'.dt005.trace.jsonl.gz')) as emit:
            fine = run_episode(**config, dt=.005, emit=emit)
        write_json(args.output/(case_id+'.dt005.json'), fine)
        coarse = episodes[case_id]
        fields = ['completed_robots', 'grant_order', 'collision_pairs', 'unresolved_pairs', 'safe_and_complete']
        refinements[case_id] = dict(dt=.005,
                                   same_outcomes=all(coarse[k] == fine[k] for k in fields),
                                   time_difference=abs(coarse['time']-fine['time']),
                                   max_final_coordinate_difference=max(abs(x-y) for name in ('A', 'B') for x,y in zip(coarse['final_poses'][name], fine['final_poses'][name])),
                                   coarse_early_release_count=len(coarse['early_releases']), fine_early_release_count=len(fine['early_releases']))
        print(json.dumps(dict(refinement=case_id, **refinements[case_id])), flush=True)
    for case_id, omit in [('C07_full_bound', False), ('C07_omit_reaction', True)]:
        with trace_writer(args.output/(case_id+'.dt005.trace.jsonl.gz')) as emit:
            fine = run_stopping_witness(omit_reaction=omit, dt=.005, emit=emit)
        coarse = stopping[case_id]
        write_json(args.output/(case_id+'.dt005.json'), fine)
        refinements[case_id] = dict(dt=.005, same_outcomes=fine['margin_violation'] == coarse['margin_violation'] and fine['crossed_boundary'] == coarse['crossed_boundary'],
                                   clearance_difference=abs(fine['clearance']-coarse['clearance']))
    write_json(args.output/'summary.json', dict(scope='Exploratory synthetic reference environment; no LLM or proof',
                                               episodes=episodes, stopping=stopping, geometry=geometry_witness(), refinements=refinements))
    source_after = {p.name:digest(p) for p in sorted(HERE.glob('*.py'))}
    manifest = dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    python=sys.version, platform=platform.platform(),
                    parameters=dict(path=str(PARAMETER_PATH), sha256=digest(PARAMETER_PATH)),
                    code_sha256=source_before, code_sha256_after=source_after,
                    code_stable_during_run=source_before == source_after,
                    parameters_stable_during_run=parameter_before == digest(PARAMETER_PATH),
                    test_sha256={p.name:digest(p) for p in sorted((HERE/'tests').glob('test_*.py'))},
                    files_sha256={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()},
                    full_episodes=10, stopping_runs=5, geometry_fixtures=1, llm_calls=0, new_formal_builds=0,
                    limits=['Synthetic dynamics and sensing', 'No generated supervisor', 'No universal pedestrian safety',
                            'Floating-point oracle bounds are not formal proofs', 'No hardware calibration or certification'])
    write_json(args.output/'manifest.json', manifest)
    if not manifest['code_stable_during_run'] or not manifest['parameters_stable_during_run']:
        raise RuntimeError('Source or parameters changed during the run; evidence retained but provenance is invalid')


if __name__ == '__main__':
    main()
