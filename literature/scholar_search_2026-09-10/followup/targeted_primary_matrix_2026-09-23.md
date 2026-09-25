# 针对性全文证据矩阵（2026-09-23）

## 范围与取样

这轮调研检验当前批判性综述的三个问题：谁接受生成物、接受结果实际支持什么主张、从局部结果到系统保障还需什么证据。采用**目的性最大差异取样**，不是新的系统检索或领域频率估计。先从已有 82 条带正文定位的比较记录中选取不同角色、检查时机和最强反例，再用题名/主题定向查找用户意图与规格验证工作。20 项研究含 18 项既有记录（编号 C）和 2 项本轮新增（N）。既有记录的详细书目、版本、读取深度和定位见 [comparison_records.json](comparison_records.json)；本轮重新打开一手正文或出版页抽查所列关键位置。未经独立运行的结果均为作者报告。检索/核查日：2026-09-23。

纳入标准：至少一个工作流明确涉及生成式模型与形式化、测试、运行时约束或保障论证的连接；另保留 ACCESS 和 CLARISSA 持续保障等非生成式/混合背景先例，以检验“连接尚无人做”的说法。每一研究族只记一次，不把预印本和发表版累加。取样并非随机、文献可能仍有遗漏；不能从 20 项推出该领域的比例或“无人解决”断言。A–F 仅作多角色分析标签，不改变 363 条旧语料的主标签。

本轮使用公开网页检索，完整输入的第一组查询为：

1. `site:arxiv.org/html formal verification generated code specification faithfulness LLM formal methods 2025`
2. `site:arxiv.org/html LLM safety assurance case evidence runtime monitor 2026 formal`
3. `site:dl.acm.org generative AI formal methods assurance case review 2025 2026`
4. `site:arxiv.org/html agent runtime formal shield LLM verified policy 2025`

随后用精确题名检查 Astrogator、Alloy 测试、ToolGate、SynCode、AESOP 和 CLARISSA 的版本/发表状态，并直接读取作者预印本或出版社正文。检索未保存全结果页或逐项排除日志，因而不能称为可复现的系统筛选。未纳入同轮出现的 Ada/SPARK 注解补全研究，是因为当前 20 项中已有 Dafny 注解与代码验证同类工作，而需要优先纳入会挑战规格忠实性论点的研究；一般模型安全评价和宽泛治理框架不满足本表的制品—检查—系统主张比较单元。题名也叫 ToolGate 的科学基准构造论文与合同式工具调用论文不是同一研究，未合并。

## 逐项比较

| ID、研究与角色 | 生成/处理对象；接受权威 | 所能支持的主张 | 关键剩余义务；原文定位 |
| --- | --- | --- | --- |
| C35 [Clover](https://arxiv.org/html/2310.17807v4)，A/C | 代码、注解和文档；Dafny 验证及重建式一致性检查 | 对给定注解的程序验证与多侧一致性筛选 | 同源生成的三者可能一致而偏离用户意图；当前实现**不含单元测试**，原文将其列为未来扩展；§3.1–3.2、§4、§6、附录 0.A.1 |
| C02 [FVEval](https://arxiv.org/html/2410.23299v1)，A/C | SVA；Jasper 对 RTL/参考断言作等价或蕴涵检查 | 基准中的形式判定，不是单纯 LLM 自评 | 参考断言、环境假设、等价与单向蕴涵的区别；§3.2–3.4 |
| C41 [Lahiri 等](https://arxiv.org/html/2406.09757v2)，A | 候选 Dafny 规格；Dafny 与参考测试/变异比较 | 在样本范围内检出部分过弱或错误规格 | 测试与变异有限，验证失败也不必然构成真实反例；§I-C、§II-A–C |
| N01 [Astrogator](https://arxiv.org/html/2507.13290)，A；新纳入 | LLM 生成 Ansible，人工编写/审阅形式查询；符号解释器和统一算法 | 对支持的 Ansible/查询语义判断程序是否满足形式查询 | §3–4 的用户审批与未规定细节检查是**拟议端到端流程**；§6.3 实验使用手写查询并接受所有满足查询的程序，不能称已实测整条人审链。知识库、模块语义和用户认可仍须信任；§3–4、§5.2–5.5、§6.3 |
| N02 [Cunha–Macedo](https://arxiv.org/html/2510.23350)，A/C；新纳入 | 从自然语言生成 Alloy 正反测试；Alloy 执行与隐藏 oracle 比较 | 对四个小型结构域模型的错误规格提供反例式经验验证 | 测试集不是规格完整性证明；作者承认 Alloy4Fun 例子偏教育性，且负测试受需求歧义影响；§3.2–3.4、§4.4–4.6 |
| C49 [TR2MTL](https://arxiv.org/html/2406.05709v1)，A | 交通规则转 MTL；解析与参照公式评价 | 定义片段内的翻译质量评价 | 规则歧义、感知/地图假设；解析成功不等于意图忠实或部署动作安全；§IV–V |
| C65 [Herald](https://arxiv.org/html/2410.10878v2)，B/A | 自然语言与 Lean 陈述；Lean 编译、回译/NLI、人审 | Lean 可接受形式陈述；对指定验证集内通过验证的译文有人审结果 | 形式可编译与语义忠实分离；ProofNet 的 185 条验证题目每题尝试 128 次翻译并只收集首个通过验证的结果；Herald 有 151 项通过，其中 101 项人审为正确、24 项轻微错误、26 项重大错误，不能视为随机抽样质量率；§4.1.2、附录 D、Table 4 |
| C71 [DeepSeek-Prover-V2](https://arxiv.org/html/2504.21801v2)，B | 子目标与 Lean 证明；Lean 最终检查 | 在固定形式目标/允许前提下证明成立 | 题目翻译、axioms、admit/sorry 和奖励漏洞要分开；作者修订版报告特定接口误计；§2.1–2.3、§3.2 |
| C05 [SynCode](https://openreview.net/forum?id=HiUZtgAPoH)，D | 语法约束解码；CFG/DFA 掩码 | 在论文条件下约束输出语法前缀 | Theorem 2 只谈有效前缀扩展，不保证生成终止为完整语法正确输出，更不保证程序语义或需求满足；作者正式版为 TMLR 2025，方法定理见 §4.3–4.5（[可读预印本](https://arxiv.org/html/2403.01632v4)） |
| C20 [SafePlan](https://arxiv.org/html/2503.06892v1)，D/C | 机器人计划/代码；逻辑化提示和 LLM 推理 | 经验性拒绝与任务表现 | 结构化逻辑提示仍由模型判断，不能写成独立形式验收器；§III–V |
| C27 [PLC 测试生成](https://arxiv.org/html/2405.01874v1)，C | PLC 测试和断言；编译/执行、覆盖与人工检查 | 所运行测试上的经验依据 | 测试 oracle 与覆盖率不能推出功能正确；§III–VI |
| C06 [ToolGate](https://arxiv.org/html/2601.04688v1)，E | 工具调用与符号状态；前后条件运行时检查 | 受合同约束的内部符号状态提交 | §3/附录 E 的外部工具先执行后验收：拒绝结果写入内部状态不等于撤销外部副作用；合同及观测忠实性待证；§3.2、3.4、附录 E/G |
| C07 [VeriGuard](https://arxiv.org/html/2510.05156v1)，A/E | 生成策略函数；离线 Nagini/Viper 验证，在线动作拦截 | 在给定合同和已正确填参的策略下实施阻断/重规划 | 在线参数由 LLM 从非结构化状态提取，映射正确性不随策略证明自动成立；§3.2–3.3 |
| C18 [AESOP](https://arxiv.org/html/2407.08735v1)，E | LLM 选择恢复目标；快速检测与保持备用计划的 MPC | 在论文初始可行/延迟等假设下，在线保持恢复可行性 | 不是“运行时只会阻断”的例子；语义检测准确性、物理模型和延迟界另需证据；§III–IV、Theorem 1、附录 E/H |
| C10 [Trusta](https://arxiv.org/pdf/2309.12941)，F/A | LLM 辅助论证形式化；Prolog/Z3/MONA 等检查 | 对所编码论证约束的逻辑分析 | 语义提取和叶子证据真实性未由结构检查自动建立；预印本 §3.2；已核[正式版 DOI](https://doi.org/10.1016/j.scico.2025.103288) |
| C11 [ACCESS](https://arxiv.org/html/2403.15236v1)，F；背景 | 工程产物、形式分析与动态论证；运行时评价服务 | 对已建模的论证节点持续给出有效性状态 | §3.7 明示 non-invasive，控制响应由系统决定；不等于逐动作门禁；§3.4–3.7、§5.6–5.7 |
| C14 [CAF](https://ojs.aaai.org/index.php/AAAI/article/view/41151/45112)，F | 形式安全断言、依赖图和组合/失效传播 | 提出持续更新证据和 CI/CD 门禁机制 | 组合函数对具体性质及组合算子的正确性需证明；§Composition Calculus 的最小值是示例，不能当一般 voting 保证；PDF pp.3–6 |
| C15 [CLARISSA 语义分析](https://www.cambridge.org/core/journals/theory-and-practice-of-logic-programming/article/automating-semantic-analysis-of-system-assurance-cases-using-goaldirected-asp/1515C06F4BC02013C302239B8C6C4562)，F/A；背景/混合 | 论证语句的 object/property/environment；LLM 辅助提取，s(CASP) 分析 | 对已编码语义的逻辑性质给出检查 | 原文 §5.1 明说 LLM 支持有限；提取忠实、证据真值和系统行为仍另需论证；§5.1–5.4 |
| C16 [CLARISSA 持续保障](https://www.csl.sri.com/~rushby/papers/sassur24.pdf)，F；背景 | 证据/论证依赖；ETB2 检测变化并重跑下游服务 | 已建模依赖内的增量更新先例 | 缺失依赖不会凭传播机制自动发现；变更重检不等于每次动作的原子授权；PDF pp.9–11 |
| C01 [Forge v2](https://arxiv.org/html/2606.22413v2)，A；作者相关 | Java 控制器提取成多个形式模型；Dafny/Z3、FDR4、Isabelle | 多后端分别检查已编码义务 | §5.5 明确源到模型的语义保持尚未作为一般定理建立；作者相关工作不能当独立佐证；§3–4、§5.5–5.7 |

## 横向判断及对正文的约束

1. **规格忠实性已有实质应对，不是空白。** Astrogator 提议用户审阅形式查询，Lahiri 等用测试/变异评价候选规格，Cunha–Macedo 用正反例测试找错，Herald 对指定验证集中通过验证的译文进行人审。它们解决的是不同片段，均不能让“用户真实意图”自动成为已证明事实。正文应将缺口定位为各片段证据如何连接到特定部署主张。
2. **接受权威不能由角色名推断。** FVEval 含正式形式检查，SafePlan 的逻辑化提示仍主要由模型裁决，SynCode 的保证是语法级；ToolGate 的“状态接受”不等于外部副作用可回滚。
3. **运行时与保障先例已相当强。** VeriGuard 联合离线证明和在线拦截；AESOP 在延迟下保持恢复可行性；ACCESS 动态评价；CLARISSA 与 CAF 传播失效。论文不能将这些连接描述为尚未实现。仍可比较其参数/观测/物理语义、原子提交、组合规则和进展假设各自何处需补证。
4. **论点应使用条件性语言。** 有限目的性样本足以展示反例和分析框架的适用性，不能证明“所有研究都遗漏某义务”，也不能从旧语料 4/363 与 176/363 的标签差距推断领域成熟度。

新增 N01、N02 的具体版本与限制以本轮一手正文为准。18 项 C 记录的详细提取在既有 JSON 中；本轮只抽查关键位置，未重跑外部工具、未做独立双人编码。正式投稿前，作者应逐条复核本表涉及的关键解释和引用版本。
