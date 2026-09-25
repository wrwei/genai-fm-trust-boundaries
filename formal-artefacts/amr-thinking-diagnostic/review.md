# Independent pre-dispatch review

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

Date: 2026-09-17. Scope: the approved two-configuration protocol, bounded runner, and conditional physical adapter. This review used local files and offline fixtures only; it did not read credentials, contact a provider, or modify historical artifacts. The live `run/` directory did not exist when the checks below completed.

**Disposition: no outstanding blocker for the declared bounded diagnostic.** This is a code/protocol review, not a prediction of model success.

## Protocol and implementation checks

- Both conditions use `deepseek-flash`, a maximum of 8,192 completion tokens, the same P2-R1 failure, the same 12-rule profile, deterministic enhanced feedback, and all 1,824 acceptance inputs. The first prompt in each condition is byte-identical to the prior D12-F first prompt. The initial program parses and fails 839 inputs.
- N12-F explicitly disables thinking and sets temperature 0. T12-F explicitly enables thinking, requests high reasoning effort, and omits temperature. The protocol appropriately interprets this as a comparison of solving configurations from one observed failure, without claiming identical sampling distributions or an independent success rate.
- Only the UTF-8 encoding of the provider's `content` field becomes source. Reasoning content remains in the raw provider envelope and is neither concatenated into source nor fed into subsequent prompts. The runner records counts and evidence of reasoning separately. Absent reasoning details are allowed and marked unconfirmed.
- The output limit applies to total `completion_tokens`, including reasoning. An explicitly impossible or inconsistent reasoning count invalidates usage and stops the batch.
- Scheduling is N then T per repair, skips terminal conditions, and is bounded by four repairs each and eight calls total. Acceptance precedes cycle stopping. A pre-existing run cannot be reused.
- The actual POST function has a fixed HTTPS endpoint, no proxy, redirect refusal, one exclusive dispatch marker, no retry loop, a 150-second network timeout, and a 180-second parent-process deadline. Credential echoes are redacted and exception text is not persisted. These boundaries were exercised with a fake credential value and mocked transport, without a real key or network connection.
- Physics requires a completed live result with both conditions terminal. Selection is the first successful condition in the declared N12-F/T12-F order and its first accepted repair. The adapter verifies the evidence manifest, ledger-derived states, exact selected response SHA-256, provider envelope, and a fresh full acceptance assessment. Offline fixtures and partial/fatal batches cannot deploy.
- The physical adapter reuses the existing checker-import adaptation, physical equations, parameter contract, scenarios, and independent collision oracle. It preserves the selected source bytes, records source identity during episodes, and snapshots/checks physical inputs separately, including the prior helper runner. It runs the declared five scenarios paired with the handwritten calibration at dt 0.01 and horizon 120 seconds.

## Review findings resolved before dispatch

1. Oversized follow-up payloads now produce a final `payload_limit_stop` result and evidence manifest, without an additional POST.
2. The physical input snapshot now includes the prior runner helper used by the unchanged physics adapter.
3. Added offline checks cover the actual POST boundary, malformed/falsey content, deeply nested JSON, and credential-echo/error-message handling.

## Verification evidence

Independent command, run from the repository root:

```text
python -B -m unittest discover -s formal-artefacts/amr-thinking-diagnostic/tests -v
Ran 27 tests in 44.878s
OK
```

This includes 22 runner tests and 5 physical deployment-gate tests. Positive source fixtures are confined to temporary offline runs; they cannot become live evidence. The historical pilot and Forge evidence manifests matched their exact file inventories, and all 47 preparation input hashes verified.

Reviewed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `runner.py` | `3518d247c3a61399f8aced4fd9dc91068bda04f89bb0c6fe77490c4ce6cb9c55` |
| `simulate.py` | `af92b0435fd05a5523aa9ab79d180ae7002828207cf3d6902af67becc7744f97` |
| `tests/test_runner.py` | `7c1100e6438d0b13b29d2f8ea33b95c17ed3772cff516d20a9e23cf20f4e3a93` |
| `tests/test_simulate.py` | `b2d86bd02b0bd82d0dd65bde7d0a2f2b9b53a4230ada9ab27bc675749048c180` |
| `research_amr_thinking_protocol_2026-09-17.md` | `f6a67232e2a3cd873a9e2e4db743090537fcf1ca5b4adbfa6ad7d801913d7b2d` |

No live result is asserted by this pre-dispatch review.
