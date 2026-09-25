# Replication final consistency review

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-21. Bounded review of the current `analyze.py`, `generation_audit.py`, `physics_audit.py`, and `research_amr_replication_results_2026-09-21.md`. This review does not rerun generation, physical episodes or historical test suites and does not modify either evidence directory during that review.

**Final disposition: PASS.** Generation and physical audit outputs, the finalized research result report and the updated RESEARCH_STATUS.md are consistent. No unresolved blocking finding remains. Physical completion and independent trace-audit success are now recorded explicitly.

## Generation and report consistency

The six sample rows, rule counts, completion/reasoning-token counts, durations, fingerprint and six initial acceptances agree with independently checked generation evidence. The aggregate input/output totals are 6,882 / 59,092. The report distinguishes five raw/canonical identities from behavioral diversity and correctly preserves the one-task, three-wording and selected-configuration limitations. It makes no repair-benefit claim from this zero-repair batch.

The generation audit's successful output applies to this finalized batch. Its finite-domain behavior diagnostic preserves physical selection: five raw identities, five canonical identities, two selection behavior classes and one step behavior class.

The analyzer distinguishes recorded assessment-infrastructure failure from successful provider decoding and counts actual dispatch markers independently of attempt records. Those are appropriate fixes for its two focused fatal fixtures; the parent reports both fixtures passed. The actual batch has six attempts and six dispatches. Full fresh assessment is supplied by the separate generation audit, not claimed to be independently recomputed by the analyzer itself. No blocking issue was found in these actual-batch claims.

## Physical audit review

Static review compared the trace auditor with the frozen closed-loop implementation. The auditor reconstructs monitor facts, source/ref decisions, fallback behavior, commands/delivery, reservation state, releases and completion; reconstructs continuous motion pieces and re-scores geometric intervals; checks source identities, exact source mapping, all episode summary fields and aggregate comparisons; and rechecks frozen inputs and physical evidence afterward. Its claims concern archived trajectory replay and kinematic bounds, not independent re-execution of the entire route-planning plant.

One concrete gate gap was sent to the physical-audit owner: the original audit inferred `termination='horizon'` for any noncomplete terminal trace without asserting its final time was 120 seconds. It should reject an early truncated trace even if a matching summary also labels it `horizon`, and reject any event after the declared horizon. The owner added both checks; independent inspection confirms the timestamp bound and final incomplete-trace equality are present. The owner reports syntax verification passed. This finding is resolved; the corrected auditor subsequently completed all 30 archived episodes successfully.

The final research report should retain advisory preference behavior, permanent-blockage noncompletion and the inapplicability of straight-approach stopping evidence where applicable. Zero collision or assumption-violation counts do not establish hardware safety or satisfy an inapplicable geometric premise.

## Final physical disposition

The completed physical audit and final report were inspected after the parent confirmed audit process exit 0. A bounded read-only consistency check against `physics-audit.json` and finalized `closed-loop/summary.json` confirms:

- 30 episodes, 70 manifest entries and 166 frozen input files; 75,816 step decisions, 44,148 selection decisions, 42,498 standstill checks and 2,133,618 geometric pair intervals.
- Exactly 24 safe-and-complete episodes and six permanent-blockage episodes ending at 120 seconds with both robots Stopped at zero speed and A retaining its reservation.
- No recorded collision, unresolved geometric result, early release, runtime rejection or completion mismatch; minimum geometric distance lower bound 0.26068542394925565 m.
- In normal_B, only source_03 (P3-R1) and the handwritten reference select B first; the other four distinct raw sources select A first. Source/sample reuse remains explicit.
- The stated temporary-blockage and blackout brake/resume/proceed transition times agree with the audited boundaries. All recorded pedestrian stopping diagnostics explicitly mark the straight-approach premise inapplicable.

The finalized result report and main research-status update retain all interpretation limits and no longer represent the physical audit as pending. The appended physical section of `result-audit.md` matches the separate detailed physical audit. No experiment, broad test suite or full audit was repeated in this last consistency pass; no code or archived evidence was changed.
