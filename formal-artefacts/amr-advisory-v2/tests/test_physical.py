import unittest
import physical
class PhysicalTests(unittest.TestCase):
 def test_positive(self):
  for advice,first in [('A','A'),('B','B'),(None,'A')]:
   s=physical.run_episode(advice=advice)
   self.assertEqual(s['grant_order'][0],first)
   self.assertEqual(s['completed_robots'],['A','B'])
   self.assertFalse(s['early_releases']+s['reference_violations']+s['collision_pairs']+s['unresolved_pairs'])
 def test_center(self):
  self.assertTrue(physical.run_episode(center_clear=True)['early_releases'])
  self.assertFalse(physical.run_episode()['early_releases'])
 def test_gaps(self):
  for gap in ['commit','apply']:
   bad=physical.run_gap(gap,bad=True); good=physical.run_gap(gap,bad=False)
   self.assertTrue(bad['reference_violations']); self.assertFalse(good['reference_violations'])
   if gap=='apply':
    self.assertGreater(bad['final_speed'],0); self.assertEqual(good['final_speed'],0)
 def test_environment(self):
  s=physical.run_episode(wait_advice=True,horizon=3)
  self.assertEqual(s['grant_order'],[]); self.assertEqual(s['termination'],'horizon')
  for mode in ['temporary','permanent']:
   s=physical.run_episode(pedestrian=mode)
   self.assertIsNotNone(s['pedestrian_trigger'])
   self.assertFalse(s['collision_pairs']+s['unresolved_pairs'])
   self.assertEqual(s['completed_robots'],['A','B'] if mode=='temporary' else [])
 def test_stopping(self):
  inside=physical.run_braking(inside=True); outside=physical.run_braking(inside=False)
  self.assertTrue(inside['condition']); self.assertFalse(outside['condition'])
  self.assertGreaterEqual(inside['standstill_margin'],.2); self.assertEqual(inside['final_speed'],0)
