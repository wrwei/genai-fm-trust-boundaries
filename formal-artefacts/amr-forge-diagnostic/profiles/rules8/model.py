"""Extract ordered source branches into an independently executed relation.

Only immutable syntax and vocabulary cross the source/target boundary. Target
guards are postfix stack programs; every enabled branch remains observable.
Fault names denote experimental mutations, not claims about existing tools.
"""
from dataclasses import dataclass
from collections.abc import Mapping

from .language import Program, MODES, SELECT_FACTS, STEP_FACTS


@dataclass(frozen=True)
class TargetRule:
    guard: tuple
    action: str
    next_mode: str | None

    def to_dict(self):
        return {'guard': [list(instruction) for instruction in self.guard],
                'action': self.action, 'next': self.next_mode}


@dataclass(frozen=True)
class Model:
    schema: str
    select: tuple[TargetRule, ...]
    step: tuple[TargetRule, ...]
    fault: str | None = None

    def to_dict(self):
        return {'schema': self.schema, 'fault': self.fault,
                'encoding': 'postfix-priority-guards/v1',
                'select': [rule.to_dict() for rule in self.select],
                'step': [rule.to_dict() for rule in self.step]}


def _compile(expression, invert_observation=False):
    op, *args = expression
    if op == 'const':
        return (('PUSH', args[0]),)
    if op == 'var':
        code = (('LOAD', args[0]),)
        return code + (('NOT',),) if invert_observation and args[0] == 'ObservationUsable' else code
    if op == 'not':
        code = _compile(args[0], invert_observation)
        # Cancellation also simplifies an original not ObservationUsable when
        # the deliberately faulty compiler flips its inner occurrence.
        return code[:-1] if code[-1] == ('NOT',) else code + (('NOT',),)
    if op in ('and', 'or'):
        code = tuple(instruction for arg in args for instruction in _compile(arg, invert_observation))
        return code + ((op.upper(), len(args)),)
    raise ValueError(f'unsupported expression opcode: {op}')


def _extract_rules(rules, fault, is_step):
    preceding = []
    extracted = []
    for rule in rules:
        condition = _compile(rule.condition, is_step and fault == 'invert_observation_tests')
        guard = condition
        if fault != 'omit_priority':
            for previous in preceding:
                guard += previous + (('NOT',), ('AND', 2))
        if not is_step and fault == 'choose_b_when_both' and rule.action == 'SelectA':
            both = (('LOAD', 'RequestA'), ('LOAD', 'RequestB'), ('AND', 2))
            extracted.append(TargetRule(guard + both + (('AND', 2),), 'SelectB', rule.next_mode))
            extracted.append(TargetRule(guard + both + (('NOT',), ('AND', 2)), 'SelectA', rule.next_mode))
        else:
            extracted.append(TargetRule(guard, rule.action, rule.next_mode))
        preceding.append(condition)
    return tuple(extracted)


def extract_model(program: Program, fault=None):
    """Compile a parsed Program, optionally injecting one named extraction fault."""
    if fault not in (None, 'omit_priority', 'choose_b_when_both', 'invert_observation_tests'):
        raise ValueError(f'unknown extraction fault: {fault}')
    return Model(program.schema, _extract_rules(program.select, fault, False),
                 _extract_rules(program.step, fault, True), fault)


def _facts(facts, expected):
    if not isinstance(facts, Mapping) or set(facts) != set(expected):
        raise ValueError('facts must have exactly the target input keys')
    if any(type(value) is not bool for value in facts.values()):
        raise ValueError('target input values must be exact booleans')
    return dict(facts)


def _enabled(code, environment):
    stack = []
    for instruction in code:
        opcode = instruction[0]
        if opcode == 'PUSH':
            stack.append(instruction[1])
        elif opcode == 'LOAD':
            stack.append(environment[instruction[1]])
        elif opcode == 'NOT':
            stack.append(not stack.pop())
        elif opcode in ('AND', 'OR'):
            count = instruction[1]
            values = stack[-count:] if count else []
            if count:
                del stack[-count:]
            stack.append(all(values) if opcode == 'AND' else any(values))
        else:
            raise ValueError(f'unknown target instruction: {opcode}')
    if len(stack) != 1 or type(stack[0]) is not bool:
        raise ValueError('invalid target stack result')
    return stack[0]


def model_select(model, facts):
    environment = _facts(facts, SELECT_FACTS)
    return tuple(rule.action for rule in model.select if _enabled(rule.guard, environment))


def model_step(model, mode, facts):
    if mode not in MODES:
        raise ValueError(f'unknown target mode: {mode}')
    environment = _facts(facts, STEP_FACTS)
    environment.update(('Mode' + name, mode == name) for name in MODES)
    return tuple((rule.action, rule.next_mode) for rule in model.step if _enabled(rule.guard, environment))
