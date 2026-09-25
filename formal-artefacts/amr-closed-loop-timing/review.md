# Independent review of the stable closed-loop timing package

**Review date:** 22 September 2026  
**Verdict:** **Pass after scope correction.** I found no unresolved critical, high, or medium-severity defect in the theorem statements, executable formulas, selected-source binding, retained-trace audit, or reported conditional result. One medium-severity wording issue and one low-severity plan inconsistency were corrected during review.

## Findings and resolution

### [P2, resolved] Continuous physical times were initially stated as integer-tick bounds

The Isabelle functions quantify over `nat` event times ([`AMR_Closed_Loop_Timing.thy`, lines 15–23](hol/AMR_Closed_Loop_Timing.thy)), so the proved 9- and 169-tick bounds start at an integer plant tick. A continuous crossing immediately after a tick can take almost 10 ticks to become visible/released, and a continuous arrival can take almost 170 ticks to reach Finish. The initial prose described 9/169 directly from arbitrary continuous physical instants, which exceeded the formal result.

The design and reports now define the event tick as the first integer plant tick at or after the continuous event. They state 9/169 from that quantized tick and the corresponding generic bounds of less than 10/170 from the exact continuous instant ([design, lines 16–25](../../docs/superpowers/specs/2026-09-22-amr-closed-loop-timing-design.md); [README, lines 12–21](README.md); [results, lines 9–25](../../literature/scholar_search_2026-09-10/followup/research_amr_closed_loop_timing_results_2026-09-22.md)). The 3,100-tick service premise is also explicitly said to include arrival quantization. This resolves the mismatch without changing the natural-number theorem or the 6,884-tick conditional composition.

### [P3, resolved] The plan said seven source milestones

The implementation, HOL table, tests, and reports all use eight milestone cases. The plan now says eight at [line 49](../../docs/superpowers/plans/2026-09-22-amr-closed-loop-timing.md).

## Formal result and scope

The clock arithmetic is sound for the declared natural-tick model. `next5` is a ceiling to the five-tick grid and is proved to lie in `[n,n+4]`; the observation/release, Waiting start, BrakeRequested start, and Finish functions then give the stated 9, 15/160 (covered by 163), and 169 maxima ([theory, lines 15–56](hol/AMR_Closed_Loop_Timing.thy)). The Finish derivation includes observation delivery, ten-tick Brake delivery, the 149-tick halt threshold, and the next control opportunity.

The final theorem is deliberately conditional arithmetic, not a driver refinement. Its eight timestamp premises state the first grant, two start services, two 3,100-tick travel services, two Finish services, and the inter-task grant service; `presburger` proves `f2 <= 6884` from them ([theory, lines 131–142](hol/AMR_Closed_Loop_Timing.thy)). The reports consistently preserve this distinction and do not present 68.84 s as an arbitrary-environment, whole-Python, continuous-plant, or hardware deadline.

The discrete authorization step is separately justified. Under ownership, registration, freshness, absence of blockage, and empty pending state, valid Release followed by source-compatible selection, Validate, and Commit grants the other robot for every advice value ([theory, lines 108–129](hol/AMR_Closed_Loop_Timing.thy)). This proves authorization sequencing; it does not claim physical clearance or scheduler timing.

The selected source and extracted target are kernel-evaluated at eight declared environments ([theory, lines 58–106](hol/AMR_Closed_Loop_Timing.thy)). The target result uses the previously proved universal extraction-preservation theorem rather than a second unconnected table. The exported [proof audit](hol/export/AMR_Closed_Loop_Timing.AMR_Closed_Loop_Timing/timing-proof-audit.txt) lists 16 named facts and reports no skipped proofs or oracle dependencies. The successful [Isabelle build log](hol/build.log) records all three exports.

## Executable checks and provenance

[`source_milestones.py`](source_milestones.py) loads the actual selected bytes, checks both the controller identity and raw SHA-256 against `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`, and compares literal action/mode pairs. The Python rows agree with the independently exported HOL source/target rows. The frontend remains outside the formal theorem, as the reports state.

[`verify.py`, lines 84–119](verify.py) compares the Python and HOL tables, checks 1,001 event times and 201,402 grant/brake-age/mode cases, and observes exact model maxima of 9, 15, 160, and 169 ticks. It also checks the 6,884-tick composition. The tests cover ceiling alignment, omitted sensor/command stages, the halt timer, invalid values and modes, omission of a task chain, late Proceed, late Release, missing goal Brake, and early Finish ([tests](tests)).

The verifier validates every entry in the predecessor runtime-binding, extraction-faithfulness, and progress-obligations manifests before using them ([`verify.py`, lines 31–35 and 78–82](verify.py)). It also checks the current HOL input hashes and audit export ([`verify.py`, lines 134–139](verify.py)). Thus the selected source, imported proof artifacts, and four retained trace identities are linked through recorded hashes rather than filenames alone.

## Retained physical traces and `AtGoal`

[`trace_binding.py`, lines 27–58](trace_binding.py) reconstructs complete-body clearance and exact endpoint rest from the saved motion pieces. Its audit then checks grants, accepted command applications, Release, goal Brake, halt duration, Finish, and the 163/9/3,100/169 local bounds ([lines 61–112](trace_binding.py)). It reads the four existing traces and does not rerun the physical experiment.

I independently inspected all four traces. Depending on grant order, the first source-level `AtGoal` is true at 31.3 s or 57.3 s, while exact endpoint rest occurs at 31.381854249492644 s or 57.38185424949265 s. Goal Brake is applied at 31.4 s or 57.4 s, and Finish occurs at 32.9 s or 58.9 s. Thus `AtGoal` becomes true about 8.185 ticks before physical arrival, but command delivery applies Brake only after arrival. The audit correctly bases its reported Finish latency on reconstructed physical arrival rather than equating `AtGoal` with arrival.

Across the four traces, the observed maxima are 155 ticks from Grant to applied Proceed, 8.069420084764545 ticks from exact physical clearance to Release, 2,978.1854249492644 ticks from applied Proceed to exact arrival, and 151.81457505073547 ticks from exact arrival to Finish. These are observations of the fixed retained routes, not universal implementation bounds.

## Fresh verification

I ran the complete checks from fresh processes with the bundled Python and Isabelle2025-2:

- `python -B -m unittest discover -s tests -v`: **15 tests passed** in 2.227 s.
- `python -B hol/build.py`: **exit 0**; Isabelle exported `timing.csv`, `source.csv`, and `timing-proof-audit.txt`.
- `python -B verify.py`: **exit 0**; 1,001 ticks, 201,402 start cases, eight source milestones, four retained runs, 16 proof facts, all 36 + 20 + 54 predecessor-manifest entries, and 35 local report links passed.

The remaining limitations are accurately reported: there is no theorem for the whole Python interpreter, queues, floating-point execution, arbitrary blockage or interruption, cancellation, general continuous dynamics, or hardware response. Within the stated integer-clock, stable-service, selected-source, fixed-route, and exact-reference travel premises, the package supports the claimed conditional 6,884-tick result.
