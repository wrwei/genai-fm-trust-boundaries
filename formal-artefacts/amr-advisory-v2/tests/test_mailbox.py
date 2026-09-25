"""Untrusted replies must not overwrite, spoof, or retroactively change a choice."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('advice_mailbox'):
    from advice_mailbox import AdviceMailbox
else:
    AdviceMailbox=None


class MailboxTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(AdviceMailbox,'bounded mailbox not implemented')
        self.box=AdviceMailbox('request-1','tasks-1')

    def test_first_valid_response_cannot_be_overwritten(self):
        self.assertEqual(self.box.receive('request-1','tasks-1','{"prefer":"B"}'),'accepted')
        self.assertEqual(self.box.receive('request-1','tasks-1','{"prefer":"A"}'),'duplicate_ignored')
        self.assertEqual(self.box.latch()['advice'],'B')

    def test_wrong_identity_and_duplicate_json_key_rejected(self):
        for req,ctx,text in [('request-2','tasks-1','{"prefer":"A"}'),
                             ('request-1','tasks-2','{"prefer":"A"}'),
                             ('request-1','tasks-1','{"prefer":"A","prefer":"B"}'),
                             ('request-1','tasks-1','{"prefer":"A","grant":true}')]:
            self.assertNotEqual(self.box.receive(req,ctx,text),'accepted')
        self.assertIsNone(self.box.latch()['advice'])

    def test_late_response_does_not_change_already_latched_value(self):
        first=self.box.latch()
        self.assertIsNone(first['advice'])
        self.box.receive('request-1','tasks-1','{"prefer":"B"}')
        self.assertIsNone(first['advice'])
        self.assertEqual(self.box.latch()['advice'],'B')

    def test_invalid_advice_is_bounded_and_never_a_wait_loop(self):
        for text in ['', 'A', '{"prefer":"C"}', 'x'*1025]:
            self.assertEqual(self.box.receive('request-1','tasks-1',text),'invalid_payload')
        self.assertEqual(self.box.latch()['reason'],'no_valid_advice')


if __name__=='__main__': unittest.main()
