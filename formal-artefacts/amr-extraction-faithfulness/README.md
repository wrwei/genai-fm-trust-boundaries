# AMR extraction faithfulness — 22 September 2026

This additive package proves preservation for the Boolean source/target structure actually used by the AMR rules12 extractor, then binds that theorem to the retained controllers. It leaves the parser, compiler, acceptance policy, deployed source and previous runtime evidence unchanged.

Design: [scope and evidence gap](../../docs/superpowers/specs/2026-09-22-amr-extraction-faithfulness-design.md). Results: [Chinese report](../../literature/scholar_search_2026-09-10/followup/research_amr_extraction_results_2026-09-22.md).

## What is proved

[AMR_Extraction.thy](hol/AMR_Extraction.thy) imports only Main. It defines pure Boolean expressions, first-match source rules, an independent postfix stack machine, the existing trailing-NOT cancellation, and guards conjoined with all earlier raw guards' negations in their original order. The suppression step appends NOT/AND 2 without applying the NOT optimization, matching the actual Python extractor.

`compile_correct` quantifies over every expression, total Boolean environment and initial stack: compiled execution pushes precisely the source value and preserves the original stack. `extraction_preserves` quantifies over every finite rule list and environment:

```text
target_results env (extract_rules rules)
  = result_list (source_result env rules)
```

Target results remain a list, so the proof does not hide extra enabled outputs by deduplication. Action and next-mode payloads are preserved. `property_lifting` transfers output properties; `total_property_lifting` additionally requires a nonempty target result. Preservation alone does not establish totality or correct requirements. Three groups of constructed witnesses expose omitted priority, a missing negation, and the uncovered case; they are not sampled model errors.

## Connection to the existing implementation

`snapshot.py` reads all six retained original responses, checks their SHA-256 identities, deduplicates only byte-identical programs and exports the parsed AST and **actual Python-extracted instruction lists separately**. The [snapshot](evidence/snapshot.json) records all five identities, vocabulary encodings, frontend dependencies and the selected deployment identity. It cross-checks that identity against the already tested runtime adapter.

[AMR_Artifacts.thy](hol/AMR_Artifacts.thy) contains ten kernel-checked equations (five sources × select/step) equating these actual target structures with the formal extractor. Ten corollaries instantiate preservation for arbitrary environments. Nineteen fixed expression structures also bind actual compiler output, including NOT cancellation and n-ary boundaries; 152 paired evaluations (19 × eight environments) bind both original Python expression evaluators to HOL results. Thirteen structures are within the parser syntax; six are constructor-only zero/unary-operator boundaries.

The Isabelle2025-2 [build](hol/build.log) succeeds. Both [general](hol/export/AMR_Extraction_Faithfulness.AMR_Extraction/proof-audit.txt) and [concrete](hol/export/AMR_Extraction_Faithfulness.AMR_Artifacts/artifact-audit.txt) audits reject skipped proofs and oracle dependencies. All concrete equations use `code_simp`, with proof checking rather than an unchecked evaluation oracle.

[Independent review](review.md) found no unresolved issues. It reverse-parsed all 20 source/target HOL definitions and checked 65 source rules, original identities and hashes independently of the exporter. Five exporter behavior tests pass. [Snapshot verification](evidence/verification.json) also confirms all 36 entries of the previous runtime evidence package remain unchanged.

## Important distinctions

- The theorem is about the explicitly modeled profile. The Python parser and exporter are engineering links with hashes, tests and review, not mechanically verified translators from raw JSON to HOL.
- HOL `None` represents the source's specific no-matching-rule exception; Python `eval_select`/`eval_step` do not return None. Other exceptions must propagate. The previous acceptance checker still rejects uncovered programs. No rejection is changed into acceptance.
- HOL represents the top of the stack at its head; Python represents it at the end. The connection covers well-formed generated code. HOL rejects operand underflow, whereas Python's AND/OR slicing can tolerate it; no arbitrary malformed-bytecode equivalence is claimed.
- Environments are total and Boolean, and guards have no side effects. Consequently source short circuiting and target eager evaluation have the same modeled value. No claim extends to arithmetic, exceptions in atom evaluation, shared mutable state or unrestricted Java.
- A per-decision payload theorem does not itself establish the physical meaning of facts, the effects of actions, timing or mission completion. These remain linked through the previous scoped runtime proofs, conformance checks and execution audits.
- Five structurally faithful extracted programs do not mean five v2-accepted controllers. The previous 1/6 strengthened-contract result is unchanged. No new LLM calls or physical runs were performed.

## Replay

Using the bundled Python executable with `-B` from this directory:

```powershell
python -B -m unittest discover -s tests -v
python -B verify_snapshot.py
python -B hol/build.py
```

`snapshot.py` regenerates the concrete snapshot and theory from the current named dependencies; use `verify_snapshot.py` first to detect drift. Build attempts are preserved in `hol/build-attempts/`. A successful build writes the exact proof-source hashes; deterministic snapshot revalidation and previous-package integrity are recorded separately in [verification.json](evidence/verification.json).
