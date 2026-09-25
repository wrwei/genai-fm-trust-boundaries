# AMR-Corridor：参考仿真与失败见证

Record-maintenance note (2026-09-22): affected records and execution copies were postprocessed at the user's request. Checksums now describe the maintained snapshot; see repository directory formal-artefacts/record-maintenance-2026-09-22. Raw replies, controller source bytes and physical trajectories are retained.

这是AIR研究案例的**第一阶段可执行环境**：手写参考监督器、固定路线连续运动、独立几何判定和明确命名的故障注入。它不包含LLM生成器、受限源码提取验证或新形式证明。

研究依据：[场景规格](../../literature/scholar_search_2026-09-10/followup/research_amr_scenario_2026-09-15.md)、[评价协议](../../literature/scholar_search_2026-09-10/followup/research_amr_evaluation_2026-09-15.md)、[实施计划](../../literature/scholar_search_2026-09-10/followup/research_amr_implementation_plan_2026-09-15.md)。结果解读见[研究结果说明](../../literature/scholar_search_2026-09-10/followup/research_amr_results_2026-09-15.md)。

## 运行

Python标准库即可运行；无需安装ROS或外部软件包。开发验证环境的具体Python版本见最终清单。

```powershell
Set-Location -LiteralPath 'formal-artefacts/amr-corridor'
python -m unittest discover -s tests -v
python run_suite.py --output results/my-reproduction
```

若系统没有python命令，可使用本机已定位运行时：

```powershell
& 'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' run_suite.py --output results/my-reproduction
```

输出目录必须尚不存在，以保留旧运行。固定场地的参数JSON由SHA-256绑定；修改JSON会明确拒绝，须同时适配实现并重新验证。这不是任意地图／任意参数仿真器。`dt=.005`、先行次序、规定的行人模式、观测中断、front-only清空和停车见证的实际制动变化是本轮明确支持的变体。

## 组成和独立性

| 文件 | 责任 |
| --- | --- |
| `plant.py` | 已送达意图驱动分段解析运动，返回可重建的MotionPiece；无controller／oracle导入 |
| `controller.py` | 延迟观测、参考选择、整车清空、预约及带序号／版本的执行接受；不读plant真值 |
| `oracle.py` | 独立凸多边形距离和连续区间检查；不读控制器谓词或plant内部状态 |
| `simulation.py` | 时钟和消息队列、传感采样、控制决策、真实轨迹评分；控制路径与评分路径分别取数据 |
| `run_suite.py` | 固定试验集、完整轨迹／事件、细步长重跑、运行前后身份检查及输出清单 |

两个AMR从已装载的等待位出发，沿各自固定路线到目标工位；省略等待位前的装载／驶入行程。低层在每个路线折点停稳，再以有界角速度原地转向。轮廓随转向连续变化。制动不瞬时归零；原地旋转省略角惯性，收到Brake后角速度可立即置零，不能据此主张真实底盘性能。

车车、车墙、车人均按整车矩形评分。速度界覆盖旋转角点运动。该数值算法未经形式证明；结果中的距离为保守下界，不是精确最小距离。单独的测试含“端点分离而中间穿越”和旋转扫碰情形。

## 场景与时间

完整episode使用0.01 s输出步长、0.05 s监测周期、0.05 s传感交付延迟和0.10 s指令计算／传输／起效总延迟。传感数值当前无注入定位误差，仍按设计误差界检查。指令到期检查针对接受时刻；这里只实现单通道和确定性有界交付，没有丢失控制命令或完整通信故障模型。

同一时刻固定执行顺序：传感采样、接收、监督／预约决策、指令交付、连续运动区间。先行建议是显式输入的A或B，**并非真实LLM响应**。版本固定为1；旧版本、错误对象及旧序号拒绝由单元测试覆盖，但没有声称完整运行时制品绑定已实现。

人员时序固定：t=10 s从H南侧开始以1 m/s横穿，t=17 s离开；永久阻塞变体到中心后停留。人员在t=10 s的可见出现不是任意遮挡模型。参考监督器收到阻塞立即制动；记录该时刻的停车条件，而未证明对任意新行人都保持可行域。

停车C07另用直线边界见证：机器人初速度1 m/s、初始车头距离3.6 m，观测延迟0.10 s，监测0.05 s，指令生效0.10 s。两组均从同一可行初态开始，只有停止判据是否省略反应项不同。它不与整个双车运输episode混成同一统计样本。

## 证据入口

- [最终结果汇总](results/reference-2026-09-15/summary.json)、[运行身份清单](results/reference-2026-09-15/manifest.json)。
- [行为测试日志](tests_final.log)、[固定试验集日志](suite_final.log)、[独立审查](review_report.md)。
- 每个运行有结果JSON和`.trace.jsonl.gz`。完整episode轨迹包含所有采样包、丢弃、指令、预约、完成事件及每个输出区间的连续MotionPiece；停车见证的决策观测记录在结果JSON，连续运动记录在压缩轨迹。
- 7个基础episode＋3个细步长episode；3个基础停车见证＋2个细步长停车见证；另有1个几何快照。它们不是15个独立工业场景，也不估计工业失效率。
- `reference-2026-09-15-initial`是明确标记的开发记录，运行时源码身份不完整，不能引用为最终证据或额外独立样本。

## 覆盖和限制

| 评价编号 | 本轮实际覆盖 |
| --- | --- |
| C01 | 两种给定先行次序的双车闭环；无自然语言解释 |
| C05 | 车头清空故障的几何见证及完整闭环；记录过早释放，不能无中生有地称为碰撞 |
| C07 | 条件内固定边界的完整／缺反应项停车对照；独立记录安全余量与真实越界 |
| C08 | A车5秒观测中断、停车、保留预约与恢复；未实现任意网络故障／令牌回收算法 |
| C10 | 一条预定人员横穿时序的条件内停车与恢复 |
| C12 | 永久阻塞、一直停车参照、制动下界之外的直线压力见证 |
| 其余及未覆盖部分 | C02真实任务语义、C03生成器、C04源码提取、C06一般适配错误、C09完整交错、C11近距突现等仍待执行 |

已完成标记只属于本目录记录的参考环境阶段。生成候选质量、语义保真证明、普遍安全／活性、外部机器人栈一致性、实机标定和认证均未获得证据。
