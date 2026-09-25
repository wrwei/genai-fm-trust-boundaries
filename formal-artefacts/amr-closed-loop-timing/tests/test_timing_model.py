import pathlib
import sys
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
try:
    import timing_model
except ImportError:
    timing_model = None


class TimingModelTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(timing_model, 'timing_model has not been implemented')

    def test_next_control_keeps_on_grid_event_and_rounds_other_residues_up(self):
        self.assertEqual([timing_model.next_control(t) for t in range(7)],
                         [0, 5, 5, 5, 5, 5, 10])

    def test_observation_and_release_include_sampling_and_delivery(self):
        expected = [5, 10, 10, 10, 10]
        self.assertEqual([timing_model.observation_visible(t) for t in range(5)], expected)
        self.assertEqual([timing_model.release_from_clear(t) for t in range(5)], expected)
        self.assertEqual(max(expected[t]-t for t in range(5)), 9)

    def test_waiting_start_includes_next_control_and_command_delivery(self):
        self.assertEqual(timing_model.start_from_grant(5, 0, 'Waiting'), 20)
        self.assertEqual(timing_model.start_from_grant(150, 0, 'Waiting'), 165)

    def test_brake_requested_start_waits_for_halt_threshold(self):
        self.assertEqual(timing_model.start_from_grant(5, 0, 'BrakeRequested'), 160)
        self.assertEqual(timing_model.start_from_grant(10, 10, 'BrakeRequested'), 170)
        self.assertLessEqual(timing_model.start_from_grant(5, 0, 'BrakeRequested')-5, 163)

    def test_finish_includes_observation_command_and_halt_timer(self):
        expected = [165, 170, 170, 170, 170]
        self.assertEqual([timing_model.finish_from_arrival(t) for t in range(5)], expected)
        self.assertEqual(max(expected[t]-t for t in range(5)), 169)

    def test_two_task_bound_contains_both_complete_task_chains(self):
        self.assertEqual(timing_model.two_task_bound(), 6884)
        self.assertEqual(timing_model.two_task_bound()/100, 68.84)

    def test_invalid_ticks_modes_and_temporal_order_are_rejected(self):
        for value in (-1, 1.5, True, float('nan')):
            with self.assertRaises((TypeError, ValueError)):
                timing_model.next_control(value)
        with self.assertRaises(ValueError):
            timing_model.start_from_grant(6, 0, 'Waiting')
        with self.assertRaises(ValueError):
            timing_model.start_from_grant(5, 6, 'BrakeRequested')
        with self.assertRaises(ValueError):
            timing_model.start_from_grant(5, 0, 'Idle')


if __name__ == '__main__':
    unittest.main()
