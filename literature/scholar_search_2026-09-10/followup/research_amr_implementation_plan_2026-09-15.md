# AMR参考仿真与失败见证实施计划

> 执行方式：使用 subagent-driven-development 分派独立运动模型与碰撞判定任务；根代理负责控制、事件闭环、结果和最终整合。沿用用户指定local目录，不提交、不推送、不清理。

**Goal:** 将已认可场景的第一阶段做成可复运行的参考闭环和可检测失败见证。

**Architecture:** plant执行实际送达的指令，产生连续分段运动；控制器只读取延迟观测；独立oracle从真实轮廓和连续运动评分。运行器记录发送、送达、制动、预约和完成事件。

**Tech Stack:** Python标准库与unittest；可选Pillow绘图，不安装机器人栈。

**Spec:** [场景规格](research_amr_scenario_2026-09-15.md)、[评价协议](research_amr_evaluation_2026-09-15.md)。这是参考环境阶段，不实施全部12类评价或真实LLM接入。

## Global Constraints

- 合成参数来自 research_amr_parameters_2026-09-15.json；机器人0.8×0.6 m，限速1 m/s，前向加速度0.5 m/s²，制动下界0.8 m/s²。
- 观测年龄界0.10 s、监测周期0.05 s、计算界0.02 s、制动传输与起效界0.08 s；不把Brake指令当成Halted。
- 只实现手写参考监督器、R-Stop及明确命名的故障注入；不声称为生成控制器G。
- 不将令牌到期或失联当成整车清空；控制器不得读取plant真值。
- 碰撞评分不可复用控制器clear或停车公式；离散帧未相交不足以判安全。
- 保留原152项指纹、正文候选与37页预览；新运行结果单独保存。

## Task 1：独立几何与连续碰撞判定

创建 `formal-artefacts/amr-corridor/oracle.py` 和 `tests/test_oracle.py`。无控制器或plant导入。

接口：`rectangle(pose, length, width)`返回凸多边形；`polygon_distance(a,b)`返回实体间距离（相交为0）；`sweep_check(pose_a, pose_b, length_a, width_a, length_b, width_b, duration, speed_bound_a, speed_bound_b)`返回带status（clear/collision/unresolved）、witness_time和保守距离下界的字典。pose回调接受区间内相对时间。

- [x] 写帧间穿越失败测试：两小矩形在端点分离、t=0.5相交；断言collision。写静止分离、旋转角扫碰撞、刚好接触、无效运动界拒绝测试。
- [x] 运行unittest保存红灯；实现独立凸多边形SAT及边距离。
- [x] 用区间中点距离与点速度上界做自适应连续分离检查，不能确认时返回unresolved，不能返回clear。
- [x] 运行测试、记录数值容差与该算法未获形式证明的限制。

## Task 2：有时间的固定路线plant

创建 `formal-artefacts/amr-corridor/plant.py` 和 `tests/test_plant.py`。不得导入controller或oracle。

接口：`RobotPlant(route, length=0.8, width=0.6, speed_limit=1.0, accel=0.5, brake=0.8, turn_rate=pi/2)`；属性pose=(x,y,theta)、speed、finished；`advance(dt, intent)`接受Proceed/Brake，返回按时间先后组成的MotionPiece列表。每段有duration、`sample(t)`和point_speed_bound；区间内位置／角度可连续求值。

- [x] 写解析制动测试：速度1、制动0.8时1.25 s停稳、位移0.625 m，继续制动不倒车。暴露实际运动测试初态的合法构造接口。
- [x] 写完整折线路线测试：停稳后有限时间旋转、无有限速度瞬时拐弯、恢复可到终点、dt分割不改变解析终态。
- [x] 运行红灯；实现分段有界加速、匀速、减速和原地转向。每段末端精确处理运动相变；不得用安全检查器公式生成轨迹。
- [x] 运行绿灯，自审物理简化和数值容差，记录独立模块限制。

## Task 3：参考控制器与事件闭环

创建 `controller.py`、`simulation.py`、`tests/test_controller.py`、`tests/test_simulation.py`。

接口：不可变Observation含robot_id/sample_time/pose/speed/blocked/mission_revision/map_revision；控制器按观测选择Proceed/Brake并记录原因。Reservation只有一名owner，fresh整车退出后释放；Command绑定robot_id、seq、revision、issued/delivery/expiry；执行器拒绝旧序列和旧版本。

- [x] 写测试：车头出Z而尾部仍在→不能释放；超时不能回收占用；新Brake送达后旧Proceed拒绝；延迟观测仍包含误差和反应时间。
- [x] 红灯后实现控制和事件队列。两个AMR从已装载的等待位出发，省略等待位以前的装载行程；固定每车一次任务。
- [x] 实现按参数运行的正常A先/B先、暂时人员阻塞、永久阻塞、R-Stop。每个实际步由plant段构成，oracle检查车车、墙和行人。
- [x] 检查条件内停车与恢复；人员时序事前固定，不能依据比较组结果改变。缺陷见证若没有碰撞，只报告其实际违反的义务。

## Task 4：失败见证、记录和复核

创建 `run_suite.py`、`README.md`、`results/`与研究结果说明。

- [x] H1：同一实际几何，比较front-only与whole-body清空；独立oracle确认尾部仍占Z。另运行提前释放消融，只报告实测后果。
- [x] H2：从同一可停车初态接近固定边界，完整判据与遗漏反应时间的判据分别闭环推进；记录真实越界／余量及Brake→Halted时延。
- [x] 输出完整事件／运动分段、参数／代码哈希和环境身份；失败注入和正常运行分开。
- [x] 运行全部行为测试、试验集和更细步长复核。逐项报告安全、正确完成、超时、未确定碰撞区间及保证前提，不做可靠性推断。
- [x] 子代理独立代码与证据范围审查；修正发现后复核，更新进度并交付。

## 实施预检

| 任务关系 | 一致性检查 |
| --- | --- |
| 1→3 | oracle只消耗时间区间内pose回调与可信运动界；不依赖控制器的安全谓词 |
| 2→3 | plant输出MotionPiece，可按两车相变时间切分重叠区间后供oracle检查 |
| 3→4 | 运行结果保留完整连续分段，评分与控制分开；人工故障不会被写成LLM错误频率 |
| 各任务内部 | 测试期望来自解析轨迹、人工几何和协议义务；测试先于实现；现有研究文档不承担软件测试 |

本阶段已执行。精确实施差异、测试命令和审查结果见同目录 `research_amr_execution_2026-09-15.md`。
