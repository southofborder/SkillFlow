# 005 conditional-notification｜面向新 DOE 的简评

样例：**N05**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/005-conditional-notification.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/005-conditional-notification.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/005-conditional-notification.png)。

核心链：读取事件，按退订、紧急和数值条件逐条筛选，将当前 summary 原值发给当前 recipient，处理完后直接返回。`ir_008 → ir_009` 保留发送载荷，`ir_011` 结束；[原文第 16 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:16)明确 count.txt 只是历史示例。

未发现已证实的关键过程缺口。此例的执行边界是必须保留的差异：实际通知仍有效，历史计数及写文件均不执行。新 DOE 不能从其他同名样例套入本地写入，也不能把历史标记扩大为整个任务不执行。

- 保留选中条件、每条接收人绑定及 access_token 全局禁令；记录可用不意味着 token 被通知消费。
- 无需为历史例子的统计口径补策略，也不因缺计数节点扣过程覆盖。字段缺失及服务失败没有明确策略，维持未知，不添加重试或生成摘要。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

