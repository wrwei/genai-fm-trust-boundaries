"""Package the retained literature map and counting scripts as Online Resource 2."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "supplementary" / "ESM_2_literature_map.zip"
INPUTS = {
    "README.md": ROOT / "paper" / "supplementary" / "ESM_2_README.md",
    "literature/corpus_labelled.json": ROOT / "literature" / "corpus_labelled.json",
    "literature/lit_search.py": ROOT / "literature" / "lit_search.py",
    "literature/label_corrections.json": ROOT / "literature" / "label_corrections.json",
    "literature/check_counts.py": ROOT / "literature" / "check_counts.py",
    "literature/README.md": ROOT / "literature" / "README.md",
    "sections/00-corpus-summary.tex": ROOT / "paper" / "sections" / "00-corpus-summary.tex",
    "literature/comparison_records.json": ROOT / "literature" / "scholar_search_2026-09-10" / "followup" / "comparison_records.json",
    "literature/targeted_primary_matrix_2026-09-23.md": ROOT / "literature" / "scholar_search_2026-09-10" / "followup" / "targeted_primary_matrix_2026-09-23.md",
}

with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, source in INPUTS.items():
        archive.write(source, name)
    manifest = "\n".join(
        f"{hashlib.sha256(source.read_bytes()).hexdigest()}  {name}"
        for name, source in INPUTS.items()
    ) + "\n"
    archive.writestr("SHA256SUMS.txt", manifest)
print(f"Created {OUT} with {len(INPUTS)} source files and SHA256SUMS.txt")
