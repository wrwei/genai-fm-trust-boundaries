# Physical implementation self-review

Executed batch: evidence/physical/20260921T144921Z. Its plan and effective parameter
copy were written before runs. All fifteen run IDs were declared in physical-contract.md
before execution. Five behavioral tests first failed because physical.py was missing
(red-tests.txt), then passed; final observed result: 5 tests, 79.295 s, OK
(green-tests-final.txt). Earlier diagnostic test output remains preserved.

## Observed results

- P-A, P-B, P-none: first grants A/B/A respectively; both robots complete at 58.9 s
  with independently checked goal positions and actual zero speed.
- E2-center: two independently confirmed early releases, A at 25.85 s and B at
  50.25 s; both actual rectangles overlap Z. E2-whole has zero early releases.
  Both have zero discrete reference-event violations: the reference consumes Clear,
  which is precisely the physical interpretation gap being tested. Their first 6,223
  trace records are identical; first divergence occurs at 25.85 s. Subsequent plant
  observations are independently produced by each branch. Both finish; that does
  not repair the early release failure.
- E3a-bad: one stale Grant reference violation after revocation. E3a-good: none,
  and no Grant. E3b-bad: one revoked Proceed reference violation after legal
  Commit/Issue, actual speed rises from zero to 0.05 m/s in the bounded .10 s motion
  interval. E3b-good rejects Apply and remains at zero speed. All remain outside Z.
- E4-wait: no grants or completed robots through 120 s; FIFO completes both at
  58.9 s in the same clear environment. Finite timeout is not a proof of divergence.
- B2-temporary: state trigger 10.68 s, A on straight N at x=8.000000618, y~0,
  heading~0, speed .00078644 m/s. First blocked observation at monitor 10.75 s
  has age .05 s, speed .01078644, front distance 3.099884 m, required .293703 m.
  One pedestrian Brake and one Resume; both robots complete at 66.1 s.
- B2-permanent: same state trigger; no completion through 120 s; stopped waiting.
- Brake-inside/outside: observed speed 1 m/s, age .05 s, heading 0, required
  bound 1.3341 m, distance 1.3441/1.3241 m. Actual plant evolves during .05 s age
  and .10 s queued command delivery. Both halt at 1.4 s; actual front margins
  .5691/.5491 m. Only the inside run satisfies the sufficient premise. Neither
  crosses H. The outside result does not imply a violated guarantee or collision.

All fifteen summaries report zero collision/unresolved pairs. Expected-outcome
checks pass 15/15, including deliberate failures; this is not fifteen safe-and-complete
runs. Seven complete episodes produce fourteen Finish snapshots with actual speed
zero. Raw observations, source inputs/actions, protocol states/events, command
bindings/verdicts, release/complete snapshots and MotionPieces are gzip JSONL.
trace-diagnostics.json independently rechecks Release overlap and Finish speed and
records the common E2 prefix. Run summaries bind trace hashes; the batch plan binds
source, physical adapter, unchanged plant/oracle/controller/simulation hashes,
original parameter hash and separately serialized effective parameter hash.

## Scope and residual limitations

The accepted raw P3-R1 source is always loaded through SourceController.from_selected;
there is no SourceSupervisor parse adaptation or handwritten functional fallback.
The scheduler is a deterministic local .01 s reference simulation, not measured
hardware or a distributed revocation protocol. Actual observation age is .05-.09 s
between arrivals; control runs at .05 s and uses .05 s snapshots. Command delivery
is .10 s. Bounded sustained-Brake evidence uses the corrected .27 s total parameter;
completion separately checks actual speed. No continuous physics refinement theorem
is asserted. HOL applies only to the reservation-zone protocol. Post-release source
Proceed is separately labeled outside_zone_after_release; intentionally premature
Release is recorded as a physical violation even though the source has logically
entered that phase.

B2 triggers near zero speed at the first straight centerline state; it is a stop/resume
and environmental-progress demonstration, not a high-speed stopping stress test.
The separate braking pair covers speed 1 m/s. The braking pair uses the frozen plant
and an independent H rectangle sweep, not the source control logic, because its
purpose is calibration of the declared physical envelope. It does not prove a
moving-obstacle guarantee. E3 logs its protocol witness then the explicit stationary
prefix and .10 s actuator-motion trace; replay should order by the time fields.
The approach window implementation is root-owned advice_trial.approach_trace(), as
agreed; this adapter does not duplicate or alter it. No APIs, commits or historical
artifact changes were made by this task.
