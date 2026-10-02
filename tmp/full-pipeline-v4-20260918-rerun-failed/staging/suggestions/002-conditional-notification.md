# 002-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N02；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：900e7b1665d4ddb3270499ce28034e505c93e464a23a17c72532a5931b4b2e96；源文 SHA-256：23970285b85f1481f6e598b18d2974121b4d6aa0e1cd51241a95b3b8add6405b

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/002/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/002/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文第1-4行的 frontmatter 名称/描述和第6行标题属于背景、名称和标题，不是独立业务步骤；本项核对其上下文地位。

当前表示：受控回述记录入口 fact:/entry、空的 fact:/contexts，以及各块 key/id/name/source、完整操作ID清单和各 metadata_json 等表示辅助字段；这些字段未被记录为额外业务动作。

比较理由：按 REVIEW-MODALITY，前言、名称、标题和表示辅助信息不作为业务要求；受控字段用于说明上下文或图结构定位，未发现其被当成执行步骤或改变数据去向。

源文 `src_001` · `SKILL.md:1-4`：

> name: conditional-notification

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

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

图位置："/blocks/block_004/instructions/2/metadata"

图位置："/blocks/block_004/instructions/3/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_005/instructions/2/metadata"

## finding_2 · semantic · represented

原文要求：读取用户提供的 events.json；每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前表示：block_001 的 ir_001 read_events_json 以 external_resource/events.json 为输入，输出 result_001/event_records；ir_001 操作级约束记录相同的字段清单。

比较理由：读取对象标识 events.json 保留，字段清单逐项一致；“用户提供”是来源背景限定，不是独立动作或数据绑定，受控的 external_resource/events.json 仍表示同一读取对象。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/constraints/0"

## finding_3 · semantic · represented

原文要求：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时选中记录；urgent 为 true 只豁免数值门槛，不豁免 opted_out 限制。

当前表示：ir_003 select_eligible_event_records 输入 result_001/event_records，输出 result_002/selected_records；两条操作级约束分别逐字记录选择条件和 urgent 豁免边界。

比较理由：条件、运算符、数值门槛和 opted_out 限制与源文一致；未发现把 urgent 表示成可绕过 opted_out 或改变 value 门槛的语义。

源文 `src_003` · `SKILL.md:8-8`：

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_004` · `SKILL.md:10-10`：

> urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/constraints/1"

## finding_4 · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

当前表示：block_003 的 ir_005 get_next_selected_record 以 result_002/selected_records 为输入，输出 result_003/current_selected_record 和 result_004/has_more_selected_records；ir_006 dispatch 使用 result_004；edges/2 和 edges/3 形成继续发送与结束分支，edges/4 回到遍历；block_004 的 ir_007 从 result_003 提取 result_005/recipient，ir_009 输入 result_005，且 ir_009 约束记录对每条选中记录调用一次 notify.send。

比较理由：遍历输入仅为 selected_records，发送块只在 has_more_selected_records 分支进入，发送后回到取下一记录；recipient 通过 result_005 绑定到 notify.send，次数约束存在，未发现未选中集合进入发送循环。

源文 `src_004` · `SKILL.md:10-10`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/2"

图位置："/blocks/block_004/instructions/2/inputs/1"

图位置："/blocks/block_004/instructions/2/constraints/0"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

## finding_5 · semantic · represented

原文要求：notify.send 的 body 参数直接取该记录的 summary 字段原值；字段取值不包含摘要生成、内容改写或额外格式转换。

当前表示：ir_008 extract_record_summary 从 result_003/current_selected_record 提取 result_006/summary；ir_008 约束记录 body 直接取 summary 原值，且不包含摘要生成、内容改写或额外格式转换；ir_009 输入 result_006；图级 /constraints/1 也记录该取值限制。

比较理由：原值绑定和禁止转换均被声明，notify.send 实际输入包含 result_006/summary；未发现生成、改写或额外格式转换操作。

源文 `src_005` · `SKILL.md:12-12`：

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_006` · `SKILL.md:14-14`：

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/constraints/1"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/outputs/0"

图位置："/blocks/block_004/instructions/1/constraints/0"

图位置："/blocks/block_004/instructions/1/constraints/1"

图位置："/blocks/block_004/instructions/2/inputs/2"

## finding_6 · semantic · represented

原文要求：未选中的记录不调用 notify.send。

当前表示：block_004 块级约束记录“未选中的记录不调用 notify.send。”；控制流从 result_002/selected_records 取 current_selected_record，发送块只在继续遍历分支进入。

比较理由：约束文字与源文一致；遍历输入为 selected_records，edges/2 和 edges/3 区分继续发送与结束，未给未选中记录到 notify.send 的显式路径。

源文 `src_005` · `SKILL.md:12-12`：

> 未选中的记录不调用 notify.send。

图位置："/blocks/block_004/constraints/0"

图位置："/edges/2"

图位置："/edges/3"

图位置："/blocks/block_003/instructions/0/inputs/0"

## finding_7 · semantic · represented

原文要求：整份流程禁止将 access_token 字段发送给任何接收对象。

当前表示：图级 /constraints/0 和 ir_009 操作级约束均逐字记录该禁止；ir_009 的输入只有 external_resource/notify.send、result_005/recipient、result_006/summary，没有 access_token。

比较理由：禁止声明在全局和发送操作两处保留；发送操作数未绑定 access_token。读取约束虽列出 access_token 字段，但读取本身不是发送。

源文 `src_006` · `SKILL.md:14-14`：

> 整份流程禁止将 access_token 字段发送给任何接收对象。

图位置："/constraints/0"

图位置："/blocks/block_004/instructions/2/constraints/1"

图位置："/blocks/block_004/instructions/2/inputs/0"

图位置："/blocks/block_004/instructions/2/inputs/1"

图位置："/blocks/block_004/instructions/2/inputs/2"

图位置："/blocks/block_001/instructions/0/constraints/0"

## finding_8 · semantic · represented

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前表示：block_005 在遍历无更多选中记录后进入；ir_011 count_processed_records 以 result_002/selected_records 为输入输出 result_007/processed_count；ir_012 write_processed_count 输入 count.txt 和 result_007；块级约束记录处理完成后写入本地 count.txt。

比较理由：写入对象 count.txt 与计数结果 result_007 绑定，顺序在遍历结束之后；循环对每条 selected_records 调用一次 notify.send 且源文未给失败分支，按已选集合计数是处理条数的合法具体表示。

源文 `src_007` · `SKILL.md:16-16`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

图位置："/edges/3"

## finding_9 · semantic · represented

原文要求：整体顺序为读取 events.json、按条件选中记录、对每条选中记录发送通知，处理完成后写 count.txt。

当前表示：edges/0 连接 block_001→block_002，edges/1 连接 block_002→block_003；edges/2、edges/3、edges/4 形成 block_003→block_004→block_003 循环及 block_003→block_005 结束分支；各 dispatch/return 终结相应块。

比较理由：控制边体现读取→选择→遍历发送→计数写入的先后；循环结束后进入计数块，return 终止。未发现把写计数提前到发送前或把未选中记录纳入发送循环的边。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_004` · `SKILL.md:10-10`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_007` · `SKILL.md:16-16`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_004/instructions/3"

图位置："/blocks/block_005/instructions/2"

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

## finding_10 · semantic · represented

原文要求：各步骤结果按实际标识传递：读取结果用于选择，选择结果用于遍历和计数，当前记录用于取 recipient/summary，提取值用于 notify.send，计数结果用于写 count.txt。

当前表示：links 逐条按 identifier 绑定 result_001→ir_003、result_002→ir_005/ir_011、result_004→ir_006、result_003→ir_007/ir_008、result_005/result_006→ir_009、result_007→ir_012。

比较理由：每个结果的使用位置与定义位置一致，未按 semantic_name 合并不同 ID；数据流覆盖源文要求的 recipient、summary、selected records 和 processed count。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_004` · `SKILL.md:10-10`：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_005` · `SKILL.md:12-12`：

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

源文 `src_007` · `SKILL.md:16-16`：

> 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/2/inputs/1"

图位置："/blocks/block_004/instructions/2/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/1/inputs/1"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：900e7b1665d4ddb3270499ce28034e505c93e464a23a17c72532a5931b4b2e96

助手复核：关键业务过程在第 1 轮图中完整可定位；安全标签的执行主体与网络边界存在依据不足，不能把 complete 视为语义正确。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 检查范围为冻结 N02 全文、末轮完整 CFG/受控事实、两轮核对发现及全部 13 条 profile 的证据。末轮读取 ir_001 保留七个字段；ir_003 保留 opted_out 非 true 与 (urgent=true 或 value>=100) 及 urgent 不豁免退订限制；ir_005/ir_006 的继续/结束分支和回边覆盖逐条通知；ir_007/ir_008 从当前记录提取 recipient/summary，ir_009 仅以对应 result_005/result_006 作为业务输入。计数 ir_011 和写入 ir_012 位于遍历结束之后，未发现关键发送、参数或后置计数遗漏。
- 初轮 finding_2 指出 record_id 字段模式缺失；末轮 ir_001.constraints[0] 已补齐。末轮 finding_2–finding_10 的业务保留结论总体与实际过程相符。图级禁传 access_token 和禁止改写仍是声明；实际字段选择支持预期依赖，但不构成已证明运行时隐私保护。
- 安全标注 ir_001/g_0009、ir_003/g_0015、ir_005/g_0021、ir_007/g_0027、ir_008/g_0028 将读取、筛选和字段提取断定为 agent_runtime/本地处理，仅引用 opcode；源文和 CFG 未规定执行主体或模型隔离。尤其 ir_003 的 agent_runtime 与同义 N03 中相同筛选标成 llm 不一致。应补充可核验执行依据，或将 actor/是否 model_observe 外置为未决，而不是据此确信模型不可见。
- 所有 dispatch（ir_002/004/006/010）的 llm actor 只引 EM03 的“LLM 调度”。EM03 是“调度不等于内容可见”的否定边界，不规定每个 dispatch 必由 LLM 执行，因此该 actor 推断证据不足。
- ir_009 的 sink 有接收对象依据；net_send 的引文只证明向 recipient 发送通知，尚未明确跨远端网络。按 EM06 应保留发送边界与网络边界的区别，不能把工具名或“发送”直接当成远程传输证明。未记录工具返回数据，当前不宜凭空补 net_receive/model_observe。
- 字段选择/计数标 transformer+transform、本地 count.txt 写入标 sink+fs_write、无数据 return 不标 user_output 均与动作相符；未把 access_token 禁止声明标为遮蔽或已脱敏。上述标注疑点为助手复核意见，原始 complete 与零 unresolved 记录保持原样，尚非人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
