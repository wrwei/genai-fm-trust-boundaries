"""Constructed one-factor contrasts; not observations of natural model errors."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from protocol import Core, SourceController, trace, step
from advice_mailbox import AdviceMailbox
from source_check import HERE, write_json


def _result(rows):
    return dict(trace=rows,violations=sum(not row['reference_accepted'] for row in rows))


def _selection(advice,wait_fault=False):
    controller=SourceController.from_selected()
    box=AdviceMailbox('one-request','one-task-set')
    if advice is not None:
        box.receive('one-request','one-task-set',json.dumps({'prefer':advice}))
    s=Core(req_a=True,req_b=True)
    rows=[]
    for n in range(6):
        before=s
        if wait_fault and box.advice is None:
            rows.append(dict(service=n,before=asdict(s),after=asdict(s),events=[],
                             source_called=False,reason='constructed_wait_for_advice'))
            continue
        if s.pending is None:
            latched=box.latch()
            choice,source=controller.select(s,latched['advice'])
        else:
            latched=None
            choice,source=None,None
        s,events=step(s,('Service',choice))
        rows.append(dict(service=n,before=asdict(before),after=asdict(s),events=events,
                         source_called=source is not None,source=source,latch=latched))
        if s.owner is not None:
            break
    return dict(owner=s.owner,services=len(rows),trace=rows,
                repeated_complete_state=bool(wait_fault and all(row['before']==row['after'] for row in rows)),
                source_id=controller.identity,
                scope='finite witness; permanent blocking additionally requires the HOL loop theorem')


def experiments():
    e3a=[('Register','A'),('Register','B'),('Validate','A'),('Observe',True,True),('Commit',)]
    e3b=[('Register','A'),('Validate','A'),('Commit',),('Issue','A'),('Observe',True,True),('Apply',)]
    return dict(
        E3a=dict(correct=_result(trace(e3a)),faulty=_result(trace(e3a,fault='cached_commit_permission'))),
        E3b=dict(correct=_result(trace(e3b)),faulty=_result(trace(e3b,fault='cached_apply_permission'))),
        E4=dict(correct=_selection(None),faulty=_selection(None,True)),
        positive={str(a) if a else 'none':_selection(a) for a in ('A','B',None)})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'evidence/mechanisms/results.json')
    args=parser.parse_args()
    result=experiments()
    write_json(args.output,result)
    print(json.dumps({k:{v:r['violations'] for v,r in result[k].items()} for k in ('E3a','E3b')}))
