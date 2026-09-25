# Independent live-result audit

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

Date: 2026-09-17. Read-only audit of the completed invocation in `run/`. No credentials, network calls, reasoning-text output, or changes to the run or historical artifacts were used. This report is outside the run directory.

**Disposition: recorded evidence is consistent; the batch correctly stopped after two calls because the thinking response was truncated. No accepted program or eligible physical source exists.** The comparison did not complete both repair trajectories.

## Observed results

| Attempt | Condition | Repair | Source bytes | Parse | Inputs checked | Source/model violations | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 001 | N12-F | 1 | 990 | pass | 1,824 | 784 / 784 | rejected by acceptance obligations; no fatal transport status |
| 002 | T12-F | 1 | 0 | fail | 0 | not evaluated | truncated, `finish_reason=length` |

N12-F repaired 55 of the initial 839 failing inputs and introduced no new failing inputs, leaving 784 failures. Source/model correspondence mismatches were zero. Its repair trajectory remains unfinished (`stop=null`) because the subsequent fatal T response stopped the entire batch; it did not reach a cycle, acceptance, or repair-limit stop.

T12-F returned an empty string in `content`. The provider reported 8,192 completion tokens and 8,192 reasoning tokens, with reasoning content present. These counts are mutually consistent and exhaust the requested total output cap. Only metadata was inspected for this report; reasoning text was not printed or fed into acceptance. The empty source fails parsing with `invalid program JSON`. Its stored zero violation counters mean **no inputs were evaluated**, not zero violations over the 1,824-input domain. No repaired/regressed-input comparison is available for that response.

The observed client durations were 2.295584 seconds for N and 40.486324 seconds for T, both below the declared 180-second parent deadline. Both transports recorded HTTP 200 without credential echo or response-body overflow.

## Integrity and replay

- All 33 entries in the run evidence manifest matched the exact files. Each attempt's complete pre-outcome file inventory matched its recorded hashes. The 63 frozen inputs, setup hashes, historical pilot and Forge inventories, and preparation hashes verified.
- The original audit checked the runtime runner against its pre-dispatch reviewed hash. Protocol identity, live mode, condition order, model configurations, caps, and timeouts match the declared protocol.
- The two recorded attempts are exactly N12-F repair 1 followed by T12-F repair 1, with one worker claim and one dispatch marker each. Both prompt byte strings match the frozen prior D12-F first prompt. Feedback and complete serialized request bodies reproduce exactly from the initial states.
- N disables thinking with temperature 0; T enables thinking with high reasoning effort and omits temperature. Both requests cap output at 8,192. No third attempt, retry, or resumed call is recorded.
- Each `response.bin` equals the exact UTF-8 encoding of the provider `content` field. Provider model, fingerprint, and request ID match the archived outcomes.
- Fresh full assessments of both exact source strings match every field of the archived compressed assessments, including their full case records. Reconstructing condition states from these fresh assessments matches `result.json` exactly.
- The batch stop is `truncated`, and `selected_for_exploratory_physics` is null. The actual physical deployment gate rejects this run because it lacks `protocol_complete`; no `closed-loop/` output directory exists.
- The run manifest was rechecked after the audit and remained unchanged.

## Usage audit

The retained provider envelopes report:

| Attempt | Hit / miss input tokens | Total completion tokens |
| --- | --- | ---: |
| 001 N12-F repair 1 | 2,560 / 240 | 270 |
| 002 T12-F repair 1 | 0 / 2,826 | 8,192 |

The totals are 5,626 input tokens and 8,462 completion tokens.

The thinking response reports 8,192 completion tokens, all identified as reasoning tokens. This exhausts the declared output limit and agrees with the empty final content and truncation status.

## Evidence identities

| Artifact | SHA-256 |
| --- | --- |
| `run/result.json` | `f5b5547c57e408e8e2d037a2f9691cf8f26281d53b4c69f73a1e7ea52b34f43d` |
| `run/evidence-sha256.json` | `b465bfb83419a0c6d0d8417c2c569bf70b857cb66e2fdeee5315f892b05682cb` |
| `run/attempts/001/response.bin` | `c4dcfc68cf4b2ddd636725bd15a2ddca6174a02f37692c6f40b127aab5bc8124` |
| `run/attempts/002/response.bin` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

These results support only the recorded outcome for this failure seed and the declared configurations/output cap. They do not establish general thinking-mode effectiveness or a completed four-repair comparison, and do not authorize additional generation or physical episodes.
