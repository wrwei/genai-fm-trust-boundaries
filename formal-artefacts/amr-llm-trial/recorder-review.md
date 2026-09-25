# Independent recorder review — CHANGES_REQUIRED

Reviewed 2026-09-15. Scope: `task-1-brief.md`, `task-1-report.md`, `recorder-review-package.diff`, final `trial.py`, recorder tests, `rehearse.py`, rehearsal integration test, README, protocol.json, and the linked research protocol. No production edits, model calls, network, original AMR edits, commits, or broad test rerun were performed.

Spec verdict: **CHANGES_REQUIRED**. Code quality verdict: **CHANGES_REQUIRED**, with otherwise straightforward, inspectable standard-library implementation and useful exact-byte evidence handling.

## Findings

### P1 — Retain simultaneous output-token and transport failures

Locations in the reviewed version: `trial.py:435`–`438`, `trial.py:510`–`515`.

A non-ok transport status accompanying an output-token cap breach was absent from the `infrastructure_failures` aggregate. Preserve the terminal reason and independent violation flags so both facts remain visible, and cover the combined case with a regression test.

### P2 — Enforce integer types for identity-bearing request numbers

Locations: `trial.py:372`, `trial.py:378`.

Metadata validation compares attempt_index and requested_max_output_tokens by Python equality without validating their types. Python accepts false == 0 and true == 1. A bounded probe confirmed that metadata attempt_index=false is persisted and accepted for initial attempt 0. Float equivalents also compare equal; nested decoding values can have the same bool/integer equality ambiguity. This weakens the strict metadata contract and produces differently typed identity data in supposedly matched records. Require exact integer types for attempt and requested cap, and compare decoding with a type-preserving canonical representation. Existing usage-count fields correctly reject bool-as-int.

## Positive checks and evidence limitations

- Prepared prompts and repair template are frozen as exact bytes, together with the executing recorder and its sibling supervisor/corridor Python inputs. In particular, dependency inventory is anchored to the executing recorder's `SUPERVISOR`, rather than an arbitrary copied bundle's unused assessor. Config is included in the hashed run manifest. Requests, raw bytes, and immutable records have separate hashes; ordinary original/snapshot/raw/record mutations fail closed.
- Source assessment receives the entire strictly decoded response. Markdown fences are not removed; invalid UTF-8 remains on disk. Repair framing contains only original requirements, the immediately preceding raw output/diagnostic, actual capped checker feedback, and the repair template. Acceptance stops a chain, and non-ok response statuses terminate it without repair.
- Normal initial/repair denominators and lexicographic final selection are coherent. Partial runs do not produce a selected candidate. Cap-stopped unattempted samples are explicitly represented in `per_sample`, though `unattempted_samples` becomes zero for these never-attempted samples; consumers must use per-sample attempts to distinguish stopped coverage.
- The current rehearsal explicitly requires fixture mode and uses historical/authored fixture bytes, simulated timeout, and null usage. Its provenance does not claim model-generated repairs or live inference. Configuration remains unbound for real sampling; README and protocol preserve the user's preparation-only authorization. No live calls are authorized by this review.
- Live identity remains operator-supplied, not independently authenticated. `provider-not-exposed` revision and null usage are explicitly represented. Hashes are integrity checks, not signatures. An imported-module cache or mutation between import and snapshot is not independently authenticated by source-file hashing; the reviewed standard CLI and fixture test path uses the intended sibling assessor.
- The saved task report states all 12 tests passed in 8.222 seconds, and compilation/help checks passed. This review did not rerun that suite. The historical review used three bounded probes with the test helper's temporary bundle setup and the unchanged real assessor, via Python `C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; they completed successfully in approximately 1.27 seconds. Their observed failures are gaps in that existing green coverage, not assertions that the green log itself is false.

## Disposition

Keep the package labelled preparation/fixture-only. This review does not approve live sampling or establish physical outcomes.

## Fix round 1 independent re-review — PASS for preparation scope

Re-reviewed 2026-09-15 against `recorder-fix-review.diff`, `task-1-fix-brief.md`, the appended implementation report, current recorder summary logic, added regressions, and the saved final green log. This appendix supersedes the initial CHANGES_REQUIRED disposition; the original findings above remain as development history.

Final spec verdict: **PASS for the offline preparation/fixture scope**. Final code-quality verdict: **PASS; no remaining actionable finding within this scoped re-review**.

- An existing pending request is returned first and its raw response remains recordable.
- Infrastructure failures and output-token violations are counted independently.
- Attempt and requested-cap fields require actual integers; identity fields require strings; canonical JSON preserves bool/int/float distinctions in decoding. The added invalid-metadata cases verify no ledger mutation.
- Stopped coverage is derived from recorded sample IDs. The historical regression included an attempted=1 assertion; completed terminal chains retain their recorded outcomes.
- Current dependency snapshots remain anchored to the executing recorder and its sibling assessor/corridor files, resolving the earlier copied-bundle provenance question.

Validation evidence: directly read `task-1-fix-round1-green.log`, which ends `Ran 16 tests in 10.339s` and `OK`; the implementation report identifies 15 recorder tests plus one rehearsal integration test. Reviewed the four new regression tests, including stopped coverage, combined causes, and strict metadata identity. No broad suite rerun or extra runtime probe was necessary for this re-review. No code or other documentation was changed by the reviewer.

Final bounded package review also covered latest README, `rehearse.py`, protocol.json, and `research_amr_llm_preparation_results_2026-09-15.md`. Their scope statements are consistent: preparation only; live identity/configuration remains unbound; no experimental model calls or live model samples; the 6-chain/11-record/5-repair rehearsal is predetermined fixture substitution with null usage, not evidence of model repair ability; no new physical simulation or theorem is claimed. Prior findings and corrections are disclosed rather than hidden. The research results explicitly defer final status to this appendix and the final verification artifact.

The coordinator's final manifest regeneration, replay/hash verification, and protected-original-file audit remain a separate pending release gate at the time of this appendix. This code/spec review does not independently certify that final artifact audit or authorize real model sampling. The preparation-only user constraint continues unchanged.
