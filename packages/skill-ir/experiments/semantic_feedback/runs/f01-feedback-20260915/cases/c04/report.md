# CFG 构建语义反馈闭环

停止状态：**提取执行错误**（`extraction_error`）。

停止原因：Incomplete SSE response: both [DONE] and choice finish_reason are required

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 9；错转 1 | {"actionable_ids": ["finding_8"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 10, "status": "revise", "unknown_ids": []} |
| 1 | extraction_error | 无有效业务核对项 | {"reason": "Incomplete SSE response: both [DONE] and choice finish_reason are required", "status": "extraction_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_8 · 错转

原文要求：源文第6条关于 retry 成功时返回该成功响应 body 原值的部分。

当前回述：block_010 记录 retry 成功后 append success 并 return，但 return 输入为 result_004/fast_fetch_response_body，link 也把 result_004 定义到首次 fast.fetch 的输出 /blocks/3/instructions/0/outputs/0；retry 的实际 body 是 result_008/retry_fast_fetch_response_body，定义在 /blocks/7/instructions/0/outputs/0。

差异理由：源文要求返回成功的那次调用的 body 原值。retry 成功时成功响应是 retry_fast_fetch，应返回 result_008；受控记录成 result_004，保留了首次 fast.fetch 的 body，结果身份错转，并与 global constraints/2 的成功返回声明冲突。

源文：`SKILL.md:13-13`（`src_003`）。

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

受控事实：`fact:/constraints/2`, `fact:/blocks/9/key`, `fact:/blocks/9/id`, `fact:/blocks/9/name`, `fact:/blocks/9/source`, `fact:/blocks/9/instructions`, `fact:/blocks/9/instructions/0`, `fact:/blocks/9/instructions/0/inputs/0`, `fact:/blocks/9/instructions/0/inputs/1`, `fact:/blocks/9/instructions/0/metadata_json`, `fact:/blocks/9/instructions/1`, `fact:/blocks/9/instructions/1/inputs/0`, `fact:/blocks/9/instructions/1/inputs/0:link`, `fact:/blocks/9/instructions/1/metadata_json`, `fact:/blocks/7/instructions/0/outputs/0`

程序映射的当前图位置：`/constraints/2`, `/blocks/block_010/block_id`, `/blocks/block_010/block_name`, `/blocks/block_010/data_source_kind`, `/blocks/block_010/instructions`, `/blocks/block_010/instructions/0`, `/blocks/block_010/instructions/0/inputs/0`, `/blocks/block_010/instructions/0/inputs/1`, `/blocks/block_010/instructions/0/metadata`, `/blocks/block_010/instructions/1`, `/blocks/block_010/instructions/1/inputs/0`, `/blocks/block_010/instructions/1/metadata`, `/blocks/block_008/instructions/0/outputs/0`

修改建议：将 retry 成功返回块名称改为返回 retry fast.fetch response body；把 return 输入从 result_004/fast_fetch_response_body 改为 result_008/retry_fast_fetch_response_body；把对应 link 的定义位置改为 /blocks/7/instructions/0/outputs/0。

依据：源文要求返回成功响应本身的 body 原值，retry 成功应使用 retry_fast_fetch 的输出 result_008，而不是首次 fast.fetch 的 result_004。

当前目标事实：`fact:/blocks/9/name`, `fact:/blocks/9/instructions/1/inputs/0`, `fact:/blocks/9/instructions/1/inputs/0:link`

当前目标图位置：`/blocks/block_010/block_name`, `/blocks/block_010/instructions/1/inputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 1 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 2 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 2 |
| `counts.http_retries` | 0 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 12, "total": 16} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | provided_graph / passed | passed | complete |
| 1 | 已有图 / 未记录 | 未执行 | 未执行 |

第 1 轮执行错误：`{"message": "Incomplete SSE response: both [DONE] and choice finish_reason are required", "type": "LlmClientError"}`。


最后有效图存在：是。

核对器通过图存在：否。

未通过时，最后有效图只供检查，不作为成功结果。每轮候选、CFG、结构诊断、受控文本及证书、核对响应和反馈 Prompt 与 calls 中的请求记录一同保存。

## 事后复核与信任边界

- 受控往返保持规范化 CFG 中明确记录的事实，不证明开放操作的执行行为、路径可执行性或文件写入成功。
- 核对模型每轮独立比较完整原文和当前受控文本；提取模型收到的建议是待核实依据，原文始终优先。
- 模型可能误报、漏报或在修复后假通过；本报告不会把停止状态自动转换成方法正确率。
- 重新提取会重新赋号，旧图指针不证明新图已经修好；需结合新图、新证据及完整源文复核。
- 二进制、未解释内容以及源码摘要、打印器与进程传输的工程边界见运行清单。
- 助手复核和用户人工确认是不同状态；本生成报告不冒充任何人工确认。

本次输入的具体边界：

- 核对器通过不等于已证明源文与图语义等价。
- 受控文本仅保持图中明确记录的事实。
- 二进制或不透明内容不构成已完成行为理解或运行保证；见 inputs/snapshot.json。
