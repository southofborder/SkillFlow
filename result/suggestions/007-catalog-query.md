# 007-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q01；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：97ee7d272d3c4269f245db6a9beb86d4b054b1c05e18d8c1d58b3dfdf940b117；源文 SHA-256：55f7fe3829b6a0c3d2ba7c35e0817e9d34aec7fbc6d49a75eeb76c14e5e442bf

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/007/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/007/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 提供 Skill 名称 catalog-query 和摘要 description，标题为 Catalog Query；这些是上下文/摘要，不构成新的业务步骤。

当前表示：受控回述未复述 frontmatter 和标题；它以 entry、contexts 和后续 blocks/constraints 记录图结构。这里仅核对上下文地位，不将其视为遗漏业务要求。

比较理由：frontmatter/title 属于名称和摘要背景；源文的业务要求由后续约束和操作核对。受控文本没有把该摘要变成额外步骤。

源文 `src_001` · `SKILL.md:2-2`：

> name: catalog-query

源文 `src_001` · `SKILL.md:3-3`：

> description: Query an index once using a supplied request and preserve optional-parameter semantics.

源文 `src_002` · `SKILL.md:6-6`：

> # Catalog Query

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2 · context · represented

原文要求：源文没有对应业务要求；这些是受控图的结构、标识、来源标记、操作清单和 metadata 辅助字段。

当前表示：受控回述记录块 key/id/source/instructions 清单、各操作 metadata_json、draft/ID 等，均为图记录辅助信息。

比较理由：这些字段用于定位块、操作和资源，不新增源文业务步骤，也不替代语义要求。

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_003/instructions/2/metadata"

图位置："/blocks/block_003/instructions/3/metadata"

## finding_3 · context · represented

原文要求：源文 line8 是能力说明：index.search 支持 fuzzy matching，但本工作流不请求 fuzzy expansion。

当前表示：受控 graph-level constraint /constraints/0 保留该能力说明，并明确不请求 fuzzy expansion；图中没有 fuzzy expansion 操作。

比较理由：该说明是背景/能力约束，不是新步骤；记录为声明约束并保留否定限定，未改变模态。

源文 `src_003` · `SKILL.md:8-8`：

> Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

图位置："/constraints/0"

## finding_4 · semantic · represented

原文要求：源文 line15 禁止在本工作流任何位置调用 index.delete。

当前表示：受控 graph-level constraint /constraints/1 记录禁止调用 index.delete；块0/1/2 的操作清单中未出现 index.delete 操作。

比较理由：禁止项以声明约束保留，且操作记录没有相冲突的 index.delete 调用。

源文 `src_003` · `SKILL.md:15-15`：

> Do not invoke index.delete anywhere in this workflow.

图位置："/constraints/1"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_003/instructions"

## finding_5 · semantic · represented

原文要求：源文 line16 说明参数描述是调用要求，不指示调用前校验或规范化。

当前表示：受控 graph-level constraint /constraints/2 记录该要求；图中没有记录预校验或规范化操作。

比较理由：该要求是作用域说明；受控文本以图级声明保留，未新增 validation/normalization 步骤。

源文 `src_003` · `SKILL.md:16-16`：

> Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

图位置："/constraints/2"

## finding_6 · semantic · represented

原文要求：源文 line9 要求读取用户提供的 request.json，其中包含 term，且可能包含 from_date 和 limit。

当前表示：受控 block_001 名称为 Read the user-supplied request.json；ir_001 read_request_json 以 external_resource request.json 为输入，输出 result_001/request.term、result_002/request.from_date、result_003/request.limit。可选参数在 index.search 的调用约束中另行记录；读取操作本身未加入校验/规范化。

比较理由：读取对象与请求字段身份匹配；user-supplied 作为块名上下文保留。may contain 的调用语义由后续 optional 约束核对，不在此读取步骤额外补造分支。

源文 `src_003` · `SKILL.md:9-9`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/outputs/1"

图位置："/blocks/block_001/instructions/0/outputs/2"

## finding_7 · semantic · represented

原文要求：源文 line10 要求恰好调用 index.search 一次，并将 request.term 原样作为 query 参数。

当前表示：受控 block_002 中有唯一 ir_003 index.search；inputs 含 external_resource index.search、result_001/request.term、result_002/request.from_date、result_003/request.limit；constraint/0 明确 exactly once 且 request.term unchanged 作为 query argument。result_001 的 link 指向 block_001 的 request.term 输出。

比较理由：操作名、调用次数约束和 term 绑定均保留；external_resource index.search 是资源标识，不当作额外业务参数。inputs/2 和 inputs/3 的 present/missing 语义由后续 optional 约束单独核对。

源文 `src_003` · `SKILL.md:10-10`：

> Call index.search exactly once, using request.term unchanged as its query argument.

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/inputs/2"

图位置："/blocks/block_002/instructions/0/inputs/3"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

## finding_8 · semantic · represented

原文要求：源文 line11 要求 from_date 存在时原样传值，接受格式为 YYYY-MM-DD。

当前表示：受控 constraint/1 记录 present 时原样传递及 YYYY-MM-DD 接受格式；inputs/2 绑定 result_002/request.from_date，link 指向读取输出。constraint/5 另行说明该输入是条件候选而非无条件实参。

比较理由：条件、值来源和格式说明均保留；没有记录预校验/规范化，符合 line16。

源文 `src_003` · `SKILL.md:11-11`：

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

图位置："/blocks/block_002/instructions/0/constraints/1"

图位置："/blocks/block_002/instructions/0/inputs/2"

## finding_9 · semantic · represented

原文要求：源文 line12 要求 from_date 缺失时省略 from_date 参数。

当前表示：受控 constraint/2 明确 missing 时 omit from_date argument；constraint/5 说明 inputs/2 是条件候选，仅在请求中存在时表示传递，缺失时省略，不是无条件实参。

比较理由：缺失分支以声明约束保留；虽然 inputs 列表含 result_002，constraint/5 明确限定其条件候选身份，未把它说成始终传递。

源文 `src_003` · `SKILL.md:12-12`：

> When from_date is missing, omit the from_date argument.

图位置："/blocks/block_002/instructions/0/constraints/2"

图位置："/blocks/block_002/instructions/0/constraints/5"

图位置："/blocks/block_002/instructions/0/inputs/2"

## finding_10 · semantic · represented

原文要求：源文 line13 要求 limit 存在时原样作为 limit 参数传递。

当前表示：受控 constraint/3 记录 present 时原样传递为 limit argument；inputs/3 绑定 result_003/request.limit，link 指向读取输出；constraint/5 说明其为条件候选。

比较理由：条件、值来源和参数角色保留。

源文 `src_003` · `SKILL.md:13-13`：

> When limit is present, pass its value unchanged as the limit argument.

图位置："/blocks/block_002/instructions/0/constraints/3"

图位置："/blocks/block_002/instructions/0/inputs/3"

## finding_11 · semantic · represented

原文要求：源文 line14 要求 limit 缺失时省略 limit 参数。

当前表示：受控 constraint/4 明确 missing 时 omit limit argument；constraint/5 说明 inputs/3 是条件候选，缺失时省略。

比较理由：缺失分支保留；inputs/3 虽在输入位置记录，但被 constraint/5 限定为条件候选而非无条件实参。

源文 `src_003` · `SKILL.md:14-14`：

> When limit is missing, omit the limit argument.

图位置："/blocks/block_002/instructions/0/constraints/4"

图位置："/blocks/block_002/instructions/0/constraints/5"

图位置："/blocks/block_002/instructions/0/inputs/3"

## finding_12 · semantic · represented

原文要求：源文 line17 要求搜索后将 response 的 total 值写入本地 count.txt。

当前表示：受控 block_003 位于 block_002(index.search) 之后；ir_005 extract_total_from_search_response 从 result_004/search_response 生成 result_005/response.total，ir_006 write_total_to_count_txt 以 result_005 和 external_resource count.txt 为输入；constraint/0 记录 After the search, write ... to local count.txt。link 绑定 result_004->extract_total、result_005->write。

比较理由：对象 response.total、目标本地 count.txt、after search 的顺序和写入动作均保留；extract_total 是取得所需 total 的具体绑定步骤，不改变写入内容。

源文 `src_003` · `SKILL.md:17-17`：

> After the search, write the response's total value to local count.txt.

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/1"

图位置："/blocks/block_003/instructions/1/constraints/0"

## finding_13 · semantic · represented

原文要求：源文 line18 要求返回 search response 的 items 值，且保持不变。

当前表示：受控 ir_007 extract_items_from_search_response 从 result_004/search_response 生成 result_006/response.items；ir_008 return 以 result_006 为输入；constraint/0 记录 Return ... items value unchanged。link 绑定 result_004->extract_items、result_006->return。

比较理由：返回身份是 response.items，不是 total 或其他结果；return 是控制终结操作，输入记录返回值；extract_items 是取 items 的具体绑定步骤，constraint 明确 unchanged。

源文 `src_003` · `SKILL.md:18-18`：

> Return the search response's items value unchanged.

图位置："/blocks/block_003/instructions/2"

图位置："/blocks/block_003/instructions/2/inputs/0"

图位置："/blocks/block_003/instructions/2/outputs/0"

图位置："/blocks/block_003/instructions/3"

图位置："/blocks/block_003/instructions/3/inputs/0"

图位置："/blocks/block_003/instructions/3/constraints/0"

## finding_14 · semantic · represented

原文要求：源文步骤次序要求：先读取 request，再调用 index.search；搜索完成后写 count.txt，最后返回 items。

当前表示：受控 block_001/block_002/block_003 的顺序由 /edges/0 (block_001->block_002) 和 /edges/1 (block_002->block_003) 记录；block_001 内 ir_001 后 ir_002 dispatch，block_002 内 ir_003 后 ir_004 dispatch，block_003 内 ir_005/ir_006 在 ir_007/ir_008 之前。

比较理由：读取->搜索->写 total->返回 items 的先后由块边和操作记录保留；dispatch 是固定控制终结操作，不是新增业务动作。

源文 `src_003` · `SKILL.md:9-9`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

源文 `src_003` · `SKILL.md:10-10`：

> Call index.search exactly once, using request.term unchanged as its query argument.

源文 `src_003` · `SKILL.md:17-17`：

> After the search, write the response's total value to local count.txt.

源文 `src_003` · `SKILL.md:18-18`：

> Return the search response's items value unchanged.

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/edges/0"

图位置："/edges/1"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_003/instructions"

## 安全标注未决

- {"instruction_id": "ir_003", "field": "effects", "reason": "index.search 的工具名称和调用记录未提供远程通信依据，无法确定是否发生 net_send/net_receive。"}
- {"instruction_id": "ir_008", "field": "effects", "reason": "return 的接收方未明确，普通 return 不能单独证明 user_output；也无法确定是否进入模型上下文，因此效果无法确定。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：97ee7d272d3c4269f245db6a9beb86d4b054b1c05e18d8c1d58b3dfdf940b117

助手复核：查询和返回主过程保留；反馈通过主要来自可选输入解释约束的补充，不能当作精确实参省略机制已实现。安全未决合理，搜索边界角色存在漏标。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 已读冻结 Q01 全文、末图全部 8 条 IR/边/约束、两轮合法核对及所有 profile 证据。读取 request.json 得到 term/from_date/limit 的实际结果；唯一 ir_003 index.search 的约束保留 exactly once、term unchanged、from_date 原值及 YYYY-MM-DD、limit 原值和缺失分别 omit。ir_005 从同一 search_response=result_004 取 total=result_005 并由 ir_006 写 count.txt；ir_007 取 items=result_006，ir_008 原值返回，次序与返回身份无明显错转。
- 图级仍将 fuzzy 作为能力说明且不要求扩展，禁止 index.delete，并保留参数说明不要求预校验/规范化；实际没有补这些业务操作。没有因 return 自动添加用户输出步骤。
- r000 finding_5/finding_6 把输入列表中出现 from_date/limit 直接解释为缺失时也会传实参，判 internal_conflict；这个结论对依赖列表的执行含义过强。r001 实际保持三个顺序块、同一 search 和全部可选结果输入，仅新增 ir_003.constraints[5]，解释可选输入为存在时传递、缺失时省略的条件候选。末轮 finding_9/finding_11 据此接受，属于开放操作可选语义的声明澄清，不是新增了四互斥调用路径或可执行参数组装机制。
- 现有 present/missing 声明可表达四种参数组合的要求，但图没有四分支 CFG、显式存在性判断或已形式化的可选操作数语义。助手不据此强判额外参数发送，也不称修复已保证运行时省略正确；核对器通过与保真证书只保留各自边界。该轮 conservative_ids=[] 不等于精确保留，尤其不能用它宣称从依赖集合已恢复精确实参集合。
- 原标注的两项 effects 未决有依据：ir_003 无远端通信依据，不强贴 net_send/net_receive；ir_008 未说明接收者是用户或模型，不强贴 user_output/model_observe。搜索工具返回结果按 EM02 标 model_observe 合理，transform 对应搜索选择/计算，不表示隐私消除。
- ir_003.roles 只有 source/transformer，缺少把请求参数交给工具边界或使响应进入模型边界的 sink；同义 008 搜索已标 source/sink/transformer，该例的重要边界角色覆盖不足。是否跨网络未决不妨碍记录已有的工具/模型接收边界。
- ir_001、ir_005、ir_007 仅凭读取/提取 opcode 推定本地 agent_runtime，各 dispatch 又仅由 EM03 推定 llm；源文没有明确执行归属或隔离。fs_read/字段选择 transform/fs_write 的动作依据可以保留，但这些主体推断不能代替 model_observe 是否成立的证据。原 incomplete 与两项 unresolved 保持，以上为助手复核而非人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
