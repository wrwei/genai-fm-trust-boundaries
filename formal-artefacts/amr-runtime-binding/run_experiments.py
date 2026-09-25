"""Four frozen offline physical runs and bounded interface faults; no network code."""
from dataclasses import replace
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from binding import HERE, V2, Runtime, SourceController
from binding_conformance import HOLTable
from physical_binding import run_episode
from physical import effective_parameters


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')


def mechanisms():
    table = HOLTable()
    source = SourceController.from_selected()
    results = []
    definitions = [
        ('empty', None, [], False),
        ('valid-B', None, [('req', 'ctx', '{"prefer":"B"}')], False),
        ('wrong-binding', None, [('old', 'ctx', '{"prefer":"B"}')], False),
        ('malformed', None, [('req', 'ctx', '{"prefer":"B","grant":true}')], False),
        ('duplicate', None, [('req', 'ctx', '{"prefer":"B"}'), ('req', 'ctx', '{"prefer":"A"}')], False),
        ('late-B', None, [('req', 'ctx', '{"prefer":"B"}')], True),
        ('bad-burst', None, [('old', 'ctx', '{"prefer":"B"}')] * 64, False),
        ('skip-binding', 'skip_binding', [('old', 'ctx', '{"prefer":"B"}')], False),
        ('reset-pending', 'reset_pending', [('req', 'ctx', '{"prefer":"B"}')], True),
        ('wait-empty', 'wait', [], False),
    ]
    expected = {'empty': 'A', 'valid-B': 'B', 'wrong-binding': 'A', 'malformed': 'A',
                'duplicate': 'B', 'late-B': 'A', 'bad-burst': 'A', 'skip-binding': 'B',
                'reset-pending': 'B', 'wait-empty': None}
    for name, fault, messages, late in definitions:
        rt = Runtime('req', 'ctx', source=source)
        rows = [rt.local(('RequestAdvice',)), rt.local(('Register', 'A')), rt.local(('Register', 'B'))]
        if late:
            rows.append(rt.local(('Validate',)))
        for req, ctx, payload in messages:
            row = rt.receive('req' if fault == 'skip_binding' else req, ctx, payload)
            row['raw_input'] = ['Message', req, ctx, payload]
            if fault == 'reset_pending':
                # Deliberate experimental implementation fault, never a runtime option.
                rt.core = replace(rt.core, pending=None)
                row['after'] = rt.snapshot()
            rows.append(row)
        supplied, blocked = 0, 0
        for _ in range(2):
            if fault == 'wait' and rt.box.advice is None:
                blocked += 1
            else:
                rows.append(rt.local(('Service',)))
                supplied += 1
        granted = [e[1] for row in rows for e in row['events'] if e[0] == 'Grant']
        mismatches = [i for i, row in enumerate(rows) if not table.check(row)]
        result = dict(name=name, constructed_fault=fault, granted=granted,
                      supplied_services=supplied, blocked_service_opportunities=blocked,
                      conformance_mismatches=mismatches, rows=rows)
        result['expected_outcome_observed'] = granted == ([] if expected[name] is None else [expected[name]])
        result['expected_outcome_observed'] &= bool(mismatches) == (fault in ('skip_binding', 'reset_pending'))
        results.append(result)
    # Current-permission gap, reached through the full source and mailbox adapter.
    rt = Runtime('req', 'ctx', source=source)
    rows = [rt.local(i) for i in [('Register', 'A'), ('Validate',), ('Observe', True, True), ('Commit',)]]
    results.append(dict(name='revoked-before-commit', rows=rows,
        expected_outcome_observed=rt.core.owner is None and all(table.check(r) for r in rows)))
    return results


def main():
    out = HERE/'evidence/run-2026-09-22'
    out.mkdir(exist_ok=False)
    reply = V2/'evidence/advice/001/response.bin'
    raw = reply.read_text(encoding='utf-8')
    cases = [
        ('none', [], 'A'),
        ('retained-B', [(0., 'req', 'ctx', raw)], 'B'),
        ('invalid-then-B', [(0., 'old', 'ctx', raw), (0., 'req', 'ctx', '{"prefer":"B","grant":true}'),
                            (.01, 'req', 'ctx', raw)], 'B'),
        ('late-B', [(.06, 'req', 'ctx', raw)], 'A'),
    ]
    repo = HERE.parents[1]
    selected = json.loads((V2/'evidence/source/summary.json').read_bytes())['selected']
    dependencies = (list(HERE.glob('*.py')) + list((HERE/'hol').glob('*.thy')) + [HERE/'hol/ROOT']
                    + list(V2.glob('*.py')) + list((V2.parent/'amr-corridor').glob('*.py'))
                    + list((V2.parent/'amr-forge-diagnostic/profiles').rglob('*.py'))
                    + [V2.parent/'amr-forge-diagnostic/diagnostics.py', V2/'evidence/source/summary.json',
                       repo/selected['path'], reply,
                       repo/'literature/scholar_search_2026-09-10/followup/research_amr_parameters_2026-09-15.json',
                       HERE/'hol/export/AMR_Runtime_Binding.AMR_Runtime_Binding/binding.csv'])
    plan = dict(started_utc=datetime.now(timezone.utc).isoformat(), maximum_runs=4,
        horizon_seconds=120, maximum_api_requests=0, cases=cases,
        scope='offline retained-content replay on serial simulation time; no new samples or wall-clock timing claim',
        identities={p.relative_to(repo).as_posix(): sha(p) for p in sorted(set(dependencies))})
    write(out/'pre-run.json', plan)
    write(out/'effective-parameters.json', effective_parameters())
    write(out/'mechanisms.json', mechanisms())
    results = []
    for name, events, first in cases:
        path = out/(name+'.jsonl.gz')
        with gzip.open(path, 'wt', encoding='utf-8') as stream:
            def emit(row):
                stream.write(json.dumps(row, separators=(',', ':'))+'\n')
            result = run_episode(advice_events=events, horizon=120., emit=emit)
        result.update(name=name, expected_first=first, trace=path.name, trace_sha256=sha(path))
        result['passed'] = (result['grant_order'] == [first, 'B' if first == 'A' else 'A']
            and result['termination'] == 'complete'
            and not any(result[k] for k in ('collision_pairs', 'unresolved_pairs', 'early_releases', 'reference_violations')))
        write(out/(name+'.summary.json'), result)
        results.append(result)
        print(json.dumps({k: result[k] for k in ('name', 'grant_order', 'time', 'passed')}), flush=True)
    unchanged = all(sha(repo/p) == h for p, h in plan['identities'].items())
    report = dict(results=results, dependencies_unchanged=unchanged,
                  passed=unchanged and all(r['passed'] for r in results))
    write(out/'summary.json', report)
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
