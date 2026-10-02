# 014 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F02**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/014-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/014-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/014-source-fetch-with-fallback.png)。

核心链：请求 source_id 与环境 FAST_KEY 分别读入，按 key 存在性进入 fast 或 archive。`ir_007` 首次 fast 的瞬态失败才到 `ir_009` 重试；`ir_011` archive 只收 source_id。三个成功出口返回各自 body，失败出口返回 archive error，均先追加本地状态；[原文第 12–16 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F02/SKILL.md:12)支撑去向及禁令。

未发现已证实的关键过程缺口。新 DOE 应把三种首次结果理解为互斥条件，而非多条路径都执行；不同调用的响应不能混作同一个实际返回值。

- 保留 FAST_KEY 仅进入 fast 的载荷关系，以及不得进入 archive／诊断的继承限制。环境值可用不等于后续服务收到它。
- 相比其他 F 样例，判断块更少并非过程变少；日志字面量、服务名作为资源输入及精确错误分类可降级。不要增加 archive 重试，也不因共同回退节点就推定一次任务多次回退。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

