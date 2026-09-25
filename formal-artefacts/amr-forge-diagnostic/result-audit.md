# Independent completed-run audit — 2026-09-17

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

**Result: the recorded seven-call diagnostic passes the read-only integrity and
reproduction checks below. None of its four trajectories produced an accepted
source. Each stopped at a genuine within-chain AST repetition.** No additional
API calls, credential access, manual source repair, or changes to the
run were performed during the original audit.

## Trajectories and stopping behavior

Every returned source parsed, and every assessment checked all 1,824 inputs.
All four trajectories started from the same unchanged old P2-R1 response 004:
839 source/model failure inputs, including 55 inputs undefined in both source
and model. A repeated response was assessed before the cycle stop was applied.

| Call | Condition | Repair | Source/model failure inputs | Correspondence count | Step rules | Repaired / newly failing inputs | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 001 | D8-O | 1 | 839 / 839 | 55 | 8 | 0 / 0 | Exact bytes and AST repeat the seed; cycle stop |
| 002 | D12-O | 1 | 784 / 784 | 0 | 9 | 55 / 0 | Continue |
| 003 | D8-F | 1 | 839 / 839 | 55 | 8 | 0 / 0 | Exact bytes and AST repeat the seed; cycle stop |
| 004 | D12-F | 1 | 784 / 784 | 0 | 9 | 55 / 0 | Continue |
| 005 | D12-O | 2 | 784 / 784 | 0 | 8 | 0 / 0 | Different AST, unchanged input failures; continue |
| 006 | D12-F | 2 | 784 / 784 | 0 | 9 | 0 / 0 | Exact bytes and AST repeat its repair 1; cycle stop |
| 007 | D12-O | 3 | 784 / 784 | 0 | 8 | 0 / 0 | Exact bytes and AST repeat its repair 2; cycle stop |

All sources have four `select` rules. There are only three distinct raw programs
among the seven responses. Calls 002, 004, and 006 are byte-identical. Calls 005
and 007 are byte-identical to the old pilot's response 005; that old response was
not supplied to those calls. The current 8-rule conditions never reached repair
2. D12-F reached repair 2; D12-O reached repair 3. No repair 4 was executed.
The recorded two-repair checkpoints correctly preserve these distinctions.

Both 12-rule conditions initially added a ninth, final `Proceed/Traversing`
fallback. This covered the same 55 ordinary-motion inputs left undefined by the
seed, with no new failing inputs. The 55 correspondence counts in the seed and
its repetitions are classified as **source and model both undefined**, not
disagreement between two defined outputs. They disappear after adding coverage.

The remaining 784 failures all violate `stop_on_invalid_or_blocked_input`: the
first step rule returns `Brake/Stopped` while `Halted` is false. Its identical
later guard returning `Brake/BrakeRequested` is shadowed by first-match semantics.
D12-O repair 2 removes that shadowed rule, reducing nine step rules to eight
without repairing any of the remaining failures. Because the cycle rule compares
ordered ASTs rather than semantic equivalence, that change correctly received a
third repair; the third response then repeated the second.

The enhanced first-repair prompts each contained three current examples and no
history. D12-F's second repair received one current stop-confirmation example
and two historical ordinary-motion examples, both correctly labeled repaired.
Their source locations were recomputed as the ninth fallback rule. The current
example explicitly showed `Halted=false`, actual `Brake/Stopped`, and allowed
`Brake/BrakeRequested`. The returned program nevertheless repeated repair 1.

| Condition | Executed repairs | Stop |
| --- | ---: | --- |
| D8-O | 1 | Cycle to seed |
| D12-O | 3 | Cycle to repair 2 |
| D8-F | 1 | Cycle to seed |
| D12-F | 2 | Cycle to repair 1 |

Reported usage totals are 16,471 input tokens and 1,800 output tokens. All seven
responses finished normally with `finish_reason=stop`, no refusal or tool call,
no truncation, and output lengths of 241–270 tokens, below the 2,048-token cap.

## Integrity and reproduction checks

The audit used Python with bytecode writing disabled. Credential access and the
network helper were replaced in memory with functions that raise immediately;
only read-only runner and diagnostic functions were invoked. The complete audit
assertions exited successfully.

- The run's evidence manifest exactly matches all **97 listed run files**, with
  no missing or additional files apart from the manifest itself. Each attempt's
  own file inventory exactly matches its outcome inventory.
- All **63 frozen generation/checking dependencies** match their saved hashes.
  The setup manifest, frozen starting response, and preparation input hashes
  verify. All **271 old-pilot files** match the saved pre-run inventory, and all
  **33 original-smoke files** match the pilot's inherited inventory.
- There are exactly seven attempt folders, seven exclusive worker claims,
  seven dispatch markers, and seven distinct provider request IDs. The order is
  D8-O1, D12-O1, D8-F1, D12-F1, D12-O2, D12-F2, D12-O3. Every dispatch specifies
  one POST, zero retries, and the approved DeepSeek endpoint.
- All request bodies reproduce byte-for-byte from the recorded condition state,
  frozen task and repair prompts, and computed feedback. Their payloads have one
  user message, `deepseek-flash`, temperature 0, thinking disabled, streaming
  disabled, and `max_tokens=2048`. The protocol configuration matches the frozen
  transport configuration.
- The saved `response.bin` bytes equal the UTF-8 encoding of the corresponding
  raw HTTP envelope's assistant content, with no edits or substitutions. Every
  transport reports HTTP 200, no credential-echo redaction, and no body-limit
  exceedance. Model, fingerprint, and request IDs match their outcomes.
- All seven compressed exhaustive reports were recomputed from the exact raw
  responses under the appropriate 8/12 profile and compared field-for-field
  after JSON normalization: **12,768 checked input evaluations in total**.
  Failure sets, repaired/newly failing sets, locations, allowed outputs, and
  correspondence categories match. These evaluations are repeated checks of
  related candidates, not independent task samples.
- Prompt/feedback replay, isolated history progression, canonical AST keys,
  acceptance decisions, cycle reasons, final condition trajectories, and
  two-repair checkpoints all match the saved result. No pending schedule slot
  remains after the four cycle stops.

- Prompt reconstruction contains only the frozen task/repair instructions, the
  immediately preceding candidate from that condition, and that condition's
  permitted feedback. No authored reference source, full domain table, or other
  condition's repaired candidate is introduced. The byte-identical transport
  content confirms that no local manual repair entered the assessed responses.

## Identical request, different recorded response

Current call 001 (D8-O repair 1) and old pilot request 005 have **byte-identical
prompts and byte-identical HTTP payloads**. Both report `deepseek-flash` and the
same fingerprint, also shared by all seven current calls:

```text
aeb56401ca74e127821c4f9126dcb669
```

The old response had 784 source/model failure inputs; the current response
exactly repeats the 839-failure seed. Their source hashes differ:

```text
Old response 005: dfe475a7dc75a684b3f4f6bc05a34e2eb34dabc61e328f3fc613664ff247f311
Current call 001: 7b263c1eabf5a5ea02fc1e45f01217b629d538a8f667bd28b16a31a36374894c
```

Thus the recorded temperature-zero configuration and fingerprint did not yield
byte-level reproducibility for this pair. The artifacts establish the difference,
but do not identify its provider-side cause. They do not establish a model
revision change, nor justify attributing old/current differences to prompt edits.

## Interpretation limits and next-stage gate

These are four post-hoc repair trajectories from one previously observed failed
candidate, with only three distinct returned programs. They do not estimate a
population acceptance rate or support a causal effect size. The identical first
responses within each rule-limit pair provide no observed enhancement benefit in
this run, but do not prove that structured feedback or historical examples are
ineffective generally.

The 12-rule trajectories show a local coverage improvement from permitting a
ninth branch; they do not establish that eight rules cannot express the contract,
nor that increasing the limit resolves stop-confirmation errors. All cycles stop
early under the fixed protocol. This run cannot determine whether additional
post-cycle calls would help, and no extra calls were authorized or attempted as
part of this audit.

No source is accepted, `selected_for_exploratory_physics` is null, and the
generated-source physical demonstration gate remains closed. Old pilot results
remain intact. Claims about physical safety, general model capability, or
independent evaluation success are not supported by this diagnostic.

Audit anchors:

```text
Frozen runner.py SHA-256:
cc1f9182a132635c2dbe9aa2741e56fe41e4a521439d228ae668f345f416bd3d
run/result.json SHA-256:
011f7270cdedc03e96d2721024b0b3f9ad059919a2ef0dc5e3f7389ef771524e
run/evidence-sha256.json SHA-256:
29ad0ce27a3df3a72783e20106cb5298fcd79d560e1a2bdf861677cd4bfd975c
```
