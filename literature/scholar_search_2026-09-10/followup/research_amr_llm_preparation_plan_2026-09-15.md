# AMR真实LLM试验准备 Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to implement the bounded recorder task; the coordinator prepares prompts and research documentation. User explicitly chose preparation only: no model calls.

**Goal:** 在保持AMR源码规范v1.1及原有结果不变的前提下，完成可核查的提示包、逐次生成／修复记录器与试验前协议。

**Architecture:** 新建同级`formal-artefacts/amr-llm-trial`。提示与规则包由研究协议规定；记录器只接收原始输出文件及元数据，调用原有assess_source，生成有限的真实失败反馈。没有网络客户端，没有自动调用模型。未来先绑定模型配置，再生成请求文件，最后导入原始输出；准备阶段只使用显式fixture模式做流程测试。

**Tech Stack:** Python 3.12 standard library; existing amr-supervisor parser, model and assessor imported without edits.

**Spec:** [本轮预备协议](research_amr_llm_protocol_2026-09-15.md)；Task 1的完整实现要求见[任务说明](../../../formal-artefacts/amr-llm-trial/task-1-brief.md)。

## Global Constraints

- No external model calls, login, credential changes, commits, pushes, worktree changes, or edits to existing AMR code and historical evidence.
- This stage has one full v1.1 obligation package, three prose variants, two independent initial samples per variant: six initial candidates; at most two repairs per initial candidate, eighteen recorded response attempts maximum.
- This is a subset pilot, not completion of the earlier six-package/36-initial-candidate design. Runtime natural-language advice and version-binding experiments remain future work.
- All six generation prompts must be materialized before binding a live run. Repair feedback must be computed from the actual rejected output and may not contain a reference controller or expected action table.
- Exact response bytes are retained; no JSON extraction, fence stripping, regeneration after success, evaluator modification, or silent exclusion of failed attempts.
- Fixture data never count as live-model evidence. Missing model identity, snapshot and decoding settings remain explicitly unbound in the preparation artifact.
- The recorder enforces its own recorded attempt caps and order; it cannot enforce or authenticate calls in an external manually operated client.

## Tasks

### Task 1: Offline request, response and repair ledger

Create `trial.py`, `tests/test_trial.py`, `task-1-report.md` within the new artifact directory. The exact API, paths, failure rules and tests are in the task brief, which is self-contained.

- [x] Write and run failing tests for raw preservation, repair causality, frozen inputs, output failures and sample accounting.
- [x] Implement offline-only recorder and CLI using unchanged assessor.
- [x] Run tests and retain red/green evidence, then complete scoped review.

### Task 2: Protocol and prompt package

Create `protocol.json`, `prompts/interface.md`, three policy prose variants and `prompts/repair.md`; assemble six request texts deterministically before any live configuration. Write a Chinese protocol with exact sample denominators, fixed feedback, completion policy, candidate selection and remaining applicability limits.

- [x] Verify all prompts state the same v1.1 priority requirements and source grammar without exposing code, finite counterexamples or reference output.
- [x] Create preparation manifest covering the prompts, new runner and unchanged assessor/physical dependencies.
- [x] Run an explicitly labelled offline rehearsal with unchanged historical fixtures; count it only as workflow validation.

### Task 3: Review and handoff

- [x] Obtain independent code/protocol review and resolve material findings.
- [x] Freshly run appropriate tests and a manifest/ledger validation.
- [x] Write preparation result, update research entry pointers, and verify protected prior material hashes.

## Decisions

Ruling: Keep work in the existing workspace and preserve all historical artifacts — ongoing user scope and research provenance take precedence over skill boilerplate about commits, worktrees or cleanup.

Ruling: Freeze protocol content separately from a live run — the user requested preparation only; an unknown provider must not be invented. The final prepared manifest is not preregistration of a fully configured model experiment.

Ruling: Start with six full-package candidates — current v1.1 language does not encode all six originally proposed obligation packages. Small-sample outcomes would assess this synthesis task only, not industrial-task diversity or model superiority.
