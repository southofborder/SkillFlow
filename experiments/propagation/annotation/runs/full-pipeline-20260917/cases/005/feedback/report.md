# CFG 构建语义反馈闭环

停止状态：**提取执行错误**（`extraction_error`）。

停止原因：LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 6；遗漏 1 | {"actionable_ids": ["finding_4"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 7, "status": "revise", "unknown_ids": []} |
| 1 | extraction_error | 无有效业务核对项 | {"reason": "LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>", "status": "extraction_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_4 · 遗漏

原文要求：每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前回述：受控图记录 event_records 输出，并提取 record_recipient、record_summary、record_value、record_urgent、record_opted_out；record_id 未出现，access_token 只在全局禁止发送约束中出现，未作为记录字段模式记录。

差异理由：源文明确列出每条记录字段集合；当前回述只保留后续使用字段，遗漏 record_id，且未把 access_token 保留为输入记录字段，仅为禁止发送约束提及，故输入对象模式不完整。

源文：`SKILL.md:8-8`（`src_003`）。

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

受控事实：`fact:/blocks/0/instructions/0/outputs/0`, `fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/2/instructions/0/outputs/1`, `fact:/blocks/2/instructions/0/outputs/2`, `fact:/blocks/2/instructions/0/outputs/3`, `fact:/blocks/2/instructions/0/outputs/4`, `fact:/constraints/0`

程序映射的当前图位置：`/blocks/block_001/instructions/0/outputs/0`, `/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_003/instructions/0/outputs/1`, `/blocks/block_003/instructions/0/outputs/2`, `/blocks/block_003/instructions/0/outputs/3`, `/blocks/block_003/instructions/0/outputs/4`, `/constraints/0`

修改建议：在 event_records 输出单元的语义标签或 metadata 中补充输入记录字段模式，至少保留 record_id 和 access_token 等源文字段；access_token 可继续只受禁止发送约束，但不应从输入模式中消失。

依据：源文明确每条记录包含这些字段；当前只提取后续使用字段，record_id 完全缺失，access_token 仅作为约束文本出现。

当前目标事实：`fact:/blocks/0/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_001/instructions/0/outputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 3 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 6 |
| `counts.http_retries` | 3 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |
| 1 | 已有图 / 未记录 | 未执行 | 未执行 |

第 1 轮执行错误：`{"message": "LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>", "type": "LlmClientError"}`。


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
