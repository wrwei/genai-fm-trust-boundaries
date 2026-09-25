Policy presentation P3: dispatcher's decision procedure.

At every update the dispatcher first asks whether the observation can be used, the task remains active, and the crossing is free of a pedestrian block. If any of these three checks fails, its instruction is Brake. Stop confirmation then decides the next mode: Halted means Stopped, and no Halted means BrakeRequested. No other instruction takes precedence over this instruction.

Only when all three checks succeed does the dispatcher consider a released robot at its goal. AtGoal together with Released requires Brake/BrakeRequested until Halted, and then Finish/Done. For inputs not handled so far, a robot that owns the reservation and has its entire body clear of the zone must report Release/Traversing. Clear body and released reservation are separate facts.

For the remaining inputs, first retain Brake/BrakeRequested if the current mode is BrakeRequested and stop confirmation is still absent. If this does not apply, require Request/Waiting when ownership and released status are both absent. If that also does not apply, a Stopped robot takes Resume/ResumePending. Every input left over takes Proceed/Traversing.

Each slash above separates the returned action from the exact next mode. The order of these checks is normative, including for inconsistent-looking Boolean facts and current Done mode. Reservation selection has precisely the constraints given in the interface; no extra preference-following requirement is added. Return just the complete program JSON.
