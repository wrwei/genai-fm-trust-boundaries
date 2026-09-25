# Restricted source language verification

Implemented `language.py` and `tests/test_language.py` against the fixed supervisor plan dated 2026-09-15. No existing reference files were edited by this task.

Command (working directory `formal-artefacts/amr-supervisor`):

```powershell
& 'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest discover -s tests -p test_language.py -v
```

TDD record: before implementation, all eight test groups failed with the explicit assertion `restricted language implementation is missing` (exit 1). After implementation, all eight passed (exit 0; 0.002 seconds on the recorded run). Test groups exercise ordered selection and Boolean precedence, non-total programs, internal mode derivation, exact facts, forbidden syntax, malformed JSON/schema/enums, resource limits, and immutable parsed structures.

## Public contract

- `parse_program(text: str) -> Program`: frozen `Program(schema, select, step)` containing tuples of frozen `Rule(condition, action, next_mode)` values. Selection rules have `next_mode=None`.
- Expressions are recursively immutable tuples: `('const', bool)`, `('var', name)`, `('not', expr)`, `('and', expr, ...)`, or `('or', expr, ...)`.
- `eval_select(program, facts) -> str` and `eval_step(program, mode, facts) -> (action, next_mode)` evaluate the first matching rule.
- Both fact interfaces require their exact exported key sets and `type(value) is bool`. Step mode predicates are named `ModeIdle`, `ModeWaiting`, `ModeTraversing`, `ModeBrakeRequested`, `ModeStopped`, `ModeResumePending`, and `ModeDone`; they are generated from the validated mode, never accepted as external facts.
- Invalid syntax, schema, enums, fact inputs, modes, limits, and uncovered inputs raise `ValueError`. Missing defaults and empty rule lists are structurally allowed; totality belongs to finite assurance.

## Boundaries

JSON is limited to 200 × 1024 UTF-8 bytes. Duplicate keys, nonstandard JSON constants, extra/missing fields, and invalid rule types are rejected. Each function has at most eight branches; the separate total cap is 32, currently redundant under the two-function layout.

Expression source length is at most 512 characters; parsed Python AST size is at most 64 nodes (including AST helper nodes). Semantic expression depth counts the root expression as one and is limited to eight; redundant parentheses are erased by the Python parser. `ast.parse` is used only for syntax, followed by explicit node/name whitelisting and conversion to tuples. There is no Python `eval`, compilation, call, attribute, comparison, arithmetic, or mutable parsed expression.

The interpreter consumes a `Program` obtained from this parser. Python code in the trusted host can instantiate dataclasses directly and is outside the untrusted JSON boundary. Frozen dataclasses protect ordinary mutation, not hostile host Python using reflective escape hatches. Source hashing and deployment identity belong to the caller, not `Program`.

These tests establish executable examples and regression checks, not a parsing proof, completeness proof, or reachability claim. Independent target semantics, safety obligations, finite correspondence, and physical execution are separate modules.

## Review fix R1: assessment input boundary

Review found that `assess_source(chr(0xd800))` attempted UTF-8 hashing before protected parsing and raised `UnicodeEncodeError`. Added regressions before the fix: malformed Unicode produced that error and four non-string inputs produced `AttributeError` (nine test methods run, five errors). Assessment now initializes `source_sha256` to null, validates string type and UTF-8 encoding inside its parse-failure boundary, and hashes only actual valid UTF-8 bytes. Malformed Unicode and non-string inputs return `parse_pass=False`, `accepted=False`, `checked_inputs=0`, a diagnostic, and no fabricated digest. Valid UTF-8 source retains its original-byte digest even if its JSON or program syntax is rejected.

An additional boundary regression confirms an empty step list is parse-valid but non-total: all 1,824 inputs are checked, with 1,792 source violations, model violations, and correspondence mismatches. This case passed before the fix and needed no behavior change. After the focused fix, `python -m unittest discover -s tests -p test_assurance.py -v` passed all nine test methods. The only production change was assessment hash/input validation; obligation and correspondence logic were untouched.

## Integration evidence label: straight stopping scope

Added `pedestrian_stopping_evidence(obs, name, now, p)` in the new closed-loop module. It computes the observed footprint's world-x half-extent as `(length*abs(cos(heading)) + width*abs(sin(heading)))/2`. The distance comparison applies only when the observed heading is forward along N (A: 0, B: pi, wrapped angular tolerance 1e-9), the observed center lies on N's centerline and within N's x interval, and the observed footprint is before H. This is an observed geometric scope check, not a proof of physical alignment under pose uncertainty.

Events retain observed pose, speed, sample time, footprint extent, and distance. Outside this scope, `straight_approach_applicable=False`, `straight_approach_condition=None`, `required_distance=None`, and `scope_reason` explains why. Only applicable but insufficient distance enters `assumption_violated`; outside-scope events make no positive stopping-lemma claim. The fixed pedestrian onset, plant, controller decisions, and command delivery behavior were not changed.

Regression fixtures include the diagnosed 45-degree approach at `(7.98524, -0.01476, pi/4)` and speed `0.18274`, aligned A/B clear approaches, an aligned insufficient gap, wrong heading, off-center pose, and poses outside the straight/before-H domain. Red: four test methods produced eight expected missing-helper assertion failures. Green: all four methods passed with `python -m unittest discover -s tests -p test_closed_loop.py -k PedestrianEvidenceTests -v` (0.002 seconds). Full episode suite regeneration is delegated to the parent integration task.
