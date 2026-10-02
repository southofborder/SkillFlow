# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 9；内部冲突 1；未决 1 | {"actionable_ids": ["finding_9"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 11, "status": "revise", "unknown_ids": ["finding_13"]} |
| 1 | audit_passed | 保留（模型判定） 10 | {"actionable_ids": [], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决。", "revision": 1, "semantic_items": 10, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 历史轮次差异

### 第 0 轮

### finding_9 · 内部冲突

原文要求：步骤9：从每个成功或失败路径返回前，都要把最终状态追加到本地 status.txt。

当前回述：graph-level constraint 1 声明 Before returning from every success or failure path, append...；成功路径 block_006/block_010/block_013 有 append；但失败路径 block_014 名称虽写 Append failure status，其操作列表只有 ir_028 return，没有 append_final_status_to_status_file 操作。

差异理由：受控约束声明要求在失败返回前追加状态，但 block_014 的操作记录缺少该步骤；名称不能补造操作，因此声明与操作记录冲突，也遗漏了源文失败路径要求。

源文：`SKILL.md:16-16`（`src_003`）。

> 9. Before returning from every success or failure path, append the final status to local status.txt.

受控事实：`fact:/constraints/1`, `fact:/blocks/13/name`, `fact:/blocks/13/instructions`, `fact:/blocks/13/instructions/0`, `fact:/blocks/13/instructions/0/inputs/0`

程序映射的当前图位置：`/constraints/1`, `/blocks/block_014/block_name`, `/blocks/block_014/instructions`, `/blocks/block_014/instructions/0`, `/blocks/block_014/instructions/0/inputs/0`

修改建议：在 block_014 的 ir_028 return 之前补充 append_final_status_to_status_file 操作，输入使用 status.txt 和失败状态（例如 "failure"）。

依据：满足图级约束1和源文步骤9，使 archive.fetch 失败路径也先追加最终状态再返回错误。

当前目标事实：`fact:/blocks/13/instructions`, `fact:/blocks/13/instructions/0`

当前目标图位置：`/blocks/block_014/instructions`, `/blocks/block_014/instructions/0`

### finding_13 · 未决

原文要求：源文未显式要求名为 dispatch 的业务步骤；这些单元出现在受控操作记录中。

当前回述：受控各块末尾记录 opcode dispatch 的操作，draft 名称如 go_read_fast_key、go_check_fast_key 等；未记录其实现。

差异理由：dispatch 是开放操作名，按其文字只知为控制转移/派发；无法仅从源文和受控文字判断它是辅助控制流连接还是会引入额外业务行为。

受控事实：`fact:/blocks/0/instructions/1`, `fact:/blocks/1/instructions/1`, `fact:/blocks/2/instructions/1`, `fact:/blocks/3/instructions/1`, `fact:/blocks/4/instructions/1`, `fact:/blocks/6/instructions/1`, `fact:/blocks/7/instructions/1`, `fact:/blocks/8/instructions/1`, `fact:/blocks/10/instructions/1`, `fact:/blocks/11/instructions/1`

程序映射的当前图位置：`/blocks/block_001/instructions/1`, `/blocks/block_002/instructions/1`, `/blocks/block_003/instructions/1`, `/blocks/block_004/instructions/1`, `/blocks/block_005/instructions/1`, `/blocks/block_007/instructions/1`, `/blocks/block_008/instructions/1`, `/blocks/block_009/instructions/1`, `/blocks/block_011/instructions/1`, `/blocks/block_012/instructions/1`

未决原因：受控文字只给出开放 opcode dispatch 和草稿名称，未说明其是否只是控制流转移；源文也没有对应步骤，无法裁决其业务语义。

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
