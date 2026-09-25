"""One-time DeepSeek transport for the frozen AMR prompt; no retry path."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent / 'amr-llm-trial'
ROOT = HERE.parent.parent
sys.path.insert(0, str(BUNDLE))
import trial

ENDPOINT = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-flash'
MAX_OUTPUT = 2048
CONFIG = {'record_mode': 'live', 'provider': 'deepseek', 'model_id': MODEL,
          'model_revision': 'provider-not-exposed',
          'decoding': {'temperature': 0, 'thinking': {'type': 'disabled'}, 'stream': False},
          'max_output_tokens': MAX_OUTPUT,
          'transport': 'direct-https-chat-completions-single-post'}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')


def read_key(path):
    """Never include file contents or values in errors; never evaluate .env code."""
    allowed = {'DEEPSEEK_API_KEY', 'OPENAI_API_KEY', 'LLM_API_KEY', 'API_KEY'}
    candidates = []
    lines = [line.strip() for line in Path(path).read_text(encoding='utf-8-sig').splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    for line in lines:
        name, sep, value = line.removeprefix('export ').partition('=')
        if sep and name.strip() in allowed:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            candidates.append(value)
    if not candidates and len(lines) == 1 and '=' not in lines[0]:
        candidates = lines
    if len(set(candidates)) != 1:
        raise ValueError('exactly one unambiguous API credential required')
    value = candidates[0]
    if len(value) < 16 or any(not 33 <= ord(c) <= 126 for c in value):
        raise ValueError('invalid API credential format')
    return value


def payload_for(prompt):
    return {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': MAX_OUTPUT, **CONFIG['decoding']}


def usage_summary(usage):
    if not isinstance(usage, dict):
        return None
    inp, out = usage.get('prompt_tokens'), usage.get('completion_tokens')
    hit = usage.get('prompt_cache_hit_tokens', 0)
    if any(type(n) is not int or n < 0 for n in (inp, out, hit)) or hit > inp:
        return None
    miss = usage.get('prompt_cache_miss_tokens', inp - hit)
    if type(miss) is not int or miss < 0 or hit + miss != inp:
        return None
    return {'input_tokens': inp, 'output_tokens': out, 'cache_hit_tokens': hit,
            'cache_miss_tokens': miss}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'redirect refused', headers, fp)


def network_child(key_path, run):
    """Called only in a short-lived child. This function contains the sole POST."""
    transport = {'status': 'transport_error', 'http_status': None}
    try:
        key = read_key(key_path)
        # Exclusive marker precedes network dispatch, including failed/ambiguous calls.
        write_json(run / 'dispatch.json', {'started_at_utc': utc_now(), 'endpoint': ENDPOINT,
                                         'maximum_posts': 1, 'retries': 0})
        body = (run / 'http-request.json').read_bytes()
        request = urllib.request.Request(ENDPOINT, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=60) as response:
                raw = response.read(4 * 1024 * 1024 + 1)
                code = response.status
        except urllib.error.HTTPError as error:
            code = error.code
            raw = error.read(4 * 1024 * 1024 + 1)
        # Protect against an unexpected credential echo even in an error body.
        redacted = key.encode() in raw
        raw = raw.replace(key.encode(), b'[REDACTED]')
        with (run / 'http-body.bin').open('xb') as handle:
            handle.write(raw)
        transport = {'status': 'received' if code == 200 and not redacted and len(raw) <= 4*1024*1024
                     else 'transport_error', 'http_status': code, 'credential_echo_redacted': redacted,
                     'body_limit_exceeded': len(raw) > 4*1024*1024}
    except Exception as error:
        # Exception messages/tracebacks can include request information: do not persist them.
        transport['error_type'] = type(error).__name__
    write_json(run / 'transport.json', transport)


def run_worker(key_path, run):
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                                '--key-file', str(key_path), '--run', str(run)],
                               timeout=90, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if completed.returncode != 0 or not (run / 'transport.json').exists():
        return {'status': 'transport_error', 'http_status': None, 'error_type': 'ChildFailed'}
    return json.loads((run / 'transport.json').read_text(encoding='utf-8'))


def verify_preparation():
    manifest = json.loads((BUNDLE / 'preparation-manifest.json').read_text(encoding='utf-8'))
    entries = manifest['input_sha256']
    for relative, digest in entries.items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise RuntimeError('frozen preparation input changed: ' + relative)
    return len(entries)


def execute(key_path, *, run=None, worker=run_worker):
    run = Path(run) if run is not None else HERE / 'run'
    checked = verify_preparation()
    trial.init_run(BUNDLE, run, CONFIG)  # Refuses existing directory before dispatch.
    request = trial.prepare_request(run)
    if request['sample_id'] != 'P1-R1' or request['attempt_index'] != 0:
        raise RuntimeError('unexpected first request')
    prompt = (run / request['prompt_path']).read_bytes().decode('utf-8')
    write_json(run / 'http-request.json', payload_for(prompt))
    for name in ('smoke.py', 'README.md'):
        (run / ('snapshot-' + name)).write_bytes((HERE / name).read_bytes())
    write_json(run / 'authorization.json', {
        'scope': 'user-authorized one-initial-response smoke experiment',
        'date': '2026-09-17', 'endpoint': ENDPOINT, 'model': MODEL,
        'max_network_posts': 1, 'max_repairs': 0, 'max_retries': 0,
        'output_cap': MAX_OUTPUT, 'client_wall_deadline_seconds': 90,
        'historical_preparation_inputs_verified': checked,
        'six_candidate_protocol_complete': False})
    started = utc_now()
    try:
        transport = worker(key_path, run)
    except subprocess.TimeoutExpired:
        transport = {'status': 'timeout', 'http_status': None, 'error_type': 'ClientWallDeadline'}
    except Exception as error:
        transport = {'status': 'transport_error', 'http_status': None, 'error_type': type(error).__name__}
    finished = utc_now()
    envelope, content, token_usage = {}, '', None
    status = 'timeout' if transport['status'] == 'timeout' else 'transport_error'
    if (run / 'http-body.bin').exists():
        try:
            envelope = json.loads((run / 'http-body.bin').read_bytes())
            token_usage = usage_summary(envelope.get('usage'))
            choices = envelope.get('choices', [])
            if len(choices) == 1:
                message = choices[0]['message']
                content = message.get('content') or ''
                if type(content) is not str:
                    raise ValueError('nontext content')
                if transport['status'] == 'received' and envelope.get('model') == MODEL:
                    reason = choices[0].get('finish_reason')
                    status = {'stop': 'ok', 'length': 'truncated', 'content_filter': 'refusal'}.get(reason, 'transport_error')
                    if message.get('tool_calls') or message.get('refusal'):
                        status = 'refusal'
        except (ValueError, KeyError, TypeError, AttributeError):
            status = 'transport_error'
            content = ''
    metadata = {'sample_id': 'P1-R1', 'attempt_index': 0, 'status': status,
                'provider': CONFIG['provider'], 'model_id': MODEL, 'decoding': CONFIG['decoding'],
                'requested_max_output_tokens': MAX_OUTPUT, 'request_sha256': request['prompt_sha256'],
                'request_id': str(envelope.get('id') or 'not-returned-single-attempt'),
                'started_at_utc': started, 'finished_at_utc': finished,
                'input_tokens': token_usage['input_tokens'] if token_usage else None,
                'output_tokens': token_usage['output_tokens'] if token_usage else None}
    record = trial.record_response(run, content.encode('utf-8'), metadata)
    result = {'scope': 'one-call smoke; six-candidate protocol incomplete',
              'started_at_utc': started, 'finished_at_utc': finished,
              'transport': transport, 'response_status': status,
              'provider_reported_model': envelope.get('model'),
              'provider_system_fingerprint': envelope.get('system_fingerprint'),
              'usage_summary': token_usage,
              'accepted': record['accepted'], 'assessment': record['assessment'],
              'trial_summary': trial.summarize(run), 'stopped': 'one-call scope completed; no further dispatch'}
    write_json(run / 'smoke-result.json', result)
    hashes = {str(p.relative_to(run)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(run.rglob('*')) if p.is_file()}
    write_json(run / 'evidence-sha256.json', hashes)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-file', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--run', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.run is None or args.run.resolve() != (HERE / 'run').resolve():
            raise SystemExit('worker run path rejected')
        network_child(args.key_file, args.run)
    else:
        try:
            result = execute(args.key_file)
            print(json.dumps(result, ensure_ascii=True, indent=2))
        except Exception as error:
            print(json.dumps({'stopped': True, 'error_type': type(error).__name__}))
            raise SystemExit(1)
