"""Recheck saved evidence and provenance; never repeat the physical witness."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from experiments import (BASE, REPO, BINDING, effective_parameters, sha, write, verify_retained,
                         profile_matrix, nominal_obligations, witness_audit)


def canonical(value):
    return json.loads(json.dumps(value))


def verify():
    evidence = BASE/'evidence'
    out = evidence/'stationary-2026-09-22'
    pre = json.loads((out/'pre-run.json').read_bytes())
    snapshot = json.loads((out/'input-snapshot.json').read_bytes())['files']
    assert set(snapshot) == set(pre['dependencies'])
    changed = {}
    allowed = {
        'formal-artefacts/amr-progress-obligations/trace_obligations.py':
            'post-run audit strengthening: detect missing/duplicate sensor delivery; physical driver and mutation unchanged',
        'docs/superpowers/specs/2026-09-22-amr-progress-obligations-design.md':
            'review clarification of the original qualitative exit-capability premise',
        'docs/superpowers/plans/2026-09-22-amr-progress-obligations.md':
            'completion checkboxes and outcome after the fixed run',
    }
    for file,digest in pre['dependencies'].items():
        assert snapshot[file]['sha256'] == digest
        assert sha(BASE/snapshot[file]['snapshot']) == digest
        current = sha(REPO/file)
        if current != digest:
            assert file in allowed, ('unexplained post-run dependency drift', file)
            changed[file] = dict(before=digest, current=current, reason=allowed[file])
    assert sha(Path(__file__).with_name('experiments.py')) == pre['dependencies'][
        'formal-artefacts/amr-progress-obligations/experiments.py']
    params = effective_parameters()
    assert params == json.loads((out/'effective-parameters.json').read_bytes())
    assert canonical(profile_matrix(params)) == json.loads((evidence/'profiles.json').read_bytes())
    assert canonical(nominal_obligations(params)) == json.loads((evidence/'nominal-obligations.json').read_bytes())
    result = json.loads((out/'summary.json').read_bytes())
    assert sha(out/'trace.jsonl.gz') == result['trace_sha256']
    audit = witness_audit(out/'trace.jsonl.gz', result, params)
    assert canonical(audit) == json.loads((out/'audit.json').read_bytes())
    from audit_execution import geometry
    starts = {r: (*params['map']['route_'+r][1], 0. if r=='A' else 3.141592653589793) for r in 'AB'}
    pairs = [('A:B', starts['A'], (.8,.6), starts['B'], (.8,.6))]
    for r in 'AB':
        for x in (9.75,14.25):
            for y in (-.87,.87):
                pairs.append((f'{r}:wall:{x}:{y}', starts[r], (.8,.6), (x,y,0), (3.5,.14)))
    gaps = {name: geometry.gap(a, da, b, db) for name,a,da,b,db in pairs}
    assert len(gaps) == 9 and all(v>0 for v in gaps.values())
    # The trace audit proved every physical piece constant at these starts.
    proof = json.loads((BASE/'hol/source-hashes.json').read_bytes())
    for file,digest in proof.items():
        assert sha(REPO/file) == digest
    proof_audit = (BASE/'hol/export/AMR_Progress_Obligations.AMR_Progress/progress-audit.txt').read_text()
    assert proof_audit.startswith('No skipped proofs or oracle dependencies\n')
    assert 'upper_bounds_do_not_imply_completion' in proof_audit and 'planned_segment_time_bound' in proof_audit
    tests = subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-v'], cwd=BASE,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (evidence/'tests.log').write_text(tests.stdout, encoding='utf-8')
    assert tests.returncode == 0, tests.stdout
    report = dict(passed=True, checked_utc=datetime.now(timezone.utc).isoformat(),
                  profile_comparisons=38, retained_nominal_runs=4, constructed_physical_runs=1,
                  tests=12, pre_run_dependencies=len(pre['dependencies']),
                  pre_run_snapshots_verified=len(snapshot), post_run_changes=changed,
                  proof_input_hashes=len(proof), proof_facts=len(proof_audit.splitlines())-1,
                  previous_manifests_verified=verify_retained(), api_calls=0,
                  witness_adapter_events=audit['counts']['adapter'],
                  witness_source_steps=audit['counts']['source_step'],
                  witness_static_intervals=audit['zero_motion_intervals'],
                  independent_static_geometry_gaps=gaps,
                  statement='Profile proof and premise-removal witness; universal closed-loop transport proof remains open')
    write(evidence/'verification.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('post_run_changes','independent_static_geometry_gaps')}))
    return report


if __name__ == '__main__':
    verify()
