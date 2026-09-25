"""Record authored candidate checks and paired source-driven physical episodes."""
import argparse
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
from contextlib import contextmanager

from language import parse_program
from model import extract_model
from assurance import assess_source, SPEC_ID
from closed_loop import run_supervised_episode, BASELINE

HERE=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def source(name):return (HERE/'candidates'/(name+'.json')).read_bytes().decode('utf-8')
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def snapshot():
    files=list(HERE.glob('*.py'))+list((HERE/'tests').glob('test_*.py'))+list((HERE/'candidates').glob('*.json'))
    return {str(p.relative_to(HERE)):sha(p) for p in sorted(files)}

@contextmanager
def trace(path):
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
            with io.TextIOWrapper(zipped,encoding='utf-8',newline='\n') as stream:
                yield lambda row:stream.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    before=snapshot()
    baseline_before={p.name:sha(p) for p in sorted(BASELINE.glob('*.py'))}
    index=json.loads((HERE/'candidates/index.json').read_text(encoding='utf-8'))
    candidates={}
    for row in index['candidates']:
        text=source(row['id'])
        assert hashlib.sha256(text.encode('utf-8')).hexdigest()==row['sha256']
        result=assess_source(text)
        candidates[row['id']]=result
        write(args.output/(row['id']+'.assessment.json'),result)
        if result['parse_pass']:
            write(args.output/(row['id']+'.model.json'),extract_model(parse_program(text)).to_dict())
        print(json.dumps(dict(candidate=row['id'],accepted=result['accepted'],source_bad=result['source_violation_inputs'],model_bad=result['model_violation_inputs'],mismatches=result['correspondence_mismatches'])),flush=True)
    fault_results={}
    for name,candidate,fault in [('F_priority','authored_reference','omit_priority'),
                               ('F_safe_different','authored_reference','choose_b_when_both'),
                               ('F_model_only','reversed_observation','invert_observation_tests')]:
        result=assess_source(source(candidate),fault=fault)
        fault_results[name]=dict(candidate=candidate,**result)
        write(args.output/(name+'.assessment.json'),fault_results[name])
        write(args.output/(name+'.model.json'),extract_model(parse_program(source(candidate)),fault=fault).to_dict())
        print(json.dumps(dict(fault=name,source_pass=result['source_policy_pass'],model_pass=result['model_policy_pass'],mismatches=result['correspondence_mismatches'])),flush=True)
    configs=[('normal_A',{}),('normal_B',dict(preference='B')),
             ('temporary',dict(pedestrian='temporary')),('blackout',dict(sensor_blackout=(10.,15.))),
             ('permanent',dict(pedestrian='permanent'))]
    episodes={}
    comparisons={}
    for case,config in configs:
        pair={}
        for arm in ('handwritten','source'):
            key=case+'_'+arm
            with trace(args.output/(key+'.trace.jsonl.gz')) as emit:
                result=run_supervised_episode(None if arm=='handwritten' else source('authored_reference'),
                                               handwritten=arm=='handwritten',emit=emit,**config)
            write(args.output/(key+'.json'),result)
            pair[arm]=result
            episodes[key]={k:v for k,v in result.items() if k not in ('events','assessment')}
            print(json.dumps(dict(episode=key,time=result['time'],done=result['completed_robots'],collisions=result['collision_pairs'],rejections=len(result['runtime_rejections']))),flush=True)
        fields=('completed_robots','grant_order','collision_pairs','unresolved_pairs','early_releases','safe_and_complete')
        comparisons[case]=dict(equal_outcomes=all(pair['source'][k]==pair['handwritten'][k] for k in fields),
                               completion_time_difference=abs(pair['source']['time']-pair['handwritten']['time']))
    with trace(args.output/'normal_A_equivalent.trace.jsonl.gz') as emit:
        equivalent=run_supervised_episode(source('authored_demorgan'),emit=emit)
    write(args.output/'normal_A_equivalent.json',equivalent)
    episodes['normal_A_equivalent']={k:v for k,v in equivalent.items() if k not in ('events','assessment')}
    write(args.output/'summary.json',dict(spec_id=SPEC_ID,candidates=candidates,translator_faults=fault_results,
                                         episodes=episodes,paired_comparisons=comparisons,
                                         provenance='Assistant-authored fixtures; no independent LLM sampling; finite checks not proofs'))
    after=snapshot()
    baseline_after={p.name:sha(p) for p in sorted(BASELINE.glob('*.py'))}
    manifest=dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),
                  spec_id=SPEC_ID,input_sha256=before,input_sha256_after=after,inputs_stable=before==after,
                  baseline_sha256=baseline_before,baseline_stable=baseline_before==baseline_after,
                  outputs_sha256={p.name:sha(p) for p in sorted(args.output.iterdir()) if p.is_file()},
                  candidate_count=len(candidates),parseable_candidates=sum(r['parse_pass'] for r in candidates.values()),
                  accepted_candidates=sum(r['accepted'] for r in candidates.values()),
                  translator_fault_checks=len(fault_results),closed_loop_runs=len(episodes),
                  archived_draft_failure_runs_separate=1,external_llm_calls=0,new_formal_builds=0)
    write(args.output/'manifest.json',manifest)
    if not manifest['inputs_stable'] or not manifest['baseline_stable']:
        raise RuntimeError('Input or baseline identity changed during run; evidence retained but invalid for final reporting')

if __name__=='__main__':main()
