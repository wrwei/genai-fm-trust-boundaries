"""Refresh maintained metadata in dependency order, without rewriting raw evidence."""
from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
FA = ROOT / 'formal-artefacts'
STAGES = ['amr-forge-diagnostic', 'amr-thinking-diagnostic',
          'amr-thinking-extended', 'amr-independent-replication']
ORIGINS = {'prior': FA/'amr-deepseek-pilot/run',
           'forge': FA/'amr-forge-diagnostic/run',
           'thinking': FA/'amr-thinking-diagnostic/run',
           'extended': FA/'amr-thinking-extended/run',
           'extended-closed-loop': FA/'amr-thinking-extended/closed-loop'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def write(p, x):
    if read(p) != x:
        p.write_bytes((json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode())
def is_sha(x): return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x)
def explicit(name):
    if not isinstance(name,str): return None
    p = Path(name)
    if not p.is_absolute():
        if not name.startswith(('formal-artefacts/','literature/')): return None
        p = ROOT/name
    return p if p.is_relative_to(ROOT) and p.is_file() else None
def refresh(x):
    if isinstance(x,list): return [refresh(v) for v in x]
    if not isinstance(x,dict): return x
    out={k:refresh(v) for k,v in x.items()}
    for k,v in out.items():
        p=explicit(k)
        if p and is_sha(v): out[k]=sha(p)
        elif p and isinstance(v,dict) and is_sha(v.get('sha256')):
            v['sha256']=sha(p)
            if 'bytes' in v: v['bytes']=p.stat().st_size
    return out
def inventory(folder, exclude=None):
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p != exclude}

def maintain():
    for stage in STAGES:
        base=FA/stage; run=base/'run'
        # These copied inventories refer to explicitly named PREVIOUS runs.
        for name,origin in ORIGINS.items():
            p=run/(name+'-inventory.json')
            if p.exists(): write(p,inventory(origin))
        for p in run.glob('*frozen-inputs.json'): write(p,refresh(read(p)))
        for p in (run/'attempts').glob('*/outcome.json'):
            x=read(p)
            x['files_sha256']={k:sha(p.parent/k) for k in x['files_sha256']}
            write(p,x)
        p=run/'setup-sha256.json'
        write(p,{k:sha(run/k) for k in read(p)})
        p=run/'evidence-sha256.json'; write(p,inventory(run,p))
        physical=base/'closed-loop'
        if physical.is_dir():
            p=physical/'pre-run.json'
            if p.exists(): write(p,refresh(read(p)))
            p=physical/'evidence-sha256.json'
            if p.exists(): write(p,inventory(physical,p))
        for name, manifest in [('generation-audit.json',run/'evidence-sha256.json'),
                               ('physics-audit.json',physical/'evidence-sha256.json')]:
            p=base/name
            if p.exists():
                x=read(p); x['manifest_sha256']=sha(manifest)
                if 'result_sha256' in x: x['result_sha256']=sha(run/'result.json')
                script=base/('generation_audit.py' if name.startswith('generation') else 'physics_audit.py')
                if 'audit_script_sha256' in x: x['audit_script_sha256']=sha(script)
                write(p,x)
        print('maintained',stage,flush=True)

if __name__=='__main__': maintain()
