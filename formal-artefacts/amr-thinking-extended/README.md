# Extended-output AMR thinking comparison

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see the [record-maintenance report](../record-maintenance-2026-09-22/README.md). Raw replies, controller source bytes and physical trajectories are retained.

This isolated stage implements the user's instruction to prioritize task completion and allow enough output for high-effort thinking. It uses the same previously observed P2-R1 failure, twelve-rule profile, actionable feedback, accumulated witnesses and 1,824-input acceptance domain. Prior raw provider replies, generated-controller bytes and physical trajectories are preserved.

Protocol: `literature/scholar_search_2026-09-10/followup/research_amr_extended_protocol_2026-09-17.md`.

N64-F disables thinking with temperature 0; T64-F enables high-effort thinking with no temperature parameter. Both use deepseek-flash, max_tokens 65536, nonstreaming responses, at most four repairs each and eight calls in total. Network timeout is 600 seconds and child deadline is 660 seconds. Acceptance or a repeated program stops a condition; transport/usage/truncation errors stop the batch, with no retry.

Only raw provider content is assessed as source. Reasoning is archived in the response envelope, never used as source or re-fed, and summarized only by metadata. Reports distinguish unevaluated output from a zero-violation accepted program.

Before live dispatch, run offline tests and review. `runner.py --key-file <local credential file>` creates the fixed run directory exclusively. Never rerun or delete/recreate an archived run. The credential is read only in the guarded worker and is not printed. Outbound messages contain synthetic Boolean robot specifications, prior generated programs and finite feedback only.

If both conditions terminate normally and an accepted source is selected, `simulate.py` verifies its exact identity and runs the five predefined paired scenarios. Physics evidence is frozen separately. This exploratory diagnostic is not independent task sampling or proof of industrial safety. After completion, see result-audit.md, analysis.json and the result report for outcomes; this maintained README retains the experiment settings.
