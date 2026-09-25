"""Independent target behavior, including deliberately defective extractions."""
import importlib
import itertools
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('model'), 'target model is not implemented')
        self.m = importlib.import_module('model')
        self.l = importlib.import_module('language')

    def program(self, select=None, step=None):
        rule = self.l.Rule
        return self.l.Program('amr-supervisor/v1', tuple(select or [rule(('const', True), 'Defer', None)]),
                              tuple(step or [rule(('const', True), 'Proceed', 'Traversing')]))

    def select_facts(self, **changes):
        return dict(dict.fromkeys(self.l.SELECT_FACTS, False), **changes)

    def step_facts(self, **changes):
        return dict(dict.fromkeys(self.l.STEP_FACTS, False), **changes)

    def test_priority_is_encoded_and_omission_exposes_both_enabled_rules(self):
        p = self.program(select=[self.l.Rule(('var', 'RequestA'), 'SelectA', None),
                                 self.l.Rule(('const', True), 'Defer', None)])
        facts = self.select_facts(RequestA=True)
        self.assertEqual(self.l.eval_select(p, facts), 'SelectA')
        self.assertEqual(self.m.model_select(self.m.extract_model(p), facts), ('SelectA',))
        self.assertEqual(self.m.model_select(self.m.extract_model(p, 'omit_priority'), facts), ('SelectA', 'Defer'))

    def test_duplicate_enabled_outcomes_are_not_deduplicated(self):
        p = self.program(select=[self.l.Rule(('const', True), 'Defer', None)] * 2)
        self.assertEqual(self.m.model_select(self.m.extract_model(p, 'omit_priority'), self.select_facts()), ('Defer', 'Defer'))

    def test_modes_are_derived_and_step_priority_preserved(self):
        p = self.program(step=[self.l.Rule(('var', 'ModeStopped'), 'Resume', 'ResumePending'),
                               self.l.Rule(('const', True), 'Proceed', 'Traversing')])
        model = self.m.extract_model(p)
        for mode in self.l.MODES:
            want = (('Resume', 'ResumePending'),) if mode == 'Stopped' else (('Proceed', 'Traversing'),)
            self.assertEqual(self.m.model_step(model, mode, self.step_facts()), want)
        self.assertEqual(self.m.model_step(self.m.extract_model(p, 'omit_priority'), 'Stopped', self.step_facts()),
                         (('Resume', 'ResumePending'), ('Proceed', 'Traversing')))

    def test_nested_boolean_expression_truth_table(self):
        expr = ('and', ('or', ('var', 'RequestA'), ('var', 'RequestB')), ('not', ('var', 'OwnerFree')), ('const', True))
        model = self.m.extract_model(self.program(select=[self.l.Rule(expr, 'SelectA', None), self.l.Rule(('const', True), 'Defer', None)]))
        for a, b, free in itertools.product((False, True), repeat=3):
            self.assertEqual(self.m.model_select(model, self.select_facts(RequestA=a, RequestB=b, OwnerFree=free)),
                             ('SelectA',) if (a or b) and not free else ('Defer',))

    def test_choose_b_fault_only_changes_both_requests(self):
        p = self.program(select=[self.l.Rule(('var', 'RequestA'), 'SelectA', None), self.l.Rule(('const', True), 'Defer', None)])
        model = self.m.extract_model(p, 'choose_b_when_both')
        for a, b in itertools.product((False, True), repeat=2):
            self.assertEqual(self.m.model_select(model, self.select_facts(RequestA=a, RequestB=b)),
                             ('SelectB',) if a and b else ('SelectA',) if a else ('Defer',))

    def test_observation_fault_flips_positive_and_negated_occurrences(self):
        for expr, original_when_true in [(('var', 'ObservationUsable'), True), (('not', ('var', 'ObservationUsable')), False)]:
            p = self.program(step=[self.l.Rule(expr, 'Brake', 'Stopped'), self.l.Rule(('const', True), 'Proceed', 'Traversing')])
            for observed in (False, True):
                facts = self.step_facts(ObservationUsable=observed)
                normal = self.m.model_step(self.m.extract_model(p), 'Idle', facts)
                faulty = self.m.model_step(self.m.extract_model(p, 'invert_observation_tests'), 'Idle', facts)
                self.assertEqual(normal, (('Brake', 'Stopped'),) if observed == original_when_true else (('Proceed', 'Traversing'),))
                self.assertEqual(faulty, (('Proceed', 'Traversing'),) if observed == original_when_true else (('Brake', 'Stopped'),))

    def test_strict_inputs_and_unknown_fault_rejected(self):
        model = self.m.extract_model(self.program())
        for facts in [{}, self.select_facts(RequestA=1), dict(self.select_facts(), Extra=False)]:
            with self.assertRaises(ValueError):
                self.m.model_select(model, facts)
        for facts in [{}, self.step_facts(Halted=0), dict(self.step_facts(), ModeIdle=True)]:
            with self.assertRaises(ValueError):
                self.m.model_step(model, 'Idle', facts)
        with self.assertRaises(ValueError):
            self.m.model_step(model, 'NotAMode', self.step_facts())
        with self.assertRaises(ValueError):
            self.m.extract_model(self.program(), 'unknown')

    def test_no_enabled_rule_is_empty_relation_and_serialization_is_detached(self):
        p = self.program(select=[self.l.Rule(('const', False), 'SelectA', None)])
        model = self.m.extract_model(p)
        self.assertEqual(self.m.model_select(model, self.select_facts()), ())
        evidence = model.to_dict()
        json.dumps(evidence)
        evidence['select'].clear()
        self.assertTrue(model.to_dict()['select'])
        with self.assertRaises(AttributeError):
            model.select = ()


if __name__ == '__main__':
    unittest.main()
