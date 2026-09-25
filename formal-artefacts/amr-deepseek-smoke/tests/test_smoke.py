import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import smoke


class SmokeTests(unittest.TestCase):
    def test_key_loader_is_local_and_does_not_echo_malformed_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'key.env'
            path.write_text('# local only\nDEEPSEEK_API_KEY="sk-fictional-unittest-only"\n', encoding='utf-8')
            self.assertEqual(smoke.read_key(path), 'sk-fictional-unittest-only')
            path.write_text('DEEPSEEK_API_KEY=secret with spaces', encoding='utf-8')
            with self.assertRaises(ValueError) as caught:
                smoke.read_key(path)
            self.assertNotIn('secret', str(caught.exception))

    def test_preparation_integrity_rejects_changed_input(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'prepared-input.txt'
            source.write_bytes(b'prepared input')
            manifest = {'input_sha256': {'prepared-input.txt': hashlib.sha256(source.read_bytes()).hexdigest()}}
            (root / 'preparation-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            with mock.patch.object(smoke, 'ROOT', root), mock.patch.object(smoke, 'BUNDLE', root):
                self.assertEqual(smoke.verify_preparation(), 1)
                source.write_bytes(b'changed input')
                with self.assertRaisesRegex(RuntimeError, 'frozen preparation input changed'):
                    smoke.verify_preparation()

    def test_payload_has_one_prompt_and_explicit_caps(self):
        payload = smoke.payload_for('unchanged prompt\r\n')
        self.assertEqual(payload['messages'], [{'role': 'user', 'content': 'unchanged prompt\r\n'}])
        self.assertEqual(payload['thinking'], {'type': 'disabled'})
        self.assertEqual(payload['max_tokens'], 2048)
        self.assertFalse(payload['stream'])
        self.assertNotIn('tools', payload)
        self.assertNotIn('response_format', payload)

    def test_usage_summary_and_invalid_usage(self):
        summary = smoke.usage_summary({'prompt_tokens': 1000, 'completion_tokens': 100,
                                 'prompt_cache_hit_tokens': 200, 'prompt_cache_miss_tokens': 800})
        self.assertEqual(summary, {'input_tokens': 1000, 'output_tokens': 100,
                                   'cache_hit_tokens': 200, 'cache_miss_tokens': 800})
        self.assertIsNone(smoke.usage_summary({'prompt_tokens': True, 'completion_tokens': 100}))
        self.assertIsNone(smoke.usage_summary({'prompt_tokens': 10, 'completion_tokens': -1}))
        self.assertIsNone(smoke.usage_summary({'prompt_tokens': 10, 'completion_tokens': 1,
                                          'prompt_cache_hit_tokens': 11}))

    @mock.patch.object(smoke, 'verify_preparation', return_value=0)
    def test_rejected_raw_source_recorded_once_without_retry(self, verify_preparation):
        calls = []
        raw_source = '```json\n{}\n```'
        def fake_worker(key, run):
            calls.append(1)
            envelope = {'id': 'offline-unit-test', 'model': 'deepseek-flash',
                        'choices': [{'finish_reason': 'stop', 'message': {'content': raw_source}}],
                        'usage': {'prompt_tokens': 1000, 'completion_tokens': 100}}
            (run / 'http-body.bin').write_bytes(json.dumps(envelope).encode())
            return {'status': 'received', 'http_status': 200}
        with tempfile.TemporaryDirectory() as folder:
            run = Path(folder) / 'run'
            result = smoke.execute(Path('unused.env'), run=run, worker=fake_worker)
            self.assertEqual(calls, [1])
            self.assertEqual(result['trial_summary']['initial_responses_recorded'], 1)
            self.assertFalse(result['trial_summary']['complete'])
            self.assertIsNone(result['trial_summary']['selected_candidate'])
            records = list((run / 'records').glob('*/response.bin'))
            self.assertEqual(records[0].read_bytes(), raw_source.encode())
            with self.assertRaises(FileExistsError):
                smoke.execute(Path('unused.env'), run=run, worker=fake_worker)
            self.assertEqual(len(calls), 1)

    @mock.patch.object(smoke, 'verify_preparation', return_value=0)
    def test_timeout_is_terminal_no_retry_and_missing_usage_recorded(self, verify_preparation):
        calls = []
        def timeout_worker(key, run):
            calls.append(1)
            raise subprocess.TimeoutExpired('offline test', 90)
        with tempfile.TemporaryDirectory() as folder:
            result = smoke.execute(Path('unused.env'), run=Path(folder) / 'run', worker=timeout_worker)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result['transport']['status'], 'timeout')
            self.assertIsNone(result['usage_summary'])
            self.assertEqual(result['trial_summary']['missing_input_token_count'], 1)
            self.assertEqual(result['trial_summary']['missing_output_token_count'], 1)
            self.assertEqual(result['trial_summary']['infrastructure_failures'], 1)


if __name__ == '__main__':
    unittest.main()
