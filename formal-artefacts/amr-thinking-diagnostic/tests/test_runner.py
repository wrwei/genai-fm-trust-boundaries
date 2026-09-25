"""Offline transport fixtures. Never read credentials or contact a provider."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

HERE = Path(__file__).resolve().parents[1]


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner_exists = (HERE / 'runner.py').is_file()
        if cls.runner_exists:
            spec = importlib.util.spec_from_file_location('thinking_runner', HERE / 'runner.py')
            cls.r = importlib.util.module_from_spec(spec)
            sys.modules['thinking_runner'] = cls.r
            spec.loader.exec_module(cls.r)

    def setUp(self):
        self.assertTrue(self.runner_exists, 'bounded thinking runner not implemented')

    def fixture_worker(self, content='{}', usage=True, status='received', finish='stop', reasoning=''):
        def work(key, attempt):
            self.assertEqual(key, 'not-a-credential')
            self.r.write_json(attempt / 'dispatch.json', {'fixture': True})
            envelope = {'model': 'deepseek-flash', 'system_fingerprint':'fixture',
                        'choices':[{'finish_reason':finish, 'message':{
                            'content':content, 'reasoning_content':reasoning}}]}
            if usage:
                envelope['usage'] = {'prompt_tokens':2000, 'completion_tokens':300,
                                    'completion_tokens_details':{'reasoning_tokens':250}}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            return {'status':status, 'http_status':200}
        return work

    def test_payload_arms_have_equal_limits_and_correct_thinking_controls(self):
        normal = self.r.payload_for('same prompt', 'N12-F')
        thinking = self.r.payload_for('same prompt', 'T12-F')
        self.assertEqual(normal, {'model':'deepseek-flash', 'messages':[{'role':'user','content':'same prompt'}],
            'max_tokens':8192, 'stream':False, 'temperature':0, 'thinking':{'type':'disabled'}})
        self.assertEqual(thinking, {'model':'deepseek-flash', 'messages':[{'role':'user','content':'same prompt'}],
            'max_tokens':8192, 'stream':False, 'reasoning_effort':'high', 'thinking':{'type':'enabled'}})
        with self.assertRaises(ValueError):
            self.r.payload_for('same prompt', 'D12-F')

    def test_both_first_prompts_match_frozen_previous_enhanced_prompt(self):
        expected = (HERE.parent / 'amr-forge-diagnostic/run/attempts/004/prompt.txt').read_bytes()
        for state in self.r.initial_states().values():
            prompt, _ = self.r.prompt_for(state)
            self.assertEqual(prompt.encode('utf-8'), expected)

    def test_serialized_payload_size_is_bounded(self):
        payload = self.r.payload_for('bounded prompt', 'T12-F')
        self.r.validate_payload(payload)
        with self.assertRaises(ValueError):
            self.r.validate_payload(self.r.payload_for('x' * 65537, 'T12-F'))

    def test_total_completion_tokens_include_reasoning_in_usage_and_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            envelope = {'model':'deepseek-flash', 'usage':{'prompt_tokens':100, 'completion_tokens':8000,
                        'completion_tokens_details':{'reasoning_tokens':7900}},
                        'choices':[{'finish_reason':'stop','message':{'content':'{}','reasoning_content':'private fixture'}}]}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            payload = self.r.payload_for('x', 'T12-F')
            raw, decoded, usage_summary, fatal = self.r.decode_response(attempt, {'status':'received'}, payload)
            self.assertIsNone(fatal)
            self.assertEqual(raw, b'{}')
            self.assertEqual(usage_summary['output_tokens'], 8000)
            self.assertEqual(set(usage_summary), {'input_tokens', 'output_tokens',
                                                  'cache_hit_tokens', 'cache_miss_tokens'})
            self.assertEqual(self.r.thinking_metadata(decoded, payload)['reasoning_tokens'],7900)
            envelope['usage']['completion_tokens'] = 8193
            (attempt / 'http-body.bin').write_bytes(self.r.json_bytes(envelope))
            self.assertEqual(self.r.decode_response(attempt, {'status':'received'}, payload)[3], 'output_cap_violation')

    def test_empty_reasoning_is_unconfirmed_without_rejecting_valid_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            envelope = {'model':'deepseek-flash', 'usage':{'prompt_tokens':100, 'completion_tokens':10},
                        'choices':[{'finish_reason':'stop','message':{'content':'{}','reasoning_content':''}}]}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            payload = self.r.payload_for('x','T12-F')
            raw, decoded, _, fatal = self.r.decode_response(attempt, {'status':'received'}, payload)
            self.assertIsNone(fatal)
            self.assertEqual(raw, b'{}')
            info = self.r.thinking_metadata(decoded, payload)
            self.assertEqual(info['mode_evidence'],'unconfirmed')
            self.assertEqual(info['reasoning_content_bytes'],0)
            self.assertIsNone(info['reasoning_tokens'])

    def test_impossible_reasoning_count_is_invalid_usage(self):
        for count in (301,-1,True,'250'):
            with self.subTest(count=count),tempfile.TemporaryDirectory() as tmp:
                attempt = Path(tmp)
                self.r.write_json(attempt/'http-body.bin',{'model':'deepseek-flash',
                    'usage':{'prompt_tokens':100,'completion_tokens':300,
                             'completion_tokens_details':{'reasoning_tokens':count}},
                    'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]})
                _,envelope,usage_summary,fatal = self.r.decode_response(attempt,{'status':'received'},
                    self.r.payload_for('x','T12-F'))
                self.assertEqual(fatal,'invalid_usage')
                self.assertIsNone(usage_summary)
                self.assertIsNone(self.r.thinking_metadata(envelope,
                    self.r.payload_for('x','T12-F'))['reasoning_tokens'])

    def test_eight_call_ceiling_round_robin_and_no_reasoning_in_prompts(self):
        calls = []
        def work(key, attempt):
            req = self.r.read_json(attempt / 'request.json')
            calls.append((req['condition'],req['repair']))
            self.assertNotIn('PRIVATE_REASONING_FIXTURE', (attempt / 'prompt.txt').read_text())
            return self.fixture_worker(json.dumps({'invalid_unique_fixture':len(calls)}),
                                       reasoning='PRIVATE_REASONING_FIXTURE')(key,attempt)
        with tempfile.TemporaryDirectory() as tmp:
            result = self.r.execute('not-a-credential', run=Path(tmp)/'run',worker=work,fixture=True)
            self.assertEqual(result['new_calls'],8)
            self.assertEqual(calls,[(cid,i) for i in range(1,5) for cid in ('N12-F','T12-F')])
            self.assertEqual([s['stop'] for s in result['conditions'].values()],['repair_limit']*2)
            protocol = self.r.read_json(Path(tmp)/'run/protocol.json')
            self.assertEqual(protocol['id'],'amr-thinking-diagnostic/v1')
            self.assertEqual(protocol['model_configs'],self.r.CONFIGS)
            outcome = self.r.read_json(Path(tmp)/'run/attempts/001/outcome.json')
            self.assertEqual(outcome['thinking']['reasoning_tokens'],250)
            self.assertNotIn('PRIVATE_REASONING_FIXTURE',json.dumps(outcome))

    def test_cycle_stops_each_condition_and_run_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            worker = self.fixture_worker(self.r.START.read_text(encoding='utf-8'))
            result = self.r.execute('not-a-credential',run=run,worker=worker,fixture=True)
            self.assertEqual(result['new_calls'],2)
            self.assertEqual([s['stop'] for s in result['conditions'].values()],['cycle']*2)
            with self.assertRaises(FileExistsError):
                self.r.execute('not-a-credential',run=run,worker=worker,fixture=True)

    def test_acceptance_is_terminal_and_selects_first_arm(self):
        source = (HERE.parent/'amr-supervisor/candidates/authored_reference.json').read_text()
        with tempfile.TemporaryDirectory() as tmp:
            result = self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=self.fixture_worker(source),fixture=True)
            self.assertEqual(result['new_calls'],2)
            self.assertEqual([s['stop'] for s in result['conditions'].values()],['accepted']*2)
            self.assertEqual(result['selected_for_exploratory_physics']['condition'],'N12-F')
            state = self.r.initial_states()['N12-F']
            report = self.r.d.assess(source,12)
            state['keys'].append(self.r.d.program_key(source,12))
            self.r.advance(state,source.encode(),report,{}, {'fatal':None,'usage_summary':None},'fixture')
            self.assertEqual(state['stop'],'accepted')

    def test_invalid_usage_stops_all_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.r.execute('not-a-credential',run=Path(tmp)/'run',
                                    worker=self.fixture_worker(usage=False),fixture=True)
            self.assertEqual(result['new_calls'],1)
            self.assertEqual(result['stop'],'invalid_usage')

    def test_fatal_transports_and_truncation_never_retry(self):
        for worker,fatal in ((self.fixture_worker(status='transport_error'),'transport_error'),
                             (self.fixture_worker(finish='length'),'truncated')):
            with self.subTest(fatal=fatal),tempfile.TemporaryDirectory() as tmp:
                result = self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=worker,fixture=True)
                self.assertEqual(result['new_calls'],1)
                self.assertEqual(result['stop'],fatal)
                self.assertIsNone(result['selected_for_exploratory_physics'])

    def test_malformed_provider_json_stops_without_retry(self):
        for body in (b'{',b'null',b'[]',b'7',b'"bad"', b'{"choices":[{"message":{"content":"\\ud800"}}]}'):
            def work(key,attempt):
                (attempt/'http-body.bin').write_bytes(body)
                return {'status':'received','http_status':200}
            with self.subTest(body=body),tempfile.TemporaryDirectory() as tmp:
                result = self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=work,fixture=True)
                self.assertEqual(result['new_calls'],1)
                self.assertIn(result['stop'],('transport_error','invalid_utf8'))

    def test_fatal_assessment_does_not_reenter_failed_parser(self):
        state = self.r.initial_states()['N12-F']
        report = {'accepted':False,'parse_pass':False,'full_cases':[],'failure_input_ids':[]}
        with patch.object(self.r.d,'program_key',side_effect=RecursionError):
            self.r.advance(state,b'[[[',report,{}, {'fatal':'assessment_error','usage_summary':None},'fixture')
        self.assertEqual(state['stop'],'assessment_error')

    def test_fixture_cannot_enter_live_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=self.fixture_worker())
            self.assertFalse((Path(tmp)/'run').exists())

    def pending(self,run):
        self.r.initialize(run,False)
        folder = run/'attempts/001'
        folder.mkdir()
        prompt,feedback = self.r.prompt_for(self.r.initial_states()['N12-F'])
        payload = self.r.payload_for(prompt,'N12-F')
        (folder/'prompt.txt').write_bytes(prompt.encode())
        self.r.write_json(folder/'feedback.json',feedback)
        self.r.write_json(folder/'request.json',{'condition':'N12-F','repair':1})
        self.r.write_json(folder/'http-request.json',payload)
        self.r.write_json(folder/'preflight.json',{'max_posts':1,'retries':0,
            'payload_sha256':self.r.sha(folder/'http-request.json')})
        self.r.write_json(folder/'dispatch-intent.json',{'max_posts':1,'retries':0})
        return folder

    def test_worker_exclusive_claim_allows_only_one_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            attempt = self.pending(run)
            with patch.object(self.r,'RUN',run),patch.object(self.r,'post_once') as post:
                self.r.network_child('not-a-credential',attempt)
                post.assert_called_once_with('not-a-credential',attempt)
                with self.assertRaises(FileExistsError):
                    self.r.network_child('not-a-credential',attempt)
                self.assertEqual(post.call_count,1)

    def test_worker_rejects_payload_prompt_and_preflight_tampering(self):
        for kind in ('payload','prompt','preflight','intent'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                run = Path(tmp)/'run'
                attempt = self.pending(run)
                if kind == 'payload':
                    payload = self.r.read_json(attempt/'http-request.json')
                    payload['thinking']={'type':'enabled'}
                    (attempt/'http-request.json').write_bytes(self.r.json_bytes(payload))
                elif kind == 'prompt':
                    (attempt/'prompt.txt').write_text('tampered')
                elif kind == 'preflight':
                    preflight = self.r.read_json(attempt/'preflight.json')
                    preflight['payload_sha256']='0'*64
                    (attempt/'preflight.json').write_bytes(self.r.json_bytes(preflight))
                else:
                    (attempt/'dispatch-intent.json').write_bytes(self.r.json_bytes({'max_posts':2,'retries':0}))
                with patch.object(self.r,'RUN',run),patch.object(self.r,'post_once') as post:
                    with self.assertRaises(RuntimeError):
                        self.r.network_child('not-a-credential',attempt)
                    post.assert_not_called()

    def test_frozen_dependency_drift_prevents_worker_before_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            attempt = self.pending(run)
            real_sha = self.r.sha
            def drift(path):
                return '0'*64 if Path(path)==HERE/'runner.py' else real_sha(path)
            with patch.object(self.r,'RUN',run),patch.object(self.r,'sha',side_effect=drift),patch.object(self.r,'post_once') as post:
                with self.assertRaisesRegex(RuntimeError,'dependency changed'):
                    self.r.network_child('not-a-credential',attempt)
                post.assert_not_called()

    def test_child_wall_deadline_is_180_seconds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(self.r.subprocess,'run',side_effect=subprocess.TimeoutExpired('fixture',180)) as child:
                with self.assertRaises(subprocess.TimeoutExpired):
                    self.r.run_worker('not-a-credential',Path(tmp))
                self.assertEqual(child.call_args.kwargs['timeout'],180)

    def test_oversized_followup_stops_with_final_evidence_without_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            result = self.r.execute('not-a-credential',run=run,
                worker=self.fixture_worker('x'*70000),fixture=True)
            self.assertEqual(result['new_calls'],2)
            self.assertEqual(result['stop'],'payload_limit_stop')
            self.assertTrue((run/'evidence-sha256.json').exists())

    def test_falsey_nontext_content_and_deep_json_are_fatal(self):
        for content in (False,0,[],{}):
            with self.subTest(content=content),tempfile.TemporaryDirectory() as tmp:
                attempt = Path(tmp)
                self.r.write_json(attempt/'http-body.bin',{'model':'deepseek-flash',
                    'usage':{'prompt_tokens':100,'completion_tokens':10},
                    'choices':[{'finish_reason':'stop','message':{'content':content}}]})
                self.assertEqual(self.r.decode_response(attempt,{'status':'received'},
                    self.r.payload_for('x','T12-F'))[3],'transport_error')
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            (attempt/'http-body.bin').write_bytes(b'['*10000+b']'*10000)
            self.assertEqual(self.r.decode_response(attempt,{'status':'received'},
                self.r.payload_for('x','T12-F'))[3],'transport_error')

    def test_post_boundary_has_one_dispatch_150s_deadline_and_fixed_endpoint(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,size): return b'{"fixture":true}'
        class Opener:
            def __init__(self): self.requests=[]
            def open(self,request,timeout):
                self.requests.append((request,timeout))
                return Response()
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            self.r.write_json(attempt/'http-request.json',self.r.payload_for('x','T12-F'))
            opener = Opener()
            with patch.object(self.r.smoke,'read_key',return_value='OFFLINE_FIXTURE_CREDENTIAL'),patch.object(
                    self.r.urllib.request,'build_opener',return_value=opener) as build:
                self.r.post_once('not-a-credential',attempt)
                self.assertEqual(len(opener.requests),1)
                request,timeout = opener.requests[0]
                self.assertEqual(request.full_url,'https://api.deepseek.com/chat/completions')
                self.assertEqual(request.method,'POST')
                self.assertEqual(timeout,150)
                self.assertEqual(request.data,(attempt/'http-request.json').read_bytes())
                self.assertEqual(build.call_args.args[0].proxies,{})
                self.assertIsInstance(build.call_args.args[1],self.r.smoke.NoRedirect)
                with self.assertRaises(urllib.error.HTTPError):
                    build.call_args.args[1].redirect_request(request,None,302,'redirect',{},'https://invalid.example')
                with self.assertRaises(FileExistsError):
                    self.r.post_once('not-a-credential',attempt)
                self.assertEqual(len(opener.requests),1)

    def test_post_redacts_credential_echo_and_exception_messages(self):
        key = 'OFFLINE_FIXTURE_CREDENTIAL'
        for error in (urllib.error.HTTPError('https://fixture',400,'fixture',{},io.BytesIO(key.encode())),
                      RuntimeError('secret '+key)):
            with self.subTest(error=type(error).__name__),tempfile.TemporaryDirectory() as tmp:
                attempt = Path(tmp)
                self.r.write_json(attempt/'http-request.json',self.r.payload_for('x','T12-F'))
                with patch.object(self.r.smoke,'read_key',return_value=key),patch.object(
                        self.r.urllib.request,'build_opener') as build:
                    build.return_value.open.side_effect = error
                    self.r.post_once('not-a-credential',attempt)
                for path in attempt.iterdir():
                    self.assertNotIn(key.encode(),path.read_bytes())
                self.assertEqual(self.r.read_json(attempt/'transport.json')['status'],'transport_error')


if __name__ == '__main__':
    unittest.main()
