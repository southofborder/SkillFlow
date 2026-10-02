# 015 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F03**；所选轮次：**第 3 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/015-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/015-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/015-source-fetch-with-fallback.png)。

核心链：请求 source_id、环境 FAST_KEY → 有 key 时首次 fast `ir_007` → 仅瞬态失败进入重试 `ir_011` → 必要时 archive `ir_013`。成功返回对应 body，archive 失败返回 error，各终态先写状态。[原文表格第 14–18 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F03/SKILL.md:14)限定 archive 参数、返回和凭据禁令。

未发现已证实的关键过程缺口。本页只对应第 3 次图；新 DOE 应保留参数与调用身份、分支条件和响应归属，而不从表格行数或多次调用节点数推定实际执行次数。

- key 是 fast 的实参，archive 仅消费 source_id。后续仍可到达的环境数据不能自动加入 archive 或状态文件载荷，禁止流向的全局约束继续有效。
- 回退共享节点、状态文本格式及中间判断拆分可降级；一次重试、archive 最多一次的范围应保留。不为未知错误类型增加退避或诊断输出。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

