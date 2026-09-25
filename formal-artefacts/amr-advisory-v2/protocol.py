"""Source-driven local protocol; finite conformance is separate from HOL proof."""
from __future__ import annotations
from dataclasses import dataclass, replace, asdict
import json
from pathlib import Path
from source_check import HERE, ROOT, assess_bytes, language, required_select


@dataclass(frozen=True)
class Core:
    req_a: bool=False
    req_b: bool=False
    owner: str|None=None
    blocked: bool=False
    fresh: bool=True
    pending: str|None=None
    command: str|None=None

    def __post_init__(self):
        if any(type(getattr(self,k)) is not bool for k in ('req_a','req_b','blocked','fresh')):
            raise ValueError('exact booleans required')
        if any(getattr(self,k) not in (None,'A','B') for k in ('owner','pending','command')):
            raise ValueError('unknown robot')


def legal(s, robot):
    return (robot in ('A','B') and s.owner is None and not s.blocked and s.fresh
            and (s.req_a if robot=='A' else s.req_b))


def step(s, inp, *, fault=None):
    if fault not in (None,'cached_commit_permission','cached_apply_permission'):
        raise ValueError('unknown constructed protocol fault')
    op,*args=inp
    expected={'Register':1,'Observe':2,'Validate':1,'Commit':0,'Issue':1,'Apply':0,
              'Release':2,'Service':1,'RequestAdvice':0,'Reply':1,'Consume':1}
    if op not in expected or len(args)!=expected[op]:
        raise ValueError('invalid typed input')
    if op in ('Register','Issue','Release') and args[0] not in ('A','B'):
        raise ValueError('robot required')
    if op in ('Validate','Service','Reply','Consume') and args[0] not in (None,'A','B'):
        raise ValueError('invalid optional robot')
    if op=='Observe' and any(type(v) is not bool for v in args):
        raise ValueError('observation booleans required')
    if op=='Release' and type(args[1]) is not bool:
        raise ValueError('clear Boolean required')
    if op=='Register':
        return replace(s,**{'req_a' if args[0]=='A' else 'req_b':True}),[('Registered',args[0])]
    if op=='Observe':
        return replace(s,blocked=args[0],fresh=args[1]),[('Observed',*args)]
    if op=='Validate':
        return (replace(s,pending=args[0]) if s.pending is None and legal(s,args[0]) else s),[]
    if op=='Commit':
        r=s.pending
        permit=legal(s,r)
        if fault=='cached_commit_permission':
            permit=r in ('A','B') and s.owner is None and (s.req_a if r=='A' else s.req_b)
        if permit:
            return replace(s,owner=r,pending=None,**{'req_a' if r=='A' else 'req_b':False}),[('Grant',r)]
        return replace(s,pending=None),[]
    if op=='Issue':
        if s.owner==args[0] and s.fresh and not s.blocked:
            return replace(s,command=args[0]),[('Issued',args[0])]
        return s,[]
    if op=='Apply':
        r=s.command
        permit=r is not None and s.owner==r and (fault=='cached_apply_permission' or s.fresh and not s.blocked)
        return replace(s,command=None),[('Proceed',r)] if permit else []
    if op=='Release':
        if args[1] and s.owner==args[0]:
            return replace(s,owner=None,command=None),[('Released',args[0])]
        return s,[]
    if op=='Service':
        return step(s,('Validate',args[0]) if s.pending is None else ('Commit',),fault=fault)
    return s,[]  # advice I/O changes no core authority state


def reference_accepts(before, events):
    """Independent visible-event oracle: no call to step or legal."""
    owner=before.owner
    requests={'A':before.req_a,'B':before.req_b}
    blocked,fresh=before.blocked,before.fresh
    for event in events:
        kind,*args=event
        if kind=='Registered':
            requests[args[0]]=True
        elif kind=='Observed':
            blocked,fresh=args
        elif kind=='Grant':
            r=args[0]
            if owner is not None or not requests[r] or blocked or not fresh:
                return False
            owner=r
            requests[r]=False
        elif kind in ('Issued','Proceed'):
            if owner!=args[0] or blocked or not fresh:
                return False
        elif kind=='Released':
            if owner!=args[0]:
                return False
            owner=None
        else:
            return False
    return True


class SourceController:
    def __init__(self,raw):
        self.raw=raw
        self.assessment=assess_bytes(raw)
        if not self.assessment['v2_accepted']:
            raise ValueError('v2 source rejected before deployment')
        self.program=language.parse_program(raw.decode('utf-8'))
        self.identity=self.assessment['source_sha256']

    @classmethod
    def from_selected(cls):
        summary=json.loads((HERE/'evidence/source/summary.json').read_bytes())
        selected=summary['selected']
        if selected is None:
            raise ValueError('no accepted historical source')
        instance=cls((ROOT/selected['path']).read_bytes())
        if instance.identity!=selected['source_sha256']:
            raise ValueError('deployment identity mismatch')
        return instance

    def select(self,s,advice):
        if advice not in (None,'A','B'):
            raise ValueError('typed advisory value required')
        usable=s.fresh and not s.blocked
        f=dict(OwnerFree=s.owner is None,RequestA=s.req_a and usable,
               RequestB=s.req_b and usable,PreferA=advice=='A',PreferB=advice=='B')
        raw=language.eval_select(self.program,f)
        if raw!=required_select(f):
            raise RuntimeError('source functionality failure; must not be silently replaced')
        return {'SelectA':'A','SelectB':'B','Defer':None}[raw],dict(facts=f,raw_action=raw,source_id=self.identity)

    def step(self,mode,facts):
        return language.eval_step(self.program,mode,facts)


def trace(inputs,initial=None,*,fault=None):
    s=initial or Core()
    rows=[]
    for inp in inputs:
        next_s,events=step(s,inp,fault=fault)
        rows.append(dict(before=asdict(s),input=inp,after=asdict(next_s),events=events,
                         reference_accepted=reference_accepts(s,events)))
        s=next_s
    return rows
