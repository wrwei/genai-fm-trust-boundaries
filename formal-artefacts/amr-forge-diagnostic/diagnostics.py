"""Offline, bounded diagnostics for the fixed AMR v1.1 obligation partition.

The two parser profiles are separate packages copied from the frozen checker.
They never replace its top-level imports or mutate an existing parser. Complete
domain results stay in ``full_cases``; only feedback returned by the dedicated
feedback functions belongs in a repair prompt.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROFILE_PACKAGE = "_amr_forge_diagnostic_profiles"
FEEDBACK_ID = "amr-forge-diagnostic-feedback/v1"
CURRENT_CAP = 8
HISTORY_CAP = 4


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def _json_value(value):
    """Keep case outputs and feedback stable across a JSON evidence round trip."""
    return json.loads(_canonical(value))


def _profile(limit):
    if type(limit) is not int or limit not in (8, 12):
        raise ValueError("rule limit must be exactly 8 or 12")
    if PROFILE_PACKAGE not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            PROFILE_PACKAGE, HERE / "profiles" / "__init__.py",
            submodule_search_locations=[str(HERE / "profiles")])
        module = importlib.util.module_from_spec(spec)
        sys.modules[PROFILE_PACKAGE] = module
        spec.loader.exec_module(module)
    root = f"{PROFILE_PACKAGE}.rules{limit}"
    return tuple(importlib.import_module(f"{root}.{name}")
                 for name in ("language", "model", "assurance"))


def _location(language, program, original, kind, facts, mode):
    values = dict(facts)
    if kind == "step":
        values.update({"Mode" + name: mode == name for name in language.MODES})
    for index, rule in enumerate(getattr(program, kind)):
        if language._evaluate(rule.condition, values):
            return {"status": "matched", "function": kind, "rule_index": index,
                    "json_path": f"$.{kind}[{index}]",
                    "condition": original[kind][index]["when"]}
    return {"status": "no_match", "function": kind, "rule_index": None,
            "json_path": None, "condition": None}


def _correspondence(source, outputs, source_error, model_error):
    source_defined = source_error is None
    model_defined = model_error is None and bool(outputs)
    if not source_defined and not model_defined:
        return "source_and_model_undefined"
    if not source_defined:
        return "source_undefined"
    if not model_defined:
        return "model_undefined"
    return "matched" if set(outputs) == {source} else "defined_outputs_differ"


def _inspect(language, model, assurance, program, target, original, kind, facts, mode=None):
    source_error = model_error = None
    try:
        source = (language.eval_select(program, facts) if kind == "select"
                  else language.eval_step(program, mode, facts))
    except ValueError as error:
        source, source_error = None, str(error)
    try:
        outputs = (model.model_select(target, facts) if kind == "select"
                   else model.model_step(target, mode, facts))
    except ValueError as error:
        outputs, model_error = (), str(error)

    def bad(output):
        return (assurance.selection_violations(output, facts) if kind == "select"
                else assurance.step_violations(output, mode, facts))

    issues = [source_error] if source_error else bad(source)
    model_issues = ([model_error or "no_enabled_model_response"] if not outputs
                    else sorted({reason for output in outputs for reason in bad(output)}))
    if kind == "select":
        allowed = [action for action in language.SELECT_ACTIONS if not bad(action)]
        # Selection labels are precisely the frozen checker's obligation labels.
        # The generic label applies only to already-permitted selection results.
        requirement = (assurance.selection_violations(source, facts) or
                       ["selection_eligibility_and_progress"])[0]
    else:
        requirement, expected = assurance.obligation(mode, facts)
        allowed = [expected]
    context = {"function": kind, "facts": dict(facts), "mode": mode}
    input_id = kind + ":" + hashlib.sha256(_canonical(context).encode("utf-8")).hexdigest()
    return {**context, "input": deepcopy(context), "input_id": input_id,
            "source_location": _location(language, program, original, kind, facts, mode),
            "actual": _json_value(source), "allowed_outputs": _json_value(allowed),
            "violations": issues, "model_outputs": _json_value(outputs),
            "model_violations": model_issues, "source_error": source_error,
            "model_error": model_error,
            "correspondence_category": _correspondence(source, outputs, source_error, model_error),
            "requirement_id": requirement}


def _failed(case):
    return bool(case["violations"] or case["model_violations"] or
                case["correspondence_category"] != "matched")


def assess(text: str, limit: int) -> dict:
    """Return frozen assessment fields plus complete JSON-friendly diagnostics.

    ``failure_input_ids`` is the union of source, model, and correspondence
    failures. Separate sets are also returned for trajectory differences.
    Invalid source text returns no full cases, as in the frozen parse-stage gate.
    """
    language, model, assurance = _profile(limit)
    report = assurance.assess_source(text)
    config = json.loads((HERE / "profiles" / "snapshot.json").read_text(encoding="utf-8"))["profiles"][str(limit)]
    report.update(profile_id=config["profile_id"], profile_config=config, full_cases=[],
                  rule_counts=None, failure_input_ids=[], source_failure_input_ids=[],
                  model_failure_input_ids=[], correspondence_failure_input_ids=[])
    if not report["parse_pass"]:
        return report
    program = language.parse_program(text)
    target = model.extract_model(program)
    original = json.loads(text)
    report["rule_counts"] = {"select": len(program.select), "step": len(program.step),
                             "total": len(program.select) + len(program.step)}
    cases = report["full_cases"]
    for facts in assurance.valuations(language.SELECT_FACTS):
        cases.append(_inspect(language, model, assurance, program, target, original, "select", facts))
    for mode in language.MODES:
        for facts in assurance.valuations(language.STEP_FACTS):
            cases.append(_inspect(language, model, assurance, program, target, original, "step", facts, mode))
    report["source_failure_input_ids"] = [case["input_id"] for case in cases if case["violations"]]
    report["model_failure_input_ids"] = [case["input_id"] for case in cases if case["model_violations"]]
    report["correspondence_failure_input_ids"] = [case["input_id"] for case in cases
                                                if case["correspondence_category"] != "matched"]
    report["failure_input_ids"] = [case["input_id"] for case in cases if _failed(case)]
    return report


def original_feedback(report: dict) -> dict:
    """Exactly the frozen trial._feedback fields, counts, truncation and category."""
    category = ("accepted" if report["accepted"] else
                ("semantic_rejection" if report["parse_pass"] else "parse_rejection"))
    return {"rejection_category": category, "parse_error": report.get("parse_error"),
            "checked_inputs": report.get("checked_inputs", 0),
            "counts": {key: report.get(key, 0) for key in
                       ("select_inputs", "step_inputs", "source_violation_inputs",
                        "model_violation_inputs", "correspondence_mismatches")},
            "source_witnesses": deepcopy(report.get("source_witnesses", [])[:2]),
            "correspondence_witnesses": deepcopy(report.get("correspondence_witnesses", [])[:2]),
            "witness_cap": 2, "witnesses_may_not_cover_all_failure_classes": True}


FIX_DIRECTIVES = {
    "selection_unknown_action": "Provide a matching selection rule for this input. Select only an available requesting vehicle; when both are eligible either selection is allowed, and Defer is allowed only when neither is eligible.",
    "selection_without_available_request_A": "SelectA requires a free owner and RequestA. Return one of the allowed selection outputs and preserve the eligibility of other inputs.",
    "selection_without_available_request_B": "SelectB requires a free owner and RequestB. Return one of the allowed selection outputs and preserve the eligibility of other inputs.",
    "selection_unnecessary_deferral": "When the owner is free and a request is available, select an eligible requester instead of deferring. Either requester is allowed when both are eligible.",
    "selection_eligibility_and_progress": "Preserve selection eligibility and progress: choose an available requester, with either choice allowed when both are eligible, and defer only when neither is eligible.",
    "stop_on_invalid_or_blocked_input": "Give the stop obligation priority over goal, release, request, resume, and proceed behavior. On unusable observation, inactive task, or pedestrian blockage, Brake is required; use Stopped only when Halted is true, and BrakeRequested while Halted is false.",
    "brake_at_released_goal_until_halted": "At an otherwise valid released goal with Halted false, keep Brake and BrakeRequested until standstill is confirmed. This obligation follows the invalid-or-blocked stop obligation and precedes completion or movement.",
    "finish_only_at_valid_halted_released_goal": "Finish with Done only at an otherwise valid goal after Halted and Released are both true. Preserve the higher-priority stop and goal-braking obligations; this completion obligation precedes release and movement.",
    "release_owned_and_clear_zone": "Release with Traversing only when the reservation is owned and the body is clear of the zone, after higher-priority stop and goal obligations. This release obligation precedes waiting, requesting, resuming, and proceeding.",
    "wait_for_standstill": "While BrakeRequested and not Halted, preserve Brake with BrakeRequested after the higher-priority stop, goal, and release obligations. Do not report Stopped or resume before standstill.",
    "request_before_passage": "Request with Waiting when no reservation is owned and none has been released, after higher-priority stop, goal, release, and standstill obligations. Request precedes resume or proceed.",
    "resume_before_proceed": "When currently Stopped and no higher-priority stop, goal, release, standstill, or request obligation applies, Resume with ResumePending before proceeding.",
    "proceed_when_currently_allowed": "Provide Proceed with Traversing when none of the higher-priority stop, goal, release, standstill, request, or resume obligations applies. Ensure a matching rule covers the remaining valid input.",
}


def _example(case):
    example = deepcopy(case)
    example["stage"] = ("source_policy" if case["violations"] else
                        "model_policy" if case["model_violations"] else
                        "correspondence" if case["correspondence_category"] != "matched" else "satisfied")
    example["fix_directive"] = FIX_DIRECTIVES[case["requirement_id"]]
    return example


def _group_key(case):
    return (case["function"], case["requirement_id"],
            _canonical(case["allowed_outputs"]), str(case["facts"].get("Halted")))


def enhanced_feedback(report: dict, history: list[dict]) -> dict:
    """Select at most eight grouped current and four recomputed historical cases.

    History is the ordered union of inputs actually sent in earlier feedback.
    Historical status compares the previous assessed source output with its
    permitted set; output locations and results come from the current report.
    Before advancing a candidate, call update_history with its sent feedback,
    then refresh_history with that same candidate's complete assessment.
    Neither this function nor ``update_history`` mutates its arguments.
    """
    feedback = {"schema": FEEDBACK_ID,
                "stage": "parse" if not report["parse_pass"] else "accepted" if report["accepted"] else "source_model",
                "parse_error": report.get("parse_error"),
                "checked_inputs": report["checked_inputs"],
                "counts": original_feedback(report)["counts"],
                "current_example_cap": CURRENT_CAP, "regression_example_cap": HISTORY_CAP,
                "current_examples": [], "regression_examples": [],
                "selection_policy": "first input per (function, obligation, allowed outputs, Halted) group; sorted groups; history regressed, repaired, unresolved then first seen"}
    if not report["parse_pass"]:
        return feedback
    representatives = {}
    for case in report["full_cases"]:
        if _failed(case):
            representatives.setdefault(_group_key(case), case)
    feedback["current_examples"] = [_example(representatives[key])
                                     for key in sorted(representatives)[:CURRENT_CAP]]
    current_ids = {example["input_id"] for example in feedback["current_examples"]}
    current = {case["input_id"]: case for case in report["full_cases"]}
    historical = []
    seen = set()
    for index, previous in enumerate(history):
        input_id = previous["input_id"]
        if input_id in seen or input_id in current_ids or input_id not in current:
            continue
        seen.add(input_id)
        case = current[input_id]
        previously_permitted = previous["actual"] in previous["allowed_outputs"]
        now_permitted = case["actual"] in case["allowed_outputs"]
        status = ("regressed" if previously_permitted and not now_permitted else
                  "repaired" if now_permitted else "unresolved")
        priority = {"regressed": 0, "repaired": 1, "unresolved": 2}[status]
        example = _example(case)
        example.update(history_status=status, previous_actual=deepcopy(previous["actual"]),
                       previous_requirement_id=previous["requirement_id"], first_seen_order=index)
        historical.append((priority, index, example))
    historical.sort(key=lambda row: (row[0], row[1]))
    feedback["regression_examples"] = [example for _, _, example in historical[:HISTORY_CAP]]
    return feedback


def update_history(history: list[dict], feedback: dict) -> list[dict]:
    """Immutably add both sent example sets; update known inputs in first-seen order."""
    result = deepcopy(history)
    positions = {example["input_id"]: index for index, example in enumerate(result)}
    for example in feedback.get("current_examples", []) + feedback.get("regression_examples", []):
        value = deepcopy(example)
        input_id = value["input_id"]
        if input_id in positions:
            result[positions[input_id]] = value
        else:
            positions[input_id] = len(result)
            result.append(value)
    return result


def refresh_history(history: list[dict], report: dict) -> list[dict]:
    """Refresh every previously sent input, including examples omitted by caps.

    Preserve first-seen order. A parse rejection has no domain evaluation, so
    the last evaluable statuses remain available. Call this with the *previous*
    candidate's report before comparing history with the next candidate.
    """
    current = {case["input_id"]: case for case in report["full_cases"]}
    return [_example(current[previous["input_id"]]) if previous["input_id"] in current
            else deepcopy(previous) for previous in history]


def program_key(text: str, limit: int) -> str:
    """Digest parsed canonical AST, preserving rule order; raw bytes on failure.

    Bytes are also accepted for the invalid-UTF-8 transport boundary so that a
    runner never needs to replace undecodable bytes before cycle detection.
    The key prefix distinguishes canonical syntax from unparseable raw input.
    """
    language, _, _ = _profile(limit)
    raw = text if isinstance(text, bytes) else text.encode("utf-8", errors="surrogatepass")
    try:
        parsed_text = raw.decode("utf-8") if isinstance(text, bytes) else text
        program = language.parse_program(parsed_text)
    except (ValueError, TypeError, SyntaxError, UnicodeError):
        return "raw-sha256:" + hashlib.sha256(raw).hexdigest()
    return "ast-sha256:" + hashlib.sha256(_canonical(asdict(program)).encode("utf-8")).hexdigest()
