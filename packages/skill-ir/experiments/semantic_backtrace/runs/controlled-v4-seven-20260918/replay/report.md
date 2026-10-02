# 受控语义回述与完整源文核对

运行：`controlled-v4-seven-20260918`；模式：`replay`。

解释契约：`skill-ir-semantic-contract-v2`，SHA-256 `bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

唯一模型任务是比较完整原文与受控文本。转换检查、模型判断与外置评测分别报告。

## 差异与未决项

以下保留模型原始有效判定；context 项仅记录非业务上下文，不计为业务语义保留。

### c01 · F01 第 1 轮及其固定变体

执行状态：execution_error

LLM SSE network failure: [WinError 5] 拒绝访问。: 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\semantic_backtrace\\runs\\controlled-v4-seven-20260918\\calls\\c01\\a001\\.transport.json.6d82df100f22439aadf3f6293131e718.tmp' -> 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\semantic_backtrace\\runs\\controlled-v4-seven-20260918\\calls\\c01\\a001\\transport.json'

### c02 · F01 第 1 轮及其固定变体

保留（模型判定） 6；内部冲突 1

保留项 6 项，其中明确填写保守说明 0 项。未填写保守说明不代表精确表示。

逐项修改建议：[suggestions/c02.md](suggestions/c02.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_5 / 内部冲突 | 步骤4、5、8要求：非 transient 第一次失败或任何 fast.fetch 重试失败后，用 source_id 调用 archive.fetch；archive.fetch 最多调用一次且 source_id 是其唯一参数；不得在本流程任何地方把 FAST_KEY 传给 archive.fetch 或诊断输出。<br>block_011 的 call_archive_fetch 记录输入 external_resource archive.fetch、result_001 source_id_value、result_002 fast_key；其操作级约束声明 'Call archive.fetch at most once and pass source_id as its only argument'，图级约束 fact:/constraints/0 声明 'Never pass FAST_KEY to archive.fetch...'。 | 受控图自身声明只传 source_id 且永不传 FAST_KEY，但同一操作的 inputs/2 绑定了 result_002 FAST_KEY，且该绑定还通过 fact:/blocks/10/instructions/0/inputs/2:link 指向 FAST_KEY 定义。这与源文步骤5/8以及受控约束均冲突；最多调用一次的结构和 source_id 输入存在，但唯一实参要求被额外 FAST_KEY 破坏。 | fact:/constraints/0, fact:/blocks/10/key, fact:/blocks/10/id, fact:/blocks/10/name, fact:/blocks/10/source, fact:/blocks/10/instructions, fact:/blocks/10/instructions/0, fact:/blocks/10/instructions/0/inputs/0, fact:/blocks/10/instructions/0/inputs/1, fact:/blocks/10/instructions/0/inputs/2, fact:/blocks/10/instructions/0/outputs/0, fact:/blocks/10/instructions/0/outputs/1, fact:/blocks/10/instructions/0/constraints/0, fact:/blocks/10/instructions/0/constraints/1, fact:/blocks/10/instructions/0/constraints/2, fact:/blocks/10/instructions/0/metadata_json, fact:/blocks/10/instructions/1, fact:/blocks/10/instructions/1/metadata_json, fact:/blocks/10/instructions/0/inputs/1:link, fact:/blocks/10/instructions/0/inputs/2:link |

### c03 · F01 第 1 轮及其固定变体

执行状态：execution_error

LLM SSE network failure: [WinError 5] 拒绝访问。: 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\semantic_backtrace\\runs\\controlled-v4-seven-20260918\\calls\\c03\\a001\\.transport.json.f219e2d3890c45c9818527f35a505660.tmp' -> 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\semantic_backtrace\\runs\\controlled-v4-seven-20260918\\calls\\c03\\a001\\transport.json'

### c04 · F01 第 1 轮及其固定变体

保留（模型判定） 8；错转 1

保留项 8 项，其中明确填写保守说明 0 项。未填写保守说明不代表精确表示。

逐项修改建议：[suggestions/c04.md](suggestions/c04.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_7 / 错转 | On either tool's success, return that successful response's body value unchanged. For retry fast.fetch success, the successful response is the retry's response body.<br>block_010 在 retry fast.fetch 成功后 append success，但 return 输入是 result_004 fast_fetch_response_body（首次 fast.fetch 的响应 body），而不是 result_008 retry_fast_fetch_response_body；对应 link /blocks/9/instructions/1/inputs/0:link 也指向 /blocks/3/instructions/0/outputs/0。该块名称同样写成返回首次 fast.fetch 响应 body。 | 首次尝试与重试的结果身份不能互换。源文要求返回成功的那次响应 body，重试成功时应返回 result_008。当前记录违反该身份要求，并与图级约束 /constraints/2 的声明冲突；该路径仍以 return 终止，无后续 fetch，但返回身份错误。 | fact:/constraints/2, fact:/blocks/9/name, fact:/blocks/9/instructions/1, fact:/blocks/9/instructions/1/inputs/0, fact:/blocks/9/instructions/1/inputs/0:link, fact:/blocks/3/instructions/0/outputs/0, fact:/blocks/7/instructions/0/outputs/0 |

### c05 · F01 第 1 轮及其固定变体

执行状态：execution_error

controlled unit does not exist: fact:/blocks/5/instructions/0/outputs/0

### c06 · 暂停批次 001 第 0 轮

保留（模型判定） 6

保留项 6 项，其中明确填写保守说明 0 项。未填写保守说明不代表精确表示。

逐项修改建议：[suggestions/c06.md](suggestions/c06.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|

### c07 · 暂停批次 010 第 0 轮

保留（模型判定） 6

保留项 6 项，其中明确填写保守说明 1 项。未填写保守说明不代表精确表示。

逐项修改建议：[suggestions/c07.md](suggestions/c07.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_6 / 保留（含保守说明） | 源文要求 search 后写 response.total 到本地 count.txt，并返回 response.items 不变；后续写/返回需要从唯一 search response 取得 total/items。<br>block_006 extract_search_total_and_items 输入 result_006/007/008/009 四个候选 search response，输出 result_010 search_total、result_011 search_items；edges/5-8 将四个搜索分支汇入该块；links 将这些输入绑定到对应搜索输出。 | 四个 search response 来自互斥参数分支；受控以合流候选依赖表示实际响应，显式 extract 是访问 response.total/items 的数据绑定具体表达。按 DEP-MERGE 保守接受，不声称四个值同时传入或已实现精确选值。 | fact:/blocks/6/key, fact:/blocks/6/id, fact:/blocks/6/name, fact:/blocks/6/source, fact:/blocks/6/instructions, fact:/blocks/6/instructions/0, fact:/blocks/6/instructions/0/inputs/0, fact:/blocks/6/instructions/0/inputs/1, fact:/blocks/6/instructions/0/inputs/2, fact:/blocks/6/instructions/0/inputs/3, fact:/blocks/6/instructions/0/outputs/0, fact:/blocks/6/instructions/0/outputs/1, fact:/blocks/6/instructions/0/metadata_json, fact:/blocks/6/instructions/1, fact:/blocks/6/instructions/1/metadata_json, fact:/edges/5, fact:/edges/6, fact:/edges/7, fact:/edges/8, fact:/blocks/6/instructions/0/inputs/0:link, fact:/blocks/6/instructions/0/inputs/1:link, fact:/blocks/6/instructions/0/inputs/2:link, fact:/blocks/6/instructions/0/inputs/3:link, fact:/blocks/2/instructions/0/outputs/0, fact:/blocks/3/instructions/0/outputs/0, fact:/blocks/4/instructions/0/outputs/0, fact:/blocks/5/instructions/0/outputs/0 |

## 转换与执行记录

计划 7 次逻辑调用，已记录 7 次；状态 `completed_with_errors`。

记录执行 7 次，额外执行重试 0 次，HTTP 尝试 7 次。

请求配置：`deepseek-v4-flash` / `max`。独立上下文，无自动修复或择优。

| 输入 | 受控转换检查 | 模型执行 |
|---|---|---|
| c01 | passed | execution_error |
| c02 | passed | complete |
| c03 | passed | execution_error |
| c04 | passed | complete |
| c05 | passed | execution_error |
| c06 | passed | complete |
| c07 | passed | complete |

固定30图离线验收：启用=True；通过 30/30。

转换通过仅说明当前受控文本保留规范化图的明确记录；证明边界和逐输入证书另见 inputs 与 verification。

## 外置预期的复核候选

以下仅匹配判定类别与证据区域，不能自动认定语义命中、漏报或误报。

| 输入 | 外置预期 | 匹配状态 | 候选核对项 |
|---|---|---|---|
| c01 | baseline-gold-r01 | execution_error |  |
| c01 | baseline-gold-r02 | execution_error |  |
| c01 | baseline-gold-r03 | execution_error |  |
| c01 | baseline-gold-r04 | execution_error |  |
| c02 | archive-receives-credential | candidate_match | finding_5 |
| c03 | failure-status-append-missing | execution_error |  |
| c04 | retry-returns-first-body | candidate_match | finding_7 |
| c05 | added-two-second-wait | execution_error |  |
| c06 | 无本实验人工标准答案 | 待助手逐项复核 | — |
| c07 | 无本实验人工标准答案 | 待助手逐项复核 | — |

## 可复核材料与限制

- inputs：完整源文、原始案例图、实际受控文本、证据索引和转换检查记录；原始图不进入模型提示词。
- calls：原始提示词、响应、摘要、实际模型名和 SSE；parsed：严格核验后的结果。
- suggestions：逐案例修改建议；replay：新版离线重放结果。
- 约束仅为声明；条件文字未求值；开放操作、源码及运行成功未经证明。
- 保守依赖列出候选与精度损失，不代表候选同时发生，也不证明后续传播结论。
- 保留项是模型判定；未填写保守说明不自动意味着精确表示。
- 固定案例为开发诊断，不能支持泛化正确性或统计显著性结论。
