"""Source decisions must actually govern request, release, modes and completion."""
from pathlib import Path
import math
import sys
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from closed_loop import run_supervised_episode
import closed_loop

def source(name='authored_reference'):
    return (HERE/'candidates'/f'{name}.json').read_text(encoding='utf-8')


class PedestrianEvidenceTests(unittest.TestCase):
    def evidence(self, pose, name='A', speed=.18274):
        self.assertTrue(hasattr(closed_loop, 'pedestrian_stopping_evidence'),
                        'geometric stopping evidence helper is missing')
        obs=closed_loop.Observation(name,10.,pose,speed,True,1,1)
        return closed_loop.pedestrian_stopping_evidence(obs,name,10.05,closed_loop.parameters())

    def test_turning_approach_does_not_claim_straight_stopping_condition(self):
        pose=(7.98524,-.01476,math.pi/4)
        evidence=self.evidence(pose)
        self.assertFalse(evidence['straight_approach_applicable'])
        self.assertIsNone(evidence['straight_approach_condition'])
        self.assertIsNone(evidence['required_distance'])
        self.assertTrue(evidence['scope_reason'])
        self.assertEqual(evidence['observation_pose'],pose)
        self.assertEqual(evidence['observation_speed'],.18274)
        self.assertAlmostEqual(evidence['world_x_footprint_extent'],.7/math.sqrt(2))

    def test_aligned_clear_approaches_check_the_distance_condition(self):
        for name,pose in [('A',(9.,0.,0.)),('B',(15.,0.,math.pi))]:
            with self.subTest(name=name):
                evidence=self.evidence(pose,name)
                self.assertTrue(evidence['straight_approach_applicable'])
                self.assertTrue(evidence['straight_approach_condition'])
                self.assertAlmostEqual(evidence['observation_distance_to_H'],2.1)
                self.assertGreater(evidence['required_distance'],0.)

    def test_aligned_insufficient_gap_is_a_failed_condition(self):
        evidence=self.evidence((11.,0.,0.),speed=1.)
        self.assertTrue(evidence['straight_approach_applicable'])
        self.assertFalse(evidence['straight_approach_condition'])

    def test_off_center_wrong_heading_and_past_boundary_are_out_of_scope(self):
        for pose in [(9.,.1,0.),(9.,0.,math.pi),(12.,0.,0.),(7.,0.,0.)]:
            with self.subTest(pose=pose):
                evidence=self.evidence(pose)
                self.assertFalse(evidence['straight_approach_applicable'])
                self.assertIsNone(evidence['straight_approach_condition'])

class ClosedLoopTests(unittest.TestCase):
    def test_rejected_source_never_starts_a_plant_episode(self):
        events=[]
        with self.assertRaises(ValueError):
            run_supervised_episode(source('always_brake'),emit=events.append)
        self.assertEqual(events,[])

    def test_accepted_source_controls_order_request_release_and_finish(self):
        for preference in ('A','B'):
            result=run_supervised_episode(source(),preference=preference)
            self.assertTrue(result['safe_and_complete'])
            self.assertEqual(result['grant_order'][0],preference)
            self.assertEqual(result['completed_robots'],['A','B'])
            self.assertEqual(result['runtime_rejections'],[])
            actions={event['raw_action'] for event in result['events'] if event['kind']=='supervisor_step'}
            self.assertTrue({'Request','Proceed','Release','Finish'} <= actions)

    def test_temporary_pedestrian_requires_resume_before_motion(self):
        result=run_supervised_episode(source(),pedestrian='temporary')
        self.assertTrue(result['safe_and_complete'])
        steps=[event for event in result['events'] if event['kind']=='supervisor_step' and event['robot']=='A']
        resumed=[index for index,event in enumerate(steps) if event['raw_action']=='Resume']
        self.assertTrue(resumed)
        self.assertTrue(any(steps[index+1]['raw_action']=='Proceed' for index in resumed if index+1<len(steps)))
        self.assertEqual(result['collision_pairs'],[])

if __name__=='__main__':unittest.main()
