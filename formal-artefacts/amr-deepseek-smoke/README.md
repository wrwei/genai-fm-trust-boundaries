# DeepSeek single-call AMR smoke experiment — 17 September 2026

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see repository directory formal-artefacts/record-maintenance-2026-09-22. Raw replies, controller source bytes and physical trajectories are retained.

The user authorized one DeepSeek `deepseek-flash` request at `https://api.deepseek.com`. This smoke stage evaluated the frozen P1-R1 initial prompt once; it did not complete the six-chain pilot or select a physical controller.

## Execution and retained evidence

- One user message; no reference implementation, tools, repair or retry.
- Explicit non-thinking mode, temperature 0, maximum 2,048 output tokens.
- One child process makes one HTTPS POST. Redirects and environment proxies are disabled; the parent deadline is 90 seconds.
- An exclusive run directory and dispatch marker prevent accidental repeated execution.
- Only the child reads the locally supplied credential. It is absent from requests and retained evidence.
- Original request, HTTP response, assistant bytes, timing, token usage and independent assessment are retained. The whole assistant response is checked without extracting a preferred fragment.

The response was rejected because its nine step rules exceeded the frozen eight-rule cap. This rejection is part of the generation record, not a physical-safety result. The subsequent pilot inherits this first request once.

## Offline checks and commands

From this directory, run `python -B -m unittest discover -s tests -v`. Tests cover usage validation, timeout/no-retry behavior, credential handling, explicit decoding/output limits and preparation integrity.

`python smoke.py --key-file <local-env-path>` is the original one-time launcher. The retained `run` directory prevents a second dispatch. Do not remove that directory or its dispatch marker to force another request. A new experiment requires a separately recorded run.

[Official Chat Completions reference](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion/) documents the response and request vocabulary. Actual model identity and fingerprint remain in the original provider response.
