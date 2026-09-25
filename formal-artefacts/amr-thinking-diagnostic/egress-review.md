# Concrete outbound payload review

2026-09-17, before any request in this stage. The first attempted process launch was rejected by automatic approval review before execution because of possible internal research material in the external request. The live `run/` directory remained absent.

The exact first requests are preserved in `egress-preview/N12-F.request.json` and `egress-preview/T12-F.request.json`. Both prompts have SHA-256 `6751e771f414ef6d19151469dc5054d3380cd82f88f232607ced3a1c35d822a3` and are identical to the prior authorized D12-F first prompt. The complete prompt was inspected locally.

The message contains only the synthetic two-robot corridor specification, its restricted Boolean JSON grammar and safety requirements, one prior DeepSeek-generated JSON candidate, finite Boolean counterexamples and their prescribed outputs, and instructions to return a repaired JSON program. It contains no manuscript text, literature files, real industrial measurements, personal information, repository inventory, environment-file contents, or credential value.

Later requests are constructed by the same fixed function from the same specification plus this service's immediately preceding program and generated finite-check feedback. No other repository context is attached. The only destination is the user-selected `https://api.deepseek.com/chat/completions`; the user's key is used solely in its ordinary Authorization header and never added to prompt data or printed.

This review is concrete payload evidence for reconsideration of that same action, not an alternate execution route. If automatic approval still rejects it, stop live work and obtain explicit approval for these reviewed payloads.
