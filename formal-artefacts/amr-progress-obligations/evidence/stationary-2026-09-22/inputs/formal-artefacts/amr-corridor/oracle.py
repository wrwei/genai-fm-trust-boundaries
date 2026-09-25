"""Independent convex geometry and conservative continuous rectangle checks.

No controller or plant dependencies. Bounds supplied to sweep_check must bound
the speed of EVERY body point (including rotation), throughout the interval.
Floating point arithmetic and a fixed tolerance are not a formal proof.
"""
import math


def _finite(value, name, minimum=None, strict=False):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + ' must be finite') from exc
    if not math.isfinite(value) or (minimum is not None and
            (value < minimum or (strict and value == minimum))):
        raise ValueError(name + ' is outside its valid range')
    return value


def rectangle(pose, length, width):
    """Return four counterclockwise vertices for (x, y, theta), in metres/radians."""
    if len(pose) != 3:
        raise ValueError('pose must contain x, y, theta')
    x, y, theta = (_finite(v, 'pose') for v in pose)
    length = _finite(length, 'length', 0, True)
    width = _finite(width, 'width', 0, True)
    c, s = math.cos(theta), math.sin(theta)
    points = tuple((x + c*u - s*v, y + s*u + c*v)
                   for u, v in ((-length/2, -width/2), (length/2, -width/2),
                                (length/2, width/2), (-length/2, width/2)))
    if not all(math.isfinite(v) for p in points for v in p):
        raise ValueError('rectangle arithmetic overflow')
    return points


def _polygon(points):
    points = tuple(tuple(_finite(v, 'vertex') for v in p) for p in points)
    if len(points) < 3 or any(len(p) != 2 for p in points):
        raise ValueError('polygon needs at least three 2D vertices')
    return points


def _edges(points):
    return zip(points, points[1:] + points[:1])


def _point_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    norm = math.hypot(dx, dy)
    if norm == 0:
        return math.hypot(p[0]-a[0], p[1]-a[1])
    ux, uy = dx/norm, dy/norm
    along = max(0., min(norm, (p[0]-a[0])*ux + (p[1]-a[1])*uy))
    return math.hypot(p[0]-a[0]-along*ux, p[1]-a[1]-along*uy)


def polygon_distance(a, b):
    """Euclidean distance between filled convex polygons; touching gives zero.

    Vertices must be ordered around nondegenerate convex polygons. Either
    orientation is accepted. Concave or self-intersecting input is unsupported.
    """
    a, b = _polygon(a), _polygon(b)
    separated = False
    for polygon in (a, b):
        for p, q in _edges(polygon):
            dx, dy = q[0]-p[0], q[1]-p[1]
            norm = math.hypot(dx, dy)
            if norm == 0:
                continue
            nx, ny = -dy/norm, dx/norm
            pa = [x*nx + y*ny for x, y in a]
            pb = [x*nx + y*ny for x, y in b]
            if not all(math.isfinite(v) for v in pa + pb):
                raise ValueError('polygon arithmetic overflow')
            if max(pa) < min(pb) or max(pb) < min(pa):
                separated = True
                break
        if separated:
            break
    if not separated:
        return 0.
    distance = min(_point_segment(p, u, v)
                   for vertices, segments in ((a, b), (b, a))
                   for p in vertices for u, v in _edges(segments))
    if not math.isfinite(distance):
        raise ValueError('distance arithmetic overflow')
    return distance


def sweep_check(pose_a, pose_b, length_a, width_a, length_b, width_b,
                duration, speed_bound_a, speed_bound_b, *, epsilon=1e-9,
                max_depth=24, max_intervals=100000):
    """Check continuous motion at relative times in [0, duration].

    A sampled distance <= epsilon is a numerical collision witness (not
    necessarily the first contact). A midpoint distance minus epsilon and the
    relative point-speed bound times half the interval certifies separation.
    Exhausted budgets return unresolved, never clear. distance_lower_bound is
    a bound over the ENTIRE interval; unresolved/collision return zero.
    Trusted continuous callbacks and valid point-speed bounds are preconditions.
    """
    duration = _finite(duration, 'duration', 0)
    va = _finite(speed_bound_a, 'speed_bound_a', 0)
    vb = _finite(speed_bound_b, 'speed_bound_b', 0)
    relative_speed = _finite(va + vb, 'combined speed', 0)
    epsilon = _finite(epsilon, 'epsilon', 0)
    for name, value, minimum in [('max_depth', max_depth, 0),
                                  ('max_intervals', max_intervals, 1)]:
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(name + ' must be an integer within range')
    for name, value in [('length_a', length_a), ('width_a', width_a),
                        ('length_b', length_b), ('width_b', width_b)]:
        _finite(value, name, 0, True)

    def distance(t):
        return polygon_distance(rectangle(pose_a(t), length_a, width_a),
                                rectangle(pose_b(t), length_b, width_b))

    def result(status, witness=None, bound=0.):
        return dict(status=status, witness_time=witness, distance_lower_bound=bound)

    for t in (0., duration):
        d = distance(t)
        if d <= epsilon:
            return result('collision', t)
    if duration == 0:
        return result('clear', bound=max(0., d-epsilon))

    pending = [(0., duration, 0)]
    lower_bound = math.inf
    unresolved = False
    visited = 0
    while pending:
        if visited >= max_intervals:
            return result('unresolved')
        lo, hi, depth = pending.pop()
        visited += 1
        mid = lo + (hi-lo)/2
        d = distance(mid)
        if d <= epsilon:
            return result('collision', mid)
        bound = d - epsilon - relative_speed * ((hi-lo)/2)
        if bound > 0:
            lower_bound = min(lower_bound, bound)
        elif depth >= max_depth or mid == lo or mid == hi:
            unresolved = True
        else:
            pending.append((mid, hi, depth+1))
            pending.append((lo, mid, depth+1))
    return result('unresolved') if unresolved else result('clear', bound=lower_bound)
