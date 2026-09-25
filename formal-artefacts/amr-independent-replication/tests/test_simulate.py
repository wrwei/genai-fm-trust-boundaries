"""Offline deployment/mapping tests; no actual model or physical episodes."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]


class ReplicationPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = None
        if (HERE/'simulate.py').exists():
            spec = importlib.util.spec_from_file_location('replication_physics_tests', HERE/'simulate.py')
            cls.sim = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.sim)

    def setUp(self):
        self.assertIsNotNone(self.sim, 'replication physics adapter is absent')

    def fixture(self, folder, two_sources=False):
        r = self.sim.r
        source = (HERE.parent/'amr-supervisor/candidates/authored_reference.json').read_text()
        def worker(key, attempt):
            req = r.read_json(attempt/'request.json')
            text = source + ('\n' if two_sources and req['sample_id'].endswith('R2') else '')
            r.write_json(attempt/'dispatch.json', {'fixture': True})
            r.write_json(attempt/'http-body.bin', {'model': 'deepseek-flash',
                'choices': [{'finish_reason': 'stop', 'message': {'content': text}}],
                'usage': {'prompt_tokens': 2000, 'completion_tokens': 300}})
            return {'status': 'received', 'http_status': 200}
        run = Path(folder)/'offline'
        result = r.execute('not-a-key', run=run, fixture=True, worker=worker)
        return run, result

    def test_duplicates_reuse_physics_but_keep_all_six_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, result = self.fixture(tmp)
            catalog = self.sim.verify_evidence(run, result)
            self.assertEqual(len(catalog), 1)
            self.assertEqual(catalog[0]['selection']['sample_ids'], list(self.sim.r.SAMPLE_IDS))
            self.assertTrue(catalog[0]['assessment']['accepted'])
            plan = self.sim.episode_plan(catalog)
            self.assertEqual(len(plan), 10)
            self.assertEqual(sum(row['source_key'] is None for row in plan), 5)
            out = Path(tmp)/'forbidden'
            with self.assertRaisesRegex(ValueError, 'live'):
                self.sim.execute(run, out)
            self.assertFalse(out.exists())

    def test_two_byte_distinct_sources_have_fifteen_episodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, result = self.fixture(tmp, two_sources=True)
            catalog = self.sim.verify_evidence(run, result)
            self.assertEqual(len(catalog), 2)
            self.assertEqual([x['selection']['representative_sample'] for x in catalog], ['P1-R1','P1-R2'])
            self.assertEqual([len(x['selection']['sample_ids']) for x in catalog], [3,3])
            plan = self.sim.episode_plan(catalog)
            self.assertEqual(len(plan), 15)
            for key in (None, 'source_01', 'source_02'):
                self.assertEqual({x['case'] for x in plan if x['source_key'] == key},
                                 {'normal_A','normal_B','temporary','blackout','permanent'})

    def test_missing_or_reordered_source_mapping_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, result = self.fixture(tmp, two_sources=True)
            for kind in ('missing-sample','wrong-order','wrong-attempt'):
                changed = deepcopy(result)
                if kind == 'missing-sample': changed['selected_sources'][0]['sample_ids'].pop()
                elif kind == 'wrong-order': changed['selected_sources'].reverse()
                else: changed['selected_sources'][0]['first_accepted_attempt'] = 1
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    self.sim.validate_selection(changed, self.sim.r.replay(run)[0], run)

    def test_altered_source_fails_before_deployment(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, result = self.fixture(tmp)
            p = run/result['selected_sources'][0]['response_path']
            p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError, 'evidence'):
                self.sim.verify_evidence(run, result)

    def test_partial_or_fatal_batch_never_selects_physics(self):
        for stop in ('truncated','timeout','payload_limit_stop'):
            with self.subTest(stop=stop), self.assertRaisesRegex(ValueError, 'complete'):
                self.sim.validate_selection({'stop':stop}, {}, HERE/'no-run')

    def test_fixed_physical_oracle_and_profile_are_reused(self):
        physics, _ = self.sim.previous.load_physics(12)
        self.assertEqual(physics.assess_interval.__module__, 'simulation')
        self.assertEqual(physics.assess_source.__module__, '_amr_forge_diagnostic_profiles.rules12.assurance')

    def test_live_protocol_uses_serialized_sample_list_before_evidence_gate(self):
        # Exercise the live configuration boundary without forging live evidence.
        r = self.sim.r
        run = HERE/'nonexistent-live-fixture'
        result = {'mode':'live','protocol_id':'amr-independent-replication/v1'}
        protocol = {'mode':'live','id':result['protocol_id'],
                    'sample_ids':list(r.SAMPLE_IDS),'model_configs':r.CONFIGS}
        def read(path):
            return result if Path(path).name=='result.json' else protocol
        with patch.object(r,'read_json',side_effect=read), \
             patch.object(self.sim,'verify_evidence',return_value='evidence-gate-reached') as verify:
            self.assertEqual(self.sim.verify_live(run),'evidence-gate-reached')
            verify.assert_called_once_with(run,result)


if __name__ == '__main__': unittest.main()
