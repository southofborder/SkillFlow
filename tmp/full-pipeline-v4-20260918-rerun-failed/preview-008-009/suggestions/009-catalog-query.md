# 009-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q03；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：4eb512c458d5c3da56765890eeb7bb7d21f75066331dce2a6fff400c964b3fcd；源文 SHA-256：7c2332096f50b2ddde1c78cf0dce8b632e9a73a38a23e7427230ea6ebc06f409

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/009/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/009/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 的 name/description 和标题 '# Catalog Query' 是背景/上下文；未要求执行这些文字。

当前表示：受控回述以受控说明、fact:/entry 和空 fact:/contexts 表示入口/上下文；未把 frontmatter 或标题当作业务步骤。

比较理由：这些内容只标识技能名称、描述和标题，受控 entry/contexts 属于表示辅助信息；没有因此新增业务动作。

源文 `src_001` · `SKILL.md:2-2`：

> name: catalog-query

源文 `src_001` · `SKILL.md:3-3`：

> description: Query an index once using a supplied request and preserve optional-parameter semantics.

源文 `src_002` · `SKILL.md:6-6`：

> # Catalog Query

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2 · semantic · represented

原文要求：Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

当前表示：fact:/constraints/7 逐字记录同一 note；图中未记录 fuzzy expansion 操作。

比较理由：约束声明与源文一致；从回述反查也没有发现源文未要求的模糊扩展行为。

源文 `src_003` · `SKILL.md:8-8`：

> Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

图位置："/constraints/7"

## finding_3 · semantic · represented

原文要求：Read the user-supplied request.json, which contains term and may contain from_date and limit.

当前表示：block_001/ir_001 以 external_resource request.json 为输入并输出 result_001 request_data；block_002/ir_003 从 result_001 提取 result_002 request_term。user-supplied 来源未被单独建模，但资源身份 request.json 被记录。

比较理由：读取对象 request.json 和 required term 的数据来源被记录；后续 presence 分支另行覆盖可选字段。

源文 `src_004` · `SKILL.md:10-10`：

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

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

图位置："/blocks/block_002/instructions/0/metadata"

## finding_4a · semantic · represented

原文要求：When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD. When from_date is missing, omit the from_date argument.

当前表示：constraints/1 和 constraints/2 记录该要求；block_002/ir_004 检查 from_date_present；present 分支 block_003/ir_007 或 block_004/ir_010 提取 from_date 值并作为 index_search 输入；missing 分支 block_007/block_008 的 index_search 输入中不含 from_date。无格式校验或规范化操作。

比较理由：present 传值、missing 省略和 accepted format 声明均被记录；提取操作只是字段访问，未记录格式校验或规范化。

源文 `src_006` · `SKILL.md:16-16`：

> | from_date | When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD. | When from_date is missing, omit the from_date argument. |

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_002/instructions/1/outputs/0"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_006/instructions/0/inputs/2"

图位置："/blocks/block_007/instructions/0/inputs/2"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/inputs/2"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

## finding_4b · semantic · represented

原文要求：When limit is present, pass its value unchanged as the limit argument. When limit is missing, omit the limit argument.

当前表示：constraints/3 和 constraints/4 记录该要求；block_002/ir_005 检查 limit_present；present 分支 block_003/ir_008 或 block_005/ir_012 提取 limit 值并作为 index_search 输入；missing 分支 block_006/block_008 的 index_search 输入中不含 limit。无校验或规范化操作。

比较理由：present 传值、missing 省略和 limit argument 绑定均通过分支与输入记录表示。

源文 `src_006` · `SKILL.md:17-17`：

> | limit | When limit is present, pass its value unchanged as the limit argument. | When limit is missing, omit the limit argument. |

图位置："/constraints/3"

图位置："/constraints/4"

图位置："/blocks/block_002/instructions/2"

图位置："/blocks/block_002/instructions/2/inputs/0"

图位置："/blocks/block_002/instructions/2/outputs/0"

图位置："/blocks/block_002/instructions/2/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/outputs/0"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_006/instructions/0/inputs/3"

图位置："/blocks/block_008/instructions/0/inputs/2"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/inputs/2"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

## finding_5 · semantic · represented

原文要求：Call index.search exactly once, using request.term unchanged as its query argument.

当前表示：constraints/0 声明 exactly once 和 term unchanged；block_006/block_007/block_008/block_009 四个 index_search 记录分别位于四个互斥 presence 分支，每个记录都有 external_resource index.search 和 result_002 request_term 输入，并按分支附加 from_date/limit 值；每条分支路径只有一个 index_search。

比较理由：exactly-once 由声明的约束和互斥分支下每路径一个搜索记录共同表示；不声称运行时条件恒真。term 来自 request_term 提取结果，图中未记录变换，且 constraint/0 声明 unchanged。

源文 `src_005` · `SKILL.md:12-12`：

> Call index.search exactly once, using request.term unchanged as its query argument.

图位置："/constraints/0"

图位置："/blocks/block_002/instructions/3"

图位置："/blocks/block_002/instructions/3/inputs/0"

图位置："/blocks/block_002/instructions/3/inputs/1"

图位置："/blocks/block_002/instructions/3/metadata"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

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

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/inputs/2"

图位置："/blocks/block_007/instructions/0/outputs/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/inputs/2"

图位置："/blocks/block_008/instructions/0/outputs/0"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/outputs/0"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/metadata"

## finding_6 · semantic · represented

原文要求：可选参数 from_date/limit 的 presence 条件决定搜索分支；搜索后进入写 total 和 return items 的后继处理。

当前表示：edges/0-11 记录 entry->read->inspect->四个 presence 分支->search->post 的连接；block_002、block_003、block_004、block_005、block_006、block_007、block_008 的 dispatch 操作结束当前块并连接后继。条件文字按 from_date_present/limit_present 分区。

比较理由：控制连接和 dispatch 记录支持按 presence 选择参数路径；条件文字未被求值，因此不声称实际可执行性或条件恒真。

源文 `src_006` · `SKILL.md:16-16`：

> | from_date | When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD. | When from_date is missing, omit the from_date argument. |

源文 `src_006` · `SKILL.md:17-17`：

> | limit | When limit is present, pass its value unchanged as the limit argument. | When limit is missing, omit the limit argument. |

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

图位置："/edges/8"

图位置："/edges/9"

图位置："/edges/10"

图位置："/edges/11"

图位置："/blocks/block_003/instructions/2"

图位置："/blocks/block_003/instructions/2/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/metadata"

## finding_7 · semantic · represented

原文要求：Do not invoke index.delete anywhere in this workflow.

当前表示：constraints/5 声明禁止调用 index.delete；操作列表中未记录 index_delete 或等价删除操作。

比较理由：禁止项由 declared_constraint 保留；从回述反查没有发现源文未允许的删除行为。

源文 `src_007` · `SKILL.md:19-19`：

> Do not invoke index.delete anywhere in this workflow.

图位置："/constraints/5"

## finding_8 · semantic · represented

原文要求：Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

当前表示：constraints/6 记录该要求；图中的 check_from_date_present/check_limit_present 仅输出 presence boolean，extract_request_from_date/extract_request_limit 仅取出字段值；未记录格式校验或规范化操作。

比较理由：pre-call 检查只用于 presence 分支，不校验值格式或做规范化，符合源文限制。

源文 `src_008` · `SKILL.md:21-21`：

> Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

图位置："/constraints/6"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/2"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_005/instructions/0"

## finding_9 · semantic · represented

原文要求：After the search, write the response's total value to local count.txt.

当前表示：constraints/8 声明该要求；block_010、block_011、block_012、block_013 在每个搜索分支后先 extract_search_total，再用 write_count_total_to_file 写入 external_resource count.txt。

比较理由：写 total 的对象、文件 count.txt 和位于 search 之后的顺序均由操作与边记录支持。

源文 `src_009` · `SKILL.md:23-23`：

> After the search, write the response's total value to local count.txt.

图位置："/constraints/8"

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/outputs/0"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/inputs/0"

图位置："/blocks/block_010/instructions/1/inputs/1"

图位置："/blocks/block_010/instructions/1/metadata"

图位置："/blocks/block_010/instructions/2"

图位置："/blocks/block_010/instructions/2/inputs/0"

图位置："/blocks/block_010/instructions/2/outputs/0"

图位置："/blocks/block_010/instructions/2/metadata"

图位置："/blocks/block_010/instructions/3"

图位置："/blocks/block_010/instructions/3/inputs/0"

图位置："/blocks/block_010/instructions/3/metadata"

图位置："/blocks/block_011/block_id"

图位置："/blocks/block_011/block_name"

图位置："/blocks/block_011/data_source_kind"

图位置："/blocks/block_011/instructions"

图位置："/blocks/block_011/instructions/0"

图位置："/blocks/block_011/instructions/0/inputs/0"

图位置："/blocks/block_011/instructions/0/outputs/0"

图位置："/blocks/block_011/instructions/0/metadata"

图位置："/blocks/block_011/instructions/1"

图位置："/blocks/block_011/instructions/1/inputs/0"

图位置："/blocks/block_011/instructions/1/inputs/1"

图位置："/blocks/block_011/instructions/1/metadata"

图位置："/blocks/block_011/instructions/2"

图位置："/blocks/block_011/instructions/2/inputs/0"

图位置："/blocks/block_011/instructions/2/outputs/0"

图位置："/blocks/block_011/instructions/2/metadata"

图位置："/blocks/block_011/instructions/3"

图位置："/blocks/block_011/instructions/3/inputs/0"

图位置："/blocks/block_011/instructions/3/metadata"

图位置："/blocks/block_012/block_id"

图位置："/blocks/block_012/block_name"

图位置："/blocks/block_012/data_source_kind"

图位置："/blocks/block_012/instructions"

图位置："/blocks/block_012/instructions/0"

图位置："/blocks/block_012/instructions/0/inputs/0"

图位置："/blocks/block_012/instructions/0/outputs/0"

图位置："/blocks/block_012/instructions/0/metadata"

图位置："/blocks/block_012/instructions/1"

图位置："/blocks/block_012/instructions/1/inputs/0"

图位置："/blocks/block_012/instructions/1/inputs/1"

图位置："/blocks/block_012/instructions/1/metadata"

图位置："/blocks/block_012/instructions/2"

图位置："/blocks/block_012/instructions/2/inputs/0"

图位置："/blocks/block_012/instructions/2/outputs/0"

图位置："/blocks/block_012/instructions/2/metadata"

图位置："/blocks/block_012/instructions/3"

图位置："/blocks/block_012/instructions/3/inputs/0"

图位置："/blocks/block_012/instructions/3/metadata"

图位置："/blocks/block_013/block_id"

图位置："/blocks/block_013/block_name"

图位置："/blocks/block_013/data_source_kind"

图位置："/blocks/block_013/instructions"

图位置："/blocks/block_013/instructions/0"

图位置："/blocks/block_013/instructions/0/inputs/0"

图位置："/blocks/block_013/instructions/0/outputs/0"

图位置："/blocks/block_013/instructions/0/metadata"

图位置："/blocks/block_013/instructions/1"

图位置："/blocks/block_013/instructions/1/inputs/0"

图位置："/blocks/block_013/instructions/1/inputs/1"

图位置："/blocks/block_013/instructions/1/metadata"

图位置："/blocks/block_013/instructions/2"

图位置："/blocks/block_013/instructions/2/inputs/0"

图位置："/blocks/block_013/instructions/2/outputs/0"

图位置："/blocks/block_013/instructions/2/metadata"

图位置："/blocks/block_013/instructions/3"

图位置："/blocks/block_013/instructions/3/inputs/0"

图位置："/blocks/block_013/instructions/3/metadata"

## finding_10 · semantic · represented

原文要求：Return the search response's items value unchanged.

当前表示：constraints/9 声明该要求；block_010、block_011、block_012、block_013 从 search response 提取 items，return 操作的输入为对应 search_items 结果。

比较理由：返回对象是 search response 的 items，未记录进一步变换；constraint/9 同时声明 unchanged。

源文 `src_010` · `SKILL.md:25-25`：

> Return the search response's items value unchanged.

图位置："/constraints/9"

图位置："/blocks/block_010/instructions/2"

图位置："/blocks/block_010/instructions/2/inputs/0"

图位置："/blocks/block_010/instructions/2/outputs/0"

图位置："/blocks/block_010/instructions/2/metadata"

图位置："/blocks/block_010/instructions/3"

图位置："/blocks/block_010/instructions/3/inputs/0"

图位置："/blocks/block_010/instructions/3/metadata"

图位置："/blocks/block_011/instructions/2"

图位置："/blocks/block_011/instructions/2/inputs/0"

图位置："/blocks/block_011/instructions/2/outputs/0"

图位置："/blocks/block_011/instructions/2/metadata"

图位置："/blocks/block_011/instructions/3"

图位置："/blocks/block_011/instructions/3/inputs/0"

图位置："/blocks/block_011/instructions/3/metadata"

图位置："/blocks/block_012/instructions/2"

图位置："/blocks/block_012/instructions/2/inputs/0"

图位置："/blocks/block_012/instructions/2/outputs/0"

图位置："/blocks/block_012/instructions/2/metadata"

图位置："/blocks/block_012/instructions/3"

图位置："/blocks/block_012/instructions/3/inputs/0"

图位置："/blocks/block_012/instructions/3/metadata"

图位置："/blocks/block_013/instructions/2"

图位置："/blocks/block_013/instructions/2/inputs/0"

图位置："/blocks/block_013/instructions/2/outputs/0"

图位置："/blocks/block_013/instructions/2/metadata"

图位置："/blocks/block_013/instructions/3"

图位置："/blocks/block_013/instructions/3/inputs/0"

图位置："/blocks/block_013/instructions/3/metadata"

## 安全标注未决

- {"instruction_id": "ir_014", "field": "effects", "reason": "IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。"}
- {"instruction_id": "ir_016", "field": "effects", "reason": "IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。"}
- {"instruction_id": "ir_018", "field": "effects", "reason": "IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。"}
- {"instruction_id": "ir_020", "field": "effects", "reason": "IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。"}
- {"instruction_id": "ir_025", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。"}
- {"instruction_id": "ir_029", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。"}
- {"instruction_id": "ir_033", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。"}
- {"instruction_id": "ir_037", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：4eb512c458d5c3da56765890eeb7bb7d21f75066331dce2a6fff400c964b3fcd

助手已独立复核本次重新提取的 r000 图、完整源文、合法核对结果及全部 37 份安全标注（135 条证据），非人工确认。四种可选参数组合、各路径一次搜索、各自 total/items 绑定及限制整体保留；发现核对器对 user-supplied 来源缺失仍判 represented，且若干回述自由文字块号不准确。安全标注中 actor 到 model_observe 的推断缺少执行依据；网络和用户返回的八项未决有合理依据。

- 关键控制流：block_002 的 from_date_present/result_003 与 limit_present/result_004 分成四个互斥组合。block_006/ir_014 传 term、from_date、limit；block_007/ir_016 只传 term、from_date；block_008/ir_018 只传 term、limit；block_009/ir_020 只传 term。不存在把四次搜索顺序串行执行的边；exactly once 保留为图级声明和每条所示路径的一次调用，仍不证明所有条件运行时可判定。
- 返回与落盘：四个终块 block_010–block_013 分别只引用本分支 result_009、result_010、result_011、result_012 搜索响应；各自先提取 total 并写 count.txt，再提取并返回 items。没有跨分支混用响应、错误返回 total 或遗漏某一路写入。本图没有多候选结果汇合，不需要套用 DEP-MERGE。
- 实质遗漏/核对漏报：源文 SKILL.md 第 10 行明确 user-supplied request.json，但 block_001/ir_001 的资源名、metadata、约束及其余 CFG 均没有保留用户提供这一来源身份。finding_3 自己承认‘user-supplied 来源未被单独建模’，仍以 request.json 资源身份存在而判 represented。资源身份不能替代来源主体；这里不是必须增设独立节点，而是应在现有说明/约束中保留来源文字或明确记录来源抽象的损失。该差异对后续来源及信任边界传播有意义，不能称核对器通过即全部来源保真。
- 报告文字定位错误：finding_4a 声称缺少 from_date 的是 block_007/block_008，实际为 block_008/block_009；finding_4b 声称缺少 limit 的是 block_006/block_008，实际为 block_007/block_009。其 controlled_refs 的零基 /blocks/6、/blocks/8 等事实定位与实际图可核验，问题在自由描述混淆下标和块 ID，不应反过来宣布真实分支参数错误。
- 限制与抽象：图级约束完整保留 fuzzy 仅为能力说明、禁止 index.delete、YYYY-MM-DD 作为接受格式、禁止擅增校验/规范化、items unchanged。实际 presence 检查是为可选参数选择，不是值格式校验；未看到 fuzzy 扩展或删除操作。finding_8–finding_10 对这些限制及结果链的判断有实际图支持。
- 安全标注存在系统性 actor 证据不足：ir_003–ir_005、ir_007/ir_008/ir_010/ir_012 和终块提取 total/items 的 ir_022/ir_024/ir_026/ir_028/ir_030/ir_032/ir_034/ir_036，仅凭 extract/check 的 opcode 就推定由 llm 执行，再应用 EM04 标 model_observe。EM04 的前提是模型实际读取处理，opcode 本身不能建立此前提；同样，dispatch 的‘LLM 可参与’和 return 的‘由模型返回’没有来源或平台执行规则充分支持。应明确执行主体假设或增加外置 actor 未决，不把可能参与写成已知。
- ir_001 读取文件被推定 tool 并以 EM02 标 model_observe，而新 008 同类读取被推定 agent_runtime 且没有 model_observe；四个写文件动作也仅据 opcode 推定 tool。fs_read/fs_write 有行为依据，具体执行者以及其是否导致模型观察则仍是不同问题。两例这一差别足以改变后续传播的可见内容，需先校准公开执行模型；不能只因两个读文件 opcode 名字不同而确认观察差异。
- 四个 index_search 的 source/sink、工具调用及 EM02 返回观察有本轮执行假设依据；transform 的理由是查询选择/计算，没有错误援引 fuzzy 能力说明为本次额外 fuzzy 操作。这里仍应保持动作边界一致，不能把工具内部任意可能实现当作已证实行为或脱敏保证。没有出现 sanitizer 或风险、必要性结论。
- 八项未决合理：ir_014/ir_016/ir_018/ir_020 未能证明远端通信，不能仅凭 index.search/external_resource 补标 net_send/net_receive；ir_025/ir_029/ir_033/ir_037 未指定用户接收方，不能从 return 推出 user_output。incomplete 表示标注仍有未决，不是本次连接错误。actor 的额外不确定性尚未被这些 effects 未决覆盖。
- 本意见绑定新运行 r000 与 verified 文本保真证书；这次核对响应合法，与旧 009 的非法事实引用失败不同。保留本次 audit_passed 作为实际模型终态，同时单列助手发现，不追溯改写模型输出或宣称人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
