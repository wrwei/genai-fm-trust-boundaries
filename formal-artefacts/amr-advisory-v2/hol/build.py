import subprocess, pathlib, os, hashlib, json
base=pathlib.Path(__file__).resolve().parent
runtime=pathlib.Path(os.environ['ISABELLE_HOME'])
def cyg(path):
    value = str(pathlib.Path(path).resolve()).replace('\\', '/')
    return '/cygdrive/' + value[0].lower() + value[2:] if value[1:2] == ':' else value
cmd=[str(runtime/'contrib/cygwin/bin/bash.exe'),'--noprofile','--norc','-c','export USER_HOME=${ISABELLE_USER_HOME:-$HOME}; export PATH=/usr/bin:/bin:$PATH; exec "$@"','amr-hol',cyg(runtime/'bin/isabelle'),'build','-e','-D',cyg(base),'-d',cyg(base.parent.parent/'cka-repair'),'-v','AMR_Advisory_V2']
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
(base/'build.log').write_text(r.stdout,encoding='utf-8')
print(r.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if r.returncode == 0:
    sources = [base / name for name in ['AMR_Protocol.thy', 'ROOT', 'build.py', 'interface.md', 'README.md']]
    sources += [base.parent.parent/'cka-repair'/name for name in ['ROOT','Bridge_Algebra_Repair.thy','Bridge_Trace_Repair.thy']]
    hashes = {str(p.relative_to(base.parent.parent)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (base/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
raise SystemExit(r.returncode)
