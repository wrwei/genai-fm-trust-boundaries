# Offline diagnostic implementation verification — 2026-09-17

Implemented only the new diagnostic module, isolated profile copies, diagnostic tests, and these verification records. The frozen `amr-supervisor` and `amr-llm-trial` sources and evidence were not modified. No network request, credential access, model call, or commit was performed for this subtask.

## Interfaces

- `assess(text, limit)` preserves every original `assess_source` report field. Added fields are `profile_id`, `profile_config`, `rule_counts`, `full_cases`, `failure_input_ids`, `source_failure_input_ids`, `model_failure_input_ids`, and `correspondence_failure_input_ids`.
- Each parseable report has all 1,824 cases in frozen enumeration order. Each case has a stable `input_id`, function, mode, facts and input, current zero-based rule location/condition (or `no_match` status), actual response, allowed output set, source/model violations and outputs, obligation ID, and correspondence category.
- `original_feedback(report)` reproduces the frozen `trial._feedback` shape, counts, two-witness caps and rejection category. The frozen semantic category is `semantic_rejection`.
- `enhanced_feedback(report, history)` returns at most eight grouped current examples and four historical examples. Groups use function, obligation, allowed outputs, and Halted. Historical order is regressed, repaired, unresolved, then first seen. Current example IDs are excluded from historical examples.
- `update_history(history, feedback)` immutably incorporates both example sets and retains first-seen input order.
- `refresh_history(history, report)` recomputes **every previously sent input**, including those omitted by the feedback cap. Integrate before advancing: `refresh_history(update_history(history, feedback_for_old_report), old_report)`. Compare this history with the next candidate. Parse-rejected reports preserve the last evaluable history because no complete-domain cases exist for them.
- `program_key(text, limit)` hashes the parsed canonical AST with rule order retained. Parse failures use raw-byte SHA-256. It also accepts raw bytes at the transport boundary, preserving invalid UTF-8 without replacement.
- `_profile(limit)` returns `(language, model, assurance)` for an isolated package namespace. It does not replace the frozen top-level modules or mutate another profile.

## Profile provenance

`profiles/snapshot.json` records the original and copied source hashes and the exact transformation list. For both profiles, only imports in model/assurance become relative to their own package. The 12-rule profile additionally changes the rule-list bound and its error message from 8 to 12. Reversing those listed substitutions produces exact original bytes for all six copied modules. All recorded source and profile SHA-256 values were checked.

The maximum source size, expression length, AST nodes, expression depth, total branch cap, action/mode whitelist, first-match semantics, model execution, v1.1 obligation partition, and input enumeration remain unchanged.

## Tests and observed results

Runtime: `C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` with `-B`.

Command: `python -B -m unittest discover -s formal-artefacts/amr-forge-diagnostic/tests -p test_diagnostics.py -v`.

1. `diagnostics-red.log`: 16 tests failed with the expected missing diagnostic API assertion, before implementation.
2. `diagnostics-green.log`: all 16 original tests passed.
3. `diagnostics-history-red.log`: 17 tests ran; only the new complete-history-refresh test failed because the helper did not yet exist.
4. `diagnostics-history-green.log`: all 17 tests passed in 12.072 seconds after adding complete-pool refresh.

Coverage includes positive controls, per-function 9/12/13 boundaries, profile isolation, scalar/schema/action/expression rejection, unchanged safety/progress rejection, exact frozen report and original feedback comparison, two eligible select outputs, uncovered source/model classification, grouped feedback limits/order, halted-dependent obligation output, current source locations, historical priorities/caps/exclusions, immutable history updates, omitted-example repair then regression, whitespace-stable AST cycle keys, rule-order sensitivity, and parse-failure handling.

Additional direct verification used the existing `choose_b_when_both` extraction fault: both distinct selections remain permitted, while correspondence is correctly classified as `defined_outputs_differ`. Invalid UTF-8 byte strings produce distinct raw cycle keys; valid UTF-8 bytes and text produce the same AST key.

The fixed P2-R1 starting candidate produces 839 source failures, 839 model failures, and 55 source/model correspondence mismatches due to uncovered inputs. All 1,824 cases are retained. Its selected feedback contains three current groups: uncovered proceed with Halted false, uncovered proceed with Halted true, and premature Stopped with Halted false. The last group locates `$.step[0]` and requires `Brake/BrakeRequested` for that input.
