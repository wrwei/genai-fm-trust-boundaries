# Independent physical review

Reviewed 21 September 2026. **Specification verdict: PASS for the fifteen declared bounded outcomes. Quality verdict: PASS with the evidence-scope and provenance qualifications below.** This is not fifteen safe-and-complete runs. Constructed violations and environment-limited noncompletion are required outcomes, not hidden failures.

The independent reviewer read `physical-contract.md`, `physical.py`, `run_physical.py`, `tests/test_physical.py`, `physical-review-self.md`, `source_check.py`, `protocol.py`, `contract.md`, the original plant/controller/simulation geometry, and batch `evidence/physical/20260921T144921Z`. The reviewer changed only `physical-audit.py`, this report, and `evidence/physical-audit.json`; no API, commit, implementation edit, or historical-artifact edit was performed.

## Executed audit

`python physical-audit.py` completed with exit code 0. The final script SHA-256 and plan/summary/trace identities are in `evidence/physical-audit.json`. This audit does not import `physical.py`, its overlap function, or the historical collision oracle. It verifies every trace hash and per-run summary, the contract hash, all five implementation hashes bound by the plan, the serialized effective-parameter identity, and the selected original source identity.

Across all fifteen retained traces it checked:

- 22,728 source step outputs and 829 source selection outputs by re-executing the parsed original selected bytes through their language interpreter. This shares the interpreter, not a substitute handwritten controller or the source-to-model extractor.
- 66,150 motion records comprising 132,020 robot intervals by replaying delivered intents through the frozen original plant and comparing every emitted MotionPiece, then checking final poses/speeds.
- 616,374 continuous pair intervals using an independently implemented oriented-rectangle separating-axis oracle. At each interval midpoint it certifies separation over the complete interval by subtracting the two independently recomputed maximum corner-speed bounds times half the interval. All certificates succeed without subdivision; zero overlapping or unresolved intervals. The audited pairs are both robots, each robot against four walls, the same trigger-relative pedestrian while present, and the fixed H strip in braking runs. The count differs from the original oracle because this audit can certify a whole output interval across internal phase boundaries.
- 26,336 sampled observations against replayed physical pose/speed and the independently reconstructed blocked schedule; 26,316 received observations against original packets and their 0.05 s latency.
- 14,896 protocol rows for state-chain continuity and independent visible Grant/Issued/Proceed permission checks; all 54 applied-command physical snapshots; ordinary episode Apply validity from current owner/freshness/blockage, mission, generation, timing, or released outside-zone scope. Gap runs deliberately retain their faulty outcomes.
- Every one of 14 Release snapshots using complete oriented-body intersection with Z, and every one of 14 Finish snapshots against actual replayed zero speed and goal position. The source predicates do not supply these geometry/completion results.

The original five behavioral tests were inspected, but not rerun for this review; the full retained-trace audit above is the reviewer's executed validation.

## Outcome assessment

| Experiment | Independent observation | Verdict |
|---|---|---|
| P-A / P-B / P-none | First grants A / B / A; both actual missions finish at 58.9 s; no early release or reference violation | Expected |
| E2-center / E2-whole | Identical first 6,223 records, first divergence at 25.85 s. Center mutation releases overlapping bodies at 25.85 and 50.25 s; whole-body run has none. Both complete and both satisfy discrete reference events | Expected interpretation failure |
| E3a-bad / E3a-good | Validate precedes blocked update at 0.05 s; stale Commit produces exactly one illegal Grant at 0.10 s. Correct Commit produces none. Both plants remain halted outside Z | Expected Commit distinction |
| E3b-bad / E3b-good | Legal Commit and source-driven Issue precede blocked update; stale Apply produces exactly one illegal Proceed at 0.10 s. Bad actuator travels 0.0025 m and reaches 0.05 m/s over the following 0.10 s. Good Apply remains stopped. Both remain outside Z | Expected Apply distinction |
| E4-wait / E4-fifo | All observed blockage flags are false, with ordinary fresh sensor delivery. Wait run issues no grant and completes neither task through 120 s; FIFO completes both at 58.9 s | Expected advice dependency contrast |
| B2-temporary / B2-permanent | Both trigger at actual straight N centerline pose x=8.000000618, t=10.68 s. Identical pedestrian geometry starts at (12,-3.5), moves north at 1 m/s; temporary clears after 7 s, permanent stops at y=0. Temporary stops/resumes and finishes both at 66.1 s; permanent finishes neither by 120 s | Expected environmental progress contrast |
| Brake-inside / Brake-outside | Observed speed 1 m/s, heading zero, age 0.05 s, bound 1.3341 m and initial distances 1.3441 / 1.3241 m. Replay includes 0.05 s age plus 0.10 s delivery before braking. Both stop at 1.4 s, margins 0.5691 / 0.5491 m | Inside sufficient premise holds; outside premise is false but no crash is implied |

The effective delivery/onset parameter is 0.10 s and the maximum total reaction parameter is 0.27 s. The braking calculation at actual age 0.05 s uses reaction 0.22 s (age + 0.05 monitor + 0.02 compute + 0.10 delivery), while the deterministic physical trial starts Brake after 0.15 s. Those are intentionally different conservative and actual quantities. The original parameter artifact is unchanged.

## Qualifications and material gaps

1. These are synthetic deterministic reference-plant experiments, not hardware results or a continuous refinement theorem. The audit independently implements geometry but shares the original plant and original source interpreter. It checks source outputs for all logged inputs; it does not independently rebuild every trusted source-input fact or formally prove the parser/interpreter.
2. B2 triggers near zero speed (0.00078644 m/s); its blocked observation reports 0.01078644 m/s. It demonstrates stop/resume and environmental progress, not a high-speed moving-pedestrian guarantee. The separate 1 m/s braking pair evaluates a fixed-boundary sufficient condition, with conservative parameter margins not exhaustively stressed.
3. E4's 120 s timeout and permanent B2's noncompletion are bounded observations. They are not standalone proofs of divergence or impossibility. Current checks use a synchronous local scheduler, and no arbitrary distributed revocation, out-of-order delivery, or dynamic registration claim is supported here.
4. Plan provenance is incomplete for transitive execution code: it binds `physical.py`, original plant/oracle/controller/simulation, source bytes, contract, and parameters, but does not bind `protocol.py`, `source_check.py`, the language interpreter, or `run_physical.py`. This review inspects their current versions and verifies retained source/plant consequences; the batch hash list alone cannot establish their exact run-time versions. A complete future reproducibility manifest should bind these dependencies too. Do not rewrite the historical plan to imply it originally did so.
5. The effective parameter copy inherits old, unused `stress_levels` labels (including reaction 0.25 s labelled boundary). The executed timing fields and bound use the corrected 0.10/0.27 values. The inherited design labels are not results from this batch and should not be reported as its tested boundary.
6. The braking calibration pair directly exercises the plant, not source control logic. The reservation-zone HOL projection excludes legitimate post-release travel, and E2 proves why logical release alone cannot establish physical clearance. Original-source approach/advice execution and real advice-call evidence belong to the separately reviewed root-owned `advice_trial` work, not these physical batch outcomes.

No blocking defect was found in the declared bounded physical outcome claims. The original self-review's key numeric and scope claims are supported by independent replay, with the additional provenance qualifications above.
