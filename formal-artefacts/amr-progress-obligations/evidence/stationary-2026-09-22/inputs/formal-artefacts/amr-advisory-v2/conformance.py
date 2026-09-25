"""Compare independently HOL-evaluated tables with Python and exact raw source."""
import argparse
from dataclasses import asdict
import hashlib
import itertools
import json
from pathlib import Path
from protocol import Core, SourceController, step, reference_accepts
from source_check import HERE, write_json

EXPORT=HERE/'hol/export/AMR_Advisory_V2.AMR_Protocol'
CORE_CSV=EXPORT/'core-transitions.csv'
SELECTOR_CSV=EXPORT/'selector.csv'
ROBOTS=(None,'A','B')


def states():
    for row in itertools.product((False,True),(False,True),ROBOTS,(False,True),(False,True),ROBOTS,ROBOTS):
        yield Core(*row)


def inputs():
    return ([('Register',r) for r in ('A','B')]
            +[('Observe',b,f) for b,f in itertools.product((False,True),repeat=2)]
            +[('Validate',r) for r in ROBOTS]+[('Commit',)]
            +[('Issue',r) for r in ('A','B')]+[('Apply',)]
            +[('Release',r,c) for r in ('A','B') for c in (False,True)]
            +[('Service',r) for r in ROBOTS]+[('RequestAdvice',)]
            +[('Reply',r) for r in ROBOTS]+[('Consume',r) for r in ROBOTS])


def encode_state(s):
    return [int(s.req_a),int(s.req_b),ROBOTS.index(s.owner),int(s.blocked),int(s.fresh),
            ROBOTS.index(s.pending),ROBOTS.index(s.command)]


def encode_events(events):
    if not events:
        return [0,0,0]
    if len(events)!=1:
        raise ValueError('core has at most one visible event per step')
    kind,*args=events[0]
    if kind=='Observed':
        return [2,int(args[0]),int(args[1])]
    tags={'Registered':1,'Grant':3,'Issued':4,'Proceed':5,'Released':6}
    return [tags[kind],ROBOTS.index(args[0]),0]


def check_core(lines):
    if len(lines)!=432*27:
        raise ValueError('HOL core table must cover all432states x27inputs')
    failures=[]
    independent_failures=[]
    n=0
    for s in states():
        for inp in inputs():
            row=[int(x) for x in lines[n].split(',')]
            next_s,events=step(s,inp)
            observed=encode_state(s)+encode_state(next_s)+encode_events(events)
            if row!=observed:
                failures.append(dict(row=n,input=inp,hol=row,python=observed))
            if not reference_accepts(s,events):
                independent_failures.append(dict(row=n,input=inp,events=events))
            n+=1
    return dict(rows=n,states=432,inputs=27,mismatches=failures,
                independent_reference_failures=independent_failures,
                scope='exhaustive finite core transition conformance, not whole Python refinement')


def check_selector(path):
    rows=Path(path).read_text().splitlines()
    if len(rows)!=432*3:
        raise ValueError('HOL selector table must contain1296rows')
    source=SourceController.from_selected()
    failures=[]
    n=0
    for s in states():
        for advice in ROBOTS:
            choice,raw=source.select(s,advice)
            observed=encode_state(s)+[ROBOTS.index(advice),ROBOTS.index(choice)]
            row=[int(x) for x in rows[n].split(',')]
            if row!=observed:
                failures.append(dict(row=n,hol=row,source=observed,raw=raw))
            n+=1
    return dict(rows=n,source_id=source.identity,mismatches=failures,
                scope='exact source outputs vs independent HOL selector on core states/advice domain')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'evidence/conformance.json')
    parser.add_argument('--selector',type=Path,default=SELECTOR_CSV)
    args=parser.parse_args()
    report=dict(core=check_core(CORE_CSV.read_text().splitlines()),selector=check_selector(args.selector))
    report['input_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (CORE_CSV,args.selector,HERE/'protocol.py',HERE/'source_check.py',HERE/'hol/AMR_Protocol.thy')}
    report['passed']=not any((report['core']['mismatches'],report['core']['independent_reference_failures'],report['selector']['mismatches']))
    write_json(args.output,report)
    print(json.dumps({k:{a:b for a,b in v.items() if a!='input_sha256'} if isinstance(v,dict) else v
                      for k,v in report.items() if k!='input_sha256'}))
    raise SystemExit(0 if report['passed'] else 1)
