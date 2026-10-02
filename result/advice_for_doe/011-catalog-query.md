# 011 catalog-query｜面向新 DOE 的简评

样例：**Q05**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/011-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/011-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/011-catalog-query.png)。

核心链：request.json 的 term 及存在的可选参数 → 唯一 `ir_014` 搜索 → 同次响应 items 经 `ir_016/ir_017` 原值返回。[原文第 17 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:17)明确写 count.txt 是不执行的历史示例。

未发现已证实的关键过程缺口。新 DOE 需要保留该执行边界：查询和返回仍是当前动作，total 提取与本地写入不应从其他 Q 样例迁入。只看文件名或历史描述就添加副作用，会改变后续判断的过程集合。

- 用分支及 omit 约束理解可选实参，不能因 inputs 中有候选结果就判缺失时发送 null。实际载荷与可用数据分开识别。
- 日期格式检查、能力说明独立节点和返回块形式可降级。保留 index.delete 全局禁令及原值返回，不添加模糊扩展；历史计数的口径未知不属于当前 DOE 阻塞。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

