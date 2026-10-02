# 011-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q05；运行：full-pipeline-v4-20260918；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：225d1248a792c18d51ded4987b7a8a85494a04290d5c6667c85d2014772add55；源文 SHA-256：227f984e8784bbb490958bab1b833743ef5488be9199988891e5c12502d75a24

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/011/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/011/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前言与标题提供 Skill 名称 catalog-query、标题 Catalog Query 和 description 背景；这些是上下文，不是业务步骤。

当前表示：受控回述只记录入口 fact:/entry=/entry 与空上下文列表 fact:/contexts，没有把名称、标题或 description 记录成操作或参数。

比较理由：源文这部分是元数据/标题上下文；受控未将其误实现为业务行为，也不需要从中生成业务要求。

源文 `src_001` · `SKILL.md:1-4`：

> ---
> name: catalog-query
> description: Query an index once using a supplied request and preserve optional-parameter semantics.
> ---

源文 `src_002` · `SKILL.md:6-6`：

> # Catalog Query

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2 · semantic · represented

原文要求：第1条说明 index.search 支持 fuzzy matching，但本工作流不要求 fuzzy expansion；第3条要求只调用 index.search 一次并把 request.term 原值用作 query；第8条禁止在本工作流调用 index.delete；第9条说明参数说明是调用要求，不要求调用前校验或规范化。

当前表示：fact:/constraints/0 记录 fuzzy 能力说明及其不触发 fuzzy expansion；fact:/constraints/1 记录 exactly once 和 request.term unchanged as query；fact:/constraints/2 记录不得调用 index.delete；fact:/constraints/3 记录参数说明不指示 pre-call validation/normalization。图中没有 index.delete、校验或规范化操作。

比较理由：四条声明分别对应四项源约束；禁止和未要求事项没有被错误实现为操作。

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

原文要求：第2条：读取用户提供的 request.json；其中包含 term，并可能包含 from_date 和 limit。

当前表示：fact:/blocks/0 记录 block_001/source external；操作 ir_001 read_user_supplied_request_json 的输入是 external_resource request.json，输出 result_001 request.term、result_002 request.from_date、result_003 request.limit、result_004 whether from_date is present、result_005 whether limit is present。block 名称为 'Read the user-supplied request.json'。

比较理由：读取对象、term 来源以及两个可选字段的候选值/存在性均被记录；from_date/limit 只在存在性分支中后续使用，未把它们无条件当作已提供参数。存在性结果是条件表达所需的辅助表示，不新增外部业务步骤。

源文 `src_003` · `SKILL.md:9-9`：

> 2. Read the user-supplied request.json, which contains term and may contain from_date and limit.

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/outputs/1"

图位置："/blocks/block_001/instructions/0/outputs/2"

图位置："/blocks/block_001/instructions/0/outputs/3"

图位置："/blocks/block_001/instructions/0/outputs/4"

## finding_4 · semantic · represented

原文要求：第4-7条要求按 from_date 与 limit 是否存在分别传值或省略，因此需要按两个存在性结果分派到四种情形。

当前表示：ir_002 dispatch 输入 result_004 与 result_005；edges/0-3 从 block_001 分别到 block_002 'from_date present and limit present'、block_003 'from_date present and limit missing'、block_004 'from_date missing and limit present'、block_005 'from_date missing and limit missing'。两个 link 将 result_004/005 绑定回其定义位置。

比较理由：四种条件恰好覆盖两个布尔存在性的所有组合且互斥；dispatch 使用存在性结果选择后继。因此四个搜索块是互斥备选，不会表示连续四次调用。

源文 `src_003` · `SKILL.md:11-11`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_003` · `SKILL.md:12-12`：

> 5. When from_date is missing, omit the from_date argument.

源文 `src_003` · `SKILL.md:13-13`：

> 6. When limit is present, pass its value unchanged as the limit argument.

源文 `src_003` · `SKILL.md:14-14`：

> 7. When limit is missing, omit the limit argument.

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/inputs/0"

图位置："/blocks/block_001/instructions/1/inputs/1"

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

## finding_5 · semantic · represented

原文要求：第3、4、6条在 from_date 与 limit 均存在时：调用 index.search 一次，query=request.term 原值，from_date 原值传入且接受格式 YYYY-MM-DD，limit 原值作为 limit 参数传入。

当前表示：block_002 记录 ir_003 index.search；inputs/0 工具 index.search，inputs/1 result_001(query)，inputs/2 result_002(from_date)，inputs/3 result_003(limit)；输出 result_006 search response；操作约束记录 from_date present 原值传递/格式 YYYY-MM-DD 与 limit present 原值传入；ir_004 dispatch 无输入/输出。links 确认 result_001/002/003 的来源。

比较理由：该块是 edges/0 的互斥分支，只在此组合下执行。动作、对象、数据绑定、存在条件、参数传递和作用域均匹配；未记录校验或规范化步骤。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:11-11`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_003` · `SKILL.md:13-13`：

> 6. When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/inputs/2"

图位置："/blocks/block_002/instructions/0/inputs/3"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/constraints/1"

图位置："/blocks/block_002/instructions/1"

## finding_6 · semantic · represented

原文要求：第3、4、7条在 from_date 存在且 limit 缺失时：调用 index.search 一次，query=request.term 原值，from_date 原值传入且接受格式 YYYY-MM-DD，省略 limit 参数。

当前表示：block_003 ir_005 index.search 输入 index.search 工具、result_001 query、result_002 from_date，省略 limit；输出 result_007 search response；操作约束记录 from_date present 原值/格式与 limit missing 时省略 limit；ir_006 dispatch。links 确认 query/from_date 来源。

比较理由：该块是 edges/1 的互斥分支，条件 from_date present and limit missing；绑定、省略和约束匹配。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:11-11`：

> 4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_003` · `SKILL.md:14-14`：

> 7. When limit is missing, omit the limit argument.

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/inputs/2"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/1"

## finding_7 · semantic · represented

原文要求：第3、5、6条在 from_date 缺失且 limit 存在时：调用 index.search 一次，query=request.term 原值，省略 from_date 参数，limit 原值作为 limit 参数传入。

当前表示：block_004 ir_007 index.search 输入 index.search 工具、result_001 query、result_003 limit，省略 from_date；输出 result_008 search response；操作约束记录 from_date missing 时省略 from_date 与 limit present 原值传入；ir_008 dispatch。links 确认 query/limit 来源。

比较理由：该块是 edges/2 的互斥分支，条件 from_date missing and limit present；绑定、省略和约束匹配。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:12-12`：

> 5. When from_date is missing, omit the from_date argument.

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

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/1"

## finding_8 · semantic · represented

原文要求：第3、5、7条在 from_date 与 limit 均缺失时：调用 index.search 一次，query=request.term 原值，省略 from_date 和 limit 参数。

当前表示：block_005 ir_009 index.search 输入 index.search 工具、result_001 query；输出 result_009 search response；操作约束记录 from_date missing 时省略 from_date、limit missing 时省略 limit；ir_010 dispatch。link 确认 query 来源。

比较理由：该块是 edges/3 的互斥分支，条件 both missing；只使用 query，两个可选参数均省略；约束匹配。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:12-12`：

> 5. When from_date is missing, omit the from_date argument.

源文 `src_003` · `SKILL.md:14-14`：

> 7. When limit is missing, omit the limit argument.

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_005/instructions/1"

## finding_9 · semantic · represented

原文要求：第11条：返回 search response 的 items 值且不变；该返回发生在搜索之后，搜索响应来自实际执行的那个分支。

当前表示：block_006 ir_011 extract_items_from_search_response 输入 result_006/result_007/result_008/result_009 四个候选 search response，输出 result_010 search response items；ir_012 return 输入 result_010；约束记录返回 search response items unchanged；edges/4-7 将四个搜索块汇入 block_006。

比较理由：源文只有一个返回，控制边表明四个搜索块互斥且都可能进入返回块；提取操作列出四个已有结果作为候选来源。按 DEP-MERGE 保守接受该合流候选集合，不声称四个输入同时传入，也不声称已实现精确按路径选值。

明确保守依赖说明：{"rule_id": "DEP-MERGE", "candidate_fact_ids": ["fact:/blocks/5/instructions/0/inputs/0", "fact:/blocks/5/instructions/0/inputs/1", "fact:/blocks/5/instructions/0/inputs/2", "fact:/blocks/5/instructions/0/inputs/3"], "lost_distinctions": ["未区分 block_002→block_006 路径只应使用 result_006", "未区分 block_003→block_006 路径只应使用 result_007", "未区分 block_004→block_006 路径只应使用 result_008", "未区分 block_005→block_006 路径只应使用 result_009"], "reason": "edges/4-7 分别来自四个搜索块，block_006 的提取操作列出四个已有 result 输入；源文与图控制关系支持候选来源集合。", "graph_refs": ["/blocks/block_006/instructions/0/inputs/0", "/blocks/block_006/instructions/0/inputs/1", "/blocks/block_006/instructions/0/inputs/2", "/blocks/block_006/instructions/0/inputs/3"]}

源文 `src_003` · `SKILL.md:18-18`：

> 11. Return the search response's items value unchanged.

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

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/constraints/0"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

## finding_10 · context · represented

原文要求：第10条是历史示例，明确不在本工作流执行：搜索后不写 response.total 到本地 count.txt。

当前表示：受控回述的各块 instructions 列表中未记录 write count.txt、读取 total 或本地写入操作；终结操作是 ir_012 return result_010。

比较理由：源文将该示例限定为非执行上下文；受控未把它实现为步骤，也未引入 count.txt 或 total 的业务行为。

源文 `src_003` · `SKILL.md:17-17`：

> 10. Historical example, not executed in this workflow: After the search, write the response's total value to local count.txt.

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/constraints/0"

## finding_11 · context · represented

原文要求：源文没有 metadata 要求；受控 metadata_json 是表示辅助信息。

当前表示：列出的 12 个 metadata_json 单元均记录为空对象 {}，没有嵌入内容或执行。

比较理由：空 metadata 不构成业务要求，保留为未解释辅助字段，不影响语义核对。

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1/metadata"

## 安全标注未决

- {"instruction_id": "ir_003", "field": "effects", "reason": "无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定"}
- {"instruction_id": "ir_005", "field": "effects", "reason": "无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定"}
- {"instruction_id": "ir_007", "field": "effects", "reason": "无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定"}
- {"instruction_id": "ir_009", "field": "effects", "reason": "无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定"}
- {"instruction_id": "ir_012", "field": "effects", "reason": "普通 return 无法确定接收方是否直接为用户，user_output 不确定"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：225d1248a792c18d51ded4987b7a8a85494a04290d5c6667c85d2014772add55

助手复核：关键查询流程及历史 count.txt 排除正确，未发现实质建图差异；标注保留 5 项合理未决，另需澄清文件读取/字段提取的模型可见边界。不是用户人工确认。

- 关键流程：block_001 读取用户 request.json 并保留 term、两个可选字段及其存在性；四条互斥控制边分别进入 ir_003/005/007/009，各条路径只执行一次 index.search。query 始终绑定原始 term；from_date 与 limit 存在则原样传入、缺失则省略，没有误补默认 limit，也没有增加参数校验、规范化、模糊扩展或 index.delete。
- 历史示例边界：SKILL.md 第 17 行明确 count.txt 写入只是历史例子，不在本工作流执行。末图全部 12 条 IR 中没有写 count.txt、取 total 或其他写入步骤，12 份 profile 也没有 fs_write；核对 finding_10 以背景项检查了这一排除条件，未将例子误转为动作。
- 返回绑定：ir_011 从四个互斥搜索分支的 result_006–009 候选中提取 items，ir_012 返回 result_010，并保留 unchanged 约束。finding_9 正确显式记录 DEP-MERGE 及按路径选值的精度损失；这四个输入不能解释为同时发送四个响应，也不能据此宣称已实现精确运行时选择。
- 核对器结果与助手复核：第 0 轮 audit_passed，8 个业务项均 represented，其中 1 个保守依赖项。结合完整源文、操作与边，本次没有发现影响本例关键过程的遗漏、错绑或额外动作；这仍是助手复核，并非形式化语义等价证明或用户人工确认。
- 全部安全标注复核：12/12 条 IR 均有 profile。读取/存在性提取标为 source、transformer 与 fs_read、transform；四个搜索动作标为 tool、source/sink/transformer、transform/model_observe；纯 dispatch 的 roles/effects 为空，items 提取标 transform，普通 return 只保留 sink。没有因禁止删除、历史写入或 fuzzy 能力声明补造保护/写入行为。
- 网络与返回未决：incomplete 的 5 项分别是四个搜索动作的 net_send/net_receive 是否适用，以及 ir_012 是否直接面向用户。源文没有声明工具部署位置或返回接收方，保留这些未决是合理边界；不能仅凭 index.search 或 return 名称补齐网络/user_output 标签，也不能将未标注解读为保证没有通信或用户暴露。
- 模型观察依据与待澄清处：搜索结果的 model_observe 均引用 EM02 工具回传假设，有当前执行模型依据，而非只凭 LLM 调度。ir_001 文件读取与 ir_011 字段提取则被解释为纯本地 agent_runtime，原文/CFG并未明确它们采用本地专用实现还是把读取内容交回模型；该执行边界仍需注意，现有 profile 没有为这两个动作记录可见性未决。后续传播不能把缺少 model_observe 标签当成模型不可见保证；应结合固定执行模型或实际工具适配信息澄清，而不是无条件给每条 IR 加模型观察。
- 证据边界：逐条阅读了所有 actor、roles、effects 的证据与理由。搜索结果 model_observe 的引用是执行假设，操作执行者/本地性仍包含模型推断；真实引文通过校验不等于这些推断均已被证明。未改动原图、profile、核对结论或历史结果。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
