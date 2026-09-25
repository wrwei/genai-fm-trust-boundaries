"""Independent milestone extraction from retained stable physical traces."""
import math

START_BOUND = 163
TRAVEL_BOUND = 3100
RELEASE_BOUND = 9
FINISH_BOUND = 169
HALT_THRESHOLD = 149
TOL = 1e-6


def pose(piece, relative):
    x, y, heading = piece['start_pose']
    distance = piece['initial_speed']*relative + piece['acceleration']*relative*relative/2
    return (x+math.cos(heading)*distance, y+math.sin(heading)*distance,
            heading+piece['angular_velocity']*relative)


def clear_metric(value, robot, params):
    x, _, heading = value
    robot_p, zone = params['robot'], params['map']['reservation_zone_Z']
    extent = abs(math.cos(heading))*robot_p['length']/2 + abs(math.sin(heading))*robot_p['width']/2
    buffer = robot_p['position_error_bound']+robot_p['clearance_margin']
    return x-extent-(zone[1]+buffer) if robot == 'A' else zone[0]-buffer-(x+extent)


def physical_milestones(rows, params, robot):
    crossing = arrival = None
    goal = tuple(params['map']['route_'+robot][-1])
    for row in rows:
        if row['kind'] != 'motion':
            continue
        offset = 0.
        for piece in row['robots'][robot]:
            duration = piece['duration']
            lo_metric = clear_metric(pose(piece, 0.), robot, params)
            hi_metric = clear_metric(pose(piece, duration), robot, params)
            if crossing is None and (lo_metric > 0 or hi_metric > 0):
                if lo_metric > 0:
                    boundary = 0.
                else:
                    lo, hi = 0., duration
                    for _ in range(80):
                        mid = (lo+hi)/2
                        if clear_metric(pose(piece, mid), robot, params) > 0:
                            hi = mid
                        else:
                            lo = mid
                    boundary = hi
                crossing = row['time']+offset+boundary
            end = pose(piece, duration)
            end_speed = piece['initial_speed']+piece['acceleration']*duration
            if arrival is None and math.dist(end[:2], goal) <= 1e-8 and abs(end_speed) <= 1e-8:
                arrival = row['time']+offset+duration
            offset += duration
    assert crossing is not None, ('missing physical clearance', robot)
    assert arrival is not None, ('missing physical arrival', robot)
    return crossing, arrival


def audit_rows(rows, params):
    grants, grant_order = {}, []
    starts, releases, brakes, finishes = {}, {}, {}, {}
    for row in rows:
        kind = row['kind']
        if kind == 'protocol':
            for event in row['events']:
                if event[0] == 'Grant':
                    assert event[1] not in grants, ('duplicate grant', event[1])
                    grants[event[1]] = row['time']
                    grant_order.append(event[1])
        elif kind == 'command_applied' and row['current_check_verdict']:
            command = row['command']; robot = command['robot']
            if command['intent'] == 'Proceed' and robot not in starts:
                starts[robot] = row['time']
            elif command['intent'] == 'Brake' and robot in starts and row['time'] > starts[robot]:
                brakes.setdefault(robot, row['time'])
        elif kind == 'release':
            releases[row['robot']] = row['time']
        elif kind == 'complete':
            finishes[row['robot']] = row['time']
    assert set(grants) == set(starts) == set(releases) == set(finishes) == set('AB')
    assert set(brakes) == set('AB'), 'missing goal Brake application'
    assert len(grant_order) == 2
    details = {}
    start_latencies, release_latencies, travel_times, finish_latencies = [], [], [], []
    for robot in 'AB':
        crossing, arrival = physical_milestones(rows, params, robot)
        start_latency = (starts[robot]-grants[robot])*100
        release_latency = (releases[robot]-crossing)*100
        travel = (arrival-starts[robot])*100
        finish_latency = (finishes[robot]-arrival)*100
        halt_elapsed = (finishes[robot]-brakes[robot])*100
        assert start_latency <= START_BOUND+TOL, ('start bound', robot, start_latency)
        assert -TOL <= release_latency <= RELEASE_BOUND+TOL, ('release bound', robot, release_latency)
        assert travel <= TRAVEL_BOUND+TOL, ('travel service bound', robot, travel)
        assert halt_elapsed+TOL >= HALT_THRESHOLD, ('halt timer', robot, halt_elapsed)
        assert 0 <= finish_latency <= FINISH_BOUND+TOL, ('finish bound', robot, finish_latency)
        details[robot] = dict(grant=grants[robot], start=starts[robot], clear_crossing=crossing,
                              release=releases[robot], arrival=arrival, brake_applied=brakes[robot],
                              finish=finishes[robot], start_ticks=start_latency,
                              release_ticks=release_latency, travel_ticks=travel,
                              finish_ticks=finish_latency, halt_ticks=halt_elapsed)
        start_latencies.append(start_latency); release_latencies.append(release_latency)
        travel_times.append(travel); finish_latencies.append(finish_latency)
    first, second = grant_order
    assert grants[first]*100 <= 10+TOL, ('initial grant bound', grants[first]*100)
    assert (grants[second]-releases[first])*100 <= 10+TOL, ('inter-task grant bound', first, second)
    return dict(passed=True, grant_order=grant_order, robots=details,
                maxima_ticks=dict(start=max(start_latencies), release=max(release_latencies),
                                  travel=max(travel_times), finish=max(finish_latencies)),
                last_finish=max(finishes.values()))
