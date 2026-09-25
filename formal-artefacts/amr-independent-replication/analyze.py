"""Regenerate summaries outside the immutable run; no network or reasoning disclosure."""
from datetime import datetime
import gzip
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('replication_runner', HERE/'runner.py')
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def manifest_check(folder):
    expected = r.read_json(folder/'evidence-sha256.json')
    observed = r.inventory(folder)
    observed.pop('evidence-sha256.json')
    assert expected == observed
    return len(expected)


def analyze_run(run, output=HERE, physical=None):
    run, output = Path(run), Path(output)
    physical = Path(physical) if physical is not None else output/'closed-loop'
    result = r.read_json(run/'result.json')
    count = manifest_check(run)
    r.verify_inputs(run)
    states = r.initial_states()
    records, accepted_keys = [], set()
    for folder in sorted((run/'attempts').iterdir()):
        out = r.read_json(folder/'outcome.json')
        sid = out['sample_id']
        assert r.next_slot(states) == (sid,out['attempt'])
        prompt, feedback = r.prompt_for(states[sid])
        payload = r.read_json(folder/'http-request.json')
        assert payload == r.payload_for(prompt,sid)
        assert (folder/'prompt.txt').read_bytes() == prompt.encode('utf-8')
        assert r.read_json(folder/'feedback.json') == feedback
        raw, envelope, usage_summary, fatal = r.decode_response(folder,r.read_json(folder/'transport.json'),payload)
        assert raw == (folder/'response.bin').read_bytes()
        assert usage_summary == out['usage_summary']
        assert out['thinking'] == r.thinking_metadata(envelope,payload)
        report = json.loads(gzip.decompress((folder/'assessment.json.gz').read_bytes()))
        recorded_fatal = out['fatal']
        assessment_failed = ('assessment_error_type' in report
                             and report.get('parse_error') == 'assessment infrastructure failed')
        assert recorded_fatal == fatal or (recorded_fatal == 'assessment_error'
            and fatal is None and assessment_failed)
        previous = states[sid]['report']
        valid = report['parse_pass'] and report['checked_inputs'] == 1824
        accepted = bool(report['accepted'] and recorded_fatal is None)
        assert out['accepted'] is accepted
        comparable = valid and previous is not None and previous['parse_pass']
        before = set(previous['failure_input_ids']) if previous else set()
        after = set(report['failure_input_ids'])
        if accepted:
            accepted_keys.add(r.d.program_key(raw.decode('utf-8'),12))
        choices = envelope.get('choices') or [{}]
        records.append({'sequence':folder.name,'sample_id':sid,'attempt':out['attempt'],'phase':out['phase'],
            'finish_reason':choices[0].get('finish_reason'),'fatal':recorded_fatal,'accepted':accepted,
            'source_sha256':r.sha(folder/'response.bin'),'response_bytes':len(raw),
            'parse_pass':report['parse_pass'],'checked_inputs':report['checked_inputs'],
            'source_violation_inputs':report['source_violation_inputs'] if valid else None,
            'model_violation_inputs':report['model_violation_inputs'] if valid else None,
            'correspondence_mismatches':report['correspondence_mismatches'] if valid else None,
            'repaired_previous_inputs':len(before-after) if comparable else None,
            'new_bad_inputs':len(after-before) if comparable else None,
            'rule_counts':report.get('rule_counts'),'thinking':out['thinking'],'usage_summary':usage_summary,'usage':envelope.get('usage'),
            'provider_model':out['provider_model'],'fingerprint':out['fingerprint'],
            'elapsed_seconds':(datetime.fromisoformat(out['finished_at_utc'])
                               -datetime.fromisoformat(out['started_at_utc'])).total_seconds()})
        r.advance(states[sid],raw,report,feedback,out,(folder/'response.bin').relative_to(run).as_posix())
    assert json.loads(r.json_bytes(r.public_states(states))) == result['samples']
    dispatches = len(list((run/'attempts').glob('*/dispatch.json')))
    assert len(records) == result['new_calls'] <= r.MAX_CALLS
    assert dispatches == result['network_dispatches'] <= len(records)
    initial = [x for x in records if x['attempt']==0]
    assert sum(s['initial_accepted'] is True for s in states.values()) == result['initial_accepted_count']
    assert sum(s['stop']=='accepted' for s in states.values()) == result['eventually_accepted_count']
    fatal_records = [x for x in records if x['fatal'] is not None]
    assert len(fatal_records) <= 1
    if fatal_records:
        assert records[-1] is fatal_records[0] and result['stop'] == fatal_records[0]['fatal']
    if result['stop']=='protocol_complete':
        assert not fatal_records and r.next_slot(states) is None
        assert result['selected_sources']==r.select_sources(states,run)
    else:
        assert result['selected_sources']==[]
    pattern = re.compile(rb'(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}')
    assert not any(pattern.search(p.read_bytes()) for p in run.rglob('*') if p.is_file())
    samples = {sid:{k:s[k] for k in ('calls','repairs','stop','initial_accepted','first_accepted_attempt','accepted_response')}
               for sid,s in states.items()}
    analysis = {'protocol_id':result['protocol_id'],'calls':records,'stop':result['stop'],'samples':samples,
        'initial_requests_planned':6,'initial_requests_executed':len(initial),
        'initial_accepted_count':result['initial_accepted_count'],
        'eventually_accepted_count':result['eventually_accepted_count'],
        'unique_accepted_raw_sources':len({x['source_sha256'] for x in records if x['accepted']}),
        'unique_accepted_canonical_programs':len(accepted_keys),
        'selected_sources':result['selected_sources'],
        'total_input_tokens':sum((x['usage'] or {}).get('prompt_tokens',0) for x in records),
        'total_completion_tokens':sum((x['usage'] or {}).get('completion_tokens',0) for x in records),
        'cumulative_live_calls':30+len(records),
        'scope':'Six fresh contexts for one task with three prompt variants, not six independent industrial tasks.'}
    verification = {'run_manifest_files':count,'frozen_generation_inputs':len(r.read_json(run/'frozen-inputs.json')),
        'exact_run_inventory':True,'historical_and_frozen_inputs_unchanged':True,
        'provider_content_usage_prompt_feedback_order_and_states_match':True,
        'initial_and_eventual_counts_verified':True,'credential_shaped_values_absent':True,
        'independent_full_assessment_audit':'result-audit.md'}
    if (physical/'summary.json').exists():
        physical_count = manifest_check(physical)
        summary = r.read_json(physical/'summary.json')
        inputs = r.read_json(physical/'pre-run.json')['input_sha256']
        assert all(r.sha(Path(p))==h for p,h in inputs.items())
        assert summary['unique_source_count']==len(result['selected_sources'])
        assert summary['episode_count']==len(summary['episodes'])==5+5*len(result['selected_sources'])
        assert len(summary['source_catalog'])==len(result['selected_sources'])
        expected_mapping = {}
        for entry,selection in zip(summary['source_catalog'],result['selected_sources']):
            assert entry['selection']==selection
            assert (physical/'sources'/(entry['source_key']+'.json')).read_bytes()==(run/selection['response_path']).read_bytes()
            for sid in selection['sample_ids']:
                assert sid not in expected_mapping
                expected_mapping[sid]=entry['source_key']
            for case in ('normal_A','normal_B','temporary','blackout','permanent'):
                assert summary['episodes'][entry['source_key']+'_'+case]['source_id']==selection['sha256']
        assert summary['sample_to_source_key']==expected_mapping
        assert summary['inputs_unchanged'] and summary['new_model_calls']==0
        verification['physics']={'exact_inventory':True,'manifest_files':physical_count,'inputs_unchanged':True,
            'source_identity_and_sample_mapping':True,'episode_count':summary['episode_count'],
            'new_model_calls':0,'independent_trace_audit':'result-audit.md'}
        (output/'closed-loop-status.json').write_bytes(r.json_bytes({'entered':True,
            'unique_sources':summary['unique_source_count'],'episodes':summary['episode_count'],
            'reference_episodes':5,'sample_to_source_key':expected_mapping,'manual_replacement':False,'new_model_calls':0}))
    (output/'analysis.json').write_bytes(r.json_bytes(analysis))
    (output/'verification.json').write_bytes(r.json_bytes(verification))
    return analysis


def main():
    analysis = analyze_run(HERE/'run')
    print(json.dumps(analysis,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
