"""Deploy every distinct accepted replication source in the frozen five scenarios."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import platform
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name, path):
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve() != path.resolve():
            raise ValueError('unexpected module identity')
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


r = load('replication_runner', HERE/'runner.py')
previous = load('forge_physics_reference', HERE.parent/'amr-forge-diagnostic/simulate.py')
if Path(previous.runner.__file__).resolve() != (HERE.parent/'amr-forge-diagnostic/runner.py').resolve():
    raise ValueError('wrong historical physics helper')
SCOPE = ('six fresh-context requests for one task with three prose variants, not independent industrial tasks; '
         'exact-byte duplicate accepted sources share physical traces; fixed analytic simulation, not a safety theorem')


def validate_selection(result, states, run):
    if result.get('stop') != 'protocol_complete':
        raise ValueError('physics requires protocol_complete')
    if set(states) != set(r.SAMPLE_IDS) or set(result.get('samples', {})) != set(r.SAMPLE_IDS):
        raise ValueError('all six sample states required')
    if any(s.get('stop') not in ('accepted','cycle','repair_limit') for s in states.values()):
        raise ValueError('all six samples must be terminal without infrastructure failures')
    public = json.loads(r.json_bytes(r.public_states(states)))
    if public != result['samples']:
        raise ValueError('sample states differ from replay')
    if (result['initial_accepted_count'] != sum(s['initial_accepted'] for s in states.values())
        or result['eventually_accepted_count'] != sum(s['stop'] == 'accepted' for s in states.values())):
        raise ValueError('acceptance counts differ from replay')
    expected = r.select_sources(states, run)
    if not expected or result.get('selected_sources') != expected:
        raise ValueError('source mapping differs from fixed complete selection')
    return expected


def verify_evidence(run, result):
    run = Path(run).resolve()
    observed = r.inventory(run)
    observed.pop('evidence-sha256.json', None)
    if observed != r.read_json(run/'evidence-sha256.json') or result != r.read_json(run/'result.json'):
        raise ValueError('generation evidence changed')
    r.verify_inputs(run)
    states, outcomes = r.replay(run)
    selections = validate_selection(result, states, run)
    if (result['new_calls'] != len(outcomes) or len(list((run/'attempts').iterdir())) != len(outcomes)
        or any(o.get('fatal', 'missing') is not None for o in outcomes)):
        raise ValueError('incomplete or failed outcome ledger')
    catalog = []
    for number, selected in enumerate(selections, 1):
        path = (run/selected['response_path']).resolve()
        if path.name != 'response.bin' or path.parent.parent != run/'attempts' or not path.parent.name.isdigit():
            raise ValueError('selected source outside attempt ledger')
        raw = path.read_bytes()
        if r.sha(path) != selected['sha256']:
            raise ValueError('selected source identity changed')
        for sid in selected['sample_ids']:
            member = run/states[sid]['accepted_response']
            if member.read_bytes() != raw:
                raise ValueError('deduplicated members are not byte-identical')
            out = r.read_json(member.parent/'outcome.json')
            if (out['sample_id'] != sid or not out['accepted'] or out['fatal'] is not None
                or out['attempt'] != states[sid]['first_accepted_attempt']):
                raise ValueError('sample did not qualify at recorded attempt')
            decoded, _, usage_summary, fatal = r.decode_response(member.parent,
                r.read_json(member.parent/'transport.json'), r.read_json(member.parent/'http-request.json'))
            if decoded != raw or fatal is not None or usage_summary != out['usage_summary']:
                raise ValueError('candidate or token usage differs from provider envelope')
        report = r.d.assess(raw.decode('utf-8'), 12)
        if not report['accepted'] or report['source_sha256'] != selected['sha256']:
            raise ValueError('selected source fails fresh unchanged obligations')
        catalog.append({'source_key': f'source_{number:02d}', 'selection': selected,
                        'raw': raw, 'assessment': report})
    return catalog


def verify_live(run):
    result = r.read_json(run/'result.json')
    if result.get('mode') != 'live':
        raise ValueError('physical deployment requires live evidence')
    protocol = r.read_json(run/'protocol.json')
    if (protocol.get('mode') != 'live' or protocol.get('id') != 'amr-independent-replication/v1'
        or result.get('protocol_id') != protocol['id']
        or protocol.get('sample_ids') != list(r.SAMPLE_IDS) or protocol.get('model_configs') != r.CONFIGS):
        raise ValueError('unexpected replication configuration')
    return verify_evidence(run, result)


def episode_plan(catalog):
    if not 1 <= len(catalog) <= 6:
        raise ValueError('one to six distinct accepted sources required')
    rows = [{'name': 'reference_'+case, 'source_key': None, 'case': case, 'config': config}
            for case, config in previous.CASES]
    for entry in catalog:
        rows.extend({'name': entry['source_key']+'_'+case, 'source_key': entry['source_key'],
                     'case': case, 'config': config} for case, config in previous.CASES)
    return rows


def execute(run=None, output=None):
    run = Path(run or HERE/'run').resolve()
    output = Path(output or HERE/'closed-loop').resolve()
    catalog = verify_live(run)
    physics, adaptation = previous.load_physics(12)
    physics.parameters()
    if output.is_relative_to(run):
        raise ValueError('physical outputs must be outside immutable generation run')
    inputs = {r.ROOT/rel for rel in r.read_json(run/'frozen-inputs.json')}
    inputs |= {p for p in run.rglob('*') if p.is_file()}
    inputs |= {Path(__file__), Path(previous.__file__), Path(previous.runner.__file__),
               Path(sys.modules['simulation'].PARAMETER_PATH)}
    inputs |= {Path(sys.modules[n].__file__) for n in ('controller','plant','oracle','simulation')}
    before = {str(p.resolve()): r.sha(p) for p in sorted(inputs)}
    plan = episode_plan(catalog)
    output.mkdir(exist_ok=False)
    (output/'sources').mkdir()
    (output/'simulate-snapshot.py').write_bytes(Path(__file__).read_bytes())
    (output/'closed-loop-adapted.py').write_bytes(physics.adapted_source_bytes)
    public = []
    for entry in catalog:
        (output/'sources'/(entry['source_key']+'.json')).write_bytes(entry['raw'])
        public.append({k:v for k,v in entry.items() if k not in ('raw','assessment')})
    mapping = {sid: x['source_key'] for x in catalog for sid in x['selection']['sample_ids']}
    r.write_json(output/'selection.json', {'sources': public, 'sample_to_source_key': mapping,
        'assessments': {x['source_key']: r.compact(x['assessment']) for x in catalog}, 'scope': SCOPE})
    r.write_json(output/'pre-run.json', {'input_sha256': before, 'adaptation': adaptation,
        'plan': plan, 'dt': .01, 'horizon': 120., 'python': sys.version, 'platform': platform.platform(),
        'created_at_utc': r.smoke.utc_now(), 'new_model_calls': 0, 'scope': SCOPE})
    by_key = {x['source_key']: x for x in catalog}
    episodes = {}
    for row in plan:
        key, name = row['source_key'], row['name']
        raw = by_key[key]['raw'] if key is not None else None
        with previous.trace(output/(name+'.trace.jsonl.gz')) as emit:
            result = physics.run_supervised_episode(None if raw is None else raw.decode('utf-8'),
                handwritten=key is None, emit=emit, dt=.01, horizon=120., **row['config'])
        if key is not None and result['source_id'] != by_key[key]['selection']['sha256']:
            raise RuntimeError('executed source identity changed')
        compact = {k:v for k,v in result.items() if k not in ('events','assessment')}
        r.write_json(output/(name+'.json'), compact)
        episodes[name] = compact
        print(json.dumps({'episode': name, 'time': compact['time'], 'completed': compact['completed_robots'],
            'collision_pairs': compact['collision_pairs'], 'unresolved_pairs': compact['unresolved_pairs'],
            'runtime_rejections': len(compact['runtime_rejections'])}), flush=True)
    scored = ('completed_robots','collision_pairs','unresolved_pairs','early_releases',
              'completion_mismatches','runtime_rejections','safe_and_complete')
    comparisons = {}
    for entry in catalog:
        key = entry['source_key']
        comparisons[key] = {}
        for case, _ in previous.CASES:
            source, reference = episodes[key+'_'+case], episodes['reference_'+case]
            comparisons[key][case] = {'equal_scored_outcomes': all(source[k] == reference[k] for k in scored),
                'equal_grant_order': source['grant_order'] == reference['grant_order'],
                'time_difference_source_minus_handwritten': source['time']-reference['time']}
    verify_live(run)
    if before != {str(p.resolve()): r.sha(p) for p in sorted(inputs)}:
        raise RuntimeError('physical inputs changed during execution')
    result = {'source_catalog': public, 'sample_to_source_key': mapping,
        'unique_source_count': len(catalog), 'episode_count': len(episodes), 'reference_episode_count': 5,
        'episodes': episodes, 'comparisons': comparisons, 'inputs_unchanged': True,
        'new_model_calls': 0, 'adaptation': adaptation, 'scope': SCOPE}
    r.write_json(output/'summary.json', result)
    r.write_json(output/'evidence-sha256.json', r.inventory(output))
    return result


if __name__ == '__main__': execute()
