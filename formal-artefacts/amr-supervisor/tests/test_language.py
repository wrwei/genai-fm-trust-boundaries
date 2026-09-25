"""Behavioral tests for the restricted source interpreter."""
import dataclasses
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    import language
except ModuleNotFoundError:
    language = None


class LanguageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(language, "restricted language implementation is missing")

    def source(self, select=None, step=None):
        return json.dumps({"schema": "amr-supervisor/v1",
            "select": select if select is not None else [{"when": "True", "action": "Defer"}],
            "step": step if step is not None else [{"when": "True", "action": "Brake", "next": "Stopped"}]})

    def facts(self, names):
        return dict.fromkeys(names, False)

    def test_first_match_and_boolean_precedence(self):
        p = language.parse_program(self.source(select=[
            {"when": "OwnerFree and (RequestA or not RequestB)", "action": "SelectA"},
            {"when": "True", "action": "SelectB"}]))
        facts = self.facts(language.SELECT_FACTS)
        self.assertEqual(language.eval_select(p, facts), "SelectB")
        facts["OwnerFree"] = True
        self.assertEqual(language.eval_select(p, facts), "SelectA")

    def test_non_total_is_parseable_and_unmatched_is_error(self):
        p = language.parse_program(self.source(select=[], step=[]))
        with self.assertRaisesRegex(ValueError, "match"):
            language.eval_select(p, self.facts(language.SELECT_FACTS))
        with self.assertRaisesRegex(ValueError, "match"):
            language.eval_step(p, "Idle", self.facts(language.STEP_FACTS))

    def test_mode_predicates_are_internal(self):
        p = language.parse_program(self.source(step=[
            {"when": "ModeStopped and not ModeIdle", "action": "Resume", "next": "ResumePending"},
            {"when": "True", "action": "Proceed", "next": "Traversing"}]))
        facts = self.facts(language.STEP_FACTS)
        self.assertEqual(language.eval_step(p, "Stopped", facts), ("Resume", "ResumePending"))
        self.assertEqual(language.eval_step(p, "Idle", facts), ("Proceed", "Traversing"))
        facts["ModeStopped"] = True
        with self.assertRaises(ValueError):
            language.eval_step(p, "Idle", facts)

    def test_facts_exact_keys_and_real_bools(self):
        p = language.parse_program(self.source())
        for evaluator, names in [(lambda f: language.eval_select(p, f), language.SELECT_FACTS),
                (lambda f: language.eval_step(p, "Idle", f), language.STEP_FACTS)]:
            for bad in [None, {}, {**self.facts(names), "unexpected": False}]:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    evaluator(bad)
            for value in [0, 1, "False", None]:
                bad = self.facts(names)
                bad[names[0]] = value
                with self.subTest(value=value), self.assertRaises(ValueError):
                    evaluator(bad)
        with self.assertRaises(ValueError):
            language.eval_step(p, "Bogus", self.facts(language.STEP_FACTS))

    def test_rejects_executable_and_non_boolean_syntax(self):
        for expr in ["__import__('os').getcwd()", "OwnerFree.real", "OwnerFree == True",
                "1", "None", "OwnerFree + RequestA", "[True]", "True if OwnerFree else False",
                "Unknown", "ModeIdle", "ObservationUsable", "OwnerFree[0]", "lambda: True"]:
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                language.parse_program(self.source(select=[{"when": expr, "action": "Defer"}]))

    def test_rejects_json_schema_duplicate_keys_and_wrong_enums(self):
        bad = ["[]", "null", "{", self.source().replace('"schema":', '"schema":"x","schema":'),
            self.source().replace('"when":', '"when":"False","when":', 1),
            self.source().replace('amr-supervisor/v1', 'wrong'),
            self.source().replace('"Defer"', '"Brake"'), self.source().replace('"Stopped"', '"Other"'),
            self.source().replace('"Brake"', '"SelectA"'),
            self.source().replace('"True"', 'true', 1),
            self.source().replace('"select":', '"extra":0,"select":'),
            self.source(select=[{"when": "True", "action": "Defer", "next": "Idle"}]),
            self.source(step=[{"when": "True", "action": "Brake"}]),
            self.source(select="bad"), self.source(select=[False]),
            self.source().replace('"Defer"', 'NaN'), self.source().replace('"Defer"', '[]')]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                language.parse_program(value)

    def test_resource_bounds(self):
        for expr in [" " * 513 + "True", "not " * 9 + "True", " or ".join(["OwnerFree"] * 32)]:
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                language.parse_program(self.source(select=[{"when": expr, "action": "Defer"}]))
        with self.assertRaises(ValueError):
            language.parse_program(self.source(select=[{"when": "True", "action": "Defer"}] * 9))
        with self.assertRaises(ValueError):
            language.parse_program(self.source() + " " * (200 * 1024))

    def test_immutable_program_rules_and_expression(self):
        p = language.parse_program(self.source())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            p.schema = "changed"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            p.select[0].action = "SelectA"
        self.assertIsInstance(p.select, tuple)
        self.assertEqual(p.select[0].condition, ("const", True))
        self.assertIsNone(p.select[0].next_mode)


if __name__ == "__main__":
    unittest.main()
