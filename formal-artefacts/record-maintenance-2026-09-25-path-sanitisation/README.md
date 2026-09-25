# Path sanitisation for the public deposit (25 September 2026)

The records were produced on a Windows workstation, and 82 files embedded
that machine's local paths: the repository checkout and a private Isabelle
installation. They were replaced before publication.

| Found | Replaced with |
| --- | --- |
| a file or directory in the repository checkout | its GitHub URL in this repository |
| the repository checkout used as a working directory in a documented command | the path relative to the repository root, so the command still runs |
| the local Isabelle installation | `<ISABELLE_HOME>/...` |
| the Isabelle workspace next to it | `<ISABELLE_WORKDIR>/...` |
| other local scratch directories | `<LOCAL_WORKDIR>/...` |

The same path appears in four spellings (forward slashes, backslashes,
JSON-escaped backslashes and the Cygwin `/cygdrive/` form), and all four
were rewritten. Five `hol/build.py`
scripts are the only code changed: they now read the Isabelle installation
from the `ISABELLE_HOME` environment variable instead of a fixed path.

## What was not changed

No recorded checksum was edited. Manifests, frozen-input records, baseline
hashes and run records still carry the digests of the **original** bytes,
because they attest to what existed when each run was recorded. The
sanitised copy of a file therefore no longer matches its manifest digest
directly.

[`sanitisation-map.json`](sanitisation-map.json) closes that gap. For each
rewritten file it lists the original and sanitised SHA-256 and byte count,
plus how many paths of each kind were replaced.

Windows interpreter paths under `C:/Users/Admin/` are kept verbatim, since
the account name is generic. Line endings and all non-path content are
unchanged.

## Checking

```
python formal-artefacts/record-maintenance-2026-09-25-path-sanitisation/verify_digests.py
```

The script checks that every sanitised file matches its sanitised digest. It
then re-runs every manifest digest check in the deposit, mapping each
sanitised file back to its original digest through the map. It exits 0 only
if the result equals the same check run on the unsanitised working copy and
on the verbatim copy taken before any rewrite: 631 digests match, 3 mismatch
and 19 are unresolved.

The 3 mismatches and 19 unresolved entries are properties of the records
themselves and were present before sanitisation:

- Two mismatches, `run_suite.py` and `simulation.py`, are in
  `amr-corridor/results/reference-2026-09-15-initial`. The package README
  marks that run as a development record whose runtime source identity is
  incomplete, not as final evidence. The final run,
  `reference-2026-09-15`, matches.
- One mismatch is a review note,
  `literature/scholar_search_2026-09-10/followup/review_integration_2026-09-15.md`,
  edited after the `amr-advisory-v2` manifest recorded it.
- The 19 unresolved entries name files by bare filename. Each digest does
  match a file in the deposit: the corridor test files are under
  `amr-corridor/tests/`, and the supervisor baseline sources are the frozen
  copies under `amr-deepseek-smoke/run/frozen/`. The manifests do not record
  those locations, so the check reports them as unresolved rather than
  guessing.
