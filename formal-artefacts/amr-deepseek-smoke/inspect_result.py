"""Read-only replay and a labelled, single-witness post hoc diagnosis; no API."""
import hashlib
import json
from pathlib import Path

import smoke
from assurance import assess_source, obligation
from language import STEP_FACTS, MODE_FACTS, _expression, _evaluate

run = Path(__file__).resolve().parent / 'run'
hashes = json.loads((run / 'evidence-sha256.json').read_text(encoding='utf-8'))
for name, expected in hashes.items():
    assert hashlib.sha256((run / name).read_bytes()).hexdigest() == expected, name
raw = (run / 'records/001/response.bin').read_bytes()
record = json.loads((run / 'records/001/record.json').read_text(encoding='utf-8'))
result = json.loads((run / 'smoke-result.json').read_text(encoding='utf-8'))
http = json.loads((run / 'http-body.bin').read_bytes())
assert http['choices'][0]['message']['content'].encode('utf-8') == raw
assert assess_source(raw.decode('utf-8')) == record['assessment'] == result['assessment']
assert smoke.usage_summary(http['usage']) == result['usage_summary']
assert smoke.trial.summarize(run) == result['trial_summary']
assert len(list((run / 'requests').glob('*/request.json'))) == 1
assert len(list((run / 'records').glob('*/record.json'))) == 1

# Descriptive diagnosis only: inspect the original JSON's first rule in one
# context. Do not bypass the program parser or count this as an accepted program,
# a full semantic assessment, a repair, or a physical simulation.
program = json.loads(raw)
assert program['step'][0]['when'] == program['step'][1]['when']
facts = dict.fromkeys(STEP_FACTS, False)
facts.update(ObservationUsable=True, PedestrianBlocked=True, Halted=True, TaskActive=True)
mode = 'Idle'
expression_facts = {**facts, **{name: name == 'ModeIdle' for name in MODE_FACTS}}
first = program['step'][0]
assert _evaluate(_expression(first['when'], STEP_FACTS + MODE_FACTS), expression_facts)
required_name, required_response = obligation(mode, facts)
diagnosed_response = (first['action'], first['next'])
assert diagnosed_response != required_response
print(json.dumps({
    'evidence_files_verified': len(hashes),
    'preparation_inputs_verified': smoke.verify_preparation(),
    'raw_assistant_content_exact': True, 'assessment_replay_exact': True,
    'usage_summary_recomputed_exact': True, 'recorded_requests': 1, 'recorded_responses': 1,
    'valid_json': True, 'select_rules': len(program['select']), 'step_rules': len(program['step']),
    'formal_checked_inputs': record['assessment']['checked_inputs'],
    'post_hoc_diagnosis': {
        'scope': 'single-witness rule inspection; outside the formal acceptance result',
        'identical_condition_step_rules_1_based': [1, 2],
        'effect': 'first-match semantics always shadows the second rule',
        'mode': mode, 'facts': facts, 'first_rule_response': diagnosed_response,
        'required_response': required_response, 'obligation': required_name,
        'physical_consequence_measured': False,
    },
}, ensure_ascii=False, indent=2))
