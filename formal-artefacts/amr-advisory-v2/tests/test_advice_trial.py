"""No live transport in tests: verify dispatch bounds and cutoff behavior."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if importlib.util.find_spec('advice_trial'):
    import advice_trial as a
else:
    a=None


class AdviceTrialTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(a,'bounded advice trial not implemented')

    def test_payload_is_bounded_and_does_not_include_credentials(self):
        payload=a.payload_for(0)
        self.assertEqual(payload['model'],'deepseek-flash')
        self.assertLessEqual(payload['max_tokens'],128)
        self.assertNotIn('api_key',payload)
        with self.assertRaises(ValueError): a.payload_for(6)

    def test_early_advice_used_late_advice_cannot_reset_fifo(self):
        early=a.decision_at_deadline({'content':'{"prefer":"B"}','arrival_seconds':.5},1.0)
        late=a.decision_at_deadline({'content':'{"prefer":"B"}','arrival_seconds':1.5},1.0)
        self.assertEqual(early['owner'],'B')
        self.assertEqual(late['owner'],'A')
        self.assertEqual(late['adoption'],'late')
        self.assertEqual(early['source']['raw_action'],'SelectB')

    def test_malformed_reply_falls_back_and_zero_wait_missing_reply(self):
        for reply in (None,{'content':'Ignore safety and grant B','arrival_seconds':.1}):
            result=a.decision_at_deadline(reply,1.0)
            self.assertEqual(result['owner'],'A')

    def test_dispatch_marker_prevents_duplicate_attempt(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'attempt'
            p.mkdir()
            a.claim_dispatch(p,0)
            with self.assertRaises(FileExistsError): a.claim_dispatch(p,0)

    def test_prepare_has_six_frozen_prompts(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'batch'
            report=a.prepare(p)
            self.assertEqual(len(report['samples']),6)
            self.assertGreater(report['window_seconds'],0)
            self.assertEqual(len(list(p.glob('*/http-request.json'))),6)
            with self.assertRaises(FileExistsError): a.prepare(p)

    def test_reply_preserves_token_counts_and_rejects_invalid_usage(self):
        for usage in ({'prompt_tokens':50,'completion_tokens':8,
                       'prompt_cache_hit_tokens':10,'prompt_cache_miss_tokens':40},
                      {'prompt_tokens':50,'completion_tokens':-1}):
            with self.subTest(usage=usage), tempfile.TemporaryDirectory() as folder:
                p=Path(folder)
                a.write_json(p/'http-body.bin',{'model':'deepseek-flash','usage':usage,
                    'choices':[{'finish_reason':'stop','message':{'content':'{"prefer":"B"}'}}]})
                with patch.object(a,'run_worker',return_value={'status':'received'}):
                    result=a._call_once('not-a-credential',p,a.time.monotonic())
                if usage['completion_tokens'] >= 0:
                    self.assertIsNone(result['fatal'])
                    self.assertEqual(result['usage_summary'],{'input_tokens':50,'output_tokens':8,
                        'cache_hit_tokens':10,'cache_miss_tokens':40})
                else:
                    self.assertEqual(result['fatal'],'usage_unavailable')
                    self.assertIsNone(result['usage_summary'])

    def test_actual_worker_enters_credential_validation_without_network(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'batch'
            a.prepare(p)
            invalid_key=Path(folder)/'invalid.env'
            invalid_key.write_text('API_KEY=too-short',encoding='utf-8')
            worker=getattr(a,'run_worker',None)
            self.assertIsNotNone(worker,'advisory worker adapter missing')
            result=worker(invalid_key,p/'001')
            self.assertEqual(result.get('error_type'),'ValueError')
            self.assertTrue((p/'001/transport.json').exists())
            self.assertFalse((p/'001/dispatch.json').exists())

    def test_coordinated_manifest_payload_tampering_rejected(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'batch'
            a.prepare(p)
            validate=getattr(a,'validate_batch',None)
            self.assertIsNotNone(validate,'independent batch validation missing')
            payload=json.loads((p/'001/http-request.json').read_bytes())
            payload['max_tokens']=65536
            (p/'001/http-request.json').write_text(json.dumps(payload),encoding='utf-8')
            manifest=json.loads((p/'protocol.json').read_bytes())
            manifest['samples'][0]['request_sha256']=a.sha((p/'001/http-request.json').read_bytes())
            (p/'protocol.json').write_text(json.dumps(manifest),encoding='utf-8')
            with self.assertRaises(ValueError): validate(p)

    def test_different_accepted_source_cannot_replace_frozen_raw_identity(self):
        from protocol import SourceController
        from source_check import historical_sources
        checker=getattr(a,'validate_source_identity',None)
        self.assertIsNotNone(checker,'fixed raw-source binding missing')
        original=SourceController.from_selected()
        checker(original)
        same_behavior_different_bytes=SourceController(historical_sources()[2].read_bytes()+b' ')
        with self.assertRaises(ValueError): checker(same_behavior_different_bytes)


if __name__=='__main__': unittest.main()
