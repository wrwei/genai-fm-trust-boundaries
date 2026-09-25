# Independent protocol and prompt review

Date: 2026-09-15. Scope: preparation only. This review used no network, external model, experimental sampling, subagents, commits, or changes to the existing AMR implementation/results.

Reviewed `protocol-review-package.diff` (protocol JSON, common interface, P1/P2/P3, repair template and research protocol), the preparation plan, and the actual sibling `amr-supervisor/assurance.py` and `language.py`. The recorder implementation, generated request assembly, manifest completeness and runtime enforcement are outside this review and require their separate checks. This verdict concerns the reviewed package; later material edits require review again.

## Specification verdict: PASS within the authored v1.1 domain

No material specification mismatch found.

- All three policy presentations express the same ordered step requirements as `obligation`: invalid/blocked/inactive handling; released-goal braking or completion; owned-and-clear release; unfinished braking; reservation request; restart from Stopped; otherwise Proceed. Each required action and next mode agrees. In particular, release precedes unfinished braking, goal completion requires Halted, and Done does not bypass any requirement.
- The common interface explicitly includes all 32 select valuations and all 1,792 step valuations, with one-hot mode flags and no assumed physical relationships among other facts. The prose covers inconsistent-looking states rather than silently restricting the acceptance domain.
- Selection legality and required progress exactly match `selection_violations`. When ownership is unavailable or no request exists, Defer is the only legal result. When available requests exist, an eligible robot must be selected. Either robot remains legal when both request; PreferA/PreferB introduce no correctness obligation.
- Schema, rule keys, allowed expressions/names, action/mode sets, first-match interpretation, duplicate-key rejection and numeric source/expression/rule limits agree with `language.py`. The total 32-branch ceiling is redundant under two eight-rule functions, but is correctly stated alongside the tighter per-function ceiling.
- Eight step rules are feasible despite a naive expansion yielding nine cases. A local reviewer-authored construction combined conditions with the same Brake/BrakeRequested output while retaining the required priority. It was assessed in memory only, was not added to prompts or saved as a generated candidate, and is not model evidence.

Bounded probe evidence, using the unchanged assessor: 8 step rules and 3 selection rules parsed and were accepted across 1,824 inputs (32 select, 1,792 step), with zero source violations, model violations or correspondence mismatches. An independently transcribed dispatcher procedure matched `obligation` on all 1,792 step valuations, and its selection allowed-action sets matched the checker on all 32 selection valuations. These probes support expressibility and the manual prose interpretation; they do not mechanically prove equivalence of arbitrary natural-language readings or adequacy of the specification.

## Research/quality verdict: PASS for preparation, not authorization to sample

No material protocol or provenance finding found in the reviewed text.

- The sample unit is unambiguous: one complete obligation package, three prose variants, two initial candidates per variant, six initial chains. At most two repairs per chain gives 18 response attempts, not 18 independent samples. The earlier six-package/36-initial design and runtime natural-language advice remain explicitly unfinished.
- The protocol separates planned coverage, actual initial responses, repair attempts and terminal/pending states. It preserves rejected outputs, parsing and encoding failures rather than removing them from candidate accounting. Stage-specific failure counts may overlap and are not summed as distinct candidates. With zero actual candidates, rates must remain uncomputed, consistent with the no-sampling preparation stage.
- Repair context is limited to the original requirements, immediately preceding raw response and actual capped checker feedback. The supplied template warns that witness coverage is incomplete. The reviewed prompt package exposes neither reference controller source nor an expected-action table. Violation labels and correspondence observations intentionally convey diagnostic information; this is the declared feedback intervention, not an undisclosed source of additional training examples.
- Fresh initial contexts, identical prompt bytes within a variant, fixed chain order, no retries after infrastructure/response-status failures and termination upon acceptance reduce discretionary sampling. Actual independence and external-client isolation are not established by these text rules, and the protocol appropriately states the operator/service limitations.
- Output identity, configuration and byte hashes are described as recorded provenance rather than independent authentication. The recorder's inability to enforce external calls or prove service behavior is disclosed. Preparation remains explicitly unbound and true model samples remain zero.
- The closed-loop candidate is chosen only after all chains terminate, by fixed sample-ID order, without inspecting simulation performance. Frozen paired scenarios are described as calibration and observation; legal selection differences are not automatically failures. The text does not claim industrial reliability, performance superiority, statistical significance or completion of the broader study.

## Handoff conditions

No prompt/protocol changes are required by this review. Before declaring the whole preparation complete, the coordinator still needs the separate recorder review/tests, deterministic six-prompt assembly check, final manifest/ledger validation and protected historical-file checks required by the preparation plan.
