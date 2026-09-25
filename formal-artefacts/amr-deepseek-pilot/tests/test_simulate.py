import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import simulate


class SimulationGateTests(unittest.TestCase):
    def test_fixture_cannot_be_labelled_as_live_deepseek(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'out'
            summary = {'complete': True, 'selected_candidate': {'response_path': 'must-not-be-read'}}
            with patch.object(simulate.trial, 'summarize', return_value=summary), \
                 patch.object(simulate.trial, '_manifest', return_value={'config': {'record_mode': 'fixture'}}):
                with self.assertRaisesRegex(ValueError, 'live DeepSeek'):
                    simulate.execute(Path(temp), out)
            self.assertFalse(out.exists())

    def test_partial_six_chain_run_cannot_enter_simulation(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'out'
            with patch.object(simulate.trial, 'summarize', return_value={'complete': False, 'selected_candidate': None}):
                with self.assertRaises(ValueError):
                    simulate.execute(Path(temp), out)
            self.assertFalse(out.exists())

    def test_complete_but_no_accepted_candidate_cannot_enter_simulation(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'out'
            with patch.object(simulate.trial, 'summarize', return_value={'complete': True, 'selected_candidate': None}):
                with self.assertRaises(ValueError):
                    simulate.execute(Path(temp), out)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
