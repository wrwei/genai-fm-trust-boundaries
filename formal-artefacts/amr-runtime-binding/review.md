# AMR runtime binding 独立复核

复核日期：2026-09-22。范围：当前设计、适配器、HOL 模型与导出、有限对应检查、派生物理驱动、四次存档运行及执行审计。仅新增本文件；未修改实现或历史证据，未再次运行四个完整物理场景，未读取凭据或请求 API。

## 结论

适配器的 mailbox/pending/来源事件与 HOL 定义一致，前次发现的任意 `source` 对象注入已经通过精确类型、冻结原始字节 SHA256 和 identity 检查收口。本次未发现四条实际轨迹中的权限、授权顺序、完成或几何反例。

有一个 P2 未决：执行审计尚未独立连接源码动作与命令签发。应修复后再声称完整的“原始回复—原始源码—协议—实际动作”有限迹对应已由审计逐项核验。这是有限存档审计中的具体缺口，不是要求完整 Python 或连续物理精化。

## P2：源码返回值与命令签发之间缺少关联检查

位置：`audit_execution.py:82–86`、`:98–100`；相关驱动：`physical_binding.py:93–107`、`:122–133`。

审计用日志给出的 `prior_mode` 和 `facts` 重算 `raw_action/raw_next`，但未维护每机器人的源码模式链、未根据已核验观察/core 重建事实，也不检查 `physical_intent`。`command_issued` 只存储命令并检查 0.10 s 投递延迟，没有把命令的 intent/scope 连接到对应源码动作和 Issue 事件。因此目前 plant 重放能说明“存档命令产生存档运动”，但独立审计不能说明“这些命令由所记录的源码动作产生”。

只读负对照已经复现：在内存解码层，对 `none` 场景 t=1.5、机器人 A 的第一个 Proceed `source_step`，将 `ObservationUsable` 改为 False，用同一原始源码解释器重新计算，得到 `raw_action=Brake`；保留 `physical_intent=Proceed`、命令及全部 plant 记录。现有 `audit()` 对这条变体仍返回 `passed=True`。测试只截取一个已有场景，实际执行原审计的源码、plant 及几何检查；原文件哈希读取保持不变、报告写入被拦截在内存。这是校验和阶段之后的语义负对照，并非声称可以绕过文件哈希。

建议：在审计器中维护 per-robot 模式、已接收观察、最近源码决策和已签发 intent；从这些状态及已核验 core 重建本场景使用的事实和动作到 movement 的映射；在命令签发时核对 robot、intent、scope 与来源决策，并将区内 Proceed 关联到对应 Issue；由 Grant 递增重建 generation，关联后续 Apply。保留上述负对照，确保审计拒绝它。无需重新生成四条物理轨迹。

## 已独立核对的证据

- `test_binding.py` 的 7 项测试通过，包括拒绝未验 source。
- 24 个冻结 parser cases 全通过；重新执行 11 个轻量机制见证，完整结果与 `mechanisms.json` 一致。
- 对四条 gzip 轨迹逐行重新核对 5,661 个 adapter 事件与 HOL 表，并检查 core/mailbox 状态连续；四条 motion 时钟均从 0 连续到 58.9 s，步长 0.01 s。
- 首次授权按 none、retained-B、invalid-then-B、late-B 为 A/B/B/A；实际消息序列与预先 cases 完全相同。晚 B 在 0.06 s 到达，初次有效授权在 0.05 s，确实位于首次 Validate/Commit 之后。
- 存档统计确有 7,352 个 `source_step`、452 个 `source_select`、24 个签发命令、24 个应用命令及各 8 个 release/complete；逐场 summary 与汇总内结果一致，轨迹 SHA256 均匹配。
- `effective-parameters.json` 与冻结参数代码的当前派生结果完全一致；`physical-driver.diff` 精确等于实际 v2 与新增驱动的两个 `run_episode` 函数差异。
- 37 项运行前依赖 SHA256 全部匹配。实际导入的仓库 Python 模块均被覆盖，包括 DSL language/model/assurance、plant/controller/oracle/simulation；动态加载的 diagnostics 亦在清单。没有发现物理运行的实际仓库依赖遗漏。
- HOL 构建日志显示成功导出 77,760 行；构建源哈希清单的六项当前全部匹配，含 v2 与 CKA 父理论。审查了有限比对枚举/编码与 HOL 导出的结构；本次未重建 HOL 或重复全域执行。已有全域报告为零差异。

## 范围与次要改进

驱动代码确实把 adapter 返回的协议事件用于 Issue/Apply，并以实际应用后的 intent 推进 `RobotPlant`；审计的 plant 重放和独立 OBB/连续区间几何计算不是读取驱动的“通过”布尔值。共享原始解释器和 reference plant、独立几何这一依赖关系已准确说明。47,120 个 plant 间隔及 212,040 个几何 pair 区间来自既有执行审计；本次负对照完整重放其中一个存档场景，未把它当作新增物理试验。

原始回复明确标作既有内容在指定仿真时刻离线重放，`maximum_api_requests=0`，没有看到把它误称新增在线 LLM 样本、真实网络延迟重现或硬件试验的表述。

`audit_execution.py:159–160` 对机制结果仍只读取 `expected_outcome_observed` 标志；本复核已独立重算确认当前文件正确，建议把此重算或基于 rows 的再判定纳入可重复审计。类似地，可在审计入口断言结果名称与预先四个 cases 一一对应，并检查参数副本等于冻结派生结果，避免汇总遗漏或非运行参数漂移被接受。这些建议不否定当前已逐项核对的存档。

来源/功能、权限安全与条件进展仍须分别报告：跳过 binding 或重置 pending 可破坏来源对应而保留合法权限；wait-empty 拒绝提供 Service，违反接口不等待要求，但没有反驳以已提供 Service 为前提的 HOL 授权定理。无限消息洪泛、真实并发、硬件和完整运输终止继续在明确排除范围内。

## 修复后针对性复核：P2 已关闭

2026-09-22 追加。以上发现保留为修复历史；本节为当前结论。检查了新增 `source_link_audit.py`、四个负对照测试及 `audit_execution.py` 的接入。源码输入事实现由已核验采样/接收记录和 core 重建，fresh 与整车 clearance 使用独立实现；审计维护每机器人模式、released、actuator intent/since 和最近签发命令，重算源码动作及 movement，并比较 `physical_intent` 和命令 intent/scope。区内命令消耗对应 Issue/Apply 记录，Grant generation 与 permission_version 由事件重新累计。原先源码动作与实际签发命令可以脱节的具体路径已被关闭。

本复核实际运行 `python -B -m unittest discover -s formal-artefacts/amr-runtime-binding/tests -p test_source_link_audit.py -v`：四项全通过。其中 `test_rejects_self_consistent_output_from_false_observation` 保留原负对照的关键条件——修改 ObservationUsable 后仍用原始解释器重算 raw_action/raw_next——现在被事实重建检查拒绝。其他负对照覆盖伪造输入事实、动作到 movement 不一致及无源码来源的命令。

还完整运行了一次增强 `audit()`，只读取原四条存档，把唯一报告写入拦截到内存，未重跑物理场景、未修改存档。四条均通过，重算报告与当前 `execution-audit.json` 完全一致，包括 5,661 个适配器事件、7,352 个源码 step 输出、24 次命令应用、47,120 个 plant 间隔和 212,040 个独立几何 pair 区间。执行审计器 SHA256 为 `e75b59a095e274176762ff54789a5dae1ae0aac10c68c41934bda39f2cce17ed`，来源链审计器 SHA256 为 `8b51e1d86c2f4bcb7795ef49f972d35e1e8e751f28f829f5c7ffa371b19d41a2`。

前次三项次要建议也已落实：11 个机制见证重新执行后经 JSON 规范化逐项比较；四个结果与预先 case 名称及数量对应；逐场 summary 和参数副本一致性均检查。新审计脚本以事后自身哈希标识，没有伪装为物理运行前清单中的依赖。

当前没有未关闭的明确阻塞问题。README 与本轮中文结果报告将结论限定为当前串行固定任务、抽象接口证明、有限对应和四条参考 plant 存档重放，并明确保留持续 intent、真实传感器/调度、完整 Python 和连续物理精化边界；未发现范围过强的新增主张。源码解释器和 reference plant 仍是共享依赖，独立几何和来源事实重建不会使这些依赖自动消失。
