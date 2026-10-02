# 010-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q04；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：419ebdfa305fb171533662ca807f6e399ab21faafe087065dff05f9bc5711c24；源文 SHA-256：66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/010/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/010/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文背景：SKILL.md 的技能名称、描述、标题、指向 workflow.md 的链接，以及 workflow.md 标题；这些属于文档元数据、上下文或表示辅助信息。

当前表示：受控回述记录了入口、空 contexts、各块 key/id/name/source、以及各操作的 metadata_json；未逐字保留 catalog-query、标题和链接文字，但工作流内容本身已进入后续图记录。

比较理由：名称、标题、链接和 metadata 属于上下文或表示辅助信息，不是业务步骤；受控回述以图结构承载工作流要求。按契约，这不作为业务要求通过，也不据此判为业务遗漏。

源文 `src_001` · `SKILL.md:1-4`：

> ---
> name: catalog-query
> description: Query an index once using a supplied request and preserve optional-parameter semantics.
> ---

源文 `src_002` · `SKILL.md:6-6`：

> # Catalog Query

源文 `src_003` · `SKILL.md:8-8`：

> Follow the requirements in [workflow instructions](references/workflow.md); this file is part of the current workflow.

源文 `src_005` · `references/workflow.md:1-1`：

> # Query workflow

图位置："/entry_block_id"

图位置："/declared_context_keys"

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

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

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1/metadata"

## finding_2 · semantic · represented

原文要求：描述要求用 supplied request 查询一次并保留 optional-parameter semantics；工作流要求 index.search exactly once、不得调用 index.delete，且 fuzzy matching note 不请求 fuzzy expansion。

当前表示：受控回述的图级约束 constraints/0 记录一次查询与可选参数语义，constraints/1 记录 index.search exactly once，constraints/2 记录不得调用 index.delete，constraints/3 记录 fuzzy note 不请求 fuzzy expansion；图中没有 index.delete 或 fuzzy expansion 操作。

比较理由：这些声明与源文的描述、次数、禁止和说明逐项对应。约束是声明不等于已实现，但语义文字已保留，且未发现违反该禁止的额外操作。

源文 `src_001` · `SKILL.md:3-3`：

> description: Query an index once using a supplied request and preserve optional-parameter semantics.

源文 `src_006` · `references/workflow.md:3-3`：

> > Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

源文 `src_008` · `references/workflow.md:7-7`：

> Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_011` · `references/workflow.md:17-17`：

> Do not invoke index.delete anywhere in this workflow.

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/constraints/3"

## finding_3 · semantic · represented

原文要求：读取用户提供的 request.json，其中包含 term，并可能包含 from_date 和 limit。

当前表示：ir_001 使用 opcode read_request_json，输入 external_resource request.json，输出 result_001 request.term、result_002 from_date present、result_003 request.from_date、result_004 limit present、result_005 request.limit；操作级约束重复该读取要求。

比较理由：读取动作、资源对象、term/from_date/limit 的值与存在性均有记录。presence 输出是可选参数条件分支所需的派生表示，不构成源文未规定的额外业务动作。

源文 `src_007` · `references/workflow.md:5-5`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/outputs/1"

图位置："/blocks/block_001/instructions/0/outputs/2"

图位置："/blocks/block_001/instructions/0/outputs/3"

图位置："/blocks/block_001/instructions/0/outputs/4"

图位置："/blocks/block_001/instructions/0/constraints/0"

## finding_4 · semantic · represented

原文要求：根据 from_date 与 limit 的 present/missing 四种条件，采用相应的可选参数调用语义。

当前表示：ir_002 dispatch 使用 result_002 from_date present 和 result_004 limit present 作为选择输入；edges/0 到 edges/3 分别记录四种组合：both present、from_date present and limit missing、from_date missing and limit present、both missing，并指向四个搜索块。

比较理由：四种条件组合与源文的条件要求一致；dispatch 和 edges 是控制表示。这里不声称条件在运行时必然可求值，只核对记录出的分支条件和目标范围。

源文 `src_009` · `references/workflow.md:9-13`：

> - Call argument requirements:
>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
>   - When from_date is missing, omit the from_date argument.
>   - When limit is present, pass its value unchanged as the limit argument.
>   - When limit is missing, omit the limit argument.

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/inputs/0"

图位置："/blocks/block_001/instructions/1/inputs/1"

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

## finding_5 · semantic · represented

原文要求：调用 index.search 恰好一次，并使用 request.term unchanged 作为 query 参数。

当前表示：图级 constraints/1 记录 exactly once；四个分支搜索块各有且仅有一个 index.search（ir_003、ir_005、ir_007、ir_009），均输入 result_001 request.term，且各自 constraints/0 记录使用 request.term unchanged 作为 query argument；未记录循环或重试。

比较理由：四个 index.search 位于同一 dispatch 分出的互斥 presence 分支，按路径各一次，不是同一路径四次调用。term 的来源、数据绑定和 unchanged 要求均保留。

源文 `src_008` · `references/workflow.md:7-7`：

> Call index.search exactly once, using request.term unchanged as its query argument.

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/constraints/0"

## finding_6 · semantic · represented

原文要求：当 from_date 和 limit 均 present 时，from_date 值 unchanged 且接受格式为 YYYY-MM-DD；limit 值 unchanged 作为 limit 参数。

当前表示：block_002 的 ir_003 输入 index.search、result_001 term、result_003 from_date、result_005 limit；constraints/1 记录 from_date present 时 unchanged 且格式 YYYY-MM-DD，constraints/2 记录 limit present 时 unchanged 作为 limit argument。

比较理由：两个可选参数均存在，且分别绑定到读取阶段的 from_date 和 limit 结果。记录中未见额外转换、验证或参数错位。

源文 `src_009` · `references/workflow.md:10-10`：

>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_009` · `references/workflow.md:12-12`：

>   - When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/2"

图位置："/blocks/block_002/instructions/0/inputs/3"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/outputs/1"

图位置："/blocks/block_002/instructions/0/constraints/1"

图位置："/blocks/block_002/instructions/0/constraints/2"

图位置："/blocks/block_002/instructions/1"

## finding_7 · semantic · represented

原文要求：当 from_date present 且 limit missing 时，from_date 值 unchanged 且接受格式为 YYYY-MM-DD；limit 缺失则省略 limit 参数。

当前表示：block_003 的 ir_005 输入 index.search、result_001 term、result_003 from_date，未输入 limit；constraints/1 记录 from_date present 时 unchanged 且格式 YYYY-MM-DD，constraints/2 记录 limit missing 时 omit limit argument。

比较理由：from_date 的值绑定保留，limit 参数在该路径的实际输入列表中缺失，并有 omit 约束对应。

源文 `src_009` · `references/workflow.md:10-10`：

>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

源文 `src_009` · `references/workflow.md:13-13`：

>   - When limit is missing, omit the limit argument.

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/2"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/0/constraints/2"

图位置："/blocks/block_003/instructions/1"

## finding_8 · semantic · represented

原文要求：当 from_date missing 且 limit present 时，省略 from_date 参数；limit 值 unchanged 作为 limit 参数。

当前表示：block_004 的 ir_007 输入 index.search、result_001 term、result_005 limit，未输入 from_date；constraints/1 记录 from_date missing 时 omit from_date argument，constraints/2 记录 limit present 时 unchanged 作为 limit argument。

比较理由：from_date 参数在该路径缺失并有 omit 约束，limit 值绑定到读取结果并保留 unchanged 要求。

源文 `src_009` · `references/workflow.md:11-11`：

>   - When from_date is missing, omit the from_date argument.

源文 `src_009` · `references/workflow.md:12-12`：

>   - When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/0/constraints/2"

图位置："/blocks/block_004/instructions/1"

## finding_9 · semantic · represented

原文要求：当 from_date 和 limit 均 missing 时，省略 from_date 与 limit 两个可选参数。

当前表示：block_005 的 ir_009 仅输入 index.search、result_001 term，未输入 from_date 或 limit；constraints/1 记录 from_date missing 时 omit，constraints/2 记录 limit missing 时 omit。

比较理由：两个可选参数在该路径都未作为 index.search 输入，并有对应 omission 约束；与源文 missing 条件一致。

源文 `src_009` · `references/workflow.md:11-11`：

>   - When from_date is missing, omit the from_date argument.

源文 `src_009` · `references/workflow.md:13-13`：

>   - When limit is missing, omit the limit argument.

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/outputs/1"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_005/instructions/0/constraints/2"

图位置："/blocks/block_005/instructions/1"

## finding_10 · semantic · represented

原文要求：搜索之后，将响应 total 值写入本地 count.txt。

当前表示：edges/4 到 edges/7 将四个搜索块连接到四个写入块；ir_011、ir_013、ir_015、ir_017 均输入 count.txt 与对应分支的 total（result_006、result_008、result_010、result_012），各写入约束记录 after the search 写 response total 到 local count.txt。

比较理由：写入动作、执行顺序、目标文件和分支 specific total 数据绑定均保留；每个搜索路径后有且有一个写入操作，未发现把 items 或其他值写入 count.txt。

源文 `src_013` · `references/workflow.md:21-21`：

> After the search, write the response's total value to local count.txt.

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/constraints/0"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

## finding_11 · semantic · represented

原文要求：返回搜索响应的 items 值 unchanged。

当前表示：ir_012、ir_014、ir_016、ir_018 均为 return，分别输入对应分支的 items（result_007、result_009、result_011、result_013），各 return 约束记录 unchanged；return 作为终结操作出现，相关块无出边。

比较理由：返回身份绑定到对应搜索产生的 items，而不是 total；unchanged 要求有声明，返回路径按分支各一个，未发现额外返回值或返回后继续业务流程。

源文 `src_014` · `references/workflow.md:23-23`：

> Return the search response's items value unchanged.

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/constraints/0"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/constraints/0"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/constraints/0"

## finding_12 · semantic · represented

原文要求：将 query.yaml 中 missing_arguments.from_date=omit 和 missing_arguments.limit=omit 应用到同一调用；参数描述是调用要求，不要求预调用验证或规范化。

当前表示：四个搜索块的 constraints/3 均记录 query.yaml 的 missing_arguments.from_date=omit、missing_arguments.limit=omit，并说明应用到 this same call；constraints/4 均记录参数描述是调用要求且不指示 pre-call validation or normalization；图中无验证或规范化操作。

比较理由：设置值与作用域保留为声明，缺失参数行为也在相应分支的输入省略中体现。源文只要求应用设置，未要求记录读取 query.yaml 的操作，因此未记录该读取不构成业务遗漏。

源文 `src_004` · `query.yaml:1-3`：

> missing_arguments:
>   from_date: omit
>   limit: omit

源文 `src_010` · `references/workflow.md:15-15`：

> Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.

源文 `src_012` · `references/workflow.md:19-19`：

> Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

图位置："/blocks/block_002/instructions/0/constraints/3"

图位置："/blocks/block_002/instructions/0/constraints/4"

图位置："/blocks/block_003/instructions/0/constraints/3"

图位置："/blocks/block_003/instructions/0/constraints/4"

图位置："/blocks/block_004/instructions/0/constraints/3"

图位置："/blocks/block_004/instructions/0/constraints/4"

图位置："/blocks/block_005/instructions/0/constraints/3"

图位置："/blocks/block_005/instructions/0/constraints/4"

## 安全标注未决

- {"instruction_id": "ir_003", "field": "effects", "reason": "无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。"}
- {"instruction_id": "ir_005", "field": "effects", "reason": "无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。"}
- {"instruction_id": "ir_007", "field": "effects", "reason": "无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。"}
- {"instruction_id": "ir_009", "field": "effects", "reason": "无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。"}
- {"instruction_id": "ir_012", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。"}
- {"instruction_id": "ir_014", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。"}
- {"instruction_id": "ir_016", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。"}
- {"instruction_id": "ir_018", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：419ebdfa305fb171533662ca807f6e399ab21faafe087065dff05f9bc5711c24

助手复核：多文件可选参数要求和四路结果身份保留；当前末图没有合流候选歧义。标注网络/返回未决合理，但能力说明被用作实际变换证据不充分。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 已读冻结 SKILL.md、references/workflow.md、query.yaml 三文件全文，末图全部 18 条 IR/控制边/输入输出/约束、两轮合法核对及全部 18 条 profile 证据与 8 项未决。ir_001 约束记录用户来源、term 与可选 from_date/limit，并输出其值及存在性；ir_002 根据两存在性值进入四种互斥组合，分别调用 ir_003/005/007/009。
- 四路 search 的业务输入分别为 term+from_date+limit、term+from_date、term+limit、仅 term，缺失参数确实未列入相应路径，未用 null 替省略。所有调用保留 term 原值、相应 from_date 的 YYYY-MM-DD 和原值、limit 原值；query.yaml 的 missing_arguments.from_date=omit 与 limit=omit 及 this same call 作用域均在各调用约束保留。只要求应用该静态设置，不据此凭空新增运行时读取 query.yaml 的动作。
- 每条路径只经历一个 search，再写本路 total、返回本路 items：result_006/007→ir_011/012，result_008/009→ir_013/014，result_010/011→ir_015/016，result_012/013→ir_017/018。四处静态 search 不等于运行四次；无跨分支结果替换、错误返回、重试或额外格式校验。delete 禁止、fuzzy 能力说明不要求扩展和不要求预校验/规范化均保留。
- 旧版本 010 的 DEP-MERGE 合流候选说明不能沿用到本次图：本次 r001 为每路独立写入/返回，没有公共合流节点引用多个候选响应，末轮所有 conservative=null、conservative_ids=[] 与实际结构一致。此处不需要为新图补旧候选集合，也不能把空 conservative 解释为其他语义已精确证明。
- r000 finding_5 把可选结果列于输入/输出直接解释成无条件实参，判 internal_conflict，与 007/009 的初轮一样对依赖列表的执行含义推断偏强；r001 展开四路之后把可选参数省略表达得更明确。可以确认当前图的路径和参数集合，但不能倒推初轮一定已违反省略要求。
- 原 8 个 effects 未决对应四个 search 的远程通信及四个 return 的 user_output：材料确无远端网络/面向用户证据，保留合理。四搜索均有 tool、source/sink/transformer 与 EM02 下的 model_observe，参数到达工具和返回内容引入有现有接口支持；四次写入 sink/fs_write 与 count.txt 相符，return 没有自动标 user_output。
- 重要证据问题：四个 search 的 roles.transformer 和 effects.transform 都引用 src_006 的“index.search supports fuzzy matching”，而该能力说明后半明确当前工作流不要求 fuzzy expansion。一般查询选择/计算可能支持 transform，但可选能力说明不是本次实际执行该能力的证据。应引用实际 search 行为/输入输出来说明一般变换，并明确不是执行 fuzzy；不能让能力说明在安全标注阶段重新变成动作事实。
- ir_001 的 context_read/fs_read/字段提取 transform 有来源与接口依据，但确定为本地 agent_runtime 仍缺执行证据；dispatch 仅凭 EM03“LLM调度”列 llm，也不能证明本节点执行主体。整体完整性通过不证明这些推断正确，原 audit_passed/incomplete 与未决记录原样保留；以上为助手复核，尚非人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
