# 002 conditional-notification｜面向新 DOE 的简评

样例：**N02**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/002-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/002-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/002-conditional-notification.png)。

核心链：读取 events.json，逐条判定 opted_out 非 true 且（urgent 或 value ≥ 100），将 summary 原值发送给同条记录的 recipient，最后写 count.txt。`ir_007 → ir_008` 直接传递两项字段；[原文第 10–14 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N02/SKILL.md:10)明确发送范围和 token 禁令。

未发现已证实的关键过程缺口。段落写法没有改变任务与数据去向；新 DOE 应结合实际字段输入与继承约束，而非因为完整记录含 access_token 就认为该值已到接收人。

- 保留选中条件、原字段及对应接收人，区分记录读取、通知消费和本地计数三类关系。
- 尾部选择选中数的统计口径仍需通用回溯标记，但不决定当前通知的载荷或接收人。计数实现形式、循环块数量和操作命名均可降级，不要求为后续判定重写 IR。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

