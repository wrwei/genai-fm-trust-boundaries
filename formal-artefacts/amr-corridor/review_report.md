# Independent review — AMR reference environment

Date: 2026-09-15. Reviewed the immutable `review_package_initial.txt`, the implementation plan, scenario and evaluation specification, parameter JSON, and the current runner. This review covers the first environment stage only: handwritten R/R-Stop, both normal orders, temporary/permanent blockage, observation blackout, front-only release and stopping-bound mutations. No generated DSL, LLM service, theorem or arbitrary pedestrian guarantee was assessed.

## Judgment

The core architecture follows the first-stage plan. The plant integrates analytic timed translation and finite-duration turns independently of the stopping formula. The controller module imports neither plant nor oracle. Sensor sampling is the explicit truth-to-observation boundary. The continuous collision checker uses independent rectangle geometry, a point-speed Lipschitz bound and conservative unresolved results; integration checks robot/robot, robot/wall and robot/pedestrian pairs over the union of plant phase boundaries. True occupancy is used for release scoring, not for deciding release. No general mathematical proof of the floating-point algorithm is established by this review.

One completion-evidence defect must be corrected before the reviewed snapshot is treated as the final reference. Several reproducibility improvements are also identified below. No current fixed-scenario collision-oracle unsoundness or physical trajectory discontinuity was found by inspection.

## Prioritized findings

### R1 — P2: completion bypasses observation validity

Initial `simulation.py:179` checks `obs` and distance to goal but does not call `usable`. Other decisions and release do call it (`controller.py:29–33`, `48–50`, `110–112`). Completion can therefore rely on a stale sample while the current decision correctly says the observation is unusable.

Reproduction on the initial snapshot: `run_episode(sensor_blackout=(29.9, 40), horizon=32)` marks A complete at 31.45 s using the last received sample at 29.8 s, age 1.65 s rather than the permitted 0.10 s. For the targeted state-machine diagnostic only, `simulation.assess_interval` was replaced in memory with a no-op; the same production plant, controller, sensor and command scheduling code ran unchanged. This diagnostic is not collision evidence. The actual robot reaches its target in this exact deterministic case, so this finding demonstrates invalid completion evidence, not a demonstrated physical wrong-goal outcome.

Require `usable(obs, name, t, p)` at Finish, and run a real closed-loop regression that withholds completion during the target-time blackout and permits it after fresh observations return. Root accepted this finding and delegated the fix; the original snapshot remains the reference for these line numbers.

### R2 — P2: hashed parameter edits can silently disagree with simulated physics

Initial `simulation.py:76–77`, `111`, `157–158`, `230–236`, and `247` use hardcoded footprint, zone, or RobotPlant defaults, whereas the controller reads the JSON values. Timing and walls also contain fixed constants (`48–50`, `105–107`). These constants agree with the frozen JSON today, so there is no demonstrated mismatch in the current evidence. However, editing the parameter file can change the controller bound and recorded parameter hash without changing the actual body or dynamics being scored.

Pass relevant parsed values consistently to plant and oracle, or explicitly validate and reject drift in fields that intentionally define one frozen fixture. A claim of a parameterized scenario family would be premature without this. The current synthetic fixed-parameter scope makes this a reproducibility defect rather than evidence that the present trajectories are wrong.

### R3 — P2: completion score lacks an independent physical terminal check

Initial `simulation.py:225–226` defines `safe_and_complete` from the controller-owned `completed` set plus collision/unresolved/release statistics. It does not separately verify true goal position and zero speed, although the evaluation protocol requires correct physical target completion. The present nominal model reaches the correct goals, and no wrong-goal trace was established. Still, an independent evaluator should verify terminal target distance, speed and declared target tolerance so that a future observation/adapter mutation cannot award its own success through Done. Keep this true-state score outside the controller path.

### R4 — P2: refined stopping runs omit complete motion traces

The initial runner's `run_suite.py:95–100` executes the two C07 0.005 s refinements without an `emit` callback. Their JSON decision summaries are retained, but unlike the other stopping runs, the complete MotionPiece stream is absent. Wrap them in `trace_writer`, as for the three coarse witnesses. Full motion records are an explicit Task 4 evidence requirement.

## Code quality and claim boundaries

- The modules have small, readable interfaces and clear dependency separation. Command sequence, recipient, revision and delivery-expiry checks are explicit. Reservation ownership is not reclaimed by timeout.
- Rotation freezes immediately under delivered Brake; angular inertia and angular acceleration are not modeled. The plant documents this simplification. Finite-duration rotation and zero translational speed at turns remain preserved.
- The oracle's continuous callback and all-body-point speed bounds are trusted preconditions. It validates numeric range, not whether an arbitrary caller supplied a true motion bound. That is appropriate for this interface but must remain explicit.
- `distance_lower_bound_m` is a conservative interval-wide lower bound, not an exact sampled or exact global minimum distance. `collision` includes numerical contact within epsilon. Unresolved must remain separate from clear.
- Pedestrian first-observation stopping admissibility is logged; it is not a general continuously enforced pedestrian avoidance invariant. The current pre-fixed timing and strip trajectory support conditional examples only.
- The sensor is delayed exact truth in ordinary episodes. Declared position/speed error bounds are used in controller margins but boundary noise trajectories are not thereby tested. The `.01` goal tolerance deserves an explicit definition alongside those assumptions.
- The API returns only unresolved pair names (`simulation.py:94–95`), not the unresolved time intervals. No such result was observed in the supplied suite, but retaining interval witnesses would make future unresolved evidence easier to audit.
- Manifest hashes must correspond to the code actually executing each run. The initial suite running concurrently with review fixes is preliminary and should be rerun from final unchanged sources before delivery.

## Verification record and limits

Parent reported genuine passing tests: oracle 9, plant 6, controller 6, simulation 5 plus blackout 1. I reviewed those tests and did not rerun the identical suite. My independent executed check was the target-time blackout state-machine diagnostic above; an additional bounded sensor-bias exploratory diagnostic did not establish a physical false-completion case and is not used as a finding or result claim. The source was not changed for diagnostics.

This report does not certify final runner outputs, rerun the complete recorded experiments, establish abstract/continuous refinement, prove numerical bounds, verify all 12 evaluation categories, validate sensor-error stress families, establish hardware calibration, or assess LLM quality. Parent owns final evidence generation and preservation of prior research fingerprints. Follow-up fixes and their actual regression results should be appended before final acceptance.

## Focused final-snapshot re-review

Reviewed `review_package_final.txt` on 2026-09-15, compared its changes against the initial snapshot, and checked current source line references. This section supersedes the open-finding status above; the initial findings are retained as the review history.

| Finding | Disposition | Final source and evidence |
| --- | --- | --- |
| R1 — completion freshness | Addressed | `simulation.py:212` now requires `usable(obs, name, t, p)` before recording completion. `tests/test_simulation.py:64` executes the original target-time blackout through the real closed loop and rejects completion during loss of observation. |
| R2 — parameter drift | Addressed for the explicitly frozen fixture | `simulation.py:22` verifies the complete parameter-file SHA-256 before parsing. Changes to dynamics, geometry or even byte formatting are refused rather than silently applied inconsistently. `tests/test_parameters.py:13` supplies a changed-width file and requires rejection. This is intentionally not a generalized configurable map implementation. |
| R3 — physical terminal scoring | Addressed | `simulation.py:105` independently checks actual position against declared goals with 0.01 m tolerance, and actual speed against 1e-9 m/s tolerance. `simulation.py:253` supplies plant snapshots and preserves controller-reported completion separately. `safe_and_complete` uses validated physical completion; a logical terminal mismatch is separately reported. The literal wrong-goal and moving-at-goal fixtures at `tests/test_simulation.py:53` exercise rejection. |
| R4 — refined stopping traces | Addressed in runner implementation | `run_suite.py:89` now writes complete compressed MotionPiece traces for both refined stopping runs. Source hashes before/after execution (`42`, `97`) and a drift failure (`110`) strengthen run provenance; final artifact presence remains part of the root's evidence checks. |

The recovery half of R1 was additionally checked with a targeted state-machine run to horizon 41 s under blackout (29.9, 40): A's first complete event occurs at 40.0 s, after sensor reception resumes, and independent physical scoring accepts A with no mismatch. As in the earlier diagnostic, only `assess_interval` was disabled in memory to avoid repeating collision work; this establishes state-machine recovery behavior, not new collision evidence. The checked-in regression stops at 32 s and therefore tests withholding completion, despite its name mentioning recovery. No source changes were made by the reviewer.

No new blocking defect was found in the four fixes. Source inspection supports closing R1–R4 for this first, frozen reference environment, contingent on the root's already-running final tests and complete evidence generation succeeding. Final recorded outputs and the forthcoming README/research account have not yet been reviewed here. Earlier limits concerning conditional pedestrian examples, exact delayed sensing, numerical oracle preconditions, and absence of formal or hardware guarantees remain applicable.

## Final evidence and document check

Reviewed the final `README.md` and `research_amr_results_2026-09-15.md` against `results/reference-2026-09-15/summary.json`, `manifest.json`, the C10 event result, and the final test-log tail. No numerical discrepancy or new blocking overclaim was found.

- Episode times 57.40/57.40/64.95/62.90/120.00/120.00/53.95 s match their corresponding records. The front-only case completes both tasks but has two early releases and `safe_and_complete=false`; the prose correctly reports an occupancy violation without inventing a collision. All seven base episodes report no collision, unresolved pair or physical completion mismatch.
- C10 records one pedestrian brake and one recovery. Its first blocked observation at 10.05 s has observed distance 2.95117 m versus required 0.526574 m. The documents correctly limit this to one prescribed, visible trajectory and do not claim arbitrary pedestrian avoidance.
- The stopping clearances 0.525 m, 0.075 m and -0.100 m, the full-bound brake times 2.35/2.45/3.70 s, and the distinction between insufficient margin and actual boundary crossing match the output. Weak braking is correctly labeled an offline-known assumption violation, not an online-detected fault or a within-assumptions failure.
- The stated denominators match the manifest: seven base plus three refined episodes, three base plus two refined stopping runs, and a separate geometric snapshot. The prose excludes unit tests, development records and repeated runs from claims of independent industrial samples. The final log says 30 tests passed.
- All five refinements report unchanged outcomes; the three episode completion-time differences are zero and maximum final-coordinate differences are approximately 8.1e-13 m. The manifest records unchanged code and parameters, ten episodes, five stopping runs, zero LLM calls and zero new formal builds. Both refined stopping traces now appear in the manifest.

The documents explicitly disclose fixed parameter identity, exact delayed sensing without injected localization noise, instantaneous angular stop as a simplification, numerical oracle limitations, incomplete interface/version evaluation, and remaining LLM/formal/hardware work. The claim that this first reference-environment stage is complete is supported at this scope. No blocking item remains from this review.

I did not rerun the suite or independently repeat every hash/trajectory reconstruction. The root reports a separate integrity check reconstructing all 15 traces and checking final poses, hashes and 152 protected files. That integrity result remains attributable to the root's recorded check; this final review is an independent consistency and evidence-scope assessment of the delivered documents and results.
