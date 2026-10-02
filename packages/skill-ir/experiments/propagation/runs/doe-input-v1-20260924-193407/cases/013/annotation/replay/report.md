# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_012` / `effects`：return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。
- `ir_014` / `effects`：return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。
- `ir_016` / `effects`：return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。
- `ir_018` / `effects`：return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id | agent_runtime | source | 1. context_read |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key | agent_runtime | source, transformer | 1. context_read<br>2. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | fast.fetch | tool, llm | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Retry fast.fetch once after a transient error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool, llm | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | archive.fetch | tool, llm | source, sink | 1. net_send<br>2. net_receive<br>3. model_observe |
| ir_010 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_006 · Append success status and return fast.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_012 | return | agent_runtime | sink | 顺序未确定；编号仅供证据定位。<br>[]（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_007 · Append success status and return fast.fetch retry body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_014 | return | agent_runtime | sink | 顺序未确定；编号仅供证据定位。<br>[]（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_008 · Append success status and return archive.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_016 | return | agent_runtime | sink | 顺序未确定；编号仅供证据定位。<br>[]（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_009 · Append failure status and return archive.fetch error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_017 | append_status_to_local_file | agent_runtime | sink | 1. fs_write |
| ir_018 | return | agent_runtime | sink | 顺序未确定；编号仅供证据定位。<br>[]（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `loc_rt_source_id`：`runtime_context` / `source_id`。
- 位置 `loc_rt_FAST_KEY`：`runtime_context` / `FAST_KEY`。
- 位置 `loc_remote_fast_fetch`：`remote` / `fast.fetch`。
- 位置 `loc_remote_archive_fetch`：`remote` / `archive.fetch`。
- 位置 `loc_storage_status_txt`：`storage` / `local status.txt`。
- 位置 `loc_model_context`：`model_context` / `LLM context`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_rt_source_id", "output": "v_ir001_source_id"}`
- output[0] ← `{"kind": "local", "name": "v_ir001_source_id"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_rt_FAST_KEY", "output": "v_ir003_fast_key"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir003_fast_key"}], "dependencies": ["derived"], "output": "v_ir003_fast_key_present"}`
- output[0] ← `{"kind": "local", "name": "v_ir003_fast_key"}`
- output[1] ← `{"kind": "local", "name": "v_ir003_fast_key_present"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_remote_fast_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "v_ir005_result"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir005_result"}], "dependencies": ["derived"], "output": "v_ir005_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir005_result"}], "dependencies": ["derived"], "output": "v_ir005_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir005_result"}], "dependencies": ["derived"], "output": "v_ir005_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "v_ir005_result"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "v_ir005_body"}`
- output[1] ← `{"kind": "local", "name": "v_ir005_error"}`
- output[2] ← `{"kind": "local", "name": "v_ir005_status"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_remote_fast_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "v_ir007_result"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir007_result"}], "dependencies": ["derived"], "output": "v_ir007_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir007_result"}], "dependencies": ["derived"], "output": "v_ir007_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir007_result"}], "dependencies": ["derived"], "output": "v_ir007_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "v_ir007_result"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "v_ir007_body"}`
- output[1] ← `{"kind": "local", "name": "v_ir007_error"}`
- output[2] ← `{"kind": "local", "name": "v_ir007_status"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}], "target": "loc_remote_archive_fetch"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "receive", "location": "loc_remote_archive_fetch", "inputs": [{"kind": "input", "index": 1}], "output": "v_ir009_result"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir009_result"}], "dependencies": ["derived"], "output": "v_ir009_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir009_result"}], "dependencies": ["derived"], "output": "v_ir009_error"}`
  - 操作 3：`{"op": "compute", "inputs": [{"kind": "local", "name": "v_ir009_result"}], "dependencies": ["derived"], "output": "v_ir009_status"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "v_ir009_result"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "v_ir009_body"}`
- output[1] ← `{"kind": "local", "name": "v_ir009_error"}`
- output[2] ← `{"kind": "local", "name": "v_ir009_status"}`

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

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 是本地读取运行时上下文键的操作，由代理运行时执行，不是模型或工具。

> read_source_id

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从用户请求/运行时上下文引入 source_id 到当前流程。

> Read source_id from the user's request

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：输入类型 context_key 表明该操作获取运行时上下文内容。

> context_key

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：本地控制分发由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转，不引入、写出或转换内容数据，因此无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：控制流操作在给定效果词汇中没有适用项，不强制标记 transform。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 是本地读取环境/运行时上下文的操作，由代理运行时执行。

> read_fast_key

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从环境读取 FAST_KEY，将凭据内容引入当前流程。

> read FAST_KEY from the environment

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：输出存在性布尔值，改变表示形式，属于本地转换。

> fast_key_present

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：输入类型 context_key 表明读取运行时上下文/环境变量。

> context_key

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：由读取的 FAST_KEY 派生 fast_key_present 布尔值。

> fast_key_present

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：本地控制分发由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅依据存在性结果进行控制跳转，不引入、写出或转换内容数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，在给定效果词汇中没有适用项。

> dispatch

### ir_005

- `operator` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：fast.fetch 工具执行该抓取动作。

> fast.fetch

- `operator` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 上下文，模型参与结果观察。

> content returned by an agent tool enters the LLM context by default.

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：接收远程响应体，将外部内容引入当前流程。

> fast_fetch_first_body

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将请求参数发送到远程 fast.fetch，形成接收方边界。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：向 fast.fetch 发送 source_id 和 FAST_KEY 请求参数。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0021`。
  理由：该调用接收远程响应体、错误和状态。

> fast_fetch_first_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 处理上下文，形成模型观察。

> content returned by an agent tool enters the LLM context by default.

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：本地控制分发由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅依据状态结果进行控制跳转，不引入、写出或转换内容数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，在给定效果词汇中没有适用项。

> dispatch

### ir_007

- `operator` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：fast.fetch 工具执行该重试抓取动作。

> fast.fetch

- `operator` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 上下文，模型参与结果观察。

> content returned by an agent tool enters the LLM context by default.

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：接收远程重试响应体，将外部内容引入当前流程。

> fast_fetch_retry_body

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：重试调用向远程 fast.fetch 发送请求参数，形成接收方边界。

> Retry fast.fetch exactly once

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `cfg`，位置 `g_0027`。
  理由：重试 IR 输入包含 fast_key 以及 source_id，并作为 fast.fetch 请求参数发送。

> fast_key

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0027`。
  理由：该重试调用接收远程响应体、错误和状态。

> fast_fetch_retry_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 处理上下文，形成模型观察。

> content returned by an agent tool enters the LLM context by default.

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：本地控制分发由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅依据重试状态进行控制跳转，不引入、写出或转换内容数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，在给定效果词汇中没有适用项。

> dispatch

### ir_009

- `operator` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：archive.fetch 工具执行该抓取动作。

> archive.fetch

- `operator` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 上下文，模型参与结果观察。

> content returned by an agent tool enters the LLM context by default.

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：接收 archive.fetch 响应体，将外部内容引入当前流程。

> archive_body

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 source_id 发送到远程 archive.fetch，形成接收方边界。

> pass source_id as its only argument

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 请求只发送 source_id 作为参数，不发送 FAST_KEY。

> pass source_id as its only argument

- `effects` / 步骤 2（索引 1） / `net_receive`；依据 `cfg`，位置 `g_0033`。
  理由：接收 archive.fetch 的响应体、错误和状态。

> archive_body

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认进入 LLM 处理上下文，形成模型观察。

> content returned by an agent tool enters the LLM context by default.

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：本地控制分发由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅依据 archive 状态进行控制跳转，不引入、写出或转换内容数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，在给定效果词汇中没有适用项。

> dispatch

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地文件追加操作由代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将状态内容写入本地存储位置，形成存储边界。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加内容，属于文件写入。

> append the final status to local status.txt

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：本地返回控制由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将成功响应体交给调用方，形成可见性边界；未证明直接面向用户。

> return that successful response's body value unchanged

### ir_013

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地文件追加操作由代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将重试成功状态写入本地存储位置，形成存储边界。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加重试成功状态，属于文件写入。

> append the final status to local status.txt

### ir_014

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：本地返回控制由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将重试成功响应体交给调用方，形成可见性边界；未证明直接面向用户。

> return that successful response's body value unchanged

### ir_015

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：本地文件追加操作由代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive 成功状态写入本地存储位置，形成存储边界。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加 archive 成功状态，属于文件写入。

> append the final status to local status.txt

### ir_016

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：本地返回控制由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive 成功响应体交给调用方，形成可见性边界；未证明直接面向用户。

> return that successful response's body value unchanged

### ir_017

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：本地文件追加操作由代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive 失败状态写入本地存储位置，形成存储边界。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加 archive 失败状态，属于文件写入。

> append the final status to local status.txt

### ir_018

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：本地返回控制由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive 错误交给调用方，形成可见性边界；未证明直接面向用户。

> return its error

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
