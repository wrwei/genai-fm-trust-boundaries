"""Offline behavioral checks for bounded diagnostic profiles and repair feedback."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
SUPERVISOR = HERE.parent / "amr-supervisor"
sys.path.insert(0, str(SUPERVISOR))
sys.path.insert(0, str(HERE.parent / "amr-llm-trial"))
from assurance import assess_source as frozen_assess
from language import parse_program as frozen_parse
from trial import _feedback as frozen_feedback
sys.path.insert(0, str(HERE))
try:
    diagnostic = importlib.import_module("diagnostics")
except ModuleNotFoundError:
    diagnostic = None


def candidate(name="authored_reference"):
    return (SUPERVISOR / "candidates" / f"{name}.json").read_text(encoding="utf-8")


def padded(function, count):
    data = json.loads(candidate())
    rule = {"when": "False", "action": "Defer"} if function == "select" else {
        "when": "False", "action": "Brake", "next": "BrakeRequested"}
    data[function] += [deepcopy(rule) for _ in range(count - len(data[function]))]
    return json.dumps(data)


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(diagnostic, "the diagnostic API must be implemented")

    def test_profiles_accept_fixed_positives_with_complete_input_domain(self):
        for limit in (8, 12):
            for name in ("authored_reference", "authored_demorgan"):
                with self.subTest(limit=limit, name=name):
                    report = diagnostic.assess(candidate(name), limit)
                    self.assertTrue(report["accepted"])
                    self.assertEqual(report["checked_inputs"], 1824)
                    self.assertEqual(len(report["full_cases"]), 1824)
                    self.assertEqual(len({case["input_id"] for case in report["full_cases"]}), 1824)
                    self.assertEqual(report["select_inputs"], 32)
                    self.assertEqual(report["step_inputs"], 1792)

    def test_nine_twelve_thirteen_rule_boundaries_apply_to_each_function(self):
        for function in ("select", "step"):
            for count, limit, expected in ((9, 8, False), (9, 12, True),
                                            (12, 12, True), (13, 12, False)):
                with self.subTest(function=function, count=count, limit=limit):
                    report = diagnostic.assess(padded(function, count), limit)
                    self.assertEqual(report["parse_pass"], expected)
                    self.assertEqual(report["accepted"], expected)

    def test_profile_twelve_does_not_mutate_frozen_or_profile_eight_parser(self):
        text = padded("step", 12)
        self.assertTrue(diagnostic.assess(text, 12)["accepted"])
        with self.assertRaises(ValueError):
            frozen_parse(text)
        self.assertFalse(diagnostic.assess(text, 8)["parse_pass"])
        self.assertTrue(diagnostic.assess(text, 12)["accepted"])

    def test_relaxed_rule_limit_does_not_relax_action_or_expression_syntax(self):
        for value in (False, 1, {}, "Defer"):
            data = json.loads(padded("step", 12))
            data["step"][0]["action"] = value
            with self.subTest(value=value):
                self.assertFalse(diagnostic.assess(json.dumps(data), 12)["parse_pass"])
        data = json.loads(padded("step", 12))
        data["step"][0]["when"] = "__import__('os')"
        self.assertFalse(diagnostic.assess(json.dumps(data), 12)["parse_pass"])
        for value in (None, 1, [], True):
            self.assertFalse(diagnostic.assess(json.dumps(value), 12)["parse_pass"])

    def test_relaxed_rule_limit_preserves_safety_and_progress_obligations(self):
        for name in ("always_brake", "early_release", "finish_unhalted", "ignore_pedestrian", "goal_stop_gap"):
            with self.subTest(name=name):
                report = diagnostic.assess(candidate(name), 12)
                self.assertTrue(report["parse_pass"])
                self.assertFalse(report["accepted"])
                self.assertGreater(report["source_violation_inputs"], 0)

    def test_frozen_assessment_fields_and_original_feedback_are_exact(self):
        for text in (candidate(), candidate("always_brake"), '{"broken":true}'):
            frozen = frozen_assess(text)
            report = diagnostic.assess(text, 8)
            self.assertEqual({key: report[key] for key in frozen}, frozen)
            category = "accepted" if frozen["accepted"] else (
                "semantic_rejection" if frozen["parse_pass"] else "parse_rejection")
            self.assertEqual(diagnostic.original_feedback(report), frozen_feedback(frozen, category))
            self.assertNotIn("full_cases", diagnostic.original_feedback(report))

    def test_select_allowed_outputs_include_both_eligible_vehicles(self):
        report = diagnostic.assess(candidate(), 12)
        both = [case for case in report["full_cases"] if case["function"] == "select"
                and all(case["facts"][name] for name in ("OwnerFree", "RequestA", "RequestB"))]
        self.assertEqual(len(both), 4)
        for case in both:
            self.assertEqual(case["allowed_outputs"], ["SelectA", "SelectB"])
            self.assertIn(case["actual"], case["allowed_outputs"])
            self.assertEqual(case["correspondence_category"], "matched")

    def test_uncovered_inputs_are_distinguished_from_defined_disagreement(self):
        data = json.loads(candidate())
        data["step"] = []
        report = diagnostic.assess(json.dumps(data), 12)
        first = next(case for case in report["full_cases"] if case["function"] == "step")
        self.assertEqual(first["correspondence_category"], "source_and_model_undefined")
        self.assertEqual(first["source_location"]["status"], "no_match")
        self.assertIsNone(first["source_location"]["rule_index"])
        self.assertEqual(first["allowed_outputs"], [["Brake", "BrakeRequested"]])

    def test_current_examples_cover_both_standstill_states_in_stable_order(self):
        text = (HERE.parent / "amr-deepseek-pilot/run/records/004/response.bin").read_text(encoding="utf-8")
        report = diagnostic.assess(text, 12)
        feedback = diagnostic.enhanced_feedback(report, [])
        self.assertLessEqual(len(feedback["current_examples"]), 8)
        self.assertEqual(feedback, diagnostic.enhanced_feedback(report, []))
        stopped = next(example for example in feedback["current_examples"]
                       if example["requirement_id"] == "stop_on_invalid_or_blocked_input")
        self.assertFalse(stopped["input"]["facts"]["Halted"])
        self.assertEqual(stopped["actual"], ["Brake", "Stopped"])
        self.assertEqual(stopped["allowed_outputs"], [["Brake", "BrakeRequested"]])
        self.assertEqual(stopped["source_location"]["json_path"], "$.step[0]")
        self.assertIn("Halted", stopped["fix_directive"])
        self.assertIn("Stopped", stopped["fix_directive"])
        self.assertTrue(any(example["source_location"]["status"] == "no_match"
                            for example in feedback["current_examples"]))
        self.assertEqual(feedback["regression_examples"], [])

    def test_current_group_cap_and_first_enumerated_representatives(self):
        data = json.loads(candidate())
        data["select"] = []
        data["step"] = []
        report = diagnostic.assess(json.dumps(data), 12)
        examples = diagnostic.enhanced_feedback(report, [])["current_examples"]
        self.assertEqual(len(examples), 8)
        keys = [(example["function"], example["requirement_id"],
                 json.dumps(example["allowed_outputs"], sort_keys=True),
                 str(example["facts"].get("Halted"))) for example in examples]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(example["fix_directive"] for example in examples))
        for example in examples:
            earlier = [case for case in report["full_cases"]
                       if case["function"] == example["function"]
                       and case["requirement_id"] == example["requirement_id"]
                       and case["allowed_outputs"] == example["allowed_outputs"]
                       and case["facts"].get("Halted") == example["facts"].get("Halted")]
            self.assertEqual(example["input_id"], earlier[0]["input_id"])

    def test_history_prioritizes_regressed_then_repaired_then_unresolved(self):
        data = json.loads(candidate())
        data["step"] = [{"when": "True", "action": "Brake", "next": "Stopped"}]
        report = diagnostic.assess(json.dumps(data), 12)
        current_ids = {x["input_id"] for x in diagnostic.enhanced_feedback(report, [])["current_examples"]}
        bad = [case for case in report["full_cases"] if case["function"] == "step"
               and not case["facts"]["ObservationUsable"] and not case["facts"]["Halted"]
               and case["input_id"] not in current_ids]
        good = [case for case in report["full_cases"] if case["function"] == "step"
                and not case["facts"]["ObservationUsable"] and case["facts"]["Halted"]]
        unresolved, repaired, regressed = deepcopy(bad[0]), deepcopy(good[0]), deepcopy(bad[1])
        repaired["actual"] = ["Brake", "BrakeRequested"]
        repaired["violations"] = ["stop_on_invalid_or_blocked_input"]
        regressed["actual"] = ["Brake", "BrakeRequested"]
        regressed["violations"] = []
        history = [unresolved, repaired, regressed]
        saved = deepcopy(history)
        examples = diagnostic.enhanced_feedback(report, history)["regression_examples"]
        self.assertEqual([x["history_status"] for x in examples], ["regressed", "repaired", "unresolved"])
        self.assertEqual([x["input_id"] for x in examples],
                         [regressed["input_id"], repaired["input_id"], unresolved["input_id"]])
        self.assertEqual(history, saved)
        self.assertTrue(all(x["actual"] == ["Brake", "Stopped"] for x in examples))

    def test_history_recomputes_locations_caps_at_four_and_excludes_current(self):
        before = diagnostic.assess(candidate("always_brake"), 12)
        first_feedback = diagnostic.enhanced_feedback(before, [])
        history = diagnostic.update_history([], first_feedback)
        data = json.loads(candidate("always_brake"))
        data["step"].insert(0, {"when": "False", "action": "Brake", "next": "Stopped"})
        after = diagnostic.assess(json.dumps(data), 12)
        # A passing controller makes every previously failing sent case repaired.
        repaired_data = json.loads(candidate())
        repaired_data["step"].insert(0, {"when": "False", "action": "Brake", "next": "Stopped"})
        repaired = diagnostic.assess(json.dumps(repaired_data), 12)
        feedback = diagnostic.enhanced_feedback(repaired, history)
        self.assertEqual(len(feedback["regression_examples"]), min(4, len(history)))
        self.assertTrue(all(x["history_status"] == "repaired" for x in feedback["regression_examples"]))
        index = {case["input_id"]: case for case in repaired["full_cases"]}
        for example in feedback["regression_examples"]:
            self.assertEqual(example["source_location"], index[example["input_id"]]["source_location"])
        repeated = diagnostic.enhanced_feedback(after, history)
        self.assertFalse({x["input_id"] for x in repeated["current_examples"]} &
                         {x["input_id"] for x in repeated["regression_examples"]})

    def test_update_history_accumulates_both_sets_without_mutation_or_reordering(self):
        report = diagnostic.assess(candidate("always_brake"), 12)
        feedback = diagnostic.enhanced_feedback(report, [])
        history = diagnostic.update_history([], feedback)
        saved_history, saved_feedback = deepcopy(history), deepcopy(feedback)
        repaired = diagnostic.enhanced_feedback(diagnostic.assess(candidate(), 12), history)
        updated = diagnostic.update_history(history, repaired)
        self.assertEqual([x["input_id"] for x in updated], [x["input_id"] for x in history])
        self.assertEqual(history, saved_history)
        self.assertEqual(feedback, saved_feedback)
        self.assertTrue(all(x["actual"] in x["allowed_outputs"] for x in updated[:4]))
        updated[0]["facts"]["Halted"] = "changed"
        self.assertEqual(history, saved_history)

    def test_refresh_all_history_detects_regression_after_unsent_repair(self):
        # A historically sent input outside the current representatives must
        # still be refreshed when the four-example history cap omits it.
        data = json.loads(candidate())
        data["step"] = [{"when": "True", "action": "Brake", "next": "Stopped"}]
        broken = diagnostic.assess(json.dumps(data), 12)
        current_ids = {x["input_id"] for x in diagnostic.enhanced_feedback(broken, [])["current_examples"]}
        history = [deepcopy(case) for case in broken["full_cases"]
                   if case["function"] == "step" and case["violations"]
                   and case["input_id"] not in current_ids][:7]
        repaired = diagnostic.assess(candidate(), 12)
        sent = diagnostic.enhanced_feedback(repaired, history)
        self.assertEqual(len(sent["regression_examples"]), 4)
        omitted_id = history[4]["input_id"]
        self.assertNotIn(omitted_id, {x["input_id"] for x in sent["regression_examples"]})
        last_sent = diagnostic.update_history(history, sent)
        before = deepcopy(last_sent)
        refresh = getattr(diagnostic, "refresh_history", None)
        self.assertIsNotNone(refresh, "refresh every previously sent input from the current complete assessment")
        refreshed = refresh(last_sent, repaired)
        self.assertEqual(last_sent, before)
        self.assertEqual([x["input_id"] for x in refreshed], [x["input_id"] for x in history])
        self.assertTrue(all(x["actual"] in x["allowed_outputs"] for x in refreshed))
        # Keep the omitted input first only to expose its classification within
        # the cap; the helper itself must have preserved the original ordering.
        examples = diagnostic.enhanced_feedback(broken, [refreshed[4], *refreshed[:4]])["regression_examples"]
        self.assertEqual(examples[0]["input_id"], omitted_id)
        self.assertEqual(examples[0]["history_status"], "regressed")
        self.assertEqual(refresh(refreshed, diagnostic.assess("broken", 12)), refreshed)

    def test_program_key_uses_ast_preserves_rule_order_and_invalid_raw_bytes(self):
        original = json.loads(candidate())
        whitespace = deepcopy(original)
        whitespace["step"][0]["when"] = "  " + whitespace["step"][0]["when"] + "  "
        self.assertEqual(diagnostic.program_key(json.dumps(original), 12),
                         diagnostic.program_key(json.dumps(whitespace, indent=4, sort_keys=True), 12))
        reordered = deepcopy(original)
        reordered["select"][0], reordered["select"][1] = reordered["select"][1], reordered["select"][0]
        self.assertNotEqual(diagnostic.program_key(json.dumps(original), 12),
                            diagnostic.program_key(json.dumps(reordered), 12))
        self.assertEqual(diagnostic.program_key("not json", 12), diagnostic.program_key("not json", 12))
        self.assertNotEqual(diagnostic.program_key("not json", 12), diagnostic.program_key("not json ", 12))

    def test_invalid_text_has_no_fabricated_full_domain_or_history_evaluations(self):
        report = diagnostic.assess("broken", 12)
        self.assertEqual(report["full_cases"], [])
        self.assertEqual(report["checked_inputs"], 0)
        feedback = diagnostic.enhanced_feedback(report, [])
        self.assertEqual(feedback["stage"], "parse")
        self.assertEqual(feedback["current_examples"], [])
        self.assertEqual(feedback["regression_examples"], [])
        self.assertTrue(feedback["parse_error"])

    def test_unknown_profile_limits_are_rejected(self):
        for limit in (0, 9, 13, True, "12"):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                diagnostic.assess(candidate(), limit)


if __name__ == "__main__":
    unittest.main()
