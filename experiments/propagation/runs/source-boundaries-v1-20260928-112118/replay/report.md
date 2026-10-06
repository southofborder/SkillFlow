# 三例来源范围、工具返回与模型观察实测

从冻结源包重新建图及有界反馈；每例只标注一次，传播和重放离线。不回退历史图，不按质量补跑。核对未通过的末次结构有效图仅用于诊断。

审查顺序：来源是什么？ → 读取范围是什么？ → 模型观察哪个版本？ → 最终取出什么？ → 实际传给谁？

核对器通过、标注记录完整及传播完成都不是语义等价或无 DOE 的证明。

| 样例 | 反馈 | 标注 | 传播 | 逻辑调用 | 审查材料 |
|---|---|---|---|---:|---|
| 001 / N01 | audit_passed | complete | execution_error | 8 | [建图与核对](../cases/001/feedback/report.md) · [实际选图与停止状态](../cases/001/selection.json) · [联合标注](../cases/001/annotation/report.md) · [助手复核](../cases/001/assistant-review.md) |
| 010 / Q04 | audit_passed | complete | complete | 3 | [建图与核对](../cases/010/feedback/report.md) · [实际选图与停止状态](../cases/010/selection.json) · [联合标注](../cases/010/annotation/report.md) · [传播审查](../cases/010/propagation/report.html) · [DOE 原始事实](../cases/010/propagation/doe-input.json) · [助手复核](../cases/010/assistant-review.md) |
| 013 / F01 | audit_passed | complete | complete | 3 | [建图与核对](../cases/013/feedback/report.md) · [实际选图与停止状态](../cases/013/selection.json) · [联合标注](../cases/013/annotation/report.md) · [传播审查](../cases/013/propagation/report.html) · [DOE 原始事实](../cases/013/propagation/doe-input.json) |

计划内逻辑调用最多 63 次，其中联合标注最多 3 次；暂态核对执行重试和 HTTP 尝试分别统计。

对照旧结果按源文动作和关系核对，不按旧 IR 编号认定同一动作。完整模型响应、证据及用量保存在各例阶段调用记录中。
