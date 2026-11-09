# 文档引导式分析

状态：partial；步骤：doe。

正常七次分析调用；程序组装标注；两个依赖感知 worker；不调用模型监控。

| 步骤 | 状态 |
|---|---|
| assembly | partial |
| doe | partial |
| flow | complete |
| graph | complete |
| processing | complete |
| propagation | incomplete |
| review | complete |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

保留的限制：
- Unified source review is partial or retains material issues.
- Propagation is incomplete: incomplete
- DOE retains analysis limitations: partial

本地调用计数：{'logical_calls': 7, 'structural_corrections': 0, 'json_normalizations': 0}
未报告问题不表示逐项通过；缺失标注不表示没有 DOE。
