# Execution ledger — Forge-informed AMR diagnostic, 17 September 2026

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

Plan: `literature/scholar_search_2026-09-10/followup/research_amr_forge_revision_2026-09-17.md`.
User authorized execution after reviewing the design.

- Task 1: complete — isolated profiles and feedback, 17 tests pass, frozen-source copy hashes checked; full-pool historical refresh included.
- Task 2: complete — combined 42 diagnostic/runner/guard tests passed in 70.439 s; no blocking preflight review findings.
- Task 3: complete — seven live requests, all four conditions cycle-stopped, none accepted, no retries.
- Task 4: complete — parent replay and independent result audit passed (97 evidence files, 63 generation dependencies, all seven full assessments and token counts reproduced). Result report written. Physics correctly not entered because no source accepted; separate adapter 8 tests pass. See result-audit.md and verification.json.

Ruling: work in the existing main checkout — the user's explicit branch policy takes precedence over worktree defaults. New experiment lives in its own directory; raw provider replies, generated-controller bytes and scientific results from prior runs are retained.
Ruling: reuse the already checked single-POST transport function through a new guarded worker entry point — do not rerun either old live runner.

Resolved before live calls: normalize frozen witness tuples to JSON values before ledger comparison; preserve old repair JSON framing so D8-O's first repair prompt is byte-identical to prior request 005; finalize malformed provider envelopes with explicit fatal statuses; refresh all previously sent historical inputs, including omitted examples; save full failure-set deltas and repair-two checkpoint.
Independent reviewer added 13 worker guard tests. Live execution completed with fixed directory run/, seven dispatch markers and complete outcome records; do not rerun this completed experiment. Credential use remained inside the guarded network worker.
Physical adapter completed by forge_physics with 8 passing tests; it was not executed on a generated source because no diagnostic candidate was accepted.
Ruling: freeze the explicit generation/checking dependency set, not unrelated test and simulator Python files. The physics stage freezes its own adapter/plant inputs separately; it cannot influence diagnostic prompts. This permits independent offline preparation without invalidating generation evidence.
