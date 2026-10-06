# CFG 构建语义反馈闭环

停止状态：**提取执行错误**（`extraction_error`）。

停止原因：IncompleteRead(0 bytes read)

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 错转 1；保留（模型判定） 14 | {"actionable_ids": ["finding_1"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14", "finding_15"]}, "revision": 0, "semantic_items": 15, "status": "revise", "unknown_ids": []} |
| 1 | extraction_error | 无有效业务核对项 | {"reason": "IncompleteRead(0 bytes read)", "status": "extraction_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_1 · 错转

原文要求：Read FAST_KEY from the environment.

当前回述：受控图在 block_002 的 opcode/名称中写 read_fast_key_from_environment，但 /contexts 将 FAST_KEY 声明为上下文键，block_002 的数据来源标记为 context，输入 kind 为 context_key；未把 environment 作为实际来源记录。

差异理由：源文明确 FAST_KEY 来自 environment。受控记录虽保留 environment 字样，但数据来源标记、上下文声明和操作数种类均指向 context/context_key，二者不一致；动作名不能替代来源绑定，故该项未正确保留。

源文：`SKILL.md:8-8`（`src_003`）。

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

受控事实：`fact:/contexts`, `fact:/blocks/1/name`, `fact:/blocks/1/source`, `fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`, `fact:/blocks/1/instructions/0/outputs/0`

程序映射的当前图位置：`/declared_context_keys`, `/blocks/block_002/block_name`, `/blocks/block_002/data_source_kind`, `/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`, `/blocks/block_002/instructions/0/outputs/0`

修改建议：将 FAST_KEY 的来源表示改为与 'from the environment' 一致；移除或修正 /contexts 中把 FAST_KEY 作为上下文键的声明，并将 block_002 的数据来源/输入种类记录为 environment 对应的来源表示，而不是 context/context_key。

依据：源文只支持 FAST_KEY 来自 environment，不支持 context/context_key 来源。

当前目标事实：`fact:/contexts`, `fact:/blocks/1/source`, `fact:/blocks/1/instructions/0/inputs/0`

当前目标图位置：`/declared_context_keys`, `/blocks/block_002/data_source_kind`, `/blocks/block_002/instructions/0/inputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 3 |
| `counts.audit_execution_calls` | 1 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 3 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 3 |
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
| 1 | 已有图 / 未记录 | 未执行 | 未执行 |

第 1 轮执行错误：`{"message": "IncompleteRead(0 bytes read)", "type": "IncompleteRead"}`。


### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |

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
