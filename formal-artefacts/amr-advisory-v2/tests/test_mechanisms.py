import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('run_mechanisms'):
    from run_mechanisms import experiments
else:
    experiments=None


class MechanismTests(unittest.TestCase):
    def test_faults_are_observed_and_positive_controls_use_source(self):
        self.assertIsNotNone(experiments,'mechanism experiment not implemented')
        r=experiments()
        for key in ('E3a','E3b'):
            self.assertEqual(r[key]['correct']['violations'],0)
            self.assertEqual(r[key]['faulty']['violations'],1)
        self.assertEqual(r['E4']['correct']['owner'],'A')
        self.assertIsNone(r['E4']['faulty']['owner'])
        self.assertTrue(r['E4']['faulty']['repeated_complete_state'])
        self.assertEqual([r['positive'][key]['owner'] for key in ('A','B','none')],['A','B','A'])


if __name__=='__main__': unittest.main()
