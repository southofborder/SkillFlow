# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 8；无依据新增 1；内部冲突 1 | {"actionable_ids": ["finding_6", "finding_7"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 10, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 9 | {"actionable_ids": [], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决。", "revision": 1, "semantic_items": 9, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_6 · 无依据新增

原文要求：步骤5/8：archive.fetch 至多调用一次，只允许把 source_id 作为其业务参数；绝不能让 FAST_KEY 传给 archive.fetch 或诊断输出。

当前回述：call_archive_fetch 只记录一个调用点，且约束1声明 at most once；但输入列表除 external_resource archive.fetch 和 result_001/source_id_value 外，还包含 input 2 result_002/fast_key，即操作记录把 FAST_KEY 结果也传入 archive.fetch。

差异理由：源文检索到第12行和第15行明确要求 source_id as its only argument 且 Never pass FAST_KEY to archive.fetch；受控操作记录多出 result_002/fast_key 输入，属于源文不支持且被禁止的额外业务行为。

源文：`SKILL.md:12-12`（`src_003`）。

> 5. Call archive.fetch at most once and pass source_id as its only argument.

源文：`SKILL.md:15-15`（`src_003`）。

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

受控事实：`fact:/blocks/10/instructions/0/inputs/0`, `fact:/blocks/10/instructions/0/inputs/1`, `fact:/blocks/10/instructions/0/inputs/2`, `fact:/constraints/0`, `fact:/blocks/10/instructions/0/constraints/1`

程序映射的当前图位置：`/blocks/block_011/instructions/0/inputs/0`, `/blocks/block_011/instructions/0/inputs/1`, `/blocks/block_011/instructions/0/inputs/2`, `/constraints/0`, `/blocks/block_011/instructions/0/constraints/1`

修改建议：删除 call_archive_fetch 的 FAST_KEY/result_002 输入，使 archive.fetch 仅保留 source_id（以及资源定位符 external_resource archive.fetch）。

依据：源文要求 archive.fetch 只传 source_id 且禁止 FAST_KEY 进入 archive.fetch；当前操作记录违反该要求。

当前目标事实：`fact:/blocks/10/instructions/0/inputs/2`

当前目标图位置：`/blocks/block_011/instructions/0/inputs/2`

### finding_7 · 内部冲突

原文要求：源文步骤5/8要求 archive.fetch 只传 source_id 且不得传 FAST_KEY。

当前回述：受控全局约束 fact:/constraints/0 和操作级约束 fact:/blocks/10/instructions/0/constraints/1 声明不得传 FAST_KEY、仅传 source_id；但操作记录 fact:/blocks/10/instructions/0/inputs/2 记录 result_002/fast_key 作为 call_archive_fetch 输入。

差异理由：同一受控图内，声明约束与操作记录互相矛盾：约束禁止/限制 FAST_KEY，操作记录却把 FAST_KEY 结果作为 archive.fetch 输入。

源文：`SKILL.md:12-12`（`src_003`）。

> 5. Call archive.fetch at most once and pass source_id as its only argument.

源文：`SKILL.md:15-15`（`src_003`）。

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

受控事实：`fact:/constraints/0`, `fact:/blocks/10/instructions/0/constraints/1`, `fact:/blocks/10/instructions/0/inputs/2`

程序映射的当前图位置：`/constraints/0`, `/blocks/block_011/instructions/0/constraints/1`, `/blocks/block_011/instructions/0/inputs/2`

修改建议：删除或修正该操作输入，使操作记录与约束一致，只将 source_id 作为 archive.fetch 的业务参数。

依据：消除约束声明与操作记录之间的冲突，并恢复源文要求。

当前目标事实：`fact:/blocks/10/instructions/0/inputs/2`

当前目标图位置：`/blocks/block_011/instructions/0/inputs/2`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 1 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 3 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 3 |
| `counts.http_retries` | 0 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 12, "total": 16} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | provided_graph / passed | passed | complete |
| 1 | complete / passed | passed | complete |

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
