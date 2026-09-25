# AMR v2 experiment execution plan

> For agentic workers: use subagent-driven-development for bounded delegated work and review; the approved case design is binding.

**Goal:** execute the redesigned AMR case, retaining successful and failed evidence, and produce a claim-scoped report that can be integrated into the article.

**Architecture:** a source-driven supervisor, a typed advisory mailbox and a current-state execution protocol are checked at separate boundaries. An independently specified reference protocol bounds the HOL model; geometry independently checks physical predicates. Real advice is a small recorded batch after deterministic checks pass.

**Tech stack:** Python standard library, existing AMR plant/oracle, Isabelle2025-2 and the existing checked finite-trace theory, authorized DeepSeek endpoint.

**Spec:** [approved redesign](research_amr_case_redesign_2026-09-21.md).

## Global constraints

- Work on `main`, as explicitly instructed by the user; preserve all historical evidence and existing uncommitted replication records.
- New implementation/evidence lives under `formal-artefacts/amr-advisory-v2/`. No edits to historical checkers, candidate bytes, physical manifests or proof logs.
- Distinguish source/model finite checks, HOL theorems, finite Python/HOL conformance and continuous simulation. Never replace a missing proof with a successful trajectory.
- Final A/B/Defer is output by the original candidate; trusted code supplies facts and checks results, but cannot conceal a functional candidate failure.
- Whole-body clearance, current permission at commit AND application, deterministic mailbox and nonblocking advice handling are separate obligations.
- Minimum liveness result is conditional authorization progress before Grant. Full physical completion proof is optional; observed completion is reported as such.
- All constructed faults are labelled. Do not count them as LLM errors. Revalidate every old raw identity, not only a passing one.
- Real advice: six requests, no retries or adaptive extra batch; preserve raw output, latency, usage and rejection. Never expose credentials.
- No commit, push, Overleaf synchronization or new infrastructure is required to run this experiment.

## Task 1: freeze finite source obligations and E1

Files: `contract.md`, `source_check.py`, `tests/test_source_check.py`, `evidence/source/`.

- [x] Read the existing finite syntax, interpreter, target interpreter and six replication responses; retain exact bytes and identities.
- [x] Freeze v2 selection semantics: honor an unambiguous available advisory choice; otherwise use frozen FIFO order, one eligible robot selects itself, occupied/no eligible means Defer. Preserve all v1.1 step obligations.
- [x] If old syntax cannot express FIFO B-first, explicitly report this incompatibility; a restricted initial-A-first profile is allowed only if named and scoped, never silently promoted to general FIFO.
- [x] Add failing tests for safe-but-wrong selection, model/source mismatch and candidate identity retention; implement and run complete finite-domain checks.
- [x] E1 compares one fixed raw source to correct and deliberately faulty extraction, reporting local old safety, v2 functional policy and correspondence independently. Use a slice witness if the whole faulty model does not pass v2; do not claim full-model acceptance from a slice.
- [x] Export candidate decision tables and a machine-readable source/target report; choose deployment candidate by a declared rule among all passing raw identities.

## Task 2: build and prove the discrete AMR protocol

Files: `hol/ROOT`, `hol/AMR_Protocol.thy`, `hol/build.py`, `hol/export/`, `hol/README.md`.

- [x] Freeze a finite executable core with two robots, requests, owner, relevant environment permission, pending selection, command issue/application and whole-clear release. Export the exact state/input/event definitions for Python conformance before implementation begins there.
- [x] Define an independent reference transition relation and trusted open protocol P_open. Candidate outputs can be arbitrary for the authority theorem; functionality/progress uses a separately checked total selector.
- [x] Account for every internal/advice event. Prove the actual HOL operational protocol embeds into an open-protocol/advice interleaving with a causal interface, then reuse `authority_boundary_traces`; do not define a guard by the desired safety predicate.
- [x] Prove conditional authorization progress without advice arrival, plus a permanent-no-advice blocking witness for an explicitly faulty protocol. New same-permission observations and messages cannot reset validated choices.
- [x] Preserve environment changes in the visible projection; prove current-commit and current-application checks, with precise local event-order assumptions.
- [x] Build under the pinned local Isabelle runtime, record source identities and logs, check proof dependencies for skipped proofs/oracles, and export executable transition observations for finite conformance.

## Task 3: implement the runtime interface and E3/E4

Files: `protocol.py`, `advice_mailbox.py`, `tests/test_protocol.py`, `tests/test_mailbox.py`, `run_mechanisms.py`, `evidence/mechanisms/`.

- [x] Write behavioral tests before implementation: stale validation cannot Grant; permission change after Issue cannot Apply; fresh same-permission updates cannot starve Grant; missing, duplicate and late advice cannot reset progress; raw source decision remains observable.
- [x] Implement Python core against the frozen HOL interface, with independent reference-event validation. Exhaust its declared state/input domain against exported HOL observations.
- [x] Implement one outstanding trusted request per task context, one accepted A/B slot, exact binding and strict parsing; zero waiting at the decision latch.
- [x] Execute E3a, E3b and E4 paired witnesses, plus effective A/B and absent-advice controls. Separate oracle verdicts from test pass/fail: an intentionally faulty run should produce a retained violation.

## Task 4: physical contrasts and boundary calibration

Files: `physical.py`, `tests/test_physical.py`, `run_physical.py`, `evidence/physical/`.

- [x] Reuse the unchanged plant/oracle and selected raw source. Add narrowly scoped integration hooks in the new directory, with provenance for any adapted old loop.
- [x] E2 compares conservative body-clear against center-only clearance from the same initial configuration; independently score premature Release, even without collision.
- [x] E3 uses state-triggered permission changes in safe waiting positions, independently for Validate→Commit and Issue→Apply. E4 keeps the road usable and removes advice; compare the waiting fault with normal source-driven FIFO.
- [x] Include valid A/B influence controls, temporary/permanent blockage and straight-approach braking calibration inside and just outside the stated sufficient bound. Observations follow each run's own plant, not a copied trajectory.
- [x] Record actions, effects, relevant states, geometry and completion; replay with an independent audit. Keep physical assumptions and limitations explicit.

## Task 5: real advice and integration

Files: `advice_trial.py`, `tests/test_advice_trial.py`, `evidence/advice/protocol.json`, `evidence/advice/`, `README.md`, final results report and `RESEARCH_STATUS.md`.

- [x] Freeze three task wordings with two repetitions each, strict A/B output, bounded requests and no retry. Verify the credential worker, endpoint allowlist, irreversible dispatch marker offline.
- [x] Make six authorized requests; record actual content, timing and usage. Bind every response through the same mailbox. Execution refinement: use real-time-paced fixed approach and source-driven authorization with the predeclared cutoff, then independently replay all response contents offline. Scripted A/B/no-advice physical controls remain separate; no full real-time mission claim.
- [x] Produce an obligation coverage matrix E1–E4/B1/B2, distinguish violated assumptions from defects, and report unexpected or negative findings.
- [x] Obtain independent code/spec/evidence review, resolve substantive issues, run relevant final checks once, freeze an evidence manifest and summarize manuscript-ready conclusions. Boundary reviews, final closure review and 30 final tests passed; final postflight manifest records the current evidence bundle.
- [x] Write a single case integration excerpt and update the existing integration entry; do not promote undeveloped proof/physical claims into active TeX.

## Progress ledger

2026-09-21: design accepted by the user for execution. Existing supervisor baseline test run started. Historical replication remains unmodified. Ruling: keep work in the user-designated main checkout; new case artifacts are isolated by directory, not by branch. Ruling: proof and Python runtime share a frozen interface; do not run competing implementations of that interface. Delegate the HOL implementation while the primary agent develops finite source checks, then review both before integration.


Execution update: source and runtime reviews passed; the final Isabelle build completed at 22:51:34 with persistent mailbox, source-latch and progress strengthening. Final conformance has 11,664 core rows and 1,296 selector rows with zero mismatches. All 15 physical expected outcomes, including constructed violations, were independently replayed. Six bounded real calls completed with no retries; all returned timely B advice and the original source selected B. The full 30-test suite passed in 61.113 s. Results and the I28 integration block are written. The physical pre-run transitive-code provenance gap and all proof and physical scope limits remain explicit. That execution did not change historical evidence, active TeX or the Overleaf branch. Later record maintenance is documented separately.

Closure: independent final review found no Critical or Important issues. The minor direct-control premise-witness documentation gap is resolved by explicitly reusing the checked/imported controlled_advice_counterexample, not claiming a new physical bypass run. All five tasks are complete within the declared bounded scope; see research_amr_v2_results_2026-09-21.md and amr-advisory-v2/closure-review.md.
