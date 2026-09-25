# AMR transport progress obligations — 22 September 2026

This additive package makes the existing **physical exit-capability premise** quantitative. It does not change the accepted controller, adapter, reference plant, prior evidence, or manuscript. The [original scenario, section 7](../../literature/scholar_search_2026-09-10/followup/research_amr_scenario_2026-09-15.md) already limits progress to continued control execution, eventual removal of blockage, a reservation holder capable of exiting, and no permanent hardware fault. The stationary witness deliberately removes that capability; it does not refute the original complete premise set.

Design: [scope and predeclared experiment](../../docs/superpowers/specs/2026-09-22-amr-progress-obligations-design.md). Results: [Chinese report](../../literature/scholar_search_2026-09-10/followup/research_amr_progress_results_2026-09-22.md). Review: [independent assessment](review.md).

## What is proved and measured

- [AMR_Progress.thy](hol/AMR_Progress.thy) proves the exact rest-to-rest profile bound `T <= L/v + k*v`, where `k=1/(2*a)+1/(2*b)`, and establishes the peak/cruise premises for `w=min(v,sqrt(L/k))`. It also proves that a finite nonnegative duration list drains in its total time. These are real-number profile/schedule results, not a refinement proof of Python floats, continuous plant code, or the closed-loop driver.
- An explicit constant-function model satisfies `x'=v`, `v'=a`, nonnegative speed/acceleration and their upper bounds, while never reaching a different goal. A separate theorem adds **assumed local timestamp bounds** for two tasks. Its 70.2-second instance is budget accounting, not a new theorem discharging those bounds for the implementation.
- [38 fixed comparisons](evidence/profiles.json) independently calculate phase durations and compare them with the actual reference plant's emitted motion pieces and terminal rest. Both staged routes have length `14+4*sqrt(2)` m, five segments and two seconds of turns. At the actual reference defaults their duration is **29.7818542495 s**. Replacing each diagonal length with 3 m yields a conservative **30.125 s** ceiling, rounded to a 31-second diagnostic travel budget.
- [Four retained executions](evidence/nominal-obligations.json), reused without new physical runs, satisfy the fixed sample/control clocks, all due sensor deliveries exactly once, command delivery, held Proceed until arrival, release, physical standstill, and local timing budgets. First/second grant-to-motion delays are 1.55/0.15 s; arrival-to-Finish delay is about 1.51815 s; the first task finishes at 32.9 s and the last at **58.9 s**. Six negative audit tests reject delayed commands, missing control, missing motion, false standstill, missing observations and duplicate delivery.
- [One new constructed witness](evidence/stationary-2026-09-22/summary.json) retains the same driver code object and copies its globals with only `RobotPlant` substituted by `StationaryPlant`. A receives a grant at 0.05 s and Proceed at 1.6 s, but both robots remain stationary and neither completes by 120 s. There is no collision, unresolved geometry, early release, protocol-reference violation or completion mismatch. The unchanged driver's geometry oracle checks 108,000 pair intervals; the final verifier independently checks the nine constant robot/wall separations.

The witness [audit](evidence/stationary-2026-09-22/audit.json) verifies 2,410 adapter transitions against HOL, 4,802 source motion decisions through the retained source-link audit, and 24,000 constant robot motion intervals. Exact-reference-plant replay rejects the witness at **1.6 s**, when the nominal plant would accelerate at 0.5 m/s². That rejection is expected: numeric safety envelopes permit the stationary behavior, while the exact progressing reference dynamics do not. The 120-second run is a bounded observation; the separate constant-function HOL countermodel establishes the unbounded mathematical non-completion statement.

## Conditional budget and remaining work

| Local obligation | Diagnostic budget | Status |
| --- | ---: | --- |
| Initial grant / next grant after prior task finishes | 0.1 s | Checked on four traces; universal driver scheduling proof open |
| Grant to held Proceed | 2 s | Checked on eight transports; source/timing refinement open |
| Held Proceed to physical arrival at rest | 31 s | Exact-profile theorem and 38 implementation comparisons; no general Python/physical refinement |
| Arrival at rest to reported Finish, including release | 2 s | Checked on eight transports; source/timing refinement open |

Serializing these obligations gives `2*(0.1+2+31+2)=70.2 s`; the actual driver overlaps the first robot's post-release travel with the other's reservation. This is a conservative **conditional budget diagnostic**. It must not be presented as a universally proved mission deadline. Arbitrary interruptions, obstacles, scheduler starvation, actuator faults, or hardware response are outside this calculation.

An implementation progress guarantee needs an explicit execution-response/progress contract, such as the exact reference profile or a separately justified bounded travel service. A positive acceleration bound by itself would also need conditions about when acceleration/Proceed is applied. The existing CKA-supported authority result and source extraction theorem remain useful, but neither supplies physical progress automatically.

## Verification and provenance

Isabelle2025-2 [build](hol/build.log) passes; [14 audited facts](hol/export/AMR_Progress_Obligations.AMR_Progress/progress-audit.txt) have no skipped-proof/oracle dependencies. [Final verification](evidence/verification.json) checks 12 tests, 38 profile comparisons, four retained timing audits, the saved witness, three proof-input hashes and the previous 36 + 20 file manifests. Zero API calls, no active TeX changes, no commits or pushes.

The run's [pre-run manifest](evidence/stationary-2026-09-22/pre-run.json) records 24 input hashes. Their [exact copies](evidence/stationary-2026-09-22/input-snapshot.json) were saved after the run and checked against those pre-run hashes before later documentation/audit edits. Verification explicitly records the strengthened observation-delivery audit and review/plan updates. The experiment runner, plant mutation, retained controller and driver are unchanged from the run.

From this directory, using the bundled Python executable:

```powershell
python -B verify.py
python -B hol/build.py
```

`verify.py` reads the retained witness; it does not run the physical experiment again. `experiments.py` is the fixed original runner and refuses to overwrite its run directory. Reproduction needs a separately declared output/protocol rather than deleting retained evidence. Build-attempt logs include earlier proof development failures and the final successful build.
