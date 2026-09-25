# AMR advisory v2: physical preflight

This is a read-only implementation preflight for the approved redesign, sections 4--7. It does not authorize a claim about hardware, industrial compliance, or continuous-physics refinement.

## Exact reuse boundary

Reuse these interfaces without importing their controller truth into the v2 protocol:

- `amr-corridor.plant.RobotPlant.advance(dt, intent) -> list[MotionPiece]`, together with `pose`, `speed`, and `MotionPiece.sample`, supplies each branch's own physical trajectory.
- `amr-corridor.controller.Observation` and `usable(obs, robot_id, now, params)` supply received observations and freshness. Freshness is separate from advice validity and action permission.
- `amr-corridor.controller.braking_distance(speed, age, params, omit_reaction=False)` is the frozen straight-approach sufficient bound.
- `amr-corridor.oracle.rectangle`, `polygon_distance`, and `sweep_check`, plus `simulation.assess_interval`, are the independent physical scorers. The oracle must receive plant poses, never `BodyClearOfZ` or another controller Boolean.
- `simulation.parameters()` and `clock_multiple()` retain the frozen parameter identity and event-grid checks. `score_completion()` may remain the independent endpoint scorer.
- `amr-supervisor.closed_loop.SourceSupervisor.select(facts)` and `.step(mode, facts)` remain the only source-program decisions. Preserve separate log fields for raw source decision, guard verdict, committed action, and applied actuator effect.

Do not reuse `run_supervised_episode` as the v2 protocol itself. Its selection facts encode a preference rather than registration order; reservation acquisition is immediate after `select`; and `Actuator.accept` checks only identity/revisions/delivery/expiry/sequence. It has no Validate/Commit/Apply split, permission version, reservation generation binding, revocation barrier, mailbox, or current-state Apply guard. `Reservation.serial` increments on acquire but is absent from `Command`; carrying that serial only in a log is not a permission check.

The v2 adapter therefore needs explicit records such as `TaskContext(context_id, mission_set_version, registrations)`, `AdviceSlot(context_id, choice, received_at)`, `Decision(decision_id, source_choice, eligible_set, latched_advice, fifo_order)`, and `ProceedToken(decision_id, robot_id, permission_version, reservation_serial, observation_basis, issued_at, expiry)`. Commit must atomically recheck and acquire; Apply must query current permission, owner, reservation serial, and token validity before changing actuator intent. A new observation number alone must not revoke a still-applicable decision.

## E2: state-triggered center-only release

Use the same accepted supervisor, initial state, disturbances, and service schedule in both branches. Fork from one pre-release snapshot and then let each plant produce its own observations.

The good predicate is existing whole-body `body_clear(..., front_only=False)`. Implement the faulty predicate explicitly as center-only: `x_center > Z.right` for A and `x_center < Z.left` for B, with the same observation usability gate. Do not use existing `front_only=True`: despite its name it tests a footprint edge, not the center, so it is the wrong mutation.

Trigger the comparison on the first monitor event at which the owner's observed center is beyond the exit boundary while the independent current plant rectangle still intersects `rectangle((12, 0, 0), 12, 5.2)`. At that event, pass the branch-specific Clear Boolean to the unchanged source step. Score a `Release` as premature when the actual plant rectangle has `polygon_distance(..., zone) <= 1e-9`. The required witness is early Release; collision is neither required nor an acceptable substitute. File/hash rejection, different observations copied from the other branch, or controller geometry reused by the oracle do not count as E2 evidence.

## E3: stopped, outside-zone witnesses

Use a robot halted at its staging point before entry: A at `(4,-2)` or B at `(20,2)`. Both are outside `Z=[6,18]x[-2.6,2.6]`; verify this with the oracle rectangle and `speed == 0` before injecting the change. Keep the plant under Brake throughout the witness prefix so braking inertia cannot be mistaken for an authorization failure.

- **E3a Validate to Commit:** create and validate a candidate while owner is free and entry permission is true; then increment the permission version and set permission false; then call Commit. The good protocol rejects or revalidates and emits no Grant/acquire. The faulty paired protocol omits only the Commit recheck and records the stale Grant.
- **E3b Issue to Apply:** establish a legal owner and Commit, issue a Proceed token while permission is true, then revoke permission/increment its version before the queued delivery event. The good Apply leaves the actuator at Brake and logs a stale/revoked rejection. The faulty paired protocol omits only the Apply check and changes actuator intent to Proceed. End or brake immediately after the Apply verdict so the witness remains about authorization outside Z.

For deterministic same-time ordering use: trusted permission update, queued Apply, monitor/service. Record old and current permission versions, owner, reservation serial, decision id, token generation, plant pose/speed, actuator intent before/after, and all four source/guard/commit/apply layers. Rejecting E3b early at Commit does not witness the Apply gap; allowing the plant to enter Z before revocation confounds the test.

## Real-advice advance window

Freeze two task registrations before any request: A first, B second, with stable task identities and mission-set version. This makes absent-advice FIFO deterministically A-before-B. Send the single advice request for that task context when both tasks are registered but both robots are still on their approach to their waiting positions. A valid `B` reply can then change the first grant; a valid `A` reply agrees with FIFO.

Use a real-time-paced approach prelude: start the plants at route endpoints `(2,-2)` and `(22,2)`, advance normally toward staging `(4,-2)` and `(20,2)`, and stop them there under the ordinary plant/controller schedule. Run the advice request concurrently; its callback may only fill the one-slot mailbox. The simulation clock advances from a monotonic wall-clock schedule and never waits for the callback. Latch exactly once when both zone requests are present and both robots are halted at staging; consume only a response parsed and queued before that event, otherwise call source `select` immediately with no advice and A-before-B FIFO facts. Late/duplicate responses are logged and cannot restart selection.

Record dispatch wall/simulation time, parsed-arrival wall/simulation time, fixed latch time, opportunity-window duration, adopted/not-adopted reason, and source result. If execution faster than real time is retained, actual service latency cannot participate in a physical window; only replay compatibility may be claimed. Do not pause simulated time, delay staging/latching based on response status, or preselect one candidate outside `C.select`.

## Straight braking boundary calibration

Build a dedicated straight plant on the N centerline, A heading `0` toward the fixed H boundary `x=11.5` (or symmetric B heading `pi` toward `x=12.5`). At the trigger observation verify heading, centerline, footprint-before-H, finite speed, and observation age as `pedestrian_stopping_evidence` does. Let

`D = braking_distance(observed_speed, now - sample_time, frozen_params)`

and define front-edge distances `D + epsilon` (inside the sufficient domain) and `D - epsilon` (just outside), with a declared positive `epsilon` larger than numerical tolerance, for example `0.01 m`. Start both paired runs from otherwise identical observed speed/state, trigger Brake on that observation, deliver it through the normal queue, advance with `RobotPlant.advance`, and use the independent front-edge geometry at exact halt to report margin, boundary crossing, and any unresolved interval. The outside run only shows that the guarantee's premise is false; it does not predict collision.

The current helpers expose a timing inconsistency that must be resolved before calling the inside run guaranteed: `braking_distance` assumes `brake_delivery_and_onset_upper_bound = 0.08 s`, while both existing simulations deliver commands after `0.10 s`. Either change the v2 scheduler to a measured/bounded delay no greater than `0.08 s`, or calculate and label a v2 bound using an assumption at least as large as the actual delivery/onset. Do not hide this by using the separate `total_reaction_upper_bound=0.25 s`; the helper currently sums observation age, monitor period, compute bound, and the `0.08 s` field directly. Also retain `actual_brake >= 0.8 m/s^2`; a weaker plant belongs to an assumption-violation calibration, not the just-outside distance pair.

## Physical inconsistencies and hidden substitutes to block

- Existing `front_only=True` is edge-clear, not center-clear.
- Existing `halt_bound` is elapsed commanded-Brake evidence, not a direct physical speed check; E3 setup must additionally check plant speed zero.
- Existing supervisor runtime acquires immediately after selection and delivers commands without current reservation/permission binding; logs do not repair these missing checks.
- `preference` is not FIFO registration order, and one eligible robot must still be selected regardless of advice.
- The current plants start at staging because routes are passed with `[1:]`; a useful real-advice advance window needs an explicit approach prelude or a separately justified waiting delay fixed before dispatch.
- Real API wall latency measured against a compute-fast simulation is not physical responsiveness. Pace the experiment or report only replay/interface compatibility.
- A stale action rejected by mission/map revision is not an E3 permission-revocation witness unless that revision is the declared permission state and is checked at both Commit and Apply.
- A file identity mismatch, safety fallback, lack of collision, or copied paired trajectory cannot substitute for the independent E2/E3 oracle verdict.
