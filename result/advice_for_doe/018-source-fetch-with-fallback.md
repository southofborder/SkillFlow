# 018 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F06**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/018-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/018-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/018-source-fetch-with-fallback.png)。

核心链：请求 source_id 与环境 FAST_KEY → 条件 fast／一次瞬态重试／archive 回退 → 各成功响应的 summary 原值返回；archive 失败返回自身 error，各终态先追加本地状态。`ir_014/ir_016/ir_018` 返回不同成功来源；[原文第 13 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F06/SKILL.md:13)明确字段为 summary。

未发现已证实的关键过程缺口。新 DOE 必须保留此字段差异：它是服务响应字段，不是额外摘要生成动作，也不能沿用其他 F 样例的 body。实际返回载荷与完整可用响应应分开识别。

- 保留 fast 消费 key、archive 仅收 source_id，以及 key 禁止进入 archive／诊断的全局限制；静态可达性不证明外发。
- summary 的名字、状态 success/failure 文字及判断拆块不要求展开新处理。未定义格式和瞬态错误规则降级；真实状态追加仍有效，不能套用历史日志样例将它删除。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

