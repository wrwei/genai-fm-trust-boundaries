# DeepSeek AMR six-chain pilot continuation — 17 September 2026

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see repository directory formal-artefacts/record-maintenance-2026-09-22. Raw replies, controller source bytes and physical trajectories are retained.

The authorized pilot used P1-R1, P2-R1, P3-R1, P1-R2, P2-R2 and P3-R2, with at most two repairs per sample, first-acceptance stopping and at most 18 total requests. P1-R1's smoke response is inherited exactly once; the continuation adds 17 requests. No transport request is retried.

## Fixed execution scope

The frozen v1.1 policy and eight-rule parser remain the scientific baseline. The model was `deepseek-flash`, non-thinking, temperature 0 and at most 2,048 output tokens. Repair prompts contain the prior raw response and actual capped feedback, without manual diagnostic advice, reference solutions, tools or model substitution. Temperature zero and equivalent repeated prompts limit diversity; these are repeated requests for one task.

The original HTTP messages, assistant bytes, prompts, timing, usage, assessments and lineage are retained. Current record checksums describe the maintained snapshot; the maintenance record identifies changed metadata and execution copies. This is continuation of a failed first sample, not replacement of it.

## Outcome and physical gate

Six initial responses and twelve repairs yielded zero accepted controllers: one parse rejection and seventeen semantic rejections. Token totals are 30,744 input and 4,558 output. No generated controller qualified for physical deployment.

The predeclared physical gate requires all chains to terminate and at least one to pass, selecting the lexicographically first accepted sample and its first accepted response. A selected source would be compared with the handwritten reference on normal A, normal B, temporary blockage, observation blackout and permanent blockage: ten related episodes with dt 0.01 s, monitor period 0.05 s, application delay 0.10 s and horizon 120 s. These planned generated-source runs were not executed because the acceptance gate failed.

Legal A/B choice differences are allowed by this historical optional-preference contract. Permanent physical blockage may legitimately prevent completion. Finite source acceptance and physical trajectory evaluation are different evidence objects; this pilot does not establish runtime natural-language advice, general robot safety or statistical reliability.

## Reproduction

- Retained-record analysis: `python analyze.py`.
- Physical gate: `python simulate.py`.

Maintenance exception: updating the historical `pilot.py`, its archived copy and continuation tests remains pending explicit confirmation after automatic approval review rejected that control change. This legacy launcher is incompatible with the cleaned trial/smoke metadata interface and must not be used for new runs. The read-only record analysis and physical eligibility checks remain separate from that launcher. New offline validation is recorded in the maintenance report; old continuation test transcripts describe the earlier version.

Existing dispatch markers and exclusive run directories must remain intact. Work is on main; this package is research evidence, not an Overleaf publication snapshot.
