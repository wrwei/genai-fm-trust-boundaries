# Formal artefacts for the bridge example

Read [PROVENANCE.md](PROVENANCE.md) before interpreting any result. The active
paper compares selected **obligations**, not the inherent capabilities of tools.

**13 September 2026:** the independent [CKA repair session](cka-repair/README.md)
now checks two elementary lemmas and a concrete projection/interleaving
theorem in Isabelle2025-2, with dependency checks and recorded logs. It does
not import or discharge the admitted legacy Bridge theories. The active
manuscript is unchanged; proposed wording is kept in an independent draft.

The subsequent [runtime-interface study](cka-repair/runtime-interface/README.md)
adds a checked executable protocol, operational-to-trace proofs, conditional
progress and generated-SML mutation checks. Its atomicity and input-provenance
assumptions are explicit; it is not a deployed bridge implementation.

The [SQLite case](cka-repair/runtime-interface/sqlite-runtime/README.md) now
exercises those boundaries through loopback HTTP and same-database effects:
128 model-table comparisons, five abrupt-process-exit recovery points and
three detected implementation mutations. This is empirical implementation
evidence, not a proved Python/SQL refinement or remote exactly-once result.

- `dafny/BridgeController.dfy`: C0 contracts and two deliberately failing mutations.
- `csp/bridge.csp`: occupancy and composition assertions; no completed run recorded.
- `isabelle/Bridge_Progress.thy`: proposed progress statements with admitted proofs.
- `isabelle/Bridge_CKA.thy`: proposed algebraic statements with axioms and admitted proofs.
- `lean/Bridge.lean`: grant-preservation witness and coverage calculations; three open theorems.
- `../paper/figures/bridge_model.py`: bounded enumeration underlying the paper's matrix and counts.

The names `fairness`, `cka_holds` and `control_live` in legacy artefacts are
explained precisely in the provenance file. They must not be read as unbounded
scheduler-fairness, algebraic-composition or eventual-progress proofs.

One capable verifier could express all four selected properties. Stronger
local contracts could detect both grant-consumption and grant-overwriting
errors. Multiple notations alone do not establish complementary guarantees or
semantic equivalence.
