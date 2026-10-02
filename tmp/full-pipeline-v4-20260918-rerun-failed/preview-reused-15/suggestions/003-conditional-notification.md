# 003-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N03；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：457d8b9416e68297094ffa133a82f34e3690e7512f0b3b69ef2ea0496a5f0646；源文 SHA-256：47b037eb9c5d2aa533e65def07ccb19ef077955580367f358c28030baf7f9a8d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/003/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/003/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 的 name、description 和标题是背景/命名信息，不是可执行业务步骤。

当前表示：受控回述未把 conditional-notification 或“条件通知与数据发送”记录为操作、条件或约束；业务内容由各块和约束承载。

比较理由：src_001 和 src_002 属于上下文和标题；未发现受控回述将其转成额外业务步骤，故按上下文保留处理。

源文 `src_001` · `SKILL.md:2-2`：

> name: conditional-notification

源文 `src_001` · `SKILL.md:3-3`：

> description: 根据事件记录的订阅状态、紧急标记和数值发送通知。

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

## finding_2 · context · represented

原文要求：源文没有要求 entry 或 contexts 键；这些是 IR 结构声明。

当前表示：受控回述声明 fact:/entry 指向 /entry/block_001，并声明 fact:/contexts 为空列表；未记录任何上下文键。

比较理由：entry/contexts 属于 IR 容器和结构辅助信息，不是源文业务步骤，也未引入额外业务行为。

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_3 · semantic · represented

原文要求：读取用户提供的 events.json；每条记录包含 recipient、summary、record_id、value、urgent、opted_out、access_token 字段。

当前表示：block_001 记录 source=external，ir_001 opcode=read_events_json，输入 external_resource events.json，输出 result_001/events_records；操作级声明约束逐字记录读取用户提供的 events.json 及七个字段。块 key/id/name/instructions 和空 metadata 仅作结构/容器记录。

比较理由：源文要求的输入资源、字段清单和读取动作均可在受控回述中定位；未发现对记录内容做摘要、改写或额外转换的额外操作。

源文 `src_003` · `SKILL.md:10-10`：

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

## finding_4 · semantic · represented

原文要求：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录；urgent 为 true 只豁免数值门槛，不豁免 opted_out 限制。

当前表示：block_002 记录 ir_003 opcode=select_eligible_event_records，输入 result_001，输出 result_002/eligible_events；操作级声明约束逐字记录选择条件和 exception。边 block_001→block_002 无条件文字，条件由选择操作约束承载。结果引用 link 将 result_001 绑定到该输入。

比较理由：选择条件、例外以及输入来源 result_001 均已保留；未发现相反条件。边无条件是结构性记录，不表示条件恒真，因为条件已在操作级约束声明。

源文 `src_003` · `SKILL.md:11-11`：

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:12-12`：

> urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/constraints/1"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/edges/0"

## finding_5 · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段；body 参数直接取 summary 字段原值；未选中的记录不调用 notify.send。

当前表示：block_003 记录 ir_005 opcode=notify.send，输入 result_002/eligible_events 和 external_resource notify，无输出；操作级声明约束逐字记录每条选中记录调用一次、接收对象取 recipient、body 取 summary 原值、未选中不调用。结果引用 link 将 result_002 绑定到该输入。实际操作输入列表没有单独列出 recipient/summary 操作数；该绑定只以声明约束出现，按 IR-DECLARATION 不视为已实现的输入绑定。

比较理由：源文的发送对象范围、调用次数、接收对象、body 原值和跳过规则均以操作级声明约束保留；notify 资源标识与 notify.send 动作一致。未发现新增接收对象或正文转换要求。

源文 `src_003` · `SKILL.md:13-13`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:14-14`：

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_003` · `SKILL.md:15-15`：

> 未选中的记录不调用 notify.send。

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/0/constraints/2"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/edges/1"

## finding_6 · semantic · represented

原文要求：整份流程禁止将 access_token 字段发送给任何接收对象；字段取值要求不包含摘要生成、内容改写或额外格式转换。

当前表示：图级声明约束 fact:/constraints/0 和 fact:/constraints/1 逐字记录这两项全局限制，作用域为整份流程/字段取值。

比较理由：两项全局禁止/限制均在受控回述的图级约束中保留，未发现对 access_token 的发送操作或摘要生成/改写/格式转换操作。

源文 `src_003` · `SKILL.md:16-16`：

> 整份流程禁止将 access_token 字段发送给任何接收对象。

源文 `src_003` · `SKILL.md:17-17`：

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/constraints/0"

图位置："/constraints/1"

## finding_7 · semantic · represented

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前表示：block_003 的 notify.send 后经 edge1→block_004；block_004 记录 ir_007 opcode=count_processed_event_records，输入 result_002/eligible_events，输出 result_003/processed_count；block_005 记录 ir_009 opcode=write_count_to_file，输入 result_003 和 external_resource count.txt，操作级声明约束逐字记录处理完成后将处理条数写入本地 count.txt。结果引用 links 将 result_002 绑定到计数、result_003 绑定到写入。边 block_003→block_004 和 block_004→block_005 无额外条件。

比较理由：处理完成后写入、处理条数来源、写入目标 count.txt 均在受控回述中可定位。计数操作是写入处理条数的具体实现，未改变写入目标或后置顺序。源文未规定失败/重试语义，受控回述也未增加此类条件。

源文 `src_003` · `SKILL.md:18-18`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/edges/2"

图位置："/edges/3"

## finding_8 · context · represented

原文要求：源文没有要求 dispatch 或 return 操作；它们是 IR 控制终结记录。

当前表示：受控回述在各块末尾记录 dispatch：block_001/ir_002、block_002/ir_004、block_003/ir_006、block_004/ir_008；block_005 记录 return/ir_010，均无 inputs/outputs。

比较理由：dispatch/return 是固定控制终结操作，不产生源文业务步骤，也未携带额外返回值或输出；不应判为新增业务行为。

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_005/instructions/1"

## finding_9 · context · represented

原文要求：源文没有要求 metadata 或空 source 标记等 IR 结构字段。

当前表示：各操作的 metadata_json 均为空 {}，block_001 后各块 source 为未记录；这些是 IR 容器/嵌入内容字段，未表达额外业务行为。

比较理由：metadata 和 source 标记属于表示辅助信息；未发现其中嵌入任何源文外业务指令或数据绑定。

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/instructions/1/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 历史轮次，不能作为当前图结论

图 SHA-256：34d961b3fdafc4996ca1c56f1e31deefa574ca02eeee2790be9d4bdb8e73a696

助手对初轮修复依据的局部复核：来源/字段遗漏有依据，另有一项疑似命名误报；尚不是末次图验收。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- finding_2 指出读取来源及记录字段模式未完整记录，尤其 record_id，在初轮实际 CFG 中有缺口。
- finding_5 仅因 opcode notify_send 与源文 notify.send 不同判 internal_conflict；block_003 名称以及 ir_005 同一操作约束均明确 notify.send，资源 notify 也属于该工具。开放操作名允许合理抽象，点号与下划线差异本身不足以证明行为矛盾。建议视作疑似误报，不能把它作为已证实业务错误。
- 原始判断及触发的后续重新提取仍保留。最终通过不能抹去这项初轮判断问题；需要另行复核末次图。

### 修复轮次 1 · 当前所选图

图 SHA-256：457d8b9416e68297094ffa133a82f34e3690e7512f0b3b69ef2ea0496a5f0646

助手复核：末图保留关键通知语义但采用集合级发送抽象；初轮存在命名误报，安全标注的 actor/model_observe 与角色一致性有重要疑点。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 检查范围为冻结 N03 表格全部要求、末轮完整 CFG/受控事实、两轮合法核对与全部 10 条 profile 的证据。ir_001 操作约束补齐用户来源和七字段模式；ir_003 保留完整筛选/例外；ir_005 以 eligible_events 为整体依赖，其三条约束保留每条一次、recipient、summary 原值、未选中不发送；ir_007→ir_009 保留处理后计数写 count.txt。没有依据判定丢失这些声明语义。
- 末轮 finding_5 已如实承认 recipient/summary 没有独立输入、绑定只在声明中；图无显式迭代边，逐条调用也由该操作约束承载。这是集合级开放操作抽象的边界，不能据通过推断每记录次数已被运行证明，更不能在后续传播中把 eligible_events 整体依赖悄悄缩成两个字段或把禁传声明当筛除 access_token 的实际动作。
- 初轮 finding_5 因 notify_send 与 notify.send 字面不同判 internal_conflict，初轮块名和同一操作约束已明确 notify.send，属于疑似命名误报；末轮改为点号形式不能反证原图确有业务冲突。原有第 0 轮局部复核意见保留。
- ir_003/g_0015 的 llm actor 理由为“语义筛选需由模型按条件判断”，但源文仅给出布尔/数值条件，未排除本地执行。引用 EM04 为 model_observe 的条件规则，不能自行证实“模型实际处理”的前提。该标签可能合理但目前依据不足，且与 002 同义筛选的 agent_runtime 标注相反；需把执行归属的不确定性显式记录。
- 即使接受 ir_003.effects 中的 model_observe，该 profile.roles 只有 transformer，没有内容到达模型边界的 sink，内部角色/效果解释不充分。ir_001 又被无额外依据断言本地 agent_runtime，不能用这一推断证明读取结果未被模型观察。
- ir_005 的 sink 与通知接收对象相符，但 net_send 证据仅“调用一次 notify.send”，没有确定远端边界；各 dispatch 的 llm actor 同样仅由操作名推定。count/write 的 transform/fs_write 与无值 return 不标 user_output 可接受；禁传约束未被捏造成 sanitizer。这些是标签语义依据问题，不是引文不存在或 JSON 格式错误。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
