# 008 catalog-query｜面向新 DOE 的简评

样例：**Q02**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/008-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/008-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/008-catalog-query.png)。

核心链：`ir_001/ir_003` 读取解析 request.json，term 和存在的可选字段进入 `ir_011` 搜索；同次响应的 total 经 `ir_015` 写 count.txt，items 经 `ir_016` 返回。[原文第 10–18 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:10)支撑这条查询与交付链。

未发现已证实的关键过程缺口。解析 JSON 是获取字段，不代表日期校验或内容变换。新 DOE 应识别真实调用只消费请求参数，返回和本地写入消费本次响应的不同字段，不能把整个可用请求／响应都算作每个动作的载荷。

- 缺失日期和 limit 的分支配合 omit 约束解释实参；候选输入可按条件取值，不按强制 AND 解释。
- 保留 query 原值、items 原值、先写 total 后返回，以及 index.delete 全局禁令。格式非法值策略、独立返回块和模糊能力说明的展示方式降级，不据此追加处理或阻塞 DOE。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

