# 014-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F02；运行：full-pipeline-v4-20260918；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：13d9e80c7ecdb488709b6642a52c3802baa9e74653bde4f4940e40e7bfc73027；源文 SHA-256：f67fa82a7b92a8f0fc13d46d8b5857e34dcdb36a3a965dfec809b6eb8aa3b8cb

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/014/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/014/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 与标题提供技能名称和背景，不是业务执行要求。

当前表示：受控回述以入口、块键/ID/名称/数据来源标记、操作ID清单、metadata、上下文键声明和 dispatch 控制操作记录图结构；这些不构成源文新增业务步骤。

比较理由：src_001/src_002 属于背景；受控字段中的键、名称、列表、metadata、/contexts 声明和 dispatch 固定控制终结操作按契约属于表示辅助信息或固定控制，不改变业务要求。显式读取操作名另行保留了 request/environment 语义。

源文 `src_001` · `SKILL.md:2-2`：

> name: source-fetch-with-fallback

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

图位置："/entry_block_id"

图位置："/declared_context_keys"

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1/metadata"

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1/metadata"

## finding_2 · semantic · represented

原文要求：从用户请求读取 source_id，并从环境读取 FAST_KEY。

当前表示：block_001 的 ir_001 操作名为 read_source_id_from_request，输入 context_key/source_id，输出 result_001；block_002 的 ir_003 操作名为 read_fast_key_from_environment，输入 context_key/FAST_KEY，输出 result_002；edges/0 与 edges/1 表示先读 source_id、再读 FAST_KEY。

比较理由：两个读取动作、对象标识、输出结果和先后关系均可定位。context_key 是操作数种类，显式 opcode 已分别保留 request 与 environment 语义，未发生对象或来源错转。

源文 `src_003` · `SKILL.md:8-8`：

> Read source_id from the user's request and read FAST_KEY from the environment. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/edges/0"

图位置："/edges/1"

## finding_3 · semantic · represented

原文要求：若 FAST_KEY 存在，先尝试 fast.fetch；若不存在，直接调用 archive.fetch，且不调用 fast.fetch。

当前表示：block_003 的 ir_005 check_fast_key_present 读取 result_002，输出 result_003；dispatch 使用 result_003；edges/2 在“FAST_KEY is present”时指向 first fast.fetch 块，edges/3 在“FAST_KEY is absent”时直接指向 archive.fetch 块；graph /constraints/0 与 block_003 constraint 复述该条件。

比较理由：条件对象、分支值、两个出口及缺失时的直达路径均有记录。absent 分支越过 fast.fetch 块，符合“without calling fast.fetch”。

源文 `src_003` · `SKILL.md:8-8`：

> If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/constraints/0"

图位置："/blocks/block_003/constraints/0"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/edges/2"

图位置："/edges/3"

## finding_4 · semantic · represented

原文要求：在 FAST_KEY 存在时，第一次尝试 fast.fetch，并传入 source_id 与 FAST_KEY。

当前表示：block_003 的 ir_007 操作名为 fast.fetch，输入 external_resource/fast.fetch、result_001(source_id)、result_002(FAST_KEY)，输出 result_004 结果状态与 result_005 body；edges/4 表示首次成功，edges/6 表示首次非瞬态失败后转 archive.fetch；block 与操作约束复述存在 FAST_KEY 时先试 fast.fetch。

比较理由：动作、资源、两个业务输入及结果身份均正确；external_resource 是资源输入，不作为业务参数数量判断。首次尝试只在此块记录，未发生对象错绑。

源文 `src_003` · `SKILL.md:8-8`：

> If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_004/constraints/0"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/edges/4"

图位置："/edges/6"

## finding_5 · semantic · represented

原文要求：仅当 fast.fetch 第一次尝试因瞬态错误失败时，恰好重试一次；非瞬态首次失败不重试。

当前表示：block_004 的 ir_009 是唯一一次 fast.fetch 重试，输入仍为 external_resource/fast.fetch、result_001(source_id)、result_002(FAST_KEY)，输出 result_006 结果状态与 result_007 body；edges/5 从首次瞬态失败进入该重试，edges/7 表示重试成功，edges/8 表示重试失败；没有回边形成第二次重试；graph /constraints/1 与 block/op 约束复述恰好一次及非瞬态不重试。

比较理由：重试对象、次数、触发条件、传入参数和失败后去向均有记录。图中无循环回到重试块，非瞬态首次失败经 edges/6 直接转 archive.fetch，未重试。

源文 `src_004` · `SKILL.md:10-10`：

> Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

图位置："/constraints/1"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/outputs/1"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/edges/5"

图位置："/edges/7"

图位置："/edges/8"

## finding_6 · semantic · represented

原文要求：在 FAST_KEY 缺失、非瞬态首次失败或重试失败后，调用 archive.fetch 并传入 source_id；archive.fetch 至多一次且 source_id 是其唯一业务参数。

当前表示：block_005 的 ir_011 是唯一 archive.fetch 操作，输入 external_resource/archive.fetch 与 result_001(source_id)，没有 result_002(FAST_KEY)；edges/3、edges/6、edges/8 分别从缺失、非瞬态首次失败、重试失败进入该块；edges/9/edges/10 区分 archive 成功与失败；graph /constraints/2、/constraints/3 与 block/op 约束复述调用条件、至多一次和唯一参数。

比较理由：回退触发路径、调用对象、业务参数、次数上界及结果出口均保留。external_resource 为资源输入，不增加或减少业务实参；图中没有第二个 archive.fetch 操作或回到该块的循环。

源文 `src_003` · `SKILL.md:8-8`：

> if it is absent, go directly to archive.fetch without calling fast.fetch.

源文 `src_004` · `SKILL.md:10-10`：

> After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

源文 `src_005` · `SKILL.md:12-12`：

> Call archive.fetch at most once and pass source_id as its only argument.

图位置："/constraints/2"

图位置："/constraints/3"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/outputs/1"

图位置："/blocks/block_006/instructions/0/outputs/2"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/edges/3"

图位置："/edges/6"

图位置："/edges/8"

图位置："/edges/9"

图位置："/edges/10"

## finding_7 · semantic · represented

原文要求：任一工具成功时，原样返回该成功响应的 body，并且不再发起 fetch 调用。

当前表示：首次 fast.fetch 成功的 edges/4 指向 block_006，其 return 输入 result_005(fast_fetch_body)；重试成功的 edges/7 指向 block_007，其 return 输入 result_007(fast_fetch_retry_body)；archive.fetch 成功的 edges/9 指向 block_008，其 return 输入 result_009(archive_fetch_body)；三个 return 块均无后继边；graph /constraints/4 与各块/操作约束复述成功返回和不再 fetch。

比较理由：三条成功路径分别返回对应成功响应的 body，结果标识未互换；return 是终结操作且无出边，满足不再 fetch。

源文 `src_005` · `SKILL.md:12-12`：

> On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

图位置："/constraints/4"

图位置："/blocks/block_007/constraints/0"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_008/constraints/0"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/constraints/0"

图位置："/blocks/block_009/constraints/0"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/constraints/0"

图位置："/edges/4"

图位置："/edges/7"

图位置："/edges/9"

## finding_8 · semantic · represented

原文要求：若 archive.fetch 失败，停止并返回其错误；不重试 archive.fetch。

当前表示：edges/10 在 archive.fetch failed 时指向 block_010；其 return 输入 result_010(archive_fetch_error)，且无边后继；图中仅有一个 archive.fetch 操作；graph /constraints/5 与 block/op 约束复述失败停止、返回错误及不重试。

比较理由：失败出口、返回结果身份和终止性均有记录。单次 archive.fetch 操作与无回边共同支持不重试。

源文 `src_006` · `SKILL.md:14-14`：

> If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/constraints/5"

图位置："/blocks/block_010/constraints/0"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/inputs/0"

图位置："/blocks/block_010/instructions/1/constraints/0"

图位置："/edges/10"

## finding_9 · semantic · represented

原文要求：在整个工作流中，绝不把 FAST_KEY 传给 archive.fetch 或诊断输出。

当前表示：graph /constraints/6、block_005 约束/1 及 archive.fetch 操作约束/1 记录该禁止；archive.fetch 操作的输入只有 external_resource/archive.fetch 与 result_001(source_id)，没有 result_002(FAST_KEY)；受控图中没有接收 FAST_KEY 的诊断输出操作。

比较理由：禁止要求以图级和相关作用域约束声明记录，且实际 archive.fetch 输入未出现 FAST_KEY。无诊断输出操作把 FAST_KEY 作为输入。上下文键声明本身不等于向诊断输出传递。

源文 `src_006` · `SKILL.md:14-14`：

> Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/constraints/6"

图位置："/blocks/block_006/constraints/1"

图位置："/blocks/block_006/instructions/0/constraints/1"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

## finding_10 · semantic · represented

原文要求：每条成功或失败返回路径返回前，先把最终状态追加到本地 status.txt。

当前表示：block_006/7/8/9 在各自 return 前均有 append_final_status_to_status_file：输入 literal "success" 或 "failure" 与 external_resource/status.txt；指令顺序为先 append 后 return；graph /constraints/7 与各块/操作约束复述该要求。

比较理由：四个 return 块覆盖全部成功/失败终态路径，且 append 操作位于 return 之前。源文未规定状态字面量，"success"/"failure" 是该要求的合法具体表达；external_resource 不必然表示远端，status.txt 作为本地相对文件名与 local status.txt 相容。

源文 `src_007` · `SKILL.md:16-16`：

> Before returning from every success or failure path, append the final status to local status.txt.

图位置："/constraints/7"

图位置："/blocks/block_007/constraints/1"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_008/constraints/1"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_009/constraints/1"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/constraints/0"

图位置："/blocks/block_010/constraints/1"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/constraints/0"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

尚无已保存的助手逐例复核。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
