# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | audit_passed | 保留（模型判定） 8 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": ["finding_9"], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9"]}, "revision": 0, "semantic_items": 8, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

### finding_9 · 保留（模型判定）

保守规则：`DEP-MERGE`；候选事实：fact:/blocks/5/instructions/0/inputs/0, fact:/blocks/5/instructions/0/inputs/1, fact:/blocks/5/instructions/0/inputs/2, fact:/blocks/5/instructions/0/inputs/3

保留理由：edges/4-7 分别来自四个搜索块，block_006 的提取操作列出四个已有 result 输入；源文与图控制关系支持候选来源集合。

损失的区分：未区分 block_002→block_006 路径只应使用 result_006；未区分 block_003→block_006 路径只应使用 result_007；未区分 block_004→block_006 路径只应使用 result_008；未区分 block_005→block_006 路径只应使用 result_009

原文要求：第11条：返回 search response 的 items 值且不变；该返回发生在搜索之后，搜索响应来自实际执行的那个分支。

当前回述：block_006 ir_011 extract_items_from_search_response 输入 result_006/result_007/result_008/result_009 四个候选 search response，输出 result_010 search response items；ir_012 return 输入 result_010；约束记录返回 search response items unchanged；edges/4-7 将四个搜索块汇入 block_006。

差异理由：源文只有一个返回，控制边表明四个搜索块互斥且都可能进入返回块；提取操作列出四个已有结果作为候选来源。按 DEP-MERGE 保守接受该合流候选集合，不声称四个输入同时传入，也不声称已实现精确按路径选值。

源文：`SKILL.md:18-18`（`src_003`）。

> 11. Return the search response's items value unchanged.

受控事实：`fact:/blocks/5/key`, `fact:/blocks/5/id`, `fact:/blocks/5/name`, `fact:/blocks/5/source`, `fact:/blocks/5/instructions`, `fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/inputs/0`, `fact:/blocks/5/instructions/0/inputs/1`, `fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/3`, `fact:/blocks/5/instructions/0/outputs/0`, `fact:/blocks/5/instructions/1`, `fact:/blocks/5/instructions/1/inputs/0`, `fact:/blocks/5/instructions/1/constraints/0`, `fact:/edges/4`, `fact:/edges/5`, `fact:/edges/6`, `fact:/edges/7`, `fact:/blocks/5/instructions/0/inputs/0:link`, `fact:/blocks/5/instructions/0/inputs/1:link`, `fact:/blocks/5/instructions/0/inputs/2:link`, `fact:/blocks/5/instructions/0/inputs/3:link`, `fact:/blocks/5/instructions/1/inputs/0:link`

程序映射的当前图位置：`/blocks/block_006/block_id`, `/blocks/block_006/block_name`, `/blocks/block_006/data_source_kind`, `/blocks/block_006/instructions`, `/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/inputs/0`, `/blocks/block_006/instructions/0/inputs/1`, `/blocks/block_006/instructions/0/inputs/2`, `/blocks/block_006/instructions/0/inputs/3`, `/blocks/block_006/instructions/0/outputs/0`, `/blocks/block_006/instructions/1`, `/blocks/block_006/instructions/1/inputs/0`, `/blocks/block_006/instructions/1/constraints/0`, `/edges/4`, `/edges/5`, `/edges/6`, `/edges/7`

## 历史轮次差异

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 1 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 2 |
| `counts.audit_execution_calls` | 1 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 2 |
| `counts.semantic_revisions` | 0 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 2 |
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

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |

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
