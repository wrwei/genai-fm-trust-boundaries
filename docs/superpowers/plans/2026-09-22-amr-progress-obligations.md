# AMR Progress Obligations Implementation Plan

> Execute this authorized continuation on main. Apply executing-plans sequentially and requesting-code-review for the final independent review. Preserve existing dirty and untracked work; no commit or push.

**Goal:** Determine exactly what the existing contracts do and do not justify about transport completion.

**Architecture:** Add a standalone proof and evidence package under `formal-artefacts/amr-progress-obligations/`. Read the retained controller, driver, parameter and evidence packages without modifying them.

**Tech Stack:** Isabelle2025-2 and bundled Python; no network/dependencies.

**Spec:** `docs/superpowers/specs/2026-09-22-amr-progress-obligations-design.md`.

- [x] Write profile and witness tests; verify the expected initial failure. Implement independent profile calculation and exact-dynamics comparisons.
- [x] Prove phase time bound, finite schedule drainage and upper-bound countermodel in `hol/AMR_Progress.thy`; build and audit dependencies.
- [x] Run the one predeclared stalled-plant witness; audit four retained traces against local timing obligations and record the nominal conditional budget.
- [x] Request independent review; fix findings; verify provenance and tests; write results and update research links and integration candidate.

Outputs: `profiles.py`, `experiments.py`, `trace_obligations.py`, focused tests, `hol/`, immutable physical run, evidence manifests, README and Chinese results report. The budget is a diagnostic with explicitly unproved cross-layer obligations, not an asserted full-loop theorem.

Completed 22 September 2026. Isabelle builds with 14 audited facts; 38 profile comparisons, four retained trace audits, the one fixed stationary witness and 12 tests pass their stated expectations. Independent review corrected attribution of the original exit-capability/no-fault premise and exposed a sensor-delivery completeness gap; both are addressed. The witness is deliberately outside that original progress premise and exact reference dynamics. The 70.2 s budget remains conditional accounting, not a proved full-loop deadline. Matching copies of all 24 pre-run inputs preserve the original experiment version through later documentation and audit improvements. Previous runtime/extraction manifests verify unchanged. Results are linked in RESEARCH_STATUS, handoff and I31 of the unique integration candidate; no active TeX edit, API call, commit or push.
