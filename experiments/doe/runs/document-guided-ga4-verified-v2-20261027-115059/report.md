# 文档引导式分析

状态：`execution_error`；当前步骤：`processing`。

独立请求继承工作文档；最终各提交一份完整 CFG 和标注。
程序不会根据名称猜连接，也不会自动生成需求或敏感性声明。

语义修复预算已使用：True。诊断性结果：True。

结构合法、源文核对、语义审查、确定性计算分别记录，均不证明语义完整。

| 步骤 | 状态 |
|---|---|
| task | complete |
| flow | complete |
| relationships | complete |
| graph | complete |
| graph-review | complete |
| graph-repair | complete |
| graph-rereview | complete |
| processing | complete |

当前原因：ValueError: Working document references an unknown frozen file: task/task

保留的限制：

实际记录计数：`{'logical_calls': 10, 'structural_corrections': 2, 'json_normalizations': 0, 'http_attempts': None, 'http_retries': None, 'known_token_usage': {}, 'returned_models': [], 'chains_with_unknown_usage': 8}`。
本页不使用字符数推算 tokens；调用用量与耗时见各请求收据。
