# 015-source-fetch-with-fallback · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：F03；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：9f79230a22497d54d2a8ceba8a14ec0d642e8b987b52fca16a6c81819026a3ea；源文 SHA-256：f628c93b4c944d1cba8b91f8492ad8bd59cbf7fcb570d6f076bd248390945c9d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/015/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/015/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 的 name/description 与标题仅为技能上下文/标题，不是业务步骤要求。

当前表示：受控回述以 entry 和 contexts 记录工作流入口与上下文键 user_request、environment；未将名称/描述建成业务操作。

比较理由：按 context 核对，这些内容不要求建成业务步骤；受控回述的入口和上下文声明足以说明其上下文地位。

源文 `src_001` · `SKILL.md:2-2`：

> name: source-fetch-with-fallback

源文 `src_001` · `SKILL.md:3-3`：

> description: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.

源文 `src_002` · `SKILL.md:6-6`：

> # Source Fetch With Fallback

图位置："/entry_block_id"

图位置："/declared_context_keys"

## finding_2 · semantic · represented

原文要求：源文第1行要求从用户请求读取 source_id，并从环境读取 FAST_KEY。

当前表示：受控回述 block_001 的 read_source_id_from_request 以 context_key user_request 为输入并输出 result_001/source_id；block_002 的 read_fast_key_from_environment 以 context_key environment 为输入并输出 result_002/fast_key；edge0 连接两者。

比较理由：动作、对象、来源和结果标识均有对应记录，顺序先后不改变读取两项输入的要求。

源文 `src_003` · `SKILL.md:10-10`：

> | 1 | input | Read source_id from the user's request and read FAST_KEY from the environment. |

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

原文要求：源文第2行要求：FAST_KEY 存在时先用 source_id 和 FAST_KEY 调用 fast.fetch；FAST_KEY 不存在时直接走 archive.fetch，不调用 fast.fetch。

当前表示：block_003 check_fast_key_present 消费 result_002，输出 result_003，dispatch 消费 result_003；edge2 在 FAST_KEY present 时到 block_004 first fast.fetch，edge3 在 absent 时直接到 block_008 archive.fetch；block_004 的 fast_fetch 输入为 fast.fetch 资源、result_001/source_id、result_002/fast_key，输出 result_004/005/006，dispatch 消费 first_fast_error 与 transient 标记。

比较理由：present 分支调用 fast.fetch 并带 source_id 与 FAST_KEY，absent 分支直接走 archive.fetch 而不经过 fast.fetch，条件与输入对象保留。

源文 `src_003` · `SKILL.md:11-11`：

> | 2 | preferred | If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch. |

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

图位置："/blocks/block_004/instructions/1/inputs/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

## finding_4 · semantic · represented

原文要求：源文第3行要求：仅当 fast.fetch 首次尝试因 transient error 失败时重试一次；不得重试 non-transient 首次失败。

当前表示：block_006 retry fast_fetch 带块级约束：仅在首次尝试为 transient error 时重试一次且不重试 non-transient；其输入为 fast.fetch 资源、result_001/source_id、result_002/fast_key，输出 result_007/retry_fast_body 与 result_008/retry_fast_error；edge5 transient 首次失败到 retry，edge6 non-transient 首次失败到 archive.fetch，edge7 retry 成功到返回，edge8 retry 失败到 archive.fetch，无回边到 retry。

比较理由：transient 条件、恰好一次、non-transient 不重试以及失败后转 fallback 均有记录。

源文 `src_003` · `SKILL.md:12-12`：

> | 3 | retry | Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure. |

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/inputs/2"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/outputs/1"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/inputs/0"

图位置："/blocks/block_006/instructions/1/metadata"

图位置："/edges/5"

图位置："/edges/6"

图位置："/edges/7"

图位置："/edges/8"

## finding_5 · semantic · represented

原文要求：源文第4行要求：non-transient 首次失败或 fast.fetch 任意重试失败后，用 source_id 调用 archive.fetch。

当前表示：edge6 将 non-transient first failure 指向 block_008 archive.fetch；edge8 将 failed retry 指向 block_008；block_008 的 archive_fetch 输入 result_001/source_id。

比较理由：源文要求的两个 fallback 触发条件都到达 archive.fetch，并传递 source_id。

源文 `src_003` · `SKILL.md:13-13`：

> | 4 | fallback | After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id. |

图位置："/edges/6"

图位置："/edges/8"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

## finding_6 · semantic · represented

原文要求：源文第5行要求：archive.fetch 至多调用一次，且只传 source_id 作为其唯一参数。

当前表示：block_008 有块级约束：archive.fetch 至多一次且只传 source_id；实际只有一个 archive_fetch 操作，输入为 external_resource archive.fetch（工具标识，非业务实参）与 result_001/source_id，没有其他业务实参；无 retry archive 边。

比较理由：按 IR-RESOURCE，external_resource 是资源标识，不应当作额外业务参数；source_id 是唯一业务参数，单一操作和无重试边支持至多一次。

源文 `src_003` · `SKILL.md:14-14`：

> | 5 | archive | Call archive.fetch at most once and pass source_id as its only argument. |

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/constraints/0"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/outputs/0"

图位置："/blocks/block_008/instructions/0/outputs/1"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/inputs/0"

图位置："/blocks/block_008/instructions/1/metadata"

图位置："/edges/3"

图位置："/edges/6"

图位置："/edges/8"

图位置："/edges/9"

图位置："/edges/10"

## finding_7 · semantic · represented

原文要求：源文第6行要求：任一工具成功时，返回该成功响应的 body 值且保持不变，并停止任何后续 fetch 调用。

当前表示：constraints/2 记录该要求；first fast success edge4 到 block_005，retry success edge7 到 block_007，archive success edge9 到 block_009；这些块先 append_final_status_to_local_file，再用 result_004、result_007、result_009 分别返回对应 body，且无后续 fetch 边。

比较理由：各成功路径返回的是对应成功响应的 body 结果标识，success 后无 fetch 出边。

源文 `src_003` · `SKILL.md:15-15`：

> | 6 | return | On either tool's success, return that successful response's body value unchanged and make no further fetch calls. |

图位置："/constraints/2"

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/inputs/0"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/inputs/0"

图位置："/blocks/block_007/instructions/1/metadata"

图位置："/blocks/block_009/block_id"

图位置："/blocks/block_009/block_name"

图位置："/blocks/block_009/data_source_kind"

图位置："/blocks/block_009/instructions"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/metadata"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/1/inputs/0"

图位置："/blocks/block_009/instructions/1/metadata"

图位置："/edges/4"

图位置："/edges/7"

图位置："/edges/9"

## finding_8 · semantic · represented

原文要求：源文第7行要求：archive.fetch 失败时停止并返回其错误；不得重试 archive.fetch。

当前表示：block_010 有块级约束：archive.fetch 失败时停止并返回错误，不重试 archive.fetch；edge10 archive failed 到 block_010；block_010 先 append status，再 return result_010/archive_error，且无出边。

比较理由：失败错误身份为 result_010，返回前 append 状态符合 status 要求，无 archive retry。

源文 `src_003` · `SKILL.md:16-16`：

> | 7 | stop | If archive.fetch fails, stop and return its error; do not retry archive.fetch. |

图位置："/blocks/block_010/block_id"

图位置："/blocks/block_010/block_name"

图位置："/blocks/block_010/data_source_kind"

图位置："/blocks/block_010/constraints/0"

图位置："/blocks/block_010/instructions"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/metadata"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/1/inputs/0"

图位置："/blocks/block_010/instructions/1/metadata"

图位置："/edges/10"

## finding_9 · semantic · represented

原文要求：源文第8行要求：整个工作流中不得把 FAST_KEY 传给 archive.fetch 或 diagnostic output。

当前表示：constraints/0 记录禁止把 FAST_KEY 传给 archive.fetch 或 diagnostic output；archive_fetch 输入不含 result_002/fast_key；各 append/return 路径输入为 status.txt 与 body/error，也不含 fast_key；图中无 diagnostic output 操作。

比较理由：声明约束与实际输入绑定一致，未发现把 FAST_KEY 传给 archive.fetch 或诊断输出的记录。

源文 `src_003` · `SKILL.md:17-17`：

> | 8 | global constraint | Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow. |

图位置："/constraints/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0/inputs/1"

图位置："/blocks/block_010/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0/inputs/1"

## finding_10 · semantic · represented

原文要求：源文第9行要求：从每个成功或失败路径返回前，先把 final status 追加到本地 status.txt。

当前表示：constraints/1 记录该要求；所有 return 操作（block_005、block_007、block_009、block_010 的 return）之前都有 append_final_status_to_local_file，append 输入含 status.txt 和相应 body/error。

比较理由：图中每个 return 前均有 append 到 status.txt，覆盖成功路径和 archive 失败路径。

源文 `src_003` · `SKILL.md:18-18`：

> | 9 | status | Before returning from every success or failure path, append the final status to local status.txt. |

图位置："/constraints/1"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_009/instructions/0"

图位置："/blocks/block_009/instructions/1"

图位置："/blocks/block_009/instructions/0/inputs/0"

图位置："/blocks/block_010/instructions/0"

图位置："/blocks/block_010/instructions/1"

图位置："/blocks/block_010/instructions/0/inputs/0"

## 安全标注未决

- {"instruction_id": "ir_007", "field": "effects", "reason": "无法确定是否发生 net_send/net_receive：CFG 仅记录 fast.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。"}
- {"instruction_id": "ir_011", "field": "effects", "reason": "无法确定是否发生 net_send/net_receive：CFG 仅记录 fast.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。"}
- {"instruction_id": "ir_015", "field": "effects", "reason": "无法确定是否发生 net_send/net_receive：CFG 仅记录 archive.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：9f79230a22497d54d2a8ceba8a14ec0d642e8b987b52fca16a6c81819026a3ea

助手复核：主要控制路径与返回身份保留，但四次final status追加实际依赖body/error且映射未说明，核对器仅查存在/顺序而判通过，属于重要假通过候选；安全标注也有主体及空标签/未决口径问题。

- 本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。
- 重要核对漏项：四个 append_final_status_to_local_file（ir_009/013/017/019）的实际业务输入依次绑定 result_004 first_fast_body、result_007 retry_fast_body、result_009 archive_body、result_010 archive_error。源文要求追加 final status，图没有显式状态值或 body/error 到最终状态的转换说明；不能只凭 opcode 名称和图级约束认定写入内容正确。 已核查四追加操作各自 constraints=[]、metadata={}，相关块也没有 body/error→status 的映射解释；仅图级约束重复追加最终状态的要求。
- finding_10 的 actual_representation 已明确列出 append 输入为相应 body/error，但 reason 只检查所有 return 前存在 append，最终仍判 represented。这是对写入对象/数据身份核对不足的假通过候选；建议澄清或修正四个追加操作的数据绑定，明确记录各终态的状态值或有依据的状态产生关系。开放 opcode 未定义内部执行，不能据此断言已经把完整 body/error 写盘或实际泄露，但同样不能宣称 final status 已准确表达。 这一表示缺口会影响后续传播：按实际依赖会将body/error关联到写入点，若凭动作名称改解释为只有状态，又可能凭空减小数据范围；应先澄清表达，再分析传播，不在此判断实际泄露。
- 其他关键路径保留：user_request 读取 source_id、environment 读取 FAST_KEY；存在密钥才首次 fast.fetch，缺失直接 archive。首次 transient 失败只重试一次，non-transient 首次失败和任意重试失败回退；archive 单次、无重试。fast 参数只有 source_id/key，archive 只有 source_id，工具资源标识不计业务实参。
- 成功返回绑定正确：首次/重试/archive 分别返回 result_004/result_007/result_009 的各自 body，不混用首次与重试结果；archive 失败返回 result_010 error，所有成功终态无后续fetch。密钥禁传声明保留，archive和追加的直接输入均没有FAST_KEY；这不代表传播后密钥绝无暴露。
- 当前10块20IR、r000 audit_passed，9个业务项均represented。助手保留这一模型原判，同时明确最终状态写入的表示缺口尚未被有效核对消除；不得以核对器通过替代语义正确性。
- 20/20 profile及全部证据已阅读。两源读取为source/context_read，key存在性检查为transformer/transform，三工具source/sink并按EM02标model_observe，四追加sink/fs_write，return仅sink。文件写入效果本身有依据，但profile解释“追加最终状态”继承了原文/动作名，未澄清当前输入其实为body/error；安全效果标签不能替代第一阶段的写入内容核对。
- 3项unresolved分别为三工具的网络发送/接收边界，符合EM06，比014直接推定网络更谨慎。四return却以无充分效果依据记录空effects、没有接收方未决，与013同义场景的口径不一致；未确认接收方时，空标签不能当作无用户/模型暴露保证。
- 6个dispatch actor=llm仅引用EM03“LLM调度不等于内容可见”，仍不足以确定实际执行主体。context读和存在性检查被推定本地runtime，其对模型是否可见也未明确；后续传播应保存这些执行边界的不确定性，不从缺少model_observe反推隔离。
- 本复核仅使用本次表格式F03冻结源文与新提取r000末图，不借用旧固定F03第3轮基线。未修改当前audit/图/profile，不追加模型调用，结论是助手复核而非用户确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
