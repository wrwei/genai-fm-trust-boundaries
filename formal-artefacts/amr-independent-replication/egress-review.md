# Reviewed outbound scope for six initial requests

Maintenance note (2026-09-22): this document describes the dated experiment or review below. Test counts and review-time hashes are historical records, not claims that the current maintained files are byte-identical to the original versions. Raw provider replies, generated-controller bytes and physical trajectories are retained; current record bindings are documented in the [record-maintenance report](../record-maintenance-2026-09-22/README.md).

User authorized this DeepSeek service/model and credential-file use, explicitly prioritized sufficient resources, and asked to continue after committing/pushing existing research. That prerequisite was completed as 8259f42 on origin/main before any new stage work.

The six exact initial requests are in egress-preview/{P1,P2,P3}-{R1,R2}.request.json. They contain only the already established synthetic two-robot Boolean task, restricted JSON grammar and v1.1 requirements. Each is a single user message with no previous source, success example or feedback. The original prepared prompt undergoes exactly three eight-to-twelve rule-count wording substitutions. R1/R2 pairs have identical actual prompt bytes. Before dispatch these previews must match runner-generated payloads.

Subsequent repairs contain only the same synthetic task, this chain's own service-generated program and deterministic finite-check feedback. No paper text, real industrial/individual data, repository inventory, other candidate or credential value is sent. Historical records may be checked for integrity locally but never become initial message context.

Requests go only to the user-selected https://api.deepseek.com/chat/completions. The local credential is used solely in the ordinary Authorization header by the guarded worker. Socket/parent timeouts of 600/660 seconds accommodate complete outputs.
