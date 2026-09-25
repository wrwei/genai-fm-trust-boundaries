"""Integer timing contract for the fixed 10 ms AMR driver clock."""

CONTROL_PERIOD = 5
SENSOR_DELIVERY = 5
COMMAND_DELIVERY = 10
HALT_THRESHOLD = 149
START_BOUND = 163
TRAVEL_BOUND = 3100
FINISH_BOUND = 169
INITIAL_GRANT_BOUND = 10
INTERTASK_GRANT_BOUND = 10


def tick(value, name='tick'):
    if type(value) is not int:
        raise TypeError(f'{name} must be an integer')
    if value < 0:
        raise ValueError(f'{name} must be nonnegative')
    return value


def next_control(time):
    time = tick(time)
    return time + (-time) % CONTROL_PERIOD


def observation_visible(event):
    return next_control(event) + SENSOR_DELIVERY


def release_from_clear(clear):
    return observation_visible(clear)


def start_from_grant(grant, brake_since, mode):
    grant, brake_since = tick(grant, 'grant'), tick(brake_since, 'brake_since')
    if grant % CONTROL_PERIOD:
        raise ValueError('grant must occur on the control clock')
    if brake_since > grant:
        raise ValueError('Brake must already be applied by the grant')
    if mode == 'Waiting':
        issue = grant + CONTROL_PERIOD
    elif mode == 'BrakeRequested':
        issue = max(grant + CONTROL_PERIOD, next_control(brake_since + HALT_THRESHOLD))
    else:
        raise ValueError('stable grant mode must be Waiting or BrakeRequested')
    return issue + COMMAND_DELIVERY


def finish_from_arrival(arrival):
    arrival = tick(arrival, 'arrival')
    brake_effect = observation_visible(arrival) + COMMAND_DELIVERY
    return next_control(brake_effect + HALT_THRESHOLD)


def two_task_bound():
    one = START_BOUND + TRAVEL_BOUND + FINISH_BOUND
    return INITIAL_GRANT_BOUND + one + INTERTASK_GRANT_BOUND + one
