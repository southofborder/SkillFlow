# SkillFlow 项目长期记忆

Cross-computer continuation: read [Research and chat handoff](docs/research-chat-handoff.md)
before continuing work from a new environment. The current choice is GitHub plus
a local checkout; Cloud creation is paused. The research pipeline remains frozen
for comparison. Installation and offline checks do not authorize model calls,
calibration resume, long experiments, or changes to the research protocol.
The handoff distinguishes committed material from newer local-only preparation.

讨论或实现 DOE 前，先阅读 [DOE 目标与设计原则](docs/doe/SkillFlow-DOE目标与设计原则.md)。这是 2026-10-06 确认的当前目标基准；后续用户明确修订优先。

核心目标：**面向 Agent Skills 的任务相关静态数据最小化分析，结合敏感数据来源、沿途处理、路径条件和接收方，以发现所有非必要敏感数据暴露为目标。**不必要动作和必要动作中的多余敏感载荷都在范围内，不能按动作必要性预先筛掉 sink。“动作必要不代表它携带的每份数据、每个敏感字段都必要”是重点强调的独特贡献点之一，不是总目标的范围限制。敏感数据到达 sink 或边界等级高，也不直接等于 DOE；“所有”是覆盖目标，不是当前零漏报保证。

当前架构是 `src/skillflow/` 下的构图、传播和后续 DOE。`common` 提供共用能力；旧 SFG/FCG/DOE 及 `skill_ir` 属于历史材料，不是现行接口。现行规范入口为 [文档导航](docs/README.md)。

坚持“原样传递，不自动缩小”；`possible` 依赖不等于全部明文包含。契约补充的观察是静态可能关系，不是运行实测。保留明确局部机制、数据版本、条件和接收方；不把核对通过、事实保持证明或传播完成描述为已证明自然语言语义等价或不存在 DOE。

新 DOE 结果独立保存，不回写冻结输入或传播事实。现行任务基准先由只看源文与用户任务的独立阶段提取并封存；后续标注仅引用 Task 版本，用 realizations 交代六类正向需求及未表达限制。审查须覆盖源文、Task、每个 seed 与全部 IR；Task 错误只经有限类别与源范围隔离修订，随后完整重建标注。最多一轮语义修复，不以行级覆盖、审查通过或计算完成证明语义完整、限制满足或需求最小。不能恢复旧评分引擎。

Current constraint extension: realizations may express supported constraints
separately from positive demands. Review uses declaration_checks for both kinds.
Forward constraint checks do not prune propagation facts or create demand seeds.
Unsupported restrictions remain explicit limitations. Consult the current
[constraint reference](docs/doe/constraint-implementation.md), not older version
descriptions, for exact interfaces and guarantees.

Language policy (confirmed 2026-10-16): project discussion may use Chinese. All maintained prompts, synthetic examples, generated interpretations and evidence reasons, program diagnostics, and new reports use English, including new runs of 001, 010, and 013. Genuine source text, user input, and quotations retain their original language. Do not translate or rewrite frozen historical artifacts. Update corresponding tests without removing multilingual input and reference-preservation coverage.
