# CFG 构建语义反馈闭环

停止状态：**仅剩未决，停止**（`unresolved`）。

停止原因：只剩未决项，没有可继续自动修复的明确差异。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | unresolved | 保留（模型判定） 7；未决 1 | {"actionable_ids": [], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "只剩未决项，没有可继续自动修复的明确差异。", "revision": 0, "semantic_items": 8, "status": "unresolved", "unknown_ids": ["finding_8"]} |

## 最后一轮差异、未决和修改建议

### finding_8 · 未决

原文要求：源文没有对应的 dispatch/return 业务要求；源文仅用编号 1 到 9 描述读取、选择、发送、禁止发送、字段处理和写入。

当前回述：受控图在 block_001 至 block_004 末尾各记录一个 opcode dispatch（draft 分别为 go_prepare_notifications、go_send_notifications、go_count_processed、go_write_count），在 block_005 末尾记录 opcode return（draft return_done）；这些操作没有源文业务约束绑定，具体效果未在受控文字中定义。

差异理由：开放操作名 dispatch/return 的实现语义未定义；源文没有对应业务要求。不能仅凭操作名或 draft 名称判定它们只是控制流/返回脚手架、合法实现细节还是新增业务动作；块间顺序在 finding_9 另行核对。

源文：`SKILL.md:8-16`（`src_003`）。

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。
> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。
> 3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。
> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。
> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。
> 6. 未选中的记录不调用 notify.send。
> 7. 整份流程禁止将 access_token 字段发送给任何接收对象。
> 8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。
> 9. 处理完成后，将处理条数写入本地 count.txt。

受控事实：`fact:/blocks/0/instructions/1`, `fact:/blocks/1/instructions/1`, `fact:/blocks/2/instructions/1`, `fact:/blocks/3/instructions/1`, `fact:/blocks/4/instructions/1`

程序映射的当前图位置：`/blocks/block_001/instructions/1`, `/blocks/block_002/instructions/1`, `/blocks/block_003/instructions/1`, `/blocks/block_004/instructions/1`, `/blocks/block_005/instructions/1`

未决原因：受控文字未定义 dispatch/return 的实际效果，源文也未给出对应要求；因此无法裁决其是否构成额外业务行为。

## 历史轮次差异

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 1 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 2 |
| `counts.semantic_revisions` | 0 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 3 |
| `counts.http_retries` | 1 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |

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
