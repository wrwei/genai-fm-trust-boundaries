"""Execute frozen bounded physical suite, retaining every run and diagnostic."""
from pathlib import Path
import gzip, json, hashlib, datetime
import physical
HERE=Path(__file__).resolve().parent
RUNS=[('P-A','episode',dict(advice='A')),('P-B','episode',dict(advice='B')),('P-none','episode',{}),
      ('E2-center','episode',dict(center_clear=True)),('E2-whole','episode',{}),
      ('E3a-bad','gap',dict(gap='commit',bad=True)),('E3a-good','gap',dict(gap='commit')),
      ('E3b-bad','gap',dict(gap='apply',bad=True)),('E3b-good','gap',dict(gap='apply')),
      ('E4-wait','episode',dict(wait_advice=True)),('E4-fifo','episode',{}),
      ('B2-temporary','episode',dict(pedestrian='temporary')),('B2-permanent','episode',dict(pedestrian='permanent')),
      ('Brake-inside','braking',dict(inside=True)),('Brake-outside','braking',dict(inside=False))]

def expected(run,s):
    clean=not any(s.get(k) for k in ('collision_pairs','unresolved_pairs','reference_violations','early_releases'))
    if run in ('E3a-bad','E3b-bad'):return bool(s['reference_violations']) and (run!='E3b-bad' or s['final_speed']>0)
    if run=='E2-center':return bool(s['early_releases'])
    if run.startswith('E3'):return clean and s['final_speed']==0
    if run=='E4-wait':return clean and not s['grant_order'] and s['termination']=='horizon'
    if run=='B2-permanent':return clean and not s['completed_robots'] and s['pedestrian_trigger'] is not None
    if run.startswith('Brake'):return clean and s['condition']==(run=='Brake-inside') and (run!='Brake-inside' or s['standstill_margin']>=.2)
    return clean and s['completed_robots']==['A','B'] and s['grant_order'][0]==('B' if run=='P-B' else 'A')

def main():
    root=HERE/'evidence/physical';root.mkdir(exist_ok=True)
    batch=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=root/batch;out.mkdir()
    plan=dict(batch=batch,runs=RUNS,identities=physical.identity(),contract_sha256=hashlib.sha256((HERE/'physical-contract.md').read_bytes()).hexdigest())
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (out/'effective-parameters.json').write_text(json.dumps(physical.effective_parameters(),indent=2)+'\n')
    summaries=[]
    for run,kind,kwargs in RUNS:
        trace=out/(run+'.jsonl.gz')
        with gzip.open(trace,'wt',encoding='utf-8') as f:
            def emit(row):f.write(json.dumps(row,separators=(',',':'))+'\n')
            try:
                s=getattr(physical,'run_'+kind)(**kwargs,emit=emit)
                s.update(run_id=run,trace=trace.name)
            except Exception as error:
                s=dict(run_id=run,error=repr(error));emit(dict(kind='exception',error=repr(error)))
        s['trace_sha256']=hashlib.sha256(trace.read_bytes()).hexdigest()
        s['expected_outcome_observed']=False if 'error' in s else expected(run,s)
        (out/(run+'.summary.json')).write_text(json.dumps(s,indent=2)+'\n')
        summaries.append(s)
        print(run,s['expected_outcome_observed'],s.get('termination'),flush=True)
    final=dict(**plan,results=summaries,expected_outcomes=sum(s['expected_outcome_observed'] for s in summaries),total=len(summaries))
    (out/'summary.json').write_text(json.dumps(final,indent=2)+'\n')
    (root/'latest.json').write_text(json.dumps(dict(batch=batch,summary=str((out/'summary.json').relative_to(HERE))),indent=2)+'\n')
    print(out,flush=True)
if __name__=='__main__':main()
