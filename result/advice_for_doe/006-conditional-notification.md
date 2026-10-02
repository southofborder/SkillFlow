# 006 conditional-notification｜面向新 DOE 的简评

样例：**N06**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/006-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/006-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/006-conditional-notification.png)。

核心链：`ir_003` 将 events.json 按完整条件筛选，`ir_005` 形成 recipient／record_id 载荷，`ir_007` 按每条一次发送，再写本地计数。[原文第 12 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N06/SKILL.md:12)明确 body 是 record_id 原值，此处没有摘要生成。

关键操作与字段差异已经保留。集合抽象不是已证实的过程遗漏；新 DOE 应重点保留每条载荷到对应接收人的关系，不沿用其他 N 样例的 summary，也不能把整条事件当作发送参数。

- 结合原有字段和每条约束解释对应关系；如仍不确定，报告关联未决，不直接判单次调用、跨记录串发或实际泄露，不强求显式循环。
- 空集边的展开和计数口径可降级；退订条件及全局 token 禁令仍应继承。该例的真实关键区别是输出字段变化，不是块数变化。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

