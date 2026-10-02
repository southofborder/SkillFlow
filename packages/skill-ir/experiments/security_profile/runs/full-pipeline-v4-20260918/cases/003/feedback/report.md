# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 遗漏 1；保留（模型判定） 6；内部冲突 1 | {"actionable_ids": ["finding_2", "finding_5"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_6", "finding_7", "finding_8", "finding_9"]}, "revision": 0, "semantic_items": 8, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 5 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_5", "finding_6", "finding_7"]}, "revision": 1, "semantic_items": 5, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_2 · 遗漏

原文要求：读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前回述：受控回述记录 block_001/ir_001 读取 external_resource events.json，输出 result_001/events_records；未记录“用户提供”的来源限定，也未记录每条记录的字段清单。record_id 在受控文字中完全未出现，其他字段只零散出现在后续条件/禁止约束中。

差异理由：源文把输入来源和记录模式作为显式要求；受控文本只保留文件名和读取动作，缺少来源限定与字段模式，尤其 record_id。因此该组合要求存在局部遗漏，不能标 represented。

源文：`SKILL.md:10-10`（`src_003`）。

> | 1 | input | 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。 |

受控事实：`fact:/blocks/0/instructions/0`, `fact:/blocks/0/instructions/0/inputs/0`, `fact:/blocks/0/instructions/0/outputs/0`, `fact:/blocks/0/source`

程序映射的当前图位置：`/blocks/block_001/instructions/0`, `/blocks/block_001/instructions/0/inputs/0`, `/blocks/block_001/instructions/0/outputs/0`, `/blocks/block_001/data_source_kind`

修改建议：在该读取操作的声明中补充 events.json 记录模式：每条记录包含 recipient、summary、record_id、value、urgent、opted_out、access_token；若“用户提供”属于输入来源要求，也应在相关输入/资源声明中明确记录。

依据：当前仅记录文件名和读取动作，缺少源文显式输入模式与来源限定。

当前目标事实：`fact:/blocks/0/instructions/0`

当前目标图位置：`/blocks/block_001/instructions/0`

### finding_5 · 内部冲突

原文要求：调用 notify.send。

当前回述：ir_005 的操作名(opcode)记录为 notify_send；同一操作的操作级约束文字要求调用 notify.send。

差异理由：源文明确调用对象为 notify.send；受控记录在操作身份上写作 notify_send，而约束声明又写作 notify.send。两者分属操作记录与约束声明，当前图未给出二者同一调用的映射，形成声明—操作冲突；约束文字不能替代操作身份。

源文：`SKILL.md:13-13`（`src_003`）。

> | 4 | send | 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。 |

受控事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/constraints/0`

程序映射的当前图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/constraints/0`

修改建议：将操作名对齐为源文 notify.send，或显式记录 notify_send 与 notify.send 的同一调用映射。

依据：当前操作身份与源文及自身约束声明的调用名不一致。

当前目标事实：`fact:/blocks/2/instructions/0`

当前目标图位置：`/blocks/block_003/instructions/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 4 |
| `counts.audit_execution_calls` | 2 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 4 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 4 |
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

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |

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
