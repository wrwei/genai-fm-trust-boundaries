# AMR受限监督器：原始候选、模型对应与源码执行

这是参考仿真之后的语义保障阶段。固定语法、规则验收、独立目标解释器和源码驱动的物理闭环已经实现。本目录中的候选均为助手构造的机制测试，**不是独立真实LLM生成试验**，不能估计生成成功率。

依据：[实施计划与v1.1规格](../../literature/scholar_search_2026-09-10/followup/research_amr_supervisor_plan_2026-09-15.md)、[研究结果](../../literature/scholar_search_2026-09-10/followup/research_amr_supervisor_results_2026-09-15.md)。原[AMR参考环境](../amr-corridor/README.md)保持原样；新运行器导入其plant、传感／执行器类型和独立几何评分。

## 复现

Python标准库，无需新增安装。使用新输出目录，避免覆盖旧证据。

```powershell
Set-Location -LiteralPath 'formal-artefacts/amr-supervisor'
python -m unittest discover -s tests -v
python run_supervisor_suite.py --output results/my-reproduction
```

本机也可使用：`C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

最终入口：[summary.json](results/supervisor-2026-09-15/summary.json)、[manifest.json](results/supervisor-2026-09-15/manifest.json)、[测试日志](tests_final.log)、[独立审查](review_report.md)。每个闭环保留结果JSON与压缩JSONL；每个可解析候选保留评估与完整提取模型。源码按UTF-8原始字节解码，验收哈希与候选索引的文件哈希一致。

## 语法和控制边界

源JSON恰含schema、select、step；schema为`amr-supervisor/v1`，规则规格版本另记为`amr-supervisor-obligations/v1.1`。when使用布尔常量、白名单谓词、not／and／or及括号，解析器拒绝函数调用、任意代码、重复键和不受支持字段。两个函数分别最多8条有序分支；step共享规则并接收当前模式。ModeStopped等模式谓词由当前模式内部导出。

选择返回SelectA／SelectB／Defer；逐车返回Request、Proceed、Brake、Resume、Release、Finish及下一模式。有效观测、整车清空、预约状态和Halted依据来自固定接口，源程序不能改写这些值或物理参数。

原始源解释器递归执行不可变表达式并取首个满足分支；目标模型编译为后缀栈指令，其第i条守卫包括此前所有分支条件的否定，目标解释器收集所有启用结果。两者不共用求值函数，但共用解析后的不可变语法与词汇；这不是独立证明了文本解析器。

## 三项验收分别报告

| 项目 | 含义 |
| --- | --- |
| source_policy_pass | 原始程序是否满足已认可的动作／模式义务，包括禁止无故一直停止 |
| model_policy_pass | 提取模型的所有启用结果是否满足同一义务，且每个输入有结果 |
| correspondence_pass | 每个输入的目标结果集合是否恰为源码单一结果；重复相同结果不算行为变化 |

检查域为32组选择输入，加7种模式×256组逐车输入，共1824组。它包含不能同时出现在真实物理系统中的布尔组合，既不是已证可达域，也不是无界进展证明。固定规则本身仍需需求认可；源码／模型一致不等于规则充分。

当前共有9份构造候选：两份合格等价程序、六份语义／进展缺陷、一份语法不受限输入。另有三项明确命名的提取故障：遗漏前序否定；双方都有申请时把A改为B；翻转观测有效谓词。它们用于检验验收链，未声称任何外部工具具有这些故障。

## 物理接入与对照

SourceSupervisor在创建plant之前重新验收源文本，通过后只执行源码。目标模型不替代运行中的源码；每步保留原始动作和下一模式、当前检查及实际应用结果。Request和Select共同触发预约，Release释放预约，Finish触发任务完成，Resume之后仍需下一监测周期的Proceed才能运动。

同接口手写监督器是环境校准对照；其step直接执行认可规则，并非独立算法竞争基线。A先、B先、临时人员阻塞、观测中断和永久人员阻塞各做源码／手写配对；等价源程序另跑一次正常闭环，共11个相关运行。有限验收的人工缺陷候选不进入合格候选部署。

模式协议的请求／停稳／恢复过程使运行时间与上一阶段参考控制不同。对照双方采用相同新协议、相同物理模型及固定外生事件；不把两个不同阶段的完成时间当成LLM效率差异。

## 保留的规格失败见证

初稿v1通过全部有限检查，但没有“到站后先制动”的步骤。机器人到达实际终点后持续Proceed，无法建立当前Halted接口所需的持续有效Brake依据，120秒仍未完成。保留[原代码、源码与完整失败轨迹](development/spec-v1/README.md)，可单独复现。

v1.1显式增加到站制动义务，保留原Halted判定和物理评分。旧程序作为goal_stop_gap加入最终缺陷目录，不能将这次开发期规格修正伪装成固定规格下的LLM修复成功。归档重放使用旧加载器的换行规范化文本，归档result中的source_id指提交文本，manifest另存原文件字节哈希；最终新运行器直接保留UTF-8源码字节。

## 限制

本阶段没有真实LLM调用、新HOL／Isabelle证明、文本解析证明、物理抽象关系证明或完整制品／通信绑定保证。选择偏好由固定A/B输入给出，没有自然语言语义评价。运行日志中的source_id用于来源追踪；它不等于独立执行器已验证完整源码／规格／适配器链。

人员事件仍固定在仿真t=10 s开始。新模式协议下，机器人此时可能处于汇入转向段；直线停车公式只有在明确的直线接近域内才评价，否则记录“不适用”，不能把实体间的x方向距离直接当成直线制动保证。闭环碰撞仍由独立连续轨迹判定，数值结果不是普遍人车安全定理。
