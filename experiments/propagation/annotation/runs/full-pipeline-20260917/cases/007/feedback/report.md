# CFG 构建语义反馈闭环

停止状态：**revise**（`revise`）。

停止原因：存在明确差异；按当前图和本轮证据重新完整提取，保留未决。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 10；错转 1；未决 1 | {"actionable_ids": ["finding_9"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 0, "semantic_items": 12, "status": "revise", "unknown_ids": ["finding_10"]} |
| 1 | revise | 保留（模型判定） 7；内部冲突 2 | {"actionable_ids": ["finding_5", "finding_6"], "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "revision": 1, "semantic_items": 9, "status": "revise", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

### finding_5 · 内部冲突

原文要求：源文要求：from_date 存在时原值传递且格式 YYYY-MM-DD；缺失时省略 from_date 参数。

当前回述：受控图在 /blocks/6/instructions/0/inputs/2 无条件记录 result_004 request_from_date 作为 index.search 输入；同时 /constraints/1 声明 present 时原值传递、/constraints/2 声明 missing 时省略；控制边允许 from_date missing 分支跳过提取并到达搜索。

差异理由：源文要求按 from_date 存在性条件包含或省略参数。操作记录的输入列表未标注条件且包含 result_004，缺失分支下该输入与 /constraints/2 的 omit 声明冲突；约束声明不能证明实际输入列表已条件化，故判内部冲突。

源文：`SKILL.md:11-12`（`src_003`）。

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
> 5. When from_date is missing, omit the from_date argument.

受控事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/inputs/0`, `fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/6/instructions/0/inputs/2`, `fact:/blocks/6/instructions/0/constraints/1`, `fact:/blocks/6/instructions/0/constraints/2`, `fact:/edges/2`, `fact:/edges/3`, `fact:/edges/4`, `fact:/blocks/2/instructions/0/inputs/0:link`, `fact:/blocks/2/instructions/1/inputs/0:link`, `fact:/blocks/3/instructions/0/inputs/0:link`, `fact:/blocks/6/instructions/0/inputs/2:link`

程序映射的当前图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/inputs/0`, `/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_007/instructions/0/inputs/2`, `/blocks/block_007/instructions/0/constraints/1`, `/blocks/block_007/instructions/0/constraints/2`, `/edges/2`, `/edges/3`, `/edges/4`

修改建议：将 result_004 输入显式标记为条件输入，仅在 from_date present 分支加入；确保 missing 分支不记录该输入，使操作记录与 omit 约束和控制边一致。

依据：消除无条件输入与缺失时省略声明的冲突。

当前目标事实：`fact:/blocks/6/instructions/0/inputs/2`, `fact:/blocks/6/instructions/0/constraints/2`

当前目标图位置：`/blocks/block_007/instructions/0/inputs/2`, `/blocks/block_007/instructions/0/constraints/2`

### finding_6 · 内部冲突

原文要求：源文要求：limit 存在时原值作为 limit 参数传递；缺失时省略 limit 参数。

当前回述：受控图在 /blocks/6/instructions/0/inputs/3 无条件记录 result_006 request_limit 作为 index.search 输入；同时 /constraints/3 声明 present 时原值传递、/constraints/4 声明 missing 时省略；控制边允许 limit missing 分支跳过提取并到达搜索。

差异理由：源文要求按 limit 存在性条件包含或省略参数。操作记录的输入列表未标注条件且包含 result_006，缺失分支下该输入与 /constraints/4 的 omit 声明冲突；约束声明不能证明实际输入列表已条件化，故判内部冲突。

源文：`SKILL.md:13-14`（`src_003`）。

> 6. When limit is present, pass its value unchanged as the limit argument.
> 7. When limit is missing, omit the limit argument.

受控事实：`fact:/blocks/4/instructions/0`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/outputs/0`, `fact:/blocks/4/instructions/1`, `fact:/blocks/4/instructions/1/inputs/0`, `fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/inputs/0`, `fact:/blocks/5/instructions/0/outputs/0`, `fact:/blocks/6/instructions/0/inputs/3`, `fact:/blocks/6/instructions/0/constraints/3`, `fact:/blocks/6/instructions/0/constraints/4`, `fact:/edges/5`, `fact:/edges/6`, `fact:/edges/7`, `fact:/blocks/4/instructions/0/inputs/0:link`, `fact:/blocks/4/instructions/1/inputs/0:link`, `fact:/blocks/5/instructions/0/inputs/0:link`, `fact:/blocks/6/instructions/0/inputs/3:link`

程序映射的当前图位置：`/blocks/block_005/instructions/0`, `/blocks/block_005/instructions/0/inputs/0`, `/blocks/block_005/instructions/0/outputs/0`, `/blocks/block_005/instructions/1`, `/blocks/block_005/instructions/1/inputs/0`, `/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/inputs/0`, `/blocks/block_006/instructions/0/outputs/0`, `/blocks/block_007/instructions/0/inputs/3`, `/blocks/block_007/instructions/0/constraints/3`, `/blocks/block_007/instructions/0/constraints/4`, `/edges/5`, `/edges/6`, `/edges/7`

修改建议：将 result_006 输入显式标记为条件输入，仅在 limit present 分支加入；确保 missing 分支不记录该输入，使操作记录与 omit 约束和控制边一致。

依据：消除无条件输入与缺失时省略声明的冲突。

当前目标事实：`fact:/blocks/6/instructions/0/inputs/3`, `fact:/blocks/6/instructions/0/constraints/4`

当前目标图位置：`/blocks/block_007/instructions/0/inputs/3`, `/blocks/block_007/instructions/0/constraints/4`

## 历史轮次差异

### 第 0 轮

### finding_9 · 错转

原文要求：源文要求说明：参数描述是调用要求，且不指示调用前校验或规范化。

当前回述：受控操作级约束 /blocks/5/instructions/0/constraints/5 写为 'Do not validate or normalize parameters before call.'

差异理由：源文是说明性/非指示性表述，受控文字改为直接禁止校验/规范化，增强了义务强度，属于错转。

源文：`SKILL.md:16-16`（`src_003`）。

> 9. Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

受控事实：`fact:/blocks/5/instructions/0/constraints/5`

程序映射的当前图位置：`/blocks/block_006/instructions/0/constraints/5`

修改建议：改为与源文一致：'Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.' 或删除该重复约束，保留图级 /constraints/2。

依据：避免将不指示误转为禁止，保持义务强度一致。

当前目标事实：`fact:/blocks/5/instructions/0/constraints/5`

当前目标图位置：`/blocks/block_006/instructions/0/constraints/5`

### finding_10 · 未决

原文要求：源文只要求 index.search 使用 request.term 作为 query，并在 from_date/limit 存在时传值、缺失时省略；未说明是否向 index.search 传入 presence flags。

当前回述：index.search 输入列表含 result_003 from_date_present、result_004 limit_present，且输入列表未区分调用参数与控制操作数。

差异理由：若 presence flags 是调用参数，则源文无依据；若仅用于决定省略条件，则可能合法。受控文字未标明其角色。

源文：`SKILL.md:10-10`（`src_003`）。

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文：`SKILL.md:11-11`（`src_003`）。

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文：`SKILL.md:12-12`（`src_003`）。

> 5. When from_date is missing, omit the from_date argument.

源文：`SKILL.md:13-13`（`src_003`）。

> 6. When limit is present, pass its value unchanged as the limit argument.

源文：`SKILL.md:14-14`（`src_003`）。

> 7. When limit is missing, omit the limit argument.

受控事实：`fact:/blocks/5/instructions/0/inputs/2`, `fact:/blocks/5/instructions/0/inputs/3`, `fact:/blocks/5/instructions/0/inputs/4`, `fact:/blocks/5/instructions/0/inputs/5`, `fact:/blocks/5/instructions/0/constraints/1`, `fact:/blocks/5/instructions/0/constraints/2`, `fact:/blocks/5/instructions/0/constraints/3`, `fact:/blocks/5/instructions/0/constraints/4`

程序映射的当前图位置：`/blocks/block_006/instructions/0/inputs/2`, `/blocks/block_006/instructions/0/inputs/3`, `/blocks/block_006/instructions/0/inputs/4`, `/blocks/block_006/instructions/0/inputs/5`, `/blocks/block_006/instructions/0/constraints/1`, `/blocks/block_006/instructions/0/constraints/2`, `/blocks/block_006/instructions/0/constraints/3`, `/blocks/block_006/instructions/0/constraints/4`

未决原因：受控文字未区分操作参数与控制操作数，无法判断 result_003/result_004 是否作为 index.search 实际调用参数传入。

修改建议：标明这些 presence flags 是控制操作数而非 index.search 业务参数；若作为参数则移除。

依据：消除源文未要求参数或条件建模不明的边界。

当前目标事实：`fact:/blocks/5/instructions/0/inputs/4`, `fact:/blocks/5/instructions/0/inputs/5`

当前目标图位置：`/blocks/block_006/instructions/0/inputs/4`, `/blocks/block_006/instructions/0/inputs/5`

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
