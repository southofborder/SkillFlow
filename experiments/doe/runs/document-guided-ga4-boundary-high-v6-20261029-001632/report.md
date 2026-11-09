# 文档引导式分析

状态：failed；步骤：review。

正常七次分析调用；程序组装标注；两个依赖感知 worker；不调用模型监控。

| 步骤 | 状态 |
|---|---|
| assembly | partial |
| flow | complete |
| graph | complete |
| processing | complete |
| review | running |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

保留的限制：

本地调用计数：{'logical_calls': 8, 'structural_corrections': 1, 'json_normalizations': 0}
未报告问题不表示逐项通过；缺失标注不表示没有 DOE。

原因：ValueError: CLI produced no complete answer; this is not an eligible transient network retry
