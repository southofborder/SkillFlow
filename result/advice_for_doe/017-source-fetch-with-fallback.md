# 017 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F05**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/017-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/017-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/017-source-fetch-with-fallback.png)。

核心链：读 source_id 与 FAST_KEY，凭据存在才尝试 fast，首次瞬态失败重试一次，缺凭据或限定失败回退 archive；三个成功出口返回对应 body，archive 失败返回 error。`ir_013–ir_016` 直接结束；[原文第 16 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F05/SKILL.md:16)将 status.txt 追加明确标为历史示例。

未发现已证实的关键过程缺口。历史状态写入不属于当前动作，新 DOE 不应套用其他 F 样例的日志去向；同时获取、回退和返回仍然实际存在，不能一并排除。

- 保留 `ir_011` archive 仅消费 source_id，以及 FAST_KEY 不得到 archive／诊断的全局限制。环境凭据可用不等于它已进入这两个去向。
- 短条件标签结合边的起点理解，首次瞬态失败与重试后的任意失败不可混同。日志格式、错误码细分和块数量降级，不增加历史副作用或新的重试策略。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

