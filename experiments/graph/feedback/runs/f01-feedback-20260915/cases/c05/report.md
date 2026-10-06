# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 12；无依据新增 1 | {"actionable_ids": ["finding_8"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 13, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 11 | {"actionable_ids": [], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决。", "revision": 1, "semantic_items": 11, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_8 · 无依据新增

原文要求：源文步骤3只规定暂态首次失败时重试恰好一次，未规定任何等待或延迟；步骤4/7也未要求在 archive.fetch 前等待。

当前回述：block_007（/blocks/6）包含 ir_wait_1 opcode wait_for_seconds，输入 literal 2，并声明约束 “Wait for 2 seconds before continuing.”；该等待位于暂态检查之后、dispatch 之前，会影响暂态和非暂态分支。

差异理由：源文检索不到 wait、delay、seconds 等要求；该操作增加固定 2 秒延迟，属于源文未支持的新行为，而非条件表达的必要具体化。

源文：`SKILL.md:10-10`（`src_003`）。

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

源文：`SKILL.md:11-11`（`src_003`）。

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

受控事实：`fact:/blocks/6/instructions/1`, `fact:/blocks/6/instructions/1/inputs/0`, `fact:/blocks/6/instructions/1/constraints/0`, `fact:/blocks/6/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_007/instructions/1`, `/blocks/block_007/instructions/1/inputs/0`, `/blocks/block_007/instructions/1/constraints/0`, `/blocks/block_007/instructions/1/metadata`

修改建议：删除 wait_for_seconds 操作及其 “Wait for 2 seconds before continuing.” 约束；若确需延迟，应补充源文依据并明确只适用于哪些分支。

依据：源文未规定等待，当前等待会给暂态重试及非暂态转 archive 路径增加额外时序行为。

当前目标事实：`fact:/blocks/6/instructions/1`, `fact:/blocks/6/instructions/1/constraints/0`

当前目标图位置：`/blocks/block_007/instructions/1`, `/blocks/block_007/instructions/1/constraints/0`

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
