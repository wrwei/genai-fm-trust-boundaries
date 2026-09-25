# Extended runner verification

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

2026-09-17. Implemented only the new runner, its tests and these verification logs. No credential file read, provider request, commit, old-stage modification or fixed live run creation occurred in this implementation task.

Inherited utilities are loaded under `_amr_extended_smoke` and `_amr_extended_diagnostics`. `CONFIGS`, `payload_for`, state, replay, decode and result APIs are unchanged.

The previous thinking run inventory and its exact frozen source hashes are recorded in `thinking-inventory.json` and `thinking-frozen-inputs.json`, both included in setup hashes. The previous thinking inputs join the new runtime freeze and are checked before initial setup and throughout execution. Physics adapter and new tests remain outside the request-stage runtime freeze.

Offline command: `python -B -m unittest discover -s formal-artefacts/amr-thinking-extended/tests -p test_runner.py -v`.

**25 tests passed in 37.325 seconds**, recorded in `runner-tests.txt`. The targeted output-boundary rerun passed and is saved in `runner-tests-output-boundary.txt`. `runner-tests-red.txt` records all 25 tests failing before implementation. The independent combined-suite results are recorded in `preflightreview.md`.

Both new first prompts equal previous thinking attempt 001 byte-for-byte.

Final implementation SHA-256:

- runner.py: `662cf63549da98aa67f4a4eef7dcc997eff7b1068406ab867b6e06a8c4fdf9b7`
- tests/test_runner.py: `84289f0378e09d15616e6b6a0fc1283946a3f7b484302f79f07e280d3e79ded3`
