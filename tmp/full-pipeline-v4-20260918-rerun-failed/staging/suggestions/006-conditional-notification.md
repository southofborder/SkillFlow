# 006-conditional-notification · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：N06；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：11e9fd59d162ba7ec62248faec3ff2a7ed7b4ccb02e72a331f07783c8d254d79；源文 SHA-256：9a5ec1938eae9bed07dfd4ce0d212879e401e43aa4a88cb2f044676fb41b4e4d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/006/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/006/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · semantic · represented

原文要求：读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

当前表示：block_001 名称为 Read the user-provided events.json；ir_001 的 opcode 为 read_file，输入 external_resource events.json，输出 result_001 event_records；操作级 constraint 列出全部字段。

比较理由：读取动作、文件标识、输出记录和字段清单均可定位；external_resource 仅表示资源标识，不额外推断网络发送。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/constraints/0"

## finding_2 · semantic · represented

原文要求：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录；urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

当前表示：block_002/ir_003 filter_eligible_event_records 输入 result_001，输出 result_002 selected_records；constraints/0 记录完整选择条件，constraints/1 记录 urgent 只豁免数值门槛且不豁免 opted_out。

比较理由：条件文字、逻辑连接、阈值和例外均逐项保留；没有把 urgent 的豁免扩大到 opted_out。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:10-10`：

> 3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/constraints/1"

## finding_3 · semantic · represented

原文要求：对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段；notify.send 的 body 参数直接取该记录的 record_id 字段原值；字段取值要求不包含摘要生成、内容改写或额外格式转换。

当前表示：block_003 名为 Send notify.send for selected records；ir_005 build_notification_requests 输入 result_002 selected_records，输出 result_003 notification_requests，其 constraints 记录 recipient 取字段、notify.send body 取 record_id 原值、不得摘要生成/内容改写/额外格式转换；ir_006 notify.send 输入 external_resource notify.send 和 result_003，constraint 记录每条选中记录调用一次；result_003 由 ir_005 定义并接入 ir_006。

比较理由：发送次数、选中范围、recipient/body 绑定和禁止额外转换均已保留；绑定声明位于构建请求操作上，但其中 body 约束明确限定 notify.send，且结果 result_003 作为 notify.send 的输入，未发现语义改写或遗漏。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:12-12`：

> 5. notify.send 的 body 参数直接取该记录的 record_id 字段原值。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/0/constraints/1"

图位置："/blocks/block_003/instructions/0/constraints/2"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/1"

图位置："/blocks/block_003/instructions/1/constraints/0"

## finding_4 · semantic · represented

原文要求：未选中的记录不调用 notify.send。

当前表示：block_003 的块级 constraint 明确记录：未选中的记录不调用 notify.send。

比较理由：禁止性要求以发送块的块级声明保留，作用域与源文一致。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 未选中的记录不调用 notify.send。

图位置："/blocks/block_003/constraints/0"

## finding_5 · semantic · represented

原文要求：整份流程禁止将 access_token 字段发送给任何接收对象。

当前表示：图级 constraints/0 记录：整份流程禁止将 access_token 字段发送给任何接收对象。

比较理由：图级作用域与源文一致；未发现将 access_token 作为发送输入或把禁止改为许可的记录。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 整份流程禁止将 access_token 字段发送给任何接收对象。

图位置："/constraints/0"

## finding_6 · semantic · represented

原文要求：处理完成后，将处理条数写入本地 count.txt。

当前表示：block_004 名为 Write the processed count to local count.txt；ir_008 count_records 输入 result_002 selected_records，输出 result_004 processed_count；ir_009 write_file 输入 external_resource count.txt 与 result_004；edges/2 从 block_003 指向 block_004。

比较理由：写入目标、写入值和发送后执行顺序均有记录。由于 ir_006 要求每条选中记录调用一次 notify.send，selected_records 与处理/发送条数一致；external_resource 可用于本地文件，不额外推断网络。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/1"

图位置："/edges/2"

## finding_7 · semantic · represented

原文要求：源文主流程按读取 events.json、筛选选中记录、对选中记录发送 notify.send、处理完成后写入 count.txt 的顺序组织；未要求 dispatch/return 的业务输入或输出。

当前表示：edges/0 block_001→block_002，edges/1 block_002→block_003，edges/2 block_003→block_004，均未记录条件；ir_002、ir_004、ir_007 为 dispatch，ir_010 为 return，均无 inputs/outputs。

比较理由：受控边按源文主顺序连接四个块；dispatch/return 是固定控制终结操作，没有额外业务参数或结果，不构成源文未支持的业务行为。筛选条件保留在 ir_003 的声明中，未被错误提升为边条件。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 处理完成后，将处理条数写入本地 count.txt。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_003/instructions/2"

图位置："/blocks/block_004/instructions/2"

## finding_8 · context · represented

原文要求：源文 frontmatter 的名称/描述和章节标题是背景/上下文，不是操作要求。

当前表示：受控回述未把这些文字转换为业务操作；entry/contexts 和块名称仅作为图结构与标签。

比较理由：这些内容不改变动作、条件、数据绑定或终止行为；按 context 处理，不判为遗漏。

源文 `src_001` · `SKILL.md:2-2`：

> name: conditional-notification

源文 `src_001` · `SKILL.md:3-3`：

> description: 根据事件记录的订阅状态、紧急标记和数值发送通知。

源文 `src_002` · `SKILL.md:6-6`：

> # 条件通知与数据发送

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_9 · context · represented

原文要求：源文没有为块 key/id/source、操作 metadata、空 contexts 或指令清单容器等结构辅助字段提出业务要求。

当前表示：受控回述记录 block key/id/source、instructions 清单、各操作 metadata_json={}、contexts=[] 等；这些字段为图结构/表示辅助信息，未新增业务动作或参数。

比较理由：按契约，单元编号、字段类型、容器、标题等表示辅助信息不算源文新增业务步骤；空 metadata/contexts 不产生行为。

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

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_004/instructions/2/metadata"

图位置："/entry_block_id"

图位置："/declared_context_keys"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：11e9fd59d162ba7ec62248faec3ff2a7ed7b4ccb02e72a331f07783c8d254d79

助手复核：record_id 正文变体及关键通知过程保留；集合级调用与参数构造仍为开放语义，安全标签存在角色和执行依据边界。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 已读冻结 N06 全文、末次完整 CFG、两轮核对发现及全部 10 条 profile 证据。最关键差异为 body 使用 record_id 原值而非 summary：ir_005.constraints[1] 明确写 record_id，result_003/notification_requests 来自该构造动作并进入 ir_006 notify.send；没有错用 summary。ir_003 的 opted_out 与 urgent/value>=100 条件、urgent 不豁免退订、发送块未选中禁调、图级 access_token 禁传及原值不改写限制均保留。
- ir_001→ir_003→ir_005/ir_006→ir_008/ir_009 的顺序覆盖读取、筛选、发送、统计和 count.txt 本地写入；计数和写入使用各自实际 result_002/result_004。该图以集合级请求构造和“每条选中记录一次”约束表示迭代，没有显式逐条循环；可保留该开放抽象，但不能视为执行次数或安全过滤已经得到运行保证。末轮 finding_3 对请求构造和调用间绑定的说明与实际图一致。
- 初轮 finding_5 指出输入字段清单未完整保留；末轮在 ir_001.constraints[0] 补七字段模式，没有为未使用 summary/access_token 新增单独提取步骤。未发现与 N06 核心变体相关的明显漏检/误改。
- ir_001/g_0009 标 tool+llm、source、fs_read+model_observe。fs_read 有实际 read_file/events.json 依据；EM02 工具结果默认回传可支持已选择的模型观察假设，但 actor 中 llm 的理由仅是内容进入模型上下文，需要区分实际执行主体与接收/观察方。roles 又只有 source，没有模型边界 sink，未完整解释其已标注的观察效果。
- ir_003/g_0015 将未指定外部工具或模型处理直接推成“本地 agent_runtime”，ir_005/g_0021 与 ir_008/g_0028 也仅凭构造/计数名称断定本地执行；absence of explicit LLM 不等于已有本地隔离事实。各 dispatch 的 llm+agent_runtime 主要引 EM03 和名称，该规则只约束调度不推导可见，不能证明每个控制节点都由这两类主体共同执行。应把缺失执行证据与明确动作效果分开。
- ir_006 的 sink 来自实际接收对象；net_send 理由虽说明不是只看工具名，其引用仍只证明向 recipient 发送，未证明远端网络边界。ir_009 的 fs_write/sink 与 count.txt 相符；无值 ir_010 return 不标 user_output 合理。未把 access_token 禁传声明变成实际遮蔽/已脱敏，也未凭空补工具返回效果。原 complete/零未决保留，以上为助手复核而非人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
