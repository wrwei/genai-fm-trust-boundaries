# AMR advisory v2: source, authority and progress

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see repository directory formal-artefacts/record-maintenance-2026-09-22. Raw replies, controller source bytes and physical trajectories are retained.

Completed bounded experiment, 21 September 2026. The industrial scenario is two AMRs, one transport task each, a shared corridor and a pedestrian crossing. This package implements the [approved design](../../literature/scholar_search_2026-09-10/followup/research_amr_case_redesign_2026-09-21.md). Read the [results and claim coverage](../../literature/scholar_search_2026-09-10/followup/research_amr_v2_results_2026-09-21.md) for interpretation.

The generated restricted source makes the final selection and motion-policy decisions. A runtime LLM supplies only typed A/B advisory data. Trusted local protocol steps recheck current permission at reservation commit and command application. Physical predicates have separate geometry evidence.

## Evidence entry points

| Evidence | Result | Entry |
|---|---|---|
| Frozen requirements | Fixed one-time registration A before B; useful advice followed, otherwise source-driven FIFO | [contract](contract.md) |
| All historical sources | Six responses / five unique sources; all satisfy old policy, only P3-R1 satisfies v2 | [source summary](evidence/source/summary.json), [source review](source-review.md) |
| E1 source/model contrast | Faulty model passes all 1,824 v2 inputs; same source fails one; correspondence detects one mismatch | [source summary](evidence/source/summary.json) |
| Discrete protocol / CKA-oriented reuse | Operational decomposition, independent-reference authority and conditional authorization proved in Isabelle | [formal scope](hol/README.md), [build](hol/build.log), [independent review](formal-review.md) |
| Finite implementation link | 11,664 core transitions and 1,296 source-selector rows match HOL exports | [final conformance](evidence/conformance-final.json) |
| Runtime mechanisms | Separate Commit/Apply faults; nonblocking A/B/FIFO controls; no-advice waiting fault | [mechanism results](evidence/mechanisms/results.json), [runtime review](runtime-review.md) |
| Physical contrasts | All 15 expected outcomes retained, including deliberately failing variants | [batch summary](evidence/physical/20260921T144921Z/summary.json), [independent audit](evidence/physical-audit.json), [review](physical-review.md) |
| Real advice | Six bounded requests; all B replies timely and adopted by original source | [raw batch](evidence/advice/summary.json), [offline audit](evidence/advice-audit.json), [review](advice-review.md) |

Selected source SHA-256: `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`. The first passing distinct source was selected in predeclared historical order; neither its bytes nor earlier acceptance claims were changed. v2 is a stronger functional contract, not a correction of the historical optional-preference contract.

## Offline reproduction

Python uses the standard library. From the repository root (substitute the installed Python executable on Windows):

```text
python -B -m unittest discover -s formal-artefacts/amr-advisory-v2/tests -v
python -B formal-artefacts/amr-advisory-v2/source_check.py --output <new-empty-source-directory>
python -B formal-artefacts/amr-advisory-v2/conformance.py --output <new-conformance-file.json>
python -B formal-artefacts/amr-advisory-v2/run_mechanisms.py --output <new-mechanisms-file.json>
python -B formal-artefacts/amr-advisory-v2/advice-audit.py --output <new-advice-audit-file.json>
```

`physical-audit.py` audits the retained physical batch and writes `evidence/physical-audit.json`; its output is deterministic. `run_physical.py` creates a newly timestamped 15-run batch and updates `evidence/physical/latest.json`. These are different operations: use the audit to inspect retained evidence, and a new batch only when re-execution is wanted. Full physical tests take about 80 seconds on the recorded host. Isabelle reproduction requires the pinned runtime described in [hol/README.md](hol/README.md); building refreshes its log, source manifest and exports.

The live batch is complete and has irreversible dispatch markers. The runner refuses to dispatch it again. Reading evidence and running tests/audits requires no API credential or network. A new live batch is not part of offline reproduction.

## What is established, and what remains outside scope

- Isabelle proves the finite operational model's authority bound and a source-restricted authorization result within at most three supplied Service opportunities, allowing arbitrary finite benign gaps and arbitrary advice, including none. This is not unrestricted scheduling, infinite fairness, or physical transport completion.
- CKA-oriented reuse instantiates the existing finite interleaving-language `authority_boundary_traces` theorem with independently defined components and an operational embedding. It is not a complete CKA algebra instance or a measured advantage over direct state-machine verification.
- Removing provider silence is covered by the imported, already checked [`controlled_advice_counterexample`](../cka-repair/Bridge_Trace_Repair.thy): a provider-only controlled token extends the empty trusted language's visible projection. Map its Boolean `True` to a controlled action token. This is an inherited finite-language premise counterexample, not a new AMR physical bypass run. E4 supplies the separate no-progress witness.
- Source/core exhaustive finite comparisons are translation-validation evidence. The parser, complete Python mailbox/driver, continuous plant refinement, dynamic arrivals and distributed revocation are not proved.
- Constructed E1–E4 faults demonstrate distinct missing obligations. They are not estimates of natural LLM failure rates. Fifteen expected physical outcomes includes premature-release and stale-permission violations; it does not mean fifteen safe runs.
- The real calls demonstrate replies during a paced deterministic approach to halted staging and source-driven authorization. Decision records followed the 3.63 s cutoff by 0.104–0.120 s. This does not validate the physical monitor's compute bound or a full real-time robot stack.
- Physical B2 blockage begins near zero speed; the separate 1 m/s fixed-boundary braking pair supplies the stated braking calibration. The effective delay bound is explicitly corrected to 0.10 s, total reaction to 0.27 s; inherited unused stress labels are not executed boundary tests.
- The physical batch's original pre-run hash list omitted some transitive code. The final manifest binds the current complete package and supporting code, and independent replay checks consequences, but neither retroactively supplies missing pre-run provenance. Historical manifests remain unchanged.

`evidence-manifest.json` is the final postflight SHA-256 inventory, excluding itself and caches. `evidence/final-verification.json` records the final checks. The active TeX and Overleaf branch are unchanged; the existing [integration candidate](../../literature/scholar_search_2026-09-10/followup/review_integration_2026-09-15.md) contains the single new case excerpt.
