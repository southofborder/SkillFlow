# 009 catalog-query｜面向新 DOE 的简评

样例：**Q03**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/009-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/009-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/009-catalog-query.png)。

核心链：request.json → 提取 term 及存在的可选字段 → `ir_012` 搜索 → 同次 total 写 count.txt、items 原值返回。[原文第 12 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:12)规定一次 index.search，[第 23 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:23)规定当前有效的本地写入。

未发现已证实的关键过程缺口。external_resource 为 index、opcode 为 index.search，合起来标识同一服务方法；新 DOE 不能因二者拆写就改判去向，也不能把服务身份当成额外业务数据参数。

- 结合存在分支与调用上的 omit 约束识别真正传入的日期／limit。来源可条件选择，不要求补 phi 或把所有输入解释为同时消费。
- 工具命名、表格来源及日期格式验证细节降级。仍保留字段原值、禁止 index.delete、无模糊扩展和同次响应关系；请求缺失与值非法的差异保持未定。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

