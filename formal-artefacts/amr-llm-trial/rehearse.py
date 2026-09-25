"""Exercise six offline fixture chains, never call a model or claim model evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from trial import init_run, prepare_request, record_response, summarize

HERE = Path(__file__).resolve().parent
CANDIDATES = HERE.parent / 'amr-supervisor' / 'candidates'


def write_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def run_rehearsal(output: Path) -> dict:
    """Create a new labelled fixture run using unchanged prior mechanism fixtures."""
    output = Path(output).resolve()
    config = json.loads((HERE / 'fixture-config.json').read_bytes().decode('utf-8'))
    if config['record_mode'] != 'fixture':
        raise ValueError('Rehearsal accepts only fixture mode')
    output.parent.mkdir(parents=True, exist_ok=True)
    init_run(HERE, output, config)
    sources = {name: (CANDIDATES / (name + '.json')).read_bytes()
               for name in ('authored_reference', 'goal_stop_gap', 'always_brake')}
    origins = []
    while (request := prepare_request(output)) is not None:
        sample, attempt = request['sample_id'], request['attempt_index']
        raw, status, origin = sources['authored_reference'], 'ok', 'authored_reference'
        if sample == 'P2-R1' and attempt == 0:
            raw, origin = sources['goal_stop_gap'], 'goal_stop_gap'
        elif sample == 'P3-R1' and attempt == 0:
            raw = b'```json\r\n' + sources['authored_reference'] + b'\r\n```'
            origin = 'authored_reference wrapped in Markdown fences by rehearsal'
        elif sample == 'P1-R2':
            raw, status, origin = b'', 'timeout', 'simulated timeout; no call made'
        elif sample == 'P2-R2' and attempt == 0:
            raw, origin = b'\xff\xfe\x80invalid UTF-8 fixture', 'invalid UTF-8 bytes authored for rehearsal'
        elif sample == 'P3-R2':
            raw, origin = sources['always_brake'], 'always_brake'
        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = dict(sample_id=sample, attempt_index=attempt, status=status,
                        provider=config['provider'], model_id=config['model_id'],
                        decoding=config['decoding'], requested_max_output_tokens=config['max_output_tokens'],
                        request_sha256=request['prompt_sha256'],
                        request_id=f'FIXTURE-{sample}-{attempt}',
                        started_at_utc=timestamp, finished_at_utc=timestamp,
                        input_tokens=None, output_tokens=None)
        record = record_response(output, raw, metadata)
        origins.append(dict(sample_id=sample, attempt_index=attempt, status=status,
                            origin=origin, raw_sha256=hashlib.sha256(raw).hexdigest(),
                            accepted=record['accepted']))
    result = summarize(output)
    write_json(output / 'summary.json', result)
    write_json(output / 'rehearsal-origins.json', dict(
        provenance='Offline fixture workflow rehearsal. No model call, sampling, repair generation or new physical simulation.',
        input_fixture_sha256={name: hashlib.sha256(raw).hexdigest() for name, raw in sources.items()},
        entries=origins))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_rehearsal(args.output), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
