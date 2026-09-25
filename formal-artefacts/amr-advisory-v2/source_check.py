"""Finite v2 source/function/correspondence checks; historical bytes are immutable."""
from __future__ import annotations
import argparse
from dataclasses import replace
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SPEC = 'amr-advisory-contract/v2/fixed-registration-A-before-B'
_spec = importlib.util.spec_from_file_location('_amr_v2_profiles', HERE.parent/'amr-forge-diagnostic/diagnostics.py')
_profiles = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_profiles)
language, model, old = _profiles._profile(12)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def historical_sources():
    return [HERE.parent/'amr-independent-replication/run/attempts'/f'{n:03}'/'response.bin'
            for n in range(1, 7)]


def required_select(f):
    if not f['OwnerFree'] or not (f['RequestA'] or f['RequestB']):
        return 'Defer'
    if not f['RequestA']:
        return 'SelectB'
    if not f['RequestB']:
        return 'SelectA'
    return 'SelectB' if f['PreferB'] and not f['PreferA'] else 'SelectA'


def extract(program, fault=None):
    target = model.extract_model(program)
    if fault is None:
        return target
    if fault != 'honor_b_model_only':
        raise ValueError('unsupported constructed fault')
    b_only = (('LOAD','RequestA'),('LOAD','RequestB'),('LOAD','PreferB'),
              ('LOAD','PreferA'),('NOT',),('AND',4))
    rules = []
    for r in target.select:
        if r.action == 'SelectA':
            rules.extend((model.TargetRule(r.guard+b_only+(('AND',2),),'SelectB',None),
                          model.TargetRule(r.guard+b_only+(('NOT',),('AND',2)),'SelectA',None)))
        else:
            rules.append(r)
    return replace(target, select=tuple(rules), fault=fault)


def assess_bytes(raw, *, fault=None):
    if type(raw) is not bytes:
        raise TypeError('exact bytes required')
    program = language.parse_program(raw.decode('utf-8'))
    target = extract(program, fault)
    rows = []
    for bits in itertools.product((False,True), repeat=5):
        facts = dict(zip(language.SELECT_FACTS, bits))
        src = language.eval_select(program, facts)
        tgt = model.model_select(target, facts)
        want = required_select(facts)
        rows.append(dict(kind='select', facts=facts, source=src, target=list(tgt),
                         required=want, old_source_ok=not old.selection_violations(src,facts),
                         old_target_ok=bool(tgt) and all(not old.selection_violations(v,facts) for v in tgt),
                         source_ok=src==want, target_ok=bool(tgt) and all(v==want for v in tgt),
                         correspondence=set(tgt)=={src}))
    for mode in language.MODES:
        for bits in itertools.product((False,True), repeat=8):
            facts = dict(zip(language.STEP_FACTS,bits))
            src = language.eval_step(program,mode,facts)
            tgt = model.model_step(target,mode,facts)
            want = old.obligation(mode,facts)[1]
            src_ok = not old.step_violations(src,mode,facts)
            tgt_ok = bool(tgt) and all(not old.step_violations(v,mode,facts) for v in tgt)
            rows.append(dict(kind='step', mode=mode, facts=facts, source=src, target=tgt,
                             required=want, old_source_ok=src_ok, old_target_ok=tgt_ok,
                             source_ok=src_ok, target_ok=tgt_ok, correspondence=set(tgt)=={src}))
    report = dict(spec_id=SPEC, source_sha256=sha(raw), constructed_fault=fault,
                  checked_inputs=len(rows), selection_inputs=32, step_inputs=1792,
                  old_policy_pass=all(r['old_source_ok'] for r in rows),
                  old_model_policy_pass=all(r['old_target_ok'] for r in rows),
                  v2_source_pass=all(r['source_ok'] for r in rows),
                  v2_model_pass=all(r['target_ok'] for r in rows),
                  correspondence_pass=all(r['correspondence'] for r in rows),
                  source_failures=sum(not r['source_ok'] for r in rows),
                  model_failures=sum(not r['target_ok'] for r in rows),
                  correspondence_mismatches=sum(not r['correspondence'] for r in rows),
                  cases=rows)
    report['v2_accepted'] = all(report[k] for k in ('v2_source_pass','v2_model_pass','correspondence_pass'))
    return report


def compact(r):
    return {k:v for k,v in r.items() if k!='cases'}


def execute(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    identities = {}
    samples = []
    selected = None
    for p in historical_sources():
        raw = p.read_bytes()
        r = assess_bytes(raw)
        info = json.loads((p.parent/'outcome.json').read_bytes())
        identity = r['source_sha256']
        samples.append(dict(sample_id=info['sample_id'], path=p.relative_to(ROOT).as_posix(), **compact(r)))
        if identity not in identities:
            dest = output/'sources'/f'{identity}.json'
            dest.parent.mkdir(exist_ok=True)
            with dest.open('xb') as f:
                f.write(raw)
            with gzip.open(output/f'{identity}.assessment.json.gz','xb') as f:
                f.write(json.dumps(r,ensure_ascii=False,allow_nan=False).encode())
            identities[identity] = dict(path=dest.relative_to(ROOT).as_posix(), **compact(r))
            if selected is None and r['v2_accepted']:
                selected = identities[identity]
    e1raw = historical_sources()[0].read_bytes()
    e1 = {'correct':assess_bytes(e1raw), 'faulty':assess_bytes(e1raw,fault='honor_b_model_only')}
    for name,r in e1.items():
        with gzip.open(output/f'E1-{name}.json.gz','xb') as f:
            f.write(json.dumps(r,ensure_ascii=False,allow_nan=False).encode())
    e1brief = {name:compact(r) for name,r in e1.items()}
    e1brief['first_mismatch'] = next(r for r in e1['faulty']['cases'] if not r['correspondence'])
    summary = dict(spec_id=SPEC, samples=samples, distinct_sources=list(identities.values()),
                   selected=selected, E1=e1brief,
                   scope='finite declared domain; parser and continuous refinement are not proved')
    write_json(output/'summary.json',summary)
    if selected:
        r=assess_bytes((ROOT/selected['path']).read_bytes())
        write_json(output/'selected-selection-table.json',[c for c in r['cases'] if c['kind']=='select'])
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'evidence/source')
    args=parser.parse_args()
    result=execute(args.output)
    print(json.dumps({'samples':len(result['samples']),'identities':len(result['distinct_sources']),
                      'accepted_samples':sum(x['v2_accepted'] for x in result['samples']),
                      'selected':result['selected']['source_sha256'] if result['selected'] else None,
                      'E1':result['E1']},ensure_ascii=False))
