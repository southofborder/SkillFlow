# 018-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F06；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：f47fb1a92cfa2a55ae485abd344b1943853cfb823e1de444ecad7e5cc8fac1d7；源文 SHA-256：f71d7f167ce30cad6dcca125ca38e3b747b885de72fccb8013826d89d4a6056f

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/018/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/018/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前置元数据与标题提供技能名称、描述和标题，属于背景/上下文，不是业务步骤。

当前表示：受控回述将描述记录为图级约束 fact:/constraints/0，入口为 fact:/entry；名称和 Markdown 标题未作为独立业务步骤建模。

比较理由：名称/标题为上下文，描述已以约束形式保留；未发现需要作为业务要求补记的语义。

源文 `src_001` · `SKILL.md:2-2`：

> name: source-fetch-with-fallback

源文 `src_001` · `SKILL.md:3-3`：

> description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

图位置："/entry_block_id"

图位置："/constraints/0"

## finding_2 · semantic · represented

原文要求：步骤 1：从用户请求读取 source_id，并从环境读取 FAST_KEY。

当前表示：block_001 的 read_source_id_from_request 使用 context_key source_id 并输出 result_001；block_002 的 read_fast_key_from_environment 使用 context_key FAST_KEY 并输出 result_002；/contexts 声明两个键；边 0、1 按顺序连接读取和检查前控制流；结果引用绑定将 result_001/result_002 连接到后续使用。

比较理由：读取动作、对象和后续绑定均存在；block source 标记为 context 属表示辅助，opcode 已明确 from_request/from_environment。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

图位置："/declared_context_keys"

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

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/edges/0"

图位置："/edges/1"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_006/instructions/0/inputs/1"

## finding_3 · semantic · represented

原文要求：步骤 2：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 尝试 fast.fetch；若不存在，直接调用 archive.fetch，不调用 fast.fetch。

当前表示：block_003 check_fast_key_present 读取 result_002 并输出 result_003；dispatch 使用 result_003；边 /edges/2 条件 'FAST_KEY is present' 到 block_004，边 /edges/3 条件 'FAST_KEY is absent' 到 block_006（archive.fetch）；/constraints/1 记录该条件；result_003 引用绑定存在。

比较理由：存在/缺失分支、先 fast 后 archive、缺失时跳过 fast.fetch 均由边和块结构保留。

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/constraints/1"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/edges/2"

图位置："/edges/3"

## finding_4 · semantic · represented

原文要求：步骤 3：仅当第一次 fast.fetch 以 transient error 失败时重试 fast.fetch 恰好一次；非 transient 首次失败不重试。

当前表示：block_004 first fast.fetch 输出 result_006 succeeded 和 result_007 transient；dispatch 使用二者；边 /edges/5 条件 'first fast.fetch failed with a transient error' 到 block_005；边 /edges/6 条件 'first fast.fetch failed with a non-transient error' 到 block_006；block_005 只有一次 fast.fetch 重试，且 incoming 仅来自 transient 边；/constraints/2 与 block/op 约束记录 exactly once 和非 transient 不重试。

比较理由：重试触发条件、次数和禁止非 transient 重试均保留；block_005 无回边，结构上恰好一次。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

图位置："/constraints/2"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/outputs/2"

图位置："/blocks/block_004/instructions/0/outputs/3"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/inputs/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/outputs/1"

图位置："/blocks/block_005/instructions/0/outputs/2"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

## finding_5 · semantic · represented

原文要求：步骤 4：非 transient 首次失败或任意重试失败后，调用 archive.fetch 并传 source_id。

当前表示：边 /edges/6（first fast.fetch failed non-transient）和 /edges/8（retry fast.fetch failed）均指向 block_006 archive.fetch；block_006 输入 result_001 source_id；/constraints/3 记录该回退要求。

比较理由：两种触发条件到同一 archive.fetch 的路径和 source_id 绑定均存在。

源文 `src_003` · `SKILL.md:11-11`：

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

图位置："/constraints/3"

图位置："/edges/6"

图位置："/edges/8"

图位置："/blocks/block_006/instructions/0/inputs/1"

## finding_6 · semantic · represented

原文要求：步骤 5：archive.fetch 最多调用一次，且仅传 source_id 作为业务参数。

当前表示：block_006 中 ir_011 archive.fetch 只有一个结果输入 result_001 source_id（另有 external_resource archive.fetch）；/constraints/4 及 block/op 约束记录 at most once 和 only argument；图中无循环，只有一个 archive.fetch 操作。

比较理由：次数和参数绑定符合源文；external_resource 按契约不作为业务参数。

源文 `src_003` · `SKILL.md:12-12`：

> 5. Call archive.fetch at most once and pass source_id as its only argument.

图位置："/constraints/4"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/constraints/1"

图位置："/blocks/block_006/constraints/2"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/outputs/1"

图位置："/blocks/block_006/instructions/0/outputs/2"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0/constraints/2"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/edges/9"

图位置："/edges/10"

## finding_7 · semantic · represented

原文要求：步骤 6：任一工具成功后，返回该成功响应的 summary 值且不改变，不再发起 fetch 调用。

当前表示：block_007 对 result_004 提取 first_fast_fetch_summary result_014 并 return；block_008 对 result_008 提取 retry_fast_fetch_summary result_015 并 return；block_009 对 result_011 提取 archive_fetch_summary result_016 并 return；成功块无后续 fetch；/constraints/5 及 return 约束记录 unchanged/no further fetch。

比较理由：三个成功出口分别覆盖首次 fast、重试 fast、archive 的成功响应，返回身份和 summary 提取绑定正确。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.

图位置："/constraints/5"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/constraints/0"

图位置："/blocks/block_007/constraints/1"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/outputs/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/inputs/1"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_007/instructions/2"

图位置："/blocks/block_007/instructions/2/inputs/0"

图位置："/blocks/block_007/instructions/2/constraints/0"

图位置："/blocks/block_007/instructions/2/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/constraints/0"

图位置："/blocks/block_008/constraints/1"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/outputs/0"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/inputs/1"

图位置："/blocks/block_008/instructions/1/constraints/0"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_008/instructions/2"

图位置："/blocks/block_008/instructions/2/inputs/0"

图位置："/blocks/block_008/instructions/2/constraints/0"

图位置："/blocks/block_008/instructions/2/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/constraints/0"

图位置："/blocks/block_009/constraints/1"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/outputs/0"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/inputs/1"

图位置："/blocks/block_009/instructions/1/constraints/0"

图位置："/blocks/block_009/instructions/1/metadata"

图位置："/blocks/block_009/instructions/2"

图位置："/blocks/block_009/instructions/2/inputs/0"

图位置："/blocks/block_009/instructions/2/constraints/0"

图位置："/blocks/block_009/instructions/2/metadata"

图位置："/edges/4"

图位置："/edges/7"

图位置："/edges/9"

## finding_8 · semantic · represented

原文要求：步骤 7：archive.fetch 失败时停止并返回其 error，不再重试 archive.fetch。

当前表示：边 /edges/10 条件 'archive.fetch failed' 到 block_010；block_010 append failure 后 return result_012 archive_fetch_error；block_010 无出边；/constraints/6 及 return 约束记录 stop/return error/no retry。

比较理由：失败出口、返回身份和停止/不重试语义均保留。

源文 `src_003` · `SKILL.md:14-14`：

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/constraints/6"

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/constraints/0"

图位置："/blocks/block_010/constraints/1"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/constraints/0"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/inputs/0"

图位置："/blocks/block_010/instructions/1/constraints/0"

图位置："/blocks/block_010/instructions/1/metadata"

图位置："/edges/10"

## finding_9 · semantic · represented

原文要求：步骤 8：整个工作流中不得将 FAST_KEY 传给 archive.fetch 或诊断输出。

当前表示：/constraints/7 和 block/op 级 archive.fetch 约束记录禁止；ir_011 archive.fetch 输入不含 FAST_KEY；append_final_status_to_status_file 的输入仅为 local status.txt 和字面量 success/failure，不含 FAST_KEY；图中没有其他诊断输出携带 FAST_KEY。

比较理由：禁止项在声明层记录，实际 archive.fetch 和状态追加操作的输入也未违反。

源文 `src_003` · `SKILL.md:15-15`：

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/constraints/7"

图位置："/blocks/block_006/constraints/1"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/inputs/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/inputs/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/inputs/1"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

## finding_10 · semantic · represented

原文要求：步骤 9：每个成功或失败路径返回前，把最终状态追加到 local status.txt。

当前表示：成功块 block_007/008/009 均在 return 前执行 append_final_status_to_status_file，输入 local status.txt 和字面量 "success"；失败块 block_010 在 return 前执行同一操作，输入 local status.txt 和字面量 "failure"；/constraints/8 及 block/op 约束记录。

比较理由：所有终止路径（首次 fast 成功、重试 fast 成功、archive 成功、archive 失败）都在 return 前有状态追加；字面量 success/failure 是未规定状态值的合法具体表达。

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/constraints/8"

图位置："/blocks/block_007/constraints/1"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/inputs/1"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_008/constraints/1"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/inputs/1"

图位置："/blocks/block_008/instructions/1/constraints/0"

图位置："/blocks/block_009/constraints/1"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/inputs/1"

图位置："/blocks/block_009/instructions/1/constraints/0"

图位置："/blocks/block_010/constraints/1"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/constraints/0"

## 安全标注未决

- {"instruction_id": "ir_007", "field": "effects", "reason": "图仅记录fast.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。"}
- {"instruction_id": "ir_009", "field": "effects", "reason": "图仅记录fast.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。"}
- {"instruction_id": "ir_011", "field": "effects", "reason": "图仅记录archive.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：f47fb1a92cfa2a55ae485abd344b1943853cfb823e1de444ecad7e5cc8fac1d7

助手复核：新018的summary返回身份、四终态状态写入和关键控制完整；旧context/environment误报未复现。profile有3项合理网络未决，存在性transform、return未知及本地/模型观察边界仍需澄清。

- 新run从源重新提取的r000为10块23IR，不能沿用旧018的c7c09c68图或判定。完整源文相同；本轮audit_passed、9业务项represented，旧实验的environment/context误报未复现。finding_2明确承认context为表示类别，read_fast_key_from_environment的动作文字、FAST_KEY键与后续result_002绑定保留真实来源。
- 关键summary变体正确：首次响应result_004由ir_013提取summary result_014，重试响应result_008由ir_016提取result_015，archive响应result_011由ir_019提取result_016；对应ir_015/018/021分别返回本次summary。没有错返body或首次响应，也没有添加重新生成摘要的LLM步骤，unchanged约束保留。
- 最终状态绑定清楚：ir_014/017/020分别在三个成功return之前向local status.txt追加success，ir_022在失败return之前追加failure。写入数据是状态字面量，非body/error；源文未规定状态格式，这种具体表示合理。archive失败ir_023返回result_012 archive_error。
- 请求/环境读取、缺密钥直达archive、首次transient才单次重试、non-transient首次失败与任意retry失败回退、archive至多一次均由实际边和操作保留。fast调用只有source_id/key两个业务参数，archive只有source_id；密钥禁传声明及直接输入绑定无冲突，成功返回没有后续fetch。未据此声称传播后没有泄露。
- 23/23份profile与全部标签证据已阅读。三工具source/sink与model_observe明确引用EM02回传假设，未把工具名当网络；3项网络effects未决保留合理。四次状态写入sink/fs_write、三次summary字段提取transformer/transform均有对应图操作，transform不是重新摘要或已脱敏保证。
- 标注需要澄清：ir_005 check_fast_key_present从key值产生布尔结果，却被当纯控制操作，roles/effects皆空；此前同类存在性计算多标transform。按现词表“计算/选择/改变表示”，这一空标签解释至少需要统一，不能将有数据输出的判断与无输出dispatch简单等同。此问题不改变当前CFG分支正确性。
- 四个return effects为空，以“不能单凭return证明user_output”作理由但没有接收方未决；这只能说明不能贴确定用户输出，不能证明不存在适用效果。源文仍未指定接收边界，与旧013同义场景保留return未决的口径不同，应保留这一不确定性。
- 隐含模型观察边界仍未解决：读取FAST_KEY与summary字段提取均被解释为纯本地agent_runtime，源文未明确其工具实现/回传或模型隔离机制。不能将未贴model_observe等同于内容模型不可见；也不能据EM01推定所有环境字段已经读取。当前标签是动作标注，敏感集合与传播仍待后续。
- 本复核只绑定新run该图与新profile，旧018误报和失败复核独立保留。未修改图、标签、模型结论或冻结语料，未执行Skill工具/脚本，属于助手复核而非用户人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
