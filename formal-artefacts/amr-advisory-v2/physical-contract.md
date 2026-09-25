# Physical contract frozen before suite execution

Run IDs: P-A, P-B, P-none, E2-center, E2-whole, E3a-bad, E3a-good,
E3b-bad, E3b-good, E4-wait, E4-fifo, B2-temporary, B2-permanent,
Brake-inside, Brake-outside. Fifteen bounded runs; constructed failures retained.

Raw source: SourceController.from_selected(), frozen selected P3-R1; no replacement
controller. One registration each A then B; staging poses (4,-2), (20,2).
Original plant, geometry, routes and continuous polygon oracle remain unchanged.
Implementation adapts scheduling ideas from amr-supervisor/closed_loop.py; it does
not call SourceSupervisor or monkeypatch historical modules.

Effective v2 parameters are a separate serialized copy: command delay/onset .10 s,
total reaction .27 s, accepted observation age .10 s. Actual observations lag .05 s;
monitor .05 s, plant output .01 s. Source facts use received observations and bounded
sustained Brake evidence. Finish is independently scored against actual pose/speed.

Current permission update precedes queued Apply, which precedes monitor decisions.
Zone Proceed requires current owner and matching reservation generation; Brake is
unconditional. Post-release Proceed is explicitly outside-zone travel, outside the
HOL reservation-zone event projection. Fixed mission identity is mission-A/B.

E2 paired runs replay an identical deterministic prefix, then each has its own
observations. Center-only Clear is usability AND center x>18 (A), x<6 (B).
Every Release is independently checked for rectangle overlap, even without collision.
E3 uses stopped staging snapshots, selected A, Validate; revoke after Validate for
E3a or after legal Commit/Issue for E3b. Delivery .10 s; bad Apply physically advances
for .10 s, still outside Z. Correct version rejects at the specified final check.

B2 triggers once on the owner's first actual straight N centerline pose before H
with aligned heading. Pedestrian starts at (12,-3.5), moves north at 1 m/s for 7 s;
permanent stops at y=0. Sensor blocked is true throughout crossing/permanent blockage.
Independent sweeps use that same exogenous trajectory. Trigger and braking domain
are logged. Clear runs horizon 120 s; E4 wait horizon 120 s; B2 horizon 120 s.

Straight braking uses observed speed 1, heading 0, centerline N, initial observed
front distance braking_distance(1,.05,v2) +/- .01 m. Plant evolves for observation
age .05 then command delay .10 before Brake. Outside premise does not predict crash.

HOL connection is core-only; source, Python scheduling, geometry and physical
completion have bounded empirical evidence, not a continuous refinement theorem.
Approach window is root's advice_trial.approach_trace() (original first two waypoints).
