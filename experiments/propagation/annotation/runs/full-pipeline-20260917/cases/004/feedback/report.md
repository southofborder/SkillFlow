# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 12；遗漏 2 | {"actionable_ids": ["finding_5", "finding_10"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 14, "status": "revise", "unknown_ids": []} |
| 1 | audit_error | 无有效业务核对项 | {"reason": "LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_5 · 遗漏

原文要求：events.json 中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前回述：受控回述未把该字段清单作为读取结果的记录模式记录；recipient/summary/opted_out/urgent/value/access_token 只在后续约束中零散出现，record_id 未在任何受控单元出现。

差异理由：源文明确每条记录包含 record_id 等字段，但 result_001/event_records 未保留完整字段模式，无法核对记录字段身份。

源文：`references/workflow.md:3-3`（`src_006`）。

> 其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

受控事实：`fact:/blocks/0/instructions/0/outputs/0`, `fact:/blocks/0/instructions/0`

程序映射的当前图位置：`/blocks/block_001/instructions/0/outputs/0`, `/blocks/block_001/instructions/0`

修改建议：在 result_001/event_records 的输出元数据或关联记录中补充每条记录的字段清单，至少包含 record_id，并保留 recipient、summary、value、urgent、opted_out、access_token 字段身份。

依据：源文明确 events.json 每条记录包含这些字段，当前回述缺少完整模式且完全未出现 record_id。

当前目标事实：`fact:/blocks/0/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_001/instructions/0/outputs/0`

### finding_10 · 遗漏

原文要求：payload.json 内容声明 body_from 为 summary。

当前回述：受控回述记录读取 payload.json 并输出 body_from_field，且 constraints/2 指向 payload.json 的 body_from 字段；但没有保留 payload.json 的实际内容或 body_from=summary 的值。

差异理由：源数据文件中的 body_from 值未出现在受控单元中，result_004/body_from_field 的实际值无法核对；constraint/1 提到 summary 但未绑定为该 payload 字段值。

源文：`payload.json:2-2`（`src_004`）。

> "body_from": "summary"

受控事实：`fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/constraints/2`

程序映射的当前图位置：`/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/constraints/2`

修改建议：补充 payload.json 的实际内容/嵌入值，至少记录 body_from=summary，使读取输入和 result_004/body_from_field 的值身份可核对。

依据：源文 payload.json 的实际值决定 body_from 配置，当前受控回述未保留该值。

当前目标事实：`fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/outputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 3 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 5 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 1 |
| `counts.http_attempts` | 7 |
| `counts.http_retries` | 2 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |
| 1 | complete / passed | passed | 未执行 |

第 1 轮执行错误：`{"message": "LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>", "type": "LlmClientError"}`。


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
