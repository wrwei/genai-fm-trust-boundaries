"""Fixed obligation checks, independent source/model accounting over finite inputs.

The rules are an authored specification. Exhausting Boolean valuations does not
prove natural-language adequacy, physical abstraction, reachability or liveness.
"""
import hashlib
import itertools

from language import parse_program, eval_select, eval_step, MODES, SELECT_FACTS, STEP_FACTS
from model import extract_model, model_select, model_step

SPEC_ID = 'amr-supervisor-obligations/v1'


def valuations(names):
    for bits in itertools.product((False, True), repeat=len(names)):
        yield dict(zip(names, bits))


def selection_violations(action, f):
    if action not in ('SelectA', 'SelectB', 'Defer'):
        return ['selection_unknown_action']
    if action == 'SelectA' and not (f['OwnerFree'] and f['RequestA']):
        return ['selection_without_available_request_A']
    if action == 'SelectB' and not (f['OwnerFree'] and f['RequestB']):
        return ['selection_without_available_request_B']
    if action == 'Defer' and f['OwnerFree'] and (f['RequestA'] or f['RequestB']):
        return ['selection_unnecessary_deferral']
    return []


def obligation(mode, f):
    """Name and required response for the fixed precedence obligations."""
    blocked = not f['ObservationUsable'] or not f['TaskActive'] or f['PedestrianBlocked']
    finish = not blocked and f['AtGoal'] and f['Halted'] and f['Released']
    release = not (blocked or finish) and f['OwnReservation'] and f['BodyClearOfZ']
    braking = not (blocked or finish or release) and mode == 'BrakeRequested' and not f['Halted']
    request = not (blocked or finish or release or braking) and not f['OwnReservation'] and not f['Released']
    resume = not (blocked or finish or release or braking or request) and mode == 'Stopped'
    requirements = (
        (blocked, 'stop_on_invalid_or_blocked_input', ('Brake', 'Stopped' if f['Halted'] else 'BrakeRequested')),
        (finish, 'finish_only_at_valid_halted_released_goal', ('Finish', 'Done')),
        (release, 'release_owned_and_clear_zone', ('Release', 'Traversing')),
        (braking, 'wait_for_standstill', ('Brake', 'BrakeRequested')),
        (request, 'request_before_passage', ('Request', 'Waiting')),
        (resume, 'resume_before_proceed', ('Resume', 'ResumePending')),
        (not any((blocked, finish, release, braking, request, resume)), 'proceed_when_currently_allowed', ('Proceed', 'Traversing')),
    )
    active = [(name, response) for applies, name, response in requirements if applies]
    if len(active) != 1:
        raise RuntimeError('Authored obligation partition is not exclusive/total')
    return active[0]


def step_violations(response, mode, f):
    name, expected = obligation(mode, f)
    return [] if response == expected else [name]


def assess_source(text, *, fault=None):
    report = dict(spec_id=SPEC_ID, source_sha256=None,
                  translator_fault=fault, parse_pass=False, parse_error=None,
                  checked_inputs=0, select_inputs=0, step_inputs=0,
                  source_violation_inputs=0, model_violation_inputs=0, correspondence_mismatches=0,
                  source_witnesses=[], model_witnesses=[], correspondence_witnesses=[],
                  source_policy_pass=False, model_policy_pass=False, correspondence_pass=False, accepted=False)
    try:
        if type(text) is not str:
            raise ValueError('program text must be a string')
        try:
            source_bytes = text.encode('utf-8')
        except UnicodeError as error:
            raise ValueError('program text must be valid UTF-8') from error
        report['source_sha256'] = hashlib.sha256(source_bytes).hexdigest()
        program = parse_program(text)
    except (ValueError, TypeError, SyntaxError) as error:
        report['parse_error'] = str(error)
        return report
    report['parse_pass'] = True
    target = extract_model(program, fault=fault)

    def inspect(kind, facts, mode=None):
        context = dict(function=kind, facts=facts, mode=mode)
        source_error = model_error = None
        try:
            source = eval_select(program, facts) if kind == 'select' else eval_step(program, mode, facts)
        except ValueError as error:
            source, source_error = None, str(error)
        try:
            outputs = model_select(target, facts) if kind == 'select' else model_step(target, mode, facts)
        except ValueError as error:
            outputs, model_error = (), str(error)
        def bad(value):
            return selection_violations(value, facts) if kind == 'select' else step_violations(value, mode, facts)
        source_issues = [source_error] if source_error else bad(source)
        model_issues = [model_error or 'no_enabled_model_response'] if not outputs else sorted({reason for output in outputs for reason in bad(output)})
        # The target is a relation: duplicate equal outcomes have no semantic effect.
        mismatch = source_error is not None or model_error is not None or set(outputs) != {source}
        report['checked_inputs'] += 1
        report[kind+'_inputs'] += 1
        if source_issues:
            report['source_violation_inputs'] += 1
            if len(report['source_witnesses']) < 4:
                report['source_witnesses'].append(dict(**context, response=source, violations=source_issues))
        if model_issues:
            report['model_violation_inputs'] += 1
            if len(report['model_witnesses']) < 4:
                report['model_witnesses'].append(dict(**context, responses=outputs, violations=model_issues))
        if mismatch:
            report['correspondence_mismatches'] += 1
            if len(report['correspondence_witnesses']) < 4:
                report['correspondence_witnesses'].append(dict(**context, source_response=source, model_responses=outputs,
                                                                 source_error=source_error, model_error=model_error))
    for facts in valuations(SELECT_FACTS):
        inspect('select', facts)
    for mode in MODES:
        for facts in valuations(STEP_FACTS):
            inspect('step', facts, mode)
    report['source_policy_pass'] = report['source_violation_inputs'] == 0
    report['model_policy_pass'] = report['model_violation_inputs'] == 0
    report['correspondence_pass'] = report['correspondence_mismatches'] == 0
    report['accepted'] = all(report[key] for key in ('source_policy_pass', 'model_policy_pass', 'correspondence_pass'))
    return report
