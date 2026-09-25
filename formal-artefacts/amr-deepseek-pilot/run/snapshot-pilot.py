"""Bounded continuation of the frozen six-chain DeepSeek experiment; no retries."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent / 'amr-deepseek-smoke'
PRIOR = SMOKE / 'run'
RUN = HERE / 'run'
sys.path.insert(0, str(SMOKE))
import smoke

trial = smoke.trial
CONFIG = smoke.CONFIG
BUDGET_CNY = Decimal('10')
RESERVE_CNY = Decimal('2.113536')
MAX_ATTEMPTS = 18
write_json = smoke.write_json


def read_json(path):
    return trial._read_json(Path(path))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(Path(folder).rglob('*')) if p.is_file()}


def known_cost(records):
    return sum((Decimal(str(r['metadata']['cost'])) for r in records
                if r['metadata']['cost'] is not None), Decimal(0))


def initialize(*, run=None, prior=None):
    """Import the one recorded response byte-for-byte into a new exclusive run."""
    run = Path(run or RUN).resolve()
    prior = Path(prior or PRIOR).resolve()
    if run.exists():
        raise FileExistsError('continuation run already exists')
    checked = smoke.verify_preparation()
    evidence = read_json(prior / 'evidence-sha256.json')
    original_inventory = inventory(prior)
    if evidence != {k: v for k, v in original_inventory.items() if k != 'evidence-sha256.json'}:
        raise RuntimeError('prior evidence hash inventory mismatch')
    manifest = trial._manifest(prior)
    summary = trial.summarize(prior)
    requests, records = trial._ledger(prior)
    if (manifest['config'] != CONFIG or manifest['protocol']['max_repairs'] != 2 or
            manifest['protocol']['max_attempts'] != MAX_ATTEMPTS or
            len(requests) != 1 or len(records) != 1 or records[0]['sample_id'] != 'P1-R1' or
            records[0]['attempt_index'] != 0 or records[0]['accepted'] or
            records[0]['metadata']['status'] != 'ok' or records[0]['violation_flags'] or
            known_cost(records) != Decimal('0.004396') or
            read_json(prior / 'smoke-result.json')['trial_summary'] != summary):
        raise RuntimeError('prior run is not the authorized one-response continuation')
    run.mkdir()  # The exclusive directory is the lifetime execution lock.
    for name in ('frozen', 'requests', 'records'):
        shutil.copytree(prior / name, run / name)
    (run / 'lineage').mkdir()
    shutil.copy2(prior / 'manifest.json', run / 'lineage/prior-manifest.json')
    shutil.copy2(prior / 'evidence-sha256.json', run / 'lineage/prior-evidence-sha256.json')
    write_json(run / 'lineage/prior-files-sha256.json', original_inventory)
    previous_hash = manifest.pop('manifest_sha256')
    manifest['lineage'] = {
        'previous_run': str(prior), 'previous_manifest_sha256': previous_hash,
        'previous_manifest_file_sha256': original_inventory['manifest.json'],
        'imported_record_sha256': records[0]['record_sha256'],
        'imported_response_sha256': records[0]['raw_sha256'],
        'inherited_attempts': 1, 'inherited_cost_cny': 0.004396,
        'cost_accounting': 'inherited records are included once in the trial ledger',
        'continued_at_utc': smoke.utc_now()}
    for entry in manifest['frozen_files']:
        entry['snapshot_path'] = str(run / 'frozen' / Path(entry['snapshot_path']).name)
    manifest['manifest_sha256'] = trial._sha(trial._json_bytes(manifest))
    trial._atomic_write(run / 'manifest.json', trial._json_bytes(manifest))
    (run / 'transport').mkdir()
    for source, target in [(Path(__file__), 'snapshot-pilot.py'), (SMOKE / 'smoke.py', 'snapshot-smoke.py')]:
        with (run / target).open('xb') as stream:
            stream.write(source.read_bytes())
    write_json(run / 'authorization.json', {
        'scope': 'user-authorized fixed six-chain continuation including inherited smoke response',
        'created_at_utc': smoke.utc_now(), 'endpoint': smoke.ENDPOINT, 'config': CONFIG,
        'budget_total_cny': 10, 'inherited_cost_cny': 0.004396,
        'per_call_reserve_cny': float(RESERVE_CNY), 'max_total_attempts': 18,
        'max_new_network_posts': 17, 'max_repairs_per_sample': 2, 'max_retries': 0,
        'client_wall_deadline_seconds': 90, 'historical_preparation_inputs_verified': checked,
        'prompt_source': 'trial.prepare_request only; no manual feedback',
        'tariff_source': 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/',
        'cost_basis': 'reported usage at peak tariff upper estimate; not invoice'})
    frozen = ['manifest.json', 'authorization.json', 'snapshot-pilot.py', 'snapshot-smoke.py',
              'lineage/prior-manifest.json', 'lineage/prior-evidence-sha256.json', 'lineage/prior-files-sha256.json']
    write_json(run / 'runner-sha256.json', {name: digest(run / name) for name in frozen})
    trial.summarize(run)
    return manifest


def verify_ready(run):
    for name, expected in read_json(run / 'runner-sha256.json').items():
        if digest(run / name) != expected:
            raise RuntimeError('continuation input changed')
    if (digest(Path(__file__)) != digest(run / 'snapshot-pilot.py') or
            digest(SMOKE / 'smoke.py') != digest(run / 'snapshot-smoke.py')):
        raise RuntimeError('runner source changed')
    smoke.verify_preparation()
    manifest = trial._manifest(run)
    if (manifest['config'] != CONFIG or manifest['protocol']['max_repairs'] != 2 or
            manifest['protocol']['max_attempts'] != MAX_ATTEMPTS):
        raise RuntimeError('frozen authorization changed')
    prior = Path(manifest['lineage']['previous_run'])
    if inventory(prior) != read_json(run / 'lineage/prior-files-sha256.json'):
        raise RuntimeError('original smoke evidence changed')
    return trial._ledger(run)


def preflight(run, attempt, request, records):
    return {'sample_id': request['sample_id'], 'attempt_index': request['attempt_index'],
            'request_record_sha256': request['request_record_sha256'],
            'http_request_sha256': digest(attempt / 'http-request.json'),
            'authorization_sha256': digest(run / 'authorization.json'),
            'known_cumulative_cost_cny': float(known_cost(records)),
            'reserved_cny': float(RESERVE_CNY), 'total_budget_cny': 10,
            'ledger_attempt_number': len(records) + 1, 'maximum_posts': 1, 'retries': 0}


def network_child(key_path, attempt):
    """Fixed-path worker verifies authorization and the exact pending prompt before POST."""
    attempt = Path(attempt).resolve()
    run = RUN.resolve()
    if (attempt.parent != run / 'transport' or not attempt.name.isdigit() or
            attempt.name != f'{int(attempt.name):03d}' or not 2 <= int(attempt.name) <= 18):
        raise RuntimeError('worker attempt path rejected')
    if (run / 'summary.json').exists():
        raise RuntimeError('run already finished')
    # A second child for the same attempt cannot dispatch, even if the first failed preflight.
    write_json(attempt / 'worker-claim.json', {'claimed_at_utc': smoke.utc_now()})
    requests, records = verify_ready(run)
    if (len(requests) != len(records) + 1 or int(attempt.name) != len(requests) or
            any(r['metadata']['cost'] is None or r['metadata']['status'] != 'ok' or
                r['violation_flags'] for r in records) or
            known_cost(records) + RESERVE_CNY > BUDGET_CNY):
        raise RuntimeError('worker budget or ledger preflight failed')
    request = requests[-1]
    prompt = (run / request['prompt_path']).read_bytes().decode('utf-8')
    if (read_json(attempt / 'http-request.json') != smoke.payload_for(prompt) or
            read_json(attempt / 'preflight.json') != preflight(run, attempt, request, records)):
        raise RuntimeError('worker prompt or authorization mismatch')
    smoke.network_child(key_path, attempt)  # Sole POST helper: no proxies, redirects, or retries.


def run_worker(key_path, attempt):
    completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker',
                                '--key-file', str(key_path), '--attempt', str(attempt)],
                               timeout=90, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if completed.returncode != 0 or not (attempt / 'transport.json').exists():
        return {'status': 'transport_error', 'http_status': None, 'error_type': 'ChildFailed'}
    return read_json(attempt / 'transport.json')


def record_attempt(run, attempt, request, transport, started, finished):
    envelope, content, cost = {}, '', None
    status = 'timeout' if transport.get('status') == 'timeout' else 'transport_error'
    if (attempt / 'http-body.bin').exists():
        try:
            envelope = read_json(attempt / 'http-body.bin')
            cost = smoke.usage_cost(envelope.get('usage'))
            choices = envelope.get('choices', [])
            if len(choices) != 1:
                raise ValueError('single choice required')
            message = choices[0]['message']
            content = message.get('content')
            if type(content) is not str:
                raise ValueError('text content required')
            if transport.get('status') == 'received' and envelope.get('model') == smoke.MODEL:
                status = {'stop': 'ok', 'length': 'truncated', 'content_filter': 'refusal'}.get(
                    choices[0].get('finish_reason'), 'transport_error')
                if message.get('tool_calls') or message.get('refusal'):
                    status = 'refusal'
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError):
            status, content = 'transport_error', ''
    raw = content.encode('utf-8')
    with (attempt / 'assistant-response.bin').open('xb') as stream:
        stream.write(raw)
    write_json(attempt / 'response-envelope.json', envelope)
    write_json(attempt / 'response-details.json', {
        'started_at_utc': started, 'finished_at_utc': finished, 'transport': transport,
        'response_status': status, 'provider_reported_model': envelope.get('model'),
        'provider_system_fingerprint': envelope.get('system_fingerprint'),
        'usage': envelope.get('usage'), 'cost_estimate': cost})
    metadata = {'sample_id': request['sample_id'], 'attempt_index': request['attempt_index'],
                'status': status, 'provider': CONFIG['provider'], 'model_id': smoke.MODEL,
                'decoding': CONFIG['decoding'], 'requested_max_output_tokens': smoke.MAX_OUTPUT,
                'request_sha256': request['prompt_sha256'],
                'request_id': str(envelope.get('id') or 'not-returned-single-attempt'),
                'started_at_utc': started, 'finished_at_utc': finished,
                'input_tokens': cost['input_tokens'] if cost else None,
                'output_tokens': cost['output_tokens'] if cost else None,
                'cost': cost['peak_upper_cny'] if cost else None}
    record = trial.record_response(run, raw, metadata)
    assessment = record['assessment']
    print(f"{request['sample_id']} attempt={request['attempt_index']} parse={assessment.get('parse_pass')} "
          f"source={assessment.get('source_violation_inputs', 0)} model={assessment.get('model_violation_inputs', 0)} "
          f"correspondence={assessment.get('correspondence_mismatches', 0)} "
          f"accepted={record['accepted']} cost_cny={metadata['cost']}", flush=True)
    if status != 'ok':
        return status
    if cost is None:
        return 'unknown_cost'
    if record['violation_flags']:
        return record['violation_flags'][0]
    if cost['input_tokens'] > 1048576:
        return 'input_token_reservation_violation'
    return None


def execute(key_path, *, run=None, prior=None, worker=run_worker):
    run = Path(run or RUN).resolve()
    initialize(run=run, prior=prior)
    started = smoke.utc_now()
    attempts = 0
    stopped = 'attempt_limit'
    error_type = None
    for _ in range(MAX_ATTEMPTS - 1):
        try:
            requests, records = verify_ready(run)
        except Exception as error:
            stopped, error_type = 'preflight_integrity_failure', type(error).__name__
            break
        if any(r['metadata']['cost'] is None for r in records):
            stopped = 'unknown_cost'
            break
        if known_cost(records) + RESERVE_CNY > BUDGET_CNY:
            stopped = 'budget_reservation_exceeds_remaining'
            break
        request = trial.prepare_request(run)
        if request is None:
            stopped = 'protocol_complete' if trial.summarize(run)['complete'] else 'protocol_stopped'
            break
        attempt = run / 'transport' / f'{len(records) + 1:03d}'
        attempt.mkdir()
        prompt = (run / request['prompt_path']).read_bytes().decode('utf-8')
        write_json(attempt / 'http-request.json', smoke.payload_for(prompt))
        write_json(attempt / 'preflight.json', preflight(run, attempt, request, records))
        sent = smoke.utc_now()
        write_json(attempt / 'dispatch-intent.json', {'started_at_utc': sent, 'maximum_posts': 1, 'retries': 0})
        attempts += 1
        try:
            transport = worker(key_path, attempt)
        except subprocess.TimeoutExpired:
            transport = {'status': 'timeout', 'http_status': None, 'error_type': 'ClientWallDeadline'}
        except Exception as error:
            transport = {'status': 'transport_error', 'http_status': None, 'error_type': type(error).__name__}
        finished = smoke.utc_now()
        if not (attempt / 'transport.json').exists():
            write_json(attempt / 'transport.json', transport)
        stopped = record_attempt(run, attempt, request, transport, sent, finished)
        if stopped:
            break
    summary = trial.summarize(run)
    if stopped is None:
        stopped = 'protocol_complete' if summary['complete'] else 'attempt_limit'
    _, records = trial._ledger(run)
    spend = known_cost(records)
    retained = RESERVE_CNY if summary['missing_cost_count'] else Decimal(0)
    prior_unchanged = inventory(Path(trial._manifest(run)['lineage']['previous_run'])) == read_json(run / 'lineage/prior-files-sha256.json')
    result = {
        'schema': 'amr-deepseek-continuation/v1', 'started_at_utc': started,
        'finished_at_utc': smoke.utc_now(), 'trial_summary': summary,
        'calls': {'inherited': 1, 'new': attempts, 'total': attempts + 1,
                  'new_dispatch_markers': len(list((run / 'transport').glob('*/dispatch.json')))},
        'budget': {'authorized_total_cny': 10, 'inherited_cost_cny': 0.004396,
                   'known_cost_cny': float(spend), 'retained_reservation_cny': float(retained),
                   'remaining_conservative_cny': float(BUDGET_CNY - spend - retained),
                   'cost_basis': 'reported usage peak upper estimate; not invoice'},
        'original_smoke_unchanged': prior_unchanged, 'stopped': stopped, 'error_type': error_type}
    write_json(run / 'summary.json', result)
    write_json(run / 'evidence-sha256.json', inventory(run))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-file', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--attempt', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.worker:
            network_child(args.key_file, args.attempt)
        else:
            if args.attempt is not None:
                raise RuntimeError('attempt path is worker-only')
            print(json.dumps(execute(args.key_file), ensure_ascii=True, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({'stopped': True, 'error_type': type(error).__name__}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
