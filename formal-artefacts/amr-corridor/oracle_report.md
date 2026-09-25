# Independent collision oracle evidence

Implemented 2026-09-15 as Task 1 of the AMR implementation plan. Only standard-library `math` is imported by production code; there are no controller or plant imports.

## API

- `rectangle(pose, length, width)` returns a tuple of four counterclockwise `(x,y)` vertices; pose is `(x,y,theta)` in metres and radians. Dimensions must be finite and positive.
- `polygon_distance(a,b)` computes filled convex-polygon Euclidean distance using independent separating-axis overlap and point-to-edge distance calculations. Intersections and touching return zero. Vertex lists must be ordered, nondegenerate convex polygons; either winding is accepted.
- `sweep_check(pose_a, pose_b, length_a, width_a, length_b, width_b, duration, speed_bound_a, speed_bound_b, *, epsilon=1e-9, max_depth=24, max_intervals=100000)` returns `{'status': 'clear'|'collision'|'unresolved', 'witness_time': float|None, 'distance_lower_bound': float}`.

Pose callbacks receive relative times in `[0,duration]`. Each speed bound must bound the speed of every material body point, including rotation, over the entire interval. For rigid motion, a sufficient point-speed bound is the translation-speed bound plus angular-speed bound times the rectangle circumradius. This precondition is the caller's responsibility and cannot be inferred from finitely many callback samples.

The algorithm samples interval endpoints for immediate collision witnesses, then adaptively subdivides intervals whose midpoint distance does not certify separation. The separation bound is midpoint distance minus epsilon minus the sum of point-speed bounds times the half-interval duration. A clear result returns the minimum certified bound across all covered leaves. Exhausted subdivision or visit budgets yield unresolved; collision and unresolved use the universally conservative zero lower bound. A witness is a sampled numerical contact, not necessarily earliest contact.

## Tests and actual runs

Command, from `.`:

```powershell
& C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s formal-artefacts/amr-corridor/tests -p test_oracle.py -v
```

Tests were written before production code. An initial class-setup absence assertion was classified by unittest as one setup error; the harness was corrected to a per-test assertion before implementation. The subsequent genuine red run, before `oracle.py` existed, reported:

```text
Ran 9 tests in 0.003s
FAILED (failures=9)
AssertionError: False is not true : Independent collision oracle has not been implemented
```

After implementing the oracle, the same command reported:

```text
test_exact_contact_and_zero_duration ... ok
test_frame_endpoints_clear_but_midpoint_crosses ... ok
test_invalid_inputs_are_rejected ... ok
test_polygon_analytic_distances_overlap_and_contact ... ok
test_rectangle_rotation ... ok
test_rotation_sweep_hits_between_clear_endpoints ... ok
test_static_clear_has_conservative_distance ... ok
test_subdivision_finds_off_midpoint_collision ... ok
test_unresolved_budget_never_reports_clear ... ok
Ran 9 tests in 0.009s
OK
```

Analytic fixtures include a 3-4-5 diagonal gap, containment, exact edge contact, a 90-degree rectangle rotation, an inter-frame translational crossing at `t=0.5`, an off-midpoint crossing at `t=0.25`, a 180-degree rotating bar that hits an obstacle only during its sweep, a 1.8 m stationary clearance, and explicitly exhausted subdivision. Validation tests reject negative duration/speed bounds, nonfinite inputs, nonpositive dimensions, invalid epsilon, and invalid budgets.

## Limits

This is a reference numerical algorithm, not a formally verified collision checker or interval-arithmetic implementation. `epsilon=1e-9` m is a numerical tolerance for the small synthetic scene; a sampled gap within epsilon is reported as numerical collision, even if mathematically positive. Floating-point roundoff is not rigorously enclosed for arbitrary coordinate magnitudes. Continuous, deterministic callbacks and correct point-speed bounds are assumed; a discontinuity or an underestimated bound can invalidate clearance. Concave, unordered, or degenerate polygons are outside the distance API contract. Very close trajectories or oversized bounds can exhaust budgets and remain unresolved. No physical-model, controller, certification, or real-robot safety claim follows from these tests.

Files added by this subtask: `oracle.py`, `tests/test_oracle.py`, and this `oracle_report.md`. No commits, cleanup, or changes to existing research documents were made.
