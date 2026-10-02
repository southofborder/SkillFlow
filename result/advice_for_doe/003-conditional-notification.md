# 003 conditional-notification｜面向新 DOE 的简评

样例：**N03**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/003-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/003-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/003-conditional-notification.png)。

核心链：events.json 经 `ir_003` 完整筛选为 eligible_records，`ir_005` 提取 recipient／summary 集合，`ir_007` 按每条一次的约束发送，随后写本地计数。[原文第 13–16 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N03/SKILL.md:13)限定当前记录字段、未选中不发及 token 禁令。

关键操作与筛选已找到，不能因集合表达或缺显式循环就判遗漏。仍应留意两组字段的逐记录对应：它会影响“哪个正文到哪个接收人”的判断；现有约束有依据，尚不能断言串发或只调用一次。

- 新 DOE 优先结合筛选、字段来源和每条约束建立对应；仍无法确定时报告关联未决，不推定任意正文发送给全部接收人，也不强求 loop 或补边。
- 空集跳过的图形展开、计数口径细节降级。保留不向任何接收人发送 access_token 的全局限制，可用记录不等于实际载荷。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

