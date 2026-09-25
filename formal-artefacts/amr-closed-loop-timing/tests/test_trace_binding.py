import copy
import gzip
import json
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
try:
    import trace_binding
except ImportError:
    trace_binding = None


class TraceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        retained = BASE.parent/'amr-runtime-binding/evidence/run-2026-09-22'
        with gzip.open(retained/'none.jsonl.gz', 'rt', encoding='utf-8') as stream:
            cls.rows = [json.loads(line) for line in stream]
        cls.params = json.loads((retained/'effective-parameters.json').read_bytes())

    def setUp(self):
        self.assertIsNotNone(trace_binding, 'trace_binding has not been implemented')

    def test_retained_trace_meets_stronger_milestone_bounds(self):
        report = trace_binding.audit_rows(self.rows, self.params)
        self.assertEqual(report['grant_order'], ['A','B'])
        self.assertAlmostEqual(report['robots']['A']['clear_crossing'], 27.369305799152382)
        self.assertAlmostEqual(report['robots']['A']['arrival'], 31.381854249492644)
        self.assertEqual(report['robots']['A']['finish'], 32.9)
        self.assertLessEqual(report['maxima_ticks']['start'], 163)
        self.assertLessEqual(report['maxima_ticks']['release'], 9)
        self.assertLessEqual(report['maxima_ticks']['finish'], 169)

    def test_late_proceed_application_breaks_start_bound(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r['kind']=='command_applied'
                   and r['command']['intent']=='Proceed' and r['command']['robot']=='A')
        row['time'] = 1.69
        rows.sort(key=lambda r:r['time'])
        with self.assertRaisesRegex(AssertionError, 'start bound'):
            trace_binding.audit_rows(rows, self.params)

    def test_late_release_breaks_clearance_response_bound(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r['kind']=='release' and r['robot']=='A')
        row['time'] = 27.47
        rows.sort(key=lambda r:r['time'])
        with self.assertRaisesRegex(AssertionError, 'release bound'):
            trace_binding.audit_rows(rows, self.params)

    def test_missing_goal_brake_application_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows.remove(next(r for r in rows if r['kind']=='command_applied'
                         and r['command']['intent']=='Brake' and r['command']['robot']=='A'
                         and r['time']>1.))
        with self.assertRaisesRegex(AssertionError, 'Brake application'):
            trace_binding.audit_rows(rows, self.params)

    def test_finish_before_halt_timer_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r['kind']=='complete' and r['robot']=='A')
        row['time'] = 32.85
        rows.sort(key=lambda r:r['time'])
        with self.assertRaisesRegex(AssertionError, 'halt timer'):
            trace_binding.audit_rows(rows, self.params)


if __name__ == '__main__':
    unittest.main()
