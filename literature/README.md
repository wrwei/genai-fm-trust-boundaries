# Literature snapshot and revision audit

Updated 12 September 2026. `corpus_labelled.json` now contains 365 records:
the original 363-record arXiv snapshot and 2 supplementary records (Trusta and
ACCESS) tagged `source: "scholar"`. `check_counts.py` excludes the latter from
the snapshot denominator and all A–G and year counts.

The original 363 record objects are unchanged against commit `baf93da`.
The SHA-256 of that historical Git blob is
`5e9b414793adb0a4e6358d31a930749f218426e4b793d7c7f687790efb9e9b85`;
it is not the hash of today's expanded file. Line-ending-independent hashing
of the original record list with Python `json.dumps(records, ensure_ascii=False,
sort_keys=True, separators=(',', ':')).encode('utf-8')` gives
`dce358993b02739ec6db475ac9efa169984053660c5272a05d283a56a47786f0`.
The snapshot labels remain initial model-generated abstract-level labels,
not validated full-text classifications or a census of the research field.

A separate supplementary research register holds 330 bibliography and
screening records and 82 comparison records, which overlap. It must not be
confused with the 2 additions to the main collection. This deposit includes
only the parts of that register that the evidence manifests reference, plus
the comparison records and targeted primary matrix under
[`scholar_search_2026-09-10/followup/`](scholar_search_2026-09-10/followup).
The rest of the register, and the internal tracker of manuscript revision
proposals, are not included.

`label_corrections.json` records two targeted AI-assisted primary-source
corrections (FVEval and AssertionBench), with URLs, section locators, previous
labels and reasons. These are applied in memory; the original snapshot records
retain their initial labels for audit. This is not an independent human coding exercise or a representative
sample from which to estimate classification error.

```sh
python3 literature/check_counts.py
# Regenerate the LaTeX macros and figure after changing documented corrections:
MPLCONFIGDIR=/tmp/air-matplotlib python3 literature/check_counts.py --write
# Inspect cached labels (includes the 2 supplementary records; not the paper's counts):
python3 literature/lit_search.py --cached
```

The corrected provisional classes are 178, 84, 39, 37, 15, 4 and 6 for
A through G. The mixed C category includes empirical and unresolved cases and
must not be equated with model self-judgement. Auxiliary `checker: none`
means not extracted from the abstract, not established absence of a checker.

The year histogram uses the first-submission `date`, not the auxiliary `year`
field, which differs on one record. There are 136 first submissions in 2025
and 155 in partial 2026, through 2 September. The latest record date is not the
original retrieval timestamp.

The exact original query strings and classification prompt remain in
`lit_search.py`. The regex boundary escapes were repaired on 9 September 2026:
the old expressions matched zero saved records, while the repaired expressions
match all 363. Positive/negative lexical controls were also checked. Matching
the expressions does not establish substantive eligibility.

The raw retrieval responses, original execution timestamp, exclusion log,
classifier identity/settings and drafting notebook are unavailable. Live
retrieval has no historical cutoff and caps each query at 1,000 records. It
writes new **unlabelled** records and does not recreate the original search or
classification. Fine-grained sub-theme counts from the unavailable notebook
have been removed from the paper rather than presented as reproducible.

Before treating the map as a systematic study: recover or rerun a dated search,
expand appropriate bibliographic coverage, record exclusions and versions, and
conduct full-text independent coding with adjudication. Audit the assurance
category and mixed C category especially carefully. Arithmetic checks do not
substitute for that work.

The dated research generators in `scholar_search_2026-09-10` retain their
historical file hashes and clean-worktree checks. They generate/overwrite
historical artefacts and are not current-tree validators after the collection
was expanded. Preserve their original audits; use `check_counts.py` for current
snapshot counts and the revision-status record for this consistency pass.
