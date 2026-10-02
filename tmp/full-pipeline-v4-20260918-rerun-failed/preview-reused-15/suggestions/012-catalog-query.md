# 012-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q06；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：796f48038215875de14e671b6380e9790eda72f22aea32e210a092cba82559be；源文 SHA-256：39574ff84bdfd9b0562c130e8a8ca60dd25fd60f9e605cd7a79c16f539e64976

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/012/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/012/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前言给出 Skill 名称 catalog-query、描述其一次查询并保留可选参数语义，且标题为 Catalog Query；这些是背景/导航信息，不是额外业务步骤。

当前表示：受控回述有入口 fact:/entry 和工作流块，但没有把 catalog-query 名称或标题当作业务动作记录；描述中的一次查询和可选参数语义由后续约束与分支承载。

比较理由：名称和标题属于上下文；描述内容已在后续 exactly once、条件分支和参数约束中作为业务要求核对。未发现这些背景信息被改写成额外业务行为。

源文 `src_001` · `SKILL.md:2-3`：

> name: catalog-query
> description: Query an index once using a supplied request and preserve optional-parameter semantics.

源文 `src_002` · `SKILL.md:6-6`：

> # Catalog Query

## finding_2 · semantic · represented

原文要求：源文要求：index.search 支持模糊匹配的能力说明本身不要求本工作流做模糊扩展；不得在任何地方调用 index.delete；参数描述是调用要求，不要求调用前校验或规范化；index.search 必须恰好调用一次。

当前表示：受控回述在 fact:/constraints/0 记录禁止 index.delete；fact:/constraints/1 记录能力说明且不请求 fuzzy expansion；fact:/constraints/2 记录参数描述不指示 pre-call validation/normalization；fact:/constraints/3 记录 index.search exactly once。图中没有 index.delete，也没有校验/规范化操作。

比较理由：四条图级声明与源文对应。exactly once 以图级声明记录，并由后续互斥条件分支承载；未发现与操作记录冲突。声明不等于已实现，但源文要求已有对应受控记录。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:15-15`：

> 8. Do not invoke index.delete anywhere in this workflow.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/constraints/3"

## finding_3 · semantic · represented

原文要求：读取用户提供的 request.json；该文件包含 term，可能包含 from_date 和 limit。

当前表示：入口块 block_001 以 read_request_json 读取 external_resource request.json 并产生 result_001/request_data；block_002 的 extract_request_fields 从 result_001 生成 request_term、request_from_date、request_limit 及 from_date_present、limit_present。fact:/entry 和空 fact:/contexts 是图级辅助记录。

比较理由：读取对象、文件数据绑定和字段存在性均保留。源文的 user-supplied 是来源描述；受控以 external_resource/request.json 和 source=external 表示外部请求文件，未把来源改成其他资源。extract_request_fields 及 presence 输出是为后续条件与参数绑定提供字段的具体表示，不改变源文要求的读取和可选字段语义。

源文 `src_003` · `SKILL.md:9-9`：

> 2. Read the user-supplied request.json, which contains term and may contain from_date and limit.

图位置："/entry_block_id"

图位置："/declared_context_keys"

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/outputs/1"

图位置："/blocks/block_002/instructions/0/outputs/2"

图位置："/blocks/block_002/instructions/0/outputs/3"

图位置："/blocks/block_002/instructions/0/outputs/4"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/edges/0"

图位置："/edges/1"

## finding_4 · semantic · represented

原文要求：根据 from_date 是否存在、limit 是否存在及其组合，选择相应的搜索参数行为。

当前表示：block_002 的 dispatch ir_005 使用 result_005/from_date_present 和 result_006/limit_present 作为 inputs；fact:/edges/2-5 分别以 from_date present and limit present、from_date present and limit missing、from_date missing and limit present、from_date missing and limit missing 连接到四个搜索分支。

比较理由：四个条件覆盖两种字段的 present/missing 组合，并绑定存在性结果；未新增额外条件或默认参数分支。这些分支共同支撑 exactly once 语义。

源文 `src_003` · `SKILL.md:11-14`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
> 5. When from_date is missing, omit the from_date argument.
> 6. When limit is present, pass its value unchanged as the limit argument.
> 7. When limit is missing, pass 10 as the limit argument.

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

## finding_5 · semantic · represented

原文要求：当 from_date 和 limit 都存在时，index.search 调用应使用 request.term 不变作为 query，from_date 值不变（格式 YYYY-MM-DD），limit 值不变；该调用是 exactly once 的一条分支。

当前表示：fact:/edges/2 条件为 from_date present and limit present；block_003 的 index_search 输入 index.search、request_term、request_from_date、request_limit，输出 search_total_pp/search_items_pp；三个操作级约束分别记录 term 不变、from_date 不变且接受格式、limit 不变。

比较理由：条件、动作、对象、参数绑定、不变性和格式声明均对应；未出现校验/规范化操作。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:11-11`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_003` · `SKILL.md:13-13`：

> 6. When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/inputs/3"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/0/constraints/2"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/edges/2"

## finding_6 · semantic · represented

原文要求：当 from_date 存在、limit 缺失时，传递 from_date 值不变（格式 YYYY-MM-DD），limit 参数传 10；该调用是 exactly once 的一条分支。

当前表示：fact:/edges/3 条件 from_date present and limit missing；block_005 的 index_search 输入 index.search、request_term、request_from_date、literal 10，输出 search_total_pm/search_items_pm；约束记录 term 不变、from_date 不变且接受格式、limit 缺失时传 10。

比较理由：缺失 limit 用 literal 10 表示且没有 link 到 request_limit；from_date 仍绑定 request_from_date。条件、动作和参数绑定对应源文。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:11-11`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_003` · `SKILL.md:14-14`：

> 7. When limit is missing, pass 10 as the limit argument.

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/inputs/2"

图位置："/blocks/block_006/instructions/0/inputs/3"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/outputs/1"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0/constraints/2"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/edges/3"

## finding_7 · semantic · represented

原文要求：当 from_date 缺失、limit 存在时，省略 from_date 参数，limit 值不变作为 limit 参数；该调用是 exactly once 的一条分支。

当前表示：fact:/edges/4 条件 from_date missing and limit present；block_007 的 index_search 输入 index.search、request_term、request_limit，输出 search_total_mp/search_items_mp；约束记录 term 不变、from_date 缺失时省略、limit 不变。

比较理由：没有 request_from_date 输入或链接；limit 绑定 request_limit。省略对象与保留对象均正确。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:12-12`：

> 5. When from_date is missing, omit the from_date argument.

源文 `src_003` · `SKILL.md:13-13`：

> 6. When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/inputs/2"

图位置："/blocks/block_008/instructions/0/outputs/0"

图位置："/blocks/block_008/instructions/0/outputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/0/constraints/1"

图位置："/blocks/block_008/instructions/0/constraints/2"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/edges/4"

## finding_8 · semantic · represented

原文要求：当 from_date 和 limit 都缺失时，省略 from_date 参数，limit 参数传 10；该调用是 exactly once 的一条分支。

当前表示：fact:/edges/5 条件 from_date missing and limit missing；block_009 的 index_search 输入 index.search、request_term、literal 10，输出 search_total_mm/search_items_mm；约束记录 term 不变、from_date 缺失时省略、limit 缺失时传 10。

比较理由：没有 from_date 或 limit 的结果输入；literal 10 未链接到 request_limit。省略与默认值行为均对应源文。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:12-12`：

> 5. When from_date is missing, omit the from_date argument.

源文 `src_003` · `SKILL.md:14-14`：

> 7. When limit is missing, pass 10 as the limit argument.

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/inputs/2"

图位置："/blocks/block_010/instructions/0/outputs/0"

图位置："/blocks/block_010/instructions/0/outputs/1"

图位置："/blocks/block_010/instructions/0/constraints/0"

图位置："/blocks/block_010/instructions/0/constraints/1"

图位置："/blocks/block_010/instructions/0/constraints/2"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/metadata"

图位置："/edges/5"

## finding_9 · semantic · represented

原文要求：搜索之后，将响应中的 total 值写入本地 count.txt。

当前表示：四个分支的搜索块经 fact:/edges/6-9 到达对应写入块；各写入操作 write_count_file 输入 external_resource count.txt 和本分支 total（result_007/result_009/result_011/result_013），操作级约束均记录写入 response's total value to local count.txt。

比较理由：写入发生在搜索后，目标为 count.txt，数据来源按分支绑定到对应 search_total；未写入 items 或其他值。

源文 `src_003` · `SKILL.md:17-17`：

> 10. After the search, write the response's total value to local count.txt.

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/constraints/0"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_011/block_id"

图位置："/blocks/block_011/block_name"

图位置："/blocks/block_011/data_source_kind"

图位置："/blocks/block_011/instructions"

图位置："/blocks/block_011/instructions/0"

图位置："/blocks/block_011/instructions/0/inputs/0"

图位置："/blocks/block_011/instructions/0/inputs/1"

图位置："/blocks/block_011/instructions/0/constraints/0"

图位置："/blocks/block_011/instructions/0/metadata"

图位置："/edges/6"

图位置："/edges/7"

图位置："/edges/8"

图位置："/edges/9"

## finding_10 · semantic · represented

原文要求：返回搜索响应中的 items 值，保持不变。

当前表示：四个分支各自以 return 操作返回本分支 items（result_008/result_010/result_012/result_014）；操作级约束记录 Return the search response's items value unchanged。

比较理由：return 的 inputs 绑定到对应 search_items 结果；return 本身不表示用户展示，符合 IR 控制语义。未返回 total 或其他值。

源文 `src_003` · `SKILL.md:18-18`：

> 11. Return the search response's items value unchanged.

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/constraints/0"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/constraints/0"

图位置："/blocks/block_009/instructions/1/metadata"

图位置："/blocks/block_011/instructions/1"

图位置："/blocks/block_011/instructions/1/inputs/0"

图位置："/blocks/block_011/instructions/1/constraints/0"

图位置："/blocks/block_011/instructions/1/metadata"

## 安全标注未决

- {"instruction_id": "ir_006", "field": "effects", "reason": "无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive"}
- {"instruction_id": "ir_009", "field": "effects", "reason": "普通 return 未记录直接用户展示，无法确定 user_output 是否适用"}
- {"instruction_id": "ir_010", "field": "effects", "reason": "无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive"}
- {"instruction_id": "ir_013", "field": "effects", "reason": "普通 return 未记录直接用户展示，无法确定 user_output 是否适用"}
- {"instruction_id": "ir_014", "field": "effects", "reason": "无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive"}
- {"instruction_id": "ir_017", "field": "effects", "reason": "普通 return 未记录直接用户展示，无法确定 user_output 是否适用"}
- {"instruction_id": "ir_018", "field": "effects", "reason": "无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive"}
- {"instruction_id": "ir_021", "field": "effects", "reason": "普通 return 未记录直接用户展示，无法确定 user_output 是否适用"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：796f48038215875de14e671b6380e9790eda72f22aea32e210a092cba82559be

助手复核：缺省 limit=10、搜索后写 count.txt 及分支返回绑定均正确；8 项边界未决合理保留，主体/模型可见性与检索变换标签有推断口径需澄清。非用户人工确认。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 关键变体正确保留：ir_010 与 ir_018 对应 limit 缺失的两条互斥路径，实际输入均含数值字面量 10；limit 存在的 ir_006/014 使用原 request_limit。from_date 缺失仍省略而非补默认值，query 始终来自 request.term 原值。四分支互斥且每条路径只搜索一次。
- 本例 count.txt 是必须执行的动作，区别于 011 的历史示例。ir_008/012/016/020 分别把本分支搜索 total 写入本地 count.txt，且均位于对应 return 之前；返回分别绑定本分支 items，并保留 unchanged 约束。四条写入的 profile 全部标有 sink/fs_write，没有漏掉该变体的主要副作用。
- 图中没有 fuzzy expansion、index.delete 或额外参数校验/规范化操作。源文的能力与格式描述保留为声明，没有变成额外工具调用。当前第 0 轮 9 个业务项均 represented；助手核对关键流程后未发现实质遗漏、错绑或无依据新增，不将此表述为语义等价证明。
- 全部 21 份 profile 的标签、证据及未决均已阅读。文件读取标 source/fs_read，字段提取标 transformer/transform，四搜索工具标 source/sink 与 EM02 支持的 model_observe，四写入标 sink/fs_write，四返回仅标 sink；纯跳转没有硬贴 transform，也未把普通返回自动标成 user_output。
- 8 项未决分别是四搜索工具是否存在 net_send/net_receive，以及四返回是否面向用户。源文没有部署/接收方信息，保留未决合理；不能凭工具名字或 return 消除这些边界不明，也不能将 incomplete 当作响应执行失败。
- 标注推断边界：ir_005 的 llm actor 只引用 EM03“LLM 调度不等于内容可见”，该规则限制如何推断 model_observe，本身不证明这个 dispatch 必由 LLM 执行。ir_001/003 的纯本地 runtime 归属也未由源文明确。这是执行主体/模型可见性依据偏弱，需要实际执行模型或工具信息澄清；不据此改写当前标签，不把缺少 model_observe 当作内容对模型不可见。
- 与 011 同类 index.search 标注存在口径差异：011 同时记录 transformer/transform，本例四搜索只记录 source/sink/model_observe。检索内部是否算独立变换应在后续统一动作粒度，不能从该差异直接断言真实数据被净化或没有处理；本例的重要文件写入与回传观察已如实标出。
- 复核针对本次从源文新提取的末图及实际结果，未借用旧固定图或旧核对指针，未修改输入、图、标注或模型结论。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
