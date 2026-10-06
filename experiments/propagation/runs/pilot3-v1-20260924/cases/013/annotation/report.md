# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64`

[四字段标注](profiles.json) · [位置声明](locations.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id | agent_runtime | source | 1. context_read |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key | agent_runtime | source | 1. context_read |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | fast.fetch | agent_runtime, tool | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Retry fast.fetch once after a transient error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | agent_runtime, tool | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | archive.fetch | agent_runtime, tool | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_010 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_006 · Append success status and return fast.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_012 | return | agent_runtime | sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_007 · Append success status and return fast.fetch retry body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_014 | return | agent_runtime | sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_008 · Append success status and return archive.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_016 | return | agent_runtime | sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_009 · Append failure status and return archive.fetch error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_017 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_018 | return | agent_runtime | sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `loc_ctx_source_id`：`runtime_context` / `source_id`。
- 位置 `loc_ctx_FAST_KEY`：`runtime_context` / `FAST_KEY`。
- 位置 `loc_remote_fast_fetch`：`remote` / `fast.fetch`。
- 位置 `loc_remote_archive_fetch`：`remote` / `archive.fetch`。
- 位置 `loc_storage_status_txt`：`storage` / `local status.txt`。
- 位置 `loc_model_context`：`model_context` / `symbolic:llm_context`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_ctx_source_id", "output": "ir_001_source_id"}`
- output[0] ← `{"kind": "local", "name": "ir_001_source_id"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_ctx_FAST_KEY", "output": "ir_003_fast_key"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_003_fast_key"}], "dependencies": ["derived"], "output": "ir_003_fast_key_present"}`
- output[0] ← `{"kind": "local", "name": "ir_003_fast_key"}`
- output[1] ← `{"kind": "local", "name": "ir_003_fast_key_present"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_remote_fast_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "ir_005_response"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_005_response"}], "dependencies": ["possible"], "output": "ir_005_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_005_response"}], "dependencies": ["possible"], "output": "ir_005_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_005_response"}], "dependencies": ["derived"], "output": "ir_005_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "ir_005_body"}, {"kind": "local", "name": "ir_005_error"}, {"kind": "local", "name": "ir_005_status"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "ir_005_body"}`
- output[1] ← `{"kind": "local", "name": "ir_005_error"}`
- output[2] ← `{"kind": "local", "name": "ir_005_status"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_remote_fast_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "ir_007_response"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_007_response"}], "dependencies": ["possible"], "output": "ir_007_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_007_response"}], "dependencies": ["possible"], "output": "ir_007_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_007_response"}], "dependencies": ["derived"], "output": "ir_007_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "ir_007_body"}, {"kind": "local", "name": "ir_007_error"}, {"kind": "local", "name": "ir_007_status"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "ir_007_body"}`
- output[1] ← `{"kind": "local", "name": "ir_007_error"}`
- output[2] ← `{"kind": "local", "name": "ir_007_status"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}], "target": "loc_remote_archive_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_archive_fetch", "inputs": [{"kind": "input", "index": 1}], "output": "ir_009_response"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_009_response"}], "dependencies": ["possible"], "output": "ir_009_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_009_response"}], "dependencies": ["possible"], "output": "ir_009_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "ir_009_response"}], "dependencies": ["derived"], "output": "ir_009_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "ir_009_body"}, {"kind": "local", "name": "ir_009_error"}, {"kind": "local", "name": "ir_009_status"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "ir_009_body"}`
- output[1] ← `{"kind": "local", "name": "ir_009_error"}`
- output[2] ← `{"kind": "local", "name": "ir_009_status"}`

### ir_010 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_011 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_storage_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_012 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_013 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_storage_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_014 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_015 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_storage_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_016 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_017 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_storage_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_018 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：从用户请求或运行时上下文读取 source_id 的动作由本地代理运行时执行。

> Read source_id from the user's request

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该读取把 source_id 引入当前流程，充当来源角色。

> Read source_id from the user's request

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：指令从 context_key 读取 source_id，属于运行时上下文读取。

> read_source_id

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 由本地代理运行时执行控制跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转不引入、发送或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表无适用效果；不代表无操作。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：从环境读取 FAST_KEY 由本地代理运行时执行。

> read FAST_KEY from the environment

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取 FAST_KEY 将其引入当前流程，充当来源角色。

> read FAST_KEY from the environment

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：指令从 context_key 读取 FAST_KEY，属于运行时上下文读取。

> read_fast_key

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 由本地代理运行时执行控制跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制跳转不引入、发送或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，词表无适用效果；不代表无操作。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地代理运行时发起并编排 fast.fetch 调用。

> try fast.fetch first with source_id and FAST_KEY

- `operator` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：fast.fetch 是执行远端获取动作的工具。

> fast.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：工具响应体等结果引入当前流程，充当来源角色。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 source_id 与 FAST_KEY 作为参数发往远端 fast.fetch，形成接收端边界前的汇点角色。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：将 source_id 和 FAST_KEY 作为请求参数发往远端工具，符合 net_send。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0021`。
  理由：fast.fetch 输出响应体、错误和状态，表明从远端接收响应。

> fast_fetch_first_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 上下文，且未见隔离边界。

> content returned by an agent tool enters the LLM context by default

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 由本地代理运行时执行控制跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制跳转不引入、发送或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，词表无适用效果；不代表无操作。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地代理运行时按条件发起 fast.fetch 重试。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `operator` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：fast.fetch 是执行重试远端获取动作的工具。

> fast.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：重试成功后的响应体等结果引入当前流程，充当来源角色。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：重试调用仍包含 FAST_KEY 输入并发送到远端 fast.fetch，形成汇点角色。

> result_002

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `cfg`，位置 `g_0027`。
  理由：重试 fast.fetch 将包含 FAST_KEY 的参数发往远端，符合 net_send。

> result_002

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0027`。
  理由：fast.fetch 重试输出响应体、错误和状态，表明从远端接收响应。

> fast_fetch_retry_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：重试工具返回内容默认进入 LLM 上下文，且未见隔离边界。

> content returned by an agent tool enters the LLM context by default

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 由本地代理运行时执行控制跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制跳转不引入、发送或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，词表无适用效果；不代表无操作。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地代理运行时执行该归档获取调用。

> Call archive.fetch at most once and pass source_id as its only argument.

- `operator` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：archive.fetch 是执行归档获取动作的工具。

> archive.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：归档工具成功响应体等结果引入当前流程，充当来源角色。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 source_id 发往远端 archive.fetch，且约束排除 FAST_KEY，形成汇点角色。

> Call archive.fetch at most once and pass source_id as its only argument.

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：将 source_id 作为请求参数发往远端 archive.fetch，符合 net_send，且未发送 FAST_KEY。

> Call archive.fetch at most once and pass source_id as its only argument.

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0033`。
  理由：archive.fetch 输出响应体、错误和状态，表明从远端接收响应。

> archive_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：归档工具返回内容默认进入 LLM 上下文，且未见隔离边界。

> content returned by an agent tool enters the LLM context by default

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 由本地代理运行时执行控制跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制跳转不引入、发送或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，词表无适用效果；不代表无操作。

> dispatch

### ir_011

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加动作由代理运行时执行，未出现工具执行者。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将状态内容写入本地存储位置，充当汇点角色。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加状态到本地文件，创建或修改文件内容。

> append the final status to local status.txt

### ir_012

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：return 指令由本地代理运行时执行。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将成功响应体原样返回给调用方，形成内容传递边界，但未证明直接面向用户。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 只转发 result_004；EM06 明确不能据此判定 user_output，词表也无普通返回效果。

> an ordinary return alone does not prove user-facing output

### ir_013

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加动作由代理运行时执行，未出现工具执行者。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将重试状态内容写入本地存储位置，充当汇点角色。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加重试状态到本地文件，创建或修改文件内容。

> append the final status to local status.txt

### ir_014

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：return 指令由本地代理运行时执行。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将重试成功响应体原样返回给调用方，形成内容传递边界，但未证明直接面向用户。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 只转发 result_007；EM06 明确不能据此判定 user_output，词表也无普通返回效果。

> an ordinary return alone does not prove user-facing output

### ir_015

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加动作由代理运行时执行，未出现工具执行者。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将归档成功状态内容写入本地存储位置，充当汇点角色。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加归档成功状态到本地文件，创建或修改文件内容。

> append the final status to local status.txt

### ir_016

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：return 指令由本地代理运行时执行。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将归档成功响应体原样返回给调用方，形成内容传递边界，但未证明直接面向用户。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 只转发 result_010；EM06 明确不能据此判定 user_output，词表也无普通返回效果。

> an ordinary return alone does not prove user-facing output

### ir_017

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加动作由代理运行时执行，未出现工具执行者。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将归档失败状态内容写入本地存储位置，充当汇点角色。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加归档失败状态到本地文件，创建或修改文件内容。

> append the final status to local status.txt

### ir_018

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：return 指令由本地代理运行时执行。

> return its error

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive.fetch 错误返回给调用方，形成内容传递边界，但未证明直接面向用户。

> return its error

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 只转发 result_011；EM06 明确不能据此判定 user_output，词表也无普通返回效果。

> an ordinary return alone does not prove user-facing output

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
