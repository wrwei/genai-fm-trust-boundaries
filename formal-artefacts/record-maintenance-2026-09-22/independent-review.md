# Independent maintenance review — 2026-09-22

**Disposition: the reviewed trial, smoke, Forge, thinking and extended runner changes preserve their non-monetary execution controls. The overall cleanup remains pending because the pilot runner has not yet been migrated, and upstream manifest rebinding is still in progress.**

This review was read-only apart from this report. It inspected the named source files, exercised local temporary fixtures and decoded retained provider envelopes. It did not change a runner, JSON record or manifest, call a provider, read real credentials, or run physical mission simulations. It did not invoke the rebinding script's `maintain()` function.

## Pending item

`amr-deepseek-pilot/pilot.py` still uses the legacy accounting helper and record fields removed from the current smoke/trial interfaces. Its continuation path therefore remains incompatible with the maintained schema. The parent reports that automatic approval review rejected the attempted edit. This known pending item was confirmed by static inspection; no repair or alternate execution route was attempted here. A completed review of the other stages must not be represented as a completed pilot migration.

## Preserved execution controls

| Component | Request/repair bound | Requested output cap | Socket / parent timeout |
| --- | --- | ---: | --- |
| Trial recorder | Six samples, at most two repairs each and 18 recorded attempts | Positive integer from the frozen configuration | Offline recorder; transport owns deadlines |
| Smoke | One initial request; no repair or retry | 2,048 tokens | 60 / 90 seconds |
| Forge | Four condition-local chains, four repairs each, at most 16 calls | 2,048 tokens | Inherited 60 / 90 seconds |
| Thinking | Two condition-local chains, four repairs each, at most eight calls | 8,192 tokens | 150 / 180 seconds |
| Extended thinking | Two condition-local chains, four repairs each, at most eight calls | 65,536 tokens | 600 / 660 seconds |

The three diagnostic runners still enforce a 65,536-byte serialized request bound. Each retains fixed live paths, exclusive worker claims, exact prompt/feedback/payload checks, dependency hashes, single-use dispatch markers, the fixed HTTPS endpoint, no redirect/proxy route and no retry loop. Thinking and extended runners keep their own bounded transport; Forge uses the smoke single-POST helper. Existing run directories remain non-reusable. Acceptance/cycle decisions remain local to each chain, while diagnostic fatal statuses stop the whole batch.

The trial recorder continues to validate exact configuration and metadata shapes, integer token fields, request identity, timestamps, source bytes, prior-record links and frozen inputs. An output-cap violation remains independent of transport failure, prevents acceptance and stops further resource-limited recording. Removing accounting fields did not remove these checks.

## Token and schema compatibility

`smoke.usage_summary()` returns only `input_tokens`, `output_tokens`, `cache_hit_tokens` and `cache_miss_tokens`, or `None`. It rejects booleans, negative/non-integer counts, excess cache hits and a cache hit/miss partition that does not equal input tokens. Thinking and extended decoding additionally reject impossible or conflicting reasoning counts; the completion total, including reasoning, is checked against the output cap.

All three diagnostic `decode_response()` functions retain the four-item `(raw, envelope, usage_summary, fatal)` interface. Their outcome and trajectory writers, replay consumers and source-deployment gates use the maintained token-summary field consistently. The trial/smoke metadata exchange matches the recorder's current strict schema. A scoped search found no remaining calls to the removed helper or old record-field accesses in those reviewed current and snapshot Python files; the known pilot exception is outside this passing conclusion.

The smoke/trial layer continues its existing behavior of recording missing token counts explicitly rather than inventing values. This is distinct from the diagnostic runners' fatal `invalid_usage` gate. The helper validates component counts and cache partition; this review does not claim it independently verifies every optional provider aggregate field.

Fresh bounded checks performed here:

- Six existing offline unit tests passed in 2.450 seconds: pending-request idempotence/duplicate rejection; UTF-8 and output-limit handling; independent transport/output failure flags; numeric and identity validation; smoke single-call behavior; and smoke timeout behavior with missing usage.
- Direct decoder fixtures passed for all three diagnostic runners: four-item return shape, valid token counts, invalid usage, output overflow, truncation and oversized payload rejection. Thinking/extended fixtures also rejected impossible and conflicting reasoning counts.
- The 7 Forge, 2 thinking and 3 extended retained responses independently decoded to exactly the archived source bytes, token summaries and fatal statuses. These 12 checks did not alter any archive or recompute a physical result.

## Explicit manifest origins

The replacement [rebinding script](rebind_stages.py) uses explicit historical origins: `prior` points to the pilot run, `forge` to the Forge run, `thinking` to the thinking run, `extended` to the extended run, and `extended-closed-loop` to the extended physical archive. None of the existing copied inventories resolves to its containing later-stage run.

Stage order is Forge → thinking → extended → replication. Within each stage the script rebuilds copied inventories from those origins, refreshes root-relative or absolute frozen-input references, hashes attempt-local files relative to their actual attempt folder, then refreshes setup and run manifests. Physical pre-run bindings and physical manifests follow; derived audit identity references follow those manifests. Replication consequently sees the already-maintained extended physical archive. Copies include the earlier archive's own evidence manifest, matching the runners' inventory semantics.

Read-only probes confirmed the script's repository root, explicit path lookup and all declared inventory origins. Bare names such as `assessment.json.gz` are not resolved by the generic path helper; attempt hashes use their explicit local owner instead. This avoids the earlier mistake of resolving copied historical inventory names against the wrong stage.

At the time of review, all 11 copied inventories still differed from their actual origins while upstream maintenance was active. Their entry counts matched (271 pilot, 98 Forge, 34 thinking, 49 extended, 27 extended physical, including each origin's manifest). These are pending synchronization results, not a successful final hash audit. The script refreshes bindings; it does not itself establish that a scientific audit was rerun. Final `verify_inputs`, inventory equality and result-audit checks must follow the last upstream mutation.

## Reviewed file identities

These digests identify the maintained source inspected for this review; they are not original pre-execution hashes.

| File | SHA-256 |
| --- | --- |
| `formal-artefacts/amr-llm-trial/trial.py` | `741fab8db555c96b55772625c152379b04529b7d6f08519d28066d715bf76161` |
| `formal-artefacts/amr-deepseek-smoke/smoke.py` | `4cd7aeb114588967ba5168ef2201d9dfc549da98ebfddfc75f4770f37e5b09c7` |
| `formal-artefacts/amr-forge-diagnostic/runner.py` | `85d641a795de8b6bbbbfe82c6413cd61bc3cf72c5f1e6257b85a7f6ee8ef6f52` |
| `formal-artefacts/amr-thinking-diagnostic/runner.py` | `96e4ab31cf682b24e2ff5226d9b92936fc5463ecb9996e86b38206fe7f749f3d` |
| `formal-artefacts/amr-thinking-extended/runner.py` | `1eae182511db9c256a5567db8bca8f65200d5136303db809c2701c3182ba9277` |
| `.superpowers/record-cleanup-2026-09-22/rebind_stages.py` | `2a142502fbce9706236b2da1b0232334a01ee07cb8090e39e470df550123c971` |

## Final integration update — 2026-09-22

After the independent review above, the parent reported that core final verification passed, `rebind_stages.py` completed, and the retained replication analyzer plus the full generation audit freshly passed. Those checks were completed by the parent; their fresh outputs were saved only in the maintenance directory. This update preserves the earlier review-time observation that copied inventories were then awaiting synchronization.

The parent subsequently confirmed that upstream files were stable. This reviewer then refreshed the v2 final evidence manifest and independently re-read every one of its 205 entries: all paths resolved inside the repository, all byte counts matched and all SHA-256 values matched. Resolved paths were unique; the manifest did not include itself or the maintenance directory. `v2-verification.json` now records the completed check and the manifest digest. No physical mission simulation or provider request was performed.

The separately identified pilot-runner migration remains the pending item described above unless a later explicit migration record resolves it; successful archive verification does not imply that legacy entry point was updated.
