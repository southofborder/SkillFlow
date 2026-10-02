# 连贯自然语言回译

图 SHA-256：0d9ebf8762a201c2abf693071b0e77f6b6a6e72ec846eb36e6f514633730431c

## unit_1

入口为 block_001（Read source_id from the user's request），其 data_source_kind 为 context。ir_001 使用 opcode read_source_id_from_request，输入是 context_key source_id，输出 result_001（source_id_value）；ir_002 是 opcode dispatch，输入为空。显式边 /edges/0 从 block_001 指向 block_002。block_002（Read FAST_KEY from the environment）的 data_source_kind 为 context，ir_003 使用 opcode read_fast_key_from_environment，输入是 context_key FAST_KEY，输出 result_002（fast_key）；ir_004 是 opcode dispatch。显式边 /edges/1 从 block_002 指向 block_003。declared_context_keys 列出 source_id 和 FAST_KEY；result_001 与 result_002 分别是两项读取操作的结果定义。

图位置：`["/entry_block_id", "/declared_context_keys/0", "/declared_context_keys/1", "/blocks/block_001", "/blocks/block_001/instructions/0", "/blocks/block_001/instructions/1", "/blocks/block_002", "/blocks/block_002/instructions/0", "/blocks/block_002/instructions/1", "/edges/0", "/edges/1"]`

## unit_2

block_003（Check whether FAST_KEY is present）的块级约束 /blocks/block_003/constraints/0 声明：若 FAST_KEY 存在，先用 source_id 和 FAST_KEY 尝试 fast.fetch；若不存在，直接转到 archive.fetch 且不调用 fast.fetch。显式操作 ir_005（opcode check_fast_key_presence）以 result_002（fast_key）为输入，输出 result_003（fast_key_present）；ir_006 是 opcode dispatch，输入 result_003。显式边 /edges/2 的条件文字为 FAST_KEY is present，指向 block_004；/edges/3 的条件文字为 FAST_KEY is absent，指向 block_011。这里的约束是声明要求，操作 ir_005/ir_006 提供检查与分发，但图中并未据此证明运行分支已经执行。

图位置：`["/blocks/block_003", "/blocks/block_003/constraints/0", "/blocks/block_003/instructions/0", "/blocks/block_003/instructions/1", "/blocks/block_002/instructions/0", "/edges/2", "/edges/3"]`

## unit_3

在 FAST_KEY 存在分支上，block_004（data_source_kind 为 external）的 ir_007（opcode call_fast_fetch）以 external_resource fast.fetch、result_001（source_id_value）和 result_002（fast_key）为输入，输出 result_004（fast_fetch_response_body）与 result_005（fast_fetch_error）；ir_008 是 opcode dispatch。显式边 /edges/4 从 block_004 指向 block_005。block_005 的 ir_009（opcode check_fast_fetch_success）输入 result_005，输出 result_006（fast_fetch_succeeded）；ir_010 是 opcode dispatch，输入 result_006。显式边 /edges/5 的条件为 first fast.fetch attempt succeeded，指向 block_006；/edges/6 的条件为 first fast.fetch attempt failed，指向 block_007。若按 /edges/5 走首次成功路径，block_006 的 ir_011（opcode append_final_status_to_status_file）以 external_resource status.txt 和字面量 success 为输入，ir_012（opcode return）返回 result_004，即首次 fast.fetch 的响应体；没有从 block_006 出发的显式边。图级约束 /constraints/1 要求每个成功或失败返回前追加 final status，/constraints/2 要求任一工具成功时原样返回成功响应体且不再 fetch。

图位置：`["/blocks/block_004", "/blocks/block_004/instructions/0", "/blocks/block_004/instructions/1", "/blocks/block_001/instructions/0", "/blocks/block_002/instructions/0", "/edges/4", "/blocks/block_005", "/blocks/block_005/instructions/0", "/blocks/block_005/instructions/1", "/edges/5", "/edges/6", "/blocks/block_006", "/blocks/block_006/instructions/0", "/blocks/block_006/instructions/1", "/constraints/1", "/constraints/2"]`

## unit_4

首次 fast.fetch 失败路径到 block_007。ir_013（opcode check_transient_error）输入 result_005（首次 fast.fetch 错误），输出 result_007（fast_fetch_error_transient）；ir_014 是 opcode dispatch，输入 result_007。显式边 /edges/7 的条件为 first fast.fetch failure was transient，指向 block_008；/edges/8 的条件为 first fast.fetch failure was non-transient，指向 block_011。block_008（data_source_kind 为 external）中，ir_015（opcode retry_fast_fetch）以 external_resource fast.fetch、result_001 和 result_002 为输入，输出 result_008（retry_fast_fetch_response_body）与 result_009（retry_fast_fetch_error）；其指令级约束 /blocks/block_008/instructions/0/constraints/0 声明仅当首次失败为瞬时错误时恰好重试 fast.fetch 一次，非瞬时首次失败不重试。ir_016 是 opcode dispatch，显式边 /edges/9 指向 block_009。block_009 的 ir_017（opcode check_fast_fetch_success）输入 result_009，输出 result_010（retry_fast_fetch_succeeded）；ir_018 是 opcode dispatch，输入 result_010。显式边 /edges/10 的条件为 fast.fetch retry succeeded，指向 block_010；/edges/11 的条件为 fast.fetch retry failed，指向 block_011。若按 /edges/10 走重试成功路径，block_010 的 ir_019（opcode append_final_status_to_status_file）以 status.txt 和字面量 success 为输入，ir_020（opcode return）返回 result_008，即重试 fast.fetch 的响应体；没有从 block_010 出发的显式边。

图位置：`["/blocks/block_007", "/blocks/block_007/instructions/0", "/blocks/block_007/instructions/1", "/edges/7", "/edges/8", "/blocks/block_008", "/blocks/block_008/instructions/0", "/blocks/block_008/instructions/0/constraints/0", "/blocks/block_008/instructions/1", "/edges/9", "/blocks/block_009", "/blocks/block_009/instructions/0", "/blocks/block_009/instructions/1", "/edges/10", "/edges/11", "/blocks/block_010", "/blocks/block_010/instructions/0", "/blocks/block_010/instructions/1", "/blocks/block_004/instructions/0", "/blocks/block_001/instructions/0", "/blocks/block_002/instructions/0"]`

## unit_5

block_011（Call archive.fetch once with source_id，data_source_kind 为 external）是 archive.fetch 调用块，可由 /edges/3（FAST_KEY 不存在）、/edges/8（首次非瞬时失败）或 /edges/11（重试失败）进入。ir_021（opcode call_archive_fetch）以 external_resource archive.fetch 和 result_001（source_id_value）为输入，输出 result_011（archive_fetch_response_body）与 result_012（archive_fetch_error）；ir_022 是 opcode dispatch。该指令级约束 /blocks/block_011/instructions/0/constraints/0 声明在首次非瞬时失败或 fast.fetch 任一次重试失败后，用 source_id 调用 archive.fetch；/blocks/block_011/instructions/0/constraints/1 声明 archive.fetch 至多调用一次且只把 source_id 作为参数；/blocks/block_011/instructions/0/constraints/2 声明 archive.fetch 失败时停止并返回其错误，不重试 archive.fetch。图级约束 /constraints/0 声明整个工作流绝不把 FAST_KEY 传给 archive.fetch 或诊断输出；ir_021 的显式输入中没有 FAST_KEY，但这是声明限制与实际输入的区分。显式边 /edges/12 从 block_011 指向 block_012。block_012 的 ir_023（opcode check_archive_fetch_success）输入 result_012，输出 result_013（archive_fetch_succeeded）；ir_024 是 opcode dispatch，输入 result_013。显式边 /edges/13 的条件为 archive.fetch succeeded，指向 block_013；/edges/14 的条件为 archive.fetch failed，指向 block_014。若走 archive 成功路径，block_013 的 ir_025（opcode append_final_status_to_status_file）以 status.txt 和字面量 success 为输入，ir_026（opcode return）返回 result_011。若走 archive 失败路径，block_014 的 ir_027 以 status.txt 和字面量 failure 为输入，ir_028（opcode return）返回 result_012；block_013 与 block_014 都没有出发的显式边。

图位置：`["/blocks/block_011", "/blocks/block_011/instructions/0", "/blocks/block_011/instructions/0/constraints/0", "/blocks/block_011/instructions/0/constraints/1", "/blocks/block_011/instructions/0/constraints/2", "/blocks/block_011/instructions/1", "/edges/3", "/edges/8", "/edges/11", "/edges/12", "/blocks/block_012", "/blocks/block_012/instructions/0", "/blocks/block_012/instructions/1", "/edges/13", "/edges/14", "/blocks/block_013", "/blocks/block_013/instructions/0", "/blocks/block_013/instructions/1", "/blocks/block_014", "/blocks/block_014/instructions/0", "/blocks/block_014/instructions/1", "/constraints/0", "/blocks/block_001/instructions/0"]`

## unit_6

约束按作用域记录如下。图级 /constraints/0 声明整个工作流绝不让 FAST_KEY 进入 archive.fetch 或诊断输出；图级 /constraints/1 声明在每个成功或失败路径返回前，把 final status 追加到本地 status.txt；图级 /constraints/2 声明任一工具成功时原样返回该成功响应的 body 值，且不再进行后续 fetch 调用。块级 /blocks/block_003/constraints/0 声明 FAST_KEY 存在时优先尝试 fast.fetch、缺席时直接 archive.fetch。指令级 /blocks/block_008/instructions/0/constraints/0 声明确切一次重试的触发条件；指令级 /blocks/block_011/instructions/0/constraints/0 至 /blocks/block_011/instructions/0/constraints/2 声明 archive.fetch 的触发、至多一次和失败停止要求。这些是声明要求，不证明运行时已履行；约束的存在也不等于对应显式操作必然存在。

图位置：`["/constraints/0", "/constraints/1", "/constraints/2", "/blocks/block_003/constraints/0", "/blocks/block_008/instructions/0/constraints/0", "/blocks/block_011/instructions/0/constraints/0", "/blocks/block_011/instructions/0/constraints/1", "/blocks/block_011/instructions/0/constraints/2"]`
