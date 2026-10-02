# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 6；内部冲突 2 | {"actionable_ids": ["finding_5", "finding_6"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_7", "finding_8", "finding_9"]}, "revision": 0, "semantic_items": 8, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 11 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14"]}, "revision": 1, "semantic_items": 11, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_5 · 内部冲突

原文要求：源文第11-12行要求：from_date 存在时原样传递，接受格式为 YYYY-MM-DD；from_date 缺失时省略 from_date 参数。

当前回述：受控回述在 constraints/1、constraints/2 记录了存在时原样传递、YYYY-MM-DD 格式以及缺失时省略；但 ir_003 的 inputs/2 始终列出 result_002/request_from_date，且其 link 指向 block_001 的该输出。

差异理由：声明约束与操作输入列表不一致：若 from_date 缺失，按 constraints/2 应省略该参数，但 inputs/2 仍把 result_002 记录为 index.search 的输入。不能把整项视为已保留。

源文：`SKILL.md:11-11`（`src_003`）。

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文：`SKILL.md:12-12`（`src_003`）。

> 5. When from_date is missing, omit the from_date argument.

受控事实：`fact:/blocks/1/instructions/0/constraints/1`, `fact:/blocks/1/instructions/0/constraints/2`, `fact:/blocks/1/instructions/0/inputs/2`, `fact:/blocks/1/instructions/0/inputs/2:link`, `fact:/blocks/0/instructions/0/outputs/1`

程序映射的当前图位置：`/blocks/block_002/instructions/0/constraints/1`, `/blocks/block_002/instructions/0/constraints/2`, `/blocks/block_002/instructions/0/inputs/2`, `/blocks/block_001/instructions/0/outputs/1`

修改建议：使 from_date 的操作输入记录与约束一致：缺失时不应把 result_002 记录为实际实参；若当前 IR 只能以约束表达条件省略，应明确 inputs/2 是条件候选而非无条件实参，并保持 constraints/2 的省略声明。

依据：当前 inputs/2 无条件出现，与 from_date 缺失时省略的声明冲突。

当前目标事实：`fact:/blocks/1/instructions/0/inputs/2`, `fact:/blocks/1/instructions/0/constraints/1`, `fact:/blocks/1/instructions/0/constraints/2`

当前目标图位置：`/blocks/block_002/instructions/0/inputs/2`, `/blocks/block_002/instructions/0/constraints/1`, `/blocks/block_002/instructions/0/constraints/2`

### finding_6 · 内部冲突

原文要求：源文第13-14行要求：limit 存在时原样作为 limit 参数传递；limit 缺失时省略 limit 参数。

当前回述：受控回述在 constraints/3、constraints/4 记录了存在时原样传递、缺失时省略；但 ir_003 的 inputs/3 始终列出 result_003/request_limit，且其 link 指向 block_001 的该输出。

差异理由：声明约束与操作输入列表不一致：若 limit 缺失，按 constraints/4 应省略该参数，但 inputs/3 仍把 result_003 记录为 index.search 的输入。不能把整项视为已保留。

源文：`SKILL.md:13-13`（`src_003`）。

> 6. When limit is present, pass its value unchanged as the limit argument.

源文：`SKILL.md:14-14`（`src_003`）。

> 7. When limit is missing, omit the limit argument.

受控事实：`fact:/blocks/1/instructions/0/constraints/3`, `fact:/blocks/1/instructions/0/constraints/4`, `fact:/blocks/1/instructions/0/inputs/3`, `fact:/blocks/1/instructions/0/inputs/3:link`, `fact:/blocks/0/instructions/0/outputs/2`

程序映射的当前图位置：`/blocks/block_002/instructions/0/constraints/3`, `/blocks/block_002/instructions/0/constraints/4`, `/blocks/block_002/instructions/0/inputs/3`, `/blocks/block_001/instructions/0/outputs/2`

修改建议：使 limit 的操作输入记录与约束一致：缺失时不应把 result_003 记录为实际实参；若当前 IR 只能以约束表达条件省略，应明确 inputs/3 是条件候选而非无条件实参，并保持 constraints/4 的省略声明。

依据：当前 inputs/3 无条件出现，与 limit 缺失时省略的声明冲突。

当前目标事实：`fact:/blocks/1/instructions/0/inputs/3`, `fact:/blocks/1/instructions/0/constraints/3`, `fact:/blocks/1/instructions/0/constraints/4`

当前目标图位置：`/blocks/block_002/instructions/0/inputs/3`, `/blocks/block_002/instructions/0/constraints/3`, `/blocks/block_002/instructions/0/constraints/4`

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
