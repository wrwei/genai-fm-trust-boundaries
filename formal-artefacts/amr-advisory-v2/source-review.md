# Independent source review

**Spec-compliance verdict: PASS.** No load-bearing defect was found in the finite source assessment or the recorded source evidence.

The checker implements the frozen fixed-registration profile, not general arrival-order FIFO: when both registered requests are eligible, only an unambiguous B preference selects B; absent, A-only, or conflicting preference falls back to A. A sole eligible request is selected regardless of preference, and occupied/no-request cases defer. The exhaustive domain is exactly 32 selection valuations plus 7 modes × 256 step valuations = 1,824 cases, while the original v1.1 step obligations remain the authority for all 1,792 step cases.

All six historical replication responses are read as exact bytes in sample order. Their SHA-256 identities match the evidence; all six sample assessments are retained and the five distinct raw identities are retained separately (P2-R1 and P3-R2 are the one duplicate pair). The deployment rule is implemented correctly: selection occurs only on first encounter of a distinct identity, and P3-R1 (`9eaa530b58253c1a07c6369882ed59eacb4cfac7dc40850e4100d31f387a47cd`) is the first and only v2-accepted historical sample. A clean regeneration reproduced the recorded semantic summary exactly after disregarding the deliberately output-directory-dependent evidence paths.

E1 changes the extracted target relation only and leaves the source bytes and source execution unchanged. Its verdict is calculated over the whole 1,824-case domain rather than inferred from the injected branch: the faulty target happens to pass the v2 model policy over that domain, while the unchanged source fails one selection case and correspondence exposes that same mismatch. Acceptance therefore remains false; model-policy success alone is not treated as source success or correspondence.

**Code-quality verdict: PASS.** The implementation is compact, deterministic, and keeps source/model judgments separate. The relative-output defect found in the first review is fixed by resolving the output path before evidence paths are relativized. The added regression test exercises a relative output, asserts six samples, five distinct identities, first-accepted selection at sample three, and verifies every copied source against its recorded SHA-256. All five source tests pass. A caller still must choose an output directory beneath the repository because evidence paths are intentionally repository-relative; that constraint does not affect the declared run.

**Load-bearing defects: none.**
