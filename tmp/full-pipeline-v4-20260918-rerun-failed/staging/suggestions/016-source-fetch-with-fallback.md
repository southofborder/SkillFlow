# 016-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F04；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 执行来源：复用父运行记录（本次未重新调用模型）；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：e7e3d42c2280d4c534c66a0380c5727c1a69085f4ed426df4ca420b2724d882d；源文 SHA-256：876c4f8d92b6b511382465efa20224df250ab505384696c91095ad29e96d8b4d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/016/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/016/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：本项是 SKILL.md 的名称、描述、标题，以及 workflow.md 标题等上下文/标签信息，不是额外业务步骤。

当前表示：受控回述以入口、contexts、各块 key/id/name/source/instructions 以及空 metadata_json 保留图结构、标签和记录顺序；未把这些标签或元数据当作新的业务动作。

比较理由：源文这些内容是上下文、标题和元数据；受控单元只说明入口、上下文键、块元数据、名称和指令记录顺序。按 context 的 represented 含义，只表示其上下文地位已说明，不作为业务要求通过。

源文 `src_001` · `SKILL.md:1-4`：

> name: source-fetch-with-fallback
> description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

源文 `src_004` · `references/workflow.md:1-1`：

> # Fetch workflow

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

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0/metadata"

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

## finding_2 · semantic · represented

原文要求：SKILL.md 要求遵循 workflow instructions，并说明该文件属于当前工作流；这是指向工作流要求的元指引。

当前表示：受控回述把 workflow.md 的要求纳入同一受控图：entry、constraints/0-11 声明要求，blocks/0-8 的指令清单和 edges/0-9 记录对应控制流；没有另设读取 SKILL.md 的业务操作。

比较理由：源文没有要求一个额外的“读取 SKILL.md”动作，只要求遵循被引用工作流。受控回述以约束和实际块/边展开这些要求，未把元指引漏掉，也未新增业务步骤。

源文 `src_003` · `SKILL.md:8-8`：

> Follow the requirements in [workflow instructions](references/workflow.md); this file is part of the current workflow.

图位置："/entry_block_id"

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/constraints/3"

图位置："/constraints/4"

图位置："/constraints/5"

图位置："/constraints/6"

图位置："/constraints/7"

图位置："/constraints/8"

图位置："/constraints/9"

图位置："/constraints/10"

图位置："/constraints/11"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_009/instructions"

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

图位置："/edges/8"

图位置："/edges/9"

## finding_3 · semantic · represented

原文要求：从用户请求读取 source_id，并从环境读取 FAST_KEY。

当前表示：block_001 的 ir_001 使用 read_source_id_from_user_request，输入 context_key/source_id，输出 result_001；block_002 的 ir_003 使用 read_fast_key_from_environment，输入 context_key/FAST_KEY，输出 result_002；edge 从 block_001 指向 block_002；contexts 声明两个键。

比较理由：两个动作、对象与来源均保留：source_id 对应用户请求读取操作，FAST_KEY 对应环境读取操作；记录顺序为 source_id 后 FAST_KEY，与源文列举顺序一致。未发现对象、绑定或次数差异。

源文 `src_005` · `references/workflow.md:3-3`：

> Read source_id from the user's request and read FAST_KEY from the environment.

图位置："/declared_context_keys"

图位置："/constraints/0"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/inputs/0"

图位置："/edges/0"

## finding_4 · semantic · represented

原文要求：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 尝试 fast.fetch；若不存在，直接走 archive.fetch，且不调用 fast.fetch。

当前表示：edge/1 从 FAST_KEY 读取块到 fast.fetch 首次尝试块，条件为 FAST_KEY present；edge/2 到 archive.fetch 块，条件为 FAST_KEY absent。fast.fetch 首次尝试 ir_005 输入 fast.fetch、result_001(source_id)、result_002(FAST_KEY)；缺席边绕过 fast.fetch 块。

比较理由：存在/缺席条件、首批工具选择、调用对象和两个业务参数均保留；FAST_KEY absent 路径没有 fast.fetch 前置块。未发现多传参数或少传 source_id/FAST_KEY。

源文 `src_006` · `references/workflow.md:5-5`：

> If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

图位置："/constraints/1"

图位置："/blocks/block_003/constraints/0"

图位置："/blocks/block_003/constraints/1"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/inputs/2"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/0/outputs/2"

图位置："/blocks/block_003/instructions/0/outputs/3"

图位置："/blocks/block_003/instructions/0/constraints/0"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/inputs/0"

图位置："/blocks/block_003/instructions/1/inputs/1"

图位置："/edges/1"

图位置："/edges/2"

## finding_5 · semantic · represented

原文要求：fast.fetch 仅在第一次尝试因 transient error 失败时恰好重试一次；非 transient 首次失败不得重试。非 transient 首次失败或任意重试失败后，用 source_id 调 archive.fetch。重试策略来自 retry 配置且仅用于 fast.fetch：fast.fetch max_attempts=2、retry_first_error=transient_only；archive.fetch max_attempts=1。

当前表示：首次 fast.fetch 的 dispatch 输入 result_005 成功标志和 result_006 transient 标志；edge/4 在 transient 首次失败时进入重试块，edge/5 在 non-transient 首次失败时去 archive.fetch。重试块 ir_007 带 source_id、FAST_KEY，约束声明这是唯一一次重试且之后不得再重试；edge/7 在重试失败时去 archive.fetch。graph constraints/2,3,4,10,11 记录重试规则和配置值。

比较理由：重试次数、触发条件、禁止条件、重试对象、重试参数和失败后回退对象均保留；archive.fetch 没有重试路径，配置 max_attempts=1 与 cfg 一致。未发现把重试策略应用到 archive.fetch 或遗漏 non-transient/重试失败回退。

源文 `src_007` · `references/workflow.md:7-9`：

>   - Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
>   - After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

源文 `src_008` · `references/workflow.md:11-11`：

> The same retry policy is specified by [retry configuration](../retry.yaml); apply it to fast.fetch only.

源文 `src_014` · `retry.yaml:1-5`：

> fast_fetch:
>   max_attempts: 2
>   retry_first_error: transient_only
> archive_fetch:
>   max_attempts: 1

图位置："/constraints/2"

图位置："/constraints/3"

图位置："/constraints/4"

图位置："/constraints/10"

图位置："/constraints/11"

图位置："/blocks/block_004/constraints/0"

图位置："/blocks/block_004/constraints/1"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/outputs/1"

图位置："/blocks/block_004/instructions/0/outputs/2"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/inputs/0"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

## finding_6 · semantic · represented

原文要求：archive.fetch 最多调用一次，且 source_id 是唯一业务参数；任何地方不得把 FAST_KEY 传给 archive.fetch 或诊断输出。

当前表示：图中只有一个 archive.fetch 操作 ir_009，输入为 external_resource/archive.fetch 和 result_001(source_id)，没有 result_002(FAST_KEY)。graph/block/operation 级约束分别记录 at most once、source_id only argument、Never pass FAST_KEY；append 状态操作也只接收 local status.txt 和 success/failure 字面量。

比较理由：external_resource 在这里是调用目标而非业务参数，因此 source_id 是唯一业务参数。单操作且无回边保证结构上最多一次；FAST_KEY 未绑定到 archive.fetch 或状态输出，满足禁传要求。

源文 `src_009` · `references/workflow.md:13-13`：

> Call archive.fetch at most once and pass source_id as its only argument.

源文 `src_012` · `references/workflow.md:19-19`：

> > Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.

图位置："/constraints/5"

图位置："/constraints/6"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/constraints/1"

图位置："/blocks/block_005/constraints/2"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/outputs/1"

图位置："/blocks/block_005/instructions/0/outputs/2"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_005/instructions/0/constraints/2"

图位置："/blocks/block_005/instructions/0/constraints/3"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/edges/2"

图位置："/edges/5"

图位置："/edges/7"

## finding_7 · semantic · represented

原文要求：任一工具成功时，原样返回该成功响应的 body 值，并且不再发起 fetch 调用。

当前表示：fast.fetch 首次成功经 edge/3 到 block_006，append 状态后 return result_003(first attempt body)；重试成功经 edge/6 到 block_007，append 后 return result_007(retry body)；archive.fetch 成功经 edge/8 到 block_008，append 后 return result_010(archive body)。三个 return 操作都有“原样返回 body、不再 fetch”的约束且无后继。

比较理由：成功分支覆盖首次 fast.fetch、重试 fast.fetch 和 archive.fetch；返回身份分别是对应成功响应的 body，未返回 error、success flag 或未重试/首次响应混用。append 是返回前的必要状态记录，不是 fetch。

源文 `src_010` · `references/workflow.md:15-15`：

> On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

图位置："/constraints/7"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/constraints/0"

图位置："/blocks/block_006/instructions/1/constraints/1"

图位置："/blocks/block_007/constraints/0"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/constraints/0"

图位置："/blocks/block_007/instructions/1/constraints/1"

图位置："/blocks/block_008/constraints/0"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/constraints/0"

图位置："/blocks/block_008/instructions/1/constraints/1"

图位置："/edges/3"

图位置："/edges/6"

图位置："/edges/8"

## finding_8 · semantic · represented

原文要求：若 archive.fetch 失败，停止并返回其 error；不得重试 archive.fetch。

当前表示：edge/9 从 archive.fetch 块到失败返回块，条件为 archive.fetch fails；该块 ir_017 先 append failure，再由 ir_018 return result_011(archive_fetch_error)。块和操作约束记录 stop、return error、do not retry；该块无后继。

比较理由：失败条件、停止、返回身份和禁止重试均保留；返回的是 archive.fetch 的 error，而不是 body 或其他工具的错误。append 在返回前执行，符合全局状态记录要求。

源文 `src_011` · `references/workflow.md:17-17`：

> If archive.fetch fails, stop and return its error; do not retry archive.fetch.

图位置："/constraints/8"

图位置："/blocks/block_009/constraints/0"

图位置："/blocks/block_009/constraints/1"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/constraints/0"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/constraints/0"

图位置："/blocks/block_009/instructions/1/constraints/1"

图位置："/edges/9"

## finding_9 · semantic · represented

原文要求：在从每个成功或失败路径返回之前，把 final status 追加到 local status.txt。

当前表示：四个终止返回块都在 return 前有 append_final_status_to_local_status_txt：block_006 和 block_007、block_008 追加 literal "success"，block_009 追加 literal "failure"；输入统一为 external_resource/local status.txt 加状态字面量，操作约束声明在返回前追加。

比较理由：所有实际终止返回路径均覆盖：首次 fast.fetch 成功、重试成功、archive.fetch 成功、archive.fetch 失败；fast.fetch 失败若不终止则走 archive.fetch，最终在 archive 的终止路径追加。源文未规定状态字符串格式，受控中的 success/failure 是具体表示，不改变“append final status”的业务要求。

源文 `src_013` · `references/workflow.md:21-21`：

> Before returning from every success or failure path, append the final status to local status.txt.

图位置："/constraints/9"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/constraints/0"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：e7e3d42c2280d4c534c66a0380c5727c1a69085f4ed426df4ca420b2724d882d

助手复核：跨文件重试/回退与全部终态正确；标注虽complete，网络标签缺远端依据、return未知与LLM执行/观察边界仍未澄清。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 跨文件源文全部核对：SKILL.md指向references/workflow.md，workflow引用retry.yaml；fast_fetch max_attempts=2、retry_first_error=transient_only与archive_fetch max_attempts=1均进入约束与实际控制路径，没有把配置读取或文档链接额外建成业务调用。
- 新图9块18IR：source_id与FAST_KEY读取来源保留；有key才首次fast，缺key直接archive；首次transient才一次重试，non-transient首次失败/任意retry失败回退；archive仅source_id业务参数且不重试。三成功分别返回result_003/007/010的本次body，失败返回result_011 archive_error，没有继续fetch。
- 四终态在return前实际追加status.txt，3条success与1条failure字面量明确表示最终状态；未规定记录格式，字面量方案可接受。与015不同，本例没有将body/error绑定到追加内容。FAST_KEY禁传声明保留、archive与状态写入实际输入也无key；不据此断言传播后绝无泄露。
- 第0轮audit_passed、8业务项represented；对照全部源文件和当前图，助手未发现关键流程遗漏或错误返回，结论不是语义等价证明。全部18份profile及标签证据已阅读。context_read、三工具source/sink、四写入sink/fs_write与EM02工具回传model_observe均有对应动作或公开假设。
- 重要标注依据问题：ir_005/007的net_send引文仅为description中的credential-gated preferred tool，ir_009为bounded archive fallback；net_receive只引用各body输出。凭据、工具调用和body响应均不能证明远端通信，违反EM06。三工具的6个网络标签因此属于证据不足推断，应补网络部署依据或记录未决，而非因complete视作已确认。
- 四return effects为空且无接收方未决，依据只为普通return不能单独证明用户输出。该限制不能证明没有适用效果；与013同义场景7项未决相比，本例没有补充网络/接收方信息，complete代表记录合法，不表示不确定性被解决。
- 执行主体/观察口径仍不稳定：本例source_id读取标llm+model_observe，FAST_KEY读取标runtime+context_read；全部dispatch和return归llm，多借EM03或“工作流执行者”推断，源文并未限定这些实现。尤其dispatch ir_004实际依赖fast_key_value，不应仅因其叫控制操作便把LLM实际用值的可见性问题抹掉；也不能据此断言key已经泄露。需要明确执行机制，再确定观察边界。
- 本次复核未修改图、标签、历史记录或配置，没有执行被引文档内工具/脚本；仅保存独立助手意见，不冒充用户人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
