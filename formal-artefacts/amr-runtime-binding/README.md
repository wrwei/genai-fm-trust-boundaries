# AMR runtime binding — 22 September 2026

This additive package connects a serial, fixed-mission Python adapter to the existing AMR v2 source-restricted composition. It retains the generated controller and existing plant. It is not a new case selection, a complete CKA algebra instance, or whole-Python/continuous-plant refinement.

Design: [claim–evidence–gap matrix](../../docs/superpowers/specs/2026-09-22-amr-runtime-binding-design.md). Results: [Chinese research report](../../literature/scholar_search_2026-09-10/followup/research_amr_binding_results_2026-09-22.md).

## Evidence chain

1. `binding.py` loads the exact accepted v2 source, verifies its fixed identity, and uses its actual output at Validate/Service. Missing advice is represented as absent preference; the source supplies fallback. Pending selections are retained.
2. Raw replies use the existing strict parser and fixed request/context binding. Only trusted `RequestAdvice` opens the mailbox. Provider messages never call a control action. Each transition records its raw input, abstract event, full before/after state and source decision when applicable.
3. `hol/AMR_Runtime_Binding.thy` proves each abstract adapter step is a `source_next` step. All finite adapter traces are in `S_source` and in the established component composition. `adapter_authority` explicitly reuses the previous authority theorem; it does not replace the interface with the set of safe traces.
4. `binding_conformance.py` compares all 432 core × 6 mailbox × 30 abstract input transitions with a table evaluated by Isabelle. All **77,760** rows match, including emitted input and output events. All **24** fixed parser cases match their literal expected outcomes.
5. `physical_binding.py` is an additive copy of the existing physical episode with explicit adapter substitutions. [The exact function diff](physical-driver.diff) and [origin hashes](physical-driver-origin.json) identify those changes. Four full runs use the adapter at every discrete protocol step.
6. `audit_execution.py` verifies the retained event sequence against the HOL table. `source_link_audit.py` independently reconstructs observations, source facts and modes, connects source actions to physical intents and signed-off commands, and consumes Issue/Apply events once. The execution audit replays actual movement and uses the prior independent geometry audit rather than the driver's geometry oracle.

## Results and replay

Isabelle2025-2 [build](hol/build.log) succeeded; the [proof audit](hol/export/AMR_Runtime_Binding.AMR_Runtime_Binding/binding-proof-audit.txt) finds no skipped proofs or oracle dependencies. [Finite conformance and parser results](evidence/conformance.json) pass. [Four physical runs](evidence/run-2026-09-22/summary.json) complete both tasks at 58.9 simulated seconds with first grants A/B/B/A (none / retained B / invalid then B / late B). No collision, unresolved geometry, early release or reference violation was reported. These runs are offline content replays at specified simulation ticks, not new LLM samples or a replay of historical network latency.

[Execution audit](evidence/run-2026-09-22/execution-audit.json) verifies 5,661 adapter events, 7,352 raw source motion outputs, 452 source selection records, 24 command applications, 47,120 robot motion intervals, 212,040 continuous pair intervals and all eight task completions. The geometry is independent of the driver's oracle; the source interpreter and reference plant are shared. These are correlated trace checks, not independent experimental sample counts.

[Eleven bounded interface witnesses](evidence/run-2026-09-22/mechanisms.json) meet their declared expectations. Skipping binding and resetting pending break correspondence while still making legal grants; waiting removes service supply without violating finite safety inclusion. No natural defect rate is inferred.

From this directory using the bundled Python executable and `-B`:

```powershell
python -B -m unittest discover -s tests -v
python -B hol/build.py
python -B binding_conformance.py
python -B audit_execution.py
```

`run_experiments.py` creates the fixed output directory exclusively and intentionally refuses to overwrite retained runs. It makes no API calls. Reverification uses the retained traces; another physical batch needs a separately declared directory/protocol, not deletion of the existing evidence. `derive_physical_driver.py` is provenance tooling; ordinary replay uses the already saved driver.

## Boundaries

- One serial scheduler, one fixed string request/context per instance, no cancellation, epoch reuse or parallel callbacks. Raw identity equality and parsed None/A/B are formal input classes; JSON and arbitrary strings are not mechanically verified.
- The two-service theorem assumes no pending choice, at least one legal request and supplied services, with only finite message inputs between them. The prior at-most-three-service result covers arbitrary pending under its own assumptions. Neither proves transport completion, infinite fairness, or resilience to messages starving the scheduler.
- The model protects discrete grants and admitted command applications. A plant can keep moving under a held actuator intent; the theorem does not establish permission for every infinitesimal motion or timely physical revocation. Release geometry, timestamps, sensor truth, command generation/expiry and continuous dynamics remain separate obligations.
- Twelve new behavior/audit tests and four existing mailbox tests pass. Four negative audit tests reject invented facts, a source-action/movement mismatch, an ungrounded command, and a self-consistent source output computed from a false observation. Earlier source/model and physical experiments are preserved as historical results, not rerun or relabelled as new samples. No current TeX, Overleaf content or credentials are changed.
