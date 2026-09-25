# AMR受限监督器：语法、验收与闭环计划

> 使用 writing-plans、TDD及 subagent-driven-development 完成这一独立实施阶段。用户已授权继续，沿用local目录，不提交、推送或清理；旧AMR参考制品与论文候选保持指纹不变。

**Goal:** 实现原始受限程序的规则验收、源码／目标模型逐输入比较和合格候选闭环部署。

**Architecture:** 源解释器执行不可变语法树，独立目标解释器执行含前序否定的后缀栈指令；验收器分别核查源码、模型和对应。新闭环使用原plant／oracle并接入选择、Request／Release／Finish和模式决策。

**Tech Stack:** Python标准库、unittest、JSON受限源程序。

**Spec:** [AMR场景](research_amr_scenario_2026-09-15.md)、[评价协议](research_amr_evaluation_2026-09-15.md)及[已完成参考环境](research_amr_results_2026-09-15.md)。

## 固定接口和范围

新增代码位于`formal-artefacts/amr-supervisor/`。旧`amr-corridor/`所有现有文件不改；闭环在新目录扩展其运行器，并记录基线源码身份。

源JSON的顶层严格为`schema`、`select`、`step`；schema=`amr-supervisor/v1`。选择规则含when、action；逐车规则含when、action、next。两个函数分别最多8条有序分支，源分支总数最多32。逐车函数共享同一组规则，以当前模式为参数，因此每个模式最多8条，避免复制7份规则。这是原模式函数设计的具体化。

模式：Idle、Waiting、Traversing、BrakeRequested、Stopped、ResumePending、Done。step输入8个布尔谓词：ObservationUsable、PedestrianBlocked、OwnReservation、Released、BodyClearOfZ、Halted、AtGoal、TaskActive。Mode加模式名的布尔量由解释器从模式导出，不由外部事实传入。

选择输入5个布尔量：OwnerFree、RequestA、RequestB、PreferA、PreferB。动作SelectA／SelectB／Defer；双方均有合法申请时A或B均满足许可义务，偏好只是建议。这允许构造“两个模型都满足安全许可，但行为不一致”的对应反例。

step动作Request、Proceed、Brake、Resume、Release、Finish；when只允许布尔常量、白名单名称、not／and／or及括号。禁止调用、属性、比较、算术和任意Python执行。表达式最长512字符、AST最多64节点、嵌套最多8；JSON最大200KB，拒绝重复键和额外字段。

## 认可的逐车规则

安全阻塞指ObservationUsable为假、TaskActive为假或PedestrianBlocked为真。下列义务按明确优先关系约束所有抽象输入；全部输入是有限检查域，不称已证可达集合。

1. 安全阻塞时Brake；Halted真时下个模式Stopped，否则BrakeRequested。
2. 无阻塞且AtGoal、Released为真但Halted为假时，Brake→BrakeRequested，建立完成所需的停稳依据。
3. 无阻塞且AtGoal、Halted、Released都真时Finish→Done。
4. 前三项不适用且OwnReservation、BodyClearOfZ都真时Release→Traversing。
5. 前四项不适用且当前BrakeRequested、Halted假时继续Brake→BrakeRequested。
6. 前五项不适用且既无OwnReservation也无Released时Request→Waiting。
7. 前六项不适用且当前Stopped时Resume→ResumePending。
8. 其余情形Proceed→Traversing。

规格版本现为v1.1。初稿v1遗漏第2项：源码和模型均通过有限检查，但到站后持续Proceed，无法建立需要持续有效制动的Halted依据，任务未完成。原代码、候选和120秒失败轨迹保留在`formal-artefacts/amr-supervisor/development/spec-v1/`，属于设计调试期间的规格充分性失败见证，不是LLM错误。此修正增加到站停车义务，保持Halted物理判定及原安全规则；正式v1.1评价单独运行。

Released由预约管理器成功释放后设置，不由p写入。Finish只有实体目标／停稳及有效观测也通过独立检查才完成任务。Resume只是重新申请运动意图，经ResumePending的下一次Proceed后生效。未通过验收的候选没有进入正式合格候选闭环的资格；其原始缺陷不因执行Brake而清零。

## Task 1：严格语法与源码解释器

创建`language.py`、`tests/test_language.py`，输入源文本返回不可变Program／Rule／Expr元组结构。接口：parse_program(text)、eval_select(program,facts)→str、eval_step(program,mode,facts)→(action,next_mode)。事实必须是精确布尔值及精确键集合；缺少匹配规则抛出明确错误。

- [x] 写拒绝外部调用、重复JSON键、错误模式／动作、非布尔输入、缺省分支以及保留首匹配优先级测试；先运行红灯再实现。
- [x] 使用ast.parse仅解析表达式；逐节点白名单转换为不可变元组，不使用eval。
- [x] 测试模式谓词由内部导出；保存测试命令、红绿记录及源码解释范围。

## Task 2：独立模型提取与目标执行

创建`model.py`、`tests/test_model.py`；不调用源解释器求值。接口extract_model(program,fault=None)、model_select(model,facts)→所有启用动作的tuple、model_step(model,mode,facts)→所有启用(action,next)的tuple。

- [x] 红灯测试同时可满足两条分支：源只取首条，正确目标只有一个启用结果，漏前序否定目标有两个结果。
- [x] 编译条件为后缀栈指令；第i条目标守卫是g_i与所有前序g_j的否定之合取，目标关系求所有启用结果。
- [x] 支持明确标记的提取故障omit_priority、choose_b_when_both、invert_observation_tests。最后者翻转step中ObservationUsable的极性；不声称真实工具存在这些错误。
- [x] 使用与源不同的栈执行算法，测试模式转移及真假表达式；保存模块报告。

## Task 3：事前规则与有限验收

创建`assurance.py`及`candidates/`、`tests/test_assurance.py`。完整域：32组选择输入＋7×256组逐车输入，每个可解析候选共1824组。源码和模型分别按独立义务判定；对应要求目标启用结果恰为源码唯一结果。

- [x] 用认可规则手写可审查的良性候选及等价表述；另构造忽略行人、始终Brake、过早Release、未停稳Finish和不受限语法候选，明确标注为人工／助手构造。
- [x] 写有限验收测试，确认良性候选通过、各错误有具体见证；模型通过但源失败，以及双方满足许可却行为不一致，必须能够分开记录。
- [x] 保存每个候选的原始源码哈希、结构通过／失败、源码义务、模型义务和对应结果，不能以回退结果替代原始验收。

## Task 4：接入物理闭环与证据

创建`closed_loop.py`、`run_supervisor_suite.py`、`tests/test_closed_loop.py`、`README.md`及独立results目录。执行时间／plant／oracle沿用冻结参考环境；监督器负责实际选择、请求、释放、完成和模式迁移。

- [x] 先写合格候选两种先行偏好、临时人员阻塞、无效候选拒绝部署测试；通过后接入现有真实运动与独立评分。
- [x] 固定规格身份和候选身份再运行；每步记录原始动作／模式、当前检查及实际应用结果。模型求值仅作评价，不偷偷代替源码程序执行。
- [x] 运行合格候选与同接口手写监督器的配对正常／人员恢复闭环；保存事件、连续轨迹和源码／模型身份。
- [x] 完成独立审查、必要修正与指纹／轨迹核查。报告“有限域内对应检查”，不称新定理、源码解析证明或真实LLM成功率。

不把这些构造候选称为实际LLM试点。 完成后才具备开展事前冻结的生成／修复实验的接口。
