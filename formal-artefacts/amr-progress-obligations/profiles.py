"""Independent analytic profiles; exact progressing dynamics, not upper bounds alone."""
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'amr-corridor'))
from plant import RobotPlant


def positive(*values):
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('positive finite exact dynamics and segment length required')


def segment(length, speed, accel, brake):
    positive(length, speed, accel, brake)
    k = 1/(2*accel) + 1/(2*brake)
    peak = min(speed, math.sqrt(length/k))
    cruise = max(0., length-k*peak*peak) if peak == speed else 0.
    up, down = peak/accel, peak/brake
    cruise_time = cruise/peak
    duration = up + cruise_time + down
    return dict(length=length, speed=speed, accel=accel, brake=brake, k=k, peak=peak,
                cruise_distance=cruise, up_time=up, cruise_time=cruise_time,
                down_time=down, duration=duration, upper_bound=length/speed+k*speed,
                integrated_distance=.5*accel*up*up + peak*cruise_time + .5*brake*down*down)


def route(points, speed, accel, brake, turn_rate):
    positive(speed, accel, brake, turn_rate)
    if (len(points) < 2 or any(len(p) != 2 or not all(math.isfinite(x) for x in p) for p in points)
            or any(tuple(p) == tuple(q) for p,q in zip(points, points[1:]))):
        raise ValueError('a finite route needs at least two vertices and positive segments')
    headings = [math.atan2(q[1]-p[1], q[0]-p[0]) for p,q in zip(points, points[1:])]
    turns = [abs((q-p+math.pi) % (2*math.pi)-math.pi)/turn_rate for p,q in zip(headings, headings[1:])]
    segments = [segment(math.dist(p,q), speed, accel, brake) for p,q in zip(points, points[1:])]
    return dict(route=points, segments=segments, turns=turns, turn_time=sum(turns),
                duration=sum(s['duration'] for s in segments)+sum(turns),
                upper_bound=sum(s['upper_bound'] for s in segments)+sum(turns),
                total_length=sum(s['length'] for s in segments))


class StationaryPlant(RobotPlant):
    """Constructed plant: Proceed has no effect. Not the reference dynamics.

    Starting at rest gives acceleration and speed identically zero, within the
    stated upper bounds. Brake retains the reference implementation. The fixture
    uses only the normal zero-speed initial state.
    """
    def _plan(self, intent):
        if intent == 'Brake':
            super()._plan(intent)
