#!/usr/bin/env python3
"""Check every recorded SHA-256 in the deposit, accounting for path sanitisation.

Manifests and run records carry digests of the ORIGINAL bytes. Files listed in
sanitisation-map.json had machine-local paths replaced after those digests were
recorded, so for them the check is two-step: the current bytes must match the
map's sanitised digest, and the manifest's digest must equal the map's original.

    python formal-artefacts/record-maintenance-2026-09-25-path-sanitisation/verify_digests.py

Exit 0 when the result reproduces the pre-sanitisation baseline stated below.
"""
import hashlib, json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
H64 = re.compile(r"^[0-9a-f]{64}$")
# Result of the same check on the unsanitised working repository (2026-09-25):
BASELINE = {"match": 631, "mismatch": 3, "unresolved": 19}

smap = json.loads((HERE / "sanitisation-map.json").read_text(encoding="utf-8"))
by_path = {e["path"]: e for e in smap["files"]}

def pairs(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, str) and H64.match(v) and ("/" in k or "." in k):
                yield k, v
            elif isinstance(v, dict) and isinstance(v.get("sha256"), str) and H64.match(v["sha256"]) and ("/" in k or "." in k):
                yield k, v["sha256"]
            else:
                yield from pairs(v)
    elif isinstance(x, list):
        for v in x:
            if isinstance(v, dict) and isinstance(v.get("sha256"), str) and isinstance(v.get("path"), str):
                yield v["path"], v["sha256"]
            else:
                yield from pairs(v)

def resolve(manifest, rel):
    """Package-relative first (the manifest's directory, then each parent up to
    its package root), repository root last. Trying the root first would let a
    bare name such as README.md resolve to the top-level README instead of the
    package's own."""
    rel = rel.replace("\\", "/")
    pkg = ROOT.joinpath(*manifest.relative_to(ROOT).parts[:2])
    bases, d = [], manifest.parent
    while d == pkg or pkg in d.parents:
        bases.append(d); d = d.parent
    bases.append(ROOT)
    for b in bases:
        p = (b / rel).resolve()
        if p.is_file():
            return p
    return None

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# 1. every sanitised file must match its recorded sanitised digest
bad_map = [e["path"] for e in smap["files"] if sha(ROOT / e["path"]) != e["sanitised_sha256"]]

# 2. every manifest digest, mapped back to original bytes where sanitised
n = {"match": 0, "mismatch": 0, "unresolved": 0}
for manifest in sorted((ROOT / "formal-artefacts").rglob("*manifest.json")):
    for rel, digest in pairs(json.loads(manifest.read_text(encoding="utf-8"))):
        p = resolve(manifest, rel)
        if p is None:
            n["unresolved"] += 1
            continue
        e = by_path.get(p.relative_to(ROOT).as_posix())
        current = e["original_sha256"] if e and sha(p) == e["sanitised_sha256"] else sha(p)
        n["match" if current == digest else "mismatch"] += 1

print(json.dumps({"sanitised_files": len(smap["files"]), "sanitised_digest_failures": bad_map,
                  "manifest_check": n, "baseline": BASELINE}, indent=1))
sys.exit(0 if not bad_map and n == BASELINE else 1)
