# CFG 构建语义反馈闭环

停止状态：**revise**（`revise`）。

停止原因：存在明确差异；按当前图和本轮证据重新完整提取，保留未决。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 5；错转 2 | {"actionable_ids": ["finding_7", "finding_8"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 7, "status": "revise", "unknown_ids": []} |
| 1 | revise | 保留（模型判定） 10；未决 1；内部冲突 3 | {"actionable_ids": ["finding_10", "finding_11", "finding_12"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 1, "semantic_items": 14, "status": "revise", "unknown_ids": ["finding_4"]} |

## 最后一轮差异、未决和修改建议

### finding_4 · 未决

原文要求：Parameter descriptions are call requirements and do not instruct pre-call validation or normalization。

当前回述：受控全局约束 fact:/constraints/2 记录该要求；同时 block_002 有 check_from_date_present、block_004 有 check_limit_present 两个存在性检查操作，未记录格式验证或归一化操作。

差异理由：这些显式操作名是 presence 检查；源文否定的是 pre-call validation/normalization，但是否把 presence 检查归入 validation 仅凭给定文本不能确定。

源文：`SKILL.md:21-21`（`src_008`）。

> Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

受控事实：`fact:/constraints/2`, `fact:/blocks/1/instructions/1`, `fact:/blocks/1/instructions/1/inputs/0`, `fact:/blocks/1/instructions/1/outputs/0`, `fact:/blocks/1/instructions/1/metadata_json`, `fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/metadata_json`

程序映射的当前图位置：`/constraints/2`, `/blocks/block_002/instructions/1`, `/blocks/block_002/instructions/1/inputs/0`, `/blocks/block_002/instructions/1/outputs/0`, `/blocks/block_002/instructions/1/metadata`, `/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/metadata`

未决原因：无法仅据受控文本判断 check_*_present 是否属于源文所否定的 pre-call validation；受控未记录值格式校验或归一化。

### finding_10 · 内部冲突

原文要求：When from_date is missing, omit the from_date argument。

当前回述：ir_012 constraints/2 声明 missing 时 omit；但 ir_012 inputs/2 仍无条件列出 result_004 request_from_date，link 将该输入绑定到 block_003 的 result_004；edge2 在 from_date missing 时绕过 block_003，故该结果可能未定义。

差异理由：约束声明的条件省略与操作记录的无条件输入不一致；按操作记录，missing 时并未真正省略 from_date 参数。

源文：`SKILL.md:16-16`（`src_006`）。

> | from_date | When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD. | When from_date is missing, omit the from_date argument. |

受控事实：`fact:/blocks/5/instructions/0/constraints/2`, `fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/2:link`, `fact:/edges/2`, `fact:/edges/1`, `fact:/blocks/5/instructions/0/constraints/1`

程序映射的当前图位置：`/blocks/block_006/instructions/0/constraints/2`, `/blocks/block_006/instructions/0/inputs/2`, `/edges/2`, `/edges/1`, `/blocks/block_006/instructions/0/constraints/1`

修改建议：将 result_004/request_from_date 改为条件输入，或仅在 from_date present 路径建立到 ir_012 的输入；missing 分支不要保留该输入引用。

依据：使操作记录与 constraints/2 的 missing-omit 声明一致。

当前目标事实：`fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/2:link`

当前目标图位置：`/blocks/block_006/instructions/0/inputs/2`

### finding_11 · 内部冲突

原文要求：When limit is missing, omit the limit argument。

当前回述：ir_012 constraints/4 声明 missing 时 omit；但 ir_012 inputs/3 仍无条件列出 result_006 request_limit，link 绑定到 block_005 的 result_006；edge5 在 limit missing 时绕过 block_005 直接到 index.search，故该结果可能未定义。

差异理由：约束声明的条件省略与操作记录的无条件输入不一致。

源文：`SKILL.md:17-17`（`src_006`）。

> | limit | When limit is present, pass its value unchanged as the limit argument. | When limit is missing, omit the limit argument. |

受控事实：`fact:/blocks/5/instructions/0/constraints/4`, `fact:/blocks/5/instructions/0/inputs/3`, `fact:/blocks/5/instructions/0/inputs/3:link`, `fact:/edges/5`, `fact:/edges/4`, `fact:/blocks/5/instructions/0/constraints/3`

程序映射的当前图位置：`/blocks/block_006/instructions/0/constraints/4`, `/blocks/block_006/instructions/0/inputs/3`, `/edges/5`, `/edges/4`, `/blocks/block_006/instructions/0/constraints/3`

修改建议：将 result_006/request_limit 改为条件输入，或仅在 limit present 路径建立到 ir_012 的输入；missing 分支不要保留该输入引用。

依据：使操作记录与 constraints/4 的 missing-omit 声明一致。

当前目标事实：`fact:/blocks/5/instructions/0/inputs/3`, `fact:/blocks/5/instructions/0/inputs/3:link`

当前目标图位置：`/blocks/block_006/instructions/0/inputs/3`

### finding_12 · 内部冲突

原文要求：After the search, write the response's total value to local count.txt。

当前回述：block_007 ir_014 从 result_007 search_response 得到 result_008 total_value；ir_015 输入 external_resource count.txt 与 result_008 total_value；其 constraints/0 声明 After the search, write the response's total value to local count.txt；edge7 保证该块在 search block_006 之后。约束声明 local，但操作输入 kind 为 external_resource。

差异理由：after-search 顺序和 total_value 身份保留；local count.txt 与 external_resource 类型声明存在内部冲突。

源文：`SKILL.md:23-23`（`src_009`）。

> After the search, write the response's total value to local count.txt.

受控事实：`fact:/blocks/6/key`, `fact:/blocks/6/id`, `fact:/blocks/6/name`, `fact:/blocks/6/source`, `fact:/blocks/6/instructions`, `fact:/blocks/6/instructions/0`, `fact:/blocks/6/instructions/0/inputs/0`, `fact:/blocks/6/instructions/0/outputs/0`, `fact:/blocks/6/instructions/0/metadata_json`, `fact:/blocks/6/instructions/1`, `fact:/blocks/6/instructions/1/inputs/0`, `fact:/blocks/6/instructions/1/inputs/1`, `fact:/blocks/6/instructions/1/constraints/0`, `fact:/blocks/6/instructions/1/metadata_json`, `fact:/edges/7`

程序映射的当前图位置：`/blocks/block_007/block_id`, `/blocks/block_007/block_name`, `/blocks/block_007/data_source_kind`, `/blocks/block_007/instructions`, `/blocks/block_007/instructions/0`, `/blocks/block_007/instructions/0/inputs/0`, `/blocks/block_007/instructions/0/outputs/0`, `/blocks/block_007/instructions/0/metadata`, `/blocks/block_007/instructions/1`, `/blocks/block_007/instructions/1/inputs/0`, `/blocks/block_007/instructions/1/inputs/1`, `/blocks/block_007/instructions/1/constraints/0`, `/blocks/block_007/instructions/1/metadata`, `/edges/7`

修改建议：将 count.txt 的输入类型改为 local file/resource，或明确 external_resource 是否等价于源文的 local count.txt。

依据：消除 constraints/0 的 local 与操作输入 external_resource 的内部冲突。

当前目标事实：`fact:/blocks/6/instructions/1/inputs/0`

当前目标图位置：`/blocks/block_007/instructions/1/inputs/0`

## 历史轮次差异

### 第 0 轮

### finding_7 · 错转

原文要求：After the search, write the response's total value to local count.txt.

当前回述：blocks/10/instructions/0 的 extract_total_from_search_response 同时接收 result_007、result_008、result_009、result_010 四个分支搜索响应结果，输出 result_011/total_value；blocks/10/instructions/1 再将该 total_value 写入 count.txt。未记录对实际执行的单个搜索响应的选择或合并。

差异理由：源文在一次搜索后要求写“该”响应的 total。受控提取操作同时消费四个分支响应身份；如果这些输入均为必需，则又与 exactly once 冲突；如果它们是替代项，则缺少选择/合并语义，未保留单一响应身份。

源文：`SKILL.md:23-23`（`src_009`）。

> After the search, write the response's total value to local count.txt.

受控事实：`fact:/blocks/10/key`, `fact:/blocks/10/id`, `fact:/blocks/10/name`, `fact:/blocks/10/source`, `fact:/blocks/10/instructions`, `fact:/blocks/10/instructions/0`, `fact:/blocks/10/instructions/0/inputs/0`, `fact:/blocks/10/instructions/0/inputs/1`, `fact:/blocks/10/instructions/0/inputs/2`, `fact:/blocks/10/instructions/0/inputs/3`, `fact:/blocks/10/instructions/0/outputs/0`, `fact:/blocks/10/instructions/0/metadata_json`, `fact:/blocks/10/instructions/1`, `fact:/blocks/10/instructions/1/inputs/0`, `fact:/blocks/10/instructions/1/inputs/1`, `fact:/blocks/10/instructions/1/constraints/0`, `fact:/blocks/10/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_011/block_id`, `/blocks/block_011/block_name`, `/blocks/block_011/data_source_kind`, `/blocks/block_011/instructions`, `/blocks/block_011/instructions/0`, `/blocks/block_011/instructions/0/inputs/0`, `/blocks/block_011/instructions/0/inputs/1`, `/blocks/block_011/instructions/0/inputs/2`, `/blocks/block_011/instructions/0/inputs/3`, `/blocks/block_011/instructions/0/outputs/0`, `/blocks/block_011/instructions/0/metadata`, `/blocks/block_011/instructions/1`, `/blocks/block_011/instructions/1/inputs/0`, `/blocks/block_011/instructions/1/inputs/1`, `/blocks/block_011/instructions/1/constraints/0`, `/blocks/block_011/instructions/1/metadata`

修改建议：将 total 提取和写入改为引用实际执行的单个 index.search 结果，或增加明确的互斥选择/合并步骤；不要用同一提取操作同时消费四个分支响应。

依据：源文只允许一次搜索，并要求写该响应的 total；四个响应输入没有保留同一结果身份。

当前目标事实：`fact:/blocks/10/instructions/0/inputs/0`, `fact:/blocks/10/instructions/0/inputs/1`, `fact:/blocks/10/instructions/0/inputs/2`, `fact:/blocks/10/instructions/0/inputs/3`, `fact:/blocks/10/instructions/1`

当前目标图位置：`/blocks/block_011/instructions/0/inputs/0`, `/blocks/block_011/instructions/0/inputs/1`, `/blocks/block_011/instructions/0/inputs/2`, `/blocks/block_011/instructions/0/inputs/3`, `/blocks/block_011/instructions/1`

### finding_8 · 错转

原文要求：Return the search response's items value unchanged.

当前回述：blocks/10/instructions/2 的 extract_items_from_search_response 同时接收 result_007、result_008、result_009、result_010 四个分支搜索响应结果，输出 result_012/response_items；blocks/10/instructions/3 返回 result_012。未记录对实际执行的单个搜索响应的选择或合并。

差异理由：源文要求原样返回“该”搜索响应的 items。受控提取操作同时消费四个分支响应身份；如果它们是替代项，则缺少选择/合并语义；如果均为必需，则与 exactly once 不符。

源文：`SKILL.md:25-25`（`src_010`）。

> Return the search response's items value unchanged.

受控事实：`fact:/blocks/10/instructions/2`, `fact:/blocks/10/instructions/2/inputs/0`, `fact:/blocks/10/instructions/2/inputs/1`, `fact:/blocks/10/instructions/2/inputs/2`, `fact:/blocks/10/instructions/2/inputs/3`, `fact:/blocks/10/instructions/2/outputs/0`, `fact:/blocks/10/instructions/2/metadata_json`, `fact:/blocks/10/instructions/3`, `fact:/blocks/10/instructions/3/inputs/0`, `fact:/blocks/10/instructions/3/constraints/0`, `fact:/blocks/10/instructions/3/metadata_json`

程序映射的当前图位置：`/blocks/block_011/instructions/2`, `/blocks/block_011/instructions/2/inputs/0`, `/blocks/block_011/instructions/2/inputs/1`, `/blocks/block_011/instructions/2/inputs/2`, `/blocks/block_011/instructions/2/inputs/3`, `/blocks/block_011/instructions/2/outputs/0`, `/blocks/block_011/instructions/2/metadata`, `/blocks/block_011/instructions/3`, `/blocks/block_011/instructions/3/inputs/0`, `/blocks/block_011/instructions/3/constraints/0`, `/blocks/block_011/instructions/3/metadata`

修改建议：将 items 提取和返回改为引用实际执行的单个 index.search 结果，或增加明确的互斥选择/合并步骤；不要在提取操作中同时消费四个分支响应。

依据：源文要求返回该搜索响应的 items 且保持不变；四个响应输入没有保留同一结果身份。

当前目标事实：`fact:/blocks/10/instructions/2/inputs/0`, `fact:/blocks/10/instructions/2/inputs/1`, `fact:/blocks/10/instructions/2/inputs/2`, `fact:/blocks/10/instructions/2/inputs/3`, `fact:/blocks/10/instructions/3/inputs/0`

当前目标图位置：`/blocks/block_011/instructions/2/inputs/0`, `/blocks/block_011/instructions/2/inputs/1`, `/blocks/block_011/instructions/2/inputs/2`, `/blocks/block_011/instructions/2/inputs/3`, `/blocks/block_011/instructions/3/inputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 4 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 4 |
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
| 1 | complete / passed | passed | complete |

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
