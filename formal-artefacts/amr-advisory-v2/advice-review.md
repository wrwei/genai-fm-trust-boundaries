# Independent advice-trial postflight review

**Specification verdict: PASS. Evidence verdict: PASS. Code-quality verdict: PASS.** The offline audit found no load-bearing defect or inconsistency in the completed six-call record.

The batch contains exactly the six frozen samples in order, two repetitions of each of the three wordings. Every `http-request.json` equals the independently regenerated payload and matches its frozen SHA-256: one user message, `deepseek-flash`, 128 maximum output tokens, temperature zero, disabled thinking, JSON-object response format, and no streaming. The recorded implementation, profile, corridor, parameter, source-summary, and exact selected-source hashes match the frozen protocol. The source identity is the preselected historical P3-R1 bytes, `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`.

There are six per-attempt intent markers and six worker dispatch markers. Each records at most one POST and zero retries to the fixed endpoint. All six transports record HTTP 200, no body-limit excess, and no credential echo. The six provider request IDs are present and distinct. No credential material appears in the audited evidence.

All six raw HTTP bodies contain one normally stopped completion. In every case the exact response bytes decode to `{"prefer": "B"}` and match both the body content and retained outcome. Strict mailbox parsing independently accepts each response as B. Each decision records both requests eligible, only `PreferB` true, and the frozen raw source returning `SelectB`; each resulting authorization event is `Grant(B)` with owner B. This is source-produced selection, not an adapter replacement of the source result.

All responses were available well before the fixed 3.63 s latch cutoff. Parsed-arrival elapsed time ranged from 0.969 s to 1.297 s, leaving at least 2.333 s of margin. Decision records occurred at 3.734–3.750 s wall elapsed. Thus the logged combined post-cutoff source reassessment, selection, and decision-recording interval was 0.104–0.120 s. Maximum pacing lag was 0.015 s. The logs do not instrument those computation stages separately, so finer attribution is not claimed.

Reported usage is internally consistent: 644 input tokens and 42 output tokens total.

The evidence supports a precise live claim: six real provider replies arrived during a wall-clock-paced, deterministic approach to halted staging; all passed the strict mailbox before the cutoff; and the frozen source used the advice to authorize B. It does not demonstrate a complete real-time physical controller, closed-loop corridor traversal, continuous safety, task completion, throughput, or a population response-quality rate.

The reproducible audit is `advice-audit.py`; its machine-readable result is `evidence/advice-audit.json`. It revalidates the frozen batch and approach, request and response bytes, dispatch bounds, raw bodies, usage/timing order, strict mailbox result, frozen source facts/action, grants, summary equality, and aggregate totals.
