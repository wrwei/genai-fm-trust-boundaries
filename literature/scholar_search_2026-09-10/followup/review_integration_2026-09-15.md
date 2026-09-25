# Review独立整合稿：2026-09-15研究范围复核版

**2026-09-21 案例更新：** 文末 I28 是已执行 AMR v2 的唯一新增成稿块，并规定其对旧 bridge 主案例操作的覆盖关系。I1–I27 保留为此前整合历史；不能在应用 I28 时再叠加被覆盖的 bridge 主案例。9 月 15 日的连续预览未包含 I28，活跃 TeX 与 Overleaf 均未应用本次更新。[完整实验结果](research_amr_v2_results_2026-09-21.md)给出证明、有限对应、物理与真实建议的分层证据。

日期：2026-09-15；正文基线442ec0e。此稿沿用9月13日独立整合候选，并在总计划执行中补充跨角色综合与两项文献案例分析；正文与主书目未应用。各批次实际证据状态分别记录。

本轮依据用户position paper原文、已有文献卡片、定向主源核查与重点案例评审。[研究主张](research_scope_2026-09-15.md)、[文献证据](research_evidence_2026-09-15.md)、[案例规格](research_case_design_2026-09-15.md)及[前批来源记录](research_sources_2026-09-15.json)给出细节。完整B*仍是较广的研究规格；本批只为[选定义务](research_case_evidence_scope_2026-09-15.md)新增独立bridge decision profile的机械对应定理、有限检查与模型见证。I8保留历史制品状态，I22单列新结果，I14分别限定其范围。

这份稿作为本轮完整候选入口；9月13日整合稿及D1–D9保留作历史依据，不与本稿叠加应用。使用者仍需审阅具体措辞，并在真正应用时重新核对替换锚点与排版。连续预览与编译状态以本轮[全文审阅记录](research_manuscript_review_2026-09-15.md)为准。

**总计划执行补充：** [三条review问题的综合论证](research_synthesis_2026-09-15.md)提供K1–K7与章节对应；[工具调用](research_case_tools_2026-09-15.md)和[物理闭环](research_case_physical_2026-09-15.md)给出两项文献剖析。I17–I22来自前批补证，I23a–I27补充本轮连续全文修订；I8a移至案例末尾，I17/I19扩为整章替换。按本稿顺序应用全部操作，不与任何旧候选叠加。[制品说明与日志](../../../formal-artefacts/bridge-profile/README.md)、[前批来源](research_master_sources_2026-09-15.json)及[全文审阅记录](research_manuscript_review_2026-09-15.md)记录依据。

## 先读这部分：文章现在应讲什么

主线是：生成工作流在什么条件下接受一个结果；这个结果能够支持什么主张；把它用于系统保障时，还需要补上哪些证据。363条快照用于导航，补充文献用于纠正和丰富比较，bridge用于说明义务选择的后果。

**不再以4对178的标签差异作为缺口论证的起点。** 即使把范围限定为快照，尚未验证的主标签也不足以判断这些论文实际投入多少保障工作。数字留在方法和分类图中；论证从验证结果与保障主张的不同对象、以及已有整合方法的适用条件展开。这不是否认快照中的标签差异。

**设计时与运行时按两个时间问题来比较：何时建立证据，何时使用或重验它。** Forge式生成—验证—修复是开发工作流；Isabelle是证明平台；CKA是组合推理的候选理论；在线监测器/门禁是执行机制。它们可以衔接。现有案例展示的是设计阶段证明运行机制、运行阶段检查输入与状态，未实现逐请求调用Isabelle或在线证书重放。无需为了说明这些关系，把review改写成提出完整平台的论文。

| 原候选 | 当前取舍 | 理由及对应位置 |
| --- | --- | --- |
| D1 方法 | 保留并压缩 | 正文交代330条记录、筛选口径和82条比较的关系；47页/434次/327 URL等检索细节留记录。I2 |
| D2 比较轴 | 保留 | 阶段、证据对象、来源映射、干预位置及变更处理分开。I3 |
| D3 运行时文献 | 按机制重新组织 | 先比较干预位置和受检对象；保留10项工作的关键修正，不按在线/统计标签排列保证强弱。I4 |
| D4 assurance先例 | 按检查、整合、维护组织 | 承认既有能力，残余义务具体化；正文不再加一张重复同一内容的长表。I6–I7 |
| D5 研究议程 | 按主张限定评价范围 | 维护效用、CKA复用和规模化生成比较均为条件性议程；先明确语义对应、运行时义务及案例需要的证据。I9–I12 |
| D6 基础证明 | 正文保留核心条件与结论 | 零行为推导、反例构造、完整脚本留制品。I5、I8 |
| D8 协议证明 | 简短交代已获得的证据 | 不升级旧Bridge理论，也不把条件进展说成部署调度保证。I8 |
| D9 SQLite案例 | 仅保留实验定位和指引 | 崩溃点、凭据、SQL和变体细节全部留补充材料。I8、I14 |
| D7 六项书目 | 随采用段落补入 | 候选条目仍未写入主书目；见文末B1 |

上一稿遗漏的同步工作也已补齐：摘要、§9开头、研究议程表、有效性限制、结论及材料声明。引言的三条review问题和贡献定位保留；§4–§7及Forge已核的作者报告数字不因本轮编辑而重写。

## I1 摘要：替换整个abstract

目标：[main.tex](../../../main.tex)。以下代码包含abstract命令；保留作者信息、keywords及其他内容。

```latex
\abstract{Large language models can generate code, specifications and proofs, but accepting these artefacts requires evidence whose scope is clear.
This critical review examines how generative models and formal methods divide responsibility for proposing, checking and justifying software artefacts.
An exploratory mapping of 363 saved arXiv records from 2020--2026, supplemented by targeted source checks, organises the discussion around six recurring roles: generation with checking, proof generation, model-based or empirical assessment, formal constraints on generation, runtime enforcement and assurance argument.
The abstract-based labels remain provisional and do not estimate field-wide prevalence.
The synthesis compares accepted objects, checking procedures, supported claims and assumptions maintained during use, including existing approaches to evidence integration and assurance-case maintenance.
Literature analyses of tool use and physical control examine parameter, observation and effect correspondences.
A bounded bridge model illustrates how selected obligations expose different planted defects and how restriction can preserve safety while removing completing behaviour.
A separate decision profile provides a mechanically checked correspondence between ordered branches and guarded actions, alongside finite checks separating raw candidate acceptance from runtime fallback.
These examples support scoped methodological conclusions, not model-performance estimates or complete deployment guarantees.
The resulting agenda addresses specification validation, semantic preservation, evidence integration, composition and maintenance, keeping source-reported results, executed checks and open obligations distinct.}
```

## I2 方法：替换Synthesis and Limits of Inference的首段

目标：[02-method.tex](../../../sections/02-method.tex)。从`Within each role`替换到`Numerical performance results ... differ.`；后续快照局限和AI辅助声明保留。

```latex
Within each role, we compare the generated artefact, acceptance procedure,
supported claim and residual obligation. Examples are selected for their
relevance to these distinctions. The saved collection retains the original
\CorpusN{}-record snapshot and \CorpusSupplementary{} contextual records
tagged separately; the latter do not enter snapshot counts or percentages.

A separate supplementary register contains 330 bibliographic and screening
records: 169 retained for qualitative review, 125 contextual, 27 excluded,
seven duplicate records and two unresolved records. These dispositions do
not represent 330 eligible independent studies or 330 full-text reviews.
An overlapping set of 82 comparison records documents selected workflows,
source versions and claim boundaries. Neither register enlarges the
snapshot denominator. Saved Scholar pages, bibliographic metadata,
screening reasons and inspection depths are retained with the materials;
later targeted rechecks are recorded separately. The supplementary work is
selective and AI-assisted, without independent duplicate human screening.
Numerical performance results from different benchmarks are not pooled
because tasks, budgets and acceptance criteria differ.
```

来源：[检索记录](../query_results.md)、[330条筛选](candidate_screening.json)、[82条比较](comparison_records.json)。不要把这些数量相加，也不要把82条称为330条的独立验证样本。47页对应434次结果出现及327个不同URL，另加3项先前文献才形成330条记录；这些细节仍可追溯。

## I3 分类：在Semantic Heterogeneity之前插入

目标：[03-taxonomy.tex](../../../sections/03-taxonomy.tex)。已有分类图、计数、比较表和institution段落均保留。

```latex
For selected workflows, the primary roles are supplemented by orthogonal
comparison fields: when evidence is established, when it is used or
rechecked, the accepted object, the checking authority, the supported
property, the mapping from observations to formal inputs, the intervention
point and the handling of changed evidence. These fields have not been
recoded across the full snapshot. A policy may be verified before
deployment and evaluated on proposed actions during operation; phase
alone does not determine the strength of its guarantee. The relevant
theorem or evaluation and the implemented interface determine what is
supported and under which assumptions.
```

依据：C07、N02、N03；跨阶段案例允许多角色，不改变初始分类分母。

## I4 运行时比较：替换章节开头的应用概述

目标：[08-runtime.tex](../../../sections/08-runtime.tex)。从`The snapshot assigns`替换至`These examples are illustrative...`；保留Observation and Enforcement。

```latex
The snapshot assigns \CorpusE{} records to runtime activity. The selected
workflows differ in their observation model, intervention point and
evidence for enforcement.

In robot control, Hafez et al. check and repair plans using reachable-set
over-approximations, retaining a previously safe continuation and braking
as fallback~\citep{hafez2025safe}. AESOP instead maintains recovery options
through multi-contingency model predictive control while slower
language-model reasoning is pending~\citep{sinha2024real}. Both supply
conditional control results: the former relies on dynamics, uncertainty,
perception and stopping assumptions; the latter on feasibility, recovery
sets and reasoning delay. These results do not certify every semantic
interpretation produced by the language model.

For tool use, the intervention point changes the supported claim.
ToolGate filters preconditions and checks executed results before accepting
them into symbolic state; rejecting a result does not itself undo its
external effect~\citep{liu2026toolgate}. Verified Tool Calls checks
postconditions after an ambiguous response and before retrying, reusing an
idempotency key. Explicit success responses are trusted, while duplicate
effect protection depends on state visibility and service-side
idempotency~\citep{mansoor2026verified}. VeriGuard checks generated policy
functions before deployment and intercepts actions at runtime; its
model-based extraction of policy parameters remains a separate
correctness obligation~\citep{miculicich2025veriguard}.

Diagnostic and approximate methods require the same attention to the
checked object. RvLLM combines domain rules and forward chaining with
model-based interpretation and follow-up queries~\citep{zhang2025rvllm}.
The inspected RoMA version estimates local probabilistic robustness in
BERT classification, providing statistical background rather than a
demonstration of rule monitoring over generative output
streams~\citep{levy2025statistical}. BRT-Align uses learned approximations
to implement latent-reachability detection and steering, so its ideal
model and implemented approximation must be distinguished~\citep{karnik2025preemptive}.
RSP-M computes signals from emitted reasoning and action text, not hidden
attention weights~\citep{zhou2025reasoning}. SAFE-AI reports pattern and
AST-based checks with code and agent-simulation experiments, requiring
assessment of check coverage rather than treating it as an internal-signal
detector~\citep{navneet2025rethinking}. These comparisons use the inspected
source versions; they are selective and have not been independently
reproduced here.
```

来源与读取边界：C17/C18、C06/C25/C07、C23/C24/C32/C33/C34的[比较卡片](comparison_records.json)；版本和章节定位沿用D3及[主源日志](comparison_source_log.json)。明确承认已有条件定理、steering和实验，不以“有LLM”或“在运行时”否定它们。

## I5 具体trace定理：用条件与结论组织运行时说明

目标：[08-runtime.tex](../../../sections/08-runtime.tex)。替换`Stating the Guard Algebraically`小节；保留下一小节。

```latex
\subsection{A Sufficient Condition for Controlled-Trace Inclusion}

For languages of finite traces, take interleaving as parallel composition
and event erasure as projection. An independent supplementary Isabelle/HOL
development proves: if every trace in $D$ erases to the empty trace over
the controlled alphabet $C$, and the selector $G$ satisfies
$G(P\parallel D)\subseteq P\parallel D$, then
\[
  \pi_C\bigl(G(P\parallel D)\bigr) \subseteq \pi_C(P).
\]
This gives a sufficient authority condition for arbitrary finite trace
length. It does not guarantee retention of useful behaviour. Applying it
to a controller still requires a correspondence with the specified
interleaving, projection and admission semantics; the bridge enumeration
in Section~\ref{sec:bridge} does not supply that general proof.

Algebraic frameworks such as CKA and Kleene algebra with tests provide
candidate composition and guard vocabularies
\citep{hoare2009cka,hoare2011cka,hoare2016cka,kozen1997kat}. The checked
result above uses a concrete trace semantics, not a completed CKA-library
instantiation. Section~\ref{sec:agenda} considers the remaining composition
and reuse questions.
```


## I6 assurance主线：替换§9开头三个段落

目标：[09-gap.tex](../../../sections/09-gap.tex)。从`Within the snapshot`至Different Objects Called Assurance之前。保留该小节及其既有例子。

```latex
A verification result establishes a property of an artefact under stated
assumptions. A system-level assurance claim additionally needs a warrant
that the property is relevant, the artefact represents the deployed
system, and the assumptions remain applicable. The same workflow may
provide both kinds of evidence. This section compares how existing
approaches construct, connect and maintain such evidence.

The snapshot's exclusive primary labels provide navigation for this
comparison, but do not measure how much assurance work each paper
contains. Supplementary sources include relevant approaches outside the
snapshot and capabilities that span its roles. The review therefore asks
which links are justified in each workflow, rather than inferring a
field-wide or within-paper research deficit from label frequencies.
```

这是对先前候选的一项实质修正：D4只替换先例段，未处理开头仍然从标签推断研究内容的问题。计数本身不删除，分类图和方法仍给出原口径。

## I7 assurance先例：替换Work connecting...至下一小节之前

目标：[09-gap.tex](../../../sections/09-gap.tex)。替换该先例段落组，保留The Missing Links to Examine及worked fragment。

```latex
Existing approaches supply concrete comparisons for these links.
The inspected Trusta preprint uses model-assisted formalisation and
checks encoded reasoning constraints~\citep{chen2025trusta}.
MCSafe-GSN-HOL reports Isabelle/HOL obligations for argument support,
assumptions, defeaters and acyclicity~\citep{yadav2026mcsafe}.
These checks have defined argument-level objects; the validity of leaf
evidence and its relevance to deployment require further warrants.
Trusta's journal metadata has been checked, while the method inspection
uses its preprint. The reported MCSafe theory library was not obtained
and replayed in this review.

Integration may organise evidence without establishing a mathematical
translation between every participating tool, as in the inspection-rover
assurance case~\citep{bourbouh2021integrating}.
ACCESS connects engineering artefacts, formal analyses and dynamic
argument evaluation; its demonstrated monitoring service is non-invasive,
so evaluation does not itself enforce an actuator
response~\citep{wei2024access}.
Two related CLARISSA contributions address semantic argument analysis
using goal-directed ASP and continuous assurance with an evidence tool
bus~\citep{murugesan2024automating,varadarajan2024enabling}.
They provide related evidence for checking and integration, not independent
replications of one result.

Maintenance is also an existing capability. MCSafe describes propagation
from changed nodes to affected parent goals; CAF describes structured
assurance records, dependency-based invalidation, local recomputation and
deployment policy gates~\citep{yadav2026mcsafe,zhao2026composable}.
LLM-supported change-impact assessment supplies candidate affected nodes
for engineers to review~\citep{viger2024supporting}.
The comparison must separate the correctness of propagation over supplied
links from the semantic completeness of those links, and distinguish
argument evaluation from effective intervention. These precedents support
specific baselines for the maintenance study in Section~\ref{sec:agenda}.
```

来源：U01、N01–N04、N13的[记录](records.json)，P12/P13的[版本与主源核验](../verification/cascon_crosswalk.json)。不重复正文长表；完整对照留D4和卡片。未获得MCSafe库是本项目证据边界，不能写成作者没有实现。

## I8a 制品状态：压缩并移至bridge章节末尾

目标：[10-bridge-case-study.tex](../../../sections/10-bridge-case-study.tex)。先移除`Status of the Formal Artefacts`至`A Guard Can Preserve Safety While Preventing Crossings`之间的旧小节，再将以下内容追加至该章末尾。随后I22插入此新末尾小节之前；矩阵与旧C0守卫结果因而连续。

```latex
\subsection{Status of the Formal Artefacts}

The original bridge has related Dafny, CSP, Isabelle/HOL and Lean
artefacts without proved equivalence. Recorded Dafny checks cover selected
contracts; Lean retains admissions and uses supplied acceptance sets for
coverage; the CSP and legacy Isabelle sketches have no completed
verification run recorded here. The original matrix is therefore credited
to Python enumeration. The new decision-profile HOL theorem is separate.

Supplementary material also contains a conditional single-operation
protocol proof and finite Python/SQLite implementation checks. They explore
interface obligations in another model, and are not a refinement proof
for either bridge representation. Detailed proof status, dependencies,
commands, failed runs and implementation limits remain in the artefact
provenance; Section~\ref{sec:threats} states their generalisation limits.
```

历史Dafny、Lean和SQLite数值仍保存在前批候选与制品记录中，未删除或改写；正文不再逐项复述这些旁支实验。

## I8b bridge中重复的prospective代数段：压缩替换

目标同上。从`The bounded trace inclusion motivates`替换至`including advisory silence ... remains to be established.`；保留随后的有限前缀解释。

```latex
The concrete trace theorem in Section~\ref{sec:runtime} states sufficient
conditions for an authority boundary. Applying it to this bridge requires
a correspondence between the transition system and the composition,
projection and guard semantics, including the placement of admission
checks. The legacy \texttt{formal-artefacts/isabelle/Bridge\_CKA.thy}
contains explicit axioms and four admitted steps; its general algebraic
claim and correspondence to this bridge remain open. The independently
checked supplementary development does not validate that earlier sketch
without additional assumptions.
```

## I9 研究议程表：替换RQ3–RQ5三行

目标：[12-research-agenda.tex](../../../sections/12-research-agenda.tex)。保留RQ1/RQ2、表头及表尾。下表为可能研究设计，不要求本review同时完成所有比较。

```latex
RQ3 & Evidence links may become stale or omit change impacts &
For maintenance-benefit claims, compare evidence-linked workflows with an existing structured approach &
Missed affected claims; excess invalidation; recomputation and review effort \\
\addlinespace
RQ4 & Model results require semantic and operational correspondence &
Check source/model mappings and runtime composition against the same stated specification &
Semantic mismatches; authority violations; retained choices; conditional progress \\
\addlinespace
RQ5 & Demonstrations do not establish general practical benefit &
Where benefit is claimed, match obligations, tasks and budgets across relevant acceptance workflows &
Accepted defects; completion; unsupported cases;
```

CKA比较和无LLM对照不列为当前必做工作；具体比较由待支持的效用主张决定。

## I10 RQ3：替换完整小节

目标同上。证据结构是比较对象；维护平台的实现和效用评价保持为后续研究。

```latex
\subsection{RQ3: How Can Evidence Produce Maintainable Assurance Cases?}

An evidence interface should record the claim, formal statement, artefact
identity, checker and version, semantic domain, assumptions, bounds and
result status. Translation and composition steps require their own links.
A schema can check these fields without establishing that the links are
semantically sufficient or that the evidence supports the engineering claim.

Existing approaches discussed in Section~\ref{sec:gap} provide precedents
for structured evidence integration and change handling. If a study claims
a maintenance benefit, its evaluation should include an applicable existing
structured workflow, with implemented, replayed and approximated components
identified. Changes to an artefact, an assumption and a translation link
should be distinguished. Relevant outcomes include missed affected claims,
unnecessary invalidations, recomputation effort and human review.

The immediate requirement for an illustrative case is narrower: expose
which results remain applicable after a specified change and which
obligations must be revisited. Correct propagation over supplied links does
not establish that all semantic dependencies have been supplied. Discharged
claims, external assumptions, unresolved obligations and defeaters must
remain distinguishable.
```

## I11 RQ4：替换完整小节

目标同上。保留语义组合问题，不预先把证明复用比较确立为研究主线。

```latex
\subsection{RQ4: How Can Heterogeneous Results Be Composed Soundly?}

Section~\ref{sec:institutions} motivates preserving the meaning of each
result. A tractable study should first identify the source and target
semantics, the properties to be preserved and the implemented translation.
An institution-based interface is one possible organisation of these
obligations; it does not discharge them merely by recording their types.

For a system containing an LLM, design-time acceptance and runtime
enforcement should refer to the same declared specification. A generated
controller can be checked under a snapshot of the state, while the state
may change before its proposed action is committed. Source/model
correspondence, current-state validation and the relation between a
controller step and its external effect are distinct obligations.

Advisory composition should allow the LLM to influence choices permitted
by the specification while preserving the stated authority boundary.
Controlled-trace inclusion, the availability of completing behaviour and
progress under service or scheduling assumptions should be evaluated
separately. Requiring every fixed advice stream to retain every reference
choice may remove the influence that the advisory component is intended
to have.

The decision-profile theorem and supplementary protocol results
illustrate different parts of this task in separate models. Neither
provides an automatic composition theorem for the full bridge or its
deployment; a case must expose the links still required.

CKA is a candidate framework for expressing sequential and concurrent
composition after the component semantics and operational correspondence
are specified. Direct state-based reasoning remains an available route.
A comparison of proof reuse is warranted if an algebraic reuse advantage
is claimed; it must then include correspondence work and invalid reuse
after changes. Such an advantage is neither assumed nor established by
the present examples.
```

完整案例的重复请求身份与双阶段LLM接口见独立规格；本批已执行的局部语义／决策profile结果仅见I22，不把它回填成完整协议或真实LLM试验已完成。

## I12 RQ5：替换A broader evaluation...段

目标同上。保留此前关于公开Forge v2的作者报告及未复现说明，也保留后文部署扰动讨论。

```latex
If a study claims practical benefit beyond an illustrative case, the
evaluation should use independently selected tasks, requirements fixed
before generation and comparable budgets. Relevant compile/test-only or
formal acceptance workflows should be matched on the obligations they
actually check; adding tools does not by itself add a stronger guarantee.

For a case about justified acceptance, record actual generated candidates,
failed obligations, repairs, runtime recommendations and executed effects.
Keep planted faults separate from naturally generated failures. Matched
scenarios can test a specific semantic mapping or enforcement condition
without requiring an evaluation of whether using an LLM is preferable to
a non-LLM solution.

Report rejected candidates, false rejections, unresolved runs, timeouts,
unsupported source features and human intervention alongside accepted
results. A successful demonstration supports feasibility for its stated
profile; broader rates or efficiency claims require an appropriate
sampling and comparison design.
```

新增版本核查确认：不能将position paper匿名伴随稿的五层完成声明、2–4轮或首个编译通过停止，混写为公开Forge v2的结果。

## I13 检索有效性：替换Coverage and Search Provenance小节

目标：[11-threats.tex](../../../sections/11-threats.tex)。保留Classification and Selective Reading小节。

```latex
\subsection{Coverage and Search Provenance}

The quantitative map uses arXiv alone. Publication practices, query
vocabulary and lexical filters can affect the six roles differently.
Exclusive primary labels do not measure field-wide prevalence or the
assurance capabilities within each paper. Possible false positives and
classification errors also preclude treating counts as lower bounds.

The separate supplementary search documents relevant work beyond the
snapshot, without determining the direction or magnitude of the net
error in its counts. Its 330 record-level dispositions and selected
comparison cards improve traceability but are neither comprehensive
full-text adjudication nor independent duplicate human screening.
Contextual and unresolved records remain explicitly distinguished from
sources retained for qualitative review.

The original arXiv retrieval timestamp, exclusion log, raw responses and
classifier configuration are missing. Saved supplementary Scholar pages
do not reconstruct that earlier search. Repairing the lexical filters
and recounting the snapshot provides limited reproducibility. A
systematic extension would additionally require a dated multi-index
protocol, work-level version handling, eligibility adjudication and
independent coding appropriate to its claims.
```

## I14 案例有效性：替换Construct Validity...至文件末尾

目标同上。

```latex
\subsection{Construct Validity and Generalisation of the Examples}

The bridge is a small synthetic transition system with planted defects,
fixed bounds and no sampled model outputs. Grant preservation is a safety
property, not scheduler fairness; an available completing trace and no
detected deadlock do not prove universal liveness. The matrix compares
selected predicates rather than tool expressiveness. Its formal-language
artefacts are not proved equivalent, several legacy proofs remain
admitted, and Lean's table-coverage results use supplied acceptance sets.

The new decision profile in Section~\ref{sec:bridge-profile} is separate
from those legacy artefacts. Its HOL theorem covers the defined abstract
syntax and guarded-action semantics, not source-text parsing or the
Python implementation. The 31 predefined snapshots are a finite checking
domain, not a proved abstraction of every request-identified protocol
state. Candidates and advice inputs are constructed examples, not sampled
LLM runs. The fallback uses the reference decision table, so agreement
with that table is not an independent proof of the fallback. A modeled
atomic commit and finite service witnesses establish neither deployment
atomicity nor unbounded liveness; physical sensing and actuation are
outside the profile.

Supplementary protocol progress assumes retained permission and
trusted-service supply. Its local Python/SQLite checks are finite
implementation evidence, not a refinement proof or a result about remote
effects, deployment scheduling or either bridge model. None of the
studies measures language-model advice quality or establishes a CKA
advantage over direct state-machine reasoning.

Forge's results are attributed to the public companion preprint and have
not been reproduced in this review. Several authors overlap, so that
study is a feasibility example rather than independent corroboration.
The evaluations in Section~\ref{sec:agenda} are proposals for testing the
remaining claims, not completed studies implied by the supplementary
proofs or implementation checks.
```

## I15 结论：替换The bridge example...段

目标：[16-conclusion.tex](../../../sections/16-conclusion.tex)。其余结论保留。

```latex
The tool and physical-control analyses identify parameter, observation
and effect correspondences. The bridge models make three links concrete:
the chosen obligations determine which mutations are rejected, an
ordered-branch interpretation requires semantic correspondence, and
runtime restriction can remove useful behaviour. The AST theorem and
finite checks support these respective claims without composing into a
deployment guarantee. Successful fallback does not establish the quality
of a rejected candidate. Together, the analyses locate the evidence
needed between generation, acceptance and execution; they establish no
universal advantage of multiple tools or algebraic composition.
```

## I16a Data availability：替换该小节正文

目标：[17-declarations.tex](../../../sections/17-declarations.tex)。保留小节标题及下一个Materials availability小节。

```latex
The manuscript repository holds the saved literature records, initial
labels, documented corrections, supplementary search and screening
records, source-inspection cards, bridge enumeration and supplementary
proof and implementation evidence. The original arXiv search responses
and classifier configuration are unavailable (Section~\ref{sec:method});
the separately saved Scholar pages do not reconstruct them.
TODO (before submission): deposit a versioned archive of the included
materials and provide its persistent identifier here.
Forge results are reported separately in the public preprint cited in
Section~\ref{sec:realisation}.
```

## I16b Code availability：替换该小节正文

目标同上。保留小节标题及后续Author contribution；资金、作者贡献等未知内容不代填。

```latex
The repository includes the literature-audit and bridge-enumeration
scripts, legacy formal artefacts, separate checked Isabelle sessions,
the decision-profile theory and finite Python checks, generated SML and
the local Python/SQLite experiment with its test and
mutation drivers. Their provenance records distinguish proof status,
execution evidence and unverified implementation correspondences.
TODO (before submission): provide the versioned archive URL or DOI and
the reuse licence.
Public Forge code is linked from its cited preprint; those experiments
were not rerun for this review.
```

## I17 Generate and Check：统一混合接受与规格忠实的表述

目标：[04-generate-check.tex](../../../sections/04-generate-check.tex)。替换该章节全文，吸收此前I17的Clover修正；不与旧I17重复应用。

```latex
%% Qualitative, overlapping themes; no unreproducible sub-theme counts.

\section{Generate and Check}
\label{sec:gen-check}

The largest provisional group, with \CorpusA{} records after the documented corrections, has a model draft an artefact that an external procedure checks.
The generator--checker split is established practice, not a new proposal of this review.
We organise representative examples into five overlapping themes; the saved corpus does not provide reproducible per-paper sub-theme labels.

\subsection{Code with a Verifier in the Loop}

One recurring workflow generates program text and gates acceptance on a verifier's verdict.
Clover makes the acceptance boundary more detailed than a single verifier
verdict. Its evaluated consistency procedure combines deductive checks,
input--output comparisons and model-based document comparisons
\citep{sun2023clover}. The formal status of the deductive checks does not
automatically extend to the other comparisons. This is a positive example
of addressing relations among artefacts, while also showing why each
relation needs its own evidence.

At repository scale, acceptance also depends on resolving specifications and dependencies across files~\citep{zhong2025towards}.
Security-oriented work generates code and submits it to bounded model checkers at volume, producing datasets of machine-labelled vulnerable programs~\citep{tihanyi2023formai,tihanyi2024secure}, and the same loop drives compiler fuzzing, where a model proposes inputs that exercise optimisation paths and the compiler itself supplies the oracle~\citep{yang2023whitefox}.
A variant grounds quantitative reasoning by requiring the model to emit code whose execution, rather than whose text, is checked~\citep{zhou2024trust}.

These workflows use different oracles: deductive verification, bounded analysis and execution comparisons support different claims.
A proof of a supplied contract does not by itself validate that contract against the engineer's intent; other workflow steps may provide that evidence.

\subsection{Specifications, Contracts and Invariants}

Another workflow moves the burden one level up, asking the model to produce the specification rather than the implementation.
Contract and specification synthesis checked by a deductive verifier~\citep{wen2024enchanting}, Dafny methods synthesised together with the annotations needed to discharge them~\citep{misu2024assisted,poesia2024dafnyannotator}, and inductive loop invariants proposed and then tested by an SMT solver~\citep{kamath2023finding} are the recurring forms.
Tooling has followed: assistants that supply the missing lemma when a proof attempt stalls~\citep{mugnier2024laurel}, and pipelines that mine potential runtime errors to drive specification inference at the scale of a thousand lines~\citep{wang2025a}.

Generating the acceptance specification makes its validation especially visible; the same issue arises when code generation relies on an inadequate supplied specification.
If no independently validated requirement or stronger specification is available, a verifier may confirm only consistency between two generated artefacts.
Where a reference specification exists, equivalence, refinement and mutation checks can provide additional evidence of adequacy.
Work evaluating how faithfully generated specifications capture user intent~\citep{lahiri2024evaluating} addresses whether successful verification corresponds to the intended behaviour.

\subsection{Hardware and Assertion Generation}

Hardware assertion generation places acceptance at the relation between a design and its checked properties.
Studies of whether models are ready for practical adoption in assertion generation report the gap between benchmark scores and industrial use~\citep{pulavarthi2025are}, and deterministic synthesis flows constrain the model to a template that the downstream tool can always parse~\citep{roy2025veritas}.
Other studies evaluate generated hardware with established formal tooling to examine which properties the outputs actually satisfy~\citep{gadde2024all}.

\subsection{Temporal Logic and Requirements}

A further theme translates natural-language requirements into temporal logic: metric temporal logic for timed properties~\citep{manas2024tr2mtl}, signal temporal logic for continuous signals~\citep{fang2025enhancing}, and linear temporal logic for discrete specifications~\citep{ma2025bridging,allegrini2025formalizing}.
The pattern also appears in planning, where a model's plan is expressed as a formal property and discharged by a model checker before execution~\citep{ramani2025bridging}.

Translation is where faithfulness is most exposed.
Typechecking a formula establishes its formal admissibility, not its correspondence to the source requirement.
A workflow can additionally validate that translation; its evidence must be distinguished from checking the resulting formula.
The abstract-level mapping cannot determine how many papers discharge or validate this translation obligation; full-text analysis is needed.

\subsection{Security and Infrastructure}

Security and infrastructure applications include protocol analysis in which a model proposes attacks and a formal tool confirms them~\citep{curaba2024cryptoformaleval}, counterexample-guided synthesis for planning~\citep{jha2023neuro}, self-healing pipelines that generate patches and re-run the checker~\citep{tihanyi2023software}, and infrastructure-as-code checked before deployment~\citep{jana2026terraformer}.

\subsection{What the Group Shares}

The common role is to check a generated artefact against an explicit target.
The checking steps may combine formal, empirical and model-based procedures,
so the final acceptance argument must identify the evidence supplied by each.
Specification adequacy and representation correspondence remain distinct
obligations even when another step addresses them. Section~\ref{sec:gap}
examines how those results are connected to an assurance claim.
```

保留既有实例与引文，不再把五种流程全部说成统一外部接受，也不把规格忠实问题限定为规格生成独有；修正硬件段落病句。

## I18 证明生成：区分内核、目标陈述与接受接口

目标：[05-generate-prove.tex](../../../sections/05-generate-prove.tex)。在`Admitted lemmas or unchecked axioms must be audited rather than counted as proved claims.`之后插入第一段；将Decomposition小节中从`This is the closest the group comes...`开始的句子组替换为第二段。

```latex
The evaluation interface is another part of this boundary. The revised
DeepSeek-Prover-V2 report describes an interface issue involving the
exposure of admissions, rather than a failure of the proof kernel's logic
\citep{ren2025deepseek}. Kimina separately uses model-based judgement in
autoformalisation and Lean checking in proof generation
\citep{wang2025kimina}. A recorded success therefore needs both an
appropriate target statement and an accurately checked final proof.
```

```latex
When the completed subproofs are combined within the same logic, its
inference rules establish the formal composition. This avoids a
translation between different logics at that step. Faithfulness of the
target statement, imported assumptions and correctness of the checking
interface remain separate obligations; sharing a kernel does not discharge
them.
```

依据：C71 v2 §3.2、C75 v1 §2.1–2.3。第一项是特定版本作者报告，不作普遍接口缺陷或内核不健全的断言。

## I19 Formalism in Service：补入具体机制并消除角色互斥表述

目标：[07-formalism-serves-model.tex](../../../sections/07-formalism-serves-model.tex)。替换章节全文，吸收此前I19首段；不改六类角色或语料标签。

```latex
%% Section 7: formalism serves the model.

\section{Formalism in Service of the Model}
\label{sec:formal-serves}

A fourth provisional group of \CorpusD{} records uses formal structure
within generation, search or model analysis. These placements can overlap
with checking the resulting artefact. A proved constraint mechanism and a
heuristic preference have different evidential roles even when both are
used during decoding or search.

Logical structure is used to shape a plan before it is executed~\citep{obi2025safeplan,xia2026grasp}, to steer proof search~\citep{george2025leanprogress,swan2023math}, or to synthesise guardrails that bound what a deployed model may emit~\citep{ravichandran2025safety}.
Elsewhere the model is pointed at an existing formal or security artefact as an analysis aid, extracting vulnerabilities from RTL~\citep{collini2025marvel}, building verification models for protocol stacks~\citep{yang2023auto}, or comparing formal and learned approaches to the same detection task~\citep{tihanyi2025vulnerability}.

SynCode makes the distinction concrete through grammar masks during token
generation~\citep{ugare2024syncode}. Its version~4 analyses two directions:
retaining tokens that preserve a grammatically extendable prefix, and,
with sufficiently long accept sequences, excluding tokens that do not.
The implementation uses accept sequences of length one or two and can
therefore admit invalid extensions under the paper's completeness criterion.
The prefix results also do not guarantee termination with a complete
output. Grammar conformance and completion must be distinguished from
the intended semantics of the generated program.

Formal structure can thus contribute checked constraints during generation;
heuristic steering offers a different kind of evidence. The relevant
comparison is the enforced property, the assumptions of its theorem and
the implemented approximation, rather than the direction of information
flow. These roles can coexist with later artefact checking and runtime
enforcement.
```

新增引文见B1末项。定向核读[SynCode v4](https://arxiv.org/html/2403.01632v4) §4.4 Theorems 1–2、§4.5；按原文方向区分有效token保留与无效扩展排除，不将短accept sequence实现误写为保证所有输出正确。

## I20 两项文献剖析：在运行时章节加入具体连接问题

目标：[08-runtime.tex](../../../sections/08-runtime.tex)。在`Observation and Enforcement`小节之前插入，位置在I4替换区域之后。以下两个例子是本文构造的分析情形，不是复现外部系统。

```latex
\subsection{Two Analytical Vignettes}

\subsubsection{Tool Calls: From Checked Arguments to External Effects}

Consider a document-move operation. A policy may approve object 17 while
a subsequent parameter-generation step selects object 71. Alternatively,
the same path may refer to a different object by the time the operation
executes. These constructed scenarios distinguish correctness of the
policy function from correspondence between checked and executed inputs.
They motivate a common immutable call description and execution-time
checks of its object, version and authorisation. A further scenario has
the move succeed but its response fail a postcondition: retaining the old
symbolic state does not reverse the move. The mechanisms in VeriGuard,
ToolGate and Verified Tool Calls address different parts of these links
under their respective conditions
\citep{miculicich2025veriguard,liu2026toolgate,mansoor2026verified}.
The scenarios are analytical witnesses, not reproduced attacks.

\subsubsection{Physical Control: From Observed State to Executed Motion}

A physical-control vignette exposes a different correspondence. Suppose
an estimated initial set omits the robot's actual localisation error.
A correctly computed safe envelope for that set need not contain the
physical trajectory. Likewise, a fallback command delivered after its
required switching time can start outside the state for which its
continuation was checked. Reachability-based control already includes a
bounded-time repair attempt and a previously safe fallback, while AESOP
explicitly retains feasible recovery options during bounded reasoning
delay~\citep{hafez2025safe,sinha2024real}. The remaining question is whether
observations and execution implement those conditions. Neither vignette
constitutes a counterexample to a theorem under its stated assumptions.
```

依据及细节：[工具剖析](research_case_tools_2026-09-15.md)、[物理剖析](research_case_physical_2026-09-15.md)。两个短分析不计为本项目新实验或跨领域复现；其完整条件表放补充研究材料。

## I21 直接回答三个review问题

目标：[09-gap.tex](../../../sections/09-gap.tex)。在`A Worked Assurance Fragment`小节之前插入，与I6/I7锚点分开。它收束前面各章的比较，后续片段和bridge负责使部分义务具体化。

```latex
\subsection{Synthesis Across the Review Questions}

For the first review question, acceptance is best identified at the level
of a particular artefact and decision step. A workflow can contain a
kernel check, an execution test and a model judgement without these
becoming the same kind of evidence. The six roles organise the literature;
they do not assign a single assurance level to every system in a group.

For the second question, the supported claim depends on the checked
semantics, property and assumptions. Reconstruction, rule-based
translation and replay of a translated counterexample already provide
different forms of correspondence evidence
\citep{sun2023clover,curaba2024cryptoformaleval}.
A concrete replay, a sampled consistency check and a general preservation
theorem answer different questions. Their value should be assessed against
the relation actually needed, without treating all unproved relations as
an absence of checking.

For the third question, using a result in a deployed-system argument
requires a warrant linking it to the requirement, artefact version,
observations and effects. Existing integration and continuous-assurance
approaches provide mechanisms for organising and maintaining these links
\citep{bourbouh2021integrating,varadarajan2024enabling}.
The remaining comparison concerns the adequacy of the links, conditions
for reusing evidence, and observable changes that invalidate it. The
worked examples examine selected obligations from this synthesis; they
do not establish the prevalence of gaps across the field or validate a
general assurance platform.
```

依据：[K1–K7对应表](research_synthesis_2026-09-15.md)。该综合不依赖新bridge实施完成，也不以旧分类标签差异作为缺口。

## I22 新bridge局部语义／决策profile：单列已执行证据

目标：[10-bridge-case-study.tex](../../../sections/10-bridge-case-study.tex)。在已移至章末的`Status of the Formal Artefacts`之前插入，位于旧C0守卫结果之后。这里的计数与旧bridge的65/13/1、旧单操作协议及SQLite实验分别保存；不合并样本或证明结论。

```latex
\subsection{An Additional Decision Profile}
\label{sec:bridge-profile}

A separate decision profile examines interpretation and acceptance of
loop-free ordered branches returning $\mathsf{GrantA}$,
$\mathsf{GrantB}$ or $\mathsf{Wait}$. Boolean guards contain atoms,
constants, negation, conjunction and disjunction. Flattening retains the
negation of each earlier branch on subsequent paths. In Isabelle/HOL, we prove, for every
profile program $p$ and Boolean atom interpretation $\rho$,
\[
  \mathsf{Actions}(\rho,\mathsf{flatten}(p))
  = \{\mathsf{eval}(\rho,p)\}.
\]
The theorem concerns these two AST-level semantics. A checked
counterexample shows that dropping prior-branch negations can allow
three actions where the source selects one. Neither result proves a
text parser or an implementation correspondence.

Separate Python checks cover 31 predefined snapshots with at most one
direction Granted or Crossing, waiting counters in $0..2$, and no two
counters simultaneously at the bound. Busy states require Wait;
otherwise a request at the bound has priority. Advice selects between
two remaining eligible requests, with A as the default when advice is
absent. Three advice inputs give 93 contexts per constructed candidate.
An independently written phase/counter table supplies the reference
choice without calling the candidate interpreter or extractor.

\begin{table}[t]
\centering
\caption{Constructed candidates in the decision profile; each row covers
93 inputs. Violations concern the specified choice, including service
and advice response, rather than only mutual exclusion.}
\label{tab:bridge-profile-candidates}
\begin{tabular}{lrr}
\toprule
Candidate & Raw violations & After modeled fallback \\
\midrule
Reference-conforming & 0 & 0 \\
Always grant A & 70 & 0 \\
Always wait & 42 & 0 \\
Ignore advice & 4 & 0 \\
\bottomrule
\end{tabular}
\end{table}

The advice-ignoring candidate violates none of the checked eligibility
or service conditions, but fails the required choice on four inputs.
Fallback cannot convert that rejected raw candidate into an accepted
one. Because fallback itself uses the reference table, its column is a
model execution check, not an independent correctness proof of fallback.

A commit witness rejects an old B proposal after the current state has
granted A. A repeated-request trace under A advice grants A, A, then B
with the bound of two opposite grants. Removing that bound permits a
repeatable projected A-service cycle while B waits; withholding Exit
also leaves the bridge safely occupied. These finite witnesses explain
the need for progress conditions without proving unbounded liveness.
These are constructed candidates and model inputs. The profile omits
request-identity lifecycles and physical effects; it is not proved to
refine the earlier C0 model. The supplement records 4,116 comparisons
on 1,029 small ASTs, 46 enabled-transition checks, and all proof and
execution logs, separately from the general HOL theorem.
```

依据：[制品README](../../../formal-artefacts/bridge-profile/README.md)、[一般对应理论](../../../formal-artefacts/bridge-profile/Bridge_Profile.thy)、[有限检查](../../../formal-artefacts/bridge-profile/verify_profile.py)、[独立评审](research_synthesis_review_2026-09-15.md)。有限检查域不是已证可达域；“投影循环”省略未封顶历史计数、epoch和请求身份，不能升格为完整B*无界执行定理。

## I23a 引言贡献：明确案例分工

目标：[01-introduction.tex](../../../sections/01-introduction.tex)。从`We contribute a trust-boundary organisation`替换至`Section~\ref{sec:method} explains`之前；保留三个review问题原文。

```latex
We contribute a comparison of acceptance authority, evidence scope and
semantic connections across representative workflows, supported by an
exploratory arXiv map. Two literature analyses examine tool effects and
physical-control assumptions. A bridge study then makes selected
obligations executable: its finite model examines coverage and progress
under restriction, while a separate decision profile checks ordered-branch
correspondence and raw candidate acceptance. The resulting research agenda
identifies evaluations for claims that these limited examples do not
establish. The mapping labels remain provisional and the proposed
evidence interface remains a research direction.
```

## I23b bridge入口：交代三项问题与两个模型

目标：[10-bridge-case-study.tex](../../../sections/10-bridge-case-study.tex)。从`The single-lane bridge illustrates`替换至`Model and Checked Properties`小节之前。

```latex
The bridge study examines three links from the synthesis: selecting
adequate obligations, preserving program meaning across representations,
and retaining useful behaviour under runtime checks. The first two
subsections introduce a finite, single-request controller and its
obligation matrix; the next examines guards on that same controller.
Section~\ref{sec:bridge-profile} then uses a separate decision profile for
ordered branches and repeated requests. The models share a scheduling
setting but are not proved equivalent. Candidates and faults are
constructed examples, not sampled LLM outputs.
```

## I23c 旧bridge结尾：引向下一语义profile

目标同上。从`The example therefore supports two scoped conclusions`替换至紧随其后的profile小节之前，保留其他段落。

```latex
For this finite controller, the checks distinguish obligation coverage
from preservation of completing behaviour. The decision profile below
examines another link: whether interpreting a candidate preserves its
choice, and whether that choice meets the stated acceptance policy.
```

## I23d assurance章节收束：将论证交给后续案例

目标：[09-gap.tex](../../../sections/09-gap.tex)。替换`A Worked Assurance Fragment`小节至文件末尾；不重复提前陈述旧C0的迹计数。

```latex
\subsection{Implications for the Worked Example}

The following bridge study examines selected links in this argument.
Its finite model separates obligation coverage from preservation of
completing behaviour, and its decision profile separates semantic
correspondence from candidate acceptance and current-state validation.
Each result supports its own claim; the examples do not form an
automatically composed deployment proof. The tool and physical-control
analyses in Section~\ref{sec:runtime} identify further observation and
effect correspondences beyond these discrete models.
```

## I24 议程编号：区分review问题与未来研究问题

在I9–I12完成后，对研究议程章节依次作以下精确替换；只重命名现有五项议程，不增加或改变问题。

```json
{
  "file": "sections/12-research-agenda.tex",
  "replacements": [
    {
      "old": "The review motivates five questions about the transition from generated artefacts to system-level arguments.",
      "new": "The synthesis motivates five agenda questions (AQ1--AQ5), distinct from the three review questions in the introduction."
    },
    {
      "old": "\\textbf{RQ}",
      "new": "\\textbf{Agenda}"
    },
    {
      "old": "RQ1",
      "new": "AQ1"
    },
    {
      "old": "RQ2",
      "new": "AQ2"
    },
    {
      "old": "RQ3",
      "new": "AQ3"
    },
    {
      "old": "RQ4",
      "new": "AQ4"
    },
    {
      "old": "RQ5",
      "new": "AQ5"
    }
  ]
}
```

## I25 模型判断章节：保留机制比较，压缩重复纠错史

目标：[06-model-as-judge.tex](../../../sections/06-model-as-judge.tex)。替换章节全文，保持标签与原纠错事实。

```latex
\section{Model Judgement, Testing and Unresolved Checking}
\label{sec:oracle}

The \CorpusC{} remaining records in the mapping's mixed category include
model judgement, execution tests and procedures not specified in the
abstract. The classification limitations are documented in
Section~\ref{sec:method}; the synthesis separates their acceptance evidence.

\subsection{Separate the Oracle from the Measurement}

A model's confidence or agreement with another model is not by itself a
semantic check. Such judgements can prioritise review, but their use as
acceptance evidence requires validation against an independently specified
target. Shared training data and prompts can correlate errors.

An execution test with an independently specified oracle can reject a
generated program; a pass establishes conformance on the exercised cases.
Test-driven repair and test generation therefore deserve separate
treatment~\citep{tang2024code,koziolek2024automated}. Their limits concern
coverage and oracle validity, particularly when a model generates both
code and tests.

A benchmark is an evaluation setting, not an oracle type. Scores may
summarise lexical agreement, execution tests or formal checks. FVEval's
formal equivalence and implication checks and AssertionBench's property
checking illustrate the last case
\citep{kang2024fveval,pulavarthi2024assertionbench}; their benchmark status
does not weaken the checking procedure.

\subsection{What Abstract-Level Evidence Cannot Establish}

A missing checker label leaves the procedure unresolved. Likewise,
generating neural traces from a temporal formula~\citep{hahn2020teaching}
is a different task from translating natural-language requirements.
Methods and evaluation implementations are needed to identify the actual
task and oracle. Full-text coding should separately record the oracle,
the object it evaluates, and whether its verdict gates deployment or
only contributes to a benchmark. That coding has not been validated
across the saved collection; unresolved records cannot support claims
that their papers lack verification.
```

## I26 证明章节收束：直接写明定理与需求的关系

目标：[05-generate-prove.tex](../../../sections/05-generate-prove.tex)。替换`The Limitation This Group Shares`小节至文件末尾。

```latex
\subsection{From a Checked Statement to an Engineering Claim}

A kernel establishes that a proof object derives the stated theorem
under its declared assumptions. Relating that theorem to an informal
requirement or to deployment needs further evidence, which other workflow
steps may supply. The review should identify those steps and their
acceptance criteria, just as it distinguishes program verification from
specification validation. Section~\ref{sec:gap} considers how the resulting
evidence supports an engineering argument.
```

## I27 assurance证据记录：合并重复的缺口宣告

目标：[09-gap.tex](../../../sections/09-gap.tex)。替换`The Missing Links to Examine`至`Synthesis Across the Review Questions`之前。

```latex
\subsection{Recording the Links}

An evidence record should identify the claim and formal statement,
artefact version, semantic relation, checker and version, assumptions,
bounds, result status and replayable certificate or log. Translation and
composition steps need records of their own. Failed checks, timeouts,
admitted lemmas and proved results must remain distinguishable. Changes
to a requirement, artefact or environmental assumption should expose
which results require rechecking. These records make the argument
inspectable; their presence alone does not establish that all relevant
semantic dependencies have been supplied.
```

## B1 七项候选书目

前六项沿用D7已核条目，随I7采纳；末项SynCode随I19采纳。均未写入`references.bib`。期刊卷期年与在线日期、预印本与正式版内容的边界沿用[原记录](review_proof_sources_2026-09-13.json)。

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

@article{ugare2024syncode,
  author = {Shubham Ugare and Tarun Suresh and Hangoo Kang and Sasa Misailovic and Gagandeep Singh},
  title = {{SynCode}: {LLM} Generation with Grammar Augmentation},
  journal = {arXiv preprint arXiv:2403.01632},
  year = {2024},
  doi = {10.48550/arXiv.2403.01632},
  url = {https://arxiv.org/abs/2403.01632v4},
  note = {Version 4, 6 November 2024}
}

```

## 本轮验收与后续边界

以下为 9 月 15 日的历史验收；9 月 21 日 AMR 实验与成稿块状态以 I28 为准。

前一批重写独立候选I9–I12及入口说明；本次总计划执行另增I17–I22，形成混合接受、证明接口、约束生成、两项文献剖析、三条RQ综合及新局部profile结果，并同步摘要、限制、结论和制品声明。position paper与公开Forge v2的版本差异另存研究主张文档，未改用户PDF。新bridge制品的实际状态以独立运行记录为准；完整B*、真实LLM抽样和部署原子性未由此完成。

本轮连续全文修订修正接受机制的绝对表述，补充SynCode条件性前缀性质，重排bridge结果并压缩旁支制品说明。编译、版面与当前引用校核见[全文审阅记录](research_manuscript_review_2026-09-15.md)。预览是本候选的派生输出；正文、主书目、历史证据和既有实验数值未改。投稿声明与公开归档仍待作者核定，未提交或推送。

## I28 已执行 AMR 案例：覆盖旧主案例操作，2026-09-21

依据：[实验报告与义务覆盖矩阵](research_amr_v2_results_2026-09-21.md)、[制品入口](../../../formal-artefacts/amr-advisory-v2/README.md)、独立[形式复核](../../../formal-artefacts/amr-advisory-v2/formal-review.md)、[物理复核](../../../formal-artefacts/amr-advisory-v2/physical-review.md)、[真实建议复核](../../../formal-artefacts/amr-advisory-v2/advice-review.md)。这是同一候选入口中的待应用文本，不是另一个完整稿，也不表示活跃正文已经更新。

应用顺序：在 I1–I27 的其余综述修订之后，以下主案例块**整体替换** `sections/10-bridge-case-study.tex` 的旧主案例内容，因此 I8a/I8b、I22、I23b/I23c 不再向该文件追加。旧 bridge 与 SQLite 的制品继续保留，作为补充研究历史，不合并计数。I5 的一般迹语义保留；相关叙述中指向旧案例的锚点须改为本块 `sec:amr-case`。以下摘要/引言/assurance/结论句同时覆盖 I1、I23a、I23d、I15 中相应案例表述。旧 I14 的 bridge 局限可留在补充材料；主文案例局限使用本块最后一段。I16 的制品声明增加本包，不能继续声称只有 bridge 证据。应用与重新编译属于后续成稿工作，本轮只执行实验并交付此单一成稿块。

摘要案例句：

```latex
A bounded industrial mobile-robot case makes these links concrete through
source--model, physical-predicate, permission-timing and progress contrasts,
with a checked finite protocol and separately scoped implementation evidence.
```

引言案例贡献句（覆盖 I23a 的 bridge 句）：

```latex
An industrial mobile-robot case examines selected links between accepted
source artefacts, advisory interfaces and physical execution. Constructed
contrasts isolate missing obligations, while a finite protocol proof,
implementation conformance checks and bounded simulations report distinct
levels of evidence rather than a single end-to-end guarantee.
```

Assurance 章节到案例的衔接句（覆盖 I23d）：

```latex
The following mobile-robot case tests this evidence structure: what a local
check establishes, which correspondence connects it to execution, and which
environmental and scheduling assumptions remain necessary.
```

主案例正文：

```latex
\section{An Industrial Mobile-Robot Case}
\label{sec:amr-case}

Two autonomous mobile robots each transport one load through a shared
single-lane corridor with a pedestrian crossing. A restricted controller
generated at design time supplies the final selection and motion-policy
outputs. At runtime, a language model may recommend A or B; it cannot issue
control events. A trusted interface binds and parses a reply, keeps the
first valid choice, and latches available advice without waiting. The source
selects the advised eligible robot or falls back to the fixed registration
order. This experiment registers A before B once each; it does not implement
general arrival-order fairness.

The case distinguishes four obligations. First, a constructed extraction
fault changes one target-model branch while leaving the source unchanged.
The faulty model satisfies the strengthened policy on all 1,824 declared
inputs, although the source chooses A when the required recommendation is B.
Both source-level functionality and source--model correspondence reject it.
This demonstrates the insufficiency of model-only acceptance, not a unique
detection advantage over exhaustive source checking. All six historical
generation responses still satisfy their earlier optional-preference
contract; only one satisfies the stronger advice-response contract used here.

Second, interpreting Clear as centre clearance produces two releases while
the robot body still overlaps the reservation zone. The same source with
whole-body clearance has none. Both runs complete without collision and
satisfy the discrete permission reference. The violated claim is physical
clearance itself: agreement on a Boolean input does not establish its
interpretation. A historical omitted goal-braking obligation provides a
separate specification-adequacy example; it was exposed by a handwritten
candidate during specification development, not counted as a generated error.

Third, two distinct timing contrasts revoke permission after validation or
after command issue. Omitting the current check produces respectively an
illegal Grant or an illegal Proceed; the latter physically moves the stopped
robot by 0.0025 m outside the shared zone. Their checked counterparts reject
the stale effects. Fourth, waiting for absent advice produces no grant in a
120 s run despite an available road, whereas source-driven fallback completes
both tasks in 58.9 s. Temporary pedestrian blockage clears and permits
completion at 66.1 s; permanent blockage does not. Thus interface-induced
stagnation and unavailable environmental premises are separately observable.

The formal model supplies a scoped composition argument. An independently
defined open trusted protocol accepts arbitrary typed candidate intent for
safety. Provider events carry advice only. An operational embedding splits
actual model runs into these components and a causal mailbox language; the
interface language is defined by transitions, not by reference safety.
Instantiating the existing finite-interleaving authority theorem with silent
provider events and a contractive causal filter, and separately proving
simulation into an independent reference, yields the visible authority bound.
An inherited checked finite-language counterexample shows why silence matters:
a provider's controlled token can extend the visible projection of an empty
trusted trace. This is a reused premise counterexample, not a physical bypass test.
The source-restricted model binds its atomic selection step to the persistent
mailbox and a total legal selector. Under usable permission until Grant,
an effective request and supplied Service opportunities, a separate theorem
gives authorization within at most three such opportunities from any pending
field, allowing arbitrary finite benign gaps and arbitrary advice, including
none. A faulty wait function has a constant state for every natural iteration.
The progress result is not inferred from safety containment.

Isabelle checks these finite-model results without skipped proofs or oracle
dependencies. Exhaustive comparisons match 11,664 Python/HOL core transitions
and 1,296 original-source/HOL selector rows. Fifteen physical runs retain all
expected outcomes, including the deliberately faulty ones. Independent replay
checks source outputs, reference-plant motion and continuous body separation.
Six real advisory replies, from three equivalent task wordings repeated twice,
arrive within a predeclared 3.63 s paced approach to halted staging; all recommend
B and the original source grants B, whereas no-advice fallback selects A.
These calls demonstrate influence through the bounded interface, not improved
scheduling quality or whole-mission real-time control.

The evidence supports distinct links in the review's assurance argument.
The theorem concerns a finite operational model; the implementation link is
finite conformance, and physical completion is observed in bounded simulation.
The progress schedule excludes unrestricted interleavings and does not prove
infinite fairness. Clear geometry, the complete Python driver, distributed
revocation and continuous physical refinement remain outside the proof.
The original physical pre-run manifest omitted some transitive code; a final
snapshot and independent replay improve reproducibility without retroactively
establishing those run-time versions. Pedestrian blockage begins near zero
speed, with a separate 1 m/s fixed-boundary braking calibration. Live decision
records follow the advice cutoff by 0.104--0.120 s and do not validate a hard
real-time compute bound. This single deterministic case is neither an industrial
certification nor a cross-task reliability study. The finite-interleaving
theorem reuse does not establish a complete CKA algebra instance or superiority
over direct state-machine verification.
```

结论案例句（覆盖 I15 的 bridge 论据）：

```latex
The mobile-robot case makes the distinction concrete: model acceptance can
miss a source mismatch, a correct Boolean policy can use a physically
inadequate predicate, and safety containment can coexist with stalled service.
The checked protocol establishes a conditional authority and authorization
result; finite implementation checks and bounded physical runs provide
different, explicitly limited links toward a system assurance argument.
```

本块不改变文献检索方法、综述比较结果或六类文献分类。真实建议的六次接入、历史六次生成和十五次物理运行是不同证据单位，不得合并为一个成功率。完整补充参数、证明对象、独立审计和开放义务引用实验报告。

## I29. AMR 运行时绑定补充（2026-09-22）

来源：[新增结果及范围](research_amr_binding_results_2026-09-22.md)。作为 I28 实现联系段的补充，保留其既有生成、E1–E4、CKA 角色与物理边界。尚未写入活跃 TeX；不是改选工业编排案例。

```latex
An additive runtime adapter makes the remaining implementation link more
explicit. It accepts a fixed request/context binding, parses replies through
the strict mailbox, invokes the original accepted source at each unlatched
selection, and records the resulting protocol events. A further Isabelle
theorem embeds all finite abstract adapter traces into the existing
source-restricted composition, thereby reusing its authority bound. Under
an initially legal request and empty pending choice, two supplied service
opportunities still authorize a robot when separated by any finite sequence
of message inputs. This theorem assumes service supply and does not establish
whole-mission completion or resistance to scheduler starvation.

Exhaustive comparison matches 77,760 complete finite adapter transitions,
including mailbox state and emitted events, with an independently evaluated
HOL table. Twenty-four parser boundary cases supply separate, finite evidence
for the raw-text interface. Four further physical runs replay retained reply
content at declared simulation times: timely B advice changes the first grant
to B, while absent or post-authorization advice retains A first. All four
complete both tasks in 58.9 simulated seconds. These are offline content
replays, not new model samples or a reproduction of network timing.

Trace auditing reconstructs source inputs and modes from checked observations
and protocol state, links source actions to issued and applied commands, and
replays reference-plant movement with independent geometric checks. A negative
audit test exposed an earlier gap: recomputing source outputs from logged
facts alone did not establish that the issued command came from those outputs.
The strengthened audit rejects that self-consistent but ungrounded record.
Thus the case supplies a mechanized abstract composition result, finite
implementation correspondence and bounded execution evidence with distinct
scopes; it does not establish a general Python/JSON preservation theorem,
continuous physical refinement or a complete CKA algebra instance.
```

这一补充不覆盖 I28 关于旧物理清单缺口的历史说明。新批次有独立运行前清单与执行审计；旧清单的事后补齐仍不能追溯证明旧执行版本。统一入口不另建第二份论文整合候选。

## I30. 受限提取的普遍保持与实际制品绑定（2026-09-22）

来源：[AMR 提取结果](research_amr_extraction_results_2026-09-22.md)。接续 I28 源码对应段与 I29 运行时绑定；应把原“仅有有限源码对应”的当前状态更新为下列分层表述，同时保留旧实验的历史方法与结果。

```latex
The source--model link can be strengthened within an explicit profile.
For the AMR Boolean rule language, a mechanized theorem covers the actual
extraction structure: recursive postfix compilation, trailing-negation
cancellation, and priority guards that exclude every earlier raw condition.
For every finite rule table and total Boolean interpretation, the target's
list of enabled action/next-mode outputs equals the source's first-match
result represented as a zero- or one-element list. Compilation also preserves
an arbitrary initial stack. Separate corollaries transfer output properties;
existence of a source output requires an additional nonempty-target premise.

Ten kernel-checked structural equalities connect the modeled extractor to
the actual Python-extracted selection and motion tables of the five retained
source identities. Their preservation corollaries quantify over arbitrary
environments. Additional fixed expression probes connect both executable
expression evaluators to HOL results. The selected identity is the same
original controller used by the runtime adapter and physical traces.

These links retain distinct scopes. The universal theorem concerns the
modeled pure Boolean profile; hashes, frontend tests and concrete structural
equalities connect the retained artifacts to it. They do not prove the
general Python parser/compiler or an unrestricted Java profile. A source
without a matching rule still fails the existing acceptance checks: its
specific exception is represented as no result in the partial semantics,
not converted into an acceptable controller. Likewise, faithful extraction
does not establish the advice-response policy. The previous strengthened
contract accepts only one of the six historical responses. Physical predicate
meaning, action effects, timing and mission completion continue to require
their own evidence.
```

这段不将19个构造表达式或152个成对求值检查视作新LLM样本，不把通用HOL元定理等同任意Python实现证明，也不改写CKA在运行时组合中的角色。

## I31. 运输进展前提的量化与去前提见证（2026-09-22）

来源：[运输进展义务结果](research_amr_progress_results_2026-09-22.md)。本块补充 I28–I30 的任务完成边界。原场景已明确预约持有者能够退出及无永久硬件故障；以下见证去掉该前提，不应写成推翻原条件主张。完整运输的源码／驱动时序精化仍未完成。

```latex
Physical progress requires a separate premise discharge. The original case
already assumes that a reservation holder can exit and that no permanent
hardware fault prevents execution. Numeric speed and acceleration upper
bounds alone do not establish that capability. A mechanized kinematic
countermodel remains stationary forever while satisfying those upper bounds.
One constructed 120-second closed-loop run illustrates the same boundary:
the unchanged controller and adapter grant and apply a legal Proceed, yet a
deliberately non-progressing plant completes neither task. The trace still
matches the abstract authority interface, while exact-reference-plant replay
rejects its missing acceleration. This removes an explicit progress premise;
it is not a failure under the original complete premise set.

For the progressing reference dynamics, a separate real-arithmetic theorem
bounds each rest-to-rest travel profile, and a finite-duration schedule result
accounts for successive segments and turns. Thirty-eight fixed comparisons
connect these calculations to the reference implementation. The staged
route takes approximately 29.7819 seconds under sustained Proceed. Four
previously retained full executions satisfy the checked local service,
observation, command and completion budgets, with the last task finishing at
58.9 seconds. Adding conservative local bounds yields a conditional
70.2-second two-task budget. The universal source/driver discharge of those
local timing bounds remains open; the accounting theorem and bounded trace
checks must not be presented as a proved whole-system deadline.
```

这项扩展零API调用，只新增一次构造plant运行；38项动力学比较、四条旧轨迹新审计及12项测试均不是新生成样本。不得将安全包络、精确参考plant和全部原始进展前提混成同一个契约。仍只维护本整合候选，活跃TeX未改。

## I32. 稳定闭环时序与条件完成界（2026-09-22）

来源：[稳定闭环时序结果](research_amr_closed_loop_timing_results_2026-09-22.md)。本块接续 I31，把先前作为开放项的固定源码／驱动局部时序在稳定环境下具体化。它不覆盖暂时阻塞恢复、任意调度、一般 plant 或硬件期限，也不把局部不等式改写为无前提完成。

```latex
For the fixed stable execution profile, the remaining local timing obligations
can be made explicit on the driver's 10 ms integer clock. A kernel-checked
scheduler model bounds observation and body-clear release by nine ticks from
their quantized event ticks, applied motion after a stable grant by 163 ticks,
and reported Finish after a quantized physical-arrival tick by 169 ticks.
Measured from exact between-tick continuous events, the corresponding generic
outer bounds are less than 10 and less than 170 ticks. Concrete evaluation of
the accepted source and its extracted target covers eight milestones from
unusable observation through release, goal braking and completion. A separate
protocol lemma shows that, after a valid release, a still-registered legal
request is granted by the selector--Validate--Commit sequence.

Composing these results with the previously justified 3,100-tick exact-
reference travel service, including arrival quantization, gives a conditional
two-task bound of 6,884 ticks, or 68.84 seconds. The theorem states the local
service inequalities as premises; it is not a whole-Python or hardware
deadline. Independent checking exhausts 1,001 event times and 201,402
grant/brake-age/mode combinations. Four retained physical runs, reused
without rerunning them, meet the stronger bounds and still finish at 58.9
seconds.

The Boolean AtGoal tolerance is kept distinct from exact physical arrival.
The trace audit reconstructs the endpoint-rest time from motion pieces before
checking Brake and Finish. This avoids treating a source predicate as the
physical effect it is intended to summarize. The result therefore adds a
bounded source/scheduler layer to the existing extraction, authority and
reference-dynamics evidence while retaining their separate assumptions.
```

本块的 15 项测试、八个里程碑和穷举时刻不是新 LLM 样本；四条物理轨迹来自既有运行时绑定批次。零 API 调用、零物理重跑，活跃 TeX 未改。
