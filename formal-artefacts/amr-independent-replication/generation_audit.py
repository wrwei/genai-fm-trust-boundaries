"""Read-only finalized generation audit; writes only sibling audit artifacts.

No provider calls, credential reads, physical episodes, or reasoning-text output.
Run after the owner confirms generation has finished, never during dispatch.
"""
from datetime import datetime
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_generation_audit_runner', HERE/'runner.py')
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)
IDS = ('P1-R1', 'P2-R1', 'P3-R1', 'P1-R2', 'P2-R2', 'P3-R2')


def check(condition, label):
    if not condition:
        raise ValueError('Audit failed: '+label)


def normalized(value):
    return json.loads(r.json_bytes(value))


def main():
    run = HERE/'run'
    check((run/'result.json').is_file() and (run/'evidence-sha256.json').is_file(), 'finalized evidence required')
    before = r.inventory(run)
    manifest = r.read_json(run/'evidence-sha256.json')
    check(manifest == {k:v for k,v in before.items() if k != 'evidence-sha256.json'}, 'complete generation manifest')
    r.verify_inputs(run)
    result, protocol = r.read_json(run/'result.json'), r.read_json(run/'protocol.json')
    check(result['mode'] == protocol['mode'] == 'live', 'live mode')
    check(result['protocol_id'] == protocol['id'] == 'amr-independent-replication/v1', 'protocol identity')
    check(protocol['sample_ids'] == list(IDS), 'sample order')
    expected_config = {'model':'deepseek-flash','max_tokens':65536,'stream':False,
                       'thinking':{'type':'enabled'},'reasoning_effort':'high'}
    check(protocol['model_configs'] == {sid:expected_config for sid in IDS}, 'model controls')
    for key, expected in {'max_repairs':2,'max_calls':18,'max_retries':0,
            'client_wall_deadline_seconds':660,'socket_timeout_seconds':600,
            'source_spec':'amr-supervisor-obligations/v1.1','rule_limit':12,
            'maximum_payload_bytes':65536,
            'endpoint':'https://api.deepseek.com/chat/completions'}.items():
        check(protocol[key] == expected, 'protocol '+key)
    check(r.sha(HERE/'runner.py') == 'dfeb7112ce7a50656824cea47f426d0dc070d8c469eebc5cd1b82f9e313476b9', 'postprocessed runner identity')
    states = r.initial_states()
    chains = {sid:{'calls':0,'stop':None,'keys':[],'accepted_response':None,
                    'first_accepted_attempt':None,'initial_accepted':None} for sid in IDS}
    rows = []
    behavior_classes, sample_behavior, accepted_ast_keys, accepted_step_keys = {}, {}, set(), set()
    folders = sorted((run/'attempts').iterdir())
    check(len(folders) <= 18, 'call ceiling')
    for sequence, folder in enumerate(folders, 1):
        check(folder.is_dir() and folder.name == f'{sequence:03d}', 'consecutive attempt directories')
        slots = [(sid,attempt) for attempt in range(3) for sid in IDS
                 if chains[sid]['stop'] is None and chains[sid]['calls'] == attempt]
        check(bool(slots), 'request after terminal state')
        sid, attempt = slots[0]
        out, req = r.read_json(folder/'outcome.json'), r.read_json(folder/'request.json')
        phase = 'initial' if attempt == 0 else 'repair'
        check(all(obj[k] == val for obj in (out,req) for k,val in
                  [('sample_id',sid),('attempt',attempt),('phase',phase)]), 'independent schedule')
        observed = r.inventory(folder)
        observed.pop('outcome.json')
        check(observed == out['files_sha256'], 'full attempt inventory')
        prompt, feedback = r.prompt_for(states[sid])
        if attempt == 0:
            task = (r.PROMPTS/(sid+'.txt')).read_text(encoding='utf-8')
            for old,new in [('at most eight rules','at most twelve rules'),
                    ('limit of eight','limit of twelve'),('eight-rule function limit','twelve-rule function limit')]:
                check(task.count(old) == 1, 'original wording')
                task = task.replace(old,new)
            check(prompt == task and feedback is None, 'fresh initial context')
            check((folder/'http-request.json').read_bytes() ==
                  (HERE/'egress-preview'/(sid+'.request.json')).read_bytes(), 'initial exact egress')
        payload = {**expected_config,'messages':[{'role':'user','content':prompt}]}
        body = (folder/'http-request.json').read_bytes()
        check(body == r.json_bytes(payload), 'complete payload bytes')
        check((folder/'prompt.txt').read_bytes() == prompt.encode('utf-8'), 'prompt bytes')
        check(r.read_json(folder/'feedback.json') == feedback, 'same-chain feedback')
        check(len(body) <= 65536, 'pre-dispatch payload limit')
        check(r.read_json(folder/'preflight.json') == {'max_posts':1,
            'retries':0,'payload_sha256':r.sha(folder/'http-request.json')}, 'preflight record')
        intent, dispatch = r.read_json(folder/'dispatch-intent.json'), r.read_json(folder/'dispatch.json')
        check(intent['max_posts'] == 1 and intent['retries'] == 0, 'single dispatch intent')
        check(dispatch['maximum_posts'] == 1 and dispatch['retries'] == 0 and
              dispatch['endpoint'] == protocol['endpoint'], 'dispatch controls')
        check(set(r.read_json(folder/'worker-claim.json')) == {'utc'}, 'worker claim')
        transport = r.read_json(folder/'transport.json')
        raw, envelope, usage_summary, fatal = r.decode_response(folder,transport,payload)
        check(raw == (folder/'response.bin').read_bytes(), 'provider final content bytes')
        check(usage_summary == out['usage_summary'] and fatal == out['fatal'], 'decoded usage and status')
        check(out['thinking'] == r.thinking_metadata(envelope,payload), 'reasoning metadata only')
        for outkey, envkey in [('provider_model','model'),('fingerprint','system_fingerprint'),('provider_request_id','id')]:
            check(out[outkey] == envelope.get(envkey), 'provider '+outkey)
        if fatal is None:
            check(transport == {'status':'received','http_status':200,
                'credential_echo_redacted':False,'body_limit_exceeded':False}, 'successful transport')
        fresh = normalized(r.d.assess(raw.decode('utf-8'),12))
        archived = json.loads(gzip.decompress((folder/'assessment.json.gz').read_bytes()))
        check(fresh == archived, 'all fresh assessment fields and full cases')
        if fresh['parse_pass']:
            check(fresh['checked_inputs'] == 1824, 'complete finite-domain assessment')
        accepted = fresh['accepted'] and fatal is None
        check(out['accepted'] == accepted, 'acceptance status')
        if accepted:
            selection = [{'input_id':c['input_id'],'facts':c['facts'],'actual':c['actual']}
                         for c in fresh['full_cases'] if c['function'] == 'select']
            steps = [{'input_id':c['input_id'],'actual':c['actual']}
                     for c in fresh['full_cases'] if c['function'] == 'step']
            check(len(selection) == 32 and len(steps) == 1792, 'behavior partition coverage')
            selection_key = hashlib.sha256(r.json_bytes(selection)).hexdigest()
            step_key = hashlib.sha256(r.json_bytes(steps)).hexdigest()
            if selection_key not in behavior_classes:
                behavior_classes[selection_key] = {'class_id':f'select_behavior_{len(behavior_classes)+1:02d}',
                    'sha256':selection_key,'sample_ids':[],'selection_outputs':selection}
            behavior_classes[selection_key]['sample_ids'].append(sid)
            sample_behavior[sid] = {'selection_class':behavior_classes[selection_key]['class_id'],
                'selection_sha256':selection_key,'step_sha256':step_key,
                'raw_sha256':r.sha(folder/'response.bin'),'accepted_attempt':attempt}
            accepted_ast_keys.add(r.d.program_key(raw.decode('utf-8'),12))
            accepted_step_keys.add(step_key)
        if usage_summary is not None:
            usage = envelope['usage']
            inp, completion = usage['prompt_tokens'], usage['completion_tokens']
            hit = usage.get('prompt_cache_hit_tokens',0)
            miss = usage.get('prompt_cache_miss_tokens',inp-hit)
            check(all(type(x) is int and x >= 0 for x in (inp,completion,hit,miss)) and hit+miss == inp, 'usage counts')
            check((inp,completion,hit,miss) == (usage_summary['input_tokens'],usage_summary['output_tokens'],usage_summary['cache_hit_tokens'],usage_summary['cache_miss_tokens']), 'token identity')
            if fatal is None:
                check(completion <= 65536, 'output token limit')
        chain = chains[sid]
        key = ('raw-sha256:'+r.sha(folder/'response.bin') if fatal else r.d.program_key(raw.decode('utf-8'),12))
        if attempt == 0:
            chain['initial_accepted'] = accepted
        if fatal:
            chain['stop'] = fatal
            check(sequence == len(folders) and result['stop'] == fatal, 'fatal stops entire batch')
        elif accepted:
            chain.update(stop='accepted',accepted_response=f'attempts/{folder.name}/response.bin',first_accepted_attempt=attempt)
        elif key in chain['keys']:
            chain['stop'] = 'cycle'
        elif attempt == 2:
            chain['stop'] = 'repair_limit'
        chain['keys'].append(key)
        chain['calls'] += 1
        r.advance(states[sid],raw,fresh,feedback,out,f'attempts/{folder.name}/response.bin')
        elapsed = (datetime.fromisoformat(out['finished_at_utc'])-datetime.fromisoformat(out['started_at_utc'])).total_seconds()
        check(elapsed >= 0, 'monotonic recorded duration')
        rows.append({'sequence':folder.name,'sample_id':sid,'attempt':attempt,'phase':phase,
            'accepted':accepted,'fatal':fatal,'parse_pass':fresh['parse_pass'],'checked_inputs':fresh['checked_inputs'],
            'source_violation_inputs':fresh['source_violation_inputs'] if fresh['parse_pass'] else None,
            'model_violation_inputs':fresh['model_violation_inputs'] if fresh['parse_pass'] else None,
            'correspondence_mismatches':fresh['correspondence_mismatches'] if fresh['parse_pass'] else None,
            'source_sha256':r.sha(folder/'response.bin'),'response_bytes':len(raw),
            'rule_counts':fresh.get('rule_counts'),
            'usage_summary':usage_summary,'thinking_metadata':out['thinking'],'fingerprint':out['fingerprint'],
            'elapsed_seconds':elapsed,'full_assessment_match':True})
    check(result['samples'] == normalized(r.public_states(states)), 'full replayed states and trajectories')
    for sid, chain in chains.items():
        check(all(result['samples'][sid][k] == chain[k] for k in
            ('calls','stop','accepted_response','first_accepted_attempt','initial_accepted')), 'independent chain summary')
    selected = {}
    if result['stop'] == 'protocol_complete':
        check(all(c['stop'] in ('accepted','cycle','repair_limit') for c in chains.values()), 'complete terminal batch')
        for sid,c in chains.items():
            if c['stop'] == 'accepted':
                digest = r.sha(run/c['accepted_response'])
                if digest not in selected:
                    selected[digest] = {'sha256':digest,'response_path':c['accepted_response'],
                        'representative_sample':sid,'first_accepted_attempt':c['first_accepted_attempt'],'sample_ids':[]}
                selected[digest]['sample_ids'].append(sid)
    check(result['selected_sources'] == list(selected.values()), 'independent exact-byte source mapping')
    check(result['new_calls'] == result['network_dispatches'] == len(folders), 'call and dispatch counts')
    check(result['initial_accepted_count'] == sum(c['initial_accepted'] is True for c in chains.values()), 'initial count')
    check(result['eventually_accepted_count'] == sum(c['stop'] == 'accepted' for c in chains.values()), 'eventual count')
    if result['stop'] == 'payload_limit_stop':
        sid,_ = r.next_slot(states)
        check(len(r.json_bytes(r.payload_for(r.prompt_for(states[sid])[0],sid))) > 65536, 'payload stop boundary')
    r.verify_inputs(run)
    check(r.inventory(run) == before, 'generation unchanged after audit')
    audit = {'disposition':'verified','audited_at_utc':r.smoke.utc_now(),'network_calls':0,
        'generation_manifest_files':len(manifest),'frozen_inputs':len(r.read_json(run/'frozen-inputs.json')),
        'full_assessments_recomputed':len(rows),'generation_unchanged':True,'rows':rows,
        'stop':result['stop'],'initial_accepted_count':result['initial_accepted_count'],
        'eventually_accepted_count':result['eventually_accepted_count'],'selected_sources':list(selected.values()),
        'behavior_diagnostic':{'selection_input_count':32,'step_input_count':1792,
            'selection_classes':list(behavior_classes.values()),'sample_mapping':sample_behavior,
            'unique_accepted_ast_count':len(accepted_ast_keys),'unique_accepted_step_behavior_count':len(accepted_step_keys),
            'all_accepted_step_behaviors_equal':len(accepted_step_keys) == 1 if accepted_step_keys else None,
            'scope':'Descriptive accepted-program output equivalence only; no change to acceptance or exact-byte physical selection.'},
        'result_sha256':r.sha(run/'result.json'),
        'manifest_sha256':r.sha(run/'evidence-sha256.json'),'audit_script_sha256':r.sha(Path(__file__)),
        'scope':'One AMR task, three wordings, six fresh requests; no physical or hardware claim.'}
    (HERE/'generation-audit.json').write_bytes(r.json_bytes(audit))
    print(json.dumps({k:v for k,v in audit.items() if k not in ('rows','selected_sources','behavior_diagnostic')},indent=2))
    return audit


if __name__ == '__main__':
    main()
