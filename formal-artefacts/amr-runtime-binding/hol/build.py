"""Build only the additive session, preserve prior session exports/logs."""
import os
import hashlib
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
INSTALL = Path(os.environ['ISABELLE_HOME'])

def cyg(path):
    value = str(path.resolve()).replace('\\', '/')
    return '/cygdrive/' + value[0].lower() + value[2:]

cmd = [str(INSTALL/'contrib/cygwin/bin/bash.exe'), '--noprofile', '--norc', '-c',
       'export USER_HOME=${ISABELLE_USER_HOME:-$HOME}; '
       'export PATH=/usr/bin:/bin:$PATH; exec "$@"', 'binding-hol',
       cyg(INSTALL/'bin/isabelle'), 'build', '-e', '-D', cyg(BASE),
       '-d', cyg(REPO/'formal-artefacts/amr-advisory-v2/hol'),
       '-d', cyg(REPO/'formal-artefacts/cka-repair'), '-v', 'AMR_Runtime_Binding']
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, encoding='utf-8', errors='replace')
(BASE/'build.log').write_text(result.stdout, encoding='utf-8')
print(result.stdout.encode('ascii', 'backslashreplace').decode())
if result.returncode == 0:
    paths = [BASE/'AMR_Runtime_Binding.thy', BASE/'ROOT', Path(__file__),
             REPO/'formal-artefacts/amr-advisory-v2/hol/AMR_Protocol.thy',
             REPO/'formal-artefacts/cka-repair/Bridge_Trace_Repair.thy',
             REPO/'formal-artefacts/cka-repair/Bridge_Algebra_Repair.thy']
    (BASE/'source-hashes.json').write_text(json.dumps({p.relative_to(REPO).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, indent=2)+'\n')
raise SystemExit(result.returncode)
