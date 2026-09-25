"""Candidate defects and semantic mismatches must survive separate accounting."""
from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from assurance import assess_source, obligation

def candidate(name):
    return (HERE/'candidates'/f'{name}.json').read_text(encoding='utf-8')

class AssuranceTests(unittest.TestCase):
    def test_released_goal_requires_braking_until_halted(self):
        facts = dict(ObservationUsable=True, TaskActive=True, PedestrianBlocked=False,
                     Released=True, AtGoal=True, Halted=False, OwnReservation=False, BodyClearOfZ=True)
        self.assertEqual(obligation('Traversing', facts),
                         ('brake_at_released_goal_until_halted', ('Brake', 'BrakeRequested')))

    def test_archived_v1_goal_stop_gap_is_rejected_by_revised_contract(self):
        original = (HERE/'development'/'spec-v1'/'source.json').read_text(encoding='utf-8')
        result = assess_source(original)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['spec_id'], 'amr-supervisor-obligations/v1.1')
        self.assertGreater(result['source_violation_inputs'], 0)

    def test_malformed_unicode_returns_parse_failure_without_fabricated_hash(self):
        result = assess_source(chr(0xd800))
        self.assertFalse(result['parse_pass'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['checked_inputs'], 0)
        self.assertIsNone(result['source_sha256'])
        self.assertTrue(result['parse_error'])

    def test_non_string_input_returns_structured_parse_failure(self):
        for text in (None, 12, b'{}', {}):
            with self.subTest(text=text):
                result = assess_source(text)
                self.assertFalse(result['parse_pass'])
                self.assertFalse(result['accepted'])
                self.assertEqual(result['checked_inputs'], 0)
                self.assertIsNone(result['source_sha256'])
                self.assertTrue(result['parse_error'])

    def test_empty_step_is_parse_valid_but_non_total(self):
        data = json.loads(candidate('authored_reference'))
        data['step'] = []
        result = assess_source(json.dumps(data))
        self.assertTrue(result['parse_pass'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['checked_inputs'], 1824)
        self.assertEqual(result['source_violation_inputs'], 1792)
        self.assertEqual(result['model_violation_inputs'], 1792)
        self.assertEqual(result['correspondence_mismatches'], 1792)
        self.assertIn('no matching step rule', result['source_witnesses'][0]['violations'])

    def test_reference_and_equivalent_expression_are_accepted(self):
        for name in ('authored_reference', 'authored_demorgan'):
            result = assess_source(candidate(name))
            self.assertTrue(result['accepted'])
            self.assertEqual(result['checked_inputs'], 1824)

    def test_candidate_safety_and_progress_defects_are_rejected_raw(self):
        for name in ('ignore_pedestrian', 'always_brake', 'early_release', 'finish_unhalted', 'reversed_observation'):
            result = assess_source(candidate(name))
            self.assertFalse(result['accepted'])
            self.assertGreater(result['source_violation_inputs'], 0, name)
            self.assertTrue(result['source_witnesses'])

    def test_unrestricted_code_is_parse_failure_not_repaired_candidate(self):
        result = assess_source(candidate('external_call'))
        self.assertFalse(result['parse_pass'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['checked_inputs'], 0)

    def test_both_policies_can_pass_while_source_model_disagree(self):
        result = assess_source(candidate('authored_reference'), fault='choose_b_when_both')
        self.assertEqual(result['source_violation_inputs'], 0)
        self.assertEqual(result['model_violation_inputs'], 0)
        self.assertGreater(result['correspondence_mismatches'], 0)
        self.assertFalse(result['accepted'])

    def test_model_only_pass_does_not_make_bad_source_pass(self):
        result = assess_source(candidate('reversed_observation'), fault='invert_observation_tests')
        self.assertTrue(result['model_policy_pass'])
        self.assertFalse(result['source_policy_pass'])
        self.assertFalse(result['correspondence_pass'])
        self.assertFalse(result['accepted'])

    def test_missing_priority_negations_do_not_preserve_first_match(self):
        result = assess_source(candidate('authored_reference'), fault='omit_priority')
        self.assertGreater(result['correspondence_mismatches'], 0)
        self.assertFalse(result['accepted'])

if __name__ == '__main__':
    unittest.main()
