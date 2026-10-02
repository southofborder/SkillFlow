# 未通过证据校验的原始回译

仅供错误诊断；不是有效回译结果，没有修复引用，也不会传给下游核对器。

## unit_1

图的结构入口由 entry_block_id 指向 block_001。block_001 按块内顺序先执行 opcode read_source_id_from_request：它读取 context_key source_id，输出 result_001（semantic_name 为 source_id_value），随后以 dispatch 结束；图中边从 block_001 指向 block_002，条件文字为 null。block_002 执行 opcode read_fast_key_from_environment：它读取 context_key FAST_KEY，输出 result_002（semantic_name 为 fast_key），随后以 dispatch 结束；图中边从 block_002 指向 block_003，条件文字为 null。declared_context_keys 声明 source_id 与 FAST_KEY 两个上下文键。

模型原始定位：`["/entry_block_id", "/blocks/block_001/instructions/0", "/blocks/block_001/instructions/1", "/edges/0", "/blocks/block_002/instructions/0", "/blocks/block_002/instructions/1", "/edges/1", "/declared_context_keys/0", "/declared_context_keys/1"]`

## unit_2

block_003 以 result_002 为输入执行 opcode check_fast_key_presence，输出 result_003（semantic_name 为 fast_key_present），再以 dispatch 结束。图中边在条件文字 FAST_KEY is present 下从 block_003 指向 block_004，在条件文字 FAST_KEY is absent 下从 block_003 指向 block_011。该块约束声明：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 尝试 fast.fetch；若 FAST_KEY 不存在，直接到 archive.fetch 而不调用 fast.fetch。这里的约束是声明要求，不等同于运行时已履行。

模型原始定位：`["/blocks/block_003/instructions/0", "/blocks/block_003/instructions/1", "/edges/2", "/edges/3", "/blocks/block_003/constraints/0"]`

## unit_3

沿 FAST_KEY is present 的结构边到达 block_004 时，图中操作 opcode call_fast_fetch 的输入包括 external_resource fast.fetch、result_001（source_id_value）与 result_002（fast_key）；输出为 result_004（fast_fetch_response_body）和 result_005（fast_fetch_error）。随后以 dispatch 结束，边无条件下指向 block_005。external_resource 用于定位调用目标或资源，不由此自动等同于被传递的业务参数。

模型原始定位：`["/edges/2", "/blocks/block_004/instructions/0", "/blocks/block_004/instructions/1", "/edges/4"]`

## unit_4

block_005 以 result_005 为输入执行 opcode check_fast_fetch_success，输出 result_006（semantic_name 为 fast_fetch_succeeded），再以 dispatch 结束。图中边在条件文字 first fast.fetch attempt succeeded 下指向 block_006，在条件文字 first fast.fetch attempt failed 下指向 block_007。

模型原始定位：`["/blocks/block_005/instructions/0", "/blocks/block_005/instructions/1", "/edges/5", "/edges/6"]`

## unit_5

沿 first fast.fetch attempt succeeded 边到 block_006 时，block_006 先执行 opcode append_final_status_to_status_file：输入为 external_resource status.txt 与 literal success；随后执行 return，其输入是 result_004（fast_fetch_response_body）。图级约束要求：每个成功或失败返回路径之前都把最终状态追加到本地 status.txt；任一工具成功时原样返回该成功响应的 body 值并且不再进行 fetch 调用。

模型原始定位：`["/edges/5", "/blocks/block_006/instructions/0", "/blocks/block_006/instructions/1", "/constraints/1", "/constraints/2"]`

## unit_6

沿 first fast.fetch attempt failed 边到 block_007 时，block_007 以 result_005 为输入执行 opcode check_transient_error，输出 result_007（semantic_name 为 fast_fetch_error_transient），再以 dispatch 结束。图中边在条件文字 first fast.fetch failure was transient 下指向 block_008，在条件文字 first fast.fetch failure was non-transient 下指向 block_011。block_008 中 opcode retry_fast_fetch 所在指令的约束声明：仅当第一次尝试因 transient error 失败时重试 fast.fetch 恰好一次；非 transient 的第一次失败不得重试。

模型原始定位：`["/edges/6", "/blocks/block_007/instructions/0", "/blocks/block_007/instructions/1", "/edges/7", "/edges/8", "/blocks/block_008/instructions/0/constraints/0"]`

## unit_7

沿 first fast.fetch failure was transient 边到 block_008 时，图中操作 opcode retry_fast_fetch 的输入包括 external_resource fast.fetch、result_001（source_id_value）与 result_002（fast_key）；输出为 result_008（retry_fast_fetch_response_body）和 result_009（retry_fast_fetch_error）。随后以 dispatch 结束，边无条件下指向 block_009。block_009 以 result_009 为输入执行 opcode check_fast_fetch_success，输出 result_010（semantic_name 为 retry_fast_fetch_succeeded），再以 dispatch 结束；图中边在条件文字 fast.fetch retry succeeded 下指向 block_010，在条件文字 fast.fetch retry failed 下指向 block_011。

模型原始定位：`["/edges/7", "/blocks/block_008/instructions/0", "/blocks/block_008/instructions/1", "/edges/9", "/blocks/block_009/instructions/0", "/blocks/block_009/instructions/1", "/edges/10", "/edges/11"]`

## unit_8

沿 fast.fetch retry succeeded 边到 block_010 时，block_010 先执行 opcode append_final_status_to_status_file：输入为 external_resource status.txt 与 literal success；随后执行 return，其输入明确是 result_004（第一次 fast.fetch 的 fast_fetch_response_body），不是 retry 输出 result_008。图级约束要求每个成功或失败返回路径前追加最终状态，并在任一工具成功时原样返回该成功响应的 body 且不再 fetch；这里图中未说明 retry 成功时 result_008 与所返回的 result_004 之间的关系，因此不对该差异作额外调和。

模型原始定位：`["/edges/10", "/blocks/block_010/instructions/0", "/blocks/block_010/instructions/1", "/constraints/1", "/constraints/2"]`

## unit_9

到达 block_011 的图中边条件包括 FAST_KEY is absent、first fast.fetch failure was non-transient、fast.fetch retry failed。block_011 中 opcode call_archive_fetch 的输入包括 external_resource archive.fetch 与 result_001（source_id_value）；输出为 result_011（archive_fetch_response_body）和 result_012（archive_fetch_error）。随后以 dispatch 结束，边无条件下指向 block_012。块级约束声明：在非 transient 的第一次 fast.fetch 失败或任何 fast.fetch 重试失败后，用 source_id 调用 archive.fetch；archive.fetch 至多调用一次且以 source_id 为唯一参数；若 archive.fetch 失败，停止并返回其错误，不重试 archive.fetch。图级约束还声明：在本工作流任何位置都不得把 FAST_KEY 传给 archive.fetch 或诊断输出。

模型原始定位：`["/edges/3", "/edges/8", "/edges/11", "/blocks/block_011/instructions/0", "/blocks/block_011/instructions/1", "/edges/12", "/blocks/block_011/constraints/0", "/blocks/block_011/constraints/1", "/blocks/block_011/constraints/2", "/constraints/0"]`

## unit_10

block_012 以 result_012 为输入执行 opcode check_archive_fetch_success，输出 result_013（semantic_name 为 archive_fetch_succeeded），再以 dispatch 结束。图中边在条件文字 archive.fetch succeeded 下指向 block_013，在条件文字 archive.fetch failed 下指向 block_014。block_013 以 external_resource status.txt 与 literal success 执行 append_final_status_to_status_file，再 return 输入 result_011（archive_fetch_response_body）；block_014 以 external_resource status.txt 与 literal failure 执行 append_final_status_to_status_file，再 return 输入 result_012（archive_fetch_error）。图级约束要求每个成功或失败返回前追加最终状态到本地 status.txt，并在任一工具成功时原样返回该成功响应的 body 且不再 fetch；archive.fetch 失败路径还受 block_011 的停止并返回错误、不重试约束。

模型原始定位：`["/blocks/block_012/instructions/0", "/blocks/block_012/instructions/1", "/edges/13", "/edges/14", "/blocks/block_013/instructions/0", "/blocks/block_013/instructions/1", "/blocks/block_014/instructions/0", "/blocks/block_014/instructions/1", "/constraints/1", "/constraints/2", "/blocks/block_011/constraints/2"]`
