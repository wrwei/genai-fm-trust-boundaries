"""Verify HOL/Python timing tables and retained stable executions; no reruns."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
RUNTIME = BASE.parent/'amr-runtime-binding'
EXTRACTION = BASE.parent/'amr-extraction-faithfulness'
PROGRESS = BASE.parent/'amr-progress-obligations'
from source_milestones import evaluate, SOURCE_ID
from timing_model import (next_control, observation_visible, release_from_clear,
                          start_from_grant, finish_from_arrival, two_task_bound)
from trace_binding import audit_rows


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')


def manifest_ok(package):
    manifest = json.loads((package/'evidence-manifest.json').read_bytes())
    for file, metadata in manifest['files'].items():
        assert sha(package/file) == metadata['sha256'], ('predecessor drift', package.name, file)
    return len(manifest['files'])


def csv(path):
    return [[int(cell) for cell in line.split(',')] for line in path.read_text().splitlines() if line]


def report_links_ok():
    report = REPO/'literature/scholar_search_2026-09-10/followup/research_amr_closed_loop_timing_results_2026-09-22.md'
    checked = 0
    for document in (BASE/'README.md', BASE/'review.md', report):
        assert document.is_file(), ('missing report document', document)
        for raw in re.findall(r'\[[^\]]+\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            if raw.startswith(('#','http://','https://')):
                continue
            target = (document.parent/raw.split('#',1)[0]).resolve()
            assert target.exists(), ('broken local report link', document, raw)
            checked += 1
    entries = {
        REPO/'RESEARCH_STATUS.md': 'research_amr_closed_loop_timing_results_2026-09-22.md',
        REPO/'docs/handoffs/2026-09-22-case-design-and-experiments.md':
            'research_amr_closed_loop_timing_results_2026-09-22.md',
        REPO/'literature/scholar_search_2026-09-10/followup/review_integration_2026-09-15.md':
            'research_amr_closed_loop_timing_results_2026-09-22.md',
    }
    for document, marker in entries.items():
        assert marker in document.read_text(encoding='utf-8'), ('missing report entry point', document)
        checked += 1
    return checked


def write_manifest(created_utc):
    files = {}
    for path in sorted(BASE.rglob('*')):
        if not path.is_file() or path.name == 'evidence-manifest.json' or '__pycache__' in path.parts:
            continue
        files[path.relative_to(BASE).as_posix()] = dict(bytes=path.stat().st_size, sha256=sha(path))
    write(BASE/'evidence-manifest.json', dict(
        created_utc=created_utc,
        scope='post-verification package snapshot; manifest excludes itself',
        files=files))


def verify():
    evidence = BASE/'evidence'
    predecessors = {p.name:manifest_ok(p) for p in (RUNTIME,EXTRACTION,PROGRESS)}
    source = evaluate()
    write(evidence/'source-milestones.json', dict(source_id=SOURCE_ID, passed=True, rows=source))

    timing_rows = [[t,next_control(t),observation_visible(t),release_from_clear(t),finish_from_arrival(t)]
                   for t in range(5)]
    source_rows = [[r['expected_action'],r['expected_next']] for r in source]
    exported_timing = csv(BASE/'hol/export/AMR_Closed_Loop_Timing.AMR_Closed_Loop_Timing/timing.csv')
    exported_source = csv(BASE/'hol/export/AMR_Closed_Loop_Timing.AMR_Closed_Loop_Timing/source.csv')
    actions = ['SelectA','SelectB','Defer','Request','Proceed','Brake','Resume','Release','Finish']
    modes = ['Idle','Waiting','Traversing','BrakeRequested','Stopped','ResumePending','Done']
    encoded_source = [[actions.index(a),modes.index(m)] for a,m in source_rows]
    assert timing_rows == exported_timing
    assert encoded_source == exported_source

    checked_ticks = checked_starts = 0
    maxima = dict(observation=0, release=0, finish=0, start_waiting=0, start_braking=0)
    for time in range(1001):
        assert time <= next_control(time) <= time+4 and next_control(time)%5 == 0
        for name, value, bound in (
                ('observation',observation_visible(time),9),
                ('release',release_from_clear(time),9),
                ('finish',finish_from_arrival(time),169)):
            latency = value-time
            assert latency <= bound
            maxima[name] = max(maxima[name], latency)
        checked_ticks += 1
    for grant in range(0,1001,5):
        for since in range(grant+1):
            for mode,key in (('Waiting','start_waiting'),('BrakeRequested','start_braking')):
                latency = start_from_grant(grant,since,mode)-grant
                assert latency <= 163
                maxima[key] = max(maxima[key],latency)
                checked_starts += 1
    assert two_task_bound() == 6884 and maxima == dict(
        observation=9, release=9, finish=169, start_waiting=15, start_braking=160)
    write(evidence/'timing-domain.json', dict(passed=True, checked_ticks=checked_ticks,
          checked_start_cases=checked_starts, maxima_ticks=maxima, two_task_bound_ticks=6884,
          two_task_bound_seconds=68.84, hol_timing_rows=exported_timing,
          hol_source_rows=exported_source))

    retained = RUNTIME/'evidence/run-2026-09-22'
    params = json.loads((retained/'effective-parameters.json').read_bytes())
    summary = json.loads((retained/'summary.json').read_bytes())
    traces = []
    for result in summary['results']:
        path = retained/result['trace']
        assert sha(path) == result['trace_sha256']
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            rows = [json.loads(line) for line in stream]
        traces.append(dict(name=result['name'], trace_sha256=sha(path), **audit_rows(rows,params)))
    write(evidence/'retained-traces.json', dict(passed=True, runs=traces,
          scope='four retained stable runs; no physical rerun or universal Python refinement'))

    proof_hashes = json.loads((BASE/'hol/source-hashes.json').read_bytes())
    for file,digest in proof_hashes.items():
        assert sha(REPO/file) == digest
    audit = (BASE/'hol/export/AMR_Closed_Loop_Timing.AMR_Closed_Loop_Timing/timing-proof-audit.txt').read_text()
    assert audit.startswith('No skipped proofs or oracle dependencies\n')
    assert 'stable_two_task_completion_bound' in audit
    tests = subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-v'],
                           cwd=BASE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (evidence/'tests.log').write_text(tests.stdout,encoding='utf-8')
    assert tests.returncode == 0, tests.stdout
    checked_utc = datetime.now(timezone.utc).isoformat()
    report = dict(passed=True, checked_utc=checked_utc,
        source_id=SOURCE_ID, source_milestones=len(source), hol_timing_rows=len(exported_timing),
        checked_ticks=checked_ticks, checked_start_cases=checked_starts,
        retained_runs=len(traces), tests=15, proof_facts=len(audit.splitlines())-1,
        proof_input_hashes=len(proof_hashes), predecessor_manifests=predecessors,
        two_task_bound_ticks=two_task_bound(), two_task_bound_seconds=two_task_bound()/100,
        observed_maxima_ticks={key:max(run['maxima_ticks'][key] for run in traces)
            for key in ('start','release','travel','finish')}, api_calls=0,
        report_links=report_links_ok(),
        statement='stable conditional timing composition; whole-Python, arbitrary-environment and hardware refinement remain open')
    write(evidence/'verification.json', report)
    write_manifest(checked_utc)
    print(json.dumps(report))
    return report


if __name__ == '__main__':
    verify()
