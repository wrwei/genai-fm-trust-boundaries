import pathlib
import sys
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
try:
    import source_milestones
except ImportError:
    source_milestones = None


class SourceMilestoneTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(source_milestones, 'source_milestones has not been implemented')

    def test_exact_selected_source_produces_literal_milestone_responses(self):
        expected = {
            'unusable': ('Brake', 'BrakeRequested'),
            'braking_owner': ('Brake', 'BrakeRequested'),
            'halted_owner': ('Proceed', 'Traversing'),
            'waiting_owner': ('Proceed', 'Traversing'),
            'clear_owner': ('Release', 'Traversing'),
            'released_motion': ('Proceed', 'Traversing'),
            'goal_brake': ('Brake', 'BrakeRequested'),
            'goal_finish': ('Finish', 'Done'),
        }
        rows = source_milestones.evaluate()
        self.assertEqual({r['name']:(r['actual_action'],r['actual_next']) for r in rows}, expected)
        self.assertTrue(all(r['passed'] for r in rows))

    def test_selected_source_identity_is_fixed(self):
        self.assertEqual(source_milestones.SOURCE_ID,
                         '9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd')

    def test_unknown_mode_and_fact_override_are_rejected(self):
        with self.assertRaises(ValueError):
            source_milestones.evaluate_case('waiting_owner', mode='Unknown')
        with self.assertRaises(ValueError):
            source_milestones.evaluate_case('waiting_owner', facts_override={'Unknown': True})


if __name__ == '__main__':
    unittest.main()
