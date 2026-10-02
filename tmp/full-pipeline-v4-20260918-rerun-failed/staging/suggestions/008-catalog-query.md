# 008-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q02；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：7a64bbb8b1014c15edf7dbc59e7e5ca0bd4fa20a2c2d9039ee6dabe6016724bf；源文 SHA-256：d96ebca9513a94331237527adb4ed3a0c55f032f11c71b4d8682f8ccdb305d04

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/008/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/008/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前言的 skill 名称 catalog-query、描述 Query an index once using a supplied request and preserve optional-parameter semantics. 以及标题 Catalog Query；这些属于标识/背景，不是独立业务步骤。

当前表示：受控回述以 entry/contexts 等图辅助字段承载入口和上下文，没有把 frontmatter 或标题记录为独立操作；描述中的查询一次与保留可选参数语义在后续约束与操作中展开。

比较理由：按 REVIEW-MODALITY 和表示辅助信息规则，名称、标题、描述是上下文；未把其补造成业务步骤。

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

原文要求：读取用户提供的 request.json；其中包含 term，且可能包含 from_date 和 limit。

当前表示：block_001 记录名称为 Read the user-supplied request.json；ir_001 opcode read_request_json 以 request.json 为输入，输出 result_001 request.term、result_002 request.from_date、result_003 request.limit；result_004/result_005 为 from_date/limit 是否存在的条件操作数；metadata 保留同一读取描述。

比较理由：读取动作、文件对象、term 以及可选 from_date/limit 的来源均可定位。存在性布尔用于承载源文 present/missing 条件，属于合法具体表达，不改变读取对象或业务参数。

源文 `src_003` · `SKILL.md:8-8`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

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

图位置："/blocks/block_001/instructions/0/metadata"

## finding_3 · semantic · represented

原文要求：index.search 支持 fuzzy matching，但本工作流不请求 fuzzy expansion。

当前表示：fact:/constraints/2 原文记录 index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

比较理由：图级声明与源文一致；图中没有 fuzzy expansion 操作或额外模糊扩展要求。

源文 `src_003` · `SKILL.md:8-8`：

> Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

图位置："/constraints/2"

## finding_4 · semantic · represented

原文要求：调用 index.search 恰好一次，并以 request.term 原样作为 query 参数。

当前表示：fact:/constraints/0 记录 Call index.search exactly once；block_002/ir_003 只记录一次 call_index_search；inputs/0 为 external_resource index.search，inputs/1 为 result_001(request_term)；constraints/0 声明 Use request.term unchanged as the query argument。

比较理由：次数、目标服务、query 数据来源和 unchanged 要求均保留；dispatch/return 不计为 index.search 调用。

源文 `src_004` · `SKILL.md:10-10`：

> Call index.search exactly once, using request.term unchanged as its query argument.

图位置："/constraints/0"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/constraints/0"

## finding_5 · semantic · represented

原文要求：from_date 存在时原样传递其值；可接受格式是 YYYY-MM-DD。

当前表示：inputs/2 为 result_002(request_from_date)，inputs/3 为 result_004(from_date_present)；constraints/1 记录 When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD。

比较理由：from_date 的值来源、存在条件和格式说明均保留；存在性布尔只承载 present/missing 条件，未把格式说明变成调用前验证。

源文 `src_004` · `SKILL.md:10-10`：

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

图位置："/blocks/block_002/instructions/0/inputs/2"

图位置："/blocks/block_002/instructions/0/inputs/3"

图位置："/blocks/block_002/instructions/0/constraints/1"

## finding_6 · semantic · represented

原文要求：from_date 缺失时省略 from_date 参数；limit 存在时原样作为 limit 参数传递。

当前表示：constraints/2 记录 When from_date is missing, omit the from_date argument；constraints/3 记录 When limit is present, pass its value unchanged as the limit argument；inputs/4 result_003(request_limit)、inputs/5 result_005(limit_present) 绑定 limit 值与存在性。

比较理由：省略条件和 limit 值绑定均保留；存在性布尔用于条件控制。

源文 `src_005` · `SKILL.md:12-12`：

> When from_date is missing, omit the from_date argument. When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_002/instructions/0/constraints/2"

图位置："/blocks/block_002/instructions/0/constraints/3"

图位置："/blocks/block_002/instructions/0/inputs/4"

图位置："/blocks/block_002/instructions/0/inputs/5"

## finding_7 · semantic · represented

原文要求：limit 缺失时省略 limit 参数；不得在本工作流任何位置调用 index.delete。

当前表示：constraints/4 记录 omit limit；图级 constraints/1 记录 Do not invoke index.delete anywhere in this workflow；图中没有 index.delete 操作。

比较理由：省略条件和禁止行为均保留；未发现 delete 调用。

源文 `src_006` · `SKILL.md:14-14`：

> When limit is missing, omit the limit argument. Do not invoke index.delete anywhere in this workflow.

图位置："/blocks/block_002/instructions/0/constraints/4"

图位置："/constraints/1"

## finding_8 · semantic · represented

原文要求：参数描述是调用要求，不指示调用前验证或规范化。

当前表示：fact:/constraints/3 原文记录 Parameter descriptions are call requirements and do not instruct pre-call validation or normalization；图中没有验证/规范化操作。

比较理由：要求性质和禁止范围保留；accepted format 仅作为调用要求，不是额外验证步骤。

源文 `src_007` · `SKILL.md:16-16`：

> Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

图位置："/constraints/3"

## finding_9 · semantic · represented

原文要求：搜索之后，将响应中的 total 值写入本地 count.txt。

当前表示：edges/1 连接 block_002 到 block_003；ir_005 write_file 输入 count.txt 与 result_006(search_total)；constraints/0 声明 Write the response's total value to local count.txt；link inputs/1 指向 call_index_search 的 total 输出。

比较理由：写入动作、本地文件对象、total 数据来源和 after search 顺序均保留；external_resource 不自动表示网络资源，约束明确 local。

源文 `src_007` · `SKILL.md:16-16`：

> After the search, write the response's total value to local count.txt.

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_002/instructions/0/outputs/0"

## finding_10 · semantic · represented

原文要求：原样返回搜索响应中的 items 值。

当前表示：ir_006 return 输入 result_007(search_items)；constraints/0 声明 Return the search response's items value unchanged；link 指向 result_007 定义。

比较理由：返回操作、返回值身份和 unchanged 要求均保留；return 不表示向用户展示内容。

源文 `src_008` · `SKILL.md:18-18`：

> Return the search response's items value unchanged.

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/constraints/0"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_002/instructions/0/outputs/1"

## finding_11 · semantic · represented

原文要求：业务顺序为读取 request、调用 index.search、搜索后写 total、最后返回 items；dispatch/return 是控制终结，不产生额外业务输出。

当前表示：edges/0 block_001 到 block_002，edges/1 block_002 到 block_003；ir_002/ir_004 为 dispatch，ir_006 为 return；block_003 内 write_file 在 return 之前。

比较理由：顺序和终止按图记录保留；dispatch/return 为固定控制操作，不能当作新增业务步骤。

源文 `src_003` · `SKILL.md:8-8`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

源文 `src_004` · `SKILL.md:10-10`：

> Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_007` · `SKILL.md:16-16`：

> After the search, write the response's total value to local count.txt.

源文 `src_008` · `SKILL.md:18-18`：

> Return the search response's items value unchanged.

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/edges/0"

图位置："/edges/1"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/1"

## finding_12 · semantic · represented

原文要求：各结果按实际 identifier 绑定：term/from_date/limit 来自 request 读取，total/items 来自 index.search 响应，并分别用于写文件和返回。

当前表示：links 记录 result_001/002/003/004/005 从 read_request_json 输出绑定到 call_index_search 输入；result_006 从 call_index_search 输出绑定到 write_file；result_007 从 call_index_search 输出绑定到 return。

比较理由：数据来源、使用位置和结果身份按 ID 保留，未用 semantic_name 替换结果身份。

源文 `src_004` · `SKILL.md:10-10`：

> Call index.search exactly once, using request.term unchanged as its query argument. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_005` · `SKILL.md:12-12`：

> When from_date is missing, omit the from_date argument. When limit is present, pass its value unchanged as the limit argument.

源文 `src_007` · `SKILL.md:16-16`：

> After the search, write the response's total value to local count.txt.

源文 `src_008` · `SKILL.md:18-18`：

> Return the search response's items value unchanged.

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/inputs/2"

图位置："/blocks/block_002/instructions/0/inputs/3"

图位置："/blocks/block_002/instructions/0/inputs/4"

图位置："/blocks/block_002/instructions/0/inputs/5"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

## finding_13 · context · represented

原文要求：无对应源文业务要求；这些是受控回述的表示辅助信息。

当前表示：块 key/id/source/instructions 清单、entry/contexts、空 metadata 或 metadata_json、dispatch 的 metadata 等仅用于定位图结构，不补造业务步骤。

比较理由：按表示辅助信息规则，这些字段不能当作新增业务要求；本项仅说明其上下文地位。

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/entry_block_id"

图位置："/declared_context_keys"

## 安全标注未决

- {"instruction_id": "ir_003", "field": "effects", "reason": "无法确定 index.search 是否通过远端网络通信；仅有工具名和 external_resource 不足以证明 net_send 或 net_receive。"}
- {"instruction_id": "ir_006", "field": "effects", "reason": "普通 return 的接收方未在源文或 CFG 说明，无法确定是否构成 user_output 或 model_observe。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：7a64bbb8b1014c15edf7dbc59e7e5ca0bd4fa20a2c2d9039ee6dabe6016724bf

助手已独立复核本次重新提取的 r000 图、完整源文、合法核对结果及全部 6 份安全标注（20 条证据），非人工确认。关键查询、可选参数约束、计数落盘和返回绑定得到表示；没有发现应把现有合法核对结果改作执行错误的情况。audit_passed 仍仅为核对器结论，可选参数的运行实现和 actor 推断存在边界；annotation incomplete 的两项未决有依据。

- 关键过程：block_001/ir_001 从 request.json 读取 term、from_date、limit 及两项存在性；metadata.description 明确保留 user-supplied 来源。block_002/ir_003 是唯一 search 调用，result_006 total 由 block_003/ir_005 写入本地 count.txt，result_007 items 由 ir_006 原样返回。没有混用 total/items，也没有在搜索前写计数。
- 可选参数采用声明式抽象：ir_003 的五条约束分别记录 term 不变、from_date/limit 存在时传原值和缺失时省略；CFG 没有四个条件分支。其 inputs 中存在性标志和可选值是数据依赖，不能据此断言这些标志作为额外业务参数发送，也不能证明运行时一定执行了参数省略。finding_5/finding_6 对存在性控制的文字应限定为这些约束和依赖的表示，尤其 finding_6 的‘存在性布尔用于条件控制’不能扩大为已经实现的控制边。
- 限制：图级约束保留 index.search exactly once、禁止 index.delete、fuzzy matching 只是能力说明、参数格式不要求校验或规范化；实际操作没有补造 fuzzy 扩展、删除或格式修正。未发现这几项关键限制被反向转换。
- 核对器 finding_2–finding_12 均判 represented，未填写 conservative，不能因此称为精确保留。本图没有分支结果合并，不需为其杜撰 DEP-MERGE 说明；可选参数在高层调用约束中表达属于抽象边界，不能用保守依赖规则替代对真实多传参数的判断。
- 标注的 fs_read、fs_write、查询 source/sink 及结果变换有相应动作依据；ir_003 的 model_observe 引用 EM02 工具返回进入模型上下文，符合本轮公开执行模型。没有把禁止声明转换成保护动作，也没有根据工具名称直接标注 net_send/net_receive。
- actor 仍有证据不足：ir_001 仅凭 read_request_json 推定 agent_runtime；ir_002/ir_004 的 llm 依据是 EM03 和‘LLM 可参与调度’，可能参与并不证明本动作确由 LLM 执行。EM03 仅限制调度不能自动推出观察。应将主体映射作为明确执行假设或记录 actor 未决，不能把推断理由当作已知执行事实。
- 与本次 009 同类请求读取相比，008 因推定 runtime 而不标 model_observe，009 因推定 tool 而标 model_observe；源文并未规定这种运行分工差异。这会实质影响后续传播的模型可见边界，宜优先澄清执行映射而非靠 opcode 的命名差异决定。这里不据此宣称已经发生敏感数据泄露。
- 两项已记录未决合理保留：ir_003 没有远端通信依据，工具名/external_resource 不能决定网络发送接收；ir_006 普通 return 未指定接收方，不能自动标 user_output 或 model_observe。incomplete 不是网络调用失败，也不应为减少未决而补造远端或用户边界。
- 本意见绑定新运行 r000 的实际图及 verified 文本保真证书；未沿用旧 008 的非法核对响应、旧图或旧人工结论。程序证据校验通过不证明上述 actor 推断或整体语义判断正确。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
