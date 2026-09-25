# Independent replication preflight review

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-17 preliminary review; completed independently on 2026-09-21 after user resumed. Scope: six fresh initial requests, same-chain repairs, inherited evidence and physical deployment of every unique accepted source. Review uses local inspection and offline fixtures only. No credentials, live requests, historical-file changes, or Git operations are performed by this reviewer.

**Disposition: PASS for the reviewed runner and physical adapter; no blocking defect found.** Final code inspection, exact egress comparison, inherited-evidence checks and the combined offline suite completed on 2026-09-21. This is a pre-dispatch implementation verdict, not a live result or a claim about provider availability. Analyzer/report verification remains a separate review.

## Protocol and fixed interpretation

The declared order is P1-R1, P2-R1, P3-R1, P1-R2, P2-R2, P3-R2, with all attempt-0 requests preceding the two possible repair rounds. Each initial message contains only its original prepared task with three eight-to-twelve rule-count wording substitutions. No old failure or success program belongs in an initial request. Repair context is restricted to the same sample's task, preceding final content, and accumulated deterministic feedback; reasoning text is never re-fed.

Acceptance remains the twelve-rule profile of the unchanged v1.1 policy over 1,824 inputs. Initial acceptance and eventual acceptance must remain separate. An accepted chain stops immediately; repeated ASTs (raw bytes for unparsable outputs) stop only that chain. Fatal provider, transport, usage, or unexplained limit failures stop the batch without retry. A complete batch is required before physical deployment.

Each accepted sample contributes its first accepted raw output to selection in fixed sample order. Exact source-byte SHA-256 controls deduplication; AST-equivalent but differently formatted programs remain separate physical sources. Duplicate sample identities remain mapped to their representative. Physics executes five fixed scenarios per unique source and five shared handwritten reference episodes, at most 35 episodes. These are repeated requests for one task and related analytic simulations, not six industrial tasks or a general reliability estimate.

## Independent checks

The historical pilot, Forge, thinking, and extended generation evidence manifests match all 270, 97, 33, and 48 recorded entries. The Forge, thinking, and extended frozen source manifests match all 63, 63, and 66 entries. The latest extended physical archive matches all 26 recorded entries.

All three prepared R1/R2 prompt pairs are byte-identical. Each prompt has exactly one occurrence of each of the three rule-limit phrases. The six saved egress-preview request files match an independent reconstruction of the protocol exactly, each with one user message and the required high-thinking, 65,536-output, nonstreaming configuration with no temperature field.

| Variant (both repeats) | Prompt SHA-256 | Request bytes |
| --- | --- | ---: |
| P1 | `25293ef573d9a4f1e86c0cb815669d16725462dd515879645f65520fb09f0665` | 5,536 |
| P2 | `fc014918da5ad2c3155e577e45f404d9845657220f9c615c10a06b0aff6d0794` | 5,807 |
| P3 | `d16d72582c212c9074db7be89da0a6059f0511eda370cfcb76473799d498655f` | 5,677 |

Static inspection of the physical adapter finds the planned boundaries present: reconstruct all six states and counters; reproduce complete fixed selection; verify exact bytes and provider-envelope decoding for every accepted sample, including duplicates; freshly assess each unique source; execute the frozen five scenarios with shared references; check runtime source identity; and freeze/recheck physical and generation inputs. The combined offline suite below now verifies these adapter gates, including the corrected serialized-list comparison in `verify_live`; it does not run physical episodes.

## Final verification

On 2026-09-21 the bundled Python interpreter ran `-B -m unittest discover -s formal-artefacts/amr-independent-replication/tests -v`: **32 tests passed in 45.054 seconds**, process exit 0. The complete fresh log is `offline-preflight-tests-2026-09-21.txt`. Coverage includes six-initial-before-repair ordering, the 18-call ceiling, chain-local repetition/history, first acceptance, exact-byte deduplication, fatal/no-retry boundaries, credential-echo redaction, frozen dependency drift, offline/live separation, mapping rejection and the positive serialized sample-list live gate.

The reviewer independently reconstructed each initial prompt from its historical prepared original and the three stipulated wording edits, compared the explicit configuration to `payload_for(prompt_for(initial_state))`, and compared serialized bytes with every saved prompt/request preview. All six match. Request SHA-256 values (identical for R1/R2 of each variant):

| Variant | Exact request SHA-256 |
| --- | --- |
| P1 | `b294640148e3901a7dcef785f8206994a118e595491f784dee261fe5a1b924a3` |
| P2 | `b90232f494483aff5671cb6130c57c2bf300484a7c50bc9ab9189cff2b5d611e` |
| P3 | `6797a8ae095e4d046b59db72ea64cb5c8c6f39fc7a6b5bbaa480a2dd224bf8d7` |

All historical archive/dependency counts stated above were rechecked successfully, as was `smoke.verify_preparation()`. No new live `run/` or `closed-loop/` directory existed when these checks finished. All test requests used local fixtures or mocked transport; this review read no credentials and dispatched no network request.

Reviewed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `runner.py` | `63e0d07b517cbc6307af3d6938039139a62cb986bb5627c3adddd8db3a07caf3` |
| `simulate.py` | `233f79691e4a244b4a6f2a591bf574d4d8daa913ef2b12ef470bfb2664010894` |
| `tests/test_runner.py` | `1ae80d5561eb2961a2ce85e6e9ccc14f1827b00c143d1d129bac50460b0013fd` |
| `tests/test_simulate.py` | `b5fc3e45dd4563b217deb82793ca1f27b2844cd859458db702b9871b72687049` |
| `README.md` | `4890cadea7bab07e26bfdcf510b99cdb2647f403faabd652287f0a309169ed4d` |
| Replication protocol | `5ae3a1338e0f6091814ec87c9d335a57488b7c8eb8361bb14bd53d0d2311125e` |

No code change was required by this final review. Physical deployment remains conditional on a complete live batch, all six terminal chains, a nonempty accepted-source selection and fresh evidence/source verification. No claim of live reproducibility, simulation success or hardware safety follows from this preflight pass.
