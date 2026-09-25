"""Breaks caught: stale effects, overwritten validation, source substitution."""
import importlib.util
from pathlib import Path
import sys
import unittest
from dataclasses import replace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('protocol'):
    import protocol as p
else:
    p=None


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(p,'runtime protocol not implemented')

    def test_stale_commit_is_rejected_but_cached_permission_fault_exposes_it(self):
        s=p.Core(req_a=True,req_b=True)
        s,_=p.step(s,('Validate','A'))
        s,_=p.step(s,('Observe',True,True))
        correct,events=p.step(s,('Commit',))
        self.assertIsNone(correct.owner)
        self.assertEqual(events,[])
        bad,events=p.step(s,('Commit',),fault='cached_commit_permission')
        self.assertEqual(bad.owner,'A')
        self.assertEqual(events,[('Grant','A')])
        self.assertFalse(p.reference_accepts(s,events))

    def test_stale_application_is_rejected_after_valid_issue(self):
        s=p.Core(owner='A')
        s,_=p.step(s,('Issue','A'))
        s,_=p.step(s,('Observe',True,True))
        _,events=p.step(s,('Apply',))
        self.assertEqual(events,[])
        _,events=p.step(s,('Apply',),fault='cached_apply_permission')
        self.assertEqual(events,[('Proceed','A')])
        self.assertFalse(p.reference_accepts(s,events))

    def test_new_same_permission_observation_preserves_validated_choice(self):
        s=p.Core(req_a=True,req_b=True)
        s,_=p.step(s,('Service','B'))
        s,_=p.step(s,('Observe',False,True))
        s,events=p.step(s,('Service','A'))
        self.assertEqual(s.owner,'B')
        self.assertEqual(events,[('Grant','B')])

    def test_no_advice_cannot_stop_source_driven_fifo_authorization(self):
        controller=p.SourceController.from_selected()
        s=p.Core(req_a=True,req_b=True)
        choice,record=controller.select(s,None)
        self.assertEqual(choice,'A')
        self.assertEqual(record['raw_action'],'SelectA')
        s,_=p.step(s,('Service',choice))
        s,events=p.step(s,('Service',None))
        self.assertEqual(events,[('Grant','A')])

    def test_source_advice_changes_choice_and_cannot_choose_ineligible_robot(self):
        controller=p.SourceController.from_selected()
        both=p.Core(req_a=True,req_b=True)
        self.assertEqual(controller.select(both,'B')[0],'B')
        self.assertEqual(controller.select(both,'A')[0],'A')
        self.assertEqual(controller.select(replace(both,req_b=False),'B')[0],'A')
        self.assertEqual(controller.select(replace(both,blocked=True),'B')[0],None)

    def test_release_requires_owner_and_clear(self):
        s=p.Core(owner='A',command='A')
        self.assertEqual(p.step(s,('Release','B',True))[0],s)
        self.assertEqual(p.step(s,('Release','A',False))[0],s)
        after,events=p.step(s,('Release','A',True))
        self.assertIsNone(after.owner)
        self.assertEqual(events,[('Released','A')])


if __name__=='__main__': unittest.main()
