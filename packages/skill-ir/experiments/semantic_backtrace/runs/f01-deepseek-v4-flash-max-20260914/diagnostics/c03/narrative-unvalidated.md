# 未通过证据校验的原始回译

仅供错误诊断；不是有效回译结果，没有修复引用，也不会传给下游核对器。

## unit_1

图的结构入口是 /entry_block_id 所指向的 block_001。block_001 的 ir_001 以 read_source_id_from_request 从输入上下文键 source_id 读取，输出 result_001（semantic_name 为 source_id_value）；ir_002 是 dispatch，无输入、无输出。block_001 到 block_002 由 /edges/0 连接。block_002 的 ir_003 以 read_fast_key_from_environment 从输入上下文键 FAST_KEY 读取，输出 result_002（semantic_name 为 fast_key）；ir_004 是 dispatch，无输入、无输出；block_002 到 block_003 由 /edges/1 连接。source_id 和 FAST_KEY 出现在 /declared_context_keys。

模型原始定位：`["/entry_block_id", "/blocks/block_001/instructions/0", "/blocks/block_001/instructions/1", "/edges/0", "/blocks/block_002/instructions/0", "/blocks/block_002/instructions/1", "/edges/1", "/declared_context_keys"]`

## unit_2

block_003 的 ir_005 以 check_fast_key_presence 消费 result_002，输出 result_003（semantic_name 为 fast_key_present）；ir_006 以 dispatch 消费 result_003，无输出。block_003 的块级约束 /blocks/block_003/constraints/0 声明：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 尝试 fast.fetch；若 FAST_KEY 不存在，直接进入 archive.fetch 而不调用 fast.fetch。对应边是 /edges/2（条件文本为 FAST_KEY is present，到 block_004）和 /edges/3（条件文本为 FAST_KEY is absent，到 block_011）；这些条件文本是图声明，不在此断言运行时该路径必然可达。

模型原始定位：`["/blocks/block_003/instructions/0", "/blocks/block_003/instructions/1", "/blocks/block_003/constraints/0", "/edges/2", "/edges/3"]`

## unit_3

在 FAST_KEY present 的声明分支下，block_004 的 ir_007 以 call_fast_fetch 调用外部资源 fast.fetch，显式输入为 fast.fetch、result_001（source_id_value）和 result_002（fast_key），输出 result_004（semantic_name 为 fast_fetch_response_body）与 result_005（semantic_name 为 fast_fetch_error）；ir_008 是 dispatch，无输入、无输出；/edges/4 连接 block_004 到 block_005。block_005 的 ir_009 以 check_fast_fetch_success 消费 result_005，输出 result_006（semantic_name 为 fast_fetch_succeeded）；ir_010 以 dispatch 消费 result_006，无输出。边 /edges/5 声明首次 fast.fetch 尝试成功时到 block_006，/edges/6 声明失败时到 block_007。block_006 的 ir_011 以 append_final_status_to_status_file 将字面值 success 追加到外部资源 status.txt，无输出；ir_012 以 return 返回 result_004，无输出。该成功路径与图级 /constraints/1 和 /constraints/2 分别声明的返回前追加最终状态、成功后原样返回成功响应 body 且不再 fetch 相符。

模型原始定位：`["/blocks/block_004/instructions/0", "/blocks/block_004/instructions/1", "/edges/4", "/blocks/block_005/instructions/0", "/blocks/block_005/instructions/1", "/edges/5", "/edges/6", "/blocks/block_006/instructions/0", "/blocks/block_006/instructions/1", "/constraints/1", "/constraints/2"]`

## unit_4

若首次 fast.fetch 失败，block_007 的 ir_013 以 check_transient_error 消费 result_005，输出 result_007（semantic_name 为 fast_fetch_error_transient）；ir_014 以 dispatch 消费 result_007，无输出。边 /edges/7 声明首次失败为 transient 时到 block_008，/edges/8 声明非 transient 时到 block_011。block_008 的 ir_015 带有指令级约束 /blocks/block_008/instructions/0/constraints/0：仅当首次尝试因 transient 错误失败时重试 fast.fetch 恰好一次，非 transient 首次失败不得重试。ir_015 以 retry_fast_fetch 调用 fast.fetch，输入为 fast.fetch、result_001 和 result_002，输出 result_008（semantic_name 为 retry_fast_fetch_response_body）与 result_009（semantic_name 为 retry_fast_fetch_error）；ir_016 是 dispatch，无输入、无输出；/edges/9 连接 block_008 到 block_009。block_009 的 ir_017 以 check_fast_fetch_success 消费 result_009，输出 result_010（semantic_name 为 retry_fast_fetch_succeeded）；ir_018 以 dispatch 消费 result_010，无输出。边 /edges/10 声明重试成功到 block_010，/edges/11 声明重试失败到 block_011。block_010 的 ir_019 将字面值 success 追加到 status.txt，无输出；ir_020 以 return 返回 result_008，无输出。result_006 与 result_010、result_004 与 result_008 分别是首次和重试的不同定义，不能互换。

模型原始定位：`["/blocks/block_007/instructions/0", "/blocks/block_007/instructions/1", "/edges/7", "/edges/8", "/blocks/block_008/instructions/0", "/blocks/block_008/instructions/0/constraints/0", "/blocks/block_008/instructions/1", "/edges/9", "/blocks/block_009/instructions/0", "/blocks/block_009/instructions/1", "/edges/10", "/edges/11", "/blocks/block_010/instructions/0", "/blocks/block_010/instructions/1"]`

## unit_5

archive 路径由 block_011 承担。其块级约束 /blocks/block_011/constraints/0、/blocks/block_011/constraints/1、/blocks/block_011/constraints/2 声明：在首次 fast.fetch 非 transient 失败或任何重试失败后，以 source_id 调用 archive.fetch；archive.fetch 至多调用一次且 source_id 是其唯一业务参数；若 archive.fetch 失败，停止并返回其错误，不重试 archive.fetch。ir_021 以 call_archive_fetch 调用外部资源 archive.fetch，显式输入只有 archive.fetch 与 result_001，输出 result_011（semantic_name 为 archive_fetch_response_body）与 result_012（semantic_name 为 archive_fetch_error）；ir_022 是 dispatch，无输入、无输出；/edges/12 连接 block_011 到 block_012。block_012 的 ir_023 以 check_archive_fetch_success 消费 result_012，输出 result_013（semantic_name 为 archive_fetch_succeeded）；ir_024 以 dispatch 消费 result_013，无输出。边 /edges/13 声明 archive.fetch 成功到 block_013，/edges/14 声明失败到 block_014。block_013 的 ir_025 将字面值 success 追加到 status.txt，无输出；ir_026 以 return 返回 result_011，无输出。block_014 的块名表示追加失败状态并返回 archive.fetch 错误，但该块实际指令只有 ir_028（opcode return），其输入为 result_012，无输出，没有任何 append 操作；因此虽然 /constraints/1 要求每个成功或失败返回前追加最终状态，失败路径的追加失败状态在图中没有显式操作，只能报告为声明与操作之间的证据缺口。

模型原始定位：`["/blocks/block_011/constraints/0", "/blocks/block_011/constraints/1", "/blocks/block_011/constraints/2", "/blocks/block_011/instructions/0", "/blocks/block_011/instructions/1", "/edges/12", "/blocks/block_012/instructions/0", "/blocks/block_012/instructions/1", "/edges/13", "/edges/14", "/blocks/block_013/instructions/0", "/blocks/block_013/instructions/1", "/blocks/block_014/block_name", "/blocks/block_014/instructions/0", "/constraints/1"]`

## unit_6

图级约束还声明两项全局要求。/constraints/0 要求任何位置都不得把 FAST_KEY 传给 archive.fetch 或诊断输出；显式图中，ir_021 调用 archive.fetch 的输入只有 archive.fetch 与 result_001，没有 result_002，而 fast.fetch 的 ir_007 和重试 ir_015 才显式使用 result_002。图中没有可见的 diagnostic output 操作节点，因此诊断输出部分没有对应操作可逐项核对。/constraints/2 要求任一工具成功后原样返回该成功响应 body 且不再做 fetch 调用；成功返回分别在 block_006 的 ir_012 返回 result_004、block_010 的 ir_020 返回 result_008、block_013 的 ir_026 返回 result_011，这些 result 标识各自追踪到不同的调用定义，不能只因语义名相似而互换。

模型原始定位：`["/constraints/0", "/blocks/block_011/instructions/0", "/blocks/block_004/instructions/0", "/blocks/block_008/instructions/0", "/constraints/2", "/blocks/block_006/instructions/1", "/blocks/block_010/instructions/1", "/blocks/block_013/instructions/1"]`
