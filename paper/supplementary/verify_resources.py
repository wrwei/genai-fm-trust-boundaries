"""Check that both submission resources contain the claimed evidence and inputs."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
source = (HERE / "ESM_1_evidence_matrix.md").read_text(encoding="utf-8")
rows = [line for line in source.splitlines() if line.startswith("| [")]
assert len(rows) == 20, f"Expected 20 study rows, found {len(rows)}"
for name in ["Clover", "PLC test generation", "DeepSeek-Prover-V2", "Forge v2"]:
    assert name in source

pdf = PdfReader(str(HERE / "ESM_1_evidence_matrix.pdf"))
pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
assert len(pdf.pages) == 2
for name in ["Clover", "PLC test generation", "DeepSeek-Prover-V2", "Forge v2"]:
    assert name in pdf_text, f"Missing PDF text: {name}"
links = sum(len(page.get("/Annots", [])) for page in pdf.pages)
assert links >= 20, f"Expected study links in PDF, found {links} annotations"

bundle = HERE / "ESM_2_literature_map.zip"
with zipfile.ZipFile(bundle) as archive:
    assert archive.testzip() is None
    manifest = archive.read("SHA256SUMS.txt").decode("utf-8").splitlines()
    for line in manifest:
        digest, name = line.split("  ", 1)
        assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
    with tempfile.TemporaryDirectory() as directory:
        archive.extractall(directory)
        result = subprocess.run(
            [sys.executable, str(Path(directory) / "literature/check_counts.py")],
            capture_output=True, text=True, check=True,
        )
        assert re.search(r"Records:\s+363\b", result.stdout)
        assert "Corrections with source locators: 2" in result.stdout

print(f"Online Resource 1: 20 rows, {len(pdf.pages)} PDF pages, {links} link annotations")
print("Online Resource 2: ZIP checksums match; extracted map audit reports 363 records and 2 corrections")
