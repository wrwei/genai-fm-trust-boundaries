# AMR thinking-mode comparison

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see the [record-maintenance report](../record-maintenance-2026-09-22/README.md). Raw replies, controller source bytes and physical trajectories are retained.

User-authorized continuation of the Forge-informed diagnostic; main development branch.
Protocol: `../../literature/scholar_search_2026-09-10/followup/research_amr_thinking_protocol_2026-09-17.md`.

N12-F: thinking disabled, temperature 0. T12-F: thinking enabled, reasoning_effort high,
temperature omitted because the provider ignores it in thinking mode. Both use deepseek-flash,
max_tokens 8192, stream false, the same prior P2-R1 failure, 12 rules, enhanced feedback and
unchanged v1.1 obligations. Fresh context every repair; no previous reasoning content is sent.

Round-robin N then T, up to four repairs per condition / eight POSTs total. Accept first;
otherwise stop repeated canonical programs. A provider, transport, token-usage
or infrastructure error stops the batch.
This is one-seed post-hoc diagnosis of model configurations, not an independent success-rate study.

The output count includes reasoning and final content. Only final content is assessed as source.

Protocol references: [thinking mode](https://api-docs.deepseek.com/guides/thinking_mode/) and
[chat completion API](https://api-docs.deepseek.com/api/create-chat-completion/).

The request body cap is 65,536 bytes. The worker has one exclusive claim and dispatch marker; socket timeout
150 s and parent deadline 180 s. Fixed endpoint https://api.deepseek.com/chat/completions only,
no redirects/proxies. Credential file is read only inside the guarded worker and is never archived.
The provider envelope is retained, but only exact content becomes source; reasoning_content is
not displayed as a result or used as a repair prompt. Its presence and token usage are recorded.

An existing run directory blocks re-execution. Never delete it to redispatch. Raw provider
replies and generated-controller bytes are preserved; this stage records its generation/checking dependencies separately. Test fixtures
are explicitly offline and cannot be deployed as live evidence.

Physics is conditional on both conditions being terminal and an accepted source. Select first
accepted condition in N12-F,T12-F order and its first accepted repair before viewing any physical
outcome. Exact unmodified source is paired with handwritten calibration in normal_A, normal_B,
temporary blocking, blackout (10–15 s), and permanent blocking, dt 0.01, horizon 120 s. Physical
adapter inputs freeze separately before episodes. No accepted source means no physical run.
