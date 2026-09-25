# Independent advice-trial pre-dispatch review

**Spec-compliance verdict: PASS.** No load-bearing defect remains in the reviewed pre-dispatch harness. No real request was prepared or issued during this review.

The harness declares exactly six samples and independently regenerates their exact payloads in fixed order. Full payload equality fixes the three frozen wordings, one user message, `deepseek-flash`, 128-token output cap, temperature zero, disabled thinking, JSON-object response format, and no streaming.

The source is now independently bound to the first accepted historical P3-R1 raw identity, `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`, during both preparation and dispatch validation. The recorded source summary and exact raw copy are frozen dependencies. A behavioral regression confirms that a semantically identical, v2-accepted program with different bytes is rejected. The dependency inventory also includes the reused transport's imported `trial.py`, original profile code, source checker, protocol, mailbox, corridor code, parameter evidence, selected summary, and selected bytes.

The advisory harness owns a restricted worker entry point: it admits only one of the six prepared attempt directories, revalidates the whole batch, and then invokes the reused single-POST network function. An offline child test with an intentionally invalid short dummy credential reaches credential-format validation, records only the error type, creates no dispatch marker, and cannot reach the network. This demonstrates that the prior smoke-worker path incompatibility is fixed without reading a real credential.

The endpoint is fixed as `https://api.deepseek.com/chat/completions`; redirects and proxies are disabled. Credentials remain confined to the short-lived child and Authorization header, retained bodies are credential-redacted, exception text and child output are suppressed, and only the credential-file path crosses the parent command line. No credential logging path was found.

Exclusive batch, per-attempt intent, and worker dispatch markers conservatively enforce at most one POST after success, failure, timeout, or ambiguity. The batch maximum is six, retries are zero, the child is bounded to 90 seconds. Missing trustworthy usage is reported explicitly. Preparation refuses an existing output directory; execution refuses an existing batch marker; each attempt refuses an existing dispatch marker.

The deterministic approach is paced against monotonic wall time and never waits for advice. Selection latches at the fixed approach cutoff. Only a strictly parsed response whose recorded parsed-arrival elapsed time is within that cutoff is offered to the mailbox; late completion is recorded after the decision and cannot reset it. Missing, late, malformed, or rejected advice reaches A through the frozen source's A-before-B FIFO behavior, while valid early B advice reaches B. Provider output never grants ownership or bypasses source evaluation.

All eight offline advice-trial tests pass. They cover payload bounds, early/late/malformed behavior, duplicate attempt refusal, six-sample preparation, actual child entry through credential validation without network, coordinated payload/manifest tampering, and byte-exact source substitution rejection.

**Code-quality verdict: PASS.** The implementation separates preparation, validation, dispatch claiming, credential-bearing transport, mailbox parsing, and source-driven authorization. Remaining scope limits are explicit: this review does not defend against a local attacker rewriting reviewed code and every manifest together, does not validate provider availability, and does not claim physical mission completion or response-quality rates.

**Dispatch blockers: none within the declared threat model and bounded six-call scope.**
