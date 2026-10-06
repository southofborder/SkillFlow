# 受控语义回述与完整源文核对

运行：`controlled-v2-f01-20260914T142804Z`；模式：`replay`。

唯一模型任务是比较完整原文与受控文本。转换检查、模型判断与外置评测分别报告。

## 差异与未决项

以下保留模型原始有效判定；context 项仅记录非业务上下文，不计为业务语义保留。

### c01

保留（模型判定） 17

逐项修改建议：[suggestions/c01.md](suggestions/c01.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|

### c02

保留（模型判定） 7；错转 1；内部冲突 1

逐项修改建议：[suggestions/c02.md](suggestions/c02.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_6 / 错转 | archive.fetch 最多调用一次；只能把 source_id 作为唯一参数，绝不能把 FAST_KEY 传给 archive.fetch 或 diagnostic output。<br>block_011 的 call_archive_fetch 输入除 external_resource archive.fetch 和 result_001/source_id_value 外，还记录 result_002/fast_key；同一操作的约束1却说 pass source_id as its only argument，图级约束0说 Never pass FAST_KEY to archive.fetch or diagnostic output。 | 源文明确要求唯一参数为 source_id 且禁止 FAST_KEY；受控操作记录额外传入了 fast_key，属于对调用参数的错误转写。 | fact:/constraints/0, fact:/blocks/10/instructions/0, fact:/blocks/10/instructions/0/inputs/0, fact:/blocks/10/instructions/0/inputs/1, fact:/blocks/10/instructions/0/inputs/2, fact:/blocks/10/instructions/0/outputs/0, fact:/blocks/10/instructions/0/outputs/1, fact:/blocks/10/instructions/0/constraints/1, fact:/blocks/10/instructions/0/inputs/1:link, fact:/blocks/10/instructions/0/inputs/2:link, fact:/edges/12 |
| finding_7 / 内部冲突 | 源文要求 archive.fetch 只接收 source_id 且不得接收 FAST_KEY。<br>操作记录 fact:/blocks/10/instructions/0/inputs/2 把 result_002/fast_key 作为 archive.fetch 输入；同一操作约束 fact:/blocks/10/instructions/0/constraints/1 声明只传 source_id，图级约束 fact:/constraints/0 禁止把 FAST_KEY 传给 archive.fetch。 | 在受控文本内部，操作记录与两个约束声明直接矛盾；这不是操作已执行的事实，而是构图内部不一致。 | fact:/blocks/10/instructions/0/inputs/2, fact:/blocks/10/instructions/0/constraints/1, fact:/constraints/0 |

### c03

保留（模型判定） 8；遗漏 1

逐项修改建议：[suggestions/c03.md](suggestions/c03.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_10 / 遗漏 | 在每个成功或失败返回路径中，返回前都要把最终状态 append 到 local status.txt。<br>全局 constraints/1 声明每个成功或失败返回前都要 append final status；三个成功路径 block_006、block_010、block_013 均在 return 前记录 append_final_status_to_status_file，输入 status.txt 和 success 字面量；但 archive.fetch 失败返回路径 block_014 的 instructions 只有 ir_028 return result_012，没有 append 操作。block_014 名称虽含 Append failure status，但名称不能补造操作。 | 源文要求覆盖所有成功和失败返回路径；受控图在成功路径有对应操作记录，在 archive.fetch 失败返回路径遗漏 append 操作，因此该源要求未被完整保留。 | fact:/constraints/1, fact:/blocks/5/instructions/0, fact:/blocks/5/instructions/0/inputs/0, fact:/blocks/5/instructions/0/inputs/1, fact:/blocks/5/instructions/1, fact:/blocks/5/instructions/1/inputs/0, fact:/blocks/9/instructions/0, fact:/blocks/9/instructions/0/inputs/0, fact:/blocks/9/instructions/0/inputs/1, fact:/blocks/9/instructions/1, fact:/blocks/9/instructions/1/inputs/0, fact:/blocks/12/instructions/0, fact:/blocks/12/instructions/0/inputs/0, fact:/blocks/12/instructions/0/inputs/1, fact:/blocks/12/instructions/1, fact:/blocks/12/instructions/1/inputs/0, fact:/blocks/13/name, fact:/blocks/13/instructions, fact:/blocks/13/instructions/0, fact:/blocks/13/instructions/0/inputs/0 |

### c04

保留（模型判定） 9；错转 1

逐项修改建议：[suggestions/c04.md](suggestions/c04.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_7b / 错转 | 对 fast.fetch retry 成功：应返回该次 retry 成功响应的 body 值且不再 fetch。<br>block_008 的 retry_fast_fetch 输出 result_008(retry_fast_fetch_response_body)；block_009 检查 retry 成功并输出 result_010；fact:/edges/10 在 retry succeeded 时进入 block_010，但 block_010 的名称写明 first fast.fetch response body after retry success，其 return 输入为 result_004(fast_fetch_response_body，首次调用 body)，不是 result_008。 | 源文要求成功响应的 body 保持不变；retry 成功时唯一成功响应是 retry 响应，受控却返回首次失败调用的 body，结果身份错转。该操作记录也与 fact:/constraints/2 的 return that successful response's body value unchanged 不一致。 | fact:/blocks/8/key, fact:/blocks/8/id, fact:/blocks/8/name, fact:/blocks/8/source, fact:/blocks/8/instructions, fact:/blocks/8/instructions/0, fact:/blocks/8/instructions/0/inputs/0, fact:/blocks/8/instructions/0/outputs/0, fact:/blocks/8/instructions/0/metadata_json, fact:/blocks/8/instructions/1, fact:/blocks/8/instructions/1/inputs/0, fact:/blocks/8/instructions/1/metadata_json, fact:/blocks/9/key, fact:/blocks/9/id, fact:/blocks/9/name, fact:/blocks/9/source, fact:/blocks/9/instructions, fact:/blocks/9/instructions/0, fact:/blocks/9/instructions/0/inputs/0, fact:/blocks/9/instructions/0/inputs/1, fact:/blocks/9/instructions/0/metadata_json, fact:/blocks/9/instructions/1, fact:/blocks/9/instructions/1/inputs/0, fact:/blocks/9/instructions/1/metadata_json, fact:/blocks/7/instructions/0/outputs/0, fact:/constraints/2, fact:/edges/9, fact:/edges/10, fact:/blocks/8/instructions/0/inputs/0:link, fact:/blocks/8/instructions/1/inputs/0:link, fact:/blocks/9/instructions/1/inputs/0:link |

### c05

保留（模型判定） 7；无依据新增 1

逐项修改建议：[suggestions/c05.md](suggestions/c05.md)。

| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |
|---|---|---|---|
| finding_5 / 无依据新增 | 源文只要求：首次 transient 失败时重试 fast.fetch 一次；非 transient 首次失败或失败重试后调用 archive.fetch；源文没有等待或延迟要求。<br>block_007 的操作清单包含 ir_wait_1 wait_for_seconds，输入 literal 2，并有操作级约束 Wait for 2 seconds before continuing；该等待位于 transient 检查与 dispatch 之间。 | 源文步骤3、4未规定任何等待；该 wait_for_seconds 是新增动作和声明约束，而且位于 block_007 分支前，会同时延迟 transient 重试路径和 non-transient 到 archive.fetch 的路径。 | fact:/blocks/6/instructions, fact:/blocks/6/instructions/1, fact:/blocks/6/instructions/1/inputs/0, fact:/blocks/6/instructions/1/constraints/0, fact:/blocks/6/instructions/1/metadata_json |

## 转换与执行记录

计划 5 次逻辑调用，已记录 5 次；状态 `complete`。

请求配置：`deepseek-v4-flash` / `max`。独立上下文，无自动修复或择优。

| 输入 | 受控转换检查 | 模型执行 |
|---|---|---|
| c01 | passed | complete |
| c02 | passed | complete |
| c03 | passed | complete |
| c04 | passed | complete |
| c05 | passed | complete |

固定30图离线验收：启用=True；通过 30/30。

转换通过仅说明当前受控文本保留规范化图的明确记录；证明边界和逐输入证书另见 inputs 与 verification。

## 外置预期的复核候选

以下仅匹配判定类别与证据区域，不能自动认定语义命中、漏报或误报。

| 输入 | 外置预期 | 匹配状态 | 候选核对项 |
|---|---|---|---|
| c01 | baseline-gold-r01 | candidate_match | finding_6, finding_9, finding_10, finding_17, finding_18 |
| c01 | baseline-gold-r02 | candidate_match | finding_12, finding_13, finding_16, finding_17, finding_18 |
| c01 | baseline-gold-r03 | candidate_match | finding_2, finding_13 |
| c01 | baseline-gold-r04 | candidate_match | finding_2, finding_12, finding_16 |
| c02 | archive-receives-credential | candidate_match | finding_6, finding_7 |
| c03 | failure-status-append-missing | candidate_match | finding_10 |
| c04 | retry-returns-first-body | candidate_match | finding_7b |
| c05 | added-two-second-wait | candidate_match | finding_5 |

## 可复核材料与限制

- inputs：完整源文、原始案例图、实际受控文本、证据索引和转换检查记录；原始图不进入模型提示词。
- calls：原始提示词、响应、摘要、实际模型名和 SSE；parsed：严格核验后的结果。
- suggestions：逐案例修改建议；replay：新版离线重放结果。
- 约束仅为声明；条件文字未求值；开放操作、源码及运行成功未经证明。
- F01 是开发示范，五案例结果不支持泛化正确性或统计显著性结论。
