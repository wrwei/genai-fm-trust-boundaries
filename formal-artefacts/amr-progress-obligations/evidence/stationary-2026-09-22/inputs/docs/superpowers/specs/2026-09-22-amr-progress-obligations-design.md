# AMR transport progress obligations

The next missing claim is transport completion, beyond obtaining a reservation. Inspection of the accepted source and fixed plant reveals a material distinction: the parameter contract supplies an acceleration **upper** bound, whereas `RobotPlant` accelerates at an exact positive value. Upper bounds and speed limits alone do not imply motion. This extension establishes that boundary before proposing any complete closed-loop theorem.

## Deliverables and acceptance

1. A kernel-checked parametric travel-time inequality for the analytic rest-to-rest phase profile. For acceleration `a>0`, braking `b>0`, attained speed cap `v>0`, define `k=1/(2a)+1/(2b)`. A segment of length `L` has duration at most `L/v+k*v`, provided its peak/cruise phases obey the exact profile equations. A finite phase schedule drains in its summed duration. These are mathematical profile theorems, not a mechanized refinement of Python floating-point integration.
2. An explicit HOL countermodel and one bounded full-driver witness: zero acceleration and zero speed satisfy the stated upper bounds, yet an issued and applied Proceed can coexist with no displacement or completion. The modified plant must be labelled as a constructed plant mutation. It is outside the exact reference plant, not a newly discovered failure of its nominal execution. Keep source, adapter, timing, routes and geometry checks unchanged. Use a new function with copied globals to substitute only the plant class, without changing any imported module globals or retained source file.
3. An independent route-profile calculator tied to frozen routes and actual plant defaults; compare planned duration/terminal position with the real plant on a fixed finite matrix. Derive a conservative nominal two-mission budget from named local obligations. Inspect the four retained full executions against those obligations. Passing executions do not establish the obligations for all schedules or environments.
4. Record open obligations, obtain independent review, update the existing research entry points and unique integration candidate. Do not edit active TeX or historical evidence.

## Fixed protocol

- No new API calls. No model selection or industrial-case switch.
- Travel comparison: 36 straight profiles (`L in {0.01,1.625,4}`, `a in {0.25,0.5,1}`, `b in {0.4,0.8}`, `v in {0.5,1}`), plus the two existing staged routes at the reference defaults. Include triangular and cruising profiles. Independently integrate the emitted motion pieces and inspect terminal rest and position.
- Constructed witness: one 120-second simulation, no advice, no pedestrian, same runtime-binding driver code object, a plant subclass that refuses forward motion and otherwise inherits Brake. Expected: first grant A, applied Proceed, no completion, unchanged poses, zero speed, no safety-oracle failure. Save compressed trace and hashes exclusively; never overwrite retained runs.
- Budget diagnostic: sensor delivery/period 0.05 s, control period 0.05 s, command delivery 0.10 s, source halt timer 1.48125 s. Conservative grant budget 0.1 s, start budget 2 s, reference route budget 31 s, post-arrival reporting budget 2 s. Serialize two such tasks for 70.2 s. These budgets need implementation/environment discharge before serving as a universal transport guarantee.
- The stalled witness must fail an exact-reference-plant replay at its first missing physical movement. This distinguishes safety-envelope consistency from refinement to the progressing plant.

## Scope

The exact reference dynamics justify the phase equations. A deployment would instead need a positive lower progress guarantee (or a bounded travel service contract), reliable bounded observations/commands, continuous service supply, and a source/driver refinement for start, release and finish timing. Safety, admission, movement and completion remain separate. No arbitrary-obstacle progress, scheduler starvation tolerance, or universal hardware guarantee is claimed.
