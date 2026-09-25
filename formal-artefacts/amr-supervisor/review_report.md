# Independent supervisor review

Reviewed 2026-09-15. The initial pass covered `language.py`, `model.py`, `assurance.py`, their supplied test source, the candidate index and reference fixture, and the frozen supervisor plan. A second pass covers the v1.1 revision, `closed_loop.py`, `run_supervisor_suite.py`, the archived v1 development failure, and integration test source. Final v1.1 episode outputs were not yet available for this pass.

## Findings

**Low priority: malformed Unicode escapes the assessment report.** `assess_source` computes `text.encode('utf-8')` for the initial source hash before entering its parser exception handler. The public parser deliberately turns invalid Unicode into `ValueError`, but the assessment wrapper never reaches it for a lone surrogate. Reproduction using the actual module: `assess_source(chr(0xd800))` raises `UnicodeEncodeError`; it does not return `parse_pass=False`. Validate text/encoding before constructing the hash, and provide an explicitly unavailable source hash for strings that cannot represent UTF-8 source. This is an input-reporting robustness issue, not a route to acceptance. Ordinary strict UTF-8 file reads cannot produce this input.

**Resolved in second pass:** the same probe now returns `parse_pass=False`, `source_sha256=None`, and a clear UTF-8 parse error. `SourceSupervisor` also safely stringifies the unavailable hash in its rejection message. Non-string inputs receive a structured rejection.

**Low priority identity cleanup:** `HandwrittenSupervisor.identity` still identifies `handwritten-obligation-reference/v1`, although the reference now delegates to v1.1 obligations. Update this event identity before freezing the final run. Actual executed Python files are independently hashed by the runner, so this is a label ambiguity rather than an untracked implementation change.

**Resolved in final-code pass:** the handwritten event identity is now `handwritten-obligation-reference/v1.1`.

No critical acceptance or source-to-target correspondence defect was found in this scope.

## Independent checks and interpretation

- Reviewed the recursive source interpreter against postfix compilation and stack execution. The model executes independently of source evaluation; both intentionally share the parsed immutable syntax and vocabulary, so this is algorithmic independence rather than independently proved parsing or specification adequacy.
- Correct compilation uses each earlier raw condition's negation, preserving first-match behavior. Omitting these negations creates an enabled-output relation. Comparing sets appropriately treats duplicate equal outcomes as the same relation value.
- The complete finite input count is 2^5 + 7 × 2^8 = 1,824. Mode predicates are derived internally from exactly one current mode. The domain includes inconsistent or unreachable physical combinations and is correctly described as an abstract enumeration domain.
- Selection obligations permit either requested robot when ownership is free and both request. Thus `choose_b_when_both` can preserve each side's policy compliance while violating behavior correspondence. Requiring raw-source obligations, model obligations, and correspondence together preserves this distinction.
- Step obligations implement the plan's exact precedence and next modes. They are stronger than a set of generic safety properties: most step valuations prescribe one exact response. Their finite satisfaction does not establish liveness or physical safety outside a justified abstraction.
- Verified all eight indexed fixture byte hashes against their current files. Provenance consistently labels them assistant-authored deterministic mechanism fixtures, not independently sampled LLM trials.
- Ran an additional fixed-seed probe, without rerunning the full supplied suite: 100 generated ordered eight-rule programs with nested `not`/`and`/`or` expressions × all 32 selection valuations. All 3,200 source/target comparisons agreed.
- Reproduced the malformed-Unicode issue above. No implementation files were changed during review.

The existing report of 22 passing tests comes from the implementation stage; this review inspected those test cases but did not rerun the entire suite. The additional checks here are executable evidence, not a correctness theorem.

## Integration and specification revision review

No blocking integration defect was found in the reviewed v1.1 source. Acceptance precedes plant construction and event emission. The deployed supervisor calls the source evaluator, never the extracted model. Raw source actions drive request registration, selection and grants, successful manager release, next modes, the delayed actuator intent, and logical completion. Runtime obligation checks retain raw responses and record rejections separately from their braking fallback. Release clearance and completion observations are checked before application; final independent physical scoring can reject a logical completion.

The source and handwritten arms share the same scenario, delayed observation/command clocks, plant, reservation manager, and independent interval/completion oracle. The handwritten step policy directly calls the obligation function. It is therefore a calibration baseline for the same contract, not an independent specification-adequacy validator or evidence that generated control outperforms a separately designed controller.

The runner is configured for five paired scenarios (10 episodes) plus one equivalent-syntax nominal episode. It separately writes nine raw candidate assessments, three injected translator-fault checks, target models, events/continuous traces, and input/output hashes. It checks code and fixture stability across the run. The physical parameter file is indirectly pinned by the unchanged baseline `parameters()` loader's enforced SHA-256. The archived v1 failure is separately counted and is not added to final v1.1 episodes.

The goal-stop specification gap is substantive and correctly classified. Independently inspected archived evidence shows: v1 acceptance across 1,824 inputs, correspondence passing, a 120-second horizon, no runtime rejections, both physical robots at their goals, and neither logical robot completed. All late goal step actions are `Proceed` while `Halted=False`. This follows from the original contract never requesting goal braking, whereas the interface establishes Halted only from sustained delivered Brake. The v1.1 goal-braking obligation resolves that interface gap explicitly; it does not weaken Halted or relabel correspondence checking as a liveness proof.

Verified every archived Python-code hash, the archived result and compressed trace hashes, and all recorded baseline Python hashes. Verified all nine current candidate hashes; `goal_stop_gap.json` is byte-identical to the archived v1 source. The preserved reproduction wrapper selects the archived semantics and original physical modules. This review inspected the archived evidence instead of spending another full physical rerun on the already demonstrated failure.

Final acceptance of run evidence still requires checking the completed v1.1 output manifest, outcomes, and traces. The present review confirms the code path and archive, not results that have not been produced yet.

## Final-code follow-up

Reviewed the new `pedestrian_stopping_evidence` helper, its four focused test cases, and its runtime call site. Applicability now requires an observed heading along the robot's intended corridor direction, an observed pose on the straight narrow-corridor centerline, and an observed footprint before the pedestrian strip. World-x footprint extent accounts for orientation. Turning, off-center, outside-corridor, reversed-heading, and past-strip cases yield an explicit reason and `straight_approach_condition=None`; they cannot be reported as satisfying the scalar straight-stopping calculation. The call site records these values without changing control, actuator timing, or the pedestrian schedule. Only an applicable calculation with an insufficient gap enters the distance-condition violation list.

This is an observed-geometry diagnostic, not a proof of actual physical alignment under observation error. The helper docstring and README state that boundary. The README also correctly distinguishes the common-contract handwritten calibration, the nine authored fixtures, the 11 planned physical episodes, the archived development specification failure, and the absence of independent LLM sampling or new formal proofs. No additional blocking finding arose in this scoped follow-up. Existing focused tests were inspected; no full-suite rerun was performed by the reviewer.

## Final evidence verdict

Final outputs are now available; this closes the pending evidence review above. Independently checked the research results document and README against the final summary, manifest, episode records, and preserved v1 failure. No outstanding blocking finding or numerical discrepancy was found. All 46 recorded output hashes and all current recorded input hashes match; the before/after input maps agree. The test log records 34 passing tests. No tests or physical episodes were rerun in this final review.

Confirmed nine fixtures: two accepted, six semantic rejections with source/model violation counts 187, 187, 42, 28, 374, and 25, plus one parse rejection. Correct extraction has zero correspondence mismatches. The three injected faults produce 1,749, 3, and 374 mismatches with exactly the reported separate policy outcomes; all three are rejected.

Confirmed all 11 physical episodes and five matched source/handwritten pairs. Paired end times are 58.95, 58.95, 65.90, 63.85, and 120.00 seconds, with equal outcomes and zero time differences. The first four settings complete both robots; permanent blockage completes neither and is not marked successful. The equivalent program completes at 58.95 seconds. Collision, unresolved-interval, early-release, runtime-rejection, and completion-mismatch lists are empty in every episode. The temporary-person source event at 10.05 seconds is explicitly outside the straight-approach domain and has a null condition. Documentation accurately preserves the distinction between finite mechanism checks, simulation evidence, the archived authored-specification failure, and experiments or proofs that have not been performed.
