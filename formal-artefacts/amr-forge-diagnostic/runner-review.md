# Independent runner preflight review — 2026-09-17

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

Result: no remaining demonstrated blocker in the reviewed transport, scheduling
and evidence-preservation controls. This is an offline implementation review,
not evidence that the live experiment succeeded.
The parent agent owns the complete runner/diagnostic suite and live execution.

Scope: `runner.py`, `tests/test_runner.py`, `README.md`, the accepted
`research_amr_forge_revision_2026-09-17.md`, the inherited single-POST transport,
and the diagnostic API where it affects runner behavior. No credentials were
read and no network request or live runner was invoked by this reviewer. The
reviewer's only source addition is `tests/test_worker_guards.py`; previous
experiment sources and evidence were not changed.

## Findings resolved before execution

1. Malformed JSON envelopes could survive decoding as a non-object and fail
   later while recording provider metadata. The runner now rejects non-object
   envelopes, normalizes the metadata envelope, and converts unencodable content
   to an explicit fatal result. Missing or invalid usage stops the
   batch. Assessor exceptions also receive an explicit fatal assessment.
2. `profiles/snapshot.json` was missing from the frozen dependency inventory.
   It is now included alongside parser/checker code, prompts, protocol, and
   historical evidence checks. The final inventory explicitly lists generation
   and checking dependencies; test files and the unimported physics adapter are
   excluded. The separate physics stage freezes its own additional inputs.
3. The first implementation omitted explicit repaired/newly failing input sets
   and the two-repair checkpoint. Both are now in the result trajectory; a parse
   failure marks the domain-set comparison unavailable instead of claiming that
   unassessed inputs were repaired.
4. Repair prompt framing initially differed from the old pilot. The original
   JSON data frame and instruction order are restored. D8-O's first repair is
   byte-for-byte equal to old request 005. Feedback is normalized through JSON
   before replay comparisons, avoiding Python tuple/list discrepancies.
5. The enhanced feedback pool initially remembered only last-displayed outputs.
   A historical input repaired while omitted by the four-example cap could
   subsequently regress without receiving regression priority. The runner now
   refreshes every already-seen input against the prior candidate's full report
   before the next feedback comparison; prompt caps and condition isolation
   remain unchanged.

A proposed nested-JSON recursion concern was withdrawn after direct offline
reproduction: the inherited profile parser already converts that recursion
failure to a parse rejection, and both `assess` and `program_key` return normally.

## Independently exercised checks

Command, run from the repository root:

```text
python -B -m unittest discover -s formal-artefacts/amr-forge-diagnostic/tests -p test_worker_guards.py -v
```

Result: **13 tests passed in 8.030 seconds**, exit code 0.

The final combined suite, run by the parent after narrowing the inventory to
those explicit dependencies, passed **42 tests in 70.439 seconds**. The reviewer
inspected the completed `offline-preflight-tests.txt` log. That final dependency
change was separately inspected and removes no imported generation/checking code.

The test fixture replaces `smoke.network_child` with a stub before any worker
invocation. It also forbids the credential reader and HTTP opener. A valid
request reaches the stub once. Every invalid request below reaches it zero
times:

- Wrong path, noncanonical attempt number, or attempt beyond the 16-call ceiling.
- Modified HTTP payload, prompt bytes, or feedback.
- Out-of-order condition or ledger attempt number.

- Changed frozen dependency hash or changed setup evidence.
- Finished run, fixture-mode protocol, or an earlier fatal record.
- A second invocation of the same worker claim.

Additional pure offline checks confirmed that the original first repair prompt
matches old request 005 byte-for-byte and that advancing from the fixed seed to
the accepted authored test fixture records 839 repaired inputs, zero newly
failing inputs, a comparable domain delta, and an acceptance stop. The authored
fixture was used only locally, never supplied to any model call.

## Reviewed invariants

- Four independent states use the fixed D8-O, D12-O, D8-F, D12-F order, at most
  four repairs per state and sixteen calls in total. A parsed AST repeat stops
  its state after acceptance has been checked; malformed source uses raw hashes.
- The live child accepts only its fixed run/attempt path, claims the attempt
  exclusively, checks frozen dependencies and the prior ledger, reconstructs
  prompt and feedback, and compares the exact serialized payload before invoking
  the inherited sole-POST helper. There is no retry or resume path.
- Requests are bounded to 65,536 serialized bytes and 2,048 output tokens.
  Missing or invalid usage stops the batch.
- Original feedback retains its old fields and truncation; enhanced histories
  stay within their own condition. The original task changes only the three
  rule-limit phrases for the twelve-rule conditions, retaining expression depth
  eight and the existing obligations.
- Each attempt keeps request/feedback/payload, raw HTTP evidence, response,
  exhaustive compressed assessment, transport outcome, token counts, and
  hashes. Selected physics source follows fixed condition order and first
  accepted repair, with exact output bytes.

Reviewed source SHA-256 values:

```text
runner.py                 cc1f9182a132635c2dbe9aa2741e56fe41e4a521439d228ae668f345f416bd3d
diagnostics.py            6566bb2a05bd241d08e3b8722593e5e633291a58e04738c07c66f00d3a273b81
tests/test_runner.py      7e1024f3db29300c3e7fbdf53ee617c5635d90a72e40a1e3b5ea95ff45c3cd5f
tests/test_worker_guards.py 33bc76818df465fe16ecbbd23d6df6db51595a55e149242cd4b7cfcf1db34f2d
```
