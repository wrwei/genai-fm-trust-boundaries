# AMR LLM试验准备包

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see repository directory formal-artefacts/record-maintenance-2026-09-22. Raw replies, controller source bytes and physical trajectories are retained.

本目录为真实生成／修复试点准备提示和离线记录流程。 **该准备阶段未调用模型。** 研究设计见[预备协议](../../literature/scholar_search_2026-09-10/followup/research_amr_llm_protocol_2026-09-15.md)。

## 试验范围

固定一个完整`amr-supervisor-obligations/v1.1`规则包，P1/P2/P3三种表述各采样两次，共6个初始候选，每个最多修复2次，总记录上限18次。生成顺序、反馈截断和候选选择写在[protocol.json](protocol.json)。这不代表原36初始候选方案已经执行，也不包括运行时自然语言建议。

候选需要在每函数8条规则以内表达固定的优先级策略。源码整体严格解析并交给[原接受器](../amr-supervisor/assurance.py)检查；全部1824个布尔输入上的源码策略、目标模型策略和对应性均须通过。输入域包括不可达组合。该任务不测自由设计导航算法的能力，有限检查也不是物理安全定理。

## 文件入口

- [接口契约](prompts/interface.md)、[P1](prompts/policy_P1.md)、[P2](prompts/policy_P2.md)、[P3](prompts/policy_P3.md)与[修复模板](prompts/repair.md)。`prompts/prepared/`已保存全部6份初始提示；同一表述的两次采样提示字节相同。
- [trial.py](trial.py)：初始化、准备下一请求、记录原始响应、汇总。只进行本地文件操作，不包含网络或模型客户端。
- [fixture-config.json](fixture-config.json)：仅用于离线流程演练。
- [rehearse.py](rehearse.py)：用历史构造程序、模拟超时和无效编码演练6条样本链；生成／修复响应均为预先安排的fixture，不调用模型。
- [任务要求](task-1-brief.md)与[协议审阅](protocol-review.md)：实现边界和独立核对记录。

## 使用方式

在本目录下执行；`python`应替换为本机Python 3.12解释器。先用`python trial.py --help`查看命令。本轮仅可以使用fixture演练；不要把示例配置改名后当作真实采样。

```powershell
New-Item -ItemType Directory -Path runs -ErrorAction SilentlyContinue
python trial.py init --bundle . --run runs/my-fixture --config fixture-config.json
python trial.py prepare --run runs/my-fixture
python trial.py record --run runs/my-fixture --response raw-response.bin --metadata response-metadata.json
python trial.py summary --run runs/my-fixture
```

`init`只能建立新运行，已存在的目录不得覆盖。`prepare`输出本次请求的编号、时间、提示路径和哈希；再次准备同一待收请求会返回原请求。将完整输出字节保存在`raw-response.bin`，随后提供元数据再调用`record`。工具不进行实际发送。

也可以一条命令生成完整演练：`python rehearse.py --output runs/my-rehearsal`。目录必须不存在；每次都会保留11份原始响应登记及其构造来源，包含5份预先安排的修复。运行`python -m unittest discover -s tests -v`检验记录器和这条完整流程。

响应元数据必须包含sample_id、attempt_index、status、provider、model_id、decoding、requested_max_output_tokens、request_sha256、request_id、started_at_utc、finished_at_utc、input_tokens和output_tokens。模型与解码身份必须匹配初始化配置，request_sha256必须匹配待收提示；时间须带UTC偏移，结束不早于开始，开始不早于请求准备时间。未知usage填JSON null，未暴露的请求编号填`not-exposed`；不能把缺失数值填成0。

status可为ok、timeout、transport_error、refusal、truncated。拒答、截断与基础设施失败终止该样本链；status=ok但编码、解析或语义失败时才进入限定修复。保留完整原文，不从围栏或其他文字中提取JSON。每次修复只使用原要求、紧邻的上一输出与它实际触发的有限反馈。先合格即停止该链。

## 证据和限制

fixture运行不计为真实模型样本。未来live运行需真实配置和用户继续采样的指令。离线导入只核验记录的一致性，不能认证服务提供者、模型版本、外部上下文隔离。

提示与输入快照保证已有字节可复核；哈希本身不能对抗可以同时改写所有文件和哈希的操作者，不构成密码学签名或外部预注册。运行保存绝对输入路径，移到另一机器后不能直接伪装成原运行继续追加；应保留原归档并在新路径建立新运行。

未完成全部6个链时不选闭环候选。全部完成后按样本编号字典序选最小的合格候选；所有失败则不选择。选择记录只提供源码路径与哈希，不产生物理安全结论。后续配对仿真应复用原场景并如实记录合法但不同的选择。
