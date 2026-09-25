"""Strict, bounded AMR supervisor syntax and first-match source semantics.

Parsing only uses Python's AST as syntax; no expression is compiled or eval'd.
Totality and action obligations are checked separately over the finite domain.
"""
from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import TypeAlias

MODES = ("Idle", "Waiting", "Traversing", "BrakeRequested", "Stopped", "ResumePending", "Done")
STEP_FACTS = ("ObservationUsable", "PedestrianBlocked", "OwnReservation", "Released",
              "BodyClearOfZ", "Halted", "AtGoal", "TaskActive")
SELECT_FACTS = ("OwnerFree", "RequestA", "RequestB", "PreferA", "PreferB")
SELECT_ACTIONS = ("SelectA", "SelectB", "Defer")
STEP_ACTIONS = ("Request", "Proceed", "Brake", "Resume", "Release", "Finish")
MODE_FACTS = tuple("Mode" + mode for mode in MODES)
MAX_TEXT_BYTES = 200 * 1024
MAX_EXPR_LENGTH = 512
MAX_AST_NODES = 64
MAX_EXPR_DEPTH = 8
Expr: TypeAlias = tuple


@dataclass(frozen=True)
class Rule:
    condition: Expr
    action: str
    next_mode: str | None = None


@dataclass(frozen=True)
class Program:
    schema: str
    select: tuple[Rule, ...]
    step: tuple[Rule, ...]


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def _expression(text: str, allowed: tuple[str, ...]) -> Expr:
    if type(text) is not str or not text.strip() or len(text) > MAX_EXPR_LENGTH:
        raise ValueError("when must be a nonempty expression of at most 512 characters")
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("invalid when syntax") from exc
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ValueError("expression exceeds 64 AST nodes")

    def convert(node, depth):
        if depth > MAX_EXPR_DEPTH:
            raise ValueError("expression exceeds depth 8")
        if isinstance(node, ast.Constant) and type(node.value) is bool:
            return ("const", node.value)
        if isinstance(node, ast.Name) and node.id in allowed:
            return ("var", node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return ("not", convert(node.operand, depth + 1))
        if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            return ("and" if isinstance(node.op, ast.And) else "or",
                    *(convert(value, depth + 1) for value in node.values))
        raise ValueError(f"forbidden expression syntax or name: {type(node).__name__}")

    return convert(tree.body, 1)


def _rules(value, step: bool) -> tuple[Rule, ...]:
    if type(value) is not list or len(value) > 12:
        raise ValueError("each function must contain a list of at most 12 rules")
    keys = {"when", "action", "next"} if step else {"when", "action"}
    actions = STEP_ACTIONS if step else SELECT_ACTIONS
    names = STEP_FACTS + MODE_FACTS if step else SELECT_FACTS
    rules = []
    for item in value:
        if type(item) is not dict or set(item) != keys:
            raise ValueError("rule has missing or extra fields")
        if type(item["action"]) is not str or item["action"] not in actions:
            raise ValueError("invalid action")
        next_mode = item.get("next")
        if step and (type(next_mode) is not str or next_mode not in MODES):
            raise ValueError("invalid next mode")
        rules.append(Rule(_expression(item["when"], names), item["action"], next_mode))
    return tuple(rules)


def parse_program(text: str) -> Program:
    """Parse strict JSON into immutable rules; an uncovered domain is permitted."""
    if type(text) is not str:
        raise ValueError("program text must be a string")
    try:
        size = len(text.encode("utf-8"))
    except UnicodeError as exc:
        raise ValueError("program text must be valid UTF-8") from exc
    if size > MAX_TEXT_BYTES:
        raise ValueError("program exceeds 200 KB")
    try:
        data = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("invalid program JSON") from exc
    if type(data) is not dict or set(data) != {"schema", "select", "step"}:
        raise ValueError("program requires exactly schema, select, step")
    if data["schema"] != "amr-supervisor/v1":
        raise ValueError("unsupported schema")
    select, step = _rules(data["select"], False), _rules(data["step"], True)
    if len(select) + len(step) > 32:
        raise ValueError("program exceeds 32 total branches")
    return Program(data["schema"], select, step)


def _validated_facts(facts, names):
    if not isinstance(facts, Mapping) or set(facts) != set(names):
        raise ValueError("facts must have the exact expected key set")
    result = dict(facts)
    if any(type(value) is not bool for value in result.values()):
        raise ValueError("facts must contain real bool values")
    return result


def _evaluate(expr: Expr, facts: Mapping[str, bool]) -> bool:
    kind = expr[0]
    if kind == "const":
        return expr[1]
    if kind == "var":
        return facts[expr[1]]
    if kind == "not":
        return not _evaluate(expr[1], facts)
    if kind == "and":
        return all(_evaluate(child, facts) for child in expr[1:])
    if kind == "or":
        return any(_evaluate(child, facts) for child in expr[1:])
    raise ValueError("invalid immutable expression")


def eval_select(program: Program, facts: Mapping[str, bool]) -> str:
    values = _validated_facts(facts, SELECT_FACTS)
    for rule in program.select:
        if _evaluate(rule.condition, values):
            return rule.action
    raise ValueError("no matching select rule")


def eval_step(program: Program, mode: str, facts: Mapping[str, bool]) -> tuple[str, str]:
    if type(mode) is not str or mode not in MODES:
        raise ValueError("invalid current mode")
    values = _validated_facts(facts, STEP_FACTS)
    values.update({"Mode" + name: name == mode for name in MODES})
    for rule in program.step:
        if _evaluate(rule.condition, values):
            return rule.action, rule.next_mode
    raise ValueError("no matching step rule")
