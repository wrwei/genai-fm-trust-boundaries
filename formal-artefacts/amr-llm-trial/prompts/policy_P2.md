Policy presentation P2: exceptions to normal operation.

The ordinary step outcome is Proceed, entering Traversing. It is displaced by the following requirements. Their authority, from highest to lowest, is: invalid/blocked/task-inactive handling; released-goal handling; whole-body release; unfinished braking; reservation request; restart transition; ordinary motion.

The restart transition applies to a current Stopped mode and yields Resume, entering ResumePending. A missing reservation requires Request, entering Waiting, when neither OwnReservation nor Released is true; this overrides the restart transition. BrakeRequested without Halted must continue Brake, entering BrakeRequested; this overrides a missing-reservation request. However, OwnReservation together with BodyClearOfZ requires Release, entering Traversing, before unfinished braking is considered.

Higher than all these is arrival with AtGoal and Released both true: without Halted, return Brake and enter BrakeRequested; with Halted, return Finish and enter Done. Highest of all, whenever ObservationUsable is false, TaskActive is false, or PedestrianBlocked is true, return Brake. Under that highest-priority condition, enter Stopped if Halted is true and BrakeRequested otherwise. Thus even an arrived and halted robot must obey this highest-priority rule if its input is blocked or invalid.

These rules apply to every input combination and mode; if multiple descriptions apply, use the higher-authority requirement, without assuming that the combination cannot occur physically. Select follows the eligibility and totality rules in the interface. Return only the complete program JSON.
