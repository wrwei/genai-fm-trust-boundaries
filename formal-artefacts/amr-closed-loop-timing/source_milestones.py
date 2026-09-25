"""Evaluate fixed stable-progress milestones with the accepted source bytes."""
import hashlib
from pathlib import Path
import sys

V2 = Path(__file__).resolve().parents[1]/'amr-advisory-v2'
sys.path.insert(0, str(V2))
from protocol import SourceController
from source_check import language

SOURCE_ID = '9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd'


def facts(**changes):
    row = dict(ObservationUsable=True, PedestrianBlocked=False, OwnReservation=False,
               Released=False, BodyClearOfZ=False, Halted=False, AtGoal=False,
               TaskActive=True)
    unknown = set(changes)-set(row)
    if unknown:
        raise ValueError(f'unknown facts: {sorted(unknown)}')
    row.update(changes)
    return row


def milestones():
    return [
        dict(name='unusable', mode='Traversing', facts=facts(ObservationUsable=False),
             expected_action='Brake', expected_next='BrakeRequested'),
        dict(name='braking_owner', mode='BrakeRequested', facts=facts(OwnReservation=True),
             expected_action='Brake', expected_next='BrakeRequested'),
        dict(name='halted_owner', mode='BrakeRequested', facts=facts(OwnReservation=True,Halted=True),
             expected_action='Proceed', expected_next='Traversing'),
        dict(name='waiting_owner', mode='Waiting', facts=facts(OwnReservation=True),
             expected_action='Proceed', expected_next='Traversing'),
        dict(name='clear_owner', mode='Traversing', facts=facts(OwnReservation=True,BodyClearOfZ=True),
             expected_action='Release', expected_next='Traversing'),
        dict(name='released_motion', mode='Traversing', facts=facts(Released=True,BodyClearOfZ=True),
             expected_action='Proceed', expected_next='Traversing'),
        dict(name='goal_brake', mode='Traversing', facts=facts(Released=True,BodyClearOfZ=True,AtGoal=True),
             expected_action='Brake', expected_next='BrakeRequested'),
        dict(name='goal_finish', mode='BrakeRequested', facts=facts(Released=True,BodyClearOfZ=True,
                                                                   AtGoal=True,Halted=True),
             expected_action='Finish', expected_next='Done'),
    ]


def controller():
    source = SourceController.from_selected()
    if source.identity != SOURCE_ID or hashlib.sha256(source.raw).hexdigest() != SOURCE_ID:
        raise ValueError('selected source identity drift')
    return source


def evaluate_case(name, *, mode=None, facts_override=None):
    try:
        case = next(row for row in milestones() if row['name'] == name)
    except StopIteration as error:
        raise ValueError('unknown milestone') from error
    selected_mode = case['mode'] if mode is None else mode
    if selected_mode not in language.MODES:
        raise ValueError('unknown mode')
    selected_facts = dict(case['facts'])
    if facts_override:
        unknown = set(facts_override)-set(language.STEP_FACTS)
        if unknown:
            raise ValueError(f'unknown facts: {sorted(unknown)}')
        selected_facts.update(facts_override)
    action, nxt = controller().step(selected_mode, selected_facts)
    result = dict(case)
    result.update(mode=selected_mode, facts=selected_facts,
                  actual_action=action, actual_next=nxt,
                  passed=(action,nxt)==(case['expected_action'],case['expected_next']),
                  source_id=SOURCE_ID)
    return result


def evaluate():
    rows = [evaluate_case(case['name']) for case in milestones()]
    if not all(row['passed'] for row in rows):
        raise AssertionError('accepted source violates stable timing milestone')
    return rows
