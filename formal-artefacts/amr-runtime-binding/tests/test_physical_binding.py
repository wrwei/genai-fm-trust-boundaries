"""Integration tests would fail if arrival events bypassed the runtime mailbox."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('physical_binding'):
    from physical_binding import run_episode
else:
    run_episode = None


class PhysicalBindingTests(unittest.TestCase):
    def test_reply_before_and_after_initial_grant(self):
        self.assertIsNotNone(run_episode, 'bound physical driver is missing')
        for arrival, expected in [(0., 'B'), (.06, 'A')]:
            rows = []
            result = run_episode(advice_events=[(arrival, 'req', 'ctx', '{"prefer":"B"}')],
                                 horizon=.15, emit=rows.append)
            self.assertEqual(result['grant_order'], [expected])
            self.assertTrue(any(r['kind'] == 'adapter' and r['event'][0] == 'Provider' for r in rows))
            self.assertFalse(result['reference_violations'])


if __name__ == '__main__':
    unittest.main()
