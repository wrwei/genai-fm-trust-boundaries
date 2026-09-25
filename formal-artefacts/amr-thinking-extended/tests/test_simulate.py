"""Bounded physical deployment gates, never credentials or network."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]


class PhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = None
        if (HERE/'simulate.py').exists():
            spec = importlib.util.spec_from_file_location('extended_physics_test', HERE/'simulate.py')
            cls.sim = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.sim)

    def setUp(self):
        self.assertIsNotNone(self.sim, 'extended physics adapter is absent')

    def fixture(self, folder):
        r = self.sim.r
        source = (HERE.parent/'amr-supervisor/candidates/authored_reference.json').read_text()
        def worker(key, attempt):
            r.write_json(attempt/'dispatch.json', {'fixture':True})
            r.write_json(attempt/'http-body.bin', {
                'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':source}}],
                'usage':{'prompt_tokens':2000,'completion_tokens':300}})
            return {'status':'received','http_status':200}
        run = Path(folder)/'offline'
        result = r.execute('not-a-credential', run=run, fixture=True, worker=worker)
        return run,result

    def test_offline_fixture_can_be_audited_but_never_deployed(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,result = self.fixture(tmp)
            raw,report = self.sim.verify_evidence(run,result)
            self.assertTrue(report['accepted'])
            self.assertEqual(report['checked_inputs'],1824)
            self.assertEqual(raw,(run/'attempts/001/response.bin').read_bytes())
            out = Path(tmp)/'forbidden-physics'
            with self.assertRaisesRegex(ValueError,'live'):
                self.sim.execute(run,out)
            self.assertFalse(out.exists())

    def test_selection_requires_both_terminal_conditions_and_fixed_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            _,result = self.fixture(tmp)
            self.assertEqual(self.sim.selected_record(result)['condition'],'N64-F')
            for change in ('missing','pending','wrong-selection','wrong-repair'):
                obj=deepcopy(result)
                if change=='missing': del obj['conditions']['T64-F']
                elif change=='pending': obj['conditions']['T64-F']['stop']=None
                elif change=='wrong-selection': obj['selected_for_exploratory_physics']['condition']='T64-F'
                else: obj['selected_for_exploratory_physics']['repair']=2
                with self.subTest(change=change),self.assertRaises(ValueError):
                    self.sim.selected_record(obj)

    def test_tampered_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run,result = self.fixture(tmp)
            p=run/result['selected_for_exploratory_physics']['response_path']
            p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'evidence'):
                self.sim.verify_evidence(run,result)

    def test_partial_batch_does_not_deploy_earlier_success(self):
        with self.assertRaisesRegex(ValueError,'complete'):
            self.sim.selected_record({'stop':'timeout','conditions':{}})

    def test_physics_reuses_fixed_profile_and_independent_oracle(self):
        module,_=self.sim.previous.load_physics(12)
        self.assertEqual(module.assess_interval.__module__,'simulation')
        self.assertEqual(module.assess_source.__module__,'_amr_forge_diagnostic_profiles.rules12.assurance')


if __name__=='__main__': unittest.main()
