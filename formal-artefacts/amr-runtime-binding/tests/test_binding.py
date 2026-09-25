"""Behavior tests: bypassing binding, resetting pending, or waiting must fail."""
import importlib.util
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
if importlib.util.find_spec('binding'):
    from binding import Runtime
else:
    Runtime = None


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Runtime, 'integrated runtime adapter is missing')
        self.rt = Runtime('req', 'ctx')
        self.rt.local(('RequestAdvice',))
        for r in 'AB':
            self.rt.local(('Register', r))

    def test_valid_b_changes_original_source_choice(self):
        self.rt.receive('req', 'ctx', '{"prefer":"B"}')
        row = self.rt.local(('Service',))
        self.assertEqual(row['source']['raw_action'], 'SelectB')
        self.assertEqual(self.rt.core.pending, 'B')
        self.assertEqual(self.rt.local(('Service',))['events'], [('Grant', 'B')])

    def test_bad_binding_and_payload_do_not_block_fallback(self):
        for req, ctx, text in [('other', 'ctx', '{"prefer":"B"}'),
                               ('req', 'other', '{"prefer":"B"}'),
                               ('req', 'ctx', '{"prefer":"B","grant":true}')]:
            self.rt.receive(req, ctx, text)
        self.rt.local(('Service',))
        self.assertEqual(self.rt.local(('Service',))['events'], [('Grant', 'A')])

    def test_late_reply_does_not_reset_pending(self):
        self.rt.local(('Validate',))
        self.rt.receive('req', 'ctx', '{"prefer":"B"}')
        self.assertEqual(self.rt.core.pending, 'A')
        self.assertEqual(self.rt.local(('Service',))['events'], [('Grant', 'A')])
        self.rt.local(('Release', 'A', True))
        self.rt.local(('Service',))
        self.assertEqual(self.rt.local(('Service',))['events'], [('Grant', 'B')])

    def test_reply_before_open_and_duplicates(self):
        rt = Runtime('req', 'ctx')
        self.assertEqual(rt.receive('req', 'ctx', '{"prefer":"B"}')['verdict'], 'not_requested')
        rt.local(('RequestAdvice',))
        rt.receive('req', 'ctx', '{"prefer":"B"}')
        rt.local(('RequestAdvice',))
        rt.receive('req', 'ctx', '{"prefer":"A"}')
        self.assertEqual(rt.box.advice, 'B')

    def test_current_permission_is_checked_after_latch(self):
        self.rt.local(('Validate',))
        self.rt.local(('Observe', True, True))
        self.assertEqual(self.rt.local(('Commit',))['events'], [])
        self.assertIsNone(self.rt.core.owner)

    def test_raw_provider_cannot_call_control_actions(self):
        with self.assertRaises(ValueError):
            self.rt.local(('Reply', 'B'))
        with self.assertRaises(ValueError):
            self.rt.local(('Validate', 'B'))

    def test_unchecked_source_cannot_enter_adapter(self):
        with self.assertRaises(ValueError):
            Runtime('req', 'ctx', source=object())


if __name__ == '__main__':
    unittest.main()
