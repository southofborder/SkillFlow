# 结构化回译

图 SHA-256：8b2a5b87fc7c05f9da0cdfdba3bf59bd1790ab094401a20e3c421334d08b01d6

## "entry"

```text
声明的入口块 ID："block_001"
```

依据：explicit_graph

图位置：["/entry_block_id"]

## "context"

```text
声明的上下文键（按记录顺序）：["source_id","FAST_KEY"]
```

依据：explicit_graph

图位置：["/declared_context_keys"]

## "global_constraints"

```text
声明的约束（图级原文；声明不等于行为已实现）：["Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.","Before returning from every success or failure path, append the final status to local status.txt.","On either tool's success, return that successful response's body value unchanged and make no further fetch calls."]
```

依据：declared_constraint

图位置：["/constraints"]

## "block:/block_001"

```text
块键："block_001"
块 ID 原文："block_001"
块名称原文（仅作标签，不据此补造操作）："Read source_id from the user's request"
数据来源标记："context"
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_001","opcode":"read_source_id_from_request","draft_instruction_id":"read_source_id"}
  实际输入（按记录顺序）：[{"type":"context_key","identifier":"source_id","semantic_name":"source_id"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_001","semantic_name":"source_id_value"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_002","opcode":"dispatch","draft_instruction_id":"go_read_fast_key"}
  实际输入（按记录顺序）：[]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_001"]

## "block:/block_002"

```text
块键："block_002"
块 ID 原文："block_002"
块名称原文（仅作标签，不据此补造操作）："Read FAST_KEY from the environment"
数据来源标记："context"
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_003","opcode":"read_fast_key_from_environment","draft_instruction_id":"read_fast_key"}
  实际输入（按记录顺序）：[{"type":"context_key","identifier":"FAST_KEY","semantic_name":"FAST_KEY"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_002","semantic_name":"fast_key"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_004","opcode":"dispatch","draft_instruction_id":"go_check_fast_key"}
  实际输入（按记录顺序）：[]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_002"]

## "block:/block_003"

```text
块键："block_003"
块 ID 原文："block_003"
块名称原文（仅作标签，不据此补造操作）："Check whether FAST_KEY is present"
数据来源标记：null
声明的约束（块级原文）：["If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch."]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_005","opcode":"check_fast_key_presence","draft_instruction_id":"check_fast_key"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_002","semantic_name":"fast_key"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_003","semantic_name":"fast_key_present"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_002","use_ref":"/blocks/block_003/instructions/0/inputs/0","definition_refs":["/blocks/block_002/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_006","opcode":"dispatch","draft_instruction_id":"go_branch_on_fast_key"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_003","semantic_name":"fast_key_present"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_003","use_ref":"/blocks/block_003/instructions/1/inputs/0","definition_refs":["/blocks/block_003/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：mixed

图位置：["/blocks/block_003","/blocks/block_003/instructions/0/inputs/0","/blocks/block_002/instructions/0/outputs/0","/blocks/block_003/instructions/1/inputs/0","/blocks/block_003/instructions/0/outputs/0"]

## "block:/block_004"

```text
块键："block_004"
块 ID 原文："block_004"
块名称原文（仅作标签，不据此补造操作）："Try fast.fetch first with source_id and FAST_KEY"
数据来源标记："external"
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_007","opcode":"call_fast_fetch","draft_instruction_id":"call_fast_fetch_first"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"fast.fetch","semantic_name":"fast.fetch"},{"type":"result","identifier":"result_001","semantic_name":"source_id_value"},{"type":"result","identifier":"result_002","semantic_name":"fast_key"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_004","semantic_name":"fast_fetch_response_body"},{"type":"result","identifier":"result_005","semantic_name":"fast_fetch_error"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":1,"identifier":"result_001","use_ref":"/blocks/block_004/instructions/0/inputs/1","definition_refs":["/blocks/block_001/instructions/0/outputs/0"]},{"input_index":2,"identifier":"result_002","use_ref":"/blocks/block_004/instructions/0/inputs/2","definition_refs":["/blocks/block_002/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_008","opcode":"dispatch","draft_instruction_id":"go_check_fast_fetch_first_success"}
  实际输入（按记录顺序）：[]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_004","/blocks/block_004/instructions/0/inputs/1","/blocks/block_001/instructions/0/outputs/0","/blocks/block_004/instructions/0/inputs/2","/blocks/block_002/instructions/0/outputs/0"]

## "block:/block_005"

```text
块键："block_005"
块 ID 原文："block_005"
块名称原文（仅作标签，不据此补造操作）："Check whether the first fast.fetch attempt succeeded"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_009","opcode":"check_fast_fetch_success","draft_instruction_id":"check_fast_fetch_first_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_005","semantic_name":"fast_fetch_error"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_006","semantic_name":"fast_fetch_succeeded"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_005","use_ref":"/blocks/block_005/instructions/0/inputs/0","definition_refs":["/blocks/block_004/instructions/0/outputs/1"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_010","opcode":"dispatch","draft_instruction_id":"go_branch_on_fast_fetch_first_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_006","semantic_name":"fast_fetch_succeeded"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_006","use_ref":"/blocks/block_005/instructions/1/inputs/0","definition_refs":["/blocks/block_005/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_005","/blocks/block_005/instructions/0/inputs/0","/blocks/block_004/instructions/0/outputs/1","/blocks/block_005/instructions/1/inputs/0","/blocks/block_005/instructions/0/outputs/0"]

## "block:/block_006"

```text
块键："block_006"
块 ID 原文："block_006"
块名称原文（仅作标签，不据此补造操作）："Append success status and return the first fast.fetch response body"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_011","opcode":"append_final_status_to_status_file","draft_instruction_id":"append_success_status_first_fast_fetch"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"status.txt","semantic_name":"local status.txt"},{"type":"literal","identifier":null,"literal_value":"success"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_012","opcode":"return","draft_instruction_id":"return_first_fast_fetch_body"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_004","semantic_name":"fast_fetch_response_body"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_004","use_ref":"/blocks/block_006/instructions/1/inputs/0","definition_refs":["/blocks/block_004/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_006","/blocks/block_006/instructions/1/inputs/0","/blocks/block_004/instructions/0/outputs/0"]

## "block:/block_007"

```text
块键："block_007"
块 ID 原文："block_007"
块名称原文（仅作标签，不据此补造操作）："Check whether the first fast.fetch failure was transient"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_013","opcode":"check_transient_error","draft_instruction_id":"check_fast_fetch_first_transient"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_005","semantic_name":"fast_fetch_error"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_007","semantic_name":"fast_fetch_error_transient"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_005","use_ref":"/blocks/block_007/instructions/0/inputs/0","definition_refs":["/blocks/block_004/instructions/0/outputs/1"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_014","opcode":"dispatch","draft_instruction_id":"go_branch_on_fast_fetch_first_transient"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_007","semantic_name":"fast_fetch_error_transient"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_007","use_ref":"/blocks/block_007/instructions/1/inputs/0","definition_refs":["/blocks/block_007/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_007","/blocks/block_007/instructions/0/inputs/0","/blocks/block_004/instructions/0/outputs/1","/blocks/block_007/instructions/1/inputs/0","/blocks/block_007/instructions/0/outputs/0"]

## "block:/block_008"

```text
块键："block_008"
块 ID 原文："block_008"
块名称原文（仅作标签，不据此补造操作）："Retry fast.fetch once"
数据来源标记："external"
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_015","opcode":"retry_fast_fetch","draft_instruction_id":"call_fast_fetch_retry"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"fast.fetch","semantic_name":"fast.fetch"},{"type":"result","identifier":"result_001","semantic_name":"source_id_value"},{"type":"result","identifier":"result_002","semantic_name":"fast_key"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_008","semantic_name":"retry_fast_fetch_response_body"},{"type":"result","identifier":"result_009","semantic_name":"retry_fast_fetch_error"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":1,"identifier":"result_001","use_ref":"/blocks/block_008/instructions/0/inputs/1","definition_refs":["/blocks/block_001/instructions/0/outputs/0"]},{"input_index":2,"identifier":"result_002","use_ref":"/blocks/block_008/instructions/0/inputs/2","definition_refs":["/blocks/block_002/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：["Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure."]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_016","opcode":"dispatch","draft_instruction_id":"go_check_retry_fast_fetch_success"}
  实际输入（按记录顺序）：[]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：mixed

图位置：["/blocks/block_008","/blocks/block_008/instructions/0/inputs/1","/blocks/block_001/instructions/0/outputs/0","/blocks/block_008/instructions/0/inputs/2","/blocks/block_002/instructions/0/outputs/0"]

## "block:/block_009"

```text
块键："block_009"
块 ID 原文："block_009"
块名称原文（仅作标签，不据此补造操作）："Check whether the fast.fetch retry succeeded"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_017","opcode":"check_fast_fetch_success","draft_instruction_id":"check_retry_fast_fetch_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_009","semantic_name":"retry_fast_fetch_error"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_010","semantic_name":"retry_fast_fetch_succeeded"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_009","use_ref":"/blocks/block_009/instructions/0/inputs/0","definition_refs":["/blocks/block_008/instructions/0/outputs/1"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_018","opcode":"dispatch","draft_instruction_id":"go_branch_on_retry_fast_fetch_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_010","semantic_name":"retry_fast_fetch_succeeded"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_010","use_ref":"/blocks/block_009/instructions/1/inputs/0","definition_refs":["/blocks/block_009/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_009","/blocks/block_009/instructions/0/inputs/0","/blocks/block_008/instructions/0/outputs/1","/blocks/block_009/instructions/1/inputs/0","/blocks/block_009/instructions/0/outputs/0"]

## "block:/block_010"

```text
块键："block_010"
块 ID 原文："block_010"
块名称原文（仅作标签，不据此补造操作）："Append success status and return the fast.fetch retry response body"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_019","opcode":"append_final_status_to_status_file","draft_instruction_id":"append_success_status_retry_fast_fetch"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"status.txt","semantic_name":"local status.txt"},{"type":"literal","identifier":null,"literal_value":"success"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_020","opcode":"return","draft_instruction_id":"return_retry_fast_fetch_body"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_008","semantic_name":"retry_fast_fetch_response_body"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_008","use_ref":"/blocks/block_010/instructions/1/inputs/0","definition_refs":["/blocks/block_008/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_010","/blocks/block_010/instructions/1/inputs/0","/blocks/block_008/instructions/0/outputs/0"]

## "block:/block_011"

```text
块键："block_011"
块 ID 原文："block_011"
块名称原文（仅作标签，不据此补造操作）："Call archive.fetch once with source_id"
数据来源标记："external"
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_021","opcode":"call_archive_fetch","draft_instruction_id":"call_archive_fetch"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"archive.fetch","semantic_name":"archive.fetch"},{"type":"result","identifier":"result_001","semantic_name":"source_id_value"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_011","semantic_name":"archive_fetch_response_body"},{"type":"result","identifier":"result_012","semantic_name":"archive_fetch_error"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":1,"identifier":"result_001","use_ref":"/blocks/block_011/instructions/0/inputs/1","definition_refs":["/blocks/block_001/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：["After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.","Call archive.fetch at most once and pass source_id as its only argument.","If archive.fetch fails, stop and return its error; do not retry archive.fetch."]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_022","opcode":"dispatch","draft_instruction_id":"go_check_archive_fetch_success"}
  实际输入（按记录顺序）：[]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：mixed

图位置：["/blocks/block_011","/blocks/block_011/instructions/0/inputs/1","/blocks/block_001/instructions/0/outputs/0"]

## "block:/block_012"

```text
块键："block_012"
块 ID 原文："block_012"
块名称原文（仅作标签，不据此补造操作）："Check whether archive.fetch succeeded"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_023","opcode":"check_archive_fetch_success","draft_instruction_id":"check_archive_fetch_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_012","semantic_name":"archive_fetch_error"}]
  实际输出（按记录顺序）：[{"type":"result","identifier":"result_013","semantic_name":"archive_fetch_succeeded"}]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_012","use_ref":"/blocks/block_012/instructions/0/inputs/0","definition_refs":["/blocks/block_011/instructions/0/outputs/1"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_024","opcode":"dispatch","draft_instruction_id":"go_branch_on_archive_fetch_success"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_013","semantic_name":"archive_fetch_succeeded"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_013","use_ref":"/blocks/block_012/instructions/1/inputs/0","definition_refs":["/blocks/block_012/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_012","/blocks/block_012/instructions/0/inputs/0","/blocks/block_011/instructions/0/outputs/1","/blocks/block_012/instructions/1/inputs/0","/blocks/block_012/instructions/0/outputs/0"]

## "block:/block_013"

```text
块键："block_013"
块 ID 原文："block_013"
块名称原文（仅作标签，不据此补造操作）："Append success status and return the archive.fetch response body"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_025","opcode":"append_final_status_to_status_file","draft_instruction_id":"append_success_status_archive_fetch"}
  实际输入（按记录顺序）：[{"type":"external_resource","identifier":"status.txt","semantic_name":"local status.txt"},{"type":"literal","identifier":null,"literal_value":"success"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
指令[1]：{"id":"ir_026","opcode":"return","draft_instruction_id":"return_archive_fetch_body"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_011","semantic_name":"archive_fetch_response_body"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_011","use_ref":"/blocks/block_013/instructions/1/inputs/0","definition_refs":["/blocks/block_011/instructions/0/outputs/0"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_013","/blocks/block_013/instructions/1/inputs/0","/blocks/block_011/instructions/0/outputs/0"]

## "block:/block_014"

```text
块键："block_014"
块 ID 原文："block_014"
块名称原文（仅作标签，不据此补造操作）："Append failure status and return the archive.fetch error"
数据来源标记：null
声明的约束（块级原文）：[]
实际记录的指令（按列表次序；显式排列不保证运行或 I/O 成功）：
指令[0]：{"id":"ir_028","opcode":"return","draft_instruction_id":"return_archive_fetch_error"}
  实际输入（按记录顺序）：[{"type":"result","identifier":"result_012","semantic_name":"archive_fetch_error"}]
  实际输出（按记录顺序）：[]
  result 引用定位（仅按 identifier，不按 semantic_name 合并）：[{"input_index":0,"identifier":"result_012","use_ref":"/blocks/block_014/instructions/0/inputs/0","definition_refs":["/blocks/block_011/instructions/0/outputs/1"]}]
  声明的约束（指令级原文）：[]
  metadata 嵌入内容（完整保留，未解释、未执行）：{}
```

依据：explicit_graph

图位置：["/blocks/block_014","/blocks/block_014/instructions/0/inputs/0","/blocks/block_011/instructions/0/outputs/1"]

## "edge:0"

```text
记录的边："block_001" → "block_002"；未记录条件文字（condition_text=null；不据此断言执行条件恒真）
```

依据：explicit_graph

图位置：["/edges/0"]

## "edge:1"

```text
记录的边："block_002" → "block_003"；未记录条件文字（condition_text=null；不据此断言执行条件恒真）
```

依据：explicit_graph

图位置：["/edges/1"]

## "edge:2"

```text
记录的边："block_003" → "block_004"；记录的条件文字原文："FAST_KEY is present"
```

依据：explicit_graph

图位置：["/edges/2"]

## "edge:3"

```text
记录的边："block_003" → "block_011"；记录的条件文字原文："FAST_KEY is absent"
```

依据：explicit_graph

图位置：["/edges/3"]

## "edge:4"

```text
记录的边："block_004" → "block_005"；未记录条件文字（condition_text=null；不据此断言执行条件恒真）
```

依据：explicit_graph

图位置：["/edges/4"]

## "edge:5"

```text
记录的边："block_005" → "block_006"；记录的条件文字原文："first fast.fetch attempt succeeded"
```

依据：explicit_graph

图位置：["/edges/5"]

## "edge:6"

```text
记录的边："block_005" → "block_007"；记录的条件文字原文："first fast.fetch attempt failed"
```

依据：explicit_graph

图位置：["/edges/6"]

## "edge:7"

```text
记录的边："block_007" → "block_008"；记录的条件文字原文："first fast.fetch failure was transient"
```

依据：explicit_graph

图位置：["/edges/7"]

## "edge:8"

```text
记录的边："block_007" → "block_011"；记录的条件文字原文："first fast.fetch failure was non-transient"
```

依据：explicit_graph

图位置：["/edges/8"]

## "edge:9"

```text
记录的边："block_008" → "block_009"；未记录条件文字（condition_text=null；不据此断言执行条件恒真）
```

依据：explicit_graph

图位置：["/edges/9"]

## "edge:10"

```text
记录的边："block_009" → "block_010"；记录的条件文字原文："fast.fetch retry succeeded"
```

依据：explicit_graph

图位置：["/edges/10"]

## "edge:11"

```text
记录的边："block_009" → "block_011"；记录的条件文字原文："fast.fetch retry failed"
```

依据：explicit_graph

图位置：["/edges/11"]

## "edge:12"

```text
记录的边："block_011" → "block_012"；未记录条件文字（condition_text=null；不据此断言执行条件恒真）
```

依据：explicit_graph

图位置：["/edges/12"]

## "edge:13"

```text
记录的边："block_012" → "block_013"；记录的条件文字原文："archive.fetch succeeded"
```

依据：explicit_graph

图位置：["/edges/13"]

## "edge:14"

```text
记录的边："block_012" → "block_014"；记录的条件文字原文："archive.fetch failed"
```

依据：explicit_graph

图位置：["/edges/14"]
