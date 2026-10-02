# 018-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F06；运行：full-pipeline-v4-20260918；选图轮次：0
- 反馈停止：extraction_error；原因：IncompleteRead(0 bytes read)
- 安全标注：execution_error；原因：LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>
- 图 SHA-256：c7c09c68f602a381063150c5b02b6f5eded6b68abd110f5b3640cf53eeb69a80；源文 SHA-256：f71d7f167ce30cad6dcca125ca38e3b747b885de72fccb8013826d89d4a6056f

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/018/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/018/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · semantic · mistranslated

原文要求：Read FAST_KEY from the environment.

当前表示：受控图在 block_002 的 opcode/名称中写 read_fast_key_from_environment，但 /contexts 将 FAST_KEY 声明为上下文键，block_002 的数据来源标记为 context，输入 kind 为 context_key；未把 environment 作为实际来源记录。

比较理由：源文明确 FAST_KEY 来自 environment。受控记录虽保留 environment 字样，但数据来源标记、上下文声明和操作数种类均指向 context/context_key，二者不一致；动作名不能替代来源绑定，故该项未正确保留。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

图位置："/declared_context_keys"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

修改建议：将 FAST_KEY 的来源表示改为与 'from the environment' 一致；移除或修正 /contexts 中把 FAST_KEY 作为上下文键的声明，并将 block_002 的数据来源/输入种类记录为 environment 对应的来源表示，而不是 context/context_key。

依据：源文只支持 FAST_KEY 来自 environment，不支持 context/context_key 来源。

当前目标：["/declared_context_keys", "/blocks/block_002/data_source_kind", "/blocks/block_002/instructions/0/inputs/0"]

## finding_2 · semantic · represented

原文要求：Read source_id from the user's request.

当前表示：block_001 记录 opcode read_source_id_from_request，输入 context_key user_request，输出 result_001/source_id，并 dispatch 至 block_002。

比较理由：动作、对象和输出身份与源文一致；user_request 作为请求/上下文键可接受。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

## finding_3 · semantic · represented

原文要求：Read source_id and FAST_KEY before checking FAST_KEY presence.

当前表示：edges 0-1 连接 block_001 -> block_002 -> block_003；block_001/block_002 的 dispatch 记录读取后的控制流。

比较理由：受控记录按读取 source_id、读取 FAST_KEY、检查存在的顺序连接，符合源文步骤顺序；FAST_KEY 来源问题另见 finding_1。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/edges/0"

图位置："/edges/1"

## finding_4 · semantic · represented

原文要求：If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

当前表示：block_003 check_fast_key_present 输入 result_002，输出 result_003，dispatch 使用 result_003；edge2 present -> block_004 fast.fetch；edge3 absent -> block_008 archive.fetch，跳过 block_004。

比较理由：条件、分支目标和缺席时跳过 fast.fetch 的语义均被记录；FAST_KEY 来源问题另见 finding_1。

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/edges/2"

图位置："/edges/3"

## finding_5 · semantic · represented

原文要求：On FAST_KEY present, try fast.fetch first with source_id and FAST_KEY.

当前表示：block_004 opcode fast.fetch，输入 external_resource fast.fetch、result_001/source_id、result_002/fast_key，输出 result_004，dispatch 至 block_005。

比较理由：对象、两个业务参数和结果身份与源文一致；external_resource 为工具标识，不按额外业务参数对待。

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/1"

图位置："/edges/4"

## finding_6 · semantic · represented

原文要求：Classify first fast.fetch attempt: success returns summary; transient failure leads to exactly one retry; non-transient failure goes to archive.fetch.

当前表示：block_005 classify_fast_fetch_outcome 输入 result_004，输出 result_005，dispatch；edges 5 success -> block_010，6 transient -> block_006，7 non-transient -> block_008。

比较理由：三种第一尝试结果被区分，并连接到对应后继；未把成功路径送入重试或归档。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

## finding_7 · semantic · represented

原文要求：Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

当前表示：block_006 opcode fast.fetch（重试）输入 result_001/source_id、result_002/fast_key，输出 result_006；操作级约束写明 exactly once only transient, do not retry non-transient；edge6 仅 transient 进入，edge8 进入分类重试结果。

比较理由：重试动作、参数、单次约束和不重试非瞬态失败的语义均保留；非瞬态路径 edge7 直接去 archive.fetch，见 finding_6。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/inputs/2"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/1"

图位置："/edges/8"

## finding_8 · semantic · represented

原文要求：Any failed retry of fast.fetch goes to archive.fetch; successful retry returns summary.

当前表示：block_007 classify_fast_fetch_outcome 输入 result_006，输出 result_007，dispatch；edge9 retry succeeds -> block_011 return retry summary；edge10 retry fails -> block_008 archive.fetch。

比较理由：重试成功与失败的分支和后继与源文一致。

源文 `src_003` · `SKILL.md:11-11`：

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/outputs/0"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/edges/9"

图位置："/edges/10"

## finding_9 · semantic · represented

原文要求：After non-transient first failure or failed retry, call archive.fetch with source_id; call archive.fetch at most once and pass source_id as its only argument; never pass FAST_KEY to archive.fetch.

当前表示：block_008 opcode archive.fetch 输入 external_resource archive.fetch、result_001/source_id，输出 result_008；块级约束 at most once and source_id only；操作级约束 pass source_id only、do not pass FAST_KEY；edge11 进入 classify archive。

比较理由：归档调用只在此处一次，业务实参仅为 source_id，未包含 result_002/FAST_KEY；external_resource 为工具标识，不作为额外参数。

源文 `src_003` · `SKILL.md:11-11`：

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

源文 `src_003` · `SKILL.md:12-12`：

> 5. Call archive.fetch at most once and pass source_id as its only argument.

源文 `src_003` · `SKILL.md:15-15`：

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/constraints/0"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/outputs/0"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/0/constraints/1"

图位置："/blocks/block_008/instructions/1"

图位置："/edges/11"

## finding_10 · semantic · represented

原文要求：On archive.fetch success, return its summary; if archive.fetch fails, stop and return its error.

当前表示：block_009 classify_archive_fetch_outcome 输入 result_008，输出 result_009，dispatch；edge12 archive succeeds -> block_012 return archive summary；edge13 archive fails -> block_013 return archive error。

比较理由：归档成功和失败的分支及后继身份与源文一致。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

源文 `src_003` · `SKILL.md:14-14`：

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/outputs/0"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/edges/12"

图位置："/edges/13"

## finding_11 · semantic · represented

原文要求：On fast.fetch first success, return that response's summary unchanged, make no further fetch calls; before returning append final status to local status.txt.

当前表示：block_010 extract_summary_from_response 输入 result_004/output result_010；append_status_to_local_file 输入 local status.txt、result_005；return result_010；块级约束 success return unchanged/no further fetch，append 约束 before returning。

比较理由：第一尝试成功路径返回的是该成功响应的摘要 result_010，未继续重试或归档；返回前追加状态。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/constraints/0"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/outputs/0"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/inputs/0"

图位置："/blocks/block_010/instructions/1/inputs/1"

图位置："/blocks/block_010/instructions/1/constraints/0"

图位置："/blocks/block_010/instructions/2"

图位置："/blocks/block_010/instructions/2/inputs/0"

## finding_12 · semantic · represented

原文要求：On fast.fetch retry success, return that response's summary unchanged, make no further fetch calls; append final status before returning.

当前表示：block_011 extract_summary_from_response 输入 result_006/output result_011；append local status、result_007；return result_011；约束同成功返回和 append before returning。

比较理由：重试成功路径返回 result_006 对应摘要，未进入 archive.fetch；返回前追加状态。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/blocks/block_011/block_id"

图位置："/blocks/block_011/block_name"

图位置："/blocks/block_011/data_source_kind"

图位置："/blocks/block_011/constraints/0"

图位置："/blocks/block_011/instructions"

图位置："/blocks/block_011/instructions/0"

图位置："/blocks/block_011/instructions/0/inputs/0"

图位置："/blocks/block_011/instructions/0/outputs/0"

图位置："/blocks/block_011/instructions/1"

图位置："/blocks/block_011/instructions/1/inputs/0"

图位置："/blocks/block_011/instructions/1/inputs/1"

图位置："/blocks/block_011/instructions/1/constraints/0"

图位置："/blocks/block_011/instructions/2"

图位置："/blocks/block_011/instructions/2/inputs/0"

## finding_13 · semantic · represented

原文要求：On archive.fetch success, return that response's summary unchanged, make no further fetch calls; append final status before returning.

当前表示：block_012 extract_summary_from_response 输入 result_008/output result_012；append local status、result_009；return result_012；约束同成功返回和 append before returning。

比较理由：归档成功路径返回归档响应摘要，未继续调用工具；返回前追加状态。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/blocks/block_012/block_id"

图位置："/blocks/block_012/block_name"

图位置："/blocks/block_012/data_source_kind"

图位置："/blocks/block_012/constraints/0"

图位置："/blocks/block_012/instructions"

图位置："/blocks/block_012/instructions/0"

图位置："/blocks/block_012/instructions/0/inputs/0"

图位置："/blocks/block_012/instructions/0/outputs/0"

图位置："/blocks/block_012/instructions/1"

图位置："/blocks/block_012/instructions/1/inputs/0"

图位置："/blocks/block_012/instructions/1/inputs/1"

图位置："/blocks/block_012/instructions/1/constraints/0"

图位置："/blocks/block_012/instructions/2"

图位置："/blocks/block_012/instructions/2/inputs/0"

## finding_14 · semantic · represented

原文要求：If archive.fetch fails, stop and return its error; do not retry archive.fetch; append final status before returning.

当前表示：block_013 extract_error_from_response 输入 result_008/output result_013；append local status、result_009；return result_013；块级约束 stop/return error/no retry，append 约束 before returning。

比较理由：归档失败路径终止并返回归档错误，无 archive.fetch 重试；返回前追加状态。

源文 `src_003` · `SKILL.md:14-14`：

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/blocks/block_013/block_id"

图位置："/blocks/block_013/block_name"

图位置："/blocks/block_013/data_source_kind"

图位置："/blocks/block_013/constraints/0"

图位置："/blocks/block_013/instructions"

图位置："/blocks/block_013/instructions/0"

图位置："/blocks/block_013/instructions/0/inputs/0"

图位置："/blocks/block_013/instructions/0/outputs/0"

图位置："/blocks/block_013/instructions/1"

图位置："/blocks/block_013/instructions/1/inputs/0"

图位置："/blocks/block_013/instructions/1/inputs/1"

图位置："/blocks/block_013/instructions/1/constraints/0"

图位置："/blocks/block_013/instructions/2"

图位置："/blocks/block_013/instructions/2/inputs/0"

## finding_15 · semantic · represented

原文要求：Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow. Before returning from every success or failure path, append final status to local status.txt.

当前表示：graph-level constraints /constraints/0 和 /constraints/1 记录这两项全局要求；相应操作级/块级约束与 append 操作在各路径上支撑。

比较理由：两项全局约束均在 /constraints 中声明，并有相应操作级/块级约束与 append 操作支撑；未发现向 archive.fetch 传 FAST_KEY 或 diagnostic output 操作。

源文 `src_003` · `SKILL.md:15-15`：

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/constraints/0"

图位置："/constraints/1"

## finding_16 · context · represented

原文要求：源文前言、标题及受控记录中的块键、块 ID、名称标签、操作 ID 清单、空 metadata 等表示辅助信息；不是额外业务要求。

当前表示：受控记录包含 entry、各块 key/id/name/instructions 清单及 metadata_json；这些为定位/表示辅助，未用于替代业务步骤。

比较理由：这些字段不引入新的业务动作或条件；其上下文地位已说明。

源文 `src_001` · `SKILL.md:1-4`：

> name: source-fetch-with-fallback

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

图位置："/entry_block_id"

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1/metadata"

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1/metadata"

图位置："/blocks/block_010/instructions/2/metadata"

图位置："/blocks/block_011/block_id"

图位置："/blocks/block_011/block_name"

图位置："/blocks/block_011/instructions"

图位置："/blocks/block_011/instructions/0/metadata"

图位置："/blocks/block_011/instructions/1/metadata"

图位置："/blocks/block_011/instructions/2/metadata"

图位置："/blocks/block_012/block_id"

图位置："/blocks/block_012/block_name"

图位置："/blocks/block_012/instructions"

图位置："/blocks/block_012/instructions/0/metadata"

图位置："/blocks/block_012/instructions/1/metadata"

图位置："/blocks/block_012/instructions/2/metadata"

图位置："/blocks/block_013/block_id"

图位置："/blocks/block_013/block_name"

图位置："/blocks/block_013/instructions"

图位置："/blocks/block_013/instructions/0/metadata"

图位置："/blocks/block_013/instructions/1/metadata"

图位置："/blocks/block_013/instructions/2/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

尚无已保存的助手逐例复核。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
