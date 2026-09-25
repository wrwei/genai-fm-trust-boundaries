# Runner implementation verification

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-17, offline only. No credential file was read, no provider request was made, and the fixed live `run/` directory was not created by this implementation task.

`python -B -m unittest discover -s formal-artefacts/amr-thinking-diagnostic/tests -p test_runner.py -v`

Result: **22 tests passed**, 30.640 seconds. Full output is in `runner-tests.txt`; the initial missing-implementation failures are in `runner-tests-red.txt`.

Actual transport boundary tests replace the key reader and urllib opener with local fixtures.

The module is loaded as `thinking_runner`. `CONFIGS` and `protocol.model_configs` map `N12-F` and `T12-F` to exact request parameters excluding `messages`. `payload_for(prompt, cid)` builds a fresh payload; it never mutates prior modules. Familiar initialization, replay, decode, state/feedback, hashing, inventory and result interfaces are retained. `smoke` and `SMOKE` are aliases for the uniquely loaded utility module; their old model configuration is not used for new requests.

Provider `reasoning_content` is archived only in `http-body.bin`. Outcome `thinking` metadata contains mode/evidence flags and byte/token counts; source assessment and subsequent prompts receive only raw `content`. Missing/empty reasoning evidence is `unconfirmed`, not a rejection.

Runtime freeze includes the new runner, README and protocol, the diagnostics/profiles and runtime dependencies, and prior pilot/forge run inventories. New tests, review notes and the separately frozen physics adapter are outside the request-stage dependency freeze. Parent review was required before the original live dispatch.
