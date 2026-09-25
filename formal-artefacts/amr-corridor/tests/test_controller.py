"""Independent numeric and protocol fixtures for the reference controller."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from controller import Observation, Command, Actuator, Reservation, braking_distance, body_clear

PARAMS = json.loads((Path(__file__).resolve().parents[3] / 'literature/scholar_search_2026-09-10/followup/research_amr_parameters_2026-09-15.json').read_text(encoding='utf-8'))

def observation(x, y=-2, robot='A', time=1, theta=0, speed=0):
    return Observation(robot, time, (x, y, theta), speed, False, 1, 1)

class ControllerTests(unittest.TestCase):
    def test_stopping_bound_includes_old_observation_and_delivery(self):
        self.assertAlmostEqual(braking_distance(1.0, .1, PARAMS), 1.391015625)
        self.assertGreater(braking_distance(1.0, .1, PARAMS), braking_distance(1.0, 0, PARAMS))

    def test_front_out_does_not_release_tail(self):
        obs = observation(18.1)
        self.assertTrue(body_clear(obs, 'A', 1, PARAMS, front_only=True))
        self.assertFalse(body_clear(obs, 'A', 1, PARAMS))
        self.assertTrue(body_clear(observation(18.7), 'A', 1, PARAMS))

    def test_wrong_object_stale_or_wrong_exit_does_not_clear(self):
        for obs in [observation(20, robot='B'), observation(20, time=0), observation(4)]:
            self.assertFalse(body_clear(obs, 'A', 1, PARAMS))

    def test_timeout_cannot_reassign_occupied_reservation(self):
        r = Reservation()
        self.assertTrue(r.acquire('A', 'mission-A'))
        self.assertFalse(r.acquire('B', 'mission-B'))
        self.assertFalse(r.release('A', 'mission-A', False))
        self.assertEqual(r.owner, 'A')
        self.assertFalse(r.release('A', 'wrong-mission', True))
        self.assertTrue(r.release('A', 'mission-A', True))
        self.assertTrue(r.acquire('B', 'mission-B'))

    def test_late_old_proceed_cannot_overwrite_new_brake(self):
        a = Actuator('A')
        brake = Command('A', 2, 'Brake', 1, 1, 0, .1, 1)
        old = Command('A', 1, 'Proceed', 1, 1, 0, .2, 1)
        self.assertEqual(a.accept(brake, .1), 'accepted')
        self.assertEqual(a.accept(old, .2), 'old_sequence')
        self.assertEqual(a.intent, 'Brake')

    def test_expired_wrong_robot_and_old_revision_cannot_execute(self):
        a = Actuator('A')
        cases = [
            (Command('B', 1, 'Proceed', 1, 1, 0, .1, 1), .1, 'wrong_robot'),
            (Command('A', 1, 'Proceed', 1, 1, 0, .1, .2), .3, 'expired'),
            (Command('A', 1, 'Proceed', 0, 1, 0, .1, 1), .1, 'wrong_revision'),
        ]
        for command, now, reason in cases:
            self.assertEqual(a.accept(command, now), reason)
            self.assertEqual(a.intent, 'Brake')

if __name__ == '__main__':
    unittest.main()
