"""Prevent textual binding errors and normalization from hiding rejection."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('snapshot'):
    import snapshot
else:
    snapshot = None


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(snapshot, 'concrete source/HOL binding exporter is missing')

    def test_nary_shape_and_instruction_order_survive_export(self):
        self.assertEqual(snapshot.expr_term(('and', ('var', 'OwnerFree'), ('not', ('const', False)), ('const', True))),
                         '(BAnd [(Atom 0),(BNot (Lit False)),(Lit True)])')
        self.assertEqual(snapshot.code_term((('LOAD', 'OwnerFree'), ('NOT',), ('NOT',), ('AND', 2))),
                         '[Load 0,Neg,Neg,Conj 2]')

    def test_unknown_atoms_and_opcodes_are_not_silently_encoded(self):
        with self.assertRaises(ValueError):
            snapshot.expr_term(('var', 'UnapprovedFact'))
        with self.assertRaises(ValueError):
            snapshot.code_term((('RUN', 'shell'),))

    def test_only_no_matching_exceptions_become_none(self):
        empty = snapshot.language.Program('amr-supervisor/v1', (), ())
        facts = dict.fromkeys(snapshot.language.SELECT_FACTS, False)
        self.assertIsNone(snapshot.source_observation(snapshot.language.eval_select, empty, facts))
        with self.assertRaises(ValueError):
            snapshot.source_observation(snapshot.language.eval_select, empty, {})

    def test_all_historical_identities_and_selected_raw_are_bound(self):
        record = snapshot.collect()
        self.assertEqual(len(record['samples']), 6)
        self.assertEqual(len(record['artifacts']), 5)
        self.assertEqual(sum(a['selected'] for a in record['artifacts']), 1)
        self.assertEqual(record['selected_source_sha256'],
                         '9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd')

    def test_probe_values_are_bound_to_both_python_interpreters(self):
        record = snapshot.collect()
        self.assertTrue(all('source_values' in e and 'target_values' in e for e in record['expressions']),
                        'independent source/target interpreter observations missing')
        self.assertEqual(len(record['environments']), 8)
        for e in record['expressions']:
            self.assertEqual(len(e['source_values']), 8)
            self.assertEqual(e['source_values'], e['target_values'])


if __name__ == '__main__':
    unittest.main()
