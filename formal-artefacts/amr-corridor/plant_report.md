# Timed plant implementation report

Scope: `plant.py` and `tests/test_plant.py` only, with this report. No controller/oracle import, package installation, commit, or existing research-file modification.

## Model and API

`RobotPlant(route, length=.8, width=.6, speed_limit=1, accel=.5, brake=.8, turn_rate=pi/2, *, initial_speed=0)` accepts finite xy vertices with distinct consecutive positions. Initial speed is a public experiment constructor input; it must permit stopping by the first waypoint. `pose`, `speed`, `finished` are read-only properties. `advance(dt, intent='Proceed')` applies an already-delivered intent, so the external scheduler owns delivery delays.

The plant integrates constant longitudinal acceleration, cruise, and deceleration analytically, solving the peak-velocity distance equation for each waypoint. Phase durations persist across time partitions. Every vertex is reached at rest before finite-duration in-place rotation; no position is clamped to a waypoint or boundary. Brake replaces the remaining plan with actual deceleration to zero. Continued braking holds, and Proceed replans from the stopped or braking state. Arrival can entail a zero-speed normalization at an analytic event, but never a positional projection.

Frozen `MotionPiece` stores duration, start_pose, initial_speed, acceleration, angular_velocity and point_speed_bound. `sample(t)` is continuous over the closed relative interval. `to_dict()` / `from_dict()` preserve exact polynomial/trigonometric reconstruction (up to floating-point evaluation). The point bound is maximum center speed plus absolute angular speed times half the footprint diagonal. Each call covers the requested time, including stationary remainder pieces.

## Evidence

Runtime: `C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
Working directory: `https://github.com/wrwei/genai-fm-trust-boundaries/tree/main/formal-artefacts/amr-corridor`.
Command: `python -m unittest discover -s tests -p test_plant.py -v`.

Red run before plant creation: six assertion failures, each `timed plant is not implemented`. An earlier discovery invocation from the repository root had an invalid start directory; this was corrected before recording the genuine red run.
Green run after implementation: all six tests passed in 0.002 seconds.

Verified behaviors:
- Initial speed 1 and brake .8: first braking interval 1.25 s, displacement .625 m, zero final speed, persistent hold without reversal.
- Full 90-degree waypoint turn: exactly 1 s at pi/2 rad/s, constant center position and zero longitudinal velocity; route completed at rest.
- Each of five alternating Proceed/Brake intervals compared as one call versus 100 partitions: matching intermediate pose and speed to nine decimal places, matching final completion.
- Braking followed by resumption reaches the route goal; delivered Brake during rotation freezes heading without a jump and subsequent Proceed completes.
- Adjacent pieces are continuous; serialized midpoint samples match exactly; endpoint speed plus footprint angular bound is covered.
- Invalid physical parameters, impossible initial stopping state, invalid time and unknown intent rejected.

## Limits

This is a deterministic reference model, not a full differential-drive dynamics model or formal proof. Longitudinal acceleration can switch instantaneously; angular inertia is explicitly omitted, so delivered Brake can freeze angular velocity immediately while heading stays continuous. Route tracking and speed have no stochastic error, wheel slip, actuator uncertainty, or lateral motion. No arbitrary initial heading is provided. Shortest signed turns are used, with an exact 180-degree tie choosing clockwise. Speed zero is normalized only at known analytic stopping events. Heading/distance comparisons use 1e-10 tolerance and residual cruise distances at most 1e-12 m are treated as roundoff; no spatial safety conclusion relies on these tests alone.

## Independent-review fixes: completion evidence

The independent reviewer reproduced A being marked complete at 31.45 s during a sensor blackout [29.9, 40), using its last observation sampled at 29.8 s. The goal was physically reached, but the logical completion transition accepted stale evidence. Added the real closed-loop regression `test_goal_completion_waits_for_fresh_observation_after_blackout`: before the fix it failed because completed_robots contained A; after requiring `usable(obs, name, t, p)` in the completion guard, it passes. That guard includes observation freshness and identity/version validity. The original seven simulation tests passed after this first fix (43.064 s).

A second review finding required scoring actual completion independently of controller Done. Added `score_completion(controller_completed, physical_states, goals)` using actual pose/speed snapshots and independently supplied goals. It accepts a reported completion only when finite goal distance is at most .01 m and finite absolute speed is at most 1e-9 m/s. The literal three-robot regression includes a wrong goal, correct goal while moving at 1 m/s, and correct goal at rest. It first failed because the scorer was missing, then passed after implementation; only the stationary correct-goal robot is counted.

Episodes now preserve controller_completed_robots separately, freeze independent_goals from the scenario at initialization, expose physical_completion_score and completion_mismatches, and derive completed_robots and safe_and_complete from physical validation. A fully reported but physically invalid completion yields termination=completion_mismatch. This checks declared scenario goals; it is not an independent natural-language task-semantics oracle.
Final targeted verification: python -m unittest discover -s tests -p test_simulation.py -v completed all 8 tests successfully in 31.516 seconds after both fixes.
