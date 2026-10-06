# 统一抽象运行时契约：三例复测

这是统一契约下的静态可能行为，不是执行日志。复用冻结源包和既有 CFG；每例一次联合标注，传播和重放零 API。完成不证明标注正确或不存在 DOE。

契约：`skillflow-abstract-runtime-v1`。

| 样例 | 调度 | 标注 | 传播 | 逻辑调用 | 审查材料 |
|---|---|---|---|---:|---|
| 001 / N01 | completed | complete | complete | 1 | [既有 CFG](cases/001/selected-analysis.json) · [联合标注](cases/001/annotation/report.md) · [DOE 原始事实](cases/001/propagation/doe-input.json) · [传播审查](cases/001/propagation/report.html) · [助手复核](cases/001/assistant-review.md) |
| 010 / Q04 | completed | execution_error | not_run | 1 | [既有 CFG](cases/010/selected-analysis.json) · [联合标注](cases/010/annotation/report.md) · [助手复核](cases/010/assistant-review.md) |
| 013 / F01 | completed | execution_error | not_run | 1 | [既有 CFG](cases/013/selected-analysis.json) · [联合标注](cases/013/annotation/report.md) · [助手复核](cases/013/assistant-review.md) |


重点核对：来源与字段是否连接；读取与模型观察是否混同；明确局部机制是否受到尊重；观察的数据版本与工具实际参数是否正确。

本次最多三次计划内逻辑模型调用；HTTP 传输尝试另计。未决、无效响应和助手发现的错误均保留，不按质量补跑。

## 工程验收与助手复核

001 完成；010、013 在 DNS 解析阶段失败，每例首次加两次传输重试均未收到响应。三例离线重放零 API，状态一致。

[查看完整工程验收和三例助手复核](assistant-review.md)。该报告分别列出模型表现、证据不足和未证明的运行事实。
