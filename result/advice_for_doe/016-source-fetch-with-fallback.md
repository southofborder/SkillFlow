# 016 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F04**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/016-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/016-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/016-source-fetch-with-fallback.png)。

核心链：主文件纳入 workflow 与固定 retry.yaml，分别读请求标识和环境凭据；fast 的 `ir_005/ir_007` 仅在有 key、首次瞬态失败条件下执行，archive `ir_009` 只传 source_id。成功返回 body、回退失败返回 error，终态追加 status.txt；[workflow 第 19 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F04/references/workflow.md:19)禁止凭据流向 archive／诊断。

未发现已证实的关键过程缺口。新 DOE 应把 [retry.yaml](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F04/retry.yaml:1)作为本次采用的重试规则；不因包内存在配置就推定额外加载、传输或另一服务调用。

- 保留 fast 最多两次、archive 最多一次及两种服务的不同载荷；凭据可用与实际被调用消费分开判断。
- 配置是否独立成节点、日志状态文字及命名条件的实现细节降级。约束可以从现有层级继承，不强求重复编码，更不把明确只适用于 fast 的重试扩展给 archive。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

