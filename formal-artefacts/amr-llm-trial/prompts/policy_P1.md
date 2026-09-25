Policy presentation P1: operational priority.

For each step, apply the first applicable requirement below. Later requirements never override an earlier requirement, irrespective of current mode.

1. An unusable observation, an inactive task, or a blocked pedestrian crossing requires Brake. If Halted is true, the next mode must be Stopped; otherwise it must be BrakeRequested.
2. With those blocking conditions absent, a robot that is AtGoal and has Released must establish stop confirmation before reporting completion: if not Halted, return Brake with next mode BrakeRequested; if Halted, return Finish with next mode Done.
3. If neither of the previous requirements applies and OwnReservation and BodyClearOfZ are true, return Release with next mode Traversing. This takes priority even if the current mode is BrakeRequested.
4. Otherwise, a robot in BrakeRequested with Halted false must keep Brake and next mode BrakeRequested.
5. Otherwise, if both OwnReservation and Released are false, return Request with next mode Waiting.
6. Otherwise, if the current mode is Stopped, return Resume with next mode ResumePending. Resume is a protocol transition; it is not immediate permission to drive.
7. In every remaining case return Proceed with next mode Traversing.

Use the selection eligibility and totality requirements stated in the interface. Produce only the complete program JSON.
