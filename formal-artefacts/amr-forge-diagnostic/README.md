# Forge-informed AMR diagnostic

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see the [record-maintenance report](../record-maintenance-2026-09-22/README.md). Raw replies, controller source bytes and physical trajectories are retained.

New post-hoc diagnostic of one existing failed initial candidate, P2-R1 (old record 004).
It does not replace the completed six-chain pilot or estimate a population success rate.

Protocol: `../../literature/scholar_search_2026-09-10/followup/research_amr_forge_revision_2026-09-17.md`.
Fixed round-robin conditions: D8-O, D12-O, D8-F, D12-F (8/12 rules, original/enhanced feedback).
Each gets at most four repairs. Acceptance precedes AST-cycle stopping. No network retry.
The same model, non-thinking decoding, 2,048-token cap and v1.1 safety obligations apply.

The user approved this execution.

Requests have a 65,536-byte JSON body cap and a 2,048-token output cap. Missing or invalid
usage stops the entire batch. The client subprocess deadline is 90 seconds.

`runner.py` uses the previously reviewed single-POST HTTPS transport with fixed-path,
source-identity and exclusive-dispatch guards. Credentials are read only inside the
network child, sent only to `https://api.deepseek.com/chat/completions`, never copied here.
An existing `run/` directory blocks re-execution. Do not delete or rename it to rerun.

Offline fixture runs require an explicit fixture flag and substitute worker; they cannot be
marked live. Tests use local fixtures. Raw provider replies, generated-controller source and physical
trajectories from prior stages are preserved.
Each live request preserves its exact prompt, feedback, payload, raw response, transport record,
compressed exhaustive assessment and hashes. Configuration and dependencies freeze before POST.
Only dependencies that drive generation/checking are in this freeze; tests and the separately
validated physics adapter do not affect model requests. Physics freezes its own additional inputs.

Conditional physics selection, declared before model calls: first accepted condition in the
fixed table order, then its first accepted repair, using exact raw output. Five paired scenarios
normal_A, normal_B, temporary, blackout, permanent. This would be an exploratory demonstration,
separate from any later independent evaluation. No acceptable source means no generated-source
physical run. Runtime natural-language advice is outside this experiment.
