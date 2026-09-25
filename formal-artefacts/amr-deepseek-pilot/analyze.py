"""Offline audit and failure taxonomy for the completed live pilot; no API calls."""
from collections import Counter
import json
from pathlib import Path

import pilot
from assurance import valuations, step_violations, selection_violations
from language import parse_program, eval_select, eval_step, MODES, SELECT_FACTS, STEP_FACTS
from model import extract_model, model_step, model_select


def analyze():
    run = pilot.RUN
    expected = pilot.read_json(run / 'evidence-sha256.json')
    assert expected == {k: v for k, v in pilot.inventory(run).items() if k != 'evidence-sha256.json'}
    requests, records = pilot.verify_ready(run)
    stored = pilot.read_json(run / 'summary.json')
    assert pilot.trial.summarize(run) == stored['trial_summary']
    rows = []
    for index, (request, record) in enumerate(zip(requests, records), 1):
        raw = (run / record['response_path']).read_bytes()
        original_dir = pilot.PRIOR if index == 1 else run / 'transport' / f'{index:03d}'
        envelope = pilot.read_json(original_dir / 'http-body.bin')
        payload = pilot.read_json(original_dir / 'http-request.json')
        prompt = (run / request['prompt_path']).read_bytes().decode('utf-8')
        assert payload == pilot.smoke.payload_for(prompt)
        assert envelope['choices'][0]['message']['content'].encode('utf-8') == raw
        replay = json.loads(json.dumps(pilot.trial.assess_source(raw.decode('utf-8'))))
        assert replay == record['assessment']
        token_usage = pilot.smoke.usage_summary(envelope['usage'])
        assert token_usage is not None
        assert token_usage['input_tokens'] == record['metadata']['input_tokens']
        assert token_usage['output_tokens'] == record['metadata']['output_tokens']
        counts, corr, stop_errors = Counter(), Counter(), Counter()
        if replay['parse_pass']:
            program = parse_program(raw.decode('utf-8'))
            target = extract_model(program)
            for kind, names, modes in [('select', SELECT_FACTS, [None]), ('step', STEP_FACTS, MODES)]:
                for mode in modes:
                    for facts in valuations(names):
                        try:
                            value = eval_select(program, facts) if kind == 'select' else eval_step(program, mode, facts)
                            errors = selection_violations(value, facts) if kind == 'select' else step_violations(value, mode, facts)
                            counts.update(errors)
                            if 'stop_on_invalid_or_blocked_input' in errors:
                                stop_errors.update(['already_halted_but_not_reported_stopped' if facts['Halted'] else
                                                    'not_halted_but_reported_stopped'])
                            source_defined = True
                        except ValueError:
                            value, source_defined = None, False
                            counts.update(['no_matching_' + kind + '_rule'])
                        outputs = model_select(target, facts) if kind == 'select' else model_step(target, mode, facts)
                        if not source_defined or set(outputs) != {value}:
                            category = ('source_and_model_both_undefined' if not source_defined and not outputs else
                                        'different_defined_response' if source_defined and outputs else
                                        'one_side_undefined')
                            corr.update([category])
            assert sum(counts.values()) == replay['source_violation_inputs']
            assert sum(corr.values()) == replay['correspondence_mismatches']
        else:
            counts['parse_rejection'] = 1
        rows.append({'sequence': index, 'sample_id': record['sample_id'], 'attempt': record['attempt_index'],
                     'accepted': record['accepted'], 'parse_pass': replay['parse_pass'],
                     'checked_inputs': replay['checked_inputs'], 'source_violation_inputs': replay['source_violation_inputs'],
                     'model_violation_inputs': replay['model_violation_inputs'],
                     'correspondence_mismatches': replay['correspondence_mismatches'],
                     'failure_counts': dict(counts), 'correspondence_categories': dict(corr),
                     'stop_confirmation_error_counts': dict(stop_errors),
                     'raw_sha256': record['raw_sha256'], 'usage_summary': token_usage,
                     'provider_fingerprint': envelope.get('system_fingerprint')})
    initial = [r for r in rows if r['attempt'] == 0]
    chains = {sample: [r for r in rows if r['sample_id'] == sample] for sample in pilot.trial.SAMPLES}
    assert stored['trial_summary']['complete'] and stored['calls']['total'] == len(rows) == 18
    assert stored['calls']['new_dispatch_markers'] == len(list((run / 'transport').glob('*/dispatch.json'))) == 17
    return {'provenance': 'offline replay of actual retained DeepSeek responses; no new model calls',
            'evidence_files_verified': len(expected), 'preparation_inputs_verified': pilot.smoke.verify_preparation(),
            'requests': len(rows), 'initial_candidates': len(initial), 'repairs': len(rows) - len(initial),
            'initial_accepted': sum(r['accepted'] for r in initial),
            'eventually_accepted': sum(any(r['accepted'] for r in chain) for chain in chains.values()),
            'parse_rejections': sum(not r['parse_pass'] for r in rows),
            'parseable_semantic_rejections': sum(r['parse_pass'] and not r['accepted'] for r in rows),
            'unique_initial_sources': len({r['raw_sha256'] for r in initial}),
            'unique_all_sources': len({r['raw_sha256'] for r in rows}),
            'fingerprints': sorted({r['provider_fingerprint'] for r in rows}),
            'total_input_tokens': sum(r['usage_summary']['input_tokens'] for r in rows),
            'total_output_tokens': sum(r['usage_summary']['output_tokens'] for r in rows),
            'total_cache_hit_tokens': sum(r['usage_summary']['cache_hit_tokens'] for r in rows),
            'rows': rows, 'closed_loop': {'eligible': False, 'generated_episodes': 0,
                 'reason': 'all six chains exhausted without accepted source; no handwritten substitution'}}


if __name__ == '__main__':
    print(json.dumps(analyze(), ensure_ascii=False, indent=2))
