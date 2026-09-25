# Task 1 fix round 1

Follow independent `recorder-review.md` and original `task-1-brief.md`; only edit trial.py, tests/test_trial.py and your logs/report. No calls, subagents, commits or old AMR edits. Coordinator owns rehearse.py and all docs. Findings were checked against current code and reviewer bounded probes.

1. An existing pending request must still be returned and its raw response retained if detected limits would otherwise stop future requests. Summary reports why stopped, never marks incomplete coverage of the six chains as complete or selects a candidate. Count all never-attempted sample IDs in `unattempted_samples`; pending counts mean actionable repair or an actual pending request. Preserve already-recorded accepted results and complete records.

2. Track simultaneous output-token exceedance and non-ok response status independently. Preserve a human-readable terminal_reason and deterministic violation_flags for all applicable causes. Acceptance is false for output-token exceedance or non-ok status. Summary infrastructure_failures must count non-ok statuses even when the output-token bound was also violated. Keep explicit output-token violation counts. Save failed raw responses before stopping future requests.

3. Strict metadata identity types: attempt_index integer0..2, requested_max_output_tokens positive actual int (not bool or float); sample_id/status/provider/model_id/request_sha strings with normal identity checks. Compare decoding via type-preserving canonical JSON so True!=1 and 0!=0.0 as submitted declarations. Invalid status lists/objects raise ValueError rather than unhandled TypeError. Keep exact metadata key contract.

4. Add targeted tests that initially fail on current code, then pass: an output-token violation stops later requests while retaining raw evidence and correct incomplete/pending/unattempted counts; timeout plus output-token violation is still counted as infrastructure failure; false/0.0 attempt indices, true/1.0 requested caps and bool/int/float decoding differences are rejected without ledger changes. Existing rehearsal tests must still pass. Keep distinct red and green logs and label historical test counts separately from new verification.

Return DONE, final test counts/seconds, exact changed files and any limitations. Update task-1-report.md by appending fix-round details; do not replace historical initial report.
