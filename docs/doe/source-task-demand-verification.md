# 原文 → Task → demands 改造与验证记录

日期：2026-10-15。当前协议入口见 [正式分析链](joint-pipeline.md)、[独立 Task](task-evidence.md)、[逐 seed 需求](backward-demand.md)和[敏感范围对照](sensitivity.md)。本记录将工程一致性证据与模型语义效果分开；测试数存在重叠，不合并成一个总数。

## 已实现的责任边界

- 独立 Task 提取仅接收冻结源文、独立用户任务及目的依据身份。Task v3 保存唯一要求释义、全部非空物理行处置和冲突／歧义；没有 CFG bindings。Task 原始版本和隔离修订分别封存。
- 标注引用精确 Task 版本，逐 requirement 返回 realization 和剩余 gaps。六类正向需求为 `value / presence / cardinality / shape / truth / action`；禁止事项和未支持限制不能通过一个 constraint/prohibit goal 冒充完整表达。
- 编译器生成原始 demand 指针到 goal 的映射；每条需求推导有独立 `seed_goal_id`。程序生成源文、requirement、realization、raw demand、goal、推导和 sink 的对应，不要求模型再手抄一份映射。
- 审查必须独立登记源范围、每项 Task、每个原始 demand 和全部 IR。程序拒绝缺记录、重复覆盖、虚假引用，以及没有关联 finding 的问题结论；这不证明审查判断正确。
- Task 问题仅投影成有限类别、源范围和已有 requirement ID，交给只读源文的修订器。旧意见自由文本、CFG、当前载荷、goals 和 DOE 不进入修订输入。修订后完整重建标注；仅标注错误则固定 Task 修复。两路共用一轮语义修复，随后在新上下文完整复审。
- 主 pipeline 保留用户入口；Task 独立拥有，标注保存 `task_ref`，加载器解析供内存消费者使用。正常、标注修复和 Task 修订分别是 3、5、6 次语义调用；结构纠正、传输重试另计。
- 传播事实、冻结输入和历史运行不做迁移。当前运行中的 Task 来源单列为独立 Task run、显式人工 fixture 或未知；不将人工基准当成真实模型提取证据。

## 工程测试证据

以下分组均使用工程夹具或注入客户端，不能解释为真实模型的检错率。

| 验证分组 | 已完成结果与范围 |
| --- | --- |
| `tests/test_source_task_pipeline.py` | **3 passed**：三条完整持久化路径的 3／5／6 次调用、Task 修订隔离、旧 Task 不变、新标注引用新 Task、只读加载和离线重放。 |
| `tests/test_cli.py tests/test_installed_cli.py tests/test_pipeline_boundaries.py` | **12 passed**：CLI、离线阶段中断／恢复、外来 DOE 替换拒绝、不同任务子阶段拒绝、伪造完成状态拒绝、严格整数策略，以及完整运行依赖树移动后加载／重放。 |
| Task、准备恢复与 Task run 映射 | 最终 **44 passed**：物理行登记、版本及来源、隔离修订字段、源映射、Task／结果篡改、布尔值与整数区别、冻结输入目录保护、保存 producer 自一致性，以及 Task 准备中断后仅从冻结 owner 严格恢复。 |
| 标注契约／编译／教学例 | **229 passed**：固定 Task、需求与处理契约、原始到编译映射、引用和处理关系。另有提示词／联合敏感性分组 **37 passed**。 |
| 持久标注／请求身份 | **66 passed**；加载、持久身份、输入 owner 和编译边界另组 **48 passed**。 |
| 四轴审查核心与报告 | **80 passed**：独立源范围、逐 requirement／seed 覆盖、finding 关联和报告。 |
| DOE／逐 seed 推导 | 已完成分组分别为非慢组 **275 passed**、来源组 **4 passed**、运行完整性 **19 passed**、正式 runner **15 passed**；其中有重叠。多种子合流、推导种子身份与确定性已覆盖。 |
| Task 来源补充校验／报告 | **13 passed**：真实持久化来源链、Task 摘要、重新封存来源造假拒绝、未知来源和当前 v4 metadata 的只读兼容。 |
| 旧工具接入 | 工具／站点分组 **59 passed**；driver 组首次 **105 passed, 1 failed**，旧 fixture 字段迁移后该项定向 **1 passed**。runner 组首次 **102 passed, 1 failed**，补齐迁移 fixture 的 Task owner 依赖后该项定向 **1 passed**。没有将首次失败写成整组一次全绿。 |

完整主 pipeline 的较慢回归和修复调用中断边界的最后定向结果，见下方最终补充；不能把未完成的组算作通过。代码稳定后的 `compileall` 与 `git diff --check` 均已通过。

## 真实模型探索性证据

独立于教学示例的合成评测库包括同一行多项限制、Task 与处置同时漏项、过宽 seed、错误位置、错误版本、错误接收方、真实全值要求和正确输出目标引出的保守依赖等案例。评分器要求逐 finding 的语义裁定台账，不能用字符串匹配代替语义匹配；未决的基准缺口单列，注入客户端不计作在线实验。

本轮仅真实调用了两个候选的审查阶段，两例都指出了预置问题：遗漏禁止事项和 title 需求扩大为整对象。第一例另有两条意见涉及合成基准说明不足或审查过严的可能，保留为 `needs_baseline_review / oracle_gap`。其余六例未运行，没有真实测量独立 Task 提取和修复的成功率。

完整材料、usage、逐项助手裁定和未决问题见[两例探索性实测](../../experiments/doe/runs/source-task-review-v1-20261015-live/assessment.assistant.md)。参考案例由助手编写，复核也由助手完成，**尚未建立独立人类专家确认的金标准**；本轮不报告总体准确率、检出率或误报率。

## 当前能力边界

行级覆盖、引用合法、四轴记录齐全和确定性计算，都不能证明自然语言要求穷尽、每个 demand 最小、所有路径可执行或不存在 DOE。源文自身仍可能混合功能要求与实现步骤，提取者和审查者也可能共同漏掉同一语义。

未形式化的次数、顺序、质量、禁止事项及条件缺口继续限制结论。当前没有独立可信的局部影响证明机制，这些缺口按全局保守处理；任意模型 binding 不能把它们缩成局部。受影响结果保留诊断计算，不升级为受支持的缩减结论。没有新增通用禁止检查器、路径求解器或重执行验证器。

完整依赖链会重复验证输入、请求及接受记录，持久化端到端回归较慢；本轮没有用跳过完整性校验或弱化身份检查来缩短测试。

## 最终补充

源码稳定后，以下最后定向组 **5 passed，315.69 秒**，没有弱化 producer 身份规则：

```powershell
python -m pytest `
  'tests/propagation/review/test_refinement.py::test_interrupt_does_not_start_later_calls_and_accepted_repair_is_not_resent[repair_accept]' `
  'tests/propagation/review/test_refinement.py::test_one_repair_stop_rules_resume_and_zero_api_replay[modes9-None-review_passed-4-repair]' `
  tests/propagation/review/test_refinement.py::test_repair_freezes_the_original_independent_request_once `
  tests/propagation/review/test_refinement.py::test_accepted_task_revision_interruption_replays_child_receipt_and_resumes_once `
  tests/propagation/review/test_four_axes.py::test_task_only_target_cannot_be_laundered_into_annotation_repair_domain `
  -q --disable-warnings --maxfail=1 --tb=short
```

该组覆盖了标注修复／Task 修订已接受调用后中断的子阶段 receipt、零 API 重放及不重发恢复；首审／复审结构纠正；独立用户任务保持；以及纯 Task 目标不能通过错误的 annotation domain 路由到固定 Task 修复。父阶段中断点现在区分 `before_repair / during_repair` 和 `before_task_revision / during_task_revision`，重放会先核对已经开始的子阶段记录。

最后的准备恢复与保存 producer 校验命令为：

```powershell
python -m pytest tests/task tests/test_task_preparation_boundary.py tests/propagation/test_task_runs.py -q --tb=short
```

结果 **44 passed，15.54 秒**。这取代上表早期 23 项分组的记录，不能再相加。

最后又针对稳定代码执行正常三调用路径的完整加载／重放：

```powershell
python -m pytest 'tests/test_source_task_pipeline.py::test_recorded_paths_and_readonly_replay[None-3]' -q --tb=short
```

结果 **1 passed，73.09 秒**。它是前面三路径组中正常路径的复验，不增加独立案例数。`python -m compileall -q src/skillflow tools/doe tools/propagation tests/task tests/test_task_preparation_boundary.py tests/test_source_task_pipeline.py` 与 `git -c core.whitespace=cr-at-eol diff --check` 均退出成功。

另外启动的 `tests/test_pipeline.py` 旧慢组因与上述已完成检查大量重叠而停止，**未完成，不计整组通过**。没有执行整仓全量 pytest。早期并发修改源码导致的 producer 身份竞争，以及一次修复调用中断的真实重放错误，均未被当作通过；身份竞争项和真实边界修复已纳入上述稳定窗口的定向重跑。Task 准备中断造成根运行无法续备的问题也已由 44 项分组验证修复。
