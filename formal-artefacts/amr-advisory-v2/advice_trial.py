"""Six predeclared advisory requests; bounded transport, paced approach, no retries."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import time

from advice_mailbox import AdviceMailbox
from protocol import Core, SourceController, step
from source_check import HERE, ROOT, write_json, sha

_spec=importlib.util.spec_from_file_location('_amr_v2_transport',HERE.parent/'amr-deepseek-smoke/smoke.py')
transport=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(transport)
sys.path.insert(0,str(HERE.parent/'amr-corridor'))
from plant import RobotPlant
from simulation import parameters

MAX_OUTPUT=128
FROZEN_SOURCE_SHA='9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd'
SAMPLES=('W1-R1','W2-R1','W3-R1','W1-R2','W2-R2','W3-R2')
WORDINGS=(
    'Two AMRs share a single-lane factory corridor. A carries routine stock due in30minutes; B carries a repair spare due in10minutes. Both are currently eligible. Recommend the earlier-deadline task.',
    'Factory transport tasks: B delivers a maintenance part with deadline10minutes; A replenishes stock with deadline30minutes. Both may safely be chosen. Which task should be recommended first under an earlier-deadline rule?',
    'A and B are waiting to use a shared industrial passage. Deadline(A)=30minutes, Deadline(B)=10minutes. Neither has any extra safety permission. Recommend the task with less time to its deadline.'
)


def utc():
    return datetime.now(timezone.utc).isoformat()


def payload_for(index):
    if type(index) is not int or not 0<=index<len(SAMPLES):
        raise ValueError('only the six frozen samples are permitted')
    prompt=WORDINGS[index%3]+'\nThis is advisory data only. Return exactly one JSON object with the single key "prefer" and value "A" or "B". No code, actions, credentials or explanation.'
    return dict(model='deepseek-flash',max_tokens=MAX_OUTPUT,stream=False,temperature=0,
                thinking={'type':'disabled'},response_format={'type':'json_object'},
                messages=[{'role':'user','content':prompt}])


def approach_trace():
    """Fixed outside-zone movement; advice cannot change this pre-decision path."""
    p=parameters()
    robots={r:RobotPlant(p['map']['route_'+r][:2]) for r in ('A','B')}
    rows=[]
    dt=.01
    for tick in range(2001):
        t=round(tick*dt,10)
        rows.append(dict(time=t,robots={r:dict(pose=list(b.pose),speed=b.speed) for r,b in robots.items()}))
        if all(b.finished for b in robots.values()):
            return rows
        for b in robots.values():
            b.advance(dt,'Proceed')
    raise RuntimeError('fixed approach does not reach halted staging within20seconds')


def dependencies():
    paths=[Path(__file__),HERE/'protocol.py',HERE/'advice_mailbox.py',HERE/'source_check.py',
           HERE.parent/'amr-deepseek-smoke/smoke.py',HERE.parent/'amr-llm-trial/trial.py',
           HERE.parent/'amr-forge-diagnostic/diagnostics.py',HERE/'evidence/source/summary.json',
           HERE/'evidence/source/sources'/f'{FROZEN_SOURCE_SHA}.json',
           ROOT/'literature/scholar_search_2026-09-10/followup/research_amr_parameters_2026-09-15.json']
    paths+=sorted((HERE.parent/'amr-forge-diagnostic/profiles').rglob('*.py'))
    paths+=sorted((HERE.parent/'amr-corridor').glob('*.py'))
    return paths


def validate_source_identity(source):
    if source.identity!=FROZEN_SOURCE_SHA:
        raise ValueError('source differs from the first accepted historical raw identity')


def prepare(output):
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    validate_source_identity(SourceController.from_selected())
    rows=approach_trace()
    write_json(output/'approach.json',rows)
    samples=[]
    for index,name in enumerate(SAMPLES):
        folder=output/f'{index+1:03}'
        folder.mkdir()
        payload=payload_for(index)
        write_json(folder/'http-request.json',payload)
        (folder/'prompt.txt').write_text(payload['messages'][0]['content'],encoding='utf-8')
        samples.append(dict(sample=name,index=index,request_sha256=sha((folder/'http-request.json').read_bytes())))
    record=dict(prepared_utc=utc(),samples=samples,maximum_requests=6,retries=0,
                window_seconds=rows[-1]['time'],approach_sha256=sha((output/'approach.json').read_bytes()),
                latch_rule='fixed paced approach finish; zero waiting for reply; arrival cutoff uses monotonic time',
                scope='six one-decision runtime samples; no response-quality rate or throughput claim',
                endpoint=transport.ENDPOINT,
                source_id=SourceController.from_selected().identity,
                inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in dependencies()})
    write_json(output/'protocol.json',record)
    return record


def validate_batch(output):
    output=Path(output).resolve()
    record=json.loads((output/'protocol.json').read_bytes())
    if (record.get('maximum_requests'),record.get('retries'),record.get('endpoint'))!=(6,0,transport.ENDPOINT):
        raise ValueError('unexpected protocol bounds or endpoint')
    expected_inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in dependencies()}
    if record.get('inputs')!=expected_inputs:
        raise ValueError('frozen implementation dependency changed')
    if record.get('source_id')!=SourceController.from_selected().identity:
        raise ValueError('selected source changed')
    validate_source_identity(SourceController.from_selected())
    approach=json.loads((output/'approach.json').read_bytes())
    if approach!=approach_trace() or record.get('window_seconds')!=approach[-1]['time']:
        raise ValueError('approach or decision window changed')
    if record.get('approach_sha256')!=sha((output/'approach.json').read_bytes()):
        raise ValueError('approach identity mismatch')
    if len(record.get('samples',[]))!=6:
        raise ValueError('exactly six declared samples required')
    for index,name in enumerate(SAMPLES):
        sample=record['samples'][index]
        raw=(output/f'{index+1:03}'/'http-request.json').read_bytes()
        if json.loads(raw)!=payload_for(index):
            raise ValueError('request differs from fixed prompt/model/token configuration')
        expected=dict(sample=name,index=index,request_sha256=sha(raw))
        if sample!=expected:
            raise ValueError('sample order or identity differs')
    return record


def claim_dispatch(folder,index):
    if type(index) is not int or not 0<=index<6:
        raise ValueError('invalid batch index')
    write_json(Path(folder)/'dispatch-intent.json',dict(index=index,sample=SAMPLES[index],
               started_utc=utc(),posts_at_most=1,retries=0))


def decision_at_deadline(reply,deadline):
    box=AdviceMailbox('request-1','fixed-tasks-A0-B1')
    if reply is None:
        adoption='missing'
    elif reply['arrival_seconds']>deadline:
        adoption='late'
    else:
        adoption=box.receive('request-1','fixed-tasks-A0-B1',reply['content'])
    latched=box.latch()
    source=SourceController.from_selected()
    s=Core(req_a=True,req_b=True)
    intent,raw=source.select(s,latched['advice'])
    s,_=step(s,('Service',intent))
    s,events=step(s,('Service',None))
    return dict(adoption=adoption,latch=latched,source=raw,owner=s.owner,events=events,
                cutoff_seconds=deadline,scope='source-driven staged authorization; not complete transport')


def _call_once(key_path,folder,start):
    try:
        status=run_worker(key_path,folder)
        if status.get('status')!='received':
            return dict(fatal='transport_error',transport=status,arrival_seconds=time.monotonic()-start)
        body=json.loads((folder/'http-body.bin').read_bytes())
        choices=body.get('choices',[])
        if len(choices)!=1 or choices[0].get('finish_reason')!='stop':
            return dict(fatal='truncated_or_invalid_completion',arrival_seconds=time.monotonic()-start)
        content=choices[0].get('message',{}).get('content')
        if type(content) is not str:
            return dict(fatal='invalid_content_type',arrival_seconds=time.monotonic()-start)
        (folder/'response.bin').write_bytes(content.encode('utf-8'))
        usage_summary=transport.usage_summary(body.get('usage'))
        return dict(content=content,arrival_seconds=time.monotonic()-start,
                    fatal=None if usage_summary else 'usage_unavailable',usage_summary=usage_summary,usage=body.get('usage'),
                    provider_model=body.get('model'),request_id=body.get('id'),
                    fingerprint=body.get('system_fingerprint'))
    except Exception as error:
        return dict(fatal='worker_failure',error_type=type(error).__name__,arrival_seconds=time.monotonic()-start)


def run_worker(key_path,folder):
    """Dedicated advisory entry point; smoke CLI intentionally rejects other stages."""
    result=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'worker',
                           '--output',str(folder),'--key-file',str(key_path)],
                          timeout=90,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    target=Path(folder)/'transport.json'
    if result.returncode!=0 or not target.exists():
        return dict(status='transport_error',error_type='ChildFailed')
    return json.loads(target.read_bytes())


def worker_entry(key_path,folder):
    folder=Path(folder).resolve()
    if folder.name not in tuple(f'{n:03}' for n in range(1,7)):
        raise ValueError('worker directory not a declared attempt')
    validate_batch(folder.parent)
    # Reuses the single-POST implementation, not the smoke stage's restricted CLI.
    transport.network_child(key_path,folder)


def execute(key_path,output):
    output=Path(output).resolve()
    protocol=validate_batch(output)
    write_json(output/'batch-dispatch-intent.json',dict(started_utc=utc(),maximum_requests=6,retries=0))
    approach=json.loads((output/'approach.json').read_bytes())
    if sha((output/'approach.json').read_bytes())!=protocol['approach_sha256']:
        raise ValueError('frozen approach changed')
    results=[]
    for index in range(6):
        folder=output/f'{index+1:03}'
        if sha((folder/'http-request.json').read_bytes())!=protocol['samples'][index]['request_sha256']:
            raise ValueError('frozen request changed')
        claim_dispatch(folder,index)
        start=time.monotonic()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(_call_once,key_path,folder,start)
            max_lag=0.
            for row in approach:
                remaining=start+row['time']-time.monotonic()
                if remaining>0:
                    time.sleep(remaining)
                max_lag=max(max_lag,time.monotonic()-(start+row['time']))
            cutoff=protocol['window_seconds']
            available=future.result() if future.done() else None
            reply=available if available and 'content' in available else None
            decision=decision_at_deadline(reply,cutoff)
            decision_time=time.monotonic()-start
            final=future.result()  # bounded child timeout; control decision already committed
        # A reply completed after the latch is still recorded, never retroactively adopted.
        outcome=dict(sample=SAMPLES[index],result=final,decision=decision,
                     decision_wall_seconds=decision_time,max_pacing_lag_seconds=max_lag,
                     planned_window_seconds=cutoff,actual_source_id=protocol['source_id'])
        write_json(folder/'outcome.json',outcome)
        results.append(outcome)
        print(json.dumps(dict(sample=SAMPLES[index],arrival_seconds=final.get('arrival_seconds'),
                   adoption=decision['adoption'],owner=decision['owner'],fatal=final.get('fatal'))),flush=True)
        if final.get('fatal'):
            break
    summary=dict(requests=len(results),results=results,
                 complete=len(results)==6 and not any(r['result'].get('fatal') for r in results),
                 scope='paced fixed approach and source-driven authorization; no full live robot-stack claim')
    write_json(output/'summary.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=('prepare','execute','worker'))
    parser.add_argument('--output',type=Path,default=HERE/'evidence/advice')
    parser.add_argument('--key-file',type=Path)
    args=parser.parse_args()
    if args.mode=='prepare':
        r=prepare(args.output)
        print(json.dumps({'samples':len(r['samples']),'window_seconds':r['window_seconds']}))
    elif args.mode=='worker':
        if args.key_file is None:
            parser.error('--key-file required')
        worker_entry(args.key_file,args.output)
    else:
        if args.key_file is None:
            parser.error('--key-file is required for explicitly authorized execution')
        r=execute(args.key_file,args.output)
        print(json.dumps({k:v for k,v in r.items() if k!='results'}))
