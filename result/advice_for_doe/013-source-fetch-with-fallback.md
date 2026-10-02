# 013 source-fetch-with-fallback｜面向新 DOE 的简评

样例：**F01**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/013-source-fetch-with-fallback.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/013-source-fetch-with-fallback.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/013-source-fetch-with-fallback.png)。

核心链：从请求读 source_id、从环境读 FAST_KEY；有 key 才调用 fast，首次瞬态失败重试一次，否则回退 archive；成功返回该响应 body，archive 失败返回其 error，各终态先追加 status.txt。`ir_007/ir_015` 使用 key，`ir_021` 的业务参数仅 source_id；[原文第 15 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md:15)禁止 key 到 archive 或诊断。

未发现已证实的关键过程缺口。新 DOE 应区分凭据门控、fast 的合法消费与 archive 的不同载荷；key 在后续仍可能可用，不代表 archive 或本地状态记录已消费它。

- 保留服务去向、瞬态条件、一次重试及每次响应归属。工具身份不算额外业务参数，成功后停止 fetch 不排除明示的状态追加。
- 日志 success/failure 的文字格式、判断拆块和未定义的 transient 细则降级。不补错误码、退避或新诊断内容，也不把静态凭据可达直接判为泄露。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

