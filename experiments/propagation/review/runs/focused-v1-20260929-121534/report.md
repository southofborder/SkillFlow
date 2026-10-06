# 联合标注三任务聚焦审查：七例执行结果

七次计划内逻辑调用：6 份有效审查，1 次传输失败；无补跑、无自动修复。模型发现与助手判断分别保存。

先读 [助手综合复核](assistant-review.md)；下表保留原始模型结论。

| 案例 | 执行状态 | 模型问题 / 未决 | 助手判别 | 报告 |
|---|---|---:|---|---|
| 001-base | complete | 0 / 0 | no_confirmed_material_issue | [模型](cases/001-base/report.html) · [助手](cases/001-base/assistant-review.md) |
| 010-base | complete | 1 / 0 | partially_supported_overstated | [模型](cases/010-base/report.html) · [助手](cases/010-base/assistant-review.md) |
| 013-base | complete | 0 / 0 | no_confirmed_material_issue | [模型](cases/013-base/report.html) · [助手](cases/013-base/assistant-review.md) |
| 013-local | execution_error | 0 / 0 | execution_not_evaluable | [模型](cases/013-local/report.html) · [助手](cases/013-local/assistant-review.md) |
| 013-field | complete | 1 / 0 | confirmed_hit | [模型](cases/013-field/report.html) · [助手](cases/013-field/assistant-review.md) |
| 010-source | complete | 2 / 0 | confirmed_hit | [模型](cases/010-source/report.html) · [助手](cases/010-source/assistant-review.md) |
| 001-version | complete | 1 / 0 | confirmed_hit | [模型](cases/001-version/report.html) · [助手](cases/001-version/assistant-review.md) |

三类受控数据关系错误确认命中；另一类因传输中断没有有效结论。原始三例无零问题预设，额外发现不自动计为误报。

[原始统计](summary.json) · [外置预期](evaluation/expectations.json) · [助手评测](evaluation/assistant-assessment.json) · [零API重放](verification/replay.json)
