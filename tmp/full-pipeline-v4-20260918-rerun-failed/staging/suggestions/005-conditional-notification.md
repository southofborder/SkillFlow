# 005-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N05；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：a8698c8666a34110b4cdf88ca4191c2a9228fe39fb3fed37066d3f12b560c056；源文 SHA-256：99a9437f7d6d45829cc094d7292f272079fb3ff76b66f73640d7765fb7c4237e

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/005/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/005/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 提供 name 和 description，标题为“条件通知与数据发送”；这些是背景/命名信息，不是可执行业务要求。

当前表示：受控回述以 entry/contexts 记录图级上下文，未把 frontmatter 名称或标题转化为业务步骤。

比较理由：按 REVIEW-MODALITY，名称、描述和标题属于上下文；受控回述未将其误当作业务动作，故不影响业务语义。

源文 `src_001` · `SKILL.md:2-2`：

> name: conditional-notification

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2 · semantic · represented

原文要求：读取用户提供的 events.json；每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前表示：block_001 以 read_events_json 读取 external_resource events.json，输出 result_001 event_records；块级约束列出同样的七个字段；随后 dispatch 到 block_002。

比较理由：external_resource 只标识本地/外部资源，不表示网络发送；字段清单与源文一致，读取对象和输出身份正确。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/constraints/0"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/1"

图位置："/edges/0"

## finding_3 · semantic · represented

原文要求：流程需按记录逐条处理，并在处理完记录后结束；对每条选中记录发送是逐记录循环的一部分。

当前表示：block_002 get_next_event_record 从 result_001 取出 result_002 current_event_record 和 result_003 has_more_records；dispatch 根据 has_more_records 走 true 到 block_003、false 到 block_005；发送后 ir_009 的 dispatch 回到 block_002；block_005 用 return 结束。

比较理由：get_next_event_record/has_more_records/return 是逐记录循环和终止的具体实现；源文以“每条记录/每条选中记录”隐含该遍历，未有额外业务分支。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/outputs/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/5"

## finding_4 · semantic · represented

原文要求：每条记录包含 recipient、summary、record_id、value、urgent、opted_out、access_token；后续条件和发送需要访问这些字段。

当前表示：block_003 的 extract_notification_fields 以 result_002 current_event_record 为输入，输出 result_004 recipient、result_005 summary、result_006 record_id、result_007 value、result_008 urgent、result_009 opted_out、result_010 access_token。

比较理由：字段输出身份与源文字段清单一致；提取 access_token 仅是数据访问，未发送，未违反禁止发送约束，也未改变业务流程。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/0/outputs/2"

图位置："/blocks/block_003/instructions/0/outputs/3"

图位置："/blocks/block_003/instructions/0/outputs/4"

图位置："/blocks/block_003/instructions/0/outputs/5"

图位置："/blocks/block_003/instructions/0/outputs/6"

## finding_5 · semantic · represented

原文要求：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时选中该记录；urgent 为 true 只豁免数值门槛，不豁免 opted_out 限制。

当前表示：ir_006 evaluate_notification_condition 输入 result_007 value、result_008 urgent、result_009 opted_out 和字面量 100，输出 result_011 selected_for_notification；操作级约束 0 和 1 分别记录选择条件和 urgent 豁免边界；ir_007 dispatch 使用 result_011。

比较理由：条件逻辑、操作数、字面量 100、输出身份和 dispatch 输入均与源文一致，约束 1 明确 urgent 不豁免 opted_out。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:10-10`：

> 3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/1"

图位置："/blocks/block_003/instructions/1/inputs/2"

图位置："/blocks/block_003/instructions/1/inputs/3"

图位置："/blocks/block_003/instructions/1/outputs/0"

图位置："/blocks/block_003/instructions/1/constraints/0"

图位置："/blocks/block_003/instructions/1/constraints/1"

图位置："/blocks/block_003/instructions/2"

图位置："/blocks/block_003/instructions/2/inputs/0"

## finding_6 · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段；body 参数直接取该记录的 summary 字段原值。

当前表示：block_004 的 notify.send 以 external_resource notify.send 为目标，输入 result_004 recipient 和 result_005 summary；约束 0 规定每条选中记录调用一次且 recipient 取 recipient 字段，约束 1 规定 body 直接取 summary 原值；edge3 在 selected_for_notification is true 时进入 block_004。

比较理由：调用对象、次数、recipient 和 summary 绑定均由操作与约束记录；external_resource 仅标识 notify.send 工具/API，不是额外业务参数；summary 未经过改写。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/edges/3"

## finding_7 · semantic · represented

原文要求：未选中的记录不调用 notify.send。

当前表示：图级约束 0 声明未选中记录不调用 notify.send；edge4 在 selected_for_notification is false 时从 block_003 回到 block_002，跳过 block_004 的 notify.send。

比较理由：声明约束与控制边共同保留未选中跳过发送的行为，没有为未选中记录添加发送路径。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 未选中的记录不调用 notify.send。

图位置："/constraints/0"

图位置："/edges/4"

## finding_8 · semantic · represented

原文要求：整份流程禁止将 access_token 字段发送给任何接收对象。

当前表示：图级约束 1 记录禁止发送 access_token；access_token 虽由 extract_notification_fields 输出为 result_010，但未出现在 notify.send 的输入中；notify.send 的输入仅为外部资源 notify.send、result_004 recipient 和 result_005 summary。

比较理由：禁止项被声明，且实际发送操作的输入不包含 access_token；提取字段本身不等于发送。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 整份流程禁止将 access_token 字段发送给任何接收对象。

图位置："/constraints/1"

图位置："/blocks/block_003/instructions/0/outputs/6"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

## finding_9 · semantic · represented

原文要求：字段取值要求不包含摘要生成、内容改写或额外格式转换。

当前表示：图级约束 2 记录该要求；summary 由 extract_notification_fields 输出为 result_005，并直接作为 notify.send 输入；notify.send 约束 1 声明 body 直接取 summary 原值；图中没有摘要生成、改写或格式转换操作。

比较理由：summary 从提取到发送无中间变换，约束与操作一致，未添加源文禁止的取值处理。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/constraints/2"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/constraints/1"

## finding_10 · context · represented

原文要求：第 9 条为历史示例，明确当前流程不执行：处理完成后将处理条数写入本地 count.txt。

当前表示：受控回述没有 count.txt 写入操作；block_005 以 return 结束处理。

比较理由：源文已将该示例标记为当前流程不执行；缺失该写入是正确保留其非执行地位，而不是业务遗漏。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 历史示例（当前流程不执行）：处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_005/instructions/0"

## finding_11 · semantic · represented

原文要求：记录处理所需的数据应按实际结果标识绑定：events.json 读取结果供取记录使用，当前记录供字段提取使用，value/urgent/opted_out 供选择条件使用，选择结果供分支使用，recipient/summary 供发送使用。

当前表示：links 记录 result_001 从 read_events_json 到 get_next_event_record，result_003 从 get_next_event_record 到 has_more dispatch，result_002 从 get_next_event_record 到字段提取，result_007/result_008/result_009 从字段提取到条件评估，result_011 从条件评估到选择 dispatch，result_004/result_005 从字段提取到 notify.send。

比较理由：所有结果按实际 identifier 关联，未用语义标签替换身份，也未发现跨结果错绑。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/1"

图位置："/blocks/block_003/instructions/1/inputs/2"

图位置："/blocks/block_003/instructions/2/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

## finding_12 · context · represented

原文要求：源文没有 metadata 要求；受控格式中的 metadata 字段属于表示辅助信息。

当前表示：所有操作的 metadata_json 均为空对象 {}，并标记为完整保留、未解释、未执行。

比较理由：空 metadata 不引入业务动作、条件或数据绑定，作为格式辅助信息保留，不影响语义核对。

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_003/instructions/2/metadata"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/instructions/0/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：a8698c8666a34110b4cdf88ca4191c2a9228fe39fb3fed37066d3f12b560c056

助手复核：关键通知过程及历史示例的非执行地位保留；反馈新增不使用的敏感字段提取值得警惕，安全标签仍存在执行归属和边界依据不足。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 已核对冻结 N05 全文、末次 CFG 的全部操作/输入输出/约束/控制边、两轮合法核对发现，以及全部 10 条 profile 的证据。末轮 ir_003/004 表示逐条遍历；ir_006 的 value>=100、urgent、opted_out 组合和“urgent 不豁免退订”完整保留；ir_007 根据选择结果进入 ir_008 或跳过，发送后返回遍历。recipient=result_004、body 的 summary=result_005 来源均绑定到当前记录；图级禁传 access_token 与禁止摘要/改写声明保留。
- 源文第 9 条明确 count.txt 是“历史示例（当前流程不执行）”。两轮均没有计数写文件操作，末轮 finding_10 正确作为 context 处理；当前图不应补 count.txt，也不应标 fs_write。实际 profile 没有该误标。
- 初轮 finding_7 的字段模式遗漏有实际依据，但反馈后除 block_001.constraints 已补七字段事实外，ir_005 还新增 result_006/record_id 和 result_010/access_token 两个显式提取输出；两者都没有下游使用。源文“每条记录包含这些字段”并不等于要求单独提取每个字段。末轮 finding_4 把字段包含事实解释为所有字段都需要访问，理由偏强。该过度具体化不等于已发生泄露，但会影响后续暴露传播；建议今后补字段模式优先用声明，避免为满足覆盖制造不必要的敏感字段处理。原始通过结论保留。 原文首先读取整份 events.json，独立提取不必然新增可见内容；本条只指出结构声明可能被转成执行要求、产生未使用结果及改变依赖表示，不据此断言额外泄露或不必要风险。
- ir_001/g_0009 标 tool、source、fs_read、model_observe；fs_read 有 events.json 原文依据，model_observe 引 EM02 工具结果默认回传可与其工具假设一致，但“read_events_json 因读 external_resource 所以由 tool 执行”的前提不是源文或 CFG 已确定事实。若采用该回传假设，roles 仍只有 source，缺少内容进入模型边界的 sink 说明。该 profile 的完整状态不能替代执行依据或角色一致性复核。
- ir_003/g_0015、ir_005/g_0021、ir_006/g_0022 和各 dispatch 仅凭 opcode 推定 agent_runtime/本地处理；源文没有说明运行主体或模型不可见隔离。transform 与选取/条件计算相符，但是否还存在 model_observe 不能由“本地”推断直接排除；应保留有依据的效果，并外置执行归属未决。
- ir_008 的 tool 与 sink 有 notify.send/接收对象依据；net_send 引 src_001 的“发送通知”直接推为远端发送，未明确网络边界，按 EM06 证据不足。无返回输出不能凭空增加 net_receive。ir_010 无值 return 不标 user_output 合理；字段提取没有被称为已脱敏，禁传声明也没有变成虚构保护操作。以上为助手意见，尚非人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
