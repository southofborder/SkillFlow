# 七例助手复核

此文件是助手的事后复核，尚未经用户确认；模型原始判断、失败响应及自动报告均保持原样。

## c01 · F01 原图（013，第1轮）

执行错误：完整响应末尾多出孤立 Markdown 围栏，未删改后接受；不能判定原图通过。

## c02 · F01 反例：archive 多传密钥

有效命中：明确多传 FAST_KEY，并指出调用与禁传声明冲突。

- `f_data_archive_only_source, f_grounding_archive_conflict`（confirmed_target）：SKILL.md:12、15 要求仅传 source_id 并禁传 FAST_KEY；/blocks/block_011/instructions/0/inputs/2 实际引用环境密钥 result_002。资源定位符与业务参数区分正确。

- `f_order_append_before_return`（explanation_identifier_error）：自由说明文字列出 block_012，而正确的成功返回块为 block_013；结构化 graph_refs 与实际图正确。说明文本的编号错误未被引文校验发现，不改变该项总体结论。

## c03 · F01 反例：失败出口缺少状态追加

执行错误：9 个核对项缺少必填 unknown_cause。原始回答提到缺追加，但不能计为有效命中。

- `f_action_append_failure_missing, f_order_append_before_return_failure, f_ground_internal_conflict_append_failure`（invalid_response_diagnostic_only）：未通过协议校验的原始响应包含失败出口只有 return、残留标题和约束不能补回 append 的诊断。不得据此将执行错误改为有效命中。

## c04 · F01 反例：重试成功返回首次结果

有效命中：实际返回首次 body，未被重试成功标题与约束掩盖。

- `f_data_return_retry_body, f_ground_internal_conflict_retry_body`（confirmed_target）：/blocks/block_010/instructions/1/inputs/0 返回首次 result_004；重试 body 实际为 block_008 定义的 result_008。错转与内部冲突成立。

- `f_guard_retry_outcome`（overly_broad_obligation）：source_requirement 同时写入成功返回 body 与失败回退，整体判 represented，但本项证据仅支持分支去向；返回身份已在另一项判错。应将此项表述限定为分支去向。当前未造成整例假通过，但说明逐项拆分仍依赖模型。

## c05 · F01 反例：新增两秒等待

有效命中：明确两秒等待无原文依据，并定位等待在分支前。

- `finding_10`（confirmed_target）：/blocks/block_007/instructions/1 存在 wait_for_seconds，输入2且约束有秒单位；等待位于 dispatch 前，两个后继均受影响。不是依据不透明名称猜测。

- `finding_20, finding_22`（execution_boundary）：“满足”“有对应实现”只应理解为图中记录了对应操作与次序，不证明文件追加成功或工具内部行为正确。

## c06 · 001 原图（暂停批次第0轮）

18 项业务要求被判为精确保留，助手未确认明确假通过；精确声明不等于运行保证。

- `finding_1, finding_2, finding_4, finding_9, finding_10, finding_12`（declaration_boundary）：precise 针对声明、范围或绑定要求的准确记录，不证明载荷不存在夹带、不证明运行时逐条恰好发送一次；后续传播仍需分析。

- `finding_13, finding_18`（source_interpretation_boundary）：从选中集合计数可以成立，但“处理条数”不能直接等同成功发送条数；原文要求写入在处理完成后，未独立要求计数必须晚于发送。现图次序可接受，不能把额外次序提升成通用义务。

## c07 · 010 原图（暂停批次第0轮）

35 项精确保留、1 项保守保留。四个响应来源按 DEP-MERGE 保留，没有将候选当成同时传递。

- `b6_extract_candidate_inputs`（confirmed_conservative）：四个实际响应结果均被引用，按路径选值未细化的损失被保留。下游 b5、b7、b8 的精确输出绑定不消除该来源精度损失。

- `c1_search_exactly_once, c2_write_return_singular_terminal, gc2_branch_calls_supported`（execution_boundary）：四个静态调用点对应互斥条件分支，不是一次运行调用四次；这些是记录的控制关系，不证明条件求值、可执行性或写入成功。

- `gc3_resource_targets`（source_wording_boundary）：正确区分 external_resource 与远端；把用户提供的 request.json 称为本地文件比原文略强，是说明措辞问题，不是当前图的明确缺陷。

## 保留的限制

三个合法反例结果均支持目标缺陷被发现；第四个反例响应无效，不能宣布四反例全部通过方法验收。原图也没有有效核对结果。

七类字段和引用合法不能保证每项足够原子：c04 的局部混合要求及 c02 的自由说明编号错误均说明这一边界。保守结果不等于必定传递，声明精确不等于运行保证。
