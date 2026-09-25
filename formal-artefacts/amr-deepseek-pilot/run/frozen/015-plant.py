"""Analytic fixed-route reference plant, independent of supervision and scoring.

SI units. Vertices require rest before bounded, finite-duration rotation.
Angular inertia is omitted: delivered Brake freezes rotation immediately.
"""
from collections import deque
from dataclasses import asdict, dataclass
from math import atan2, cos, hypot, isfinite, pi, sin, sqrt


@dataclass(frozen=True)
class MotionPiece:
    duration: float
    start_pose: tuple
    initial_speed: float
    acceleration: float
    angular_velocity: float
    point_speed_bound: float

    def sample(self, relative_t):
        if not isfinite(relative_t) or relative_t < -1e-12 or relative_t > self.duration + 1e-12:
            raise ValueError('sample time outside motion interval')
        t = min(self.duration, max(0.0, relative_t))
        x, y, theta = self.start_pose
        distance = self.initial_speed * t + self.acceleration * t * t / 2
        return (x + cos(theta) * distance, y + sin(theta) * distance,
                theta + self.angular_velocity * t)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        return cls(**{**value, 'start_pose': tuple(value['start_pose'])})


class RobotPlant:
    def __init__(self, route, length=.8, width=.6, speed_limit=1.0,
                 accel=.5, brake=.8, turn_rate=pi / 2, *, initial_speed=0.0):
        for v in (length, width, speed_limit, accel, brake, turn_rate):
            if not isfinite(v) or v <= 0:
                raise ValueError('physical parameters must be positive and finite')
        self.route = tuple(tuple(map(float, p)) for p in route)
        if len(self.route) < 2 or any(len(p) != 2 or not all(map(isfinite, p)) for p in self.route):
            raise ValueError('route requires at least two finite xy vertices')
        if any(a == b for a, b in zip(self.route, self.route[1:])):
            raise ValueError('consecutive vertices must differ')
        if not isfinite(initial_speed) or not 0 <= initial_speed <= speed_limit:
            raise ValueError('initial speed must lie within speed limits')
        x, y = self.route[0]
        dx, dy = self.route[1][0] - x, self.route[1][1] - y
        if initial_speed * initial_speed > 2 * brake * hypot(dx, dy) + 1e-12:
            raise ValueError('initial speed cannot stop by first waypoint')
        self.length, self.width = length, width
        self.speed_limit, self.accel, self.brake, self.turn_rate = speed_limit, accel, brake, turn_rate
        self._pose, self._speed = (x, y, atan2(dy, dx)), initial_speed
        self._waypoint = 1
        self._phases = deque()
        self._intent = None

    @property
    def pose(self):
        return self._pose

    @property
    def speed(self):
        return self._speed

    @property
    def finished(self):
        return self._waypoint >= len(self.route) and self._speed == 0

    def _plan(self, intent):
        if intent == 'Brake':
            if self._speed > 0:
                self._phases.append([self._speed / self.brake, -self.brake, 0.0, 'halt'])
            return
        if self.finished:
            return
        x, y, theta = self._pose
        tx, ty = self.route[self._waypoint]
        distance = hypot(tx - x, ty - y)
        if distance < 1e-10 and self._speed == 0:
            self._waypoint += 1
            self._plan(intent)
            return
        angle = (atan2(ty - y, tx - x) - theta + pi) % (2 * pi) - pi
        if abs(angle) > 1e-10:
            if self._speed > 1e-10:
                raise RuntimeError('cannot rotate while translating')
            self._phases.append([abs(angle) / self.turn_rate, 0.0,
                                 self.turn_rate if angle > 0 else -self.turn_rate, 'turn'])
            return
        # Integrate dv/dt=a then dv/dt=-b; solve the distance equation
        # for peak velocity, optionally inserting a constant-speed interval.
        v, a, b = self._speed, self.accel, self.brake
        peak = min(self.speed_limit, sqrt((2 * a * b * distance + b * v * v) / (a + b)))
        if peak < v - 1e-9:
            raise RuntimeError('unreachable waypoint without overtravel')
        peak = max(v, peak)
        up = (peak - v) / a
        cruise_distance = distance - (peak * peak - v * v) / (2 * a) - peak * peak / (2 * b)
        if up > 0:
            self._phases.append([up, a, 0.0, 'phase'])
        if cruise_distance > 1e-12:
            self._phases.append([cruise_distance / peak, 0.0, 0.0, 'phase'])
        self._phases.append([peak / b, -b, 0.0, 'arrive'])

    def advance(self, dt, intent='Proceed'):
        """Apply an already delivered command for dt and return its exact pieces."""
        if not isfinite(dt) or dt < 0 or intent not in ('Proceed', 'Brake'):
            raise ValueError('expected finite nonnegative dt and Proceed or Brake')
        if intent != self._intent:
            self._phases.clear()
            self._intent = intent
        pieces = []
        remaining = dt
        while remaining > 0:
            if not self._phases:
                self._plan(intent)
            if not self._phases:
                pieces.append(MotionPiece(remaining, self.pose, 0.0, 0.0, 0.0, 0.0))
                break
            phase = self._phases[0]
            duration, acceleration, omega, event = phase
            step = min(remaining, duration)
            end_speed = self.speed + acceleration * step
            bound = max(self.speed, end_speed) + abs(omega) * hypot(self.length, self.width) / 2
            piece = MotionPiece(step, self.pose, self.speed, acceleration, omega, bound)
            pieces.append(piece)
            self._pose = piece.sample(step)
            self._speed = end_speed
            remaining -= step
            if step == duration:
                self._phases.popleft()
                if event in ('halt', 'arrive'):
                    # Exact analytic zero-speed event; no position projection.
                    self._speed = 0.0
                if event == 'arrive':
                    self._waypoint += 1
            else:
                phase[0] -= step
        return pieces
