# CFG 构建语义反馈闭环

停止状态：**仅剩未决，停止**（`unresolved`）。

停止原因：只剩未决项，没有可继续自动修复的明确差异。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | unresolved | 保留（模型判定） 13；未决 1 | {"actionable_ids": [], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "只剩未决项，没有可继续自动修复的明确差异。", "revision": 0, "semantic_items": 14, "status": "unresolved", "unknown_ids": ["finding_11"]} |

## 最后一轮差异、未决和修改建议

### finding_11 · 未决

原文要求：源文规定 index.search exactly once，并在搜索后使用该次响应的 total 和 items。

当前回述：block_007 的 ir_012 extract_search_total_and_items 将四个条件分支的 search_response_both/from_date/limit/none（result_006、result_007、result_008、result_009）同时列为输入，输出 result_010 search_total 与 result_011 search_items；未声明该操作是按执行分支选择、phi，还是同时聚合。

差异理由：源文只允许一次搜索并引用该次响应；受控记录四个可能响应输入到同一提取操作。条件分支互斥，但受控文字未说明该提取节点的分支选择语义，因此无法仅据受控文字裁决它是否保持单次响应身份。

源文：`references/workflow.md:7-7`（`src_008`）。

> Call index.search exactly once, using request.term unchanged as its query argument.

源文：`references/workflow.md:21-21`（`src_013`）。

> After the search, write the response's total value to local count.txt.

源文：`references/workflow.md:23-23`（`src_014`）。

> Return the search response's items value unchanged.

受控事实：`fact:/blocks/6/key`, `fact:/blocks/6/id`, `fact:/blocks/6/name`, `fact:/blocks/6/source`, `fact:/blocks/6/instructions`, `fact:/blocks/6/instructions/0`, `fact:/blocks/6/instructions/0/inputs/0`, `fact:/blocks/6/instructions/0/inputs/1`, `fact:/blocks/6/instructions/0/inputs/2`, `fact:/blocks/6/instructions/0/inputs/3`, `fact:/blocks/6/instructions/0/outputs/0`, `fact:/blocks/6/instructions/0/outputs/1`, `fact:/blocks/6/instructions/0/metadata_json`

程序映射的当前图位置：`/blocks/block_007/block_id`, `/blocks/block_007/block_name`, `/blocks/block_007/data_source_kind`, `/blocks/block_007/instructions`, `/blocks/block_007/instructions/0`, `/blocks/block_007/instructions/0/inputs/0`, `/blocks/block_007/instructions/0/inputs/1`, `/blocks/block_007/instructions/0/inputs/2`, `/blocks/block_007/instructions/0/inputs/3`, `/blocks/block_007/instructions/0/outputs/0`, `/blocks/block_007/instructions/0/outputs/1`, `/blocks/block_007/instructions/0/metadata`

未决原因：受控未说明 extract_search_total_and_items 的多输入是分支选择、phi，还是同时聚合；源文单次响应要求与四输入提取之间的语义不足以裁决。

## 历史轮次差异

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 1 |
| `counts.audit_logical_calls` | 1 |
| `counts.total_logical_calls` | 2 |
| `counts.semantic_revisions` | 0 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 2 |
| `counts.http_retries` | 0 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |

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
