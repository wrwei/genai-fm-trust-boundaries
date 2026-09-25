"""Reproduce the archived, inadequate v1 goal-stop contract without patching it."""
from pathlib import Path
import argparse, gzip, hashlib, json, sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[2]/'amr-corridor'
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(HERE))
from closed_loop import run_supervised_episode

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    source=(HERE/'source.json').read_text(encoding='utf-8')
    with gzip.open(args.output/'trace.jsonl.gz','wt',encoding='utf-8') as stream:
        result=run_supervised_episode(source,emit=lambda row:stream.write(json.dumps(row)+'\n'))
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    identity=dict(scope='Archived exploratory draft-spec failure; not an LLM failure',
                  archived_code={p.name:sha(p) for p in HERE.glob('*.py')},source_sha256=sha(HERE/'source.json'),
                  baseline_code={p.name:sha(p) for p in BASE.glob('*.py')},
                  outputs={p.name:sha(p) for p in args.output.iterdir() if p.is_file()})
    (args.output/'manifest.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('completed_robots','controller_completed_robots','time','final_poses','runtime_rejections')}))

if __name__=='__main__':main()
