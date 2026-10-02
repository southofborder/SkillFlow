# 004 conditional-notification｜面向新 DOE 的简评

样例：**N04**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/004-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/004-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/004-conditional-notification.png)。

核心链：主文件纳入 workflow，读取事件及包内正文配置，筛选后逐条将 summary 发给 recipient，结束后写本地 count.txt。`ir_011/ir_012 → ir_013` 绑定同一当前记录；[payload.json 第 2 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/payload.json:2)固定 body_from 为 summary。

未发现已证实的关键载荷或去向缺口。新 DOE 应同时读取 [workflow 的字段要求](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/references/workflow.md:11)与现有约束，避免把配置字段名当作任意载荷选择，也不能把 external_resource 类型本身当作网络外发证据。

- 保留包内配置的来源身份、summary 原值和对应接收人；继承 token 禁令，完整事件仍不等于发送内容。
- 固定配置是否单列读取、计数在循环前计算、处理条数口径等问题降级。除非配置来源被证实替换并改变实际正文，否则不把这些表示细节作为进入 DOE 的阻塞条件。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

