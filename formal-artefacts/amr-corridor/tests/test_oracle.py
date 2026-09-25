"""Analytic fixtures independent of the oracle implementation."""
import importlib.util
import math
from pathlib import Path
import unittest


class OracleTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "oracle.py"
        self.assertTrue(path.exists(), "Independent collision oracle has not been implemented")
        spec = importlib.util.spec_from_file_location("independent_oracle", path)
        self.oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.oracle)

    def sweep(self, a, b, **kwargs):
        args = dict(length_a=.2, width_a=.2, length_b=.2, width_b=.2,
                    duration=1., speed_bound_a=0., speed_bound_b=0.)
        args.update(kwargs)
        return self.oracle.sweep_check(a, b, **args)

    def test_rectangle_rotation(self):
        points = self.oracle.rectangle((2., 3., math.pi / 2), 4., 2.)
        for actual, expected in zip(points, [(3, 1), (3, 5), (1, 5), (1, 1)]):
            for x, y in zip(actual, expected):
                self.assertAlmostEqual(x, y)

    def test_polygon_analytic_distances_overlap_and_contact(self):
        a = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for b, expected in [([(4, 5), (5, 5), (5, 6), (4, 6)], 5.),
                            ([(1, 0), (2, 0), (2, 1), (1, 1)], 0.),
                            ([(.2, .2), (.3, .2), (.3, .3), (.2, .3)], 0.)]:
            self.assertAlmostEqual(self.oracle.polygon_distance(a, b), expected)
            self.assertAlmostEqual(self.oracle.polygon_distance(b, a), expected)

    def test_frame_endpoints_clear_but_midpoint_crosses(self):
        result = self.sweep(lambda t: (-1 + 2*t, 0, 0), lambda t: (0, 0, 0),
                            speed_bound_a=2)
        self.assertEqual(result['status'], 'collision')
        self.assertEqual(result['witness_time'], .5)
        self.assertEqual(result['distance_lower_bound'], 0)

    def test_rotation_sweep_hits_between_clear_endpoints(self):
        result = self.sweep(lambda t: (0, 0, math.pi*t), lambda t: (0, .8, 0),
                            length_a=2, width_a=.1,
                            speed_bound_a=math.pi*math.hypot(1, .05))
        self.assertEqual(result['status'], 'collision')
        self.assertEqual(result['witness_time'], .5)

    def test_static_clear_has_conservative_distance(self):
        result = self.sweep(lambda t: (0, 0, 0), lambda t: (2, 0, 0))
        self.assertEqual(result['status'], 'clear')
        self.assertIsNone(result['witness_time'])
        self.assertGreater(result['distance_lower_bound'], 1.79)
        self.assertLessEqual(result['distance_lower_bound'], 1.8)

    def test_exact_contact_and_zero_duration(self):
        result = self.sweep(lambda t: (0, 0, 0), lambda t: (.2, 0, 0), duration=0)
        self.assertEqual(result['status'], 'collision')
        self.assertEqual(result['witness_time'], 0)

    def test_subdivision_finds_off_midpoint_collision(self):
        result = self.sweep(lambda t: (-.5+2*t, 0, 0), lambda t: (0, 0, 0),
                            speed_bound_a=2)
        self.assertEqual(result['status'], 'collision')
        self.assertAlmostEqual(result['witness_time'], .25)

    def test_unresolved_budget_never_reports_clear(self):
        result = self.sweep(lambda t: (0, 0, 0), lambda t: (1, 0, 0),
                            speed_bound_a=100, max_depth=0)
        self.assertEqual(result['status'], 'unresolved')
        self.assertIsNone(result['witness_time'])
        self.assertEqual(result['distance_lower_bound'], 0)

    def test_invalid_inputs_are_rejected(self):
        for kwargs in [dict(duration=-1), dict(speed_bound_a=-1),
                       dict(speed_bound_b=float('nan')), dict(duration=float('inf')),
                       dict(length_a=0), dict(width_b=-1), dict(epsilon=-1),
                       dict(max_depth=-1), dict(max_intervals=0)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.sweep(lambda t: (0, 0, 0), lambda t: (1, 0, 0), **kwargs)
        with self.assertRaises(ValueError):
            self.sweep(lambda t: (float('nan'), 0, 0), lambda t: (1, 0, 0))
        with self.assertRaises(ValueError):
            self.oracle.polygon_distance([(0, 0)], [(0, 0), (1, 0), (0, 1)])


if __name__ == '__main__':
    unittest.main()
