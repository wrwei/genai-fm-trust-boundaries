# Independent pre-dispatch review: extended output

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-17. Scope: the new extended-output protocol, changes from the previously reviewed runner, inherited-history protection, and the adapted physics gate. This review used local files and offline fixtures only. No credentials, provider requests, or historical-file edits were performed.

**Disposition: no outstanding blocker for this declared bounded stage.** The live run directory was absent when verification completed. This review does not assert a live model or physical result.

## Changed controls and preserved contracts

- The stage identity is `amr-thinking-extended/v1`, with distinct module names, output directory, protocol path, and conditions N64-F/T64-F. Both condition tuples retain the **12-rule** acceptance profile; “64” denotes the enlarged output allowance.
- Both requests use `deepseek-flash`, `max_tokens=65536`, and nonstreaming output. N disables thinking with temperature 0; T enables thinking with high reasoning effort and omits temperature. Both start from the same original P2-R1 failure and retain the same 1,824-input obligations, enhanced feedback, and accumulated witnesses.
- The concrete transport timeout is 600 seconds, with a 660-second parent-process deadline. The exclusive worker/dispatch markers, fixed endpoint, no proxies or redirects, no retries, maximum four repairs per condition, and maximum eight calls remain in place.
- The preceding thinking stage is included in a separate inventory and frozen-input copy. Both are covered by setup hashes and rechecked before dispatch. Drift in recorded evidence or source dependencies prevents a POST.
- The output-boundary test exercises 60,000 total tokens with 59,000 reasoning tokens and rejects 65,537 completion tokens. Missing reasoning metadata remains explicitly unconfirmed. Only exact `content` is assessed or re-fed.
- The new physical adapter differs from the prior reviewed adapter only in stage/module identity and associated messages. It retains the both-terminal/live-evidence gate, fixed first-accepted condition/repair selection, exact provider-content/source-hash checks, fresh acceptance assessment, and frozen physical equations and oracle. The same five scenarios and two controller arms are required; offline fixtures cannot deploy.

The generated first request bytes match both saved egress previews exactly. Their prompt bytes are identical to both prior thinking requests and the original D12-F first request. The common UTF-8 prompt SHA-256 is `77a084b1728c058798a2b1b941cd89a5e5f3808d4e1072b9e80dea2677528695`. Both initial assessments check 1,824 inputs and retain the known 839 failures.

The historical pilot, Forge, and thinking evidence manifests independently matched all 270, 97, and 33 recorded entries. The Forge and thinking 63-file frozen source manifests also matched the files present at that review. Prior raw provider replies and generated-controller bytes were preserved.

## Independent verification

Only the new stage's suite was run; no old full suite was repeated:

```text
python -B -m unittest discover -s formal-artefacts/amr-thinking-extended/tests -v
Ran 30 tests in 52.688s
OK
```

Reviewed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `runner.py` | `662cf63549da98aa67f4a4eef7dcc997eff7b1068406ab867b6e06a8c4fdf9b7` |
| `simulate.py` | `bf0af30269de7f77593b060e121812a0537f71b6b62327da4b10c903c0fca546` |
| `tests/test_runner.py` | `84289f0378e09d15616e6b6a0fc1283946a3f7b484302f79f07e280d3e79ded3` |
| `tests/test_simulate.py` | `990f59aaa23d074a7b59133c70b1ab75c700e58c96dd3b473cbc9a6e6bd7e438` |
| `research_amr_extended_protocol_2026-09-17.md` | `e5cb3c59fd4cff05ff01c7362ec8c34589b8501d700e4cf6b9b0c9df6254fd36` |

The interpretation remains one-seed repair diagnosis rather than independent task sampling.
