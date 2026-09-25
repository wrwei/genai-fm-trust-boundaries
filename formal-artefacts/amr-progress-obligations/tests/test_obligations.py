import copy
import gzip
import json
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
try:
    import trace_obligations
except ImportError:
    trace_obligations = None


class ObligationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        retained = BASE.parent/'amr-runtime-binding/evidence/run-2026-09-22'
        with gzip.open(retained/'none.jsonl.gz', 'rt', encoding='utf-8') as stream:
            cls.rows = [json.loads(line) for line in stream]
        cls.params = json.loads((retained/'effective-parameters.json').read_bytes())

    def setUp(self):
        self.assertIsNotNone(trace_obligations, 'trace obligations checker is missing')

    def test_retained_nominal_run_meets_local_budgets(self):
        report = trace_obligations.inspect(self.rows, self.params)
        self.assertEqual(report['grant_order'], ['A','B'])
        self.assertEqual(report['last_completion'], 58.9)
        self.assertEqual(report['conditional_two_task_budget'], 70.2)

    def test_missing_controller_opportunity_is_not_silent(self):
        rows = copy.deepcopy(self.rows)
        rows.remove(next(r for r in rows if r['kind']=='source_step' and r['robot']=='A' and r['time']==1.))
        with self.assertRaisesRegex(AssertionError, 'control clock'):
            trace_obligations.inspect(rows, self.params)

    def test_delayed_command_is_not_certified(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r['kind']=='command_applied' and r['command']['intent']=='Proceed')
        row['time'] += 1.
        rows.sort(key=lambda r: r['time'])
        with self.assertRaisesRegex(AssertionError, 'command delivery'):
            trace_obligations.inspect(rows, self.params)

    def test_reported_finish_requires_physical_standstill(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r['kind']=='complete')['actual_speed'] = 1.
        with self.assertRaisesRegex(AssertionError, 'finish physical'):
            trace_obligations.inspect(rows, self.params)

    def test_missing_physical_interval_is_not_silent(self):
        rows = copy.deepcopy(self.rows)
        rows.remove(next(r for r in rows if r['kind']=='motion' and r['time']==2.))
        with self.assertRaisesRegex(AssertionError, 'motion clock'):
            trace_obligations.inspect(rows, self.params)

    def test_missing_due_observation_is_not_silent(self):
        rows = copy.deepcopy(self.rows)
        rows.remove(next(r for r in rows if r['kind']=='observation_received'
                         and r['packet']['robot_id']=='A' and r['time']==1.))
        with self.assertRaisesRegex(AssertionError, 'sensor delivery completeness'):
            trace_obligations.inspect(rows, self.params)

    def test_duplicate_observation_delivery_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        index = next(i for i,r in enumerate(rows) if r['kind']=='observation_received')
        rows.insert(index, copy.deepcopy(rows[index]))
        with self.assertRaisesRegex(AssertionError, 'duplicate sensor delivery'):
            trace_obligations.inspect(rows, self.params)


if __name__ == '__main__':
    unittest.main()
