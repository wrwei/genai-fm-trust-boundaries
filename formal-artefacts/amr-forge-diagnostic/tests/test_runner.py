"""Offline tests: never load credentials or issue network requests."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('runner'), 'diagnostic runner not implemented')
        self.r = importlib.import_module('runner')

    def test_oversized_payload_never_dispatched(self):
        with self.assertRaises(ValueError):
            self.r.validate_payload(self.r.smoke.payload_for('x' * 65537))

    def test_rule_limit_prompt_changes_do_not_change_expression_depth(self):
        text = self.r.original_task(12)
        self.assertIn('at most twelve rules', text)
        self.assertIn('expression depth eight', text)
        self.assertNotIn('eight-rule', text)
        self.assertEqual(self.r.original_task(8), self.r.BASE_PROMPT.read_text(encoding='utf-8'))

    def test_original_feedback_first_prompt_exactly_reproduces_old_repair(self):
        prompt, _ = self.r.prompt_for(self.r.initial_states()['D8-O'])
        self.assertEqual(prompt.encode('utf-8'),
                         (self.r.PRIOR/'requests/005/prompt.txt').read_bytes())

    def test_four_round_ceiling_and_round_robin_order(self):
        calls = []
        def work(key, attempt):
            req = self.r.read_json(attempt/'request.json')
            calls.append((req['condition'], req['repair']))
            return self.fixture_worker(json.dumps({'invalid_unique_fixture':len(calls)}))(key, attempt)
        with tempfile.TemporaryDirectory() as folder:
            result = self.r.execute('not-a-credential', run=Path(folder)/'run', worker=work, fixture=True)
        self.assertEqual(len(calls), 16)
        self.assertEqual(calls, [(cid, i) for i in range(1,5)
                                for cid in ('D8-O','D12-O','D8-F','D12-F')])
        self.assertEqual([v['stop'] for v in result['conditions'].values()], ['repair_limit']*4)

    def fixture_worker(self, content, usage=True, status='received'):
        def work(key, attempt):
            self.assertEqual(key, 'not-a-credential')
            self.r.write_json(attempt / 'dispatch.json', {'fixture': True})
            envelope = {'model': 'deepseek-flash', 'choices': [{'finish_reason': 'stop', 'message': {'content': content}}]}
            if usage:
                envelope['usage'] = {'prompt_tokens': 2000, 'completion_tokens': 300}
            self.r.write_json(attempt / 'http-body.bin', envelope)
            return {'status': status, 'http_status': 200}
        return work

    def test_repeated_starting_candidate_stops_each_chain_after_one(self):
        with tempfile.TemporaryDirectory() as d:
            result = self.r.execute('not-a-credential', run=Path(d)/'run',
                                    worker=self.fixture_worker(self.r.START.read_text()), fixture=True)
            self.assertEqual(result['new_calls'], 4)
            self.assertEqual([v['stop'] for v in result['conditions'].values()], ['cycle']*4)
            self.assertEqual(result['mode'], 'offline-fixture')
            with self.assertRaises(FileExistsError):
                self.r.execute('not-a-credential', run=Path(d)/'run',
                               worker=self.fixture_worker(''), fixture=True)

    def test_accepted_source_stops_before_cycle_check(self):
        source = (HERE.parent/'amr-supervisor/candidates/authored_reference.json').read_text()
        with tempfile.TemporaryDirectory() as d:
            result = self.r.execute('not-a-credential', run=Path(d)/'run',
                                    worker=self.fixture_worker(source), fixture=True)
            self.assertEqual(result['new_calls'], 4)
            self.assertEqual([v['stop'] for v in result['conditions'].values()], ['accepted']*4)
            self.assertTrue(all(v['first_accepted_repair']==1 for v in result['conditions'].values()))

    def test_invalid_usage_stops_whole_batch(self):
        with tempfile.TemporaryDirectory() as d:
            result = self.r.execute('not-a-credential', run=Path(d)/'run',
                                    worker=self.fixture_worker('{}', usage=False), fixture=True)
            self.assertEqual(result['new_calls'], 1)
            self.assertEqual(result['stop'], 'invalid_usage')

    def test_nonlive_worker_cannot_be_marked_live(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                self.r.execute('not-a-credential', run=Path(d)/'run', worker=self.fixture_worker('{}'))
            self.assertFalse((Path(d)/'run').exists())

    def test_transport_failure_stops_batch_without_retry(self):
        with tempfile.TemporaryDirectory() as d:
            result = self.r.execute('not-a-credential', run=Path(d)/'run',
                                    worker=self.fixture_worker('{}', status='transport_error'), fixture=True)
            self.assertEqual(result['new_calls'], 1)
            self.assertEqual(result['stop'], 'transport_error')

    def test_malformed_envelopes_stop_without_retry(self):
        for body in (None, [], 'bad', 7, {'choices':[{'finish_reason':'stop','message':{'content':'\ud800'}}],
                                          'model':'deepseek-flash'}):
            with self.subTest(body_type=type(body).__name__), tempfile.TemporaryDirectory() as temp:
                def work(key, attempt):
                    self.r.write_json(attempt/'dispatch.json', {'fixture':True})
                    (attempt/'http-body.bin').write_text(json.dumps(body, ensure_ascii=True), encoding='utf-8')
                    return {'status':'received','http_status':200}
                result = self.r.execute('not-a-credential', run=Path(temp)/'run', worker=work, fixture=True)
                self.assertEqual(result['new_calls'], 1)
                self.assertIn(result['stop'], ('transport_error','invalid_utf8'))

    def test_fatal_assessment_never_reenters_broken_parser(self):
        state = self.r.initial_states()['D8-O']
        report = {'accepted':False,'parse_pass':False,'full_cases':[], 'failure_input_ids':[]}
        with patch.object(self.r.d, 'program_key', side_effect=RecursionError):
            self.r.advance(state, b'[[[', report, {}, {'fatal':'assessment_error','usage_summary':None}, 'fixture')
        self.assertEqual(state['stop'], 'assessment_error')
        self.assertEqual(state['repairs'], 1)


if __name__ == '__main__':
    unittest.main()
