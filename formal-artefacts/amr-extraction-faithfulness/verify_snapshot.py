"""Reproducibility/identity closure; kernel proofs remain separate evidence."""
import hashlib
import json
from pathlib import Path
import snapshot

HERE, ROOT = snapshot.HERE, snapshot.ROOT


def verify():
    saved = json.loads((HERE/'evidence/snapshot.json').read_bytes())
    current = json.loads(json.dumps(snapshot.collect()))
    expected = dict(saved)
    generated_hash = expected.pop('generated_theory_sha256')
    assert expected == current, 'raw/profile/compiler/frontend snapshot changed'
    path = HERE/'hol/AMR_Artifacts.thy'
    assert snapshot.sha(path) == generated_hash
    assert path.read_text(encoding='utf-8') == snapshot.theory(current)
    proof_inputs = json.loads((HERE/'hol/source-hashes.json').read_bytes())
    assert all(snapshot.sha(ROOT/p) == digest for p, digest in proof_inputs.items())
    general_audit = HERE/'hol/export/AMR_Extraction_Faithfulness.AMR_Extraction/proof-audit.txt'
    concrete_audit = HERE/'hol/export/AMR_Extraction_Faithfulness.AMR_Artifacts/artifact-audit.txt'
    general = general_audit.read_text().splitlines()
    concrete = concrete_audit.read_text().splitlines()
    assert general[0] == 'No skipped proofs or oracle dependencies'
    assert concrete[0] == 'Concrete bindings: no skipped proofs or oracle dependencies'
    assert len([x for x in concrete if x.endswith('_binding')]) == 10
    assert len([x for x in concrete if x.endswith('_preserves')]) == 10
    assert len([x for x in concrete if x.endswith('_source_values')]) == 19
    assert len([x for x in concrete if x.endswith('_target_values')]) == 19
    prior = HERE.parent/'amr-runtime-binding/evidence-manifest.json'
    prior_manifest = json.loads(prior.read_bytes())
    for name, meta in prior_manifest['files'].items():
        assert snapshot.sha(prior.parent/name) == meta['sha256'], ('prior evidence changed', name)
    report = dict(passed=True, raw_samples=6, distinct_sources=5, concrete_extraction_equalities=10,
                  concrete_universal_preservation_corollaries=10, expression_structures=19,
                  paired_interpreter_valuations=19*8, source_identity=saved['selected_source_sha256'],
                  snapshot_inputs_verified=len(current['input_sha256']), proof_inputs_verified=len(proof_inputs),
                  previous_runtime_package_entries_unchanged=len(prior_manifest['files']),
                  general_audit_sha256=snapshot.sha(general_audit), concrete_audit_sha256=snapshot.sha(concrete_audit),
                  snapshot_sha256=snapshot.sha(HERE/'evidence/snapshot.json'),
                  verifier_sha256=snapshot.sha(Path(__file__)), api_requests=0,
                  scope='deterministic snapshot regeneration and identities; no general Python/parser proof')
    (HERE/'evidence/verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    verify()
