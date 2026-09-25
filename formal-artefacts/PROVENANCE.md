# Evidence status for the revised bridge example

Recorded runs: 9 and 13 September 2026; updated 13 September 2026.
This file supersedes the earlier claims that the
example demonstrated inherent limitations of particular verification tools.
The active manuscript is `paper/main.tex`; the comparison is between selected
obligation sets. Several older section files are retained but not included.

| Evidence | Observed status | What it establishes |
| --- | --- | --- |
| `paper/figures/bridge_model.py` | Rerun successfully on 2026-09-09 | Exhaustive enumeration **within stated trace bounds**, including the matrix and 65/13/1 counts |
| `dafny/BridgeController.dfy` | Dafny 4.11.0, Z3 4.15.4: 27 verified, two expected postcondition failures, exit 4 | C0 obligations and deliberately failing C1/C2 methods; no C3/C4 methods are present |
| `lean/Bridge.lean` | Lean 4.33.1: exit 0, three `sorry` warnings | A reachable C4 grant-overwriting witness; finite coverage calculations over explicitly supplied acceptance sets |
| `csp/bridge.csp` | No completed verification run recorded here | Input artefact only; no FDR result is claimed |
| `isabelle/Bridge_Progress.thy` | 13 September legacy-session attempt stopped after the proof at line 153 ran for about 125 seconds; exit 1; six bare `sorry` steps remain | Proposed obligations, not a closed progress proof; interruption is not a counterexample |
| `isabelle/Bridge_CKA.thy` | The legacy-session attempt did not complete; four bare `sorry` steps and explicit axiomatization remain | Proposed algebraic development; not a proved general composition theorem |
| `cka-repair/Bridge_Algebra_Repair.thy` | Isabelle2025-2 build passed, exit 0; no admitted/oracle dependencies in the two checked lemmas | Subidentity multiplication is contracting; projected zero bound follows from monotonicity, without zero-preserving projection |
| `cka-repair/Bridge_Trace_Repair.thy` | Same independent session passed; dependency checks include the main theorem and auxiliary results | Conditional inclusion for arbitrary finite interleavings under event erasure and a contracting trace selector; equality needs a separate retention premise |
| `cka-repair/runtime-interface/Runtime_Interface.thy` | Isabelle2025-2 child session passed, including SML export checking; generated SML executed over all 128 transitions per kernel | A single-operation protocol simulates the reference machine, retains projected behaviours and commits at most once; progress requires retained permission and explicit service supply |
| `cka-repair/runtime-interface/sqlite-runtime/` | Python 3.11.9 / SQLite 3.45.1: nine test groups pass; 128 model-table matches, five process-exit recovery points, three mutations detected | Empirical correspondence for authenticated loopback commands and a single-operation, same-database effect; no machine-checked Python/SQL refinement, OS isolation, power-loss or remote-service guarantee |

The [repair record](cka-repair/README.md) contains the finite countermodel,
precise definitions, proof scope, source fingerprints and actual build logs.
There is no proved correspondence to the deployed bridge implementation.
The [runtime-interface extension](cka-repair/runtime-interface/README.md)
separately proves conditional eventual completion for its small protocol,
and executes 512 transition rows across that protocol and three mutations.
It does not establish a deployed scheduler's service guarantee, input
authentication or distributed atomicity. The manuscript remains at `442ec0e` in this task;
its proposed status update is in the independent revision draft.

## Historical context: the 12 September consistency pass

The 12 September revision did not attempt to install or license FDR or Isabelle. Their
previous execution obstacles are not evidence about their current availability.
The manuscript no longer relies on an unidentified companion CKA paper.
That removal is now applied in the active Section 10; the historical
`advisoryCKA` BibTeX placeholder, uncited since then, was deleted from
`paper/references.bib` on 25 September. The September 12 pass also aligns
the CSP, Lean and Isabelle explanatory text with these evidence limits.
Formal declarations, proof bodies, axioms and admitted steps are unchanged;
that documentation pass supplied no new solver or proof-assistant run.

The CKA file's formula is an exploratory obligation, not a checked translation
of the manuscript's trace inclusion. Projection/composition laws and an
interpretation of state-dependent guard placement are missing. In a trace
language interpretation, algebraic zero (the empty language) must not be
identified with the singleton empty-prefix language retained by Python's
block-everything guard. These issues require semantic development before
attempting a general proof; the consistency edits did not resolve them. The
13 September work proves a separately defined finite-trace result and corrects
the unnecessary concern about projection preserving zero; it does not rewrite
the legacy axiomatization as a verified development.

The observed Dafny failures were the `occupant.None?` postcondition in
`C1_Grant` and `old(grant) == Some(d)` in `C2_Enter`. Both are intentional.
The file's stronger C0 contracts already illustrate that grant consumption and
non-overwriting can be stated locally. Absence of C3/C4 implementations cannot
be counted as their passing a Dafny run.

Lean's open declarations are `C0_fair`, `C4_safe`, and `C4_progresses`.
The coverage theorems use `contractD`, `refineD`, `progressD`, and `fairnessD`,
whose acceptance sets were transcribed from the Python results. They prove
relations among those supplied sets, not their correspondence to `Step`.
The C4 witness and its reachability are separately proved from the Lean rules.
No equivalence theorem links the Python, Dafny, CSP, Isabelle and Lean models.

The Python JSON keys retain historical names for compatibility:

| Key | Meaning used in the revised paper |
| --- | --- |
| `refinement` | Prefix-wise occupancy check within the bound |
| `progress` | No detected non-final deadlock in states reached within ten events, plus existence of a both-completed trace within twelve |
| `fairness` | No grant overwritten before entry within ten events; a safety property, **not scheduler fairness** |
| `cka_holds` | Inclusion of bounded projected trace sets; **not a checked CKA theorem** |
| `control_live` | The advisory guard does not disable an enabled controlled event; **not universal eventual progress** |

C4 has cycles. Finite-state enumeration of traces to a depth limit does not
establish unbounded temporal liveness. The manuscript states each bound and
attributes every matrix entry and count to the Python model.

The revision also checked that the unique sufficient pair in this particular
matrix is `(progress, fairness)`, that no single column rejects all mutations,
and that advisory-only filtering preserves the **entire bounded controlled
trace set**, rather than merely its cardinality, under both advice conditions.

Commands used, from the appropriate repository directories:

```sh
# Repository root; exit 4 is expected ONLY with the two specified failures.
dafny verify --solver-path /opt/homebrew/bin/z3 formal-artefacts/dafny/BridgeController.dfy

# formal-artefacts/lean; local toolchain already installed on this host.
ELAN_HOME=/tmp/elan /tmp/elan/bin/lean Bridge.lean

# figures; headless plotting is selected by the script.
MPLCONFIGDIR=/tmp/air-matplotlib python3 bridge_model.py
```

`verify.sh` is retained as a legacy orchestration helper. Its aggregate labels
and zero exit status are not sufficient evidence of proof completion: inspect
the individual tool output, expected failures and admitted statements. The
status above comes from direct tool invocations, not from those aggregate labels.
