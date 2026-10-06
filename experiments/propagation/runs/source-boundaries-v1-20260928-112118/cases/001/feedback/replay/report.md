# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v3`；摘要：`219db2cedddcc1bcb29c2cecaadc6f520765de69a2891c8646a3a6f6f9c688dc`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 5；错转 1 | {"actionable_ids": ["finding_6"], "contract_sha256": "219db2cedddcc1bcb29c2cecaadc6f520765de69a2891c8646a3a6f6f9c688dc", "contract_version": "skill-ir-semantic-contract-v3", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_7"]}, "revision": 0, "semantic_items": 6, "status": "revise", "unknown_ids": []} |
| 1 | revise | 保留（模型判定） 7；遗漏 1 | {"actionable_ids": ["finding_3"], "contract_sha256": "219db2cedddcc1bcb29c2cecaadc6f520765de69a2891c8646a3a6f6f9c688dc", "contract_version": "skill-ir-semantic-contract-v3", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9"]}, "revision": 1, "semantic_items": 8, "status": "revise", "unknown_ids": []} |
| 2 | audit_passed | 保留（模型判定） 6 | {"actionable_ids": [], "contract_sha256": "219db2cedddcc1bcb29c2cecaadc6f520765de69a2891c8646a3a6f6f9c688dc", "contract_version": "skill-ir-semantic-contract-v3", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7"]}, "revision": 2, "semantic_items": 6, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_6 · 错转

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前回述：受控 block_004 名称为“统计处理条数”，ir_007 count_event_records 输入 result_001（event_records），输出 result_003（processed_count）；block_005 的 write_file 输入 external_resource count.txt 与 result_003，操作级约束记录“处理完成后，将处理条数写入本地 count.txt。”；result_003 的链接指向计数定义，并被用于写入。

差异理由：源第9步要求在处理完成后写入处理条数。受控的写入动作、目标 count.txt、以及发送后计数再写入的顺序均在，但计数输入绑定不同：它使用 result_001（block_001 读取的全部 event_records），而不是 result_002（selected_records）。结合源第4步“对每条选中记录调用一次 notify.send”和第6步“未选中的记录不调用 notify.send”，本流程中实际被处理并发送通知的是选中记录；当前 result_003 可能计入未选中记录，写入的 processed_count 与源的处理条数语义不一致。

源文：`SKILL.md:16-16`（`src_003`）。

> 处理完成后，将处理条数写入本地 count.txt。

受控事实：`fact:/blocks/3/key`, `fact:/blocks/3/id`, `fact:/blocks/3/name`, `fact:/blocks/3/source`, `fact:/blocks/3/instructions`, `fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/metadata_json`, `fact:/blocks/3/instructions/1`, `fact:/blocks/3/instructions/1/metadata_json`, `fact:/blocks/4/key`, `fact:/blocks/4/id`, `fact:/blocks/4/name`, `fact:/blocks/4/source`, `fact:/blocks/4/instructions`, `fact:/blocks/4/instructions/0`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/inputs/1`, `fact:/blocks/4/instructions/0/constraints/0`, `fact:/blocks/4/instructions/0/metadata_json`, `fact:/blocks/4/instructions/1`, `fact:/blocks/4/instructions/1/metadata_json`, `fact:/blocks/3/instructions/0/inputs/0:link`, `fact:/blocks/4/instructions/0/inputs/1:link`

程序映射的当前图位置：`/blocks/block_004/block_id`, `/blocks/block_004/block_name`, `/blocks/block_004/data_source_kind`, `/blocks/block_004/instructions`, `/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/metadata`, `/blocks/block_004/instructions/1`, `/blocks/block_004/instructions/1/metadata`, `/blocks/block_005/block_id`, `/blocks/block_005/block_name`, `/blocks/block_005/data_source_kind`, `/blocks/block_005/instructions`, `/blocks/block_005/instructions/0`, `/blocks/block_005/instructions/0/inputs/0`, `/blocks/block_005/instructions/0/inputs/1`, `/blocks/block_005/instructions/0/constraints/0`, `/blocks/block_005/instructions/0/metadata`, `/blocks/block_005/instructions/1`, `/blocks/block_005/instructions/1/metadata`

修改建议：将 count_event_records 的输入从 result_001/event_records 改为 result_002/selected_records，并同步更新对应结果链接，使 result_003 表示选中记录数（处理条数）而非全部读取记录数。

依据：源第9步的处理条数应落在实际被处理的选中记录上；源第6步已排除未选中记录的 notify.send。

当前目标事实：`fact:/blocks/3/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_004/instructions/0/inputs/0`

### 第 1 轮

### finding_3 · 遗漏

原文要求：源要求读取用户提供的 events.json，即来源是用户提供。

当前回述：受控只在块名称“读取用户提供的 events.json”中出现“用户提供的”；/contexts 为空，ir_001 输入为 external_resource events.json，块来源标记为 external。实际来源绑定没有记录“用户提供”这一来源。

差异理由：块名称只是标签，不能替代来源绑定；external_resource 只标识 events.json 资源，source=external 也未说明由用户提供。/contexts 为空且 ir_001 输入没有该来源上下文，因此该来源语义缺失。

源文：`SKILL.md:8-8`（`src_003`）。

> 读取用户提供的 events.json

受控事实：`fact:/contexts`, `fact:/blocks/0/name`, `fact:/blocks/0/source`, `fact:/blocks/0/instructions/0/inputs/0`

程序映射的当前图位置：`/declared_context_keys`, `/blocks/block_001/block_name`, `/blocks/block_001/data_source_kind`, `/blocks/block_001/instructions/0/inputs/0`

修改建议：在 /contexts 中记录 events.json 的用户提供来源/上下文键，或将该来源显式绑定到 ir_001 的输入；不要仅依赖块名称。

依据：当前只有块名称含“用户提供的”，而实际来源绑定为 external_resource events.json 和 source=external，无法从绑定层确认用户提供来源。

当前目标事实：`fact:/contexts`, `fact:/blocks/0/instructions/0/inputs/0`

当前目标图位置：`/declared_context_keys`, `/blocks/block_001/instructions/0/inputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 4 |
| `counts.audit_logical_calls` | 3 |
| `counts.total_logical_calls` | 7 |
| `counts.audit_execution_calls` | 3 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 7 |
| `counts.semantic_revisions` | 2 |
| `counts.structural_repairs` | 1 |
| `counts.http_attempts` | 8 |
| `counts.http_retries` | 1 |
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
