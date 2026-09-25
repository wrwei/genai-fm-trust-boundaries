"""Aggregate archived output without exposing reasoning or contacting a provider."""
from datetime import datetime
import gzip
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extended_runner', HERE/'runner.py')
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def main():
    run = HERE/'run'
    result = r.read_json(run/'result.json')
    manifest = r.read_json(run/'evidence-sha256.json')
    observed = r.inventory(run)
    observed.pop('evidence-sha256.json')
    assert observed == manifest
    r.verify_inputs(run)
    states = r.initial_states()
    records = []
    old_sources = list((r.PRIOR/'records').glob('*/response.bin'))
    old_sources += list((r.FORGE_RUN/'attempts').glob('*/response.bin'))
    old_sources += list((r.THINKING_RUN/'attempts').glob('*/response.bin'))
    for folder in sorted((run/'attempts').iterdir()):
        out = r.read_json(folder/'outcome.json')
        cid = out['condition']
        assert r.next_slot(states) == (cid, out['repair'])
        prompt, feedback = r.prompt_for(states[cid])
        payload = r.read_json(folder/'http-request.json')
        assert payload == r.payload_for(prompt, cid)
        assert (folder/'prompt.txt').read_bytes() == prompt.encode('utf-8')
        assert r.read_json(folder/'feedback.json') == feedback
        raw, envelope, usage_summary, fatal = r.decode_response(folder, r.read_json(folder/'transport.json'), payload)
        assert raw == (folder/'response.bin').read_bytes()
        assert usage_summary == out.get('usage_summary') and fatal == out['fatal']
        assert out['thinking'] == r.thinking_metadata(envelope, payload)
        report = json.loads(gzip.decompress((folder/'assessment.json.gz').read_bytes()))
        valid = report['parse_pass'] and report['checked_inputs'] == 1824
        before = set(states[cid]['report']['failure_input_ids'])
        after = set(report['failure_input_ids'])
        records.append({'attempt': folder.name, 'condition': cid, 'repair': out['repair'],
            'finish_reason': envelope.get('choices', [{}])[0].get('finish_reason'),
            'fatal': fatal, 'accepted': out['accepted'], 'source_sha256': r.sha(folder/'response.bin'),
            'response_bytes': len(raw), 'parse_pass': report['parse_pass'],
            'checked_inputs': report['checked_inputs'],
            'source_violation_inputs': report['source_violation_inputs'] if valid else None,
            'model_violation_inputs': report['model_violation_inputs'] if valid else None,
            'correspondence_mismatches': report['correspondence_mismatches'] if valid else None,
            'repaired_previous_inputs': len(before-after) if valid else None,
            'new_bad_inputs': len(after-before) if valid else None,
            'rule_counts': report['rule_counts'], 'thinking': out['thinking'], 'usage_summary': usage_summary,
            'usage': envelope.get('usage'), 'provider_model': out['provider_model'],
            'fingerprint': out['fingerprint'],
            'elapsed_seconds': (datetime.fromisoformat(out['finished_at_utc'])
                                - datetime.fromisoformat(out['started_at_utc'])).total_seconds(),
            'byte_identical_prior_sources': [p.relative_to(r.ROOT).as_posix() for p in old_sources
                                             if p.read_bytes() == raw]})
        r.advance(states[cid], raw, report, feedback, out, (folder/'response.bin').relative_to(run).as_posix())
    assert len(records) == result['new_calls'] == result['network_dispatches'] <= 8
    for cid, state in states.items():
        for key in ('repairs','stop','first_accepted_repair','accepted_response'):
            assert state[key] == result['conditions'][cid][key]
    pattern = re.compile(rb'(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}')
    assert not any(pattern.search(p.read_bytes()) for p in run.rglob('*') if p.is_file())
    analysis = {'protocol_id': result['protocol_id'], 'calls': records, 'stop': result['stop'],
        'conditions': {cid:{k:s[k] for k in ('repairs','stop','first_accepted_repair','accepted_response')}
                       for cid,s in states.items()},
        'selected_source': result['selected_for_exploratory_physics'],
        'total_input_tokens': sum((x['usage'] or {}).get('prompt_tokens',0) for x in records),
        'total_completion_tokens': sum((x['usage'] or {}).get('completion_tokens',0) for x in records),
        'cumulative_live_calls': 27+len(records),
        'scope': 'Related repair trajectories from one observed failure; not independent task samples.'}
    # Derived summaries live outside the immutable run and can be regenerated.
    (HERE/'analysis.json').write_bytes(r.json_bytes(analysis))
    verification = {'run_manifest_files': len(manifest),
        'frozen_generation_inputs': len(r.read_json(run/'frozen-inputs.json')),
        'exact_run_inventory': True, 'historical_and_frozen_inputs_unchanged': True,
        'provider_content_and_usage_match': True, 'prompts_feedback_order_and_states_match': True,
        'credential_shaped_values_absent': True,
        'independent_full_assessment_audit': 'result-audit.md'}
    physical = HERE/'closed-loop'
    if (physical/'summary.json').exists():
        summary = r.read_json(physical/'summary.json')
        physical_manifest = r.read_json(physical/'evidence-sha256.json')
        physical_inventory = r.inventory(physical)
        physical_inventory.pop('evidence-sha256.json')
        assert physical_manifest == physical_inventory
        inputs = r.read_json(physical/'pre-run.json')['input_sha256']
        assert all(r.sha(Path(p)) == expected for p,expected in inputs.items())
        selected = result['selected_for_exploratory_physics']
        assert selected == summary['source_selection']
        assert (physical/'selected-source.json').read_bytes() == (run/selected['response_path']).read_bytes()
        assert summary['episode_count'] == len(summary['episodes']) == 10
        assert summary['inputs_unchanged'] and summary['new_model_calls'] == 0
        assert all(episode['source_id'] == selected['sha256'] for name,episode in summary['episodes'].items()
                   if name.endswith('_source'))
        verification['physics'] = {'exact_inventory': True, 'manifest_files': len(physical_manifest),
            'inputs_unchanged': True, 'exact_source_identity': True, 'episode_count': 10,
            'new_model_calls': 0, 'independent_trace_audit': 'result-audit.md'}
        (HERE/'closed-loop-status.json').write_bytes(r.json_bytes({'entered': True, 'episodes': 10,
            'selected_source': selected, 'manual_replacement': False, 'new_model_calls': 0,
            'all_scenarios_executed': True, 'scope': summary['scope']}))
    (HERE/'verification.json').write_bytes(r.json_bytes(verification))
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
