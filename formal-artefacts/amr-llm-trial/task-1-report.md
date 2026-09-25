# Task 1 report — DONE_WITH_CONCERNS

Implemented the offline AMR trial recorder without model calls, network access, original AMR edits, commits, or cleanup.

## Owned files

- `trial.py`
- `tests/test_trial.py`
- `task-1-red.log`
- `task-1-green.log`
- `task-1-report.md`

## Evidence

Python runtime:

`C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`

TDD red command:

`python.exe -m unittest discover -s tests -v`

The initial run failed at import with `ModuleNotFoundError: No module named 'trial'`, demonstrating that the implementation was absent. A later focused config-validation run failed because a nested `decoding.api_key` was accepted; the recursive credential-field rejection was then implemented.

Green command:

`python.exe -m unittest discover -s tests -v`

Result: all 12 discovered tests passed in 8.222 seconds, zero failures and zero errors. This comprises 11 recorder tests plus the coordinator-owned rehearsal integration test. The saved full output is `task-1-green.log`.

Additional checks:

- `python.exe -m py_compile trial.py tests/test_trial.py` — exit 0.
- `python.exe trial.py --help` — exit 0 and lists `init`, `prepare`, `record`, and `summary`.
- `git diff --check -- formal-artefacts/amr-llm-trial` from the repository root — exit 0. The directory is currently untracked; no commit was made.

The tests use the unchanged real assessor and historical `authored_reference.json` / `always_brake.json` sources. Runs hash the loaded real assessor, corridor dependencies, and recorder; mutation checks alter only temporary originals, run snapshots, or run evidence. Covered behavior includes exact CRLF/raw preservation, fenced JSON rejection without normalization, rejected-initial-to-accepted-repair accounting, repair caps and sample progression, pending idempotence and distinct counting, metadata mismatch and duplicate rejection, original/snapshot prompt and dependency integrity, manifest binding and inventory completeness, raw/record tamper detection, terminal transport statuses, strict config validation, invalid UTF-8 retention, output-token cap evidence retention and partial stopping, missing usage accounting, partial/final denominators and selection, timestamp ordering, and prior-chain integrity.

## Concerns and limitations

- Live provider/model identity is supplied by the operator and is not independently authenticated, as required by the protocol. `model_revision="provider-not-exposed"` remains the explicit permitted limitation.
- A retained output-token violation closes the remaining chains as stopped, because no further request may legally be prepared.
- The manifest digest detects accidental edits. It is not a signature and cannot resist a malicious actor who changes evidence and deliberately recomputes every affected hash.
- All generated responses and selected-candidate assertions in this task were fixture-only; no live model response was recorded.

## Fix round 1 — DONE

The independent recorder review identified related defects: simultaneous terminal causes were collapsed, and Python equality admitted bool/float aliases in identity-bearing metadata. The fixes were implemented test-first in `trial.py` and `tests/test_trial.py`.

New behavior:

- Any already-pending request remains readable and recordable so its raw evidence is not lost.
- Stopped partial coverage reports attempted and never-attempted sample IDs from records, has no actionable pending repair, remains incomplete, and cannot select a candidate.
- Each record stores deterministic `violation_flags` for output-token and non-ok-status causes independently. Summaries count each applicable cause.
- Attempt indices and requested token caps require actual bounded integers. Identity strings require actual nonempty strings. Decoding declarations are compared as type-preserving canonical JSON, so bool, int, and float aliases cannot match accidentally.

TDD evidence is preserved separately:

- `task-1-fix-round1-red.log`: the four targeted review regressions failed against the pre-fix implementation.
- `task-1-fix-round1-attempted-red.log`: the coordinator's attempted-coverage assertion reproduced the stopped-chain undercount (`0 != 1`).
- `task-1-fix-round1-green.log`: final discovery passed all 16 tests in 10.339 seconds, comprising 15 recorder tests and the coordinator-owned rehearsal integration test, with zero failures and zero errors.

No model calls, network access, original AMR edits, prompt/protocol/rehearsal edits, cleanup, commits, or live-response recording occurred in this fix round.
