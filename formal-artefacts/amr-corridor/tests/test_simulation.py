"""Closed-loop outcomes; expected invariants do not call controller helpers."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation import run_episode, run_stopping_witness, geometry_witness
import simulation


class SimulationTests(unittest.TestCase):
    def test_reference_completes_both_tasks_and_advice_changes_order(self):
        for preference in ['A', 'B']:
            result = run_episode(preference=preference)
            self.assertEqual(result['completed_robots'], ['A', 'B'])
            self.assertEqual(result['grant_order'][0], preference)
            self.assertEqual(result['collision_pairs'], [])
            self.assertEqual(result['unresolved_pairs'], [])
            self.assertEqual(result['early_releases'], [])

    def test_temporary_blockage_recovers_but_permanent_blockage_does_not(self):
        temporary = run_episode(pedestrian='temporary')
        permanent = run_episode(pedestrian='permanent', horizon=35)
        self.assertEqual(temporary['completed_robots'], ['A', 'B'])
        self.assertGreater(temporary['pedestrian_brakes'], 0)
        self.assertGreater(temporary['resumes_after_pedestrian'], 0)
        self.assertEqual(temporary['collision_pairs'], [])
        self.assertEqual(permanent['completed_robots'], [])
        self.assertEqual(permanent['collision_pairs'], [])
        self.assertEqual(permanent['termination'], 'horizon')
        self.assertEqual(permanent['reservation_owner'], 'A')

    def test_always_stop_is_safe_but_not_successful(self):
        result = run_episode(always_stop=True, horizon=5)
        self.assertEqual(result['collision_pairs'], [])
        self.assertEqual(result['completed_robots'], [])
        self.assertFalse(result['safe_and_complete'])

    def test_omitting_reaction_loses_required_margin_from_same_initial_state(self):
        good, bad = run_stopping_witness(), run_stopping_witness(omit_reaction=True)
        self.assertEqual(good['initial_state'], bad['initial_state'])
        self.assertFalse(good['margin_violation'])
        self.assertTrue(bad['margin_violation'])
        self.assertGreater(good['halted_time'], good['brake_delivery'])
        self.assertAlmostEqual(good['halted_time'] - good['brake_delivery'], 1.25, places=6)

    def test_release_mutation_is_visible_to_independent_geometry(self):
        result = geometry_witness()
        self.assertTrue(result['front_only_clear'])
        self.assertFalse(result['whole_body_clear'])
        self.assertTrue(result['actual_body_intersects_Z'])

    def test_physical_completion_rejects_done_at_wrong_goal_or_in_motion(self):
        self.assertTrue(hasattr(simulation, 'score_completion'),
                        'independent physical completion scorer is missing')
        score = simulation.score_completion(
            {'A', 'B', 'C'},
            {'A': ((0, 0, 0), 0), 'B': ((2, 0, 0), 1),
             'C': ((3, 0, 0), 0)},
            {'A': (1, 0), 'B': (2, 0), 'C': (3, 0)})
        self.assertEqual(score['completed_robots'], ['C'])
        self.assertEqual({entry['robot'] for entry in score['completion_mismatches']}, {'A', 'B'})

    def test_goal_completion_waits_for_fresh_observation_after_blackout(self):
        result = run_episode(sensor_blackout=(29.9, 40.), horizon=32.)
        self.assertNotIn('A', result['completed_robots'])
        self.assertNotIn('A', result['completion_times'])
        self.assertFalse(any(e['kind'] == 'complete' and e['robot'] == 'A'
                             for e in result['events']))

    def test_lost_observations_stop_owner_without_regranting_occupied_zone(self):
        result = run_episode(sensor_blackout=(10., 15.), horizon=16.)
        self.assertTrue(any(e['kind'] == 'command_issued' and e['reason'] == 'observation_unusable'
                            and e['time'] > 10 for e in result['events']))
        self.assertEqual(result['grant_order'], ['A'])
        self.assertEqual(result['reservation_owner'], 'A')
        self.assertEqual(result['early_releases'], [])
        self.assertEqual(result['collision_pairs'], [])

if __name__ == '__main__':
    unittest.main()
