"""Behavioral boundaries for the progress evidence tooling."""
import math
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
try:
    import profiles
except ImportError:
    profiles = None


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(profiles, 'progress profile tooling has not been implemented')

    def test_triangular_profile_and_rest_to_rest_distance(self):
        row = profiles.segment(0.1, 1., .5, .8)
        self.assertEqual(row['cruise_distance'], 0.)
        self.assertLess(row['peak'], 1.)
        self.assertAlmostEqual(row['integrated_distance'], .1)
        self.assertLessEqual(row['duration'], row['upper_bound'])

    def test_cruising_and_threshold_profiles(self):
        for length in (1.625, 4.):
            row = profiles.segment(length, 1., .5, .8)
            self.assertAlmostEqual(row['peak'], 1.)
            self.assertAlmostEqual(row['duration'], length + 1.625)
            self.assertAlmostEqual(row['integrated_distance'], length)

    def test_upper_bounds_alone_are_not_accepted_as_positive_dynamics(self):
        for values in ((1,1,0,.8), (1,0,.5,.8), (1,1,.5,0), (0,1,.5,.8),
                       (1,1,float('nan'),.8), (1,1,.5,float('inf'))):
            with self.assertRaises(ValueError):
                profiles.segment(*values)

    def test_turns_are_timed_and_repeated_vertices_rejected(self):
        row = profiles.route([(0,0),(4,0),(4,4)], 1., .5, .8, math.pi/2)
        self.assertAlmostEqual(row['turn_time'], 1.)
        self.assertAlmostEqual(row['duration'], 12.25)
        with self.assertRaises(ValueError):
            profiles.route([(0,0),(0,0)], 1., .5, .8, math.pi/2)

    def test_nominal_plant_moves_but_upper_bound_countermodel_stays(self):
        sys.path.insert(0, str(BASE.parent/'amr-corridor'))
        from plant import RobotPlant
        nominal = RobotPlant([(0,0),(4,0)])
        stationary = profiles.StationaryPlant([(0,0),(4,0)])
        nominal.advance(1., 'Proceed')
        stationary.advance(1., 'Proceed')
        self.assertGreater(nominal.pose[0], 0.)
        self.assertEqual(stationary.pose, (0.,0.,0.))
        self.assertEqual(stationary.speed, 0.)
        self.assertFalse(stationary.finished)


if __name__ == '__main__':
    unittest.main()
