# 文档引导式分析

状态：cannot_assess；步骤：revision/review。

正常八次分析调用；两个依赖感知 worker；不调用模型监控。

| 步骤 | 状态 |
|---|---|
| annotation | cannot_assess |
| flow | complete |
| graph | complete |
| processing | complete |
| review | complete |
| revision-annotation | structural_failure |
| revision-graph | complete |
| revision-processing | complete |
| revision-sensitivity | complete |
| revision-task-correspondence | complete |
| revision/review | complete |
| revision/task | complete |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

保留的限制：
- The shared repair did not form a complete annotation; partial materials remain unselected.
- annotation: Structural correction limit reached (1); the stage has no accepted response.
- Unified source review is partial or retains material issues.

本地调用计数：{'logical_calls': 18, 'structural_corrections': 3, 'json_normalizations': 0}
未报告问题不表示逐项通过；缺失标注不表示没有 DOE。

原因：No complete annotation is available; partial source review is retained
