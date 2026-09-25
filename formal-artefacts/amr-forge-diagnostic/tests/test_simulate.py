"""Offline unit fixtures only: no live directory, credentials, or plant run."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import runner


class PhysicsAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = HERE / 'simulate.py'
        cls.adapter = None
        if path.exists():
            spec = importlib.util.spec_from_file_location('forge_physics_test_adapter', path)
            cls.adapter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.adapter)

    def setUp(self):
        self.assertIsNotNone(self.adapter, 'conditional physics adapter must exist')

    def fixture(self, folder):
        """A real offline runner ledger; never relabel it as live."""
        source = (HERE.parent / 'amr-supervisor/candidates/authored_reference.json').read_text()

        def worker(key, attempt):
            runner.write_json(attempt / 'dispatch.json', {'fixture': True})
            runner.write_json(attempt / 'http-body.bin', {
                'model': 'deepseek-flash', 'choices': [
                    {'finish_reason': 'stop', 'message': {'content': source}}],
                'usage': {'prompt_tokens': 2000, 'completion_tokens': 300}})
            return {'status': 'received', 'http_status': 200}

        run = Path(folder) / 'OFFLINE_UNIT_FIXTURE'
        result = runner.execute('not-a-credential', run=run, fixture=True, worker=worker)
        return run, result

    def test_offline_result_cannot_create_physics_output(self):
        with tempfile.TemporaryDirectory() as folder:
            run, _ = self.fixture(folder)
            output = Path(folder) / 'must-not-exist'
            with self.assertRaisesRegex(ValueError, 'live'):
                self.adapter.execute(run, output)
            self.assertFalse(output.exists())

    def test_incomplete_protocol_cannot_select_earlier_acceptance(self):
        with tempfile.TemporaryDirectory() as folder:
            run = Path(folder)
            runner.write_json(run / 'result.json', {
                'mode': 'live', 'stop': 'payload_limit_stop',
                'selected_for_exploratory_physics': {'condition': 'D8-O'}})
            with self.assertRaisesRegex(ValueError, 'protocol_complete'):
                self.adapter.verify_live_selection(run)

    def test_all_four_conditions_must_be_terminal(self):
        with tempfile.TemporaryDirectory() as folder:
            _, result = self.fixture(folder)
            for change in ('missing', 'unfinished', 'fatal'):
                altered = deepcopy(result)
                if change == 'missing':
                    del altered['conditions']['D12-F']
                else:
                    altered['conditions']['D12-F']['stop'] = None if change == 'unfinished' else 'timeout'
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'terminal'):
                    self.adapter.selected_record(altered)

    def test_selection_cannot_skip_first_accepted_condition_or_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            _, result = self.fixture(folder)
            self.assertEqual(self.adapter.selected_record(result)['condition'], 'D8-O')
            for change in ('condition', 'repair'):
                altered = deepcopy(result)
                if change == 'condition':
                    altered['selected_for_exploratory_physics']['condition'] = 'D12-O'
                else:
                    altered['selected_for_exploratory_physics']['repair'] = 2
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'selection'):
                    self.adapter.selected_record(altered)

    def test_complete_offline_evidence_can_be_checked_without_deployment(self):
        with tempfile.TemporaryDirectory() as folder:
            run, result = self.fixture(folder)
            raw, report = self.adapter.verify_evidence(run, result)
            self.assertEqual(raw, (run / 'attempts/001/response.bin').read_bytes())
            self.assertTrue(report['accepted'])
            self.assertEqual(report['checked_inputs'], 1824)
            self.assertEqual(report['profile_id'], 'amr-forge-diagnostic-rules8/v1')
            self.assertEqual(result['mode'], 'offline-fixture')

    def test_modified_response_fails_evidence_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            run, result = self.fixture(folder)
            selected = run / result['selected_for_exploratory_physics']['response_path']
            selected.write_bytes(selected.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'evidence'):
                self.adapter.verify_evidence(run, result)

    def test_frozen_input_change_fails_even_with_updated_local_ledger_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            run, result = self.fixture(folder)
            frozen = runner.read_json(run / 'frozen-inputs.json')
            frozen['formal-artefacts/amr-supervisor/closed_loop.py'] = '0' * 64
            (run / 'frozen-inputs.json').write_bytes(runner.json_bytes(frozen))
            setup = runner.read_json(run / 'setup-sha256.json')
            setup['frozen-inputs.json'] = runner.sha(run / 'frozen-inputs.json')
            (run / 'setup-sha256.json').write_bytes(runner.json_bytes(setup))
            manifest = runner.inventory(run)
            del manifest['evidence-sha256.json']
            (run / 'evidence-sha256.json').write_bytes(runner.json_bytes(manifest))
            with self.assertRaisesRegex(RuntimeError, 'frozen diagnostic dependency changed'):
                self.adapter.verify_evidence(run, result)

    def test_twelve_rule_adapter_preserves_frozen_eight_rule_imports(self):
        import language
        import assurance
        frozen_parse, frozen_assess = language.parse_program, assurance.assess_source
        source = json.loads((HERE.parent / 'amr-supervisor/candidates/authored_reference.json').read_text())
        while len(source['step']) < 12:
            source['step'].append({'when': 'False', 'action': 'Brake', 'next': 'BrakeRequested'})
        text = json.dumps(source)
        adapted, provenance = self.adapter.load_physics(12)
        supervisor = adapted.SourceSupervisor(text)
        self.assertTrue(supervisor.assessment['accepted'])
        self.assertEqual(len(supervisor.program.step), 12)
        self.assertIs(language.parse_program, frozen_parse)
        self.assertIs(assurance.assess_source, frozen_assess)
        with self.assertRaises(ValueError):
            frozen_parse(text)
        eight, _ = self.adapter.load_physics(8)
        with self.assertRaises(ValueError):
            eight.SourceSupervisor(text)
        self.assertEqual(provenance['adaptation'], 'only language and assurance imports made package-relative')
        self.assertEqual(provenance['original_sha256'], runner.sha(HERE.parent / 'amr-supervisor/closed_loop.py'))
        self.assertEqual(adapted.assess_interval.__module__, 'simulation')


if __name__ == '__main__':
    unittest.main()
