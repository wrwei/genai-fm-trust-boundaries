# 独立目标模型模块报告

日期：2026-09-15。

`model.py`只从`language.py`导入不可变Program类型及模式／事实名称常量，不导入或调用源码求值函数。源码解释器遍历表达式树并首匹配返回；目标编译器把条件编译为PUSH、LOAD、NOT、AND、OR后缀指令，再由独立栈算法执行每一条目标守卫。

第i条正常目标守卫为其条件与所有前序条件否定之合取。目标返回所有启用结果的tuple，保留重复结果；没有启用规则时返回空tuple。目标模式谓词由`model_step`根据模式内部导出；外部必须传入精确键集合与精确bool值，否则抛出ValueError。

接口：`extract_model(program, fault=None)`返回冻结Model；`model_select(model, facts)`返回动作tuple；`model_step(model, mode, facts)`返回(action, next_mode)的tuple。`Model.to_dict()`输出可JSON序列化的独立副本，包含原schema、提取故障标记、目标编码标识、目标规则及完整后缀守卫。序列化记录不是新的输入加载器。

三种故障均为明确注入的实验条件，不声称真实提取工具存在这些缺陷：

- `omit_priority`删除所有前序否定，可显示多个启用结果，包括重复动作。
- `choose_b_when_both`将每个SelectA目标守卫拆为双方申请时SelectB、其余时SelectA。其他守卫及优先关系不变。
- `invert_observation_tests`仅翻转step表达式中每个ObservationUsable出现的极性，包含原本受not包裹的出现；翻转条件用于当前规则及后续优先级排除。

验证命令（工作目录为本模块目录）：

```powershell
& 'C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p test_model.py -v
```

红灯：实现前运行8项测试，8项均因显式断言“target model is not implemented”失败，exit code 1。绿灯：实现后同一命令8项全部通过，exit code 0。覆盖首匹配／关系优先级差异、重复启用结果、7种模式导出、组合布尔表达式真值表、双方申请故障的4种组合、观测正反极性、严格输入、未知故障、空目标关系及证据副本隔离。

范围限制：本模块假设Program已经通过语言层解析，不负责重新验证人为直接构造的任意AST或外部篡改的指令对象；没有外部目标模型反序列化入口。测试不构成形式化编译器正确性证明，也不把抽象枚举输入称为已证可达状态。完整1824组对应与义务检查由验收模块执行。

## 闭环发现后的义务修订 v1.1

真实集成发现：旧v1参考程序在已经释放、到达目标但尚未确认Halted时继续Proceed，无法建立持续Brake所需的停稳确认。当前验收规格更新为`amr-supervisor-obligations/v1.1`，在安全阻塞之后、Finish／Release之前加入`AtGoal and Released and not Halted → Brake, BrakeRequested`，并更新所有后续义务的互斥排除。JSON语言schema保持v1，目标提取／执行算法未修改。

先加入两个回归测试：目标输入的动作要求，以及旧v1源码在新规格下拒绝。修复前11项验收测试中这两项失败，分别显示Proceed输出与旧源码仍被接受；修复后同一命令`python -m unittest discover -s tests -p test_assurance.py -v`的11项全部通过。

当前9个候选中参考程序和DeMorgan等价程序通过1824组验收；其余可解析候选的源码／目标违规输入数分别为：ignore_pedestrian 187、always_brake 187、early_release 42、finish_unhalted 28、reversed_observation 374、goal_stop_gap 25。无提取故障时这些候选的对应不一致数均为0；external_call在解析阶段失败。finish_unhalted同步删除目标停稳分支与Finish停稳条件，确保预期缺陷不会被新的优先分支遮挡。goal_stop_gap与`development/spec-v1/source.json`逐字节相同，归档文件未修改。规格修订来自已记录的集成反例，不追溯声称原v1已经包含此义务。
