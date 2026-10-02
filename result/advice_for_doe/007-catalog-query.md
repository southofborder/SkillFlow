# 007 catalog-query｜面向新 DOE 的简评

样例：**Q01**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/007-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/007-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/007-catalog-query.png)。

核心链：request.json 的 term 原值及存在的 from_date／limit → 唯一 `ir_009` 调用 index.search → 响应 total 写本地 count.txt → items 原值返回。[原文第 10–18 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:10)明确调用、参数和两个输出去向。

未发现已证实的关键过程缺口。新 DOE 应区分查询数据发往搜索服务、响应计数写本地、结果返回调用方；文件及服务标识本身不等于业务载荷。原值传递也没有引入摘要、模糊扩展或规范化。

- 可选结果虽列于 inputs，缺失分支和调用 omit 约束共同限定实际实参。按条件解释可能来源，不推定传 null，更不要求所有分支值同时存在。
- 日期格式校验、操作名称和拆块形式可降级。保留单次查询、全局禁止 index.delete 和真实 count 写入；缺失不自动涵盖无效值，避免增加源文没有的参数策略。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

