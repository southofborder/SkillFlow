# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：controlled unit does not exist: fact:/blocks/4/instructions/1/inputs/0

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 10；内部冲突 1 | {"actionable_ids": ["finding_6"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12"]}, "revision": 0, "semantic_items": 11, "status": "revise", "unknown_ids": []} |
| 1 | audit_error | 无有效业务核对项 | {"reason": "controlled unit does not exist: fact:/blocks/4/instructions/1/inputs/0", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_6 · 内部冲突

原文要求：from_date 缺失时省略 from_date 参数；limit 缺失时省略 limit 参数。

当前回述：constraints/2 和 constraints/4 声明 missing 时省略；edges/2、edges/5 允许 missing 分支到达同一个 index.search；但 blocks/5 instructions/0/inputs/2 和 inputs/3 固定记录 result_005 与 result_006，links 也把这两个 result 绑定到该 index.search。

差异理由：result_005 只在 from_date present 分支由 extract_from_date 定义，result_006 只在 limit present 分支由 extract_limit 定义；当 missing 分支到达 index.search 时，声明要求省略，操作输入却仍固定包含这些 result，形成声明—操作冲突，源文 missing omission 未在操作层可靠表示。

源文：`SKILL.md:16-16`（`src_006`）。

> | from_date | When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD. | When from_date is missing, omit the from_date argument. |

源文：`SKILL.md:17-17`（`src_006`）。

> | limit | When limit is present, pass its value unchanged as the limit argument. | When limit is missing, omit the limit argument. |

受控事实：`fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/constraints/2`, `fact:/blocks/5/instructions/0/constraints/4`, `fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/3`, `fact:/edges/2`, `fact:/edges/5`, `fact:/blocks/5/instructions/0/inputs/2:link`, `fact:/blocks/5/instructions/0/inputs/3:link`

程序映射的当前图位置：`/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/constraints/2`, `/blocks/block_006/instructions/0/constraints/4`, `/blocks/block_006/instructions/0/inputs/2`, `/blocks/block_006/instructions/0/inputs/3`, `/edges/2`, `/edges/5`

修改建议：协调这些现有记录：missing 分支不应把 result_005/result_006 记录为 index.search 的固定实参；present 分支传对应值，missing 分支不传，并保持单一 index.search。

依据：当前声明 missing 时省略，但操作输入和 links 固定包含仅在 present 分支定义的 result_005/result_006，导致源文缺省省略要求与操作记录不一致。

当前目标事实：`fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/3`, `fact:/blocks/5/instructions/0/constraints/2`, `fact:/blocks/5/instructions/0/constraints/4`

当前目标图位置：`/blocks/block_006/instructions/0/inputs/2`, `/blocks/block_006/instructions/0/inputs/3`, `/blocks/block_006/instructions/0/constraints/2`, `/blocks/block_006/instructions/0/constraints/4`

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
| 1 | complete / passed | passed | 未执行 |

第 1 轮执行错误：`{"message": "controlled unit does not exist: fact:/blocks/4/instructions/1/inputs/0", "type": "ResponseValidationError"}`。


### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |

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
