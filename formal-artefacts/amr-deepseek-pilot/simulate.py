"""Run the protocol-selected source against the five frozen physical scenarios."""
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'amr-deepseek-smoke'))
import smoke
from smoke import trial
from closed_loop import run_supervised_episode
from run_supervisor_suite import trace
from simulation import PARAMETER_PATH, parameters

CASES = [('normal_A', {}), ('normal_B', {'preference': 'B'}),
         ('temporary', {'pedestrian': 'temporary'}),
         ('blackout', {'sensor_blackout': (10., 15.)}),
         ('permanent', {'pedestrian': 'permanent'})]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(run=None, output=None):
    run = Path(run) if run is not None else HERE / 'run'
    output = Path(output) if output is not None else HERE / 'closed-loop'
    summary = trial.summarize(run)
    if not summary['complete'] or summary['selected_candidate'] is None:
        raise ValueError('six chains must terminate and select an accepted source before simulation')
    manifest = trial._manifest(run)
    if manifest['config'] != smoke.CONFIG:
        raise ValueError('simulation requires the frozen live DeepSeek pilot configuration')
    selected = summary['selected_candidate']
    source_path = run / selected['response_path']
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != selected['response_sha256']:
        raise ValueError('selected source identity changed')
    text = raw.decode('utf-8')
    assessment = trial.assess_source(text)
    if not assessment['accepted']:
        raise ValueError('selected source no longer passes unchanged assessment')
    smoke.verify_preparation()
    parameters()  # Refuse drift in the physical parameters before creating output.
    input_paths = [Path(entry['original_path']) for entry in manifest['frozen_files']]
    input_paths += [source_path, run / 'manifest.json', PARAMETER_PATH, Path(__file__).resolve()]
    before = {str(p.resolve()): sha(p) for p in input_paths}
    output.mkdir(exist_ok=False)
    (output / 'selected-source.json').write_bytes(raw)
    (output / 'simulate-snapshot.py').write_bytes(Path(__file__).read_bytes())
    smoke.write_json(output / 'selection.json', {'selection': selected,
                                               'six_chain_summary': summary,
                                               'assessment': assessment,
                                               'created_at_utc': smoke.utc_now()})
    smoke.write_json(output / 'pre-run.json', {'input_sha256': before,
                     'cases': CASES, 'dt': .01, 'horizon': 120.,
                     'python': sys.version, 'platform': platform.platform(),
                     'provenance': 'selected source from recorded live DeepSeek pilot; handwritten calibration paired separately'})
    episodes, comparisons = {}, {}
    for case, config in CASES:
        pair = {}
        for arm in ('handwritten', 'source'):
            key = case + '_' + arm
            with trace(output / (key + '.trace.jsonl.gz')) as emit:
                result = run_supervised_episode(None if arm == 'handwritten' else text,
                    handwritten=arm == 'handwritten', emit=emit, dt=.01, horizon=120., **config)
            # Full event sequence, observations and motion pieces live in the trace.
            compact = {k: v for k, v in result.items() if k not in ('events', 'assessment')}
            smoke.write_json(output / (key + '.json'), compact)
            pair[arm] = compact
            episodes[key] = compact
            print(json.dumps({'episode': key, 'time': compact['time'],
                'completed': compact['completed_robots'], 'grant_order': compact['grant_order'],
                'collision_pairs': compact['collision_pairs'], 'unresolved_pairs': compact['unresolved_pairs'],
                'runtime_rejections': len(compact['runtime_rejections'])}), flush=True)
        fields = ('completed_robots', 'collision_pairs', 'unresolved_pairs', 'early_releases',
                  'completion_mismatches', 'runtime_rejections', 'safe_and_complete')
        comparisons[case] = {
            'equal_scored_outcomes': all(pair['source'][k] == pair['handwritten'][k] for k in fields),
            'equal_grant_order': pair['source']['grant_order'] == pair['handwritten']['grant_order'],
            'time_difference_source_minus_handwritten': pair['source']['time'] - pair['handwritten']['time'],
            'scope': 'legal allocation orders may differ; permanent blocking need not complete'}
    after = {str(p.resolve()): sha(p) for p in input_paths}
    smoke.verify_preparation()
    if before != after:
        raise RuntimeError('simulation inputs changed; retained outputs are not validated')
    result = {'source_selection': selected, 'episode_count': len(episodes),
              'episodes': episodes, 'comparisons': comparisons,
              'inputs_unchanged': True, 'new_model_calls': 0,
              'scope': 'ten related synthetic episodes; not independent industrial tasks or a physical safety theorem'}
    smoke.write_json(output / 'summary.json', result)
    smoke.write_json(output / 'evidence-sha256.json', {
        p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    return result


if __name__ == '__main__':
    execute()
