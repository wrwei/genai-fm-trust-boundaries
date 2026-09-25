# Review 实质修订稿（独立候选版）

**状态更新：** D1–D9现作为分批候选与研究依据保留；当前待审阅措辞和篇幅取舍统一见[Review独立整合稿](review_integration_2026-09-13.md)。不要将两版段落同时合入。

日期：2026-09-13。对照正文基线 `442ec0e`；本文件未写入正文或主书目。以下保留各批原候选、来源和当时的后续安排；部分安排已经完成，当前进度见整合稿及研究总览。

**判断：维持 critical review 的定位和现有章节顺序。** 当前首先需要把已有研究的机制与证据边界讲准确，再引出具体研究义务。小规模证明用于检验本文论证；仅凭这批证明不足以把文章改成提出完整新框架的研究论文。

下列英文是可供作者审阅的正文候选。每组注明替换范围，避免把旧句与新句同时保留。证据均区分“主源内容已核对”“作者报告”和“本项目实际执行”。本次不声称完成独立人工双人编码、全部330条全文审阅或外部实验复现。

## D1：补充检索如何进入方法部分

**位置：** `sections/02-method.tex` 的 Synthesis and Limits of Inference 中，解释补充文献不进入363分母的段落之后。保留原快照局限；增加以下段落。

```latex
A separately recorded supplementary search supports the qualitative synthesis.
The saved Google Scholar pages contain 434 result appearances across 47 pages,
representing 327 distinct result URLs. These were supplemented with three
previously identified works to form a 330-record bibliography and screening
register. Record-level decisions are 169 retained for review, 125 contextual,
27 excluded, seven duplicate records and two unresolved records. These are
screening decisions, not 330 eligible independent studies or 330 full-text
reviews. An overlapping set of 82 comparison records documents selected
workflows and claim boundaries, with source versions and section locators.
Neither register is added to the snapshot denominator.

The supplementary register preserves query/result records, bibliographic
metadata, screening reasons and the depth of source inspection. It does not
provide independent duplicate human screening or a reproducible census of
Google Scholar. Later targeted bibliographic rechecks are recorded separately
from the saved search pages. We use these materials to correct and enrich
the synthesis, without estimating field prevalence from their frequencies.
```

依据：[调研总入口](../README.md)、[检索页记录](../query_results.md)、[候选筛选](candidate_screening.md)、[比较记录](comparison_records.json)。47页为当轮保存页数，不能写成47个独立检索式；327是URL去重，不等同论文实体去重。9月12日两项书目复核和9月13日工具/定向来源核对均不计入这47页。

## D2：把阶段、检查对象和执行权分开比较

**位置：** `sections/03-taxonomy.tex` 的 Comparing What Acceptance Means 小节，现有比较表后的解释段落。新增，不重新分配363条初始标签。

```latex
The primary roles are supplemented by orthogonal comparison fields: when a
claim is established, when its evidence is used, the accepted object, the
checking authority, the supported property, the mapping from observations
to formal inputs, the point of intervention, and the treatment of changed
evidence. One workflow may span several phases. For example, a policy can be
verified before deployment and evaluated on each proposed action during
operation. These phases do not determine the strength of the guarantee;
the theorem or evaluation, its assumptions and the implemented interface do.
```

依据：C07 VeriGuard、N03 ACCESS、N02 CAF；具体机制见D3、D4。将这些字段用于选定文献的比较，不声称全语料已按新字段重新编码。

## D3：重写运行时部分的应用概述

**位置：** 替换 `sections/08-runtime.tex` 从“The snapshot assigns”至“These examples are illustrative”的开篇段落。保留后面的 Observation and Enforcement；删去其与新段重复的概括即可。

```latex
The snapshot assigns \CorpusE{} records to runtime activity, but the cited
systems check different objects and intervene at different points.
Hafez et al. use reachable-set over-approximations to check and repair robot
plans, with a previously safe continuation and braking as fallback; their
collision-avoidance result is conditional on the stated dynamics, uncertainty,
perception and stopping assumptions~\citep{hafez2025safe}.
AESOP instead uses multi-contingency model predictive control to retain
recovery options while a slower language-model decision is pending. Its
control theorem depends on feasibility, recovery-set and delay assumptions;
it does not certify the semantic correctness of the model's interpretation
of an anomaly~\citep{sinha2024real}.

For tool use, ToolGate combines precondition filtering with post-execution
checks before accepting a result into symbolic state~\citep{liu2026toolgate}.
Rejecting that result does not by itself undo an external effect that has
already occurred. Verified Tool Calls addresses a different failure point:
after an ambiguous response, it inspects postconditions before retrying and
reuses an idempotency key. Its protocol trusts explicit success responses,
and protection against duplicate effects depends on state visibility and
service-side idempotency~\citep{mansoor2026verified}.
VeriGuard connects pre-deployment checking of generated policy functions
to runtime interception. Its language-model-based extraction of policy
parameters is a separate interface whose correctness does not follow from
the policy proof~\citep{miculicich2025veriguard}.

Other approaches supply diagnostic or statistical evidence. RvLLM combines
domain rules and forward chaining with model-based interpretation and
follow-up queries~\citep{zhang2025rvllm}. In the inspected version, RoMA
estimates local probabilistic robustness and evaluates BERT classification;
it is relevant statistical background, rather than evidence of monitoring
generative output streams against domain rules~\citep{levy2025statistical}.
BRT-Align formulates latent reachability and implements detection and
steering with learned approximations, requiring a distinction between the
ideal model and the implemented approximation~\citep{karnik2025preemptive}.
RSP-M derives monitoring signals from emitted reasoning and action text,
not directly from hidden attention weights~\citep{zhou2025reasoning}.
SAFE-AI combines pattern and AST-based checks with agent simulation and
reported experiments; it should not be reduced to an internal-signal
detector or described as only a conceptual proposal~\citep{navneet2025rethinking}.
These examples are selective comparisons of mechanisms and evidence, not
an exhaustive inventory or independently reproduced benchmark.
```

此稿同时修正原文的**低估与高估**：承认可达性/MPC的条件定理、BRT-Align的实际干预以及SAFE-AI实验；也保留输入映射、外部副作用和学习近似的适用条件。不能按“在线”“统计”“含LLM”等标签直接判断保证强弱。

| 记录 | 主源定位 | 支撑的具体修正 |
| --- | --- | --- |
| C17 | [Hafez v1](https://arxiv.org/html/2503.03911v1)，§II-C、III-A–C、Algorithm 1、Theorem 1 | 可达集、修复与制动；条件避碰 |
| C18 | [AESOP v1](https://arxiv.org/html/2407.08735v1)，§III、IV-A–B、Appendix H | 多备用方案MPC与时延假设 |
| C06 | [ToolGate v1](https://arxiv.org/html/2601.04688v1)，§3.2、3.4，Appendix E、G | Execute在事后Verify之前；符号状态与外部效果分开 |
| C25 | [Verified Tool Calls v1](https://arxiv.org/html/2608.02645v1)，§4、Algorithm 1 | 歧义响应后核验；显式成功直接返回 |
| C07 | [VeriGuard v1](https://arxiv.org/html/2510.05156v1)，§3.2–3.3 | 策略验证与LLM参数映射是不同义务 |
| C23 | [RvLLM v3](https://arxiv.org/html/2505.18585v3)，§2–4、Appendix G | 逻辑推导与模型解释接口 |
| C24 | [RoMA v2](https://arxiv.org/html/2504.17723v2)，§2、4、5.2–5.4、6 | BERT分类鲁棒性；decoder扩展为后续方向 |
| C32 | [BRT-Align v1](https://arxiv.org/html/2509.21528v1)，§3–5、8 | 理想可达性、状态抽象和学习近似 |
| C33 | [RSP-M v1](https://arxiv.org/html/2512.14448v1)，§4式5、§6.4–6.5 | 输出文本指标；指标口径疑问留在卡片，不据此否定全文 |
| C34 | [SAFE-AI v1](https://arxiv.org/html/2508.11824v1)，§VI、IX-C–F、X | 模式/AST检查与所报告实验 |

各项读取版本、深度及未复现状态保存在[比较卡片](comparison_records.json)和[主源日志](comparison_source_log.json)。本次依据已核记录综合，没有把它们改称9月13日重新全文复核。

## D4：用实质比较补足assurance先例

**位置：** `sections/09-gap.tex` 中从“Work connecting formal analysis”到“What distinguishes them”的段落，用以下内容替换。保留前面的概念定义，以及随后关于工程适用性和证据记录的讨论。

```latex
There are established approaches to connecting verification and assurance.
The inspected Trusta preprint describes model-assisted formalisation and
checks of encoded reasoning constraints; the journal version is cited with
its corrected publication metadata~\citep{chen2025trusta}.
ACCESS integrates engineering artefacts, formal analyses and dynamic
argument evaluation. Its demonstrated monitoring service is non-invasive:
evaluation of an argument does not itself enforce an actuator
response~\citep{wei2024access}.
Earlier heterogeneous integration is illustrated by the inspection-rover
case, which organises results from several formal tools through an assurance
case~\citep{bourbouh2021integrating}.

CLARISSA includes semantic analysis of assurance cases using goal-directed
ASP and a related continuous-assurance workflow with an evidence tool bus;
these are related contributions, not independent replications of one
result~\citep{murugesan2024automating,varadarajan2024enabling}.
MCSafe-GSN-HOL reports Isabelle/HOL obligations for argument support,
assumptions, defeaters and acyclicity, together with propagation of changed
nodes to affected parent goals. We inspected its reported method, but did
not obtain and replay its theory library~\citep{yadav2026mcsafe}.
CAF proposes structured assurance records, dependency-based invalidation,
local recomputation and deployment policy gates~\citep{zhao2026composable}.
LLM-supported change-impact assessment also has explicit prior work,
including recommendations for engineers to review~\citep{viger2024supporting}.

These precedents make integration and maintenance substantive comparison
axes, rather than unattempted capabilities. The remaining questions concern
the meaning and validity of each evidence item, the conditions under which
it supports another claim, the completeness of dependency information, and
the connection between evaluation and effective intervention. An argument
structure check, an evidence-refresh mechanism and an action-enforcement
theorem address different obligations; a workflow may supply more than one.
```

**建议比较表内容：** 下表可转为正文表格或用于压缩上述段落。它是一组有依据的选例，不是覆盖率统计；不把“未复现”写成“没有实现”。

| 工作 | 已描述/报告的能力 | 变更或运行阶段 | 仍需区分的保证 |
| --- | --- | --- | --- |
| Trusta | 论证形式化建议；编码推理约束检查 | 本轮核对预印本方法 | 叶子证据与形式化忠实性不由局部推理检查自动保证 |
| ACCESS | 工程制品/形式分析/论证关联 | DSMS周期动态评价，示例为仿真数据 | 评价服务明确non-invasive；执行响应另有责任主体 |
| Inspection rover | FRET、CoCoSim/Kind2、Rodin和AdvoCATE的证据组织 | 开发时专家构造案例 | 通过论证关联工具，不等同证明了所有工具之间的语义翻译 |
| CLARISSA两篇 | ASP语义分析；theory-based连续保障与ETB2 | 对证据采集和更新的工作流支持 | 输入语义与底层证据有效性；两篇有共同技术基础 |
| MCSafe | GSN支持/假设/defeater/无环义务，作者报告Isabelle检查 | 受影响节点向父目标传播 | 本项目未获得可重放理论库；结构有效不能替代部署行为安全 |
| CAF | FSA、证据DAG、hash失效和局部重算 | 部署门禁与在线反馈 | 传播规则适用条件和测量含义；本文未独立证明其一般语义可靠性 |
| Change-impact with LLMs | 变更后受影响节点建议 | 工程师复核与修改 | 小基准结果不建立开放环境下的语义影响完备性 |

依据：U01、N01–N04、N13的[阅读卡片](records.json)，P12/P13的[CASCON核验](../verification/cascon_crosswalk.json)。Trusta的方法细节来自预印本，不能声称期刊逐段内容已重新核对。ACCESS的50ms示例不宜成为这篇review的跨系统性能比较数字，因此正文候选仅写周期评价。

## D5：让RQ3、RQ4有实际先例和可失败的评价

**RQ3位置：** `sections/12-research-agenda.tex` 中“Compare against manual argument construction...”一句替换为下段；保留其前后关于证据字段和人工评估的内容。

```latex
Compare with manual construction and prose generation, but also with an
existing structured workflow selected for the same maintenance task, such
as ACCESS, CLARISSA, CAF or the reported MCSafe dependency mechanism.
The baseline should be implemented or replayed at a declared level, rather
than represented by a weak surrogate without justification. Inject changes
to an artefact, its assumptions and its translation links separately.
Measure missed affected claims, unnecessary invalidations, recomputation
cost and expert review time. A dependency graph can identify changes only
relative to the links it contains; semantic completeness of those links
is a separate evaluation target.
```

**RQ4位置：** 在同节RQ4中，保留“specific pair of semantics”和typed evidence比较，替换“a useful next result...”所在段为下段。D6加入后调整“current bounded example”的概括，明确Python与新增理论的不同证据。

```latex
For runtime composition, separate four obligations: an upper bound on
controlled traces, retention of required controlled behaviours, temporal
progress under scheduling assumptions, and correspondence between the
model and the deployed mechanism. A tractable first study can prove a
projection theorem for a concrete trace model, then test whether an
implementation refines that model. Changes that add a controlled advisory
event, make the guard depend on unavailable advice, or introduce an
unmodelled external side effect provide distinct negative cases.
An equality of finite trace languages can establish the existence of a
represented completing trace; it does not establish that every fair or
actual execution completes. The latter requires a specified execution
semantics and a separate progress argument.
```

**RQ5增补一项：** 现有工具数量与性质覆盖的区分已经合理，保留；增加“full obligation set in one verifier”基线，才能检验多工具的增益究竟来自工具还是新增义务。尚未选定的外部案例和实验规模不写成完成的工作。无必要在本批另造整套平台或开展大范围检索。

## D6：保留CKA目标，但按真实证明状态表述

**位置：** `sections/08-runtime.tex` 中Stating the Guard Algebraically的最后两句，以及 `sections/10-bridge-case-study.tex` 的形式制品状态与末段。不能只把旧引文撤下而不解释下一步证明对象，也不能恢复为不存在的已证明companion。

本批具体证明、反例与最终构建状态统一以[证明修复说明](../../../formal-artefacts/cka-repair/README.md)为准。以下候选对应本批已成功构建的独立会话；目前正文仍保持基线原样。

```latex
To make the proposed boundary precise, consider languages of finite traces,
with parallel composition given by interleaving and projection given by
erasure of events outside a controlled alphabet $C$. Let $G$ select traces
from its input language. If every advisory trace projects to the empty
trace and $G(P\parallel D)\subseteq P\parallel D$, then
\[
  \pi_C\bigl(G(P\parallel D)\bigr) \subseteq \pi_C(P).
\]
The supplementary Isabelle/HOL session establishes this implication for
the concrete finite-trace semantics, including the projection/interleaving
lemma. Trace length is unbounded. This is not a mechanisation of a full CKA
library or a proof that the deployed bridge implementation satisfies the
model. A general state-dependent runtime guard is represented here by a
trace selector, not identified with an arbitrary subidentity language.

Two elementary algebraic lemmas are checked separately: multiplication by
a subidentity is contracting, and multiplication by zero makes the projected
upper bound vacuous under monotone projection. The latter does not require
projection to preserve zero. A finite countermodel shows that the selected
abstract laws in the earlier sketch, together with monotone projection and
control-silence, are insufficient for its authority-boundary conclusion.
The concrete theorem supplies the missing semantic connection; it does not
validate the earlier statement without additional assumptions.
```

**同步规则：** 将上述具体结果写入正文时，必须同步更新§10“formal artefacts status”及相关材料声明：旧Progress/CKA仍有admitted步骤；新增独立会话的成功不能升级旧会话或所有工具的状态。Python的65/13/1为有限枚举；新轨迹定理不引用这些数字作为证明依据。由反向包含得到相等可用反对称性，但反向包含本身要另证，不能命名为control-liveness后即当作活性结论。

## D7：本批补充书目候选（未写入主书目）

既有运行时、Trusta、ACCESS和CKA基础引用继续使用当前键。下列六项为D4新增条目；元数据取自已核主源/出版记录。CLARISSA TPLP论文的卷期年为2024，网页在线日期为2025-01-15，保留二者而不擅改出版年。SASSUR篇作者順序经9月13日Crossref响应补齐；姓名与TPLP篇不强行统一。

```bibtex
@inproceedings{bourbouh2021integrating,
  author = {Hamza Bourbouh and Marie Farrell and Anastasia Mavridou and Irfan Sljivo and Guillaume Brat and Louise A. Dennis and Michael Fisher},
  title = {Integrating Formal Verification and Assurance: An Inspection Rover Case Study},
  booktitle = {NASA Formal Methods},
  series = {Lecture Notes in Computer Science},
  volume = {12673},
  pages = {53--71},
  year = {2021},
  doi = {10.1007/978-3-030-76384-8_4}
}

@article{murugesan2024automating,
  author = {Anitha Murugesan and Isaac Wong and Joaqu{\'i}n Arias and Robert Stroud and Srivatsan Varadarajan and Elmer Salazar and Gopal Gupta and Robin Bloomfield and John Rushby},
  title = {Automating Semantic Analysis of System Assurance Cases Using Goal-Directed {ASP}},
  journal = {Theory and Practice of Logic Programming},
  volume = {24},
  number = {4},
  pages = {805--824},
  year = {2024},
  doi = {10.1017/S1471068424000425},
  note = {Published online 15 January 2025}
}

@inproceedings{varadarajan2024enabling,
  author = {Srivatsan Varadarajan and Robin Bloomfield and John Rushby and Gopal Gupta and Anitha Murugesan and Robert Stroud and Kateryna Netkachova and Isaac Hong Wong and Joaqu{\'i}n Arias},
  title = {Enabling Theory-Based Continuous Assurance: A Coherent Approach with Semantics and Automated Synthesis},
  booktitle = {Computer Safety, Reliability, and Security. SAFECOMP 2024 Workshops},
  pages = {173--187},
  year = {2024},
  doi = {10.1007/978-3-031-68738-9_13}
}

@inproceedings{yadav2026mcsafe,
  author = {Aakash Abhay Yadav and Shashank Shelat and Bhakti Hinduja and Tushar Badlani and Divyakumar Deepak Savla},
  title = {{MCSafe-GSN-HOL}: A Formal Assurance Framework for Machine-Checkable Safety Cases of Deployed {LLM} Agents},
  booktitle = {2026 9th International Conference on Circuit, Power and Computing Technologies (ICCPCT)},
  pages = {1892--1897},
  year = {2026},
  doi = {10.1109/ICCPCT70290.2026.11654768}
}

@article{zhao2026composable,
  author = {Xiaofei Zhao},
  title = {Composable Assurance for {AI} Alignment: A Framework for Propagating Formal Safety Properties Through {MLOps}},
  journal = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume = {40},
  number = {44},
  pages = {38129--38136},
  year = {2026},
  doi = {10.1609/aaai.v40i44.41151}
}

@inproceedings{viger2024supporting,
  author = {Torin Viger and Logan Murphy and Simon Diemert and Claudio Menghi and Marsha Chechik},
  title = {Supporting Change Impact Assessment with {LLMs}},
  booktitle = {2024 IEEE 35th International Symposium on Software Reliability Engineering Workshops (ISSREW)},
  pages = {203--204},
  year = {2024},
  doi = {10.1109/ISSREW63542.2024.00079}
}
```

| 候选键 | 可核查主源 | 元数据与内容依据 |
| --- | --- | --- |
| bourbouh2021integrating | [正式出版](https://doi.org/10.1007/978-3-030-76384-8_4) | N13、bibliography补充条目；作者稿§1–3 |
| murugesan2024automating | [期刊](https://doi.org/10.1017/S1471068424000425)、[预印本v1](https://arxiv.org/html/2408.11699v1) | L003、P12；§5.1–5.4 |
| varadarajan2024enabling | [作者PDF](https://www.csl.sri.com/~rushby/papers/sassur24.pdf)、[Crossref](https://api.crossref.org/works/10.1007%2F978-3-031-68738-9_13) | P13；§3.1；本次补齐出版元数据，未声称全文重新读取 |
| yadav2026mcsafe | [IEEE](https://ieeexplore.ieee.org/abstract/document/11654768) | N01、B105；§IV–VIII |
| zhao2026composable | [AAAI全文](https://ojs.aaai.org/index.php/AAAI/article/view/41151/45112) | N02、B325；pp.38131–38135 |
| viger2024supporting | [IEEE](https://ieeexplore.ieee.org/abstract/document/10771290) | N04、B322；§III–IV |

## 合入顺序与未包含事项

建议一次审阅D1–D5的review修订，再决定D6具体证明在正文中的篇幅；D7随被选用段落合入。摘要和结论只在这批内容真正合入后做相应短同步。研究总分母、方法定位和原实验数字均不因此扩大。

这批完成后，优先验证一个运行时接口的模型对应与进展条件，再扩展案例；先搭建多个case study不会补上缺失的语义连接。后续检索只围绕这些具体义务及最接近的组合/维护先例补缺，不恢复无边界的候选搜集。

## D8：后续接口研究补充（同日第二批，尚未合入正文）

根据用户“继续”，已将一个可执行的单操作协议接到上述迹语义，详见[接口研究记录](../../../formal-artefacts/cka-repair/runtime-interface/README.md)。D1–D7的文献来源与检索口径不因此改变。对独立稿的复审结论是：维持review主线，把新增证明作为核验论证的补充制品；不宜仅因多了几项小定理就扩大新颖性主张或改写为完整新框架论文。

**建议位置与篇幅：** 若作者采纳这一结果，§10末增加以下短段，将完整定义、反例、运行记录放在补充材料。与旧bridge状态机并非同一实现，不能把它的成功回填旧Progress/CKA的证明状态。D6的具体有限迹定理继续保留。

```latex
A supplementary single-operation protocol connects the trace boundary to
an executable transition function. Requests pass through pending and
approved phases; the trusted service rechecks current permission at commit
and records completion in the same atomic model step. Isabelle/HOL checks
a step simulation, its lifting to arbitrary finite input sequences,
equality of controlled trace languages, and at-most-once commitment.
The protocol also satisfies a separate progress result: with permission
retained, a pending request completes within two trusted service steps,
independently of advice availability. An explicit unbounded-service-supply
assumption yields an eventual-completion corollary for infinite input
streams. These are conditions on the model, not evidence that a deployed
scheduler or remote service satisfies them.

The operational model is related to the earlier interleaving semantics by
proving that its traces belong to the planner/hidden-event composition.
The hidden-event language over-approximates protocol bookkeeping as well
as advice. Thus the algebra organises an established semantic connection;
it does not replace the simulation proof. The exported SML is a research
executable. Input authentication, crash recovery and atomic correspondence
to an external effect remain separate deployment obligations.
```

**结果解释需同步：**

- `[Commit]`是参考机允许的迹，但执行接口需要额外请求/服务输入。因此本例证明的是投影相等，不满足上一批较强的`P⊆G(P∥D)`保留前提。这说明那个条件是充分条件，而非通用接口设计要求。
- “两个服务步”是调度事件数，不是2毫秒或两个CPU指令；任意多的建议、轮询和确认丢失事件可以出现在其间。若没有可信服务供给或权限被撤销，定理不承诺完成。
- `LostAck`发生在模型已完成原子提交之后，不能据此宣称解决所有远程调用歧义、网络分区或分布式exactly-once执行。此前Verified Tool Calls的引用和边界仍应保留。
- CKA的新增价值目前体现在组合表述和证据组织。是否比直接状态机证明节省工作、能否迁移到真实多组件系统，还需比较；本批未建立这种优势。
- 本例由Isabelle在设计阶段证明运行时机制，并导出执行函数。运行阶段检查当前状态和输入；运行时逐请求调用证明内核、证书重放或在线再证明属于另外的机制，不能由本例自动推得。

**下一项实质研究：** 在明确的执行边界中实现/验证输入来源隔离，以及权限检查、实际效果与完成记录的原子或事务对应。先选一个具有可检验语义的真实接口再开展比较；不为增加案例数量而泛化当前单操作协议。

## D9：SQLite实现案例（同日第三批，尚未合入正文）

D8末提出的本地接口连接现已完成一批经验核验，详见[案例与证据](../../../formal-artefacts/cka-repair/runtime-interface/sqlite-runtime/README.md)。此前理论和导出代码保持原样；新增Python执行器通过对照而非代码生成连接到它们。本次只读取5项官方技术资料，没有新增Google Scholar检索或改变330条筛选。

**建议位置与取舍：** 若采纳案例，在D8之后加下列短段，细节放补充材料。D8末关于部署义务的说明仍成立；不要把当前实验称为远程调用保障，也不要把既有模型证明的“任意输入序列”移植到Python实现的测试覆盖范围。

```latex
A local SQLite case study tests the implementation boundary of this
protocol. Separate credentials restrict advisory requests to the advice
interface. Current permission, the local balance effect, completion state
and event log are updated in one write transaction. The implementation
matches all 128 transitions in the exported finite model table for fixed
operation data. Five abrupt-process-exit experiments check recovery and
retry; three implementation mutations expose authority bypass, stale
permission and split effect/completion transactions. These results provide
empirical implementation evidence, not a machine-checked Python/SQL
refinement or an exactly-once guarantee for external services.
```

**中文解释与限制：**

- 已经观察到：正常实现的9组测试通过；5个退出点恢复后是原状态或完整完成状态；两个进程竞争仅产生一条效果记录。模型表中的16状态×8输入均匹配，数据夹具固定为一个操作及增量7。
- 原子性变体是重要反例：先提交余额，再另开事务写完成记录，崩溃留下余额7且阶段Approved。效果表唯一键并没有修复这个状态不一致问题。
- 撤权以事务顺序解释：撤权先提交则禁止效果；服务先占有写事务则可先完成效果，撤权随后生效。不能声称权限撤销请求一到达就中止此前正在提交的操作。
- 此处“输入来源隔离”是服务端凭据和消息分类，前提是控制凭据、执行器及数据库受保护。它没有证明解析器正确、建立操作系统沙箱或抵抗已掌握控制凭据的调用者。
- 进程突然退出不等于断电或数据库内部故障的穷尽测试。SQLite事务文档及配置是实现依据，数据库引擎、文件系统和存储仍在信任范围内。[官方资料读取记录](../../../formal-artefacts/cka-repair/runtime-interface/sqlite-runtime/evidence/source_checks.json)
- 本批没有运行真实LLM或评估建议收益，也未测量CKA相对直接状态机推理的成本优势。

**独立判断：** 当前足以支撑一个边界清楚的补充案例，应先收束研究材料并优先审阅review的D1–D5。CKA是否值得作为主要新贡献，下一步应通过明确的组件迁移/复用问题比较证明义务；继续添加同类小案例或条件性定理，不足以回答这个价值问题。
