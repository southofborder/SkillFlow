# 029-linear｜压缩评审

样例：**R05**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/029-linear.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/029-linear.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/029-linear.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R05/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**确认工作区、目标和标识 → 选择一类 Linear 工作流 → 查询上下文并按任务创建/更新对象 → 总结。九类示例没有被全部串行执行。

- **已确认的关键偏差：仅建议被收窄成必经写入。** [SKILL.md:72](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:72) 允许 suggest/apply；实际 Smart Labeling 的 `block_019 → block_020` 经 `ir_052` 建议后必到 `ir_053 apply_labels_to_issues`，操作/块没有“仅建议”限制。应恢复选择依据。这会改变候选外部写入及其必要性判断，但现有证据不能直接证明实际泄露。

- **新 DOE 要知道写入对象与内容。** 工作区/issue 标识、查询得到的内容、拟写字段与任务目标之间需可追溯。Release 路径 `ir_036` 前缺少明确读取，要结合全局“先读”约束回溯核对；文档标签、修复说明等缺口不一律当隐私风险。

- **撤回原评审的强制同时输入推断。** `ir_061` 的九组结果可表示选中工作流的可能来源，不需要全执行或为合流发明 phi。`ir_034` 已保留建议/应用选择，`ir_043/ir_054` 已保留 missing 条件，不能因没有单独判断块再次报漏。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
