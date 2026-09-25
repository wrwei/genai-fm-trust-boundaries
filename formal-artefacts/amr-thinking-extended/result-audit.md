# Independent extended-stage result audit

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-17. The generation audit used only local archived evidence and fresh finite-domain assessments. No credentials, provider calls, reasoning-text output, or edits to run/dependency files were used. This report remains outside both evidence directories.

**Generation disposition: verified.** The batch completed normally after three calls. T64-F repair 1 is accepted over all 1,824 inputs; N64-F stops on a repeated rejected program at repair 2. The protocol-selected source is exactly the T64-F response in `run/attempts/002/response.bin`.

## Generation outcomes

| Attempt | Condition | Repair | Checked inputs | Source/model violations | Correspondence mismatches | Result |
| --- | --- | --- | ---: | --- | ---: | --- |
| 001 | N64-F | 1 | 1,824 | 784 / 784 | 0 | rejected; 55 initial failures repaired, no new failures |
| 002 | T64-F | 1 | 1,824 | 0 / 0 | 0 | accepted; all 839 initial failures repaired |
| 003 | N64-F | 2 | 1,824 | 784 / 784 | 0 | exact repeat of attempt 001; cycle stop |

All three responses parse and have provider `finish_reason=stop`, with no fatal status. The accepted source is 937 UTF-8 bytes and contains 3 selection rules plus 9 step rules, within the unchanged twelve-rule-per-function profile. Its SHA-256 is:

```text
ccaf1b8c973b72cd27bccabe008fb8d6ae5c2f8b186bacad359facc3fec3df24
```

The N responses are both 990 bytes and have the identical SHA-256 `c4dcfc68cf4b2ddd636725bd15a2ddca6174a02f37692c6f40b127aab5bc8124`; canonical program identity also repeats. Both conditions are terminal (`cycle`, `accepted`), so `protocol_complete` and selection of T64-F repair 1 follow the declared order rather than a post-hoc physical outcome choice.

The T call reports 9,291 total completion tokens, including 9,032 reasoning tokens, and completed in 42.690176 seconds. Its total output usage exceeds the earlier stage's 8,192-token cap while remaining far below the new 65,536 cap. Only reasoning existence/count metadata is summarized here. The N calls report 270 completion tokens each, with observed durations of 2.277625 and 2.595310 seconds. All calls were within the declared deadline. All three provider records identify `deepseek-flash` and fingerprint `aeb56401ca74e127821c4f9126dcb669`.

## Evidence and independent replay

- All 48 files listed by the run manifest matched their hashes. Each attempt's complete pre-outcome inventory matched its recorded hashes, and all 66 frozen inputs, setup hashes, inherited inventories and preparation checks verified.
- The original generation audit matched the runner hash to the preflight-reviewed implementation.
- Reconstructed scheduling is exactly N repair 1, T repair 1, N repair 2. Prompts, deterministic feedback, complete request-body bytes and dispatch records reproduce from the corresponding condition states. The first requests also match the saved exact egress previews and the original D12-F first prompt bytes.
- Each attempt has one worker claim and one dispatch marker, with the fixed endpoint and zero retries. All transports record HTTP 200 without credential echo or response overflow. There are exactly three attempt folders and dispatches, and no further scheduled slot after the terminal states.
- Each saved source byte string exactly equals the UTF-8 encoding of the provider's `content`. Model identity, fingerprint and request ID match the archived outcomes. Reasoning content is not used as source or included in reconstructed prompts.
- Fresh assessments of all three exact sources match every archived assessment field, including all full input cases. Fresh source hashes match the archived response identities. Reconstructed trajectories, failure-set changes, checkpoints, terminal states and selected-source record match `result.json`.

## Usage audit

| Attempt | Hit / miss input tokens | Total completion tokens |
| --- | --- | ---: |
| 001 N64-F repair 1 | 2,560 / 240 | 270 |
| 002 T64-F repair 1 | 2,688 / 138 | 9,291 |
| 003 N64-F repair 2 | 2,688 / 201 | 270 |

The totals are 8,515 input tokens and 9,831 completion tokens.

## Generation evidence identities

| Artifact | SHA-256 |
| --- | --- |
| `run/result.json` | `2e208888c013e401abbc1c5965f9c7c44ef8cda3d137b58bf66aedde7373a25e` |
| `run/evidence-sha256.json` | `c6aa2217f2fecc939c83e2ea246b7e1eb47dc2819b746705ad27e0811448e861` |

## Physical audit

**Physical disposition: all ten archived episodes and their reported outcomes verified.** This audit consumed the finalized traces; it did not rerun the plant/controller simulation or request a model response.

The 26-file physical evidence manifest matches exact bytes. All 119 pre-run input hashes still match, including generation evidence, the selected source, checker/physics dependencies and adapter files. The saved selected source is byte-identical to provider `content` in attempt 002 and carries the accepted hash above. The saved adapter and adapted closed-loop source match their frozen counterparts; the only closed-loop adaptation remains the two checker imports made package-relative. The actual live deployment gate passes this completed generation evidence. Every source episode and every source-labelled trace event use the selected hash; handwritten episodes retain their separate calibration identity.

From the traces, the audit re-evaluated **25,272 step decisions and 14,716 selection decisions** using the declared controller for each arm. Recorded raw and applied actions/modes agree with fresh evaluation, and all runtime obligation checks pass, so the reported zero runtime rejections do not conceal a fallback that replaced generated actions. Grant order, reservation ownership, release events, physical completion, terminal states and comparisons reproduce from the event records.

The audit reconstructed continuous motion pieces directly from the trace, checked trajectory continuity and observation snapshots, and re-scored **711,206 geometric pair intervals** with the frozen independent oracle. Collision pairs, collision witnesses, unresolved pairs, interval counts and minimum distance bounds match every episode summary. At release events, physical footprint geometry confirms that the body has cleared the reserved zone. At completion events and final scoring, actual goal positions and standstill agree with the reported completions. The minimum certified distance lower bound is **0.26068542394925565 m** in each episode.

| Scenario | Source completion times (s) | End time (s) | Source grant order | Source release times (s) | Outcome |
| --- | --- | ---: | --- | --- | --- |
| normal_A | A 32.95; B 58.95 | 58.95 | A, B | A 27.50; B 53.50 | both complete |
| normal_B | A 32.95; B 58.95 | 58.95 | A, B | A 27.50; B 53.50 | both complete |
| temporary | A 39.90; B 65.90 | 65.90 | A, B | A 34.45; B 60.45 | both complete after resume |
| blackout | A 37.85; B 63.85 | 63.85 | A, B | A 32.40; B 58.40 | both complete after observation recovery |
| permanent | neither | 120.00 | A | none | horizon reached; both stopped |

All ten episodes have no collisions, unresolved geometric checks, early releases, runtime rejections or completion mismatches. Both robots have zero final speed in every episode. The four clearable scenarios are safe-and-complete according to the frozen score; permanent blocking is not complete and its `safe_and_complete` value is false. In that scenario A retains the reservation, neither robot releases or finishes, and both final modes are `Stopped`.

The recorded source action sequence for A confirms the standstill distinction:

- Temporary blocking: at 10.05 seconds, `Brake / BrakeRequested`; at 11.65, `Brake / Stopped`; at 17.05, `Resume / ResumePending` while the physical intent is still Brake; at 17.10, Proceed.
- Blackout: 100 A observation deliveries are dropped over 10–15 seconds. A brakes at 10.05, becomes Stopped at 11.65, issues Resume at 15.00 with Brake still applied, and issues Proceed at 15.05.
- Permanent blocking: A brakes at 10.05 and becomes Stopped at 11.65, with no later Resume. The reported Halted facts in these three source traces were checked against reconstructed physical linear and angular standstill.

The handwritten calibration has the same scored outcomes and final times in all five scenarios. In normal_B it grants B then A, whereas the source grants A then B and swaps which robot finishes first. The frozen prompt explicitly makes PreferA/PreferB advisory and permits either eligible robot; fresh selection checks verify that this difference is legal. It is not evidence that the generated controller implements preference ordering.

Material interpretation limits remain: these are ten related deterministic episodes in the fixed analytic world, not independent task samples or a hardware safety theorem. The pedestrian-brake diagnostic marks the straight-approach stopping-distance condition **inapplicable** at its trigger, because the observed heading/pose is outside that condition's declared domain. Empty assumption-violation lists therefore do not establish that straight-approach premise there; safety evidence for these traces comes from the geometric replay under the frozen dynamics. Permanent blocking demonstrates safe waiting within the horizon, not eventual task completion.

| Physical artifact | SHA-256 |
| --- | --- |
| `closed-loop/summary.json` | `7697e632ced3a26a99ef9bc4a269816608729313a224c7a24268083f65c7193a` |
| `closed-loop/evidence-sha256.json` | `ae28f3d239808fe07c6887b6dd8bf2acc359a3dd8a5858ffea817fce2767519a` |

The original audit rechecked generation evidence, physical input hashes and the physical manifest after replay. Raw provider replies, generated-controller bytes and physical trajectories remain retained. Physical evaluation records zero additional model calls.
