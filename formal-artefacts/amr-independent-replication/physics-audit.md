# Independent replication physical trace audit

**Verified 30 archived episodes from 5 distinct accepted sources plus five reference cases.** No plant episode was rerun and no model or network call was made.

Checked all 70 physical manifest files and 166 frozen input files before and after replay. Exact accepted provider source identities, deduplication mapping, saved adapter and adapted checker imports, live deployment gate, complete episode plan, all episode summary fields and aggregate comparisons reproduce.

Re-evaluated 75,816 step and 44,148 selection decisions, reconstructing observations, blackout drops, runtime obligation checks and fallback actions, modes, physical intents, command delivery, exclusive reservation ownership, grant/release/completion events, and 42,498 physical standstill checks.

Reconstructed continuous pieces without advancing the plant and re-scored 2,133,618 pair intervals using the frozen geometric oracle. Verified continuity, derivative and speed bounds, footprint clearance at release, actual goal position and standstill at completion. Minimum distance lower bound: 0.26068542394925565 m.

| Episode | Grants | Completion times (s) | End (s) | Final owner | Complete and safe |
| --- | --- | --- | ---: | --- | --- |
| reference_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| reference_normal_B | B, A | {"A": 58.95, "B": 32.95} | 58.95 | None | True |
| reference_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| reference_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| reference_permanent | A | {} | 120.00 | A | False |
| source_01_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_01_normal_B | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_01_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| source_01_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| source_01_permanent | A | {} | 120.00 | A | False |
| source_02_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_02_normal_B | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_02_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| source_02_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| source_02_permanent | A | {} | 120.00 | A | False |
| source_03_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_03_normal_B | B, A | {"A": 58.95, "B": 32.95} | 58.95 | None | True |
| source_03_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| source_03_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| source_03_permanent | A | {} | 120.00 | A | False |
| source_04_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_04_normal_B | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_04_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| source_04_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| source_04_permanent | A | {} | 120.00 | A | False |
| source_05_normal_A | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_05_normal_B | A, B | {"A": 32.95, "B": 58.95} | 58.95 | None | True |
| source_05_temporary | A, B | {"A": 39.9, "B": 65.9} | 65.90 | None | True |
| source_05_blackout | A, B | {"A": 37.85, "B": 63.85} | 63.85 | None | True |
| source_05_permanent | A | {} | 120.00 | A | False |

Stop/resume transition times, final modes/speeds, observation drop counts, and stopping-premise evidence are recorded per episode in `physics-audit.json`. Every reported summary field, including collision witnesses, runtime rejections, early releases, physical completion mismatches, and assumption lists, was checked against reconstruction.

Related deterministic analytic episodes; not independent industrial tasks or a safety theorem. Straight-approach stopping evidence is inapplicable when its recorded domain conditions fail; geometric replay is a separate safety check. Preference is advisory, not a mandatory ordering obligation.

The pedestrian stopping diagnostic is assessed separately from geometry: an inapplicable straight stopping premise is not verified by an empty violation list. Permanent blocking can establish safe waiting only within the fixed horizon. Source preference behavior is reported through verified grant orders and reference comparisons rather than assumed to match advisory preferences.

Summary SHA-256: `181172124fed7a47bcbfca5edef1a1db33327dd6163b8318277d0a54ebe5924a`
Manifest SHA-256: `9104f593299f2f67bd8f0785222afe7679801b0c8f74e72ad70fc2b7959cd188`
