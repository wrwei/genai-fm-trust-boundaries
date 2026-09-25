"""Read-only aggregation of the completed live run; never displays reasoning text."""
from datetime import datetime
import gzip
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('thinking_runner', HERE/'runner.py')
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def main():
    run = HERE/'run'
    result = r.read_json(run/'result.json')
    manifest = r.read_json(run/'evidence-sha256.json')
    observed = r.inventory(run)
    observed.pop('evidence-sha256.json')
    assert manifest == observed
    r.verify_inputs(run)
    initial = r.initial_states()
    records = []
    old_sources = list((r.PRIOR/'records').glob('*/response.bin'))
    old_sources += list((r.FORGE_RUN/'attempts').glob('*/response.bin'))
    for folder in sorted((run/'attempts').iterdir()):
        out = r.read_json(folder/'outcome.json')
        payload = r.read_json(folder/'http-request.json')
        transport = r.read_json(folder/'transport.json')
        report = json.loads(gzip.decompress((folder/'assessment.json.gz').read_bytes()))
        raw, envelope, usage_summary, fatal = r.decode_response(folder, transport, payload)
        assert raw == (folder/'response.bin').read_bytes()
        assert usage_summary == out.get('usage_summary') and fatal == out['fatal']
        assert out['thinking'] == r.thinking_metadata(envelope, payload)
        if out['repair'] == 1:
            prompt, feedback = r.prompt_for(initial[out['condition']])
            assert payload == r.payload_for(prompt, out['condition'])
            assert (folder/'prompt.txt').read_bytes() == prompt.encode('utf-8')
            assert r.read_json(folder/'feedback.json') == feedback
        usage = envelope['usage']
        before = set(initial[out['condition']]['report']['failure_input_ids'])
        after = set(report['failure_input_ids'])
        evaluated = report['parse_pass'] and report['checked_inputs'] == 1824
        records.append({
            'attempt': folder.name, 'condition': out['condition'], 'repair': out['repair'],
            'finish_reason': envelope['choices'][0]['finish_reason'], 'fatal': fatal,
            'accepted': out['accepted'], 'response_bytes': len(raw),
            'parse_pass': report['parse_pass'], 'checked_inputs': report['checked_inputs'],
            'source_violation_inputs': report['source_violation_inputs'] if evaluated else None,
            'model_violation_inputs': report['model_violation_inputs'] if evaluated else None,
            'correspondence_mismatches': report['correspondence_mismatches'] if evaluated else None,
            'repaired_seed_inputs': len(before-after) if evaluated else None,
            'new_bad_inputs': len(after-before) if evaluated else None,
            'rule_counts': report['rule_counts'],
            'source_sha256': r.sha(folder/'response.bin'),
            'byte_identical_prior_sources': [p.relative_to(r.ROOT).as_posix() for p in old_sources
                                             if p.read_bytes() == raw],
            'usage': usage, 'thinking': out['thinking'], 'usage_summary': usage_summary,
            'fingerprint': out['fingerprint'], 'provider_model': out['provider_model'],
            'elapsed_seconds': (datetime.fromisoformat(out['finished_at_utc'])
                                - datetime.fromisoformat(out['started_at_utc'])).total_seconds(),
        })
    assert len(records) == result['new_calls'] == result['network_dispatches'] == 2
    assert records[1]['fatal'] == result['stop'] == 'truncated'
    assert result['selected_for_exploratory_physics'] is None
    assert records[1]['response_bytes'] == 0 and records[1]['checked_inputs'] == 0
    assert records[1]['usage']['completion_tokens'] == records[1]['thinking']['reasoning_tokens'] == 8192
    assert not (HERE/'closed-loop').exists()
    # Scan only credential-shaped strings, without opening the external key file.
    key_pattern = re.compile(rb'(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}')
    assert not any(key_pattern.search(p.read_bytes()) for p in run.rglob('*') if p.is_file())
    analysis = {'protocol_id': result['protocol_id'], 'calls': records, 'stop': result['stop'],
        'total_input_tokens': sum(x['usage']['prompt_tokens'] for x in records),
        'total_completion_tokens': sum(x['usage']['completion_tokens'] for x in records),
        'interpretation': 'Truncated thinking response is unevaluable, not a zero-violation program. '
            'Only one repair per arm was attempted; the non-thinking arm was interrupted by the batch stop. '
            'One previously observed failure is not an independent evaluation sample.',
        'new_physical_episodes': 0}
    r.write_json(HERE/'analysis.json', analysis)
    r.write_json(HERE/'verification.json', {'run_manifest_files': len(manifest),
        'frozen_generation_inputs': len(r.read_json(run/'frozen-inputs.json')),
        'exact_run_inventory': True, 'historical_and_frozen_inputs_unchanged': True,
        'provider_content_and_usage_match': True, 'initial_prompts_and_feedback_match': True,
        'credential_shaped_values_absent': True,
        'no_physical_output_created': True, 'independent_full_assessment_audit': 'result-audit.md'})
    r.write_json(HERE/'closed-loop-status.json', {'entered': False, 'episodes': 0,
        'reason': 'batch stopped on T12-F truncation; neither condition has an accepted controller',
        'source_selection': None, 'manual_replacement': False, 'new_model_calls': 0})
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
