# AMR stable closed-loop timing refinement

This extension closes the next bounded gap in the AMR evidence chain: under a stable usable environment, continued scheduler service, bounded sensor/command delivery, and the exact reference travel service, show how the accepted source and driver advance from reservation to applied motion, release, goal braking, and reported completion. It does not add controller behavior or claim progress under arbitrary blockage, interruption, hardware faults, or unfair scheduling.

## Chosen architecture

Use an integer 10 ms clock, matching the physical driver. A small Isabelle model proves scheduler-grid bounds and evaluates the already-bound selected source artifact on the milestone environments. It imports the existing concrete extraction artifact, protocol, runtime binding, and analytic profile results rather than restating their conclusions. Python independently evaluates the actual selected source and exhausts clock phase alignments; retained physical traces supply a separate implementation observation. The layers remain explicit because neither a timestamp theorem nor a trace audit alone proves Python/continuous refinement.

Rejected alternatives:

- Translating the entire Python interpreter, floating-point plant, queues and geometry into HOL would obscure the specific timing obligation and require a much larger refinement project.
- More successful traces alone would not establish phase-independent time bounds.

## Fixed contracts and theorem target

All theorem time values are natural-number plant ticks of 0.01 s. A continuous physical event is represented by the first integer plant tick at or after it. Bounds from that quantized event tick are therefore one tick tighter than generic bounds measured from the exact continuous instant.

- Control/sample period: 5 ticks.
- Sensor delivery: 5 ticks after sampling. A predicate recorded on an arbitrary integer event tick is visible to the source within 9 ticks; from an exact between-tick continuous event the generic bound is less than 10 ticks.
- Command delivery: 10 ticks after issue.
- Halt timer: the Python expression evaluates to 1.48125 s; the first qualifying 0.05 s control opportunity after a Brake application is 150 ticks later.
- Stable source path: observation usable, task active, pedestrian unblocked. Before clearance and goal, the owner remains on Proceed once started. Body clearance occurs before the goal on the fixed routes. Once clearance is observed, Release takes precedence and the previous Proceed command remains held. At a released goal the source requests Brake until the halt timer expires, then reports Finish.
- A grant reached while the selected robot is in `BrakeRequested` or `Waiting`, with Brake already applied no later than the grant, yields an applied Proceed within 163 ticks. This conservative bound covers both modes and arbitrary grid alignment. It is below the previously allocated 2 s.
- Body clearance recorded on an integer event tick is source-visible and released within 9 ticks (less than 10 ticks from an exact continuous crossing). Given another legal registered request, the existing selector plus Validate/Commit sequence grants it in the same driver control round; a conservative inter-task grant allowance is 10 ticks.
- The quantized arrival tick is bounded by the already stated 3,100-tick exact-reference travel service. From that tick, observation, Brake delivery, halt timing and Finish take at most 169 ticks (less than 170 ticks from an exact continuous arrival), below the previous 2 s.

The final theorem is conditional on the exact-reference travel service and the named stable scheduler/observation/command premises. With the first grant by tick 10 and a conservative 10-tick inter-task grant gap, two tasks finish by tick 6,884 = 68.84 s. The theorem may be rounded outward to 68.9 s in prose. It strengthens the prior 70.2 s diagnostic accounting, but is not a deadline for hardware or arbitrary environments.

## Concrete source and protocol bindings

The theory will import the selected source definition whose SHA-256 begins `9eaa530b5825`. Kernel-checked evaluation must establish both source and extracted-target results for the milestone environments:

- an unusable observation produces Brake;
- `BrakeRequested` before halt produces Brake;
- a halted owner before clearance produces Proceed;
- a `Waiting` robot that has received ownership produces Proceed;
- a traversing owner with body clear and not at goal produces Release;
- a released traversing robot before goal produces Proceed;
- a released goal before halt produces Brake;
- a released halted goal produces Finish.

The release/grant lemma must reuse the existing `AMR_Protocol` definitions: after a valid Release, the remaining request is legal; selected Validate followed by Commit produces its Grant. This is a discrete authorization statement, not a physical clearance proof.

## Executable checks

`timing_model.py` implements only the published integer formulas and validates finite inputs. `source_milestones.py` loads the exact accepted source bytes and independently checks the milestone action/mode results. `verify.py` must:

1. exhaust event phases modulo the five-tick clock and relevant grant/brake-age combinations;
2. check the literal 9-, 163-, and 169-tick bounds and the 6,884-tick composition;
3. check all source milestone cases against the actual interpreter;
4. read the four retained traces and confirm their milestone events lie within these stronger local bounds;
5. verify previous evidence manifests and proof-input hashes without rerunning physical experiments.

Negative tests must catch a ceiling that skips an on-grid event, late sensor/command delivery, a start formula that ignores the halt timer, a Finish formula that omits command delivery, unknown source modes/facts, and a composed bound missing the second task.

## Evidence boundaries

- The actual selected source bytes and concrete HOL rule table are bound; general JSON/Python frontend correctness remains outside scope.
- The integer model matches declared driver clocks and is checked against four retained executions. A whole-program Python refinement theorem remains open.
- The analytic profile theorem and 38 comparisons justify the exact reference service used here. Hardware response and general continuous refinement remain open.
- The result assumes stable usable observations, no pedestrian blockage, continued control and service opportunities, no command rejection, no permanent fault, and the fixed routes. It does not cover temporary-pedestrian recovery, arbitrary interruption, concurrent callbacks, cancellation, or a different map.
- No API calls, new model samples, active TeX edits, commits, pushes, or reruns of previous physical batches.
