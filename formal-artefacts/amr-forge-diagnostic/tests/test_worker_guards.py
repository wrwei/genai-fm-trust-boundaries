"""Offline worker preflight checks: the sole POST helper is always replaced.

Fixtures may declare live protocol metadata to exercise that gate, but never
call execute(), subprocess workers, credentials, or a real HTTP opener.
"""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))


class WorkerGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = importlib.import_module('runner')
        cls.seed_states = cls.r.initial_states()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / 'guard-fixture'
        self.addCleanup(patch.stopall)
        patch.object(self.r, 'RUN', self.run).start()
        # Keep the actual seed assessment, but avoid repeatedly enumerating its
        # domain: these checks exercise worker preflight, not the assessor.
        patch.object(self.r, 'initial_states',
                     side_effect=lambda: deepcopy(self.seed_states)).start()
        self.post = patch.object(self.r.smoke, 'network_child').start()
        self.credentials = patch.object(
            self.r.smoke, 'read_key', side_effect=AssertionError('credential access forbidden')).start()
        self.http = patch.object(
            self.r.smoke.urllib.request, 'build_opener',
            side_effect=AssertionError('HTTP access forbidden')).start()
        self.r.initialize(self.run, fixture=False)
        self.attempt = self.run / 'attempts' / '001'
        self.attempt.mkdir()
        prompt, feedback = self.r.prompt_for(self.seed_states['D8-O'])
        self.r.write_json(self.attempt / 'request.json', {'condition': 'D8-O', 'repair': 1})
        self.r.write_json(self.attempt / 'feedback.json', feedback)
        self.r.write_json(self.attempt / 'http-request.json', self.r.smoke.payload_for(prompt))
        (self.attempt / 'prompt.txt').write_bytes(prompt.encode('utf-8'))
        self.r.write_json(self.attempt / 'preflight.json', {'max_posts':1, 'retries':0,
            'payload_sha256':self.r.sha(self.attempt / 'http-request.json')})
        self.r.write_json(self.attempt / 'dispatch-intent.json', {'max_posts':1, 'retries':0})

    def tearDown(self):
        self.credentials.assert_not_called()
        self.http.assert_not_called()

    def overwrite_json(self, path, value):
        Path(path).write_bytes(self.r.json_bytes(value))

    def assert_rejected(self, error=RuntimeError, attempt=None):
        with self.assertRaises(error):
            self.r.network_child('not-a-credential', attempt or self.attempt)
        self.post.assert_not_called()

    def test_valid_exact_payload_reaches_stub_once_and_claim_blocks_second_call(self):
        self.r.network_child('not-a-credential', self.attempt)
        self.post.assert_called_once_with('not-a-credential', self.attempt.resolve())
        self.assertTrue((self.attempt / 'worker-claim.json').exists())
        with self.assertRaises(FileExistsError):
            self.r.network_child('not-a-credential', self.attempt)
        self.post.assert_called_once()

    def test_wrong_path_number_and_call_ceiling_fail_before_claim(self):
        for path in (self.run / '001', self.run / 'attempts' / '1',
                     self.run / 'attempts' / '000', self.run / 'attempts' / '017',
                     self.run / 'attempts' / 'other'):
            with self.subTest(path=str(path)):
                self.assert_rejected(attempt=path)
        self.assertFalse((self.attempt / 'worker-claim.json').exists())

    def test_changed_payload_is_rejected_before_post(self):
        payload = self.r.read_json(self.attempt / 'http-request.json')
        payload['model'] = 'unexpected-model'
        self.overwrite_json(self.attempt / 'http-request.json', payload)
        self.assert_rejected()

    def test_changed_prompt_is_rejected_before_post(self):
        with (self.attempt / 'prompt.txt').open('ab') as stream:
            stream.write(b'\nadditional instruction')
        self.assert_rejected()

    def test_changed_feedback_is_rejected_before_post(self):
        feedback = self.r.read_json(self.attempt / 'feedback.json')
        feedback['checked_inputs'] = 0
        self.overwrite_json(self.attempt / 'feedback.json', feedback)
        self.assert_rejected()

    def test_out_of_order_condition_is_rejected_before_post(self):
        self.overwrite_json(self.attempt / 'request.json', {'condition': 'D12-O', 'repair': 1})
        self.assert_rejected()

    def test_out_of_order_attempt_number_is_rejected_before_post(self):
        attempt = self.run / 'attempts' / '002'
        attempt.mkdir()
        self.assert_rejected(attempt=attempt)

    def test_changed_preflight_digest_is_rejected_before_post(self):
        preflight = self.r.read_json(self.attempt / 'preflight.json')
        preflight['payload_sha256'] = '0' * 64
        self.overwrite_json(self.attempt / 'preflight.json', preflight)
        self.assert_rejected()

    def test_changed_dispatch_limit_is_rejected_before_post(self):
        self.overwrite_json(self.attempt / 'dispatch-intent.json', {'max_posts':2, 'retries':0})
        self.assert_rejected()

    def test_dependency_hash_drift_is_rejected_before_post(self):
        manifest_path = self.run / 'frozen-inputs.json'
        manifest = self.r.read_json(manifest_path)
        manifest[next(iter(manifest))] = '0' * 64
        self.overwrite_json(manifest_path, manifest)
        # Preserve the outer setup hash to isolate the inner dependency check;
        # no repository source or historical evidence is modified.
        setup_path = self.run / 'setup-sha256.json'
        setup = self.r.read_json(setup_path)
        setup['frozen-inputs.json'] = self.r.sha(manifest_path)
        self.overwrite_json(setup_path, setup)
        self.assert_rejected()

    def test_setup_hash_drift_is_rejected_before_post(self):
        with (self.run / 'starting-response.bin').open('ab') as stream:
            stream.write(b' ')
        self.assert_rejected()

    def test_finished_run_is_rejected_before_claim(self):
        self.r.write_json(self.run / 'result.json', {'fixture_finished': True})
        self.assert_rejected()
        self.assertFalse((self.attempt / 'worker-claim.json').exists())

    def test_fixture_mode_is_rejected_before_claim(self):
        protocol = self.r.read_json(self.run / 'protocol.json')
        protocol['mode'] = 'offline-fixture'
        self.overwrite_json(self.run / 'protocol.json', protocol)
        self.assert_rejected()
        self.assertFalse((self.attempt / 'worker-claim.json').exists())

    def test_prior_fatal_record_is_rejected_before_post(self):
        attempt = self.run / 'attempts' / '002'
        attempt.mkdir()
        with patch.object(self.r, 'replay', return_value=(
                deepcopy(self.seed_states), [{'fatal': 'timeout', 'usage_summary': None}])):
            self.assert_rejected(attempt=attempt)


if __name__ == '__main__':
    unittest.main()
