# Online Resource 2: Literature-map reproducibility files

This companion ZIP supplies the saved corpus and the exact scripts used for the manuscript's exploratory counts. It is not a reconstruction of the original arXiv retrieval: the execution timestamp, raw responses, screening log, original classifier identity/settings and per-record rationales are unavailable. The corpus holds 363 original arXiv records and two later provenance-tagged contextual records; `check_counts.py` excludes the two additions from the reported denominator. The two targeted corrections are stored separately, leaving the original labels auditable.

From an extracted ZIP directory, run `python literature/check_counts.py` to validate the count assertions against the included LaTeX summary. `literature/lit_search.py` contains the fourteen query families, lexical filters and original classification prompt. Running a live search now is not an exact replay of the historical snapshot. `literature/README.md` describes the preserved provenance and revision limits.

The original comparison register and targeted matrix are included for audit; the English study-level synthesis is Online Resource 1. The ZIP is built by `build_esm2.py` from the repository's current literature files. It makes no claim of independent human coding or of field-wide prevalence.
