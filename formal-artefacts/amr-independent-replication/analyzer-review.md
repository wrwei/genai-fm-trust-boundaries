# Independent replication analyzer review

Reviewed `analyze.py` against `runner.py`, `simulate.py`, and the replication protocol. The review was limited to derived reporting and did not read or modify a live run.

## Findings and changes

- Acceptance is now derived from the stored assessment and the final fatal status. The analyzer asserts that the stored `outcome.accepted` value matches that derivation before it contributes to any acceptance or canonical-program count.
- A successful transport decode can subsequently become `assessment_error` if the local assessor fails. The analyzer now permits only that explicit, evidenced override and reports the final fatal status from `outcome.json`.
- The runner's assessment-infrastructure fallback intentionally has no `rule_counts`. The analyzer preserves that absence as JSON `null` instead of failing or inventing counts.
- `new_calls` and `network_dispatches` are distinct. The analyzer now verifies call count from outcome records and dispatch count from actual `attempts/*/dispatch.json` artifacts, allowing a fatal attempt before POST to have one call and zero dispatches.
- Initial and eventual acceptance counts are checked against replayed state. A fatal record must be unique, last, and equal `result.stop`; a protocol-complete result must have no fatal record and no remaining scheduled slot.
- Closed-loop reporting now requires source-catalog cardinality to equal selected-source cardinality. Each sample may map to only one source key before the complete mapping is compared with the summary.
- `analyze_run` accepts explicit run, output, and closed-loop paths so isolated regression tests can analyze temporary evidence without touching the live or immutable directories. Command-line behavior remains on the fixed local run and derived output paths.

## Focused offline verification

`python.exe -B -m unittest tests.test_analyze -v`

Two tests passed:

1. A real offline runner fixture with a successful transport and a mocked assessor exception produces `assessment_error`; analysis completes, reports no acceptance, and emits `rule_counts: null`.
2. A real offline runner fixture that fails before POST produces one attempt, zero dispatches, and a correctly summarized `transport_error` batch.

`analyze.py` also passed Python bytecode compilation. Before the focused follow-up, the existing runner and simulation suite passed all 32 tests; it was not rerun after the follow-up because the subsequent changes are covered by the two analyzer-specific regressions and do not modify the runner or simulator.
