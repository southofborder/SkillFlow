# 013-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F01；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64；源文 SHA-256：fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/013/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/013/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文前言/标题提供名称与背景：name: source-fetch-with-fallback；description 为使用凭据门控的首选工具与有界归档回退获取一个 source；标题为 Source Fetch With Fallback。

当前表示：受控回述未单独记录 frontmatter/name/description/title；其入口、块和边结构体现单 source、FAST_KEY 门控的 fast.fetch 与至多一次 archive.fetch 回退。

比较理由：这些内容属于非规范性背景与标签，不是新增业务步骤；按 context 记录其上下文地位即可。

源文 `src_001` · `SKILL.md:2-2`：

> name: source-fetch-with-fallback

源文 `src_001` · `SKILL.md:3-3`：

> description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

## finding_2 · semantic · represented

原文要求：读取 source_id（来自用户请求）并读取 FAST_KEY（来自环境）。

当前表示：受控回述声明 /contexts 含 source_id、FAST_KEY；block_001 的 read_source_id 以 context_key source_id 为输入并输出 result_001；block_002 的 read_fast_key 以 context_key FAST_KEY 为输入并输出 result_002/result_003；edge0 从 block_001 连到 block_002。

比较理由：两个读取动作、对象标识和先后连接均记录；FAST_KEY 的块名保留 environment 来源，实际以 context_key 记录为上下文键，未新增其他读取来源。

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

图位置："/blocks/block_002/instructions/0/outputs/1"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/edges/0"

## finding_3 · semantic · represented

原文要求：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 调用 fast.fetch；若不存在，直接调用 archive.fetch，不调用 fast.fetch。

当前表示：block_002 的 constraint/0 记录该条件；dispatch ir_004 使用 result_003 fast_key_present；edge1 为 FAST_KEY present→block_003，edge2 为 FAST_KEY absent→block_005；block_003 的 fast.fetch 输入为 external_resource fast.fetch、result_001 source_id、result_002 fast_key。

比较理由：present 分支进入 fast.fetch 并绑定两个业务参数；absent 分支直接进入 archive.fetch 块，且图中没有 absent 到 fast.fetch 的边。

源文 `src_003` · `SKILL.md:9-9`：

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/blocks/block_002/constraints/0"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/edges/1"

图位置："/edges/2"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/inputs/2"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/0/outputs/2"

图位置："/blocks/block_003/instructions/0/metadata"

## finding_4 · semantic · represented

原文要求：仅当 fast.fetch 首次尝试因 transient error 失败时重试恰好一次；不得因 non-transient 首次失败而重试。

当前表示：block_003 的 constraint/0 声明 exactly once only transient 且 no non-transient retry；edge3 transient→block_004；edge4 non-transient→block_005；block_004 的 ir_007 为唯一 fast.fetch 重试，输入 source_id 与 fast_key，未见第二次重试或回边。

比较理由：重试块仅由 transient 失败边进入；非 transient 边直接到 archive.fetch，单次重试和禁止条件均有记录。

源文 `src_003` · `SKILL.md:10-10`：

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/edges/3"

图位置："/edges/4"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/constraints/0"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/outputs/2"

图位置："/blocks/block_004/instructions/0/metadata"

## finding_5 · semantic · represented

原文要求：在 non-transient 首次失败后，或在 fast.fetch 任一次重试失败后，用 source_id 调用 archive.fetch。

当前表示：block_003 的 constraint/0 记录 non-transient first failure→archive.fetch；edge4 non-transient→block_005；block_004 的 constraint/1 记录 any failed retry→archive.fetch；edge7 retry failed→block_005；archive.fetch 的 source_id 绑定由 inputs/1 link 指向 result_001。

比较理由：两个触发条件分别记录，并都汇合到 block_005 的 archive.fetch 调用；参数为 source_id。

源文 `src_003` · `SKILL.md:11-11`：

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

图位置："/blocks/block_003/constraints/0"

图位置："/edges/4"

图位置："/blocks/block_004/constraints/1"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/edges/7"

图位置："/blocks/block_005/instructions/0/inputs/1"

## finding_6 · semantic · represented

原文要求：archive.fetch 至多调用一次，且只传入 source_id 作为业务参数。

当前表示：block_005 的 constraint/0 原文记录 at most once 和 source_id as only argument；block_005 只有单个 ir_009 archive.fetch，输入为 external_resource archive.fetch 和 result_001 source_id，无第二个 archive.fetch 操作或重试边。

比较理由：external_resource 是工具标识而非业务参数，业务参数仅 source_id；单操作和约束保留 at most once。

源文 `src_003` · `SKILL.md:12-12`：

> 5. Call archive.fetch at most once and pass source_id as its only argument.

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/outputs/1"

图位置："/blocks/block_005/instructions/0/outputs/2"

图位置："/blocks/block_005/instructions/0/metadata"

## finding_7 · semantic · represented

原文要求：任一工具成功时，原样返回该成功响应的 body value，且不再发起 fetch 调用。

当前表示：图级 /constraints/2 记录该要求；edge5 first attempt succeeded→block_006、edge6 retry succeeded→block_007、edge8 archive.fetch succeeded→block_008；block_006 return result_004 fast_fetch_first_body，block_007 return result_007 fast_fetch_retry_body，block_008 return result_010 archive_body；这些块无后续 fetch 出边。

比较理由：三条成功路径分别直接返回对应成功调用的 body result，return 终止路径，没有后续 fetch。

源文 `src_003` · `SKILL.md:13-13`：

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

图位置："/constraints/2"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/8"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/metadata"

## finding_8 · semantic · represented

原文要求：若 archive.fetch 失败，停止并返回其 error；不得重试 archive.fetch。

当前表示：block_005 的 constraint/1 原文记录 if fails, stop and return error, do not retry；edge9 archive.fetch failed→block_009；block_009 先 append_status，再 ir_018 return result_011 archive_error；无 archive.fetch 重试操作或边。

比较理由：失败路径返回 archive_error 并终止；append status 是 req9 要求的返回前步骤，不构成 fetch 重试。

源文 `src_003` · `SKILL.md:14-14`：

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/blocks/block_005/constraints/1"

图位置："/edges/9"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/metadata"

## finding_9 · semantic · represented

原文要求：在整个工作流中，绝不把 FAST_KEY 传给 archive.fetch 或 diagnostic output。

当前表示：图级 /constraints/0 原文记录该禁止项；archive.fetch 的 ir_009 输入列表仅有 external_resource archive.fetch 与 result_001 source_id，没有 result_002 FAST_KEY；受控图未记录 diagnostic output 操作。

比较理由：禁止项以图级约束保留，archive.fetch 的实际输入也未绑定 FAST_KEY；无 diagnostic output 操作可违反该禁止项。

源文 `src_003` · `SKILL.md:15-15`：

> 8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/constraints/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

## finding_10 · semantic · represented

原文要求：在每一条成功或失败路径返回前，将 final status 追加到 local status.txt。

当前表示：图级 /constraints/1 原文记录该要求；block_006、block_007、block_008、block_009 各有一个 append_status_to_local_file 操作，均以 external_resource local status.txt 和对应 status result（result_006、result_009、result_012、result_012）为输入，且之后才是 return。

比较理由：四条 return 路径均在 return 前记录 append 操作；状态来源分别对应最终 fast.fetch 首次成功、fast.fetch 重试成功、archive.fetch 成功和 archive.fetch 失败路径。

源文 `src_003` · `SKILL.md:16-16`：

> 9. Before returning from every success or failure path, append the final status to local status.txt.

图位置："/constraints/1"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/metadata"

## 安全标注未决

- {"instruction_id": "ir_005", "field": "effects", "reason": "无法仅凭工具名 fast.fetch 或 external_resource 判断是否向远端发送或接收；EM06 要求不据名称猜测网络通信。"}
- {"instruction_id": "ir_007", "field": "effects", "reason": "无法仅凭工具名 fast.fetch 或 external_resource 判断重试是否向远端发送或接收；EM06 要求不据名称猜测网络通信。"}
- {"instruction_id": "ir_009", "field": "effects", "reason": "无法仅凭工具名 archive.fetch 或 external_resource 判断是否向远端发送或接收；EM06 要求不据名称猜测网络通信。"}
- {"instruction_id": "ir_012", "field": "effects", "reason": "return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。"}
- {"instruction_id": "ir_014", "field": "effects", "reason": "return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。"}
- {"instruction_id": "ir_016", "field": "effects", "reason": "return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。"}
- {"instruction_id": "ir_018", "field": "effects", "reason": "return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64

助手复核：新提取 F01 的重试、回退、密钥禁传直接绑定、四终态追加与返回身份均正确；7 项网络/接收边界未决合理，环境读取的模型可见边界仍须澄清。不是用户人工确认或传播安全结论。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 本次 F01 是从冻结源文重新提取的第 0 轮图，9 块、18 条 IR。分别读取用户 source_id（ir_001/result_001）与环境 FAST_KEY（ir_003/result_002），以 fast_key_present 分派；缺密钥直接到 block_005 archive.fetch，没有走 fast.fetch。
- 重试及回退正确：首次 ir_005 fast.fetch 的 transient 失败边才进入 ir_007 单次重试；首次 non-transient 失败直接 archive；重试任意失败也进入 archive。没有二次重试、archive 重试或重试回环。首次与重试均仅有 source_id、FAST_KEY 两个业务参数，工具 external_resource 不是多传参数。
- archive ir_009 只有 source_id 一个业务输入，缺密钥、首次非暂时错误及重试失败三种入口都汇合到该单次调用。FAST_KEY 未进入 archive 输入；全图保留不得向 archive 或诊断输出传密钥的约束，也没有额外诊断输出操作。此处仅证明图上直接输入/声明如此，不是传播后已无泄露的结论。
- 成功返回身份逐项核对：首次成功 ir_012 返回 result_004（首次 body）；重试成功 ir_014 返回 result_007（重试 body），没有错返首次 body；archive 成功 ir_016 返回 result_010（archive body）。成功终态没有后续 fetch。archive 失败 ir_018 返回 result_011（archive error）并终止。
- 所有四条终态均先追加状态再返回：ir_011/013/015/017 分别消费最终首次状态 result_006、重试状态 result_009 或 archive 状态 result_012，目标均为本地 status.txt；失败出口同样实际有 append。没有仅保留标题/约束而漏掉状态写入的情况，写入格式与写入成功保障仍未规定/证明。
- 第 0 轮 audit_passed、9 个业务项 represented。依据当前真实操作、参数、边和终态，助手未发现影响本例关键过程的漏建、错绑或额外行为；这不是形式化语义等价证明。核对文字个别块名叙述与零基事实索引混用，应以真实 IR ID、证据映射及当前图为定位依据，不能复用旧 F01 节点编号。
- 18/18 份 profile 的所有证据已阅读：两次源读取为 source/context_read；三次工具调用为 tool、source/sink，并以 EM02 记录回传内容的 model_observe；四次追加为 sink/fs_write；四次返回为 sink；dispatch 未硬贴内容效果。全图没有把密钥禁传声明转成遮蔽、加密或 sanitizer，也没有声称 transform 已消除敏感数据。
- 7 项未决为三次 fetch 的网络发送/接收边界及四个 return 的用户/模型接收边界。原文没有工具部署/返回接收者信息，不能凭 fetch 名称或 external_resource 判定远程通信；同样不能把普通 return 直接标 user_output。这些未决是信息边界而非调用失败。
- 需要后续澄清的观察边界：ir_003 读取 FAST_KEY 只标 context_read，actor 解释为本地 runtime，但源文没有明确环境读取通过什么机制回传、是否对 LLM 隔离。EM01 只约束宽读取假设，不推出全部环境或全部密钥已读；EM03 也不保证上下文值对模型不可见。因此目前不能据无 model_observe 标签断言 FAST_KEY 未进入模型，更不能宣称已找全隐式泄露。实际适配/传播阶段应明确该边界，当前保留为助手观察而非改标签。
- 本复核只使用该终态案例的冻结源文、当前末图、有效核对及标注结果；没有改动原件、追溯改判或运行任何 Skill 工具/脚本。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
