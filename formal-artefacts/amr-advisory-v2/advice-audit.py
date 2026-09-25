"""Offline postflight audit of the frozen six-call advice evidence."""
from __future__ import annotations

from datetime import datetime
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import advice_trial as trial
from advice_mailbox import AdviceMailbox


def load(path):
    return json.loads(Path(path).read_bytes())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(evidence):
    evidence = Path(evidence).resolve()
    protocol = trial.validate_batch(evidence)
    approach_raw = (evidence / 'approach.json').read_bytes()
    approach = json.loads(approach_raw)
    summary = load(evidence / 'summary.json')
    batch = load(evidence / 'batch-dispatch-intent.json')

    require(batch == {'started_utc': batch.get('started_utc'), 'maximum_requests': 6, 'retries': 0},
            'invalid batch dispatch marker')
    datetime.fromisoformat(batch['started_utc'])
    require(protocol['approach_sha256'] == digest(approach_raw), 'approach digest mismatch')
    require(approach == trial.approach_trace(), 'approach does not reproduce')
    require(approach[-1]['time'] == protocol['window_seconds'] == 3.63,
            'unexpected approach cutoff')
    require(all(robot['speed'] == 0 for robot in approach[-1]['robots'].values()),
            'staging approach did not end halted')

    rows = []
    input_total = output_total = 0
    request_ids = set()
    for index, sample in enumerate(trial.SAMPLES):
        folder = evidence / f'{index + 1:03}'
        expected_names = {'dispatch-intent.json', 'dispatch.json', 'http-body.bin',
                          'http-request.json', 'outcome.json', 'prompt.txt',
                          'response.bin', 'transport.json'}
        require({p.name for p in folder.iterdir() if p.is_file()} == expected_names,
                f'{sample}: unexpected or missing attempt files')

        request_raw = (folder / 'http-request.json').read_bytes()
        request = json.loads(request_raw)
        require(request == trial.payload_for(index), f'{sample}: request payload changed')
        require(digest(request_raw) == protocol['samples'][index]['request_sha256'],
                f'{sample}: request identity mismatch')
        require((folder / 'prompt.txt').read_text(encoding='utf-8') == request['messages'][0]['content'],
                f'{sample}: prompt copy mismatch')

        intent = load(folder / 'dispatch-intent.json')
        dispatch = load(folder / 'dispatch.json')
        transport = load(folder / 'transport.json')
        require(intent['index'] == index and intent['sample'] == sample and
                intent['posts_at_most'] == 1 and intent['retries'] == 0,
                f'{sample}: invalid dispatch intent')
        require(dispatch['endpoint'] == trial.transport.ENDPOINT and
                dispatch['maximum_posts'] == 1 and dispatch['retries'] == 0,
                f'{sample}: invalid worker dispatch marker')
        require(datetime.fromisoformat(intent['started_utc']) <= datetime.fromisoformat(dispatch['started_at_utc']),
                f'{sample}: dispatch timestamp order invalid')
        require(transport == {'status': 'received', 'http_status': 200,
                              'credential_echo_redacted': False, 'body_limit_exceeded': False},
                f'{sample}: transport not cleanly received')

        body_raw = (folder / 'http-body.bin').read_bytes()
        body = json.loads(body_raw)
        choices = body.get('choices')
        require(type(choices) is list and len(choices) == 1 and choices[0].get('finish_reason') == 'stop',
                f'{sample}: completion shape invalid')
        content = choices[0].get('message', {}).get('content')
        response_raw = (folder / 'response.bin').read_bytes()
        require(type(content) is str and response_raw == content.encode('utf-8'),
                f'{sample}: raw response mismatch')
        box = AdviceMailbox('request-1', 'fixed-tasks-A0-B1')
        require(box.receive('request-1', 'fixed-tasks-A0-B1', content) == 'accepted' and
                box.latch()['advice'] == 'B', f'{sample}: strict mailbox did not accept B')

        usage_summary = trial.transport.usage_summary(body.get('usage'))
        require(usage_summary is not None, f'{sample}: invalid usage')
        outcome = load(folder / 'outcome.json')
        result = outcome['result']
        decision = outcome['decision']
        require(result['content'] == content and result['usage'] == body['usage'] and
                result['usage_summary'] == usage_summary and result['provider_model'] == body.get('model') and
                result['request_id'] == body.get('id') and result['fingerprint'] == body.get('system_fingerprint') and
                result['fatal'] is None, f'{sample}: outcome/result mismatch')
        require(result['request_id'] and result['request_id'] not in request_ids,
                f'{sample}: missing or duplicate provider request id')
        request_ids.add(result['request_id'])

        cutoff = protocol['window_seconds']
        arrival = result['arrival_seconds']
        decision_wall = outcome['decision_wall_seconds']
        pacing_lag = outcome['max_pacing_lag_seconds']
        require(0 <= arrival <= cutoff <= decision_wall, f'{sample}: timing order invalid')
        require(outcome['planned_window_seconds'] == cutoff, f'{sample}: cutoff record mismatch')
        require(decision['adoption'] == 'accepted' and decision['latch']['advice'] == 'B' and
                decision['latch']['reason'] == 'valid_advice', f'{sample}: B advice not latched')
        require(decision['source']['source_id'] == trial.FROZEN_SOURCE_SHA and
                outcome['actual_source_id'] == trial.FROZEN_SOURCE_SHA,
                f'{sample}: source identity mismatch')
        require(decision['source']['facts'] == {'OwnerFree': True, 'RequestA': True, 'RequestB': True,
                                                'PreferA': False, 'PreferB': True} and
                decision['source']['raw_action'] == 'SelectB' and decision['owner'] == 'B' and
                decision['events'] == [['Grant', 'B']], f'{sample}: source-driven B grant mismatch')

        usage = body['usage']
        require(usage['total_tokens'] == usage['prompt_tokens'] + usage['completion_tokens'],
                f'{sample}: token total mismatch')
        input_total += usage['prompt_tokens']
        output_total += usage['completion_tokens']
        rows.append(dict(sample=sample, request_sha256=digest(request_raw),
                         http_body_sha256=digest(body_raw),
                         response_sha256=digest(response_raw), raw_content=content,
                         request_id=result['request_id'], input_tokens=usage['prompt_tokens'],
                         output_tokens=usage['completion_tokens'],
                         arrival_seconds=arrival, cutoff_seconds=cutoff,
                         response_margin_seconds=cutoff-arrival,
                         decision_wall_seconds=decision_wall,
                         post_cutoff_decision_seconds=decision_wall-cutoff,
                         max_pacing_lag_seconds=pacing_lag, mailbox='accepted:B',
                         raw_source_action='SelectB', owner='B'))

    require(summary['requests'] == 6 and summary['complete'] is True and
            summary['results'] == [load(evidence / f'{i:03}' / 'outcome.json') for i in range(1, 7)],
            'summary result set mismatch')
    arrivals = [row['arrival_seconds'] for row in rows]
    decision_overruns = [row['post_cutoff_decision_seconds'] for row in rows]
    pacing = [row['max_pacing_lag_seconds'] for row in rows]
    return dict(schema='amr-advisory-v2/advice-postflight-audit/v1', **{'pass': True},
                evidence_path=evidence.relative_to(ROOT).as_posix(), samples=rows,
                totals=dict(requests=6, successful_http_200=6, accepted_strict_B=6,
                            source_select_B=6, owner_B=6, input_tokens=input_total,
                            output_tokens=output_total),
                timing=dict(cutoff_seconds=protocol['window_seconds'],
                            arrival_min_seconds=min(arrivals), arrival_max_seconds=max(arrivals),
                            response_margin_min_seconds=min(protocol['window_seconds']-v for v in arrivals),
                            decision_wall_min_seconds=min(r['decision_wall_seconds'] for r in rows),
                            decision_wall_max_seconds=max(r['decision_wall_seconds'] for r in rows),
                            post_cutoff_decision_min_seconds=min(decision_overruns),
                            post_cutoff_decision_max_seconds=max(decision_overruns),
                            pacing_lag_max_seconds=max(pacing)),
                claims_scope='live provider replies during paced staging and source-driven authorization; '
                             'not full real-time physical control or mission completion')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, default=HERE/'evidence/advice')
    parser.add_argument('--output', type=Path, default=HERE/'evidence/advice-audit.json')
    args = parser.parse_args()
    result = audit(args.evidence)
    trial.write_json(args.output, result)
    print(json.dumps({'pass': result['pass'], 'totals': result['totals'],
                      'timing': result['timing']}, ensure_ascii=False))
