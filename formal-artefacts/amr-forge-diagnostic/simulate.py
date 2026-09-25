"""Conditional exploratory physics for one protocol-selected live diagnostic source.

This module has no transport entry point. Offline ledgers may be checked by
verify_evidence, but execute always requires a completed live diagnostic.
"""
from __future__ import annotations

from contextlib import contextmanager
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner
import diagnostics

SUPERVISOR = HERE.parent / 'amr-supervisor'
CORRIDOR = HERE.parent / 'amr-corridor'
CASES = [('normal_A', {}), ('normal_B', {'preference': 'B'}),
         ('temporary', {'pedestrian': 'temporary'}),
         ('blackout', {'sensor_blackout': (10., 15.)}),
         ('permanent', {'pedestrian': 'permanent'})]
SCOPE = ('one observed candidate selected from four related diagnostic repair trajectories; '
         'ten related synthetic episodes, exploratory only; not an independent evaluation, '
         'a population success rate, or a physical safety theorem')


def selected_record(result):
    """Enforce the predeclared order before any physical episode is possible."""
    if result.get('stop') != 'protocol_complete':
        raise ValueError('physics requires stop protocol_complete')
    states = result.get('conditions', {})
    ids = [cid for cid, _, _ in runner.CONDITIONS]
    if set(states) != set(ids) or any(
            states[cid].get('stop') not in ('accepted', 'cycle', 'repair_limit') for cid in ids):
        raise ValueError('all four diagnostic conditions must be terminal without a fatal stop')
    selected = result.get('selected_for_exploratory_physics')
    first = next((cid for cid in ids if states[cid]['stop'] == 'accepted'), None)
    if first is None or not isinstance(selected, dict):
        raise ValueError('physics requires an accepted source selection')
    state = states[first]
    limit = dict((cid, n) for cid, n, _ in runner.CONDITIONS)[first]
    expected = {'condition': first, 'limit': limit,
                'response_path': state.get('accepted_response'),
                'repair': state.get('first_accepted_repair')}
    if (set(selected) != set(expected) | {'sha256'}
            or any(selected.get(key) != value for key, value in expected.items())
            or state.get('limit') != limit or type(selected.get('repair')) is not int
            or not 1 <= selected['repair'] <= runner.MAX_REPAIRS):
        raise ValueError('recorded selection differs from predeclared condition/repair order')
    return selected


def verify_evidence(run, result):
    """Read-only integrity check; deliberately does not authorize physics."""
    run = Path(run).resolve()
    manifest = runner.read_json(run / 'evidence-sha256.json')
    observed = runner.inventory(run)
    observed.pop('evidence-sha256.json', None)
    if manifest != observed or runner.read_json(run / 'result.json') != result:
        raise ValueError('diagnostic evidence manifest does not match exact run bytes')
    selected = selected_record(result)
    runner.verify_inputs(run)
    states, outcomes = runner.replay(run)
    public = {cid: {key: value for key, value in state.items()
                    if key not in ('history', 'keys', 'text', 'report')}
              for cid, state in states.items()}
    for cid, state in states.items():
        public[cid]['checkpoint_at_two'] = (
            {'executed_repairs': 2, 'assessment': state['trajectory'][1]} if state['repairs'] >= 2 else
            {'executed_repairs': state['repairs'], 'terminal_before_two': state['stop'],
             'assessment': state['trajectory'][-1] if state['trajectory'] else None})
    public = json.loads(runner.json_bytes(public))
    if public != result['conditions']:
        raise ValueError('diagnostic terminal states differ from replayed evidence')
    if (result.get('new_calls') != len(outcomes)
            or len(list((run / 'attempts').iterdir())) != len(outcomes)
            or any('fatal' not in out or out['fatal'] is not None for out in outcomes)):
        raise ValueError('diagnostic outcome ledger is incomplete or fatal')
    source = (run / selected['response_path']).resolve()
    if (source.name != 'response.bin' or source.parent.parent != run / 'attempts'
            or not source.parent.name.isdigit()):
        raise ValueError('selected response path is outside the diagnostic attempt ledger')
    raw = source.read_bytes()
    if runner.sha(source) != selected['sha256']:
        raise ValueError('selected raw response sha256 changed')
    outcome = runner.read_json(source.parent / 'outcome.json')
    if (outcome.get('fatal', 'missing') is not None or outcome.get('accepted') is not True
            or outcome.get('condition') != selected['condition']
            or outcome.get('repair') != selected['repair']
            or outcome['files_sha256'].get('response.bin') != selected['sha256']):
        raise ValueError('selected outcome is not the exact accepted nonfatal response')
    # Check the selected UTF-8 source against the preserved provider envelope.
    decoded, _, usage_summary, fatal = runner.decode_response(
        source.parent, runner.read_json(source.parent / 'transport.json'),
        runner.read_json(source.parent / 'http-request.json'))
    if decoded != raw or fatal is not None or usage_summary != outcome.get('usage_summary'):
        raise ValueError('selected response does not match the recorded transport evidence')
    report = diagnostics.assess(raw.decode('utf-8'), selected['limit'])
    if not report['accepted'] or report['source_sha256'] != selected['sha256']:
        raise ValueError('selected source fails fresh assessment under its diagnostic profile')
    return raw, report


def verify_live_selection(run):
    """The only deployment gate: complete live evidence, then fresh assessment."""
    run = Path(run).resolve()
    result = runner.read_json(run / 'result.json')
    if result.get('mode') != 'live':
        raise ValueError('physics requires a live diagnostic result, never an offline fixture')
    selected = selected_record(result)
    protocol = runner.read_json(run / 'protocol.json')
    if (protocol.get('mode') != 'live'
            or protocol.get('id') != 'amr-forge-diagnostic/v1'
            or result.get('protocol_id') != protocol['id']
            or protocol.get('model_config') != runner.smoke.CONFIG
            or protocol.get('conditions') != [list(row) for row in runner.CONDITIONS]):
        raise ValueError('live protocol identity or frozen configuration differs')
    raw, report = verify_evidence(run, result)
    return result, selected, raw, report


def load_physics(limit):
    """Keep old physics bytes intact except two package-relative checker imports."""
    language, _, assurance = diagnostics._profile(limit)
    original = SUPERVISOR / 'closed_loop.py'
    raw = original.read_bytes()
    adapted = raw
    edits = [(b'from language import parse_program, eval_select, eval_step',
              b'from .language import parse_program, eval_select, eval_step'),
             (b'from assurance import assess_source, selection_violations, step_violations, obligation',
              b'from .assurance import assess_source, selection_violations, step_violations, obligation')]
    for before, after in edits:
        if adapted.count(before) != 1:
            raise ValueError('frozen physics checker import no longer matches adaptation')
        adapted = adapted.replace(before, after)
    package = language.__package__
    name = package + '._exploratory_closed_loop'
    module = types.ModuleType(name)
    module.__file__ = str(original)
    module.__package__ = package
    # The original __file__ preserves the original physical module paths.
    # No global language/assurance module or checker constant is replaced.
    previous_path = sys.path[:]
    try:
        exec(compile(adapted, str(original), 'exec'), module.__dict__)
    finally:
        sys.path[:] = previous_path
    for dependency in ('controller', 'plant', 'oracle', 'simulation'):
        if Path(sys.modules[dependency].__file__).resolve() != (CORRIDOR / (dependency + '.py')).resolve():
            raise ValueError('unexpected cached physical dependency: ' + dependency)
    if module.parse_program is not language.parse_program or module.assess_source is not assurance.assess_source:
        raise ValueError('physics loaded a mismatched diagnostic checker')
    provenance = {'adaptation': 'only language and assurance imports made package-relative',
                  'original_path': original.relative_to(runner.ROOT).as_posix(),
                  'original_sha256': runner.sha(original),
                  'adapted_sha256': hashlib.sha256(adapted).hexdigest(),
                  'package': package, 'rule_limit': limit,
                  'unchanged': 'all physical equations, schedules and independent collision oracle',
                  'imports': [[a.decode(), b.decode()] for a, b in edits]}
    module.adapted_source_bytes = adapted
    return module, provenance


@contextmanager
def trace(path):
    with Path(path).open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding='utf-8', newline='\n') as stream:
                yield lambda row: stream.write(json.dumps(row, separators=(',', ':'), allow_nan=False) + '\n')


def execute(run=None, output=None):
    run = Path(run) if run is not None else HERE / 'run'
    output = Path(output) if output is not None else HERE / 'closed-loop'
    diagnostic, selected, raw, assessment = verify_live_selection(run)
    physics, adaptation = load_physics(selected['limit'])
    physics.parameters()  # Refuse parameter drift before creating any output.
    if output.resolve().is_relative_to(run.resolve()):
        raise ValueError('physics output must be separate from immutable diagnostic evidence')
    frozen = runner.read_json(run / 'frozen-inputs.json')
    required = [SUPERVISOR / 'closed_loop.py', HERE / 'profiles/snapshot.json']
    required += [CORRIDOR / (name + '.py') for name in ('controller', 'plant', 'oracle', 'simulation')]
    required += [HERE / 'profiles' / ('rules' + str(selected['limit'])) / (name + '.py')
                 for name in ('language', 'model', 'assurance')]
    if any(path.relative_to(runner.ROOT).as_posix() not in frozen for path in required):
        raise ValueError('original physics and checker dependencies were not frozen before diagnostic dispatch')
    # This stage freezes its adapter independently before the first episode.
    # Selection and scenarios were declared in the earlier diagnostic protocol.
    required.append(Path(__file__).resolve())
    input_paths = {runner.ROOT / name for name in frozen}
    input_paths |= set(required)
    input_paths |= {path for path in run.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    input_paths.add(Path(sys.modules['simulation'].PARAMETER_PATH))
    before = {str(path.resolve()): runner.sha(path) for path in sorted(input_paths)}
    output.mkdir(exist_ok=False)
    (output / 'selected-source.json').write_bytes(raw)
    (output / 'simulate-snapshot.py').write_bytes(Path(__file__).read_bytes())
    (output / 'closed-loop-adapted.py').write_bytes(physics.adapted_source_bytes)
    runner.write_json(output / 'selection.json', {
        'selection': selected, 'diagnostic_result_sha256': runner.sha(run / 'result.json'),
        'diagnostic_evidence_sha256': runner.sha(run / 'evidence-sha256.json'),
        'assessment': runner.compact(assessment), 'scope': SCOPE})
    runner.write_json(output / 'pre-run.json', {
        'input_sha256': before, 'adaptation': adaptation, 'cases': CASES, 'dt': .01,
        'horizon': 120., 'python': sys.version, 'platform': platform.platform(),
        'created_at_utc': runner.smoke.utc_now(), 'provenance': 'recorded live diagnostic source',
        'new_model_calls': 0, 'scope': SCOPE})
    episodes, comparisons = {}, {}
    for case, config in CASES:
        pair = {}
        for arm in ('handwritten', 'source'):
            key = case + '_' + arm
            with trace(output / (key + '.trace.jsonl.gz')) as emit:
                result = physics.run_supervised_episode(
                    None if arm == 'handwritten' else raw.decode('utf-8'),
                    handwritten=arm == 'handwritten', emit=emit, dt=.01, horizon=120., **config)
            if arm == 'source' and result['source_id'] != selected['sha256']:
                raise RuntimeError('physical episode used a different source identity')
            compact = {key: value for key, value in result.items() if key not in ('events', 'assessment')}
            runner.write_json(output / (key + '.json'), compact)
            pair[arm] = compact
            episodes[key] = compact
            print(json.dumps({'episode': key, 'time': compact['time'],
                              'completed': compact['completed_robots'], 'grant_order': compact['grant_order'],
                              'collision_pairs': compact['collision_pairs'],
                              'unresolved_pairs': compact['unresolved_pairs'],
                              'runtime_rejections': len(compact['runtime_rejections'])}), flush=True)
        fields = ('completed_robots', 'collision_pairs', 'unresolved_pairs', 'early_releases',
                  'completion_mismatches', 'runtime_rejections', 'safe_and_complete')
        comparisons[case] = {
            'equal_scored_outcomes': all(pair['source'][key] == pair['handwritten'][key] for key in fields),
            'equal_grant_order': pair['source']['grant_order'] == pair['handwritten']['grant_order'],
            'time_difference_source_minus_handwritten': pair['source']['time'] - pair['handwritten']['time'],
            'scope': 'legal allocation orders may differ; permanent blocking need not complete'}
    verify_live_selection(run)
    after = {str(path.resolve()): runner.sha(path) for path in sorted(input_paths)}
    if before != after:
        raise RuntimeError('simulation inputs changed; retained outputs are not validated')
    result = {'source_selection': selected, 'episode_count': len(episodes),
              'episodes': episodes, 'comparisons': comparisons, 'inputs_unchanged': True,
              'new_model_calls': 0, 'adaptation': adaptation, 'scope': SCOPE}
    runner.write_json(output / 'summary.json', result)
    runner.write_json(output / 'evidence-sha256.json', runner.inventory(output))
    return result


if __name__ == '__main__':
    execute()
