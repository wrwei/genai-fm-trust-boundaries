"""Build the standalone AMR progress session; preserve prior build attempts."""
import os
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
INSTALL = Path(os.environ['ISABELLE_HOME'])
REPO = BASE.parents[2]

def cyg(path):
    value = path.resolve().as_posix()
    return '/cygdrive/' + value[0].lower() + value[2:]

cmd = [str(INSTALL/'contrib/cygwin/bin/bash.exe'), '--noprofile', '--norc', '-c',
       'export USER_HOME=${ISABELLE_USER_HOME:-$HOME}; '
       'export PATH=/usr/bin:/bin:$PATH; exec "$@"', 'progress-hol',
       cyg(INSTALL/'bin/isabelle'), 'build', '-e', '-D', cyg(BASE), '-v', 'AMR_Progress_Obligations']
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, encoding='utf-8', errors='replace')
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
(BASE/'build-attempts').mkdir(exist_ok=True)
(BASE/'build-attempts'/f'{stamp}.log').write_text(result.stdout, encoding='utf-8')
(BASE/'build.log').write_text(result.stdout, encoding='utf-8')
print(result.stdout.encode('ascii', 'backslashreplace').decode())
if result.returncode == 0:
    paths = list(BASE.glob('*.thy')) + [BASE/'ROOT', Path(__file__)]
    (BASE/'source-hashes.json').write_text(json.dumps({p.relative_to(REPO).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, indent=2)+'\n')
raise SystemExit(result.returncode)
