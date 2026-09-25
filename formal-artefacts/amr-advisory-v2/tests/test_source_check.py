"""Catch policy/correspondence confusion and accidental byte rewriting."""
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
spec = importlib.util.find_spec('source_check')
if spec:
    import source_check as sc
else:
    sc = None


class SourceCheckTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(sc, 'v2 finite policy checker is not implemented')

    def test_literal_selection_cases(self):
        cases = [((1,1,1,0,1),'SelectB'), ((1,1,1,0,0),'SelectA'),
                 ((1,1,1,1,1),'SelectA'), ((0,1,1,0,1),'Defer'),
                 ((1,1,0,0,1),'SelectA'), ((1,0,1,1,0),'SelectB'),
                 ((1,0,0,1,0),'Defer')]
        for bits, want in cases:
            self.assertEqual(sc.required_select(dict(zip(sc.language.SELECT_FACTS, map(bool,bits)))), want)

    def test_revalidate_all_raw_sources_without_reclassification(self):
        results = [sc.assess_bytes(p.read_bytes()) for p in sc.historical_sources()]
        self.assertEqual(len(results), 6)
        self.assertTrue(all(r['old_policy_pass'] for r in results))
        self.assertTrue(any(not r['v2_source_pass'] for r in results))
        self.assertTrue(any(r['v2_accepted'] for r in results))
        self.assertTrue(all(r['checked_inputs']==1824 for r in results))

    def test_faulty_model_can_pass_function_while_source_differs(self):
        raw = sc.historical_sources()[0].read_bytes()
        correct = sc.assess_bytes(raw)
        faulty = sc.assess_bytes(raw, fault='honor_b_model_only')
        self.assertEqual(correct['source_sha256'], faulty['source_sha256'])
        self.assertTrue(correct['correspondence_pass'])
        self.assertFalse(faulty['correspondence_pass'])
        self.assertTrue(faulty['old_model_policy_pass'])
        self.assertTrue(faulty['v2_model_pass'])
        self.assertFalse(faulty['v2_source_pass'])
        self.assertFalse(faulty['v2_accepted'])

    def test_exact_candidate_bytes_and_complete_decision_domain(self):
        import hashlib
        raw = sc.historical_sources()[2].read_bytes()
        r = sc.assess_bytes(raw)
        self.assertEqual(r['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(len(r['cases']), 1824)
        self.assertEqual(sum(c['kind']=='select' for c in r['cases']), 32)

    def test_relative_output_and_deduplication_preserve_every_sample(self):
        import tempfile
        import os
        with tempfile.TemporaryDirectory(dir=sc.HERE) as folder:
            relative=Path(os.path.relpath(Path(folder)/'new-run',Path.cwd()))
            result=sc.execute(relative)
            self.assertEqual(len(result['samples']),6)
            self.assertEqual(len(result['distinct_sources']),5)
            self.assertEqual(result['selected']['source_sha256'],result['samples'][2]['source_sha256'])
            for item in result['distinct_sources']:
                import hashlib
                raw=(sc.ROOT/item['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),item['source_sha256'])


if __name__ == '__main__':
    unittest.main()
