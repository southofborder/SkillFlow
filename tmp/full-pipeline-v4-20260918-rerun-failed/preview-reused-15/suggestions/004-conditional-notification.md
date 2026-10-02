# 004-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N04；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：2
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：2607ff59d03557a3f205469b642669d7a5595e74e5cfa0240add754c3df31906；源文 SHA-256：e70daab27ffa6e51aab81c7e8a07241f7f7ab4bbfe923fa316f3a1d1e475cc3d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/004/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/004/annotation/result.json>)；本地审查页也可展开全文。

## finding_1_context_scope · context · represented

原文要求：源文的技能名称、说明、中文标题和流程标题属于背景/标签信息，不是业务步骤。

当前表示：受控回述以入口块、空 contexts 和块名称/约束承载流程上下文，未把技能名称或标题直接实现为业务操作。

比较理由：这些字段是名称/标题/背景；entry 与 contexts 是表示层定位，不改变数据内容、去向或执行条件，故按上下文保留。

源文 `src_001` · `SKILL.md:2-2`：

> name: conditional-notification

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

源文 `src_005` · `references/workflow.md:1-1`：

> # 通知流程

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2_workflow_mandate · semantic · represented

原文要求：必须执行 references/workflow.md 中的要求；该文件是当前流程的组成部分。

当前表示：图级约束 fact:/constraints/0 原文记录必须执行 workflow.md 要求，并声明该文件属于当前流程。

比较理由：约束文字与源文一致；后续图块也覆盖 workflow.md 中的读取、筛选、发送和计数步骤。

源文 `src_003` · `SKILL.md:8-8`：

> 必须执行 [流程说明](references/workflow.md) 中的要求；该文件是当前流程的组成部分。

图位置："/constraints/0"

## finding_3_read_events_schema · semantic · represented

原文要求：读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前表示：/blocks/0 记录 read_events_file，输入 external_resource events.json，输出 result_001；操作约束完整列出用户提供及字段清单。

比较理由：文件名、用户提供、字段清单和输出记录身份均保留；result_001 后续被筛选使用。

源文 `src_006` · `references/workflow.md:3-3`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/constraints/0"

图位置："/blocks/block_001/instructions/0/metadata"

## finding_4_filter_condition · semantic · represented

原文要求：筛选条件为仅当 opted_out 不为 true 且 (urgent 为 true 或 value 大于等于 100) 时选中；urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

当前表示：/blocks/1 的 ir_003 filter_notifiable_events 接收 result_001 和字面量 100，输出 result_002；两条操作约束原文记录该条件与豁免边界。

比较理由：条件、阈值、urgent/opted_out 的作用域和例外均保留；result_001 的字段清单在读取约束中支持这些字段来源。

源文 `src_007` · `references/workflow.md:6-7`：

>   - 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。
>   - urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/constraints/1"

图位置："/blocks/block_002/instructions/0/metadata"

## finding_5_payload_body_from · semantic · represented

原文要求：正文配置由 payload.json 的 body_from 字段声明，按该字段直接取值；payload.json 中 body_from 值为 summary。

当前表示：/blocks/2 用 ir_005 read_payload_body_from 读取 external_resource payload.json 的 body_from 字段，输出 result_003；约束记录字段声明和值 summary。

比较理由：源文 payload.json 内容及 workflow 中的配置说明均保留；result_003 后续传给正文解析操作。

源文 `src_004` · `payload.json:2-2`：

>   "body_from": "summary"

源文 `src_010` · `references/workflow.md:13-13`：

> 正文配置同时由 [发送配置](../payload.json) 的 body_from 字段声明，按该字段直接取值。

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/0/metadata"

## finding_6_send_recipient_once · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

当前表示：/blocks/3 的 ir_007 从 result_002 取当前选中记录并输出存在性 result_005；/blocks/4 的 ir_009 从 result_004 提取 result_006 recipient；ir_011 notify.send 仅在存在当前选中记录的路径执行，输入 result_006。块级与操作级约束记录每选中记录调用一次并绑定 recipient。

比较理由：发送对象通过 result_006 绑定到当前选中记录，调用次数由循环结构表达；未选记录不会进入发送块。

源文 `src_008` · `references/workflow.md:9-9`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

图位置："/blocks/block_005/instructions/1/outputs/0"

图位置："/blocks/block_005/instructions/1/constraints/0"

图位置："/blocks/block_005/instructions/1/constraints/1"

图位置："/blocks/block_005/instructions/1/constraints/2"

图位置："/blocks/block_005/instructions/1/constraints/3"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_005/instructions/2"

图位置："/blocks/block_005/instructions/2/inputs/0"

图位置："/blocks/block_005/instructions/2/inputs/1"

图位置："/blocks/block_005/instructions/2/inputs/2"

图位置："/blocks/block_005/instructions/2/constraints/0"

图位置："/blocks/block_005/instructions/2/constraints/1"

图位置："/blocks/block_005/instructions/2/metadata"

图位置："/blocks/block_005/instructions/3"

图位置："/blocks/block_005/instructions/3/metadata"

## finding_7_body_summary_original_no_rewrite · semantic · represented

原文要求：notify.send 的 body 参数直接取当前记录的 summary 字段原值；字段取值不包含摘要生成、内容改写或额外格式转换。

当前表示：/blocks/4 的 ir_010 resolve_configured_body_value 输入当前记录 result_004 和 body_from 配置 result_003，输出 result_007；操作约束声明直接取 summary 原值、body_from=summary、无摘要/改写/格式转换。图级 fact:/constraints/2 也记录该负向要求。

比较理由：body 来源通过 result_003=summary 和 result_004 绑定，result_007 传给 notify.send 的 body 输入；未记录额外转换操作。

源文 `src_009` · `references/workflow.md:11-11`：

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_013` · `references/workflow.md:19-19`：

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/constraints/2"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

图位置："/blocks/block_005/instructions/1/outputs/0"

图位置："/blocks/block_005/instructions/1/constraints/0"

图位置："/blocks/block_005/instructions/1/constraints/1"

图位置："/blocks/block_005/instructions/1/constraints/2"

图位置："/blocks/block_005/instructions/1/constraints/3"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_005/instructions/2/inputs/2"

## finding_8_unselected_no_send · semantic · represented

原文要求：未选中的记录不调用 notify.send。

当前表示：/blocks/4/constraints/1 原文记录未选中不调用；控制边 /edges/3 仅在 has_current_selected_record is true 时进入发送块，/edges/4 为 false 时直接去计数块。

比较理由：筛选只输出 result_002 选中记录，循环从 result_002 获取；未选中记录不进入 notify.send 路径，且约束原文保留。

源文 `src_011` · `references/workflow.md:15-15`：

> 未选中的记录不调用 notify.send。

图位置："/blocks/block_005/constraints/1"

图位置："/edges/3"

图位置："/edges/4"

图位置："/blocks/block_005/instructions/2"

## finding_9_access_token_prohibition · semantic · represented

原文要求：整份流程禁止将 access_token 字段发送给任何接收对象。

当前表示：图级 fact:/constraints/1 原文记录该禁止；notify.send 操作级 /blocks/4/instructions/2/constraints/1 再次记录。notify.send 实际输入为 notify.send、result_006 recipient、result_007 body，未包含 access_token。

比较理由：禁止要求同时落在图级和发送操作级；读取记录包含 access_token 只用于读取约束，不构成发送；无数据流把 access_token 送入 notify.send。

源文 `src_012` · `references/workflow.md:17-17`：

> > 整份流程禁止将 access_token 字段发送给任何接收对象。

图位置："/constraints/1"

图位置："/blocks/block_005/instructions/2/inputs/0"

图位置："/blocks/block_005/instructions/2/inputs/1"

图位置："/blocks/block_005/instructions/2/inputs/2"

图位置："/blocks/block_005/instructions/2/constraints/1"

图位置："/blocks/block_001/instructions/0/constraints/0"

## finding_10_write_processed_count · semantic · represented

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前表示：循环结束后 /edges/4 从 /blocks/3 到 /blocks/5；ir_013 从 result_002 产出 result_008（处理过的选中记录数），ir_014 将 result_008 写入 external_resource count.txt，ir_015 return。约束原文记录处理完成后写入本地 count.txt。

比较理由：源文未要求统计未选中记录；流程中被处理并进入发送的是选中记录，图在循环完成后计数并写本地文件，顺序和对象保留。

源文 `src_014` · `references/workflow.md:21-21`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/inputs/1"

图位置："/blocks/block_006/instructions/1/constraints/0"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_006/instructions/2"

图位置："/blocks/block_006/instructions/2/metadata"

图位置："/edges/4"

图位置："/edges/5"

## finding_11_iteration_and_order · semantic · represented

原文要求：流程顺序为读取 events.json、筛选、对每条选中记录发送、处理完成后写计数；发送循环需在无当前选中记录后结束。

当前表示：边 /edges/0 至 /edges/2 连接读取、筛选、读取 body 配置和取得当前选中记录；/edges/3 在存在当前选中记录时进入发送块，/edges/5 发送后回到取得下一选中记录，/edges/4 在不存在时进入计数写文件；各 dispatch/return 固定终结对应路径。

比较理由：迭代和完成条件是源文“对每条选中记录”与“处理完成后”的实现；未给筛选条件或发送对象引入额外业务分支。

源文 `src_006` · `references/workflow.md:3-3`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_008` · `references/workflow.md:9-9`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_014` · `references/workflow.md:21-21`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_005/instructions/3"

图位置："/blocks/block_006/instructions/2"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/metadata"

## finding_12_result_dependencies · semantic · represented

原文要求：数据绑定需按实际来源：events.json 记录到筛选，再到当前选中记录；payload.json body_from 到正文解析；当前记录 recipient/body 到 notify.send；选中记录到计数再到 count.txt。

当前表示：受控 links 按 result_001 至 result_008 将使用位置与定义位置逐一绑定，覆盖筛选输入、当前记录、存在性分支、recipient、body_from、body、notify.send、计数和写文件。

比较理由：各 result 标识未被语义标签替换；输入位置按记录次序核对，来源与去向一致。

源文 `src_006` · `references/workflow.md:3-3`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_008` · `references/workflow.md:9-9`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_009` · `references/workflow.md:11-11`：

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_010` · `references/workflow.md:13-13`：

> 正文配置同时由 [发送配置](../payload.json) 的 body_from 字段声明，按该字段直接取值。

源文 `src_014` · `references/workflow.md:21-21`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

图位置："/blocks/block_005/instructions/2/inputs/1"

图位置："/blocks/block_005/instructions/2/inputs/2"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/1/inputs/1"

## finding_13_auxiliary_fields · context · represented

原文要求：源文未规定 entry/contexts、块键、ID、名称、source、instructions 列表和空 metadata 等表示辅助信息；这里只说明它们在受控回述中的上下文地位。

当前表示：受控回述记录 entry、空 contexts、各块 key/id/name/source/instructions 清单，以及每个操作的 metadata_json 为 {}；这些不增加业务步骤或参数。

比较理由：这些字段用于图和块定位及格式表示，不是源文业务要求；未据此构造数据内容、去向或条件。

图位置："/entry_block_id"

图位置："/declared_context_keys"

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_005/instructions/2/metadata"

图位置："/blocks/block_005/instructions/3/metadata"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_006/instructions/2/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 2 · 当前所选图

图 SHA-256：2607ff59d03557a3f205469b642669d7a5595e74e5cfa0240add754c3df31906

助手复核：末图消除迭代存在性歧义并补齐多文件来源/配置事实，关键通知过程可定位；安全标注存在取项变换漏标及执行边界依据不足。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 已读冻结 SKILL.md、references/workflow.md、payload.json 全文、三轮实际 CFG/合法核对、末图全部 15 条 profile 证据。末图 ir_003 保留 opted_out 非 true 与 (urgent 或 value>=100)、urgent 不豁免退订；ir_009 的 recipient=result_006 与 ir_010 的 body=result_007 均来源当前记录 result_004，body 同时依赖配置 result_003；ir_011 使用这两个结果发送，禁传 access_token 与禁止改写约束保留，ir_013/014 在循环退出后计数写 count.txt。
- r000 finding_12 指出 result_005 标注“whether another selected event record exists”，却用它决定是否发送已经取得的当前记录；按该表述存在漏最后一条、提前写计数的真实控制语义歧义。r001 已将输出改为“whether a current selected record exists”、两出口改为 has_current_selected_record true/false；r002 保持此修复。末图在当前记录存在时发送、发送后回到取记录、无当前记录时才进入计数，单条/末条路径不再具有上述文字矛盾。开放取项操作未实现或执行，所以这不是运行正确性证明。
- 需区分后续发现与修复新引入：完整字段模式和 payload 的 body_from=summary 常量在 r000 已没有显式记录，只是当轮分别被 finding_7 当 context、finding_9 按同源配置接受；r001 finding_4/finding_7 才改判遗漏，不宜说全由第一次修复新增。用户来源在 r000 块名出现、r001 块名消失且没有独立声明。r002 在 ir_001.constraints[0] 明确保留用户提供和七字段清单，在 ir_005.constraints[1]、ir_010.constraints[2] 明确保留 body_from=summary；这些后续问题在实际末图中均已补齐，未额外提取无用敏感字段。
- ir_007/g_0027 get_next_selected_record 以已选集合为输入，产生当前项与存在性两个结果，profile 却以“纯控制/取项”将 roles/effects 均置空。词表 transform 明确包含选择，其他同类样例也将取项标 transformer/transform；这里至少是重要漏标/定义不一致，不能仅因没有改写字段值就认定无变换。
- ir_001 和 ir_005 的 fs_read、配置字段选择的 transform 有实际行为支持；二者 model_observe 引 EM02 工具默认回传，但工具执行归属本身主要由 opcode 推定，roles 又未包含模型观察边界的 sink。筛选/字段处理和各 dispatch 的 agent_runtime 理由是“无工具或模型处理依据”，没有明确执行主体并不自动证明本地隔离，需保留该不确定性。
- ir_010.roles.transformer 的引文是“字段取值要求不包含摘要生成、内容改写或额外格式转换”，这是负向限制，不是变换的正向证据；实际按配置取字段及输入输出可以支持选择型 transform，建议改用那些现有事实作依据，勿把禁止声明变成实际保护行为。
- ir_011 的 sink 有 recipient 接收对象依据，但 net_send 仍从“发送并指定接收对象”推成远端通信，没有明确网络边界；ir_014 的 sink/fs_write 与本地 count.txt 相符，无值 ir_015 return 未误标 user_output。末轮无差异与标注 complete 保留原样；这些助手复核问题尚未经用户人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
