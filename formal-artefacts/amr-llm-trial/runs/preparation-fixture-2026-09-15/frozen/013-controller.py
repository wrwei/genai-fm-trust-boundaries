"""Handwritten reference decisions. This module never reads the plant or oracle."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Observation:
    robot_id: str
    sample_time: float
    pose: tuple
    speed: float
    blocked: bool
    mission_revision: int
    map_revision: int


@dataclass(frozen=True)
class Command:
    robot_id: str
    seq: int
    intent: str
    mission_revision: int
    map_revision: int
    issued: float
    delivery: float
    expiry: float


def usable(obs, robot_id, now, params):
    return (obs is not None and obs.robot_id == robot_id
            and obs.mission_revision == 1 and obs.map_revision == 1
            and all(math.isfinite(x) for x in (*obs.pose, obs.speed, obs.sample_time, now))
            and 0 <= now - obs.sample_time <= params['timing']['accepted_observation_age_upper_bound'] + 1e-9)


def braking_distance(speed, age, params, omit_reaction=False):
    """Proposed sufficient bound, evaluated at observation-time front bumper."""
    if not math.isfinite(speed) or not math.isfinite(age) or age < 0:
        raise ValueError('Finite speed and nonnegative observation age required')
    r, t = params['robot'], params['timing']
    upper = max(0, speed + r['speed_error_bound'])
    delay = 0 if omit_reaction else (age + t['safety_monitor_period'] +
                                   t['monitor_compute_upper_bound'] + t['brake_delivery_and_onset_upper_bound'])
    a, b = r['forward_acceleration_upper_bound'], r['braking_deceleration_lower_bound']
    return upper * delay + .5 * a * delay ** 2 + (upper + a * delay) ** 2 / (2 * b) + r['position_error_bound'] + r['clearance_margin']


def body_clear(obs, robot_id, now, params, front_only=False):
    if not usable(obs, robot_id, now, params):
        return False
    r = params['robot']
    x, _, theta = obs.pose
    extent = abs(math.cos(theta)) * r['length'] / 2 + abs(math.sin(theta)) * r['width'] / 2
    left, right, _, _ = params['map']['reservation_zone_Z']
    if front_only:
        # Deliberate geometric mutation. This is not a safety feature.
        return x + extent > right if robot_id == 'A' else x - extent < left
    buffer = r['position_error_bound'] + r['clearance_margin']
    return x - extent > right + buffer if robot_id == 'A' else x + extent < left - buffer


class Reservation:
    """No timeout release: a missing heartbeat cannot establish clearance."""
    def __init__(self):
        self.owner = None
        self.mission_id = None
        self.serial = 0

    def acquire(self, robot_id, mission_id):
        if self.owner is not None:
            return False
        self.owner, self.mission_id = robot_id, mission_id
        self.serial += 1
        return True

    def release(self, robot_id, mission_id, clear):
        if not clear or (self.owner, self.mission_id) != (robot_id, mission_id):
            return False
        self.owner = self.mission_id = None
        return True


class Actuator:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.intent = 'Brake'
        self.sequence = -1
        self.brake_since = 0.0

    def accept(self, command, now):
        if command.robot_id != self.robot_id:
            return 'wrong_robot'
        if command.intent not in ('Proceed', 'Brake'):
            return 'bad_intent'
        if (command.mission_revision, command.map_revision) != (1, 1):
            return 'wrong_revision'
        if now < command.delivery - 1e-9:
            return 'not_delivered'
        if now > command.expiry + 1e-9:
            return 'expired'
        if command.seq <= self.sequence:
            return 'old_sequence'
        self.sequence = command.seq
        if command.intent == 'Brake' and self.intent != 'Brake':
            self.brake_since = now
        self.intent = command.intent
        return 'accepted'


def reference_decision(obs, robot_id, now, params, permitted, goal, always_stop=False):
    if not usable(obs, robot_id, now, params):
        return 'Brake', 'observation_unusable'
    if always_stop:
        return 'Brake', 'always_stop_reference'
    if obs.blocked:
        return 'Brake', 'pedestrian_blocked'
    if not permitted:
        return 'Brake', 'waiting_for_reservation'
    if math.dist(obs.pose[:2], goal) <= .01:
        return 'Brake', 'at_goal'
    return 'Proceed', 'current_permission'
