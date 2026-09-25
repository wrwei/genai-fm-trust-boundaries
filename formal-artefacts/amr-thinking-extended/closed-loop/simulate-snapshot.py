"""Deploy only an accepted, unmodified source from the completed extended-output thinking comparison."""
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


r = load('extended_runner', HERE/'runner.py')
previous = load('forge_physics_reference', HERE.parent/'amr-forge-diagnostic/simulate.py')
if Path(previous.runner.__file__).resolve() != (HERE.parent/'amr-forge-diagnostic/runner.py').resolve():
    raise ValueError('prior physics helper loaded wrong runner')
SCOPE = ('exploratory physical demonstration of one repaired source from two configurations '
         'of one observed failed candidate; not an independent task evaluation or safety theorem')


def selected_record(result):
    if result.get('stop') != 'protocol_complete':
        raise ValueError('physics requires protocol_complete')
    states = result.get('conditions', {})
    ids = [cid for cid, _, _ in r.CONDITIONS]
    if set(states) != set(ids) or any(states[cid].get('stop') not in
            ('accepted','cycle','repair_limit') for cid in ids):
        raise ValueError('both conditions must be terminal without infrastructure failures')
    first = next((cid for cid in ids if states[cid]['stop']=='accepted'), None)
    selected = result.get('selected_for_exploratory_physics')
    if first is None or not isinstance(selected,dict):
        raise ValueError('accepted source required')
    expected = {'condition':first,'limit':12,'response_path':states[first]['accepted_response'],
                'repair':states[first]['first_accepted_repair']}
    if (set(selected) != set(expected)|{'sha256'} or states[first]['limit']!=12
        or any(selected[k]!=v for k,v in expected.items())
        or type(selected['repair']) is not int or not 1<=selected['repair']<=r.MAX_REPAIRS):
        raise ValueError('selection differs from fixed condition/repair order')
    return selected


def verify_evidence(run,result):
    run=Path(run).resolve()
    observed=r.inventory(run)
    observed.pop('evidence-sha256.json',None)
    if observed!=r.read_json(run/'evidence-sha256.json') or result!=r.read_json(run/'result.json'):
        raise ValueError('run evidence changed')
    selected=selected_record(result)
    r.verify_inputs(run)
    states,outcomes=r.replay(run)
    public={cid:{k:v for k,v in s.items() if k not in ('history','keys','text','report')}
            for cid,s in states.items()}
    for cid,s in states.items():
        public[cid]['checkpoint_at_two']=(
            {'executed_repairs':2,'assessment':s['trajectory'][1]} if s['repairs']>=2 else
            {'executed_repairs':s['repairs'],'terminal_before_two':s['stop'],
             'assessment':s['trajectory'][-1] if s['trajectory'] else None})
    if json.loads(r.json_bytes(public))!=result['conditions']:
        raise ValueError('terminal states differ from evidence replay')
    if (result['new_calls']!=len(outcomes) or len(list((run/'attempts').iterdir()))!=len(outcomes)
        or any(o.get('fatal','missing') is not None for o in outcomes)):
        raise ValueError('incomplete or failed outcome ledger')
    path=(run/selected['response_path']).resolve()
    if path.name!='response.bin' or path.parent.parent!=run/'attempts' or not path.parent.name.isdigit():
        raise ValueError('source is outside attempt ledger')
    if r.sha(path)!=selected['sha256']:
        raise ValueError('selected source hash changed')
    outcome=r.read_json(path.parent/'outcome.json')
    if (not outcome['accepted'] or outcome['fatal'] is not None
        or outcome['condition']!=selected['condition'] or outcome['repair']!=selected['repair']):
        raise ValueError('source did not qualify at recorded repair')
    raw=path.read_bytes()
    decoded,_,usage_summary,fatal=r.decode_response(path.parent,r.read_json(path.parent/'transport.json'),
                                         r.read_json(path.parent/'http-request.json'))
    if decoded!=raw or fatal is not None or usage_summary!=outcome.get('usage_summary'):
        raise ValueError('source or usage differs from provider envelope')
    report=r.d.assess(raw.decode('utf-8'),12)
    if not report['accepted'] or report['source_sha256']!=selected['sha256']:
        raise ValueError('selected source fails fresh unchanged obligations')
    return raw,report


def verify_live(run):
    result=r.read_json(run/'result.json')
    if result.get('mode')!='live':
        raise ValueError('physics requires actual live evidence')
    selected=selected_record(result)
    protocol=r.read_json(run/'protocol.json')
    if (protocol.get('mode')!='live' or protocol.get('id')!='amr-thinking-extended/v1'
        or result.get('protocol_id')!=protocol['id'] or protocol.get('model_configs')!=r.CONFIGS
        or protocol.get('conditions')!=[list(x) for x in r.CONDITIONS]):
        raise ValueError('unexpected extended-output thinking comparison configuration')
    raw,report=verify_evidence(run,result)
    return selected,raw,report


def execute(run=None,output=None):
    run=Path(run or HERE/'run').resolve()
    output=Path(output or HERE/'closed-loop').resolve()
    selected,raw,report=verify_live(run)
    physics,adaptation=previous.load_physics(12)
    physics.parameters()
    if output.is_relative_to(run):
        raise ValueError('physical output must be outside immutable run')
    inputs={r.ROOT/rel for rel in r.read_json(run/'frozen-inputs.json')}
    inputs|={p for p in run.rglob('*') if p.is_file()}
    inputs|={Path(__file__), Path(previous.__file__),Path(previous.runner.__file__),
             Path(sys.modules['simulation'].PARAMETER_PATH)}
    inputs|={Path(sys.modules[n].__file__) for n in ('controller','plant','oracle','simulation')}
    before={str(p.resolve()):r.sha(p) for p in sorted(inputs)}
    output.mkdir(exist_ok=False)
    (output/'selected-source.json').write_bytes(raw)
    (output/'simulate-snapshot.py').write_bytes(Path(__file__).read_bytes())
    (output/'closed-loop-adapted.py').write_bytes(physics.adapted_source_bytes)
    r.write_json(output/'selection.json',{'selected':selected,'assessment':r.compact(report),'scope':SCOPE})
    r.write_json(output/'pre-run.json',{'input_sha256':before,'adaptation':adaptation,
                 'cases':previous.CASES,'dt':.01,'horizon':120.,'python':sys.version,'platform':platform.platform(),
                 'created_at_utc':r.smoke.utc_now(),'new_model_calls':0,'scope':SCOPE})
    episodes,comparisons={},{}
    for case,config in previous.CASES:
        pair={}
        for arm in ('handwritten','source'):
            name=case+'_'+arm
            with previous.trace(output/(name+'.trace.jsonl.gz')) as emit:
                result=physics.run_supervised_episode(None if arm=='handwritten' else raw.decode('utf-8'),
                    handwritten=arm=='handwritten',emit=emit,dt=.01,horizon=120.,**config)
            if arm=='source' and result['source_id']!=selected['sha256']:
                raise RuntimeError('physical source identity changed')
            compact={k:v for k,v in result.items() if k not in ('events','assessment')}
            r.write_json(output/(name+'.json'),compact)
            episodes[name]=pair[arm]=compact
            print(json.dumps({'episode':name,'time':compact['time'],'completed':compact['completed_robots'],
                'collision_pairs':compact['collision_pairs'],'unresolved_pairs':compact['unresolved_pairs'],
                'runtime_rejections':len(compact['runtime_rejections'])}),flush=True)
        scored=('completed_robots','collision_pairs','unresolved_pairs','early_releases',
                'completion_mismatches','runtime_rejections','safe_and_complete')
        comparisons[case]={'equal_scored_outcomes':all(pair['source'][k]==pair['handwritten'][k] for k in scored),
            'equal_grant_order':pair['source']['grant_order']==pair['handwritten']['grant_order'],
            'time_difference_source_minus_handwritten':pair['source']['time']-pair['handwritten']['time']}
    verify_live(run)
    if before!={str(p.resolve()):r.sha(p) for p in sorted(inputs)}:
        raise RuntimeError('physical inputs changed during episodes')
    result={'source_selection':selected,'episode_count':len(episodes),'episodes':episodes,'comparisons':comparisons,
            'inputs_unchanged':True,'new_model_calls':0,'adaptation':adaptation,'scope':SCOPE}
    r.write_json(output/'summary.json',result)
    r.write_json(output/'evidence-sha256.json',r.inventory(output))
    return result


if __name__=='__main__': execute()
