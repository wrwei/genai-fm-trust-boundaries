import math
import unittest
try:
    from plant import RobotPlant, MotionPiece
except ImportError:
    RobotPlant = MotionPiece = None


class PlantTests(unittest.TestCase):
    def make(self, *args, **kwargs):
        self.assertIsNotNone(RobotPlant, 'timed plant is not implemented')
        return RobotPlant(*args, **kwargs)

    def test_analytic_braking_and_hold(self):
        p = self.make([(0, 0), (10, 0)], initial_speed=1)
        pieces = p.advance(2, 'Brake')
        self.assertAlmostEqual(pieces[0].duration, 1.25)
        self.assertAlmostEqual(pieces[0].sample(1.25)[0], .625)
        self.assertAlmostEqual(p.pose[0], .625)
        self.assertEqual(p.speed, 0)
        p.advance(5, 'Brake')
        self.assertAlmostEqual(p.pose[0], .625)

    def test_turn_has_duration_and_zero_translation(self):
        p = self.make([(0, 0), (1, 0), (1, 1)])
        pieces = p.advance(20)
        turns = [q for q in pieces if abs(q.angular_velocity) > 0]
        self.assertEqual(len(turns), 1)
        q = turns[0]
        self.assertAlmostEqual(q.duration, 1)
        self.assertAlmostEqual(q.sample(.5)[2], math.pi / 4)
        self.assertAlmostEqual(q.sample(.5)[0], 1)
        self.assertAlmostEqual(q.sample(.5)[1], 0)
        self.assertAlmostEqual(q.initial_speed, 0)
        self.assertTrue(p.finished)
        self.assertAlmostEqual(p.pose[1], 1)
        self.assertEqual(p.speed, 0)

    def test_dt_partition_independence(self):
        route = [(0, 0), (1, 0), (1, 3), (-2, 3)]
        a, b = self.make(route), self.make(route)
        for duration, intent in [(1.1, 'Proceed'), (.7, 'Brake'), (5.13, 'Proceed'), (.2, 'Brake'), (20, 'Proceed')]:
            a.advance(duration, intent)
            for _ in range(100):
                b.advance(duration / 100, intent)
            for x, y in zip(a.pose, b.pose):
                self.assertAlmostEqual(x, y, places=9)
            self.assertAlmostEqual(a.speed, b.speed, places=9)
        self.assertTrue(a.finished and b.finished)

    def test_brake_resume_and_rotation_freeze(self):
        p = self.make([(0, 0), (10, 0), (10, 10)])
        p.advance(1)
        p.advance(2, 'Brake')
        self.assertEqual(p.speed, 0)
        self.assertFalse(p.finished)
        parts = p.advance(20)
        turning = next(q for q in parts if q.angular_velocity)
        # Independently locate half of the turn from the same initial state.
        p = self.make([(0, 0), (1, 0), (1, 1)])
        full = p.advance(20)
        t = 0
        for q in full:
            if q.angular_velocity:
                t += q.duration / 2
                break
            t += q.duration
        p = self.make([(0, 0), (1, 0), (1, 1)])
        p.advance(t)
        before = p.pose
        p.advance(3, 'Brake')
        self.assertEqual(p.pose, before)
        p.advance(20)
        self.assertTrue(p.finished)

    def test_serialized_pieces_continuity_and_bounds(self):
        p = self.make([(0, 0), (2, 0), (2, 1)])
        pieces = p.advance(10)
        self.assertAlmostEqual(sum(q.duration for q in pieces), 10)
        last = (0, 0, 0)
        for q in pieces:
            restored = MotionPiece.from_dict(q.to_dict())
            for x, y in zip(last, q.sample(0)):
                self.assertAlmostEqual(x, y)
            self.assertEqual(q.sample(q.duration / 2), restored.sample(q.duration / 2))
            for t in (0, q.duration):
                v = abs(q.initial_speed + q.acceleration * t)
                self.assertGreaterEqual(q.point_speed_bound + 1e-12, v + abs(q.angular_velocity) * .5)
            last = q.sample(q.duration)

    def test_invalid_inputs(self):
        for kwargs in ({'brake': 0}, {'initial_speed': -1}, {'speed_limit': float('nan')}):
            with self.assertRaises(ValueError):
                self.make([(0, 0), (10, 0)], **kwargs)
        with self.assertRaises(ValueError):
            self.make([(0, 0), (.1, 0)], initial_speed=1)
        p = self.make([(0, 0), (1, 0)])
        with self.assertRaises(ValueError):
            p.advance(-1)
        with self.assertRaises(ValueError):
            p.advance(1, 'Teleport')


if __name__ == '__main__':
    unittest.main()
