"""End-to-end recorder rehearsal; all responses are historical fixture bytes."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))


class RehearsalTest(unittest.TestCase):
    def test_six_chains_preserve_failures_and_never_become_live_samples(self):
        self.assertTrue((HERE / 'rehearse.py').is_file(), 'rehearse.py is not implemented')
        from rehearse import run_rehearsal
        with tempfile.TemporaryDirectory(prefix='amr-fixture-rehearsal-') as directory:
            result = run_rehearsal(Path(directory) / 'run')
            self.assertEqual(result['record_mode'], 'fixture')
            self.assertEqual(result['live_model_samples'], 0)
            self.assertEqual(result['initial_responses_recorded'], 6)
            self.assertEqual(result['total_recorded_attempts'], 11)
            self.assertEqual(result['repairs_recorded'], 5)
            self.assertEqual(result['initial_accepted'], 1)
            self.assertEqual(result['eventually_accepted'], 4)
            self.assertEqual(result['invalid_utf8'], 1)
            self.assertEqual(result['infrastructure_failures'], 1)
            self.assertEqual(result['missing_input_token_count'], 11)
            self.assertEqual(result['missing_output_token_count'], 11)
            self.assertTrue(result['complete'])
            self.assertEqual(result['selected_candidate']['sample_id'], 'P1-R1')
            record_files = sorted((Path(directory) / 'run' / 'records').glob('*/record.json'))
            self.assertEqual(len(record_files), 11)
            rows = [json.loads(p.read_text(encoding='utf-8')) for p in record_files]
            fences = next(row for row in rows if row['sample_id'] == 'P3-R1' and row['attempt_index'] == 0)
            self.assertFalse(fences['assessment']['parse_pass'])
            exhausted = [row for row in rows if row['sample_id'] == 'P3-R2']
            self.assertEqual(len(exhausted), 3)
            self.assertFalse(any(row['accepted'] for row in exhausted))


if __name__ == '__main__':
    unittest.main()
