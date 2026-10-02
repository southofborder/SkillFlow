# 012 catalog-query｜面向新 DOE 的简评

样例：**Q06**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/012-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/012-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/012-catalog-query.png)。

核心链：读取请求，已有 limit 原值与缺失时常量 10 经 `ir_014` 按条件选择，供唯一 `ir_016` 搜索；同次 total 写 count.txt，items 原值返回。[原文第 14 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:14)明确缺失 limit 传 10。

未发现已证实的关键过程缺口。该默认值会改变实际调用载荷，应作为本样例的有效语义保留，不能套用其他查询样例的 omit，也不能用 10 覆盖已有值。日期缺失仍按原有省略约束处理。

- 新 DOE 将互斥结果视为按存在性选取的可能来源；`resolve_limit_argument` 不要求两支同时执行，无需为适配判断强制新增 phi。
- 参数非法值处理、块数量及命名可降级。保留搜索、写本次 total、返回本次 items 的关系，以及全局删除禁令；默认 10 不扩大为所有“异常 limit”的修复规则。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

