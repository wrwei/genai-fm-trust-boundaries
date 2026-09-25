# Independent replication result audit

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-21. Generation review used finalized local evidence only. No credentials, provider requests, reasoning-text output, physical episodes or archived-file edits were involved. The reproducible checker is `generation_audit.py`; its machine-readable result is `generation-audit.json`.

**Generation disposition: verified.** All six initial requests were accepted on attempt 0 after fresh assessment of all 1,824 inputs per response. No repair requests were needed. The completed protocol selects five distinct raw source byte strings; P2-R1 and P3-R2 share identical bytes and one physical source.

## Generation outcomes

| Sequence | Sample | Rules select / step | Bytes | Completion tokens (reasoning subset) | Duration s |
| --- | --- | --- | ---: | --- | ---: |
| 001 | P1-R1 | 3 / 9 | 1156 | 7200 (6894) | 29.748056 |
| 002 | P2-R1 | 3 / 9 | 1372 | 10497 (10084) | 41.808276 |
| 003 | P3-R1 | 7 / 9 | 1736 | 13527 (13004) | 53.017314 |
| 004 | P1-R2 | 4 / 9 | 1069 | 7972 (7678) | 32.363820 |
| 005 | P2-R2 | 3 / 9 | 1372 | 9667 (9254) | 38.290119 |
| 006 | P3-R2 | 3 / 9 | 1372 | 10229 (9816) | 41.782156 |

Every row parsed, checked 1,824 inputs, and had zero source violations, model violations and source/model correspondence mismatches. All final contents came from HTTP 200 responses with `finish_reason=stop`, `deepseek-flash`, fingerprint `aeb56401ca74e127821c4f9126dcb669`, and no fatal status. Rule limits apply separately to each function: P3-R1 has seven selection rules and nine step rules, both below twelve. Every duration is below the 600-second socket and 660-second parent limits. All six include observed reasoning metadata; reasoning text is excluded from source, feedback and this report.

## Evidence and independent reconstruction

- All 90 files in the finalized generation manifest and all 72 frozen inputs verified. Setup hashes, inherited archive inventories, frozen historical dependencies and preparation checks passed before and after the audit.
- All six attempt folders have complete exact inventories, one worker claim and one dispatch marker. The sequence is exactly P1-R1, P2-R1, P3-R1, P1-R2, P2-R2, P3-R2, with zero retries and six total dispatches.
- Each initial task was independently reconstructed from its prepared original using exactly the three eight-to-twelve wording substitutions. Complete actual payload bytes match both this reconstruction and the saved egress preview. Each request has one user message, high thinking, 65,536 maximum output tokens, no temperature, no candidate and no cross-sample context. Initial feedback is null.
- Each saved response is exactly the UTF-8 encoding of provider final content.
- All six fresh finite-domain assessments match every archived field, including all 10,944 full cases across the responses. Reconstructed full states and trajectories match `result.json`. An independent chain-state reconstruction verifies first acceptance, stop decisions and source selection; every chain stops at its accepted initial attempt.
- The original audit rechecked the generation inventory and dependencies after reconstruction. The checker made zero network requests.

## Source and behavior diversity

| Physical representative | Samples using its raw source | Source SHA-256 |
| --- | --- | --- |
| P1-R1 | P1-R1 | `8c9a614d51b0004e5b3b039666c31232bc15e72ce6045a9cda6684ff52ce7824` |
| P2-R1 | P2-R1, P3-R2 | `c7e96f0c096ea4b1cb67607f700b23f24a34d6d11d3f0c36b7acba6bb446e8b9` |
| P3-R1 | P3-R1 | `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd` |
| P1-R2 | P1-R2 | `eb5a9d7915a64a816b95223e864e47f9fcff117b490c78994b6fdb61285d6ed3` |
| P2-R2 | P2-R2 | `d864df79a77d78db50ad14bf6f683ec2897dfa0c2668f95244fda76c6f7f8c75` |

There are five distinct raw byte identities and five distinct canonical program identities, but only **two selection-output behavior classes** over the complete 32-input selection domain. All accepted programs have identical step outputs over all 1,792 step inputs. This is descriptive output equivalence; the protocol still deploys five raw sources and does not collapse sources by behavior.

| Selection class | Samples | Behavior when owner is free and both robots request |
| --- | --- | --- |
| 01 | P1-R1, P2-R1, P1-R2, P2-R2, P3-R2 | Select A for all four preference combinations |
| 02 | P3-R1 | Select B only when PreferB is true and PreferA is false; otherwise select A |

The two complete selection tables differ on exactly one input: owner free, both requests true, PreferA false and PreferB true. The protocol treats preferences as advisory, so both choices satisfy the unchanged obligations. Full class tables and sample mappings are in `generation-audit.json`; these observations do not alter acceptance or exact-byte physical selection.

## Usage audit

Reported token totals are 6,882 input and 59,092 completion tokens.

## Generation evidence identities

| Artifact | SHA-256 |
| --- | --- |
| `run/result.json` | `21a2a4c58b352384af78197869e6dda8bda0eb0b8a8f33fc857380387e8e4c32` |
| `run/evidence-sha256.json` | `7517a087db92f2cc9e29fc9baee394bcfa670faabaebb95f953789331ab8167f` |
| `generation_audit.py` | `b0436454e4bf4888a34870164bfa4e04aae2b5215b358b0e38cfbe3d16eac6ab` |

This result establishes six successful fresh-context requests for three wordings of one fixed task under the chosen configuration. It does not establish success across independent industrial tasks or provider-internal statistical independence. Physical results require their own trace audit, and neither finite-domain acceptance nor analytic simulation establishes hardware safety.

## Physical result audit completed

The separate [physical trace audit](physics-audit.md), with reproducible `physics_audit.py` and detailed `physics-audit.json`, verified all 30 episodes without re-running the plant or calling a model. The original audit checked all 70 physical manifest files and 166 frozen inputs before and after replay; raw source bytes and physical trajectories are retained. Exact source identities and sample mappings, 75,816 step decisions, 44,148 selection decisions, 42,498 standstill checks and 2,133,618 geometric pair intervals were verified. All per-episode and aggregate summary fields reproduce; minimum distance lower bound is 0.26068542394925565 m.

All 24 clearable episodes complete; all six permanent-blockage episodes end at 120 seconds with both robots stopped, zero final speeds and A retaining its reservation. No collision, unresolved interval, early release, runtime rejection or completion mismatch occurs. P3-R1 alone matches reference B-first ordering in normal_B; the other raw sources legally retain A-first ordering. Recorded pedestrian-brake triggers are outside the straight-approach stopping premise, so geometric replay and that inapplicable premise remain distinct.

Physical summary SHA-256: `181172124fed7a47bcbfca5edef1a1db33327dd6163b8318277d0a54ebe5924a`.
Physical manifest SHA-256: `9104f593299f2f67bd8f0785222afe7679801b0c8f74e72ad70fc2b7959cd188`.
