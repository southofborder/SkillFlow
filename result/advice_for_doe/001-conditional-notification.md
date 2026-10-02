# 001 conditional-notification｜面向新 DOE 的简评

样例：**N01**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/001-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/001-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/001-conditional-notification.png)。

核心链：events.json → 按退订、紧急及数值筛选 → 将当前记录的 summary 原值发给其 recipient → 完成后写本地 count.txt。`ir_005 → ir_008` 保留载荷与接收对象；[原文第 11–14 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:11)规定逐条发送及 token 禁令。

未发现已证实的关键过程缺口。新 DOE 应识别退订限制同时约束两个选中条件，紧急只豁免数值门槛；access_token 出现在读入记录中，不等于通知消费或发送了该字段。

- 保留字段原值、对应接收人与全局禁令；不能将整条可用记录视为通知载荷，也不把正常通知自动判作越权。
- “处理条数”被解释为选中数属于通用保真未定项，主数据链已在。将统计口径降级，不阻塞后续 DOE，也不自行改成总数或成功数。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

