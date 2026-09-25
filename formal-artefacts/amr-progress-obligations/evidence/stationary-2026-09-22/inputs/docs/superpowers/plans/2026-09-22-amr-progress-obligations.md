# AMR Progress Obligations Implementation Plan

> Execute this authorized continuation on main. Apply executing-plans sequentially and requesting-code-review for the final independent review. Preserve existing dirty and untracked work; no commit or push.

**Goal:** Determine exactly what the existing contracts do and do not justify about transport completion.

**Architecture:** Add a standalone proof and evidence package under `formal-artefacts/amr-progress-obligations/`. Read the retained controller, driver, parameter and evidence packages without modifying them.

**Tech Stack:** Isabelle2025-2 and bundled Python; no network/dependencies.

**Spec:** `docs/superpowers/specs/2026-09-22-amr-progress-obligations-design.md`.

- [ ] Write profile and witness tests; verify the expected initial failure. Implement independent profile calculation and exact-dynamics comparisons.
- [ ] Prove phase time bound, finite schedule drainage and upper-bound countermodel in `hol/AMR_Progress.thy`; build and audit dependencies.
- [ ] Run the one predeclared stalled-plant witness; audit four retained traces against local timing obligations and record the nominal conditional budget.
- [ ] Request independent review; fix findings; verify provenance and tests; write results and update research links and integration candidate.

Outputs: `profiles.py`, `experiments.py`, `trace_obligations.py`, focused tests, `hol/`, immutable physical run, evidence manifests, README and Chinese results report. The budget is a diagnostic with explicitly unproved cross-layer obligations, not an asserted full-loop theorem.
