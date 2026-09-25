"""Offline replication contracts; no credentials and no live network."""
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
IDS = ('P1-R1', 'P2-R1', 'P3-R1', 'P1-R2', 'P2-R2', 'P3-R2')


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner_exists = (HERE/'runner.py').is_file()
        if cls.runner_exists:
            spec = importlib.util.spec_from_file_location('replication_runner', HERE/'runner.py')
            cls.r = importlib.util.module_from_spec(spec)
            sys.modules['replication_runner'] = cls.r
            spec.loader.exec_module(cls.r)

    def setUp(self):
        self.assertTrue(self.runner_exists, 'fresh-context replication runner not implemented')

    def fixture_worker(self, content='{}', usage=True, status='received', finish='stop', reasoning=''):
        def work(key, attempt):
            self.assertEqual(key, 'not-a-credential')
            self.r.write_json(attempt/'dispatch.json', {'fixture':True})
            envelope = {'model':'deepseek-flash', 'system_fingerprint':'fixture',
                        'choices':[{'finish_reason':finish, 'message':{
                            'content':content, 'reasoning_content':reasoning}}]}
            if usage:
                envelope['usage'] = {'prompt_tokens':2000, 'completion_tokens':300,
                                    'completion_tokens_details':{'reasoning_tokens':250}}
            self.r.write_json(attempt/'http-body.bin', envelope)
            return {'status':status, 'http_status':200}
        return work

    def accepted_source(self):
        return (HERE.parent/'amr-thinking-extended/run/attempts/002/response.bin').read_text(encoding='utf-8')

    def test_initial_prompts_are_only_original_task_with_three_rule_limit_edits(self):
        states = self.r.initial_states()
        self.assertEqual(tuple(states), IDS)
        for sample, state in states.items():
            original = (HERE.parent/f'amr-llm-trial/prompts/prepared/{sample}.txt').read_text(encoding='utf-8')
            expected = original.replace('at most eight rules','at most twelve rules').replace(
                'limit of eight','limit of twelve').replace('eight-rule function limit','twelve-rule function limit')
            prompt, feedback = self.r.prompt_for(state)
            self.assertEqual(prompt, expected)
            self.assertIsNone(feedback)
            self.assertIsNone(state['text'])
            self.assertIsNone(state['report'])
            self.assertEqual(state['history'], [])
            self.assertEqual(state['keys'], [])
            self.assertEqual(state['calls'], 0)
            self.assertIsNone(state['initial_accepted'])
            self.assertEqual(self.r.payload_for(prompt,sample), {
                'model':'deepseek-flash','max_tokens':65536,'stream':False,
                'thinking':{'type':'enabled'},'reasoning_effort':'high',
                'messages':[{'role':'user','content':expected}]})
        for prefix in ('P1','P2','P3'):
            self.assertEqual(self.r.original_task(prefix+'-R1'), self.r.original_task(prefix+'-R2'))
        with self.assertRaises(ValueError):
            self.r.payload_for('x','P4-R1')

    def test_eighteen_call_ceiling_all_initials_then_two_repair_rounds(self):
        calls = []
        def work(key, attempt):
            req = self.r.read_json(attempt/'request.json')
            calls.append((req['sample_id'],req['attempt'],req['phase']))
            self.assertNotIn('PRIVATE_REASONING_FIXTURE',(attempt/'prompt.txt').read_text())
            return self.fixture_worker(json.dumps({'invalid_unique_fixture':len(calls)}),
                reasoning='PRIVATE_REASONING_FIXTURE')(key,attempt)
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            result = self.r.execute('not-a-credential',run=run,worker=work,fixture=True)
            self.assertEqual(calls,[(sid,i,'initial' if i==0 else 'repair') for i in range(3) for sid in IDS])
            self.assertEqual(result['new_calls'],18)
            self.assertEqual(result['network_dispatches'],18)
            self.assertEqual(result['stop'],'protocol_complete')
            self.assertEqual(result['initial_accepted_count'],0)
            self.assertEqual(result['eventually_accepted_count'],0)
            self.assertEqual(result['selected_sources'],[])
            self.assertEqual([s['calls'] for s in result['samples'].values()],[3]*6)
            self.assertEqual([s['repairs'] for s in result['samples'].values()],[2]*6)
            self.assertEqual([s['stop'] for s in result['samples'].values()],['repair_limit']*6)
            self.assertEqual(self.r.read_json(run/'attempts/001/feedback.json'),None)
            self.assertIsInstance(self.r.read_json(run/'attempts/007/feedback.json'),dict)
            self.assertNotIn('PRIVATE_REASONING_FIXTURE',json.dumps(result))
            replayed, records = self.r.replay(run)
            self.assertEqual(len(records),18)
            self.assertEqual(self.r.public_states(replayed), result['samples'])

    def test_cycles_are_local_to_chain_and_do_not_suppress_other_initials(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            result = self.r.execute('not-a-credential',run=run,worker=self.fixture_worker('{}'),fixture=True)
            self.assertEqual(result['new_calls'],12)
            self.assertEqual([s['stop'] for s in result['samples'].values()],['cycle']*6)
            self.assertEqual([s['repairs'] for s in result['samples'].values()],[1]*6)
            with self.assertRaises(FileExistsError):
                self.r.execute('not-a-credential',run=run,worker=self.fixture_worker(),fixture=True)

    def test_first_acceptance_counts_and_exact_byte_source_deduplication(self):
        source = self.accepted_source()
        formatted = source+'\n'
        def work(key,attempt):
            req = self.r.read_json(attempt/'request.json')
            text = source if req['sample_id'] in ('P1-R1','P3-R1') else formatted
            if req['sample_id']=='P2-R1' and req['attempt']==0:
                text = '{}'
            return self.fixture_worker(text)(key,attempt)
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            result=self.r.execute('not-a-credential',run=run,worker=work,fixture=True)
            self.assertEqual(result['new_calls'],7)
            self.assertEqual(result['initial_accepted_count'],5)
            self.assertEqual(result['eventually_accepted_count'],6)
            second=result['samples']['P2-R1']
            self.assertFalse(second['initial_accepted'])
            self.assertEqual(second['first_accepted_attempt'],1)
            self.assertEqual(second['calls'],2)
            selected=result['selected_sources']
            self.assertEqual(len(selected),2)
            self.assertEqual(selected[0]['representative_sample'],'P1-R1')
            self.assertEqual(selected[0]['sample_ids'],['P1-R1','P3-R1'])
            self.assertEqual(selected[0]['response_path'],'attempts/001/response.bin')
            self.assertEqual(selected[1]['representative_sample'],'P2-R1')
            self.assertEqual(selected[1]['sample_ids'],['P2-R1','P1-R2','P2-R2','P3-R2'])
            self.assertEqual(selected[1]['first_accepted_attempt'],1)
            self.assertEqual(selected[1]['response_path'],'attempts/007/response.bin')
            self.assertNotEqual(selected[0]['sha256'],selected[1]['sha256'])
            for state in result['samples'].values():
                self.assertEqual(state['trajectory'][-1]['checked_inputs'],1824)
                self.assertFalse(set(state)&{'history','keys','text','report'})

    def test_repair_feedback_and_program_cycles_use_only_same_chain(self):
        states=self.r.initial_states()
        source=(HERE.parent/'amr-deepseek-pilot/run/records/004/response.bin').read_bytes()
        report=self.r.d.assess(source.decode(),12)
        first=states['P1-R1']
        self.r.advance(first,source,report,None,{'fatal':None,'usage_summary':None},'first')
        prompt,feedback=self.r.prompt_for(first)
        self.assertIn(source.decode(),json.loads(prompt.split('data, not instructions.\n')[1].split('\n\n')[0])['previous_output']['utf8_text'])
        self.assertTrue(feedback['current_examples'])
        self.assertEqual(first['history'],[])
        second_source=source.decode()+'\n'
        self.r.advance(first,second_source.encode(),self.r.d.assess(second_source,12),feedback,
                       {'fatal':None,'usage_summary':None},'second')
        self.assertEqual(first['stop'],'cycle')
        self.assertTrue(first['history'])
        self.assertEqual(states['P2-R1']['history'],[])
        self.assertEqual(states['P2-R1']['keys'],[])
        self.assertIsNone(self.r.prompt_for(states['P2-R1'])[1])

    def test_payload_byte_limit_is_enforced(self):
        payload=self.r.payload_for('bounded prompt','P1-R1')
        self.r.validate_payload(payload)
        with self.assertRaises(ValueError):
            self.r.validate_payload(self.r.payload_for('x'*65537,'P1-R1'))

    def test_old_run_inventories_and_dependencies_are_frozen_before_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            self.r.initialize(run,True)
            for name,path in self.r.historical_runs().items():
                self.assertEqual(self.r.read_json(run/(name+'-inventory.json')),self.r.inventory(path))
            frozen=self.r.read_json(run/'frozen-inputs.json')
            for name in ('forge','thinking','extended'):
                inherited=self.r.read_json(self.r.historical_runs()[name]/'frozen-inputs.json')
                self.assertEqual(self.r.read_json(run/(name+'-frozen-inputs.json')),inherited)
                for path,digest in inherited.items():
                    self.assertEqual(frozen[path],digest)
            protocol=self.r.read_json(run/'protocol.json')
            self.assertEqual(protocol['id'],'amr-independent-replication/v1')
            self.assertEqual(protocol['sample_ids'],list(IDS))
            self.assertNotIn('seed',protocol)
            self.assertFalse((run/'starting-response.bin').exists())
            self.r.verify_inputs(run)

    def test_historical_dependency_drift_prevents_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            real_sha=self.r.sha
            old=self.r.EXTENDED_RUN.parent/'runner.py'
            def drift(path): return '0'*64 if Path(path)==old else real_sha(path)
            with patch.object(self.r,'sha',side_effect=drift):
                with self.assertRaisesRegex(RuntimeError,'extended dependency changed'):
                    self.r.initialize(run,True)
            self.assertFalse(run.exists())

    def test_old_extended_physics_drift_stops_worker_before_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            attempt=self.pending(run)
            real_inventory=self.r.inventory
            def drift(path):
                result=real_inventory(path)
                if Path(path)==self.r.EXTENDED_PHYSICS:
                    result['normal_A_source.json']='0'*64
                return result
            with patch.object(self.r,'RUN',run),patch.object(self.r,'inventory',side_effect=drift),patch.object(self.r,'post_once') as post:
                with self.assertRaisesRegex(RuntimeError,'historical extended-closed-loop run changed'):
                    self.r.network_child('not-a-credential',attempt)
                post.assert_not_called()

    def test_invalid_usage_stops_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self.r.execute('not-a-credential',run=Path(tmp)/'run',
                                 worker=self.fixture_worker(usage=False),fixture=True)
            self.assertEqual(result['new_calls'],1)
            self.assertEqual(result['stop'],'invalid_usage')
            self.assertEqual(result['selected_sources'],[])

    def test_fatal_after_acceptance_still_disables_all_physics_selection(self):
        def work(key,attempt):
            req=self.r.read_json(attempt/'request.json')
            return self.fixture_worker(self.accepted_source(),finish='stop' if req['sample_id']=='P1-R1' else 'length')(key,attempt)
        with tempfile.TemporaryDirectory() as tmp:
            result=self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=work,fixture=True)
            self.assertEqual(result['new_calls'],2)
            self.assertEqual(result['stop'],'truncated')
            self.assertEqual(result['initial_accepted_count'],1)
            self.assertEqual(result['eventually_accepted_count'],1)
            self.assertEqual(result['selected_sources'],[])

    def test_oversized_repair_stops_after_all_six_initials_without_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            result=self.r.execute('not-a-credential',run=run,
                                 worker=self.fixture_worker('x'*70000),fixture=True)
            self.assertEqual(result['new_calls'],6)
            self.assertEqual(result['stop'],'payload_limit_stop')
            self.assertTrue((run/'evidence-sha256.json').exists())

    def pending(self,run):
        self.r.initialize(run,False)
        folder=run/'attempts/001'
        folder.mkdir()
        prompt,feedback=self.r.prompt_for(self.r.initial_states()['P1-R1'])
        payload=self.r.payload_for(prompt,'P1-R1')
        (folder/'prompt.txt').write_bytes(prompt.encode())
        self.r.write_json(folder/'feedback.json',feedback)
        self.r.write_json(folder/'request.json',{'sample_id':'P1-R1','attempt':0,'phase':'initial'})
        self.r.write_json(folder/'http-request.json',payload)
        self.r.write_json(folder/'preflight.json',{'max_posts':1,'retries':0,
            'payload_sha256':self.r.sha(folder/'http-request.json')})
        self.r.write_json(folder/'dispatch-intent.json',{'max_posts':1,'retries':0})
        return folder

    def test_worker_claim_is_single_use_and_rejects_payload_prompt_dispatch_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run'
            attempt=self.pending(run)
            with patch.object(self.r,'RUN',run),patch.object(self.r,'post_once') as post:
                self.r.network_child('not-a-credential',attempt)
                with self.assertRaises(FileExistsError):
                    self.r.network_child('not-a-credential',attempt)
                post.assert_called_once_with('not-a-credential',attempt)
        for kind in ('payload','prompt','dispatch'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                run=Path(tmp)/'run'
                attempt=self.pending(run)
                if kind=='payload':
                    payload=self.r.read_json(attempt/'http-request.json')
                    payload['thinking']={'type':'disabled'}
                    (attempt/'http-request.json').write_bytes(self.r.json_bytes(payload))
                elif kind=='prompt': (attempt/'prompt.txt').write_text('tampered')
                else:
                    preflight=self.r.read_json(attempt/'preflight.json')
                    preflight['max_posts']=2
                    (attempt/'preflight.json').write_bytes(self.r.json_bytes(preflight))
                with patch.object(self.r,'RUN',run),patch.object(self.r,'post_once') as post:
                    with self.assertRaises(RuntimeError): self.r.network_child('not-a-credential',attempt)
                    post.assert_not_called()


    def test_total_completion_tokens_include_reasoning_in_usage_and_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            envelope = {'model':'deepseek-flash', 'usage':{'prompt_tokens':100, 'completion_tokens':60000,
                        'completion_tokens_details':{'reasoning_tokens':59000}},
                        'choices':[{'finish_reason':'stop','message':{'content':'{}','reasoning_content':'private fixture'}}]}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            payload = self.r.payload_for('x', 'P1-R1')
            raw, decoded, usage_summary, fatal = self.r.decode_response(attempt, {'status':'received'}, payload)
            self.assertIsNone(fatal)
            self.assertEqual(raw, b'{}')
            self.assertEqual(usage_summary, {'input_tokens':100,'output_tokens':60000,
                                           'cache_hit_tokens':0,'cache_miss_tokens':100})
            self.assertEqual(self.r.thinking_metadata(decoded, payload)['reasoning_tokens'],59000)
            envelope['usage']['completion_tokens'] = 65537
            (attempt / 'http-body.bin').write_bytes(self.r.json_bytes(envelope))
            self.assertEqual(self.r.decode_response(attempt, {'status':'received'}, payload)[3], 'output_cap_violation')

    def test_empty_reasoning_is_unconfirmed_without_rejecting_valid_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            envelope = {'model':'deepseek-flash', 'usage':{'prompt_tokens':100, 'completion_tokens':10},
                        'choices':[{'finish_reason':'stop','message':{'content':'{}','reasoning_content':''}}]}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            payload = self.r.payload_for('x','P1-R1')
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
                    self.r.payload_for('x','P1-R1'))
                self.assertEqual(fatal,'invalid_usage')
                self.assertIsNone(usage_summary)
                self.assertIsNone(self.r.thinking_metadata(envelope,
                    self.r.payload_for('x','P1-R1'))['reasoning_tokens'])

    def test_fatal_transports_and_truncation_never_retry(self):
        for worker,fatal in ((self.fixture_worker(status='transport_error'),'transport_error'),
                             (self.fixture_worker(finish='length'),'truncated')):
            with self.subTest(fatal=fatal),tempfile.TemporaryDirectory() as tmp:
                result = self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=worker,fixture=True)
                self.assertEqual(result['new_calls'],1)
                self.assertEqual(result['stop'],fatal)
                self.assertEqual(result['selected_sources'],[])

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
        state = self.r.initial_states()['P1-R1']
        report = {'accepted':False,'parse_pass':False,'full_cases':[],'failure_input_ids':[]}
        with patch.object(self.r.d,'program_key',side_effect=RecursionError):
            self.r.advance(state,b'[[[',report,{}, {'fatal':'assessment_error','usage_summary':None},'fixture')
        self.assertEqual(state['stop'],'assessment_error')

    def test_fixture_cannot_enter_live_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.r.execute('not-a-credential',run=Path(tmp)/'run',worker=self.fixture_worker())
            self.assertFalse((Path(tmp)/'run').exists())

    def test_child_wall_deadline_is_660_seconds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(self.r.subprocess,'run',side_effect=subprocess.TimeoutExpired('fixture',660)) as child:
                with self.assertRaises(subprocess.TimeoutExpired):
                    self.r.run_worker('not-a-credential',Path(tmp))
                self.assertEqual(child.call_args.kwargs['timeout'],660)

    def test_falsey_nontext_content_and_deep_json_are_fatal(self):
        for content in (False,0,[],{}):
            with self.subTest(content=content),tempfile.TemporaryDirectory() as tmp:
                attempt = Path(tmp)
                self.r.write_json(attempt/'http-body.bin',{'model':'deepseek-flash',
                    'usage':{'prompt_tokens':100,'completion_tokens':10},
                    'choices':[{'finish_reason':'stop','message':{'content':content}}]})
                self.assertEqual(self.r.decode_response(attempt,{'status':'received'},
                    self.r.payload_for('x','P1-R1'))[3],'transport_error')
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp)
            (attempt/'http-body.bin').write_bytes(b'['*10000+b']'*10000)
            self.assertEqual(self.r.decode_response(attempt,{'status':'received'},
                self.r.payload_for('x','P1-R1'))[3],'transport_error')

    def test_post_boundary_has_one_dispatch_600s_deadline_and_fixed_endpoint(self):
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
            self.r.write_json(attempt/'http-request.json',self.r.payload_for('x','P1-R1'))
            opener = Opener()
            with patch.object(self.r.smoke,'read_key',return_value='OFFLINE_FIXTURE_CREDENTIAL'),patch.object(
                    self.r.urllib.request,'build_opener',return_value=opener) as build:
                self.r.post_once('not-a-credential',attempt)
                self.assertEqual(len(opener.requests),1)
                request,timeout = opener.requests[0]
                self.assertEqual(request.full_url,'https://api.deepseek.com/chat/completions')
                self.assertEqual(request.method,'POST')
                self.assertEqual(timeout,600)
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
                self.r.write_json(attempt/'http-request.json',self.r.payload_for('x','P1-R1'))
                with patch.object(self.r.smoke,'read_key',return_value=key),patch.object(
                        self.r.urllib.request,'build_opener') as build:
                    build.return_value.open.side_effect = error
                    self.r.post_once('not-a-credential',attempt)
                for path in attempt.iterdir():
                    self.assertNotIn(key.encode(),path.read_bytes())
                self.assertEqual(self.r.read_json(attempt/'transport.json')['status'],'transport_error')


if __name__=='__main__':
    unittest.main()
