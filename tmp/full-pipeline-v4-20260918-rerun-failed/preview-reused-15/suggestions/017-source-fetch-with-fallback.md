# 017-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F05；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：0d056b6699347c199da8e08c3d7cb7d3939c0db87dd1f0c1f463c5f08c059858；源文 SHA-256：9fac0eaf3e63727fffbc63ceb78c3833001cf9f7832630c36b938af8e5fc88ad

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/017/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/017/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前言、标题和历史示例：name/description/标题为背景；第9条是明确不在本工作流执行的历史示例，不是业务要求。

当前表示：受控回述未把前言、标题或 status.txt 追加步骤建模为操作；workflow 从 entry 和后续块开始。

比较理由：这些内容属于 context/非执行示例；不进入业务要求不会改变步骤覆盖。未发现受控回述把该历史示例当作已执行步骤。

源文 `src_001` · `SKILL.md:2-2`：

> name: source-fetch-with-fallback

源文 `src_001` · `SKILL.md:3-3`：

> description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

源文 `src_003` · `SKILL.md:16-16`：

> 9. Historical example, not executed in this workflow: Before returning from every success or failure path, append the final status to local status.txt.

## finding_2 · semantic · represented

原文要求：第1条要求从用户请求读取 source_id，并从环境读取 FAST_KEY。

当前表示：entry 与 /contexts 声明相关键；block_001 以 read_source_id_from_request 输出 result_001(source_id)，block_002 以 read_fast_key_from_environment 输出 result_002(fast_key)；edges/0 连接 block_001→block_002。

比较理由：操作名、块名和输出标识分别保留两个读取动作及对象。source_id 先于 FAST_KEY 的顺序是 IR 记录次序；源文只说并列读取，未规定顺序，因此该具体顺序不构成语义冲突。context_key 是键的承载/标识，environment/request 的语义由 opcode 与块名保留。

源文 `src_003` · `SKILL.md:8-8`：

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

图位置："/entry_block_id"

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

## finding_3 · semantic · represented

原文要求：第2条要求 FAST_KEY 存在时先调用 fast.fetch，传入 source_id 与 FAST_KEY；FAST_KEY 不存在时直接调用 archive.fetch，不调用 fast.fetch。

当前表示：block_003 用 result_002 执行 check_fast_key_present，输出 result_003；dispatch 读取 result_003。edges/2 在 present 条件去 block_004；edges/3 在 absent 条件去 block_006。block_004 的 fast.fetch 输入包含 fast.fetch 资源标识、result_001(source_id)、result_002(fast_key)。block_006 的 archive.fetch 输入只含 archive.fetch 资源标识和 result_001。

比较理由：存在分支到快取工具且参数齐全；不存在分支绕过 fast.fetch 到归档工具。条件文字和结果依赖一致。edges 条件未求值但记录明确。

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/constraints/0"

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

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/edges/2"

图位置："/edges/3"

## finding_4 · semantic · represented

原文要求：第3条要求 fast.fetch 第一次尝试仅在 transient error 时重试一次；非 transient 首次失败不得重试。

当前表示：block_004 的 fast.fetch 输出 result_004 状态并由 ir_008 dispatch 读取；edges/5(transient failure) 去 block_005 重试，edges/6(non-transient failure) 去 block_006 归档，edges/4(success) 去成功返回。block_005 只有一个 fast.fetch 操作和对应 dispatch；其操作级 constraint 明示 exactly once / transient 条件；没有回到首次尝试或再次重试的边。

比较理由：重试对象、次数、触发条件和非重试分支均可定位；非 transient 路径不进入重试块。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

图位置："/constraints/1"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/outputs/2"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

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

图位置："/edges/7"

图位置："/edges/8"

## finding_5 · semantic · represented

原文要求：第4条要求首次非 transient 失败或 fast.fetch 重试失败后，用 source_id 调用 archive.fetch；第5条要求 archive.fetch 至多调用一次，且 source_id 是其唯一业务参数。

当前表示：edges/6(non-transient first failure) 和 edges/8(retry failed) 均指向 block_006；edges/3(FAST_KEY absent) 也指向 block_006。block_006 只有一个 archive.fetch，输入为 archive.fetch 资源标识与 result_001(source_id)，无 FAST_KEY；操作级 constraints/0 声明 at most once 且 source_id 为唯一参数，图级 constraints/2、/3 也记录相应要求。

比较理由：失败原因路径和重试失败路径都进入归档调用；单一 archive.fetch 操作和约束覆盖至多一次。external_resource 是工具/资源标识，不是额外业务参数，因此业务参数仍只有 source_id。

源文 `src_003` · `SKILL.md:11-11`：

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

源文 `src_003` · `SKILL.md:12-12`：

> 5. Call archive.fetch at most once and pass source_id as its only argument.

图位置："/constraints/2"

图位置："/constraints/3"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/outputs/1"

图位置："/blocks/block_006/instructions/0/outputs/2"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/edges/3"

图位置："/edges/6"

图位置："/edges/8"

## finding_6 · semantic · represented

原文要求：第6条要求任一工具成功时，原样返回该成功响应的 body，并且不再发起 fetch 调用。

当前表示：edges/4(fast.fetch first success)→block_007 return result_005(fast_fetch_first_body)；edges/7(retry success)→block_008 return result_008(fast_fetch_retry_body)；edges/9(archive success)→block_009 return result_011(archive_fetch_body)。各 return 的操作级 constraint 均写明 body unchanged 与 make no further fetch calls；这些 return 块无后续边。

比较理由：三个成功来源分别返回各自结果身份，未把首次、重试和归档的 body 互换；return 作为终止路径不引出后续 fetch。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

图位置："/constraints/4"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/constraints/0"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/edges/4"

图位置："/edges/7"

图位置："/edges/9"

## finding_7 · semantic · represented

原文要求：第7条要求 archive.fetch 失败时停止并返回其错误，且不得重试 archive.fetch。

当前表示：edges/10(archive.fetch failed) 指向 block_010；block_010 return result_012(archive_fetch_error)。其操作级 constraint 写明 stop and return its error; do not retry archive.fetch；该 return 无后续边，图中也没有 archive.fetch 重试操作。

比较理由：错误返回身份为 archive_fetch_error，终止和禁止重试均被记录，未出现 archive.fetch 再调用路径。

源文 `src_003` · `SKILL.md:14-14`：

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/constraints/5"

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/constraints/0"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/edges/10"

## finding_8 · semantic · represented

原文要求：第8条禁止在本工作流任何位置把 FAST_KEY 传给 archive.fetch 或诊断输出。

当前表示：图级 constraints/6 逐字记录该禁止；archive.fetch 操作级 constraints/1 记录 Never pass FAST_KEY to archive.fetch；archive.fetch 输入列表只有 archive.fetch 资源标识和 result_001(source_id)，未包含 result_002(fast_key)。图中没有 diagnostic output 操作。

比较理由：对 archive.fetch 的禁止同时由声明和实际输入缺失支持；诊断输出禁止由全局声明覆盖，且当前图没有诊断输出动作可违反。禁止性要求未被误转为必须产生诊断输出。

源文 `src_003` · `SKILL.md:15-15`：

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/constraints/6"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

## 安全标注未决

- {"instruction_id": "ir_013", "field": "effects", "reason": "普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。"}
- {"instruction_id": "ir_014", "field": "effects", "reason": "普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。"}
- {"instruction_id": "ir_015", "field": "effects", "reason": "普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。"}
- {"instruction_id": "ir_016", "field": "effects", "reason": "普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：0d056b6699347c199da8e08c3d7cb7d3939c0db87dd1f0c1f463c5f08c059858

助手复核：历史status.txt步骤正确排除，重试/回退/返回流程保留；4项返回未决合理，但三工具网络效果仅凭名称推断、执行主体依据偏弱。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 关键F05变体正确：源文第9条将返回前追加status.txt明确标为历史示例、不执行。本次10块16IR中四个终态直接return，没有追加状态操作，没有把历史文字保留成强制写入约束；16份profile也无fs_write。不能把相较F01少了四次写入误判为漏步骤。
- 请求/环境来源、FAST_KEY存在分支、首次transient才单次重试、non-transient首次失败/任意重试失败回退、archive至多一次均保留。两个fast业务输入为source_id+FAST_KEY，archive只有source_id，密钥禁传声明未被改成伪造保护动作。
- 首次/重试/archive成功分别返回result_005/008/011，archive失败返回result_012 error，返回终态无后续fetch。核对器第0轮7业务项represented，助手未发现关键建图缺口。
- 全部16份profile及证据已复核：读取context_read、存在性transform、三工具多actor（agent_runtime/tool）、source/sink、EM02回传model_observe均有动作或执行假设依据；四个return保持sink并明确user_output不确定，4项unresolved保留合理。
- 重要标注依据问题：ir_007/009/011的net_send/net_receive全部仅引用fast.fetch或archive.fetch这一工具名称，理由却直接称远端工具。源文及图均无网络部署说明，EM06明令不能据工具名猜网络。网络效果应有独立依据或保留未决，本例incomplete的4项未决没有覆盖这3个工具的网络边界。并非证明实际无网络，而是当前赋值依据不足。
- 6个dispatch用EM03“LLM调度”判actor=llm，仍把可能参与当成确定参与；请求/环境读取被断言本地runtime，模型可见范围未明确。工具回传model_observe与网络效果分别判断，不能用前者补证明后者，也不能以未贴观察标签保证密钥隔离。
- 保留当前audit_passed和annotation incomplete，不修改标签或调用模型补跑。复核针对当前末图，结论仅为助手意见、非用户人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
