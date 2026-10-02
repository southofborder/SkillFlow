# 001-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N01；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：836d34ef584eff7f9543661958c2d23614132db613fbaccf077fac57f7e50c56；源文 SHA-256：6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/001/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/001/annotation/result.json>)；本地审查页也可展开全文。

## finding_1_context · context · represented

原文要求：源文 frontmatter 与标题仅提供技能名称、描述和标题背景，不是业务要求。

当前表示：受控回述记录入口块 fact:/entry 和空 contexts fact:/contexts，并把各块名称/结构作为受控字段；没有把 frontmatter 名称、描述或标题作为业务步骤执行。

比较理由：这些源单元是背景/名称信息，不是条件、动作或数据要求；受控回述的入口和上下文声明说明了其上下文地位，且未引入替代业务要求。

源文 `src_001` · `SKILL.md:2-2`：

> name: conditional-notification

源文 `src_001` · `SKILL.md:3-3`：

> description: 根据事件记录的订阅状态、紧急标记和数值发送通知。

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2_read_events_schema · semantic · represented

原文要求：读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前表示：block_001 记录 read_events_json，输入 external_resource events.json（semantic_name 为 user-provided events.json），输出 result_001 event_records；块级声明约束列出全部记录字段；dispatch ir_002 作为固定控制终结操作，无额外业务输出。

比较理由：读取动作、对象 events.json、用户提供语义和记录字段 schema 均有对应记录；metadata 为空、dispatch 无输入均不改变该要求。

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

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

## finding_3_iteration · semantic · represented

原文要求：源文要求对记录逐条处理：读取后要能对每条记录做选择；选中则发送，未选中则跳过；全部处理完成后再写计数。源文未规定具体迭代实现。

当前表示：block_002 记录 get_next_event_record，输入 result_001 event_records，输出 result_002 current_record 和 result_003 has_more_records；dispatch ir_004 使用 result_003；由边控制 has_more_records true 进入选择、false 进入计数块。

比较理由：这是对逐条处理的具体迭代表达；get_next_event_record 与 has_more_records 是源文未规定的实现细节，不新增可观察业务结果，也未改变每条记录都要经过选择的要求。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 未选中的记录不调用 notify.send。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/outputs/1"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_002/instructions/1/metadata"

## finding_4_selection · semantic · represented

原文要求：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录；urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

当前表示：block_003 记录 evaluate_event_record_selection，输入 result_002 current_record，输出 result_004 is_selected；操作级声明约束逐字记录选择条件与豁免规则；dispatch ir_006 使用 result_004 选择分支。

比较理由：选择条件、urgent 与 value 的门槛关系、以及 opted_out 不可被 urgent 豁免均有明确声明；current_record 输入可承载 opted_out、urgent、value 字段，未发现条件对象或作用域错位。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:10-10`：

> 3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/metadata"

## finding_5_extract_fields_no_transform · semantic · represented

原文要求：对选中记录，接收对象取 recipient 字段；notify.send 的 body 直接取 summary 字段原值；字段取值要求不包含摘要生成、内容改写或额外格式转换。

当前表示：block_004 的 extract_event_notification_fields 输入 result_002 current_record，输出 result_005 recipient 与 result_006 summary；操作级声明约束记录字段取值不生成摘要、不改写、不额外格式转换，并记录 body 直接取 summary 原值；全局约束 fact:/constraints/3 重复该禁止性要求。

比较理由：提取操作仅产出 recipient 和 summary，没有产出或改写 access_token 或其他内容；约束与源文禁止的摘要生成、改写、格式转换一致。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/constraints/3"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/0/metadata"

## finding_6_notify_send · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取 recipient；body 直接取 summary 原值；未选中的记录不调用 notify.send；整份流程禁止将 access_token 字段发送给任何接收对象。

当前表示：全局约束 0-2 与 block_004 的 notify_send 操作记录：输入 external_resource notify.send、result_005 recipient、result_006 summary；操作级约束记录每条选中调用一次、接收对象取 recipient、body 取 summary 原值、禁止发送 access_token；无 access_token 作为 notify_send 输入；未选中由 is_selected false 边绕开该块。

比较理由：调用次数与选中条件相符，recipient 和 summary 的绑定分别来自同一条当前记录的提取结果，禁止项在全局和操作级均有声明，且没有额外发送 access_token 的数据路径。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 未选中的记录不调用 notify.send。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 整份流程禁止将 access_token 字段发送给任何接收对象。

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/1"

图位置："/blocks/block_004/instructions/1/inputs/2"

图位置："/blocks/block_004/instructions/1/constraints/0"

图位置："/blocks/block_004/instructions/1/constraints/1"

图位置："/blocks/block_004/instructions/1/constraints/2"

图位置："/blocks/block_004/instructions/1/constraints/3"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_004/instructions/2"

图位置："/blocks/block_004/instructions/2/metadata"

## finding_7_count_write · semantic · represented

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前表示：block_005 记录 count_processed_event_records，输入 result_001 event_records，输出 result_007 processed_count；write_count_to_file 输入 external_resource count.txt 与 result_007；块级和操作级声明约束记录处理完成后写入本地 count.txt；return ir_012 作为固定控制终结操作。

比较理由：计数结果和本地 count.txt 的写入对象均有绑定；控制边只在 has_more_records false 时进入该块，满足处理完成后写入的次序；external_resource 可以是本地文件。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

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

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_005/instructions/2"

图位置："/blocks/block_005/instructions/2/metadata"

## finding_8_control_edges · semantic · represented

原文要求：读取事件后，对每条记录进行选择；选中则发送通知，未选中不发送；全部处理完成后写计数。源文未规定具体迭代和分支结构。

当前表示：边记录 block_001->block_002；block_002->block_003 条件 has_more_records is true；block_002->block_005 条件 has_more_records is false；block_003->block_004 条件 is_selected is true；block_003->block_002 条件 is_selected is false；block_004->block_002 无条件。

比较理由：控制边覆盖了读取后逐条选择、选中发送、未选中跳过、继续取下一条、无更多记录后进入计数；具体迭代与分支结构是实现细节，不与源文冲突。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 未选中的记录不调用 notify.send。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

## finding_9_data_links · semantic · represented

原文要求：源文要求读取结果用于逐条处理，当前记录用于选择和提取字段，选择结果控制是否发送，提取出的 recipient/summary 用于 notify.send，计数结果写入 count.txt。

当前表示：links 按实际 ID 记录：result_001 由 read_events_json 定义并用于 get_next_event_record、count_processed_event_records；result_002 由 get_next_event_record 定义并用于 evaluate_event_record_selection、extract_event_notification_fields；result_003 用于 dispatch；result_004 用于 dispatch；result_005/result_006 用于 notify_send；result_007 用于 write_count_to_file。

比较理由：各结果身份、定义位置和使用位置按实际 identifier 绑定，未发现首次尝试/重试/回退结果互换、对象错绑或缺失绑定。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/1"

图位置："/blocks/block_004/instructions/1/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：836d34ef584eff7f9543661958c2d23614132db613fbaccf077fac57f7e50c56

助手已复核完整源文、末图、有效核对及全部 12 条标注；关键流程未发现明显漏转，但安全主体推断仍存在依据不足。不是用户人工确认。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 图保留用户 events.json 来源、七字段声明、opted_out 与 urgent/value 联合条件、选中逐条发送、recipient/summary 绑定、禁传 access_token 和处理后写 count.txt；没有把禁止声明补成遮蔽操作。核对器初轮通过与关键流程观察一致。
- 处理条数没有被额外要求为发送成功条数；源文没有规定这层口径。保留图中实际计数表达，不凭更强业务假设判错。
- ir_001 的 fs_read 及按 EM02 的工具结果默认 model_observe 有相应证据；不能据此推导 events.json 之外的容器或敏感数据集合。
- ir_005 条件判断与 ir_007 字段选择被直接归给 llm，并据此标 model_observe，但源文、CFG 和固定规则未明确排除本地运行时执行。引用 EM03 的“内容实际由模型处理”不能反过来证明这个前提。建议将具体执行者及相应新增观察效果列为待澄清，或在后续执行模型中统一约定；本轮不改模型标签。
- ir_003/ir_010 同类选择、计算动作却推断为 agent_runtime，显示 actor 归属存在不一致的推断边界；程序证据匹配通过不能解决该问题。
- notify.send 的 sink/发送、count.txt 的 fs_write、纯 dispatch 和空 return 未硬贴 transform/user_output，符合本例记录。没有通信返回内容的证据，不强行增加 net_receive。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
