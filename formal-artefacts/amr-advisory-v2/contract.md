# AMR advisory contract v2 — frozen scenario profile

Frozen before new assessments or API requests, 21 September 2026.

Two persistent transport tasks are registered once: A at rank 0, B at rank 1. No dynamic arrival or re-registration is in this experiment. Thus FIFO when both remain eligible is A, and when only B remains it is B. This is the **fixed-registration profile**, not an implementation of arbitrary-arrival FIFO with the old five Boolean selection inputs.

The existing restricted syntax and 12-rule parser profile are unchanged. Source and target semantics are independently executed over all 32 selection valuations and 1,792 step valuations. v1.1 step obligations remain unchanged. Source bytes and historical accepted status remain unchanged.

v2 selection:

1. If owner is occupied or neither request is currently eligible: Defer.
2. If exactly one request is eligible: select that robot, regardless of advice.
3. If both are eligible and exactly one Prefer flag is true: select that robot.
4. Otherwise (missing or conflicting preference flags): select A by frozen FIFO.

The trusted adapter supplies OwnerFree, RequestA, RequestB, PreferA, PreferB; it must not preselect the final robot or hide candidate functional failures. Request eligibility includes current permission/freshness and task validity. The original source returns SelectA/SelectB/Defer. A strict one-slot mailbox never supplies two true flags, but the full Boolean check includes that conflict defensively.

Runtime mailbox: one trusted request identifier and task-context identifier; first exactly parsed JSON {"prefer":"A"} or {"prefer":"B"} response with matching binding is retained. Extra/duplicate fields, unknown choices, duplicate JSON keys, wrong binding and malformed responses are rejected. Duplicate or later responses cannot overwrite the first slot. Selection latches immediately, even if empty; new replies do not reset a validated proposal. Relevant task changes invalidate the mailbox. FIFO fallback is performed by the source from the supplied no-advice facts, not by replacing its output.

Safety reference permits either eligible robot. Current validation/commit and command issue/application are distinct steps. A synchronous local event scheduler provides current state to Apply; no distributed instantaneous-revocation claim is made. Same-permission observations do not reset validation. Physical Clear is separately checked against independent complete-body geometry.

Mechanism faults: E1 deliberately changes only a both-request/unambiguous-B model branch while retaining the same source; E2 uses center-only Clear; E3a removes current Commit checking without changing validation; E3b removes current Apply checking without changing Commit; E4 waits for missing advice before source selection. Each is explicitly constructed, not counted as a model-generation error.

Deployment rule: assess all six historical fresh-context responses and all distinct raw identities; select the first v2-accepted distinct source in historical sample order. If none pass, stop source deployment and record that outcome before any separate bounded generation proposal. This rule is frozen before new assessments.

Primary progress target: once an effective request and free owner/current permission hold, they remain usable until Grant, and trusted service continues; then authorization must occur without assuming any advice reply. Physical mission completion is empirical in this stage, not a theorem.
