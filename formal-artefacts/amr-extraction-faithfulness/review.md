# Independent extraction review — 2026-09-22

Reviewer: independent `review_extraction` agent. Read-only review of the implementation and evidence; this report is the only file written by the reviewer. No API requests, credential access, historical physical reruns, or changes to the original rules12 implementation.

## Assessment

Ready to use for the stated restricted semantic-preservation claim. No critical or important correctness finding remains. The earlier no-match ambiguity has been resolved in the design: HOL `None` represents only the two explicit Python no-matching exceptions, and does not mean the old acceptance checker accepts an uncovered controller.

The reviewed generic theorem is about the HOL compiler and extractor. The concrete artifact equalities and engineering checks connect the retained examples to that theorem. They are not a general mechanized correctness proof of the Python parser, compiler, evaluator, exporter, or runtime adapter.

## Semantic review

- `AMR_Extraction.thy:41`: `negate_correct` has a sufficient premise. A successful result `Some (b # rest)` guarantees a Boolean top. For a trailing `Neg`, `run_append` and `instruction_neg_inverse` recover the preceding result `Some ((not b) # rest)`; otherwise the appended `Neg` produces it. The lemma also correctly covers empty code executed on a nonempty initial stack. No additional compilation or stack-frame premise is needed for this generic lemma.
- `compile_correct` proves the stronger required frame property for every expression and every initial Boolean stack. Nested n-ary compilation pushes operands in reverse order in the head-stack representation; conjunction and disjunction are invariant under that reversal. Zero-arity operations leave the old stack intact and push the correct Boolean identity. `compile_nonempty` supports Python's access to `code[-1]` on valid compiled expressions.
- `priority` uses earlier original expressions in oldest-first order, appending their compiled code followed by unoptimized `Neg, Conj 2`. It does not optimize these priority negations or reuse already-masked guards. This matches `model.py:60-71`, including consecutive `NOT` instructions after an earlier negative condition.
- `target_results` is a list of every enabled payload, preserving order and multiplicity. `extraction_preserves` proves equality with a zero/one-element source observation; it does not conceal repeated enabled actions through set conversion. Payloads retain both action and optional next mode.
- `property_lifting` requires a successful source outcome. `total_property_lifting` separately requires nonempty target output. Neither theorem derives input coverage, policy adequacy, termination, or physical safety from semantic preservation alone.
- The strict HOL underflow semantics differs from Python slicing on malformed `AND`/`OR` code. The documented generated-code restriction is adequate: the compiler theorem and priority construction establish successful stack execution for that domain.

## Independent checks performed

1. Ran `python -B -m unittest discover -s formal-artefacts/amr-extraction-faithfulness/tests -v`: all 5 tests passed.
2. Recomputed all 21 snapshot input hashes and all 4 successful-build source hashes; all matched. Separately verified the generated-theory hash stored in `snapshot.json`.
3. Independently tokenized and decoded all 20 HOL source/target definitions, without using `expr_term`, `code_term`, or `output_term` to decode them. Every AST, instruction sequence, action, next mode, and list position matched the persisted snapshot. This covered 5 identities and 65 source rules. Fact, action, and mode encodings were injective for the frozen vocabularies.
4. Independently parsed all 6 raw response byte files through JSON and Python AST syntax and compared the resulting conditions and payloads to the saved source ASTs. All matched; there are 5 distinct byte identities. The selected identity is `9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`, matching the selected raw file and runtime `SOURCE_ID`.
5. Compared a fresh `collect()` result with the persisted snapshot and fresh `theory()` text with the saved theory. Both comparisons matched. The 19 expression probes each have 8 environments and observations from both actual Python interpreters; the generated HOL theory checks source and target values separately as well as exact compilation.
6. Independently exercised select and step no-match behavior with both empty rules and a false guard (4 cases), and checked that 3 unrelated validation failures propagate. Checked that omitted priority exposes two identical target outputs, while normal extraction exposes one. Checked the exact double-`NOT` priority sequence.
7. As a supplementary adversarial check, an independently written strict head-stack interpreter enumerated all instruction sequences of length at most 4 over 10 small instructions, 7 initial stacks, and 2 environments. All 119,854 cases satisfying the successful-nonempty-result premise satisfied the negation property. This is a bounded review check, not a new theorem or an LLM sample count.
8. Inspected the successful Isabelle2025-2 build log ending at 2026-09-22 19:51:43 GMT+8 and matched its recorded source hashes to current files. The proof audit lists 15 abstract theorem propositions, and the artifact audit lists 77 concrete entries: 10 structural bindings, 10 preservation corollaries, and 19 triples of compiler/source-value/target-value lemmas. Both dependency audits reject skipped proofs and oracle dependencies. The reviewer inspected this completed build and its exports; it did not launch a redundant Isabelle build.

9. Reviewed the subsequently added `verify_snapshot.py`, its saved successful report, `README.md`, and the Chinese results note. The checker compares the saved snapshot and theory against deterministic regeneration, verifies proof-source hashes, checks expected concrete audit groups, and checks all 36 prior-runtime manifest entries. The README and Chinese note accurately distinguish universal HOL results, concrete implementation links, finite probes, prior runtime evidence, and remaining obligations.

## Findings

No outstanding critical, important, or minor finding. An initial maintainability suggestion was to add saved-evidence freshness checks beyond the unit tests; the subsequently added `verify_snapshot.py` addresses it. Its persisted checks also agree with the independent snapshot/theory/hash comparisons performed above.

## Claim boundary

May state: an Isabelle/HOL semantic-preservation theorem for this pure Boolean expression language, optimized postfix compilation, ordered priority elimination, and explicit no-match observation; exact concrete compiler/AST/target bindings for the five retained identities; a checked selected-byte identity link to the existing runtime-bound controller; and the separately checked finite expression boundaries.

May not state: a mechanically proved JSON-to-HOL parser, a general refinement proof of all Python implementation code, arbitrary malformed-bytecode interpreter equivalence, acceptance or totality of every source program, complete Java-profile correctness, a new physical-runtime guarantee, mission termination, or a statistical claim about model-generated extraction faults. `incorrect_negation_witness` is a constructed wrong-negation observation, not evidence that a real compiler emitted that fault.

## Reviewed file identities

- `hol/AMR_Extraction.thy`: `b6a9f64cd57c9faac26407a34af30f0e660cff4ebcbfad163f2dead7356e03bc`
- `hol/AMR_Artifacts.thy`: `1c00caa30023d7e7f4949278c1d85e15fafc50d0d9a1d77a1d180e403bad81b6`
- `snapshot.py`: `e5a382815644bfba976718f83eb7ae30e29a76bd39ee00312a69854f00a63518`
- `tests/test_snapshot.py`: `450bc4149bee6115edf0a1529e197279550ced1e5f6da948424bf45f26189d14`
- `evidence/snapshot.json`: `73ce7b148de5495339a09100e70139f75e7752ef7001ced5025adb77e10e97e2`
