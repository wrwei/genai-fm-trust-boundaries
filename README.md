# genai-fm-trust-boundaries

Code and data for:

> Le Zhu, Ran Wei, Jim Woodcock, Haochi Wang and Xiangyang Ji.
> *From Checked Artefacts to System Assurance: A Critical Review of Trust
> Boundaries in Generative AI and Formal Methods.* Submitted to
> *Artificial Intelligence Review*, 2026.

The paper reviews how generative models and formal methods are combined,
asking in each case which component's verdict is trusted to accept a result.
It supports the review with a bounded mobile-robot case study. This repository
holds the saved literature records and counting scripts behind the review's
exploratory map, and the retained sources, proofs, runs and audits behind the
case study.

## What each claim rests on

Paths are relative to [`formal-artefacts/`](formal-artefacts). The *Boundary*
column states what each result does **not** establish, as the paper does.

| Claim in the paper | Entry point | Boundary |
| --- | --- | --- |
| Six independent fresh-context controller requests under a declared repair cap | [`amr-independent-replication/`](formal-artefacts/amr-independent-replication/README.md) | One task and one historical model batch; not a success-rate estimate |
| Selection contract, first accepted source P3-R1, the 1,824-input check, six live advice replies | [`amr-advisory-v2/contract.md`](formal-artefacts/amr-advisory-v2/contract.md), [`source-review.md`](formal-artefacts/amr-advisory-v2/source-review.md), [`advice-review.md`](formal-artefacts/amr-advisory-v2/advice-review.md) | Advisory replies are typed choices, not control events |
| Restricted source-to-model semantics | [`amr-extraction-faithfulness/`](formal-artefacts/amr-extraction-faithfulness/README.md) | Isabelle theorem for finite, pure Boolean, first-match rule tables; the general Python front end is not proved correct |
| Finite authority, adapter conformance and physical replay | [`amr-runtime-binding/`](formal-artefacts/amr-runtime-binding/README.md), [`amr-advisory-v2/`](formal-artefacts/amr-advisory-v2/README.md) | Bounded checks and replayed simulations; no Python-to-plant refinement or hardware certification |
| Conditional two-task timing | [`amr-closed-loop-timing/`](formal-artefacts/amr-closed-loop-timing/README.md) | Holds under stated scheduler and response premises; no universal scheduler proof |
| Progress is a separate obligation from speed and acceleration limits | [`amr-progress-obligations/`](formal-artefacts/amr-progress-obligations/README.md) | A stationary countermodel and a bounded run; not a completion guarantee |
| Finite bridge authority and the progress counterexample | [`cka-repair/`](formal-artefacts/cka-repair/README.md), [`paper/figures/bridge_model.py`](paper/figures/bridge_model.py) | Bounded enumeration and a finite-language theorem; not a complete Concurrent Kleene Algebra instance |

[`formal-artefacts/SUBMISSION_CLAIM_GUIDE.md`](formal-artefacts/SUBMISSION_CLAIM_GUIDE.md)
gives the full statement of each boundary. [`PROVENANCE.md`](formal-artefacts/PROVENANCE.md)
records which command produced each verdict.

The other `amr-*` packages are the earlier runs and fixtures that the
packages above load code or frozen inputs from. They are included so that
every recorded checksum resolves; the paper does not cite them as evidence
on their own.

## Layout

```
literature/        saved arXiv records, label corrections, count audit, search script
  scholar_search_2026-09-10/followup/   protocol and review notes referenced by the manifests
formal-artefacts/  case-study packages: sources, Isabelle theories, runs, manifests, audits
docs/superpowers/  design and plan documents that package READMEs and manifests reference
paper/
  sections/00-corpus-summary.tex        the counts the paper typesets, checked by literature/check_counts.py
  figures/         scripts for the bridge and evidence-chain figures
  supplementary/   builders for Online Resources 1 and 2
```

## Reproducing

**Literature counts.** Standard library only:

```
python literature/check_counts.py
```

This checks every count in `paper/sections/00-corpus-summary.tex` against
the saved records and exits non-zero if any is stale. With `--write`, it
instead regenerates that file and the literature-taxonomy figure; the
figure needs `matplotlib`.

The saved records are a snapshot. The original arXiv retrieval and
classifier configuration were not retained, as Section 2 of the paper
explains. `python literature/lit_search.py --cached` recounts the saved
labels and writes `literature/corpus_core.json`. Without `--cached`, it
queries arXiv afresh and will not reproduce the snapshot.

**Recorded checksums.** Standard library only:

```
python formal-artefacts/record-maintenance-2026-09-25-path-sanitisation/verify_digests.py
```

This re-checks every SHA-256 digest recorded in the evidence manifests. See
[the next section](#path-sanitisation) for why the check goes through a map.

**Isabelle theories.** The retained builds used Isabelle2025-2. Five
packages have a `hol/` session. Two build directly on `HOL`; the other three
form a chain, so each needs its ancestors' directories passed with `-d`.
From `formal-artefacts/`:

```
isabelle build -D amr-extraction-faithfulness/hol
isabelle build -D amr-progress-obligations/hol
isabelle build -d cka-repair -D amr-advisory-v2/hol
isabelle build -d cka-repair -d amr-advisory-v2/hol -D amr-runtime-binding/hol
isabelle build -d cka-repair -d amr-advisory-v2/hol -d amr-runtime-binding/hol \
               -d amr-extraction-faithfulness/hol -d amr-progress-obligations/hol \
               -D amr-closed-loop-timing/hol
```

| Session | Parent | Also imports theories from |
| --- | --- | --- |
| `AMR_Extraction_Faithfulness` | `HOL` | |
| `AMR_Progress_Obligations` | `HOL` | |
| `Bridge_Algebra_Repair` (in `cka-repair/`) | `HOL` | |
| `AMR_Advisory_V2` | `Bridge_Algebra_Repair` | |
| `AMR_Runtime_Binding` | `AMR_Advisory_V2` | |
| `AMR_Closed_Loop_Timing` | `AMR_Runtime_Binding` | `AMR_Extraction_Faithfulness`, `AMR_Progress_Obligations` |

These commands follow the session structure in the `ROOT` files and match the
`-d` flags the retained builds used. They have not been re-run for this
repository.

The `build.py` script in each `hol/` directory is the Windows driver that
produced the retained `build.log`. It reads the installation from
`ISABELLE_HOME` and runs Isabelle through the Cygwin shell bundled with the
Windows distribution, so on Linux or macOS use the commands above instead.

**Package verifiers.** Several packages ship a `verify.py`. These scripts
**rewrite their own evidence files** each time they run, because they
recompute the evidence and its timestamps. Run them in a scratch copy, not in
a checkout you intend to commit from.

**Figures and supplementary files.** These need `matplotlib`, `numpy` and
`Pillow`; the Online Resource builders also need `reportlab` and `pypdf`.
Everything under `formal-artefacts/` uses only the Python standard library.

## Path sanitisation

The records were produced on a Windows workstation, and 82 files embedded its
local paths. Before publication those paths were replaced: files in the
repository became links into this repository, and the private Isabelle
installation became `<ISABELLE_HOME>`. No recorded checksum was edited, so
the manifests still attest to the original bytes.

[`sanitisation-map.json`](formal-artefacts/record-maintenance-2026-09-25-path-sanitisation/sanitisation-map.json)
lists the original and sanitised digest of every rewritten file, and the
verifier above uses it to check both. The result, 631 digests matching,
3 mismatching and 19 unresolved, is identical to the same check on the
unsanitised originals. The
[record](formal-artefacts/record-maintenance-2026-09-25-path-sanitisation/README.md)
explains each of those 22 exceptions.

## Not included

The research notes under `literature/scholar_search_2026-09-10/followup/`
are included only where an evidence manifest or package README points to
them. They are kept byte-exact because manifests pin their digests. Some of
them link to other notes in the full research register that are not part
of this deposit, so 68 links inside those notes do not resolve here. Every
link in this README, the package READMEs, the claim guide and the
provenance record does resolve.

Historical Isabelle, Lean, CSP and Dafny sketches of the bridge example are
not in this repository. They contain admitted or unfinished proofs, and the
paper does not rely on them. The Forge prototype's code and results are
published separately with its preprint, which the paper cites.

## Licence

MIT. See [`LICENSE`](LICENSE).