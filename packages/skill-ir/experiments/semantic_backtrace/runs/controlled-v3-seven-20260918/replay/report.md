# 受控语义回述与完整源文核对

运行：`controlled-v3-seven-20260918`；模式：`replay`。

解释契约：`skill-ir-semantic-contract-v1`，SHA-256 `09c8359e0c14a59a0aaa76bd787c25a01db05d2fdb57e26f8be93ccc4044a483`。

唯一模型任务是比较完整原文与受控文本。转换检查、模型判断与外置评测分别报告。

## 差异与未决项

以下保留模型原始有效判定；context 项仅记录非业务上下文，不计为业务语义保留。

### c01 · F01 第 1 轮及其固定变体

执行状态：execution_error

invalid JSON response: Extra data: line 1534 column 1 (char 62228)

### c02 · F01 第 1 轮及其固定变体

保留（模型判定） 21；错转 1；内部冲突 1

表示精度：精确保留 21 项，保守保留 0 项。

逐项修改建议：[suggestions/c02.md](suggestions/c02.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| f_data_archive_only_source / 错转 | archive.fetch 必须只接收 source_id 作为其唯一参数，且不得接收 FAST_KEY。<br>call_archive_fetch 的 inputs 包含 external_resource archive.fetch、result_001/source_id、result_002/fast_key；其中 inputs/2 是与源文相冲突的额外 FAST_KEY 实参。 | 源文 line 12 要求 source_id 为唯一参数，line 15 禁止把 FAST_KEY 传给 archive.fetch；受控 inputs/2 直接违反。 | fact:/blocks/10/instructions/0, fact:/blocks/10/instructions/0/inputs/1, fact:/blocks/10/instructions/0/inputs/2, fact:/blocks/10/instructions/0/constraints/1, fact:/constraints/0, fact:/blocks/10/instructions/0/inputs/1:link, fact:/blocks/10/instructions/0/inputs/2:link |
| f_grounding_archive_conflict / 内部冲突 | 源文禁止将 FAST_KEY 传给 archive.fetch，并要求 archive.fetch 的唯一参数为 source_id。<br>受控图同时声明 fact:/constraints/0 和 fact:/blocks/10/instructions/0/constraints/1 遵守该禁止/唯一参数，但 fact:/blocks/10/instructions/0/inputs/2 将 result_002/fast_key 列入 call_archive_fetch 输入。 | 内部冲突：声明约束与操作输入不一致；从受控事实反查，操作输入无源文依据且与源文冲突。 | fact:/constraints/0, fact:/blocks/10/instructions/0/constraints/1, fact:/blocks/10/instructions/0/inputs/2, fact:/blocks/10/instructions/0/inputs/2:link |

七类检查记录（不构成完整性证明）：

| 核对类别 | 核对项 / 不适用说明 |
|---|---|
| 要求性质与作用域 | f_scope_prohibition |
| 动作与对象 | f_actions_read_source, f_actions_read_fast, f_actions_fast_fetch, f_actions_archive_fetch |
| 数据来源与绑定 | f_data_read_bindings, f_data_fast_args, f_data_archive_only_source, f_data_return_success, f_data_return_error |
| 条件与例外 | f_guards_present, f_guards_absent, f_guards_retry_transient, f_guards_non_transient_no_retry, f_guards_archive_on_failures, f_guards_archive_failure_stop |
| 顺序与依赖 | f_order_read_then_branch, f_order_fast_before_archive, f_order_append_before_return |
| 次数与终止 | f_counts_retry_once, f_counts_archive_once, f_counts_no_further_fetch_success |
| 反向依据与一致性 | f_grounding_archive_conflict |

### c03 · F01 第 1 轮及其固定变体

执行状态：execution_error

9 validation errors for AuditResult
findings.23.unknown_cause
  Field required [type=missing, input_value={'id': 'f_data_check_firs... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.25.unknown_cause
  Field required [type=missing, input_value={'id': 'f_data_check_retr... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.26.unknown_cause
  Field required [type=missing, input_value={'id': 'f_data_check_arch... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.29.unknown_cause
  Field required [type=missing, input_value={'id': 'f_data_status_fil... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.37.unknown_cause
  Field required [type=missing, input_value={'id': 'f_order_read_sour... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.38.unknown_cause
  Field required [type=missing, input_value={'id': 'f_order_append_be... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.40.unknown_cause
  Field required [type=missing, input_value={'id': 'f_order_after_non... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.41.unknown_cause
  Field required [type=missing, input_value={'id': 'f_order_retry_bef... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
findings.42.unknown_cause
  Field required [type=missing, input_value={'id': 'f_order_archive_c... 'unknown_reason': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing

### c04 · F01 第 1 轮及其固定变体

保留（模型判定） 30；错转 1；内部冲突 1

表示精度：精确保留 30 项，保守保留 0 项。

逐项修改建议：[suggestions/c04.md](suggestions/c04.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| f_data_return_retry_body / 错转 | fast.fetch 重试成功后，返回该成功重试响应的 body 原值。<br>block_010 的 return ir_020 在 retry success 路径返回 result_004（first fast.fetch response body），而 retry 操作 ir_015 的 result_008（retry_fast_fetch_response_body）未被返回。 | 受控记录返回了错误的结果身份；首次失败尝试的 body 不能替代重试成功响应的 body。 | fact:/blocks/9/instructions/1, fact:/blocks/9/instructions/1/inputs/0, fact:/blocks/9/instructions/1/inputs/0:link, fact:/blocks/7/instructions/0, fact:/blocks/7/instructions/0/outputs/0 |
| f_ground_internal_conflict_retry_body / 内部冲突 | 无直接源文要求；核对受控声明与操作记录是否冲突。<br>图级约束 fact:/constraints/2 声明任一工具成功时返回该成功响应的 body；但 block_010 在 retry success 路径的 return ir_020 绑定 result_004（first fast.fetch response body），而 retry 操作 ir_015 已定义 result_008（retry_fast_fetch_response_body）未被返回。 | 声明与操作记录对成功响应的身份不一致，构成内部冲突。 | fact:/constraints/2, fact:/blocks/9/instructions/1, fact:/blocks/9/instructions/1/inputs/0, fact:/blocks/9/instructions/1/inputs/0:link, fact:/blocks/7/instructions/0, fact:/blocks/7/instructions/0/outputs/0 |

七类检查记录（不构成完整性证明）：

| 核对类别 | 核对项 / 不适用说明 |
|---|---|
| 要求性质与作用域 | f_norm_no_retry_nontransient, f_norm_never_fastkey_archive, f_norm_never_fastkey_diagnostic, f_norm_no_retry_archive |
| 动作与对象 | f_action_read_source_id, f_action_read_fastkey, f_action_call_fast_first, f_action_append_status, f_action_call_archive, f_action_retry_fast |
| 数据来源与绑定 | f_data_fast_first_args, f_data_return_first_body, f_data_retry_args, f_data_archive_source_id_only, f_data_return_archive_body, f_data_return_archive_error, f_data_return_retry_body |
| 条件与例外 | f_guard_fastkey_presence, f_guard_fastkey_absent_archive, f_guard_first_success, f_guard_transient, f_guard_retry_outcome, f_guard_nontransient_archive, f_guard_archive_outcome |
| 顺序与依赖 | f_order_reads, f_order_checks_after_calls, f_order_append_before_return |
| 次数与终止 | f_count_retry_exactly_once, f_count_archive_at_most_once, f_count_stop_archive_failure, f_count_no_further_fetch_success |
| 反向依据与一致性 | f_ground_internal_conflict_retry_body |

### c05 · F01 第 1 轮及其固定变体

保留（模型判定） 21；无依据新增 1

表示精度：精确保留 21 项，保守保留 0 项。

逐项修改建议：[suggestions/c05.md](suggestions/c05.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_10 / 无依据新增 | 原文第3条只要求 transient 首次失败时重试一次，并未要求任何等待；源文没有 Wait for 2 seconds 或延迟步骤。<br>block_007 在 transient 检查后、dispatch 前记录了 ir_wait_1 opcode wait_for_seconds，输入 literal 2，并有操作级约束 fact:/blocks/6/instructions/1/constraints/0 Wait for 2 seconds before continuing。 | 源文第8至16行中没有 wait、delay、2 seconds 等要求；该操作和约束会给 transient 重试路径，并经同一块的非 transient 路径增加 2 秒等待，属于受控图新增的业务行为。 | fact:/blocks/6/instructions/1, fact:/blocks/6/instructions/1/inputs/0, fact:/blocks/6/instructions/1/constraints/0 |

七类检查记录（不构成完整性证明）：

| 核对类别 | 核对项 / 不适用说明 |
|---|---|
| 要求性质与作用域 | finding_1, finding_2 |
| 动作与对象 | finding_3, finding_10 |
| 数据来源与绑定 | finding_4, finding_7, finding_13, finding_15, finding_16, finding_17 |
| 条件与例外 | finding_5, finding_6, finding_8, finding_11, finding_12, finding_18 |
| 顺序与依赖 | finding_20, finding_21 |
| 次数与终止 | finding_9, finding_14, finding_19 |
| 反向依据与一致性 | finding_22 |

### c06 · 暂停批次 001 第 0 轮

保留（模型判定） 18

表示精度：精确保留 18 项，保守保留 0 项。

逐项修改建议：[suggestions/c06.md](suggestions/c06.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|

七类检查记录（不构成完整性证明）：

| 核对类别 | 核对项 / 不适用说明 |
|---|---|
| 要求性质与作用域 | finding_1, finding_2 |
| 动作与对象 | finding_3, finding_7, finding_8, finding_14 |
| 数据来源与绑定 | finding_4, finding_9, finding_10, finding_15 |
| 条件与例外 | finding_5, finding_6, finding_11 |
| 顺序与依赖 | finding_16, finding_17, finding_18 |
| 次数与终止 | finding_12 |
| 反向依据与一致性 | finding_13 |

### c07 · 暂停批次 010 第 0 轮

保留（模型判定） 36

表示精度：精确保留 35 项，保守保留 1 项。

逐项修改建议：[suggestions/c07.md](suggestions/c07.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| b6_extract_candidate_inputs / 保守保留 | 源文只有一次搜索响应；由于存在四个互斥参数分支，合流处需要从可能的分支响应取得 total/items。<br>ir_012 输入 result_006、result_007、result_008、result_009 四个搜索响应结果，link 分别指向对应分支定义。 | 这是合流依赖的保守候选集合，不是声称四个响应同时存在；候选均来自已有分支输出定义。 | fact:/blocks/6/instructions/0/inputs/0, fact:/blocks/6/instructions/0/inputs/1, fact:/blocks/6/instructions/0/inputs/2, fact:/blocks/6/instructions/0/inputs/3, fact:/blocks/2/instructions/0/outputs/0, fact:/blocks/3/instructions/0/outputs/0, fact:/blocks/4/instructions/0/outputs/0, fact:/blocks/5/instructions/0/outputs/0, fact:/blocks/6/instructions/0/inputs/0:link, fact:/blocks/6/instructions/0/inputs/1:link, fact:/blocks/6/instructions/0/inputs/2:link, fact:/blocks/6/instructions/0/inputs/3:link |

七类检查记录（不构成完整性证明）：

| 核对类别 | 核对项 / 不适用说明 |
|---|---|
| 要求性质与作用域 | n1_workflow_scope, n2_capability_note, n3_no_precall_validation, n4_no_index_delete, n5_missing_arg_config |
| 动作与对象 | a1_read_request, a2_index_search_target, a3_dispatch_control, a4_extract_total_items_action, a5_write_count_action, a6_return_items_action |
| 数据来源与绑定 | b1_request_fields, b2_term_binding, b3_from_date_binding, b4_limit_binding, b5_extract_outputs, b6_extract_candidate_inputs, b7_write_total_binding, b8_return_items_binding |
| 条件与例外 | g1_from_date_present, g2_from_date_missing_omit, g3_limit_present, g4_limit_missing_omit, g5_branch_combinations |
| 顺序与依赖 | o1_read_before_search, o2_search_before_write, o3_write_before_return |
| 次数与终止 | c1_search_exactly_once, c2_write_return_singular_terminal |
| 反向依据与一致性 | gc1_presence_flags_supported, gc2_branch_calls_supported, gc3_resource_targets, gc4_no_delete_op, gc5_no_fuzzy_op, gc6_no_validation_op, gc7_control_terminals |

## 转换与执行记录

计划 7 次逻辑调用，已记录 7 次；状态 `completed_with_errors`。

记录执行 9 次，额外执行重试 2 次，HTTP 尝试 9 次。

请求配置：`deepseek-v4-flash` / `max`。独立上下文，无自动修复或择优。

| 输入 | 受控转换检查 | 模型执行 |
|---|---|---|
| c01 | passed | execution_error |
| c02 | passed | complete |
| c03 | passed | execution_error |
| c04 | passed | complete |
| c05 | passed | complete |
| c06 | passed | complete |
| c07 | passed | complete |

固定30图离线验收：启用=True；通过 30/30。

转换通过仅说明当前受控文本保留规范化图的明确记录；证明边界和逐输入证书另见 inputs 与 verification。

## 外置预期的复核候选

以下仅匹配判定类别与证据区域，不能自动认定语义命中、漏报或误报。

| 输入 | 外置预期 | 匹配状态 | 候选核对项 |
|---|---|---|---|
| c01 | baseline-gold-r01 | execution_error |  |
| c01 | baseline-gold-r02 | execution_error |  |
| c01 | baseline-gold-r03 | execution_error |  |
| c01 | baseline-gold-r04 | execution_error |  |
| c02 | archive-receives-credential | candidate_match | f_data_archive_only_source, f_grounding_archive_conflict |
| c03 | failure-status-append-missing | execution_error |  |
| c04 | retry-returns-first-body | candidate_match | f_data_return_retry_body |
| c05 | added-two-second-wait | candidate_match | finding_10 |
| c06 | 无本实验人工标准答案 | 待助手逐项复核 | — |
| c07 | 无本实验人工标准答案 | 待助手逐项复核 | — |

## 可复核材料与限制

- inputs：完整源文、原始案例图、实际受控文本、证据索引和转换检查记录；原始图不进入模型提示词。
- calls：原始提示词、响应、摘要、实际模型名和 SSE；parsed：严格核验后的结果。
- suggestions：逐案例修改建议；replay：新版离线重放结果。
- 约束仅为声明；条件文字未求值；开放操作、源码及运行成功未经证明。
- 保守依赖列出候选与精度损失，不代表候选同时发生，也不证明后续传播结论。
- 固定案例为开发诊断，不能支持泛化正确性或统计显著性结论。
