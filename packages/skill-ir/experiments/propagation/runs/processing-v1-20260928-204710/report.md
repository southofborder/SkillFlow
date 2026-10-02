# 字段关系与观察编译：三例复测

这是统一契约下的静态可能行为，不是执行日志。复用冻结源包和既有 CFG；每例一次联合标注，传播和重放零 API。完成不证明标注正确或不存在 DOE。

契约：`skillflow-abstract-runtime-v2`。

| 样例 | 调度 | 标注 | 传播 | 逻辑调用 | 审查材料 |
|---|---|---|---|---:|---|
| 001 / N01 | completed | complete | complete | 1 | [既有 CFG](cases/001/selected-analysis.json) · [CFG 图与动作详情](cases/001/cfg-review.md) · [联合标注](cases/001/annotation/report.md) · [原始处理段](cases/001/annotation/audit/raw-annotation.json) · [观察编译映射](cases/001/annotation/audit/compilation-map.json) · [DOE 原始事实](cases/001/propagation/doe-input.json) · [传播审查](cases/001/propagation/report.html) · [助手复核](cases/001/assistant-review.md) |
| 010 / Q04 | completed | complete | complete | 1 | [既有 CFG](cases/010/selected-analysis.json) · [CFG 图与动作详情](cases/010/cfg-review.md) · [联合标注](cases/010/annotation/report.md) · [原始处理段](cases/010/annotation/audit/raw-annotation.json) · [观察编译映射](cases/010/annotation/audit/compilation-map.json) · [DOE 原始事实](cases/010/propagation/doe-input.json) · [传播审查](cases/010/propagation/report.html) · [助手复核](cases/010/assistant-review.md) |
| 013 / F01 | completed | complete | complete | 1 | [既有 CFG](cases/013/selected-analysis.json) · [CFG 图与动作详情](cases/013/cfg-review.md) · [联合标注](cases/013/annotation/report.md) · [原始处理段](cases/013/annotation/audit/raw-annotation.json) · [观察编译映射](cases/013/annotation/audit/compilation-map.json) · [DOE 原始事实](cases/013/propagation/doe-input.json) · [传播审查](cases/013/propagation/report.html) · [助手复核](cases/013/assistant-review.md) |


重点核对：筛选是否保留成员原值；同一元素的接收者和正文是否配对；原始处理段及程序生成的观察；局部机制及观察版本是否正确。

本次最多三次计划内逻辑模型调用；HTTP 传输尝试另计。未决、无效响应和助手发现的错误均保留，不按质量补跑。

[助手总复核与残余问题](assistant-review.md) · [离线验收](verification/tests.md) · [请求与重放验证](verification/requests-and-replay.json)
