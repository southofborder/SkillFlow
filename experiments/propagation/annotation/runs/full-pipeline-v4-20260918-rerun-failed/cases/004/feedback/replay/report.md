# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 13；内部冲突 1 | {"actionable_ids": ["finding_12"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_5", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_13", "finding_14", "finding_15", "finding_16", "finding_17"]}, "revision": 0, "semantic_items": 14, "status": "revise", "unknown_ids": []} |
| 1 | revise | 保留（模型判定） 9；遗漏 2 | {"actionable_ids": ["finding_4", "finding_7"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_5", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12"]}, "revision": 1, "semantic_items": 11, "status": "revise", "unknown_ids": []} |
| 2 | audit_passed | 保留（模型判定） 11 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2_workflow_mandate", "finding_3_read_events_schema", "finding_4_filter_condition", "finding_5_payload_body_from", "finding_6_send_recipient_once", "finding_7_body_summary_original_no_rewrite", "finding_8_unselected_no_send", "finding_9_access_token_prohibition", "finding_10_write_processed_count", "finding_11_iteration_and_order", "finding_12_result_dependencies"]}, "revision": 2, "semantic_items": 11, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_12 · 内部冲突

原文要求：对每条选中记录调用一次 notify.send；处理完成后才写 count.txt。

当前回述：block_005 的约束0声明每条选中记录调用一次；但 block_004 的 get_next_selected_event 输出 result_005，其语义标签为 whether another selected event record exists；dispatch ir_008 用该结果分流，边 fact:/edges/3 在 has_next_selected_event is true 时进入 block_005，边 fact:/edges/4 在 false 时进入 block_006。按该标签，最后一条选中记录若没有另一条记录，会直接进入计数/写文件块而不调用 notify.send。

差异理由：受控图自身的声明与操作/边条件冲突：result_005 表示是否还有另一条记录，却被用作是否发送当前记录的条件；这也会使 count.txt 可能在最后一条发送前写入。

源文：`references/workflow.md:9-9`（`src_008`）。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文：`references/workflow.md:21-21`（`src_014`）。

> 处理完成后，将处理条数写入本地 count.txt。

受控事实：`fact:/blocks/4/constraints/0`, `fact:/blocks/3/instructions`, `fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/outputs/1`, `fact:/blocks/3/instructions/1`, `fact:/blocks/3/instructions/1/inputs/0`, `fact:/blocks/4/instructions/2`, `fact:/edges/3`, `fact:/edges/4`, `fact:/edges/5`

程序映射的当前图位置：`/blocks/block_005/constraints/0`, `/blocks/block_004/instructions`, `/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/outputs/1`, `/blocks/block_004/instructions/1`, `/blocks/block_004/instructions/1/inputs/0`, `/blocks/block_005/instructions/2`, `/edges/3`, `/edges/4`, `/edges/5`

修改建议：将 dispatch/边条件改为依据“当前是否有待发送的选中记录”而不是依据“是否还存在另一条选中记录”；或让循环在取得当前记录后先进入 block_005 发送，再依据 result_005 决定是否回到 block_004。同步调整 result_005 的语义/条件文字，使 has_next=false 只在没有待发送记录时进入 block_006。

依据：避免最后一条选中记录未发送且 count.txt 提前写入。

当前目标事实：`fact:/blocks/3/instructions/1/inputs/0`, `fact:/blocks/3/instructions/0/outputs/1`, `fact:/edges/3`, `fact:/edges/4`

当前目标图位置：`/blocks/block_004/instructions/1/inputs/0`, `/blocks/block_004/instructions/0/outputs/1`, `/edges/3`, `/edges/4`

### 第 1 轮

### finding_4 · 遗漏

原文要求：读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前回述：受控记录 read_events_file（fact:/blocks/0/instructions/0）以 external_resource events.json 为输入并输出 result_001，但未记录该文件由用户提供，也未记录每条记录的完整字段清单；record_id 未出现在任何受控单元。

差异理由：动作和 events.json 标识保留；来源属性“用户提供”和字段组成声明缺失，尤其 record_id 未被表示，故该组合要求未完整保留。

源文：`references/workflow.md:3-3`（`src_006`）。

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

受控事实：`fact:/blocks/0/instructions/0`, `fact:/blocks/0/instructions/0/inputs/0`, `fact:/blocks/0/instructions/0/outputs/0`, `fact:/blocks/0/source`

程序映射的当前图位置：`/blocks/block_001/instructions/0`, `/blocks/block_001/instructions/0/inputs/0`, `/blocks/block_001/instructions/0/outputs/0`, `/blocks/block_001/data_source_kind`

修改建议：在该操作级增加约束，记录 events.json 由用户提供，并列出每条记录包含 recipient、summary、record_id、value、urgent、opted_out、access_token。

依据：补齐源文明确的事件输入来源和字段组成声明。

当前目标事实：`fact:/blocks/0/instructions/0`

当前目标图位置：`/blocks/block_001/instructions/0`

### finding_7 · 遗漏

原文要求：payload.json 声明 {"body_from": "summary"}。

当前回述：受控记录读取 payload.json 的 body_from 字段（fact:/blocks/2/instructions/0/outputs/0、fact:/blocks/2/instructions/0/constraints/0），但没有记录该字段值为 "summary"，也没有嵌入该配置字面值。

差异理由：源文配置值明确为 summary；受控仅记录字段名和读取动作，缺失配置值本身，因此无法从受控事实确认 body_from 映射到 summary。

源文：`payload.json:1-3`（`src_004`）。

> "body_from": "summary"

受控事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/2/instructions/0/constraints/0`

程序映射的当前图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_003/instructions/0/constraints/0`

修改建议：补充 payload.json 的 body_from 字段值为 summary，或在读取结果上记录对应字面值/值事实。

依据：保留源文 payload.json 的明确配置值，避免只记录字段名。

当前目标事实：`fact:/blocks/2/instructions/0/constraints/0`

当前目标图位置：`/blocks/block_003/instructions/0/constraints/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 3 |
| `counts.audit_logical_calls` | 3 |
| `counts.total_logical_calls` | 6 |
| `counts.audit_execution_calls` | 3 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 6 |
| `counts.semantic_revisions` | 2 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 6 |
| `counts.http_retries` | 0 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.max_audit_execution_retries` | 2 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |
| `limits.execution_call_bounds` | {"audit": 12, "extraction": 16, "total": 28} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |
| 1 | complete / passed | passed | complete |
| 2 | complete / passed | passed | complete |

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |
| 2 | 1 | complete | 否 |

最后有效图存在：是。

核对器通过图存在：是。

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
