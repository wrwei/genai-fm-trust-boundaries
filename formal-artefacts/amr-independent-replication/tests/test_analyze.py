"""Focused offline checks for fatal-batch analysis; no credentials or network."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('replication_analyze_test', HERE/'analyze.py')
a = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = a
spec.loader.exec_module(a)


class AnalyzeFatalTests(unittest.TestCase):
    def received_worker(self, key, attempt):
        self.assertEqual(key, 'not-a-credential')
        a.r.write_json(attempt/'dispatch.json', {'fixture':True})
        a.r.write_json(attempt/'http-body.bin', {
            'model':'deepseek-flash', 'system_fingerprint':'fixture',
            'choices':[{'finish_reason':'stop', 'message':{'content':'{}'}}],
            'usage':{'prompt_tokens':2000, 'completion_tokens':300,
                     'completion_tokens_details':{'reasoning_tokens':250}}})
        return {'status':'received', 'http_status':200}

    def analyze_fixture(self, run, root):
        output = root/'derived'
        output.mkdir()
        return a.analyze_run(run, output=output, physical=root/'absent-closed-loop')

    def test_assessment_error_overrides_successful_transport_without_counts(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                a.r.d, 'assess', side_effect=RuntimeError('offline fixture')):
            root, run = Path(tmp), Path(tmp)/'run'
            result = a.r.execute('not-a-credential', run=run,
                                 worker=self.received_worker, fixture=True)
            self.assertEqual(result['stop'], 'assessment_error')
            analysis = self.analyze_fixture(run, root)
            self.assertEqual(analysis['stop'], 'assessment_error')
            self.assertEqual(len(analysis['calls']), 1)
            self.assertEqual(analysis['calls'][0]['fatal'], 'assessment_error')
            self.assertFalse(analysis['calls'][0]['accepted'])
            self.assertIsNone(analysis['calls'][0]['rule_counts'])

    def test_pre_post_transport_failure_has_attempt_without_dispatch(self):
        def fail_before_post(key, attempt):
            self.assertEqual(key, 'not-a-credential')
            return {'status':'transport_error', 'http_status':None,
                    'error_type':'MissingCredentialFixture'}

        with tempfile.TemporaryDirectory() as tmp:
            root, run = Path(tmp), Path(tmp)/'run'
            result = a.r.execute('not-a-credential', run=run,
                                 worker=fail_before_post, fixture=True)
            self.assertEqual(result['new_calls'], 1)
            self.assertEqual(result['network_dispatches'], 0)
            analysis = self.analyze_fixture(run, root)
            self.assertEqual(analysis['stop'], 'transport_error')
            self.assertEqual(len(analysis['calls']), 1)
            self.assertEqual(analysis['calls'][0]['fatal'], 'transport_error')


if __name__ == '__main__':
    unittest.main()
