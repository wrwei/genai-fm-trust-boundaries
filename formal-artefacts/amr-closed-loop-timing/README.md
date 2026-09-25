# AMR stable closed-loop timing — 22 September 2026

This additive package closes the next bounded gap in the AMR evidence chain. Under a stable usable environment, continued control/service execution, fixed observation and command delivery, and the previously justified exact-reference travel service, it connects the accepted source's milestone decisions to a conditional two-task completion bound of **6,884 ticks = 68.84 s**. It does not change the accepted controller, protocol, plant, retained runs, or active manuscript.

Design: [predeclared scope](../../docs/superpowers/specs/2026-09-22-amr-closed-loop-timing-design.md). Results: [Chinese report](../../literature/scholar_search_2026-09-10/followup/research_amr_closed_loop_timing_results_2026-09-22.md). Review: [independent assessment](review.md).

## Kernel-checked result

[AMR_Closed_Loop_Timing.thy](hol/AMR_Closed_Loop_Timing.thy) imports the existing runtime binding, concrete extraction artifact, protocol, and progress theory. Its Isabelle2025-2 build proves:

- the five-tick ceiling is on the control grid and adds at most four ticks;
- a predicate recorded on an integer plant tick becomes source-visible, and integer-tick body clearance is released, within nine ticks under the declared five-tick sampling/delivery contract;
- a stable grant in `Waiting` or `BrakeRequested`, with Brake already applied no later than the grant, reaches applied Proceed within 163 ticks;
- an integer plant tick recording arrival at rest reaches Finish within 169 ticks through observation, Brake delivery, the halt timer, and the next control opportunity;
- the exact selected source and extracted target produce the declared outputs on eight stable milestones;
- after a valid release, if the other request remains registered and permission is fresh and unblocked, selected Validate followed by Commit grants that other robot;
- if the first grant occurs by tick 10, each task satisfies the 163/3,100/169 local inequalities, and the next grant follows the prior finish within 10 ticks, the second Finish is no later than tick 6,884.

The composition theorem keeps every local time inequality as a premise. The 3,100-tick travel term is the imported exact-reference service, not a theorem about arbitrary Python plants or hardware. The exported [proof audit](hol/export/AMR_Closed_Loop_Timing.AMR_Closed_Loop_Timing/timing-proof-audit.txt) contains 16 facts with no skipped-proof or oracle dependencies.

The HOL time variables are natural-number plant ticks. When a continuous crossing or arrival happens between ticks, its event tick is the first integer tick at or after that time. Thus the generic bounds measured directly from the exact continuous instant are **less than 10** and **less than 170** ticks, respectively; the 9/169 statements start at the quantized event tick. The 6,884-tick theorem uses that integer arrival tick and a 3,100-tick service premise that already includes quantization.

## Executable and retained evidence

[timing_model.py](timing_model.py) independently implements the published integer formulas. The verifier checks 1,001 event times and 201,402 grant/brake-age/mode combinations. Exact maxima are 9 ticks for observation/release, 15 for the `Waiting` start path, 160 for the `BrakeRequested` path, and 169 for arrival-to-Finish. The stated 163-tick common start bound is deliberately conservative.

[source_milestones.py](source_milestones.py) loads the accepted source bytes with SHA-256
`9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`
and checks eight literal action/mode results. Python results equal the independently exported HOL source and extracted-target table.

[trace_binding.py](trace_binding.py) reads, but does not rerun, the four stable physical traces from the runtime-binding package. It reconstructs continuous body-clear crossing and endpoint arrival from motion pieces, then checks protocol grants, applied commands, release, goal Brake, halt duration, and Finish. All four still finish at 58.9 s. Their largest observed delays are:

| Milestone | Observed maximum | Proved/assumed bound |
| --- | ---: | ---: |
| Grant to applied Proceed | 155 ticks | 163 ticks |
| Physical clearance to Release | 8.069421 ticks | 9 ticks |
| Applied Proceed to physical arrival | 2,978.185425 ticks | 3,100-tick exact-reference premise |
| Physical arrival to Finish | 151.814576 ticks | 169 ticks |

The source's Boolean `AtGoal` tolerance can become true shortly before exact endpoint arrival. The audit therefore computes physical arrival independently and does not equate `AtGoal` with arrival. In the retained runs the source requests goal Brake before arrival, but its ten-tick delivery applies Brake after the plant has reached the endpoint at rest.

Fifteen tests include negative mutations for late Proceed, late Release, missing goal Brake, early Finish, invalid times/modes, and formula omissions. [Final verification](evidence/verification.json) also rechecks the 36-, 20-, and 54-file predecessor manifests.

## Scope and reproduction

The result assumes stable usable observations, no pedestrian blockage, active tasks, continued control/service opportunities, accepted command delivery, no permanent fault, fixed routes, and the exact reference travel service. Temporary-blockage recovery, arbitrary interruption, cancellation, scheduler starvation, concurrent callbacks, other maps, whole-program Python refinement, general continuous-plant refinement, and hardware response remain open.

From this directory, using the bundled Python:

```powershell
python -B hol/build.py
python -B verify.py
```

The verifier uses retained traces and makes no API calls or physical reruns. This extension made no active TeX changes, commits, or pushes.
