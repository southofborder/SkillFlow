# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_user_request | agent_runtime, llm | source, sink, transformer | 1. context_read<br>2. model_observe<br>3. transform |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | source | 1. context_read |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_presence | agent_runtime | transformer | 1. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool | source, sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · Classify the first fast.fetch attempt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | classify_fast_fetch_outcome | agent_runtime | sink, transformer | 1. model_observe<br>2. transform |
| ir_010 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | fast.fetch | tool | source, sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |
| ir_012 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_007 · Classify the fast.fetch retry

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | classify_fast_fetch_outcome | agent_runtime | sink, transformer | 1. model_observe<br>2. transform |
| ir_014 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_008 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | archive.fetch | tool | source, sink | []（无已记录效果；不等于空操作，请结合证据与未决项） |
| ir_016 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_009 · Classify the archive.fetch result

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_017 | classify_fetch_outcome | agent_runtime | sink, transformer | 1. model_observe<br>2. transform |
| ir_018 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_010 · Append status and return the first fast.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_020 | return | agent_runtime | sink | 1. user_output |

### block_011 · Append status and return the fast.fetch retry body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_021 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_022 | return | agent_runtime | sink | 1. user_output |

### block_012 · Append status and return the archive.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_023 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_024 | return | agent_runtime | sink | 1. user_output |

### block_013 · Append status and return the archive.fetch error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_025 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_026 | return | agent_runtime | sink | 1. user_output |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `loc_user_request`：`runtime_context` / `user_request`。
- 位置 `loc_environment`：`runtime_context` / `environment`。
- 位置 `loc_fast_key`：`runtime_context` / `environment.FAST_KEY`。
- 位置 `loc_fast_fetch_tool`：`tool` / `fast.fetch`。
- 位置 `loc_archive_fetch_tool`：`tool` / `archive.fetch`。
- 位置 `loc_status_file`：`storage` / `local status.txt`。
- 位置 `loc_model_context`：`model_context` / `agent_model_context`。
- 位置 `loc_user`：`user` / `user`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_user_request", "output": "user_request_container"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "user_request_container"}], "target": "loc_model_context"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "user_request_container"}, "path": ["source_id"], "output": "source_id"}`
- output[0] ← `{"kind": "local", "name": "source_id"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_fast_key", "output": "fast_key"}`
- output[0] ← `{"kind": "local", "name": "fast_key"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_key_present"}`
- output[0] ← `{"kind": "local", "name": "fast_key_present"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：无匹配效果的保守计算。
  - 操作 0：`{"op": "receive", "location": "loc_fast_fetch_tool", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_first_response"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_response"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_model_context"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_first_outcome"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_first_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_first_body"}`

### ir_010 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_011 · 事件与公开结果

- 事件 0：无匹配效果的保守计算。
  - 操作 0：`{"op": "receive", "location": "loc_fast_fetch_tool", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_retry_response"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_response"}`

### ir_012 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_013 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_model_context"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_retry_outcome"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_retry_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_retry_body"}`

### ir_014 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_015 · 事件与公开结果

- 事件 0：无匹配效果的保守计算。
  - 操作 0：`{"op": "receive", "location": "loc_archive_fetch_tool", "inputs": [{"kind": "input", "index": 1}], "output": "archive_fetch_response"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_response"}`

### ir_016 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_017 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_model_context"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "archive_fetch_outcome"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "archive_fetch_body"}`
  - 操作 2：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "archive_fetch_error"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_outcome"}`
- output[1] ← `{"kind": "local", "name": "archive_fetch_body"}`
- output[2] ← `{"kind": "local", "name": "archive_fetch_error"}`

### ir_018 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_019 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_020 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_user"}`

### ir_021 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_022 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_user"}`

### ir_023 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_024 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_user"}`

### ir_025 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_026 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "loc_user"}`

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该读取动作由本地代理运行时从 user_request 上下文发起。

> read_source_id_from_user_request

- `operator` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：用户请求用于自然语言提取 source_id，LLM 参与处理。

> For content acquired for the agent's natural-language processing, assume that content enters model processing

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取用户请求并把内容引入当前流程，承担 source。

> Read source_id from the user's request

- `roles` / `sink`；依据 `execution_model`，位置 `EM03`。
  理由：请求内容进入模型处理上下文，构成至模型可见边界的 sink。

> assume that content enters model processing

- `roles` / `transformer`；依据 `cfg`，位置 `g_0009`。
  理由：从请求容器中选出 source_id，承担 transformer。

> read_source_id_from_user_request

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取 user_request 运行时上下文内容。

> context_key

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`，位置 `EM03`。
  理由：自然语言请求容器按 EM03 进入模型处理上下文。

> assume that content enters model processing

- `effects` / 步骤 3（索引 2） / `transform`；依据 `cfg`，位置 `g_0009`。
  理由：在观察后从请求容器中显式选择 source_id，属于 transform。

> source_id

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：环境变量读取由本地代理运行时执行。

> read_fast_key_from_environment

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从环境读取 FAST_KEY 并引入当前流程，承担 source。

> read FAST_KEY from the environment

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：读取运行时环境上下文中的 FAST_KEY 绑定。

> context_key

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：存在性检查由本地代理运行时执行。

> check_fast_key_presence

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：将 FAST_KEY 转换为存在性布尔结果，承担 transformer。

> check_fast_key_presence

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：计算 FAST_KEY 是否存在的布尔结果，属于 transform。

> fast_key_present

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_007

- `operator` / `tool`；依据 `source`，位置 `src_003`。
  理由：fast.fetch 工具执行该抓取动作。

> try fast.fetch first with source_id and FAST_KEY

- `roles` / `source`；依据 `execution_model`，位置 `EM09`。
  理由：该调用在工具边界获取 fast.fetch 响应，承担 source。

> use receive at a tool location in a null-effect event

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：source_id 与 FAST_KEY 作为请求参数到达 fast.fetch 工具边界，承担 sink。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM09`。
  理由：未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。

> if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：分类提取由本地代理运行时执行。

> classify_fast_fetch_outcome

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：工具响应进入模型上下文，构成至模型可见边界的 sink。

> content returned by an agent tool enters the LLM context by default

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：从响应中分类并提取 outcome/body，承担 transformer。

> classify_fast_fetch_outcome

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch 返回内容按工具结果假设进入模型处理上下文。

> content returned by an agent tool enters the LLM context by default

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：对已观察响应进行分类并提取 outcome 与 body，属于 transform。

> fast_fetch_first_body

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_011

- `operator` / `tool`；依据 `source`，位置 `src_003`。
  理由：fast.fetch 工具执行重试抓取。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `roles` / `source`；依据 `execution_model`，位置 `EM09`。
  理由：重试调用在工具边界获取 fast.fetch 响应，承担 source。

> use receive at a tool location in a null-effect event

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：重试调用同样以 source_id 和 FAST_KEY 为参数到达 fast.fetch 工具边界，承担 sink。

> fast_key

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM09`。
  理由：未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。

> if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_013

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：重试响应分类由本地代理运行时执行。

> classify_fast_fetch_outcome

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：重试工具响应进入模型上下文，构成至模型可见边界的 sink。

> content returned by an agent tool enters the LLM context by default

- `roles` / `transformer`；依据 `cfg`，位置 `g_0045`。
  理由：从重试响应中分类并提取 outcome/body，承担 transformer。

> classify_fast_fetch_outcome

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch 重试返回内容按工具结果假设进入模型处理上下文。

> content returned by an agent tool enters the LLM context by default

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0045`。
  理由：对已观察重试响应进行分类并提取 outcome 与 body，属于 transform。

> fast_fetch_retry_body

### ir_014

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_015

- `operator` / `tool`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 工具执行该抓取动作。

> call archive.fetch with source_id

- `roles` / `source`；依据 `execution_model`，位置 `EM09`。
  理由：该调用在工具边界获取 archive.fetch 响应，承担 source。

> use receive at a tool location in a null-effect event

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：仅 source_id 作为参数到达 archive.fetch 工具边界，承担 sink。

> call archive.fetch with source_id

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM09`。
  理由：未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。

> if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event

### ir_016

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_017

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：archive.fetch 响应分类由本地代理运行时执行。

> classify_fetch_outcome

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：archive.fetch 响应进入模型上下文，构成至模型可见边界的 sink。

> content returned by an agent tool enters the LLM context by default

- `roles` / `transformer`；依据 `cfg`，位置 `g_0057`。
  理由：分类并提取 outcome/body/error，承担 transformer。

> classify_fetch_outcome

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：archive.fetch 返回内容按工具结果假设进入模型处理上下文。

> content returned by an agent tool enters the LLM context by default

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0057`。
  理由：对已观察响应进行分类并提取 outcome、body 与 error，属于 transform。

> archive_fetch_body

### ir_018

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：dispatch 由本地代理运行时执行控制转移。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制分派不引入、传递或转换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。

> dispatch

### ir_019

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：本地文件追加由代理运行时执行。

> append_final_status_to_local_status_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：最终状态内容到达本地文件存储位置，承担 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加内容，属于 fs_write。

> append the final status to local status.txt

### ir_020

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：返回操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将成功响应 body 提供给用户可见输出边界，承担 sink。

> return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `user_output`；依据 `source`，位置 `src_003`。
  理由：该最终返回将 body 提供给用户，属于 user_output。

> return that successful response's body value unchanged

### ir_021

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0069`。
  理由：本地文件追加由代理运行时执行。

> append_final_status_to_local_status_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：重试最终状态内容到达本地文件存储位置，承担 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加内容，属于 fs_write。

> append the final status to local status.txt

### ir_022

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0070`。
  理由：返回操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将重试成功响应 body 提供给用户可见输出边界，承担 sink。

> return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `user_output`；依据 `source`，位置 `src_003`。
  理由：该最终返回将 body 提供给用户，属于 user_output。

> return that successful response's body value unchanged

### ir_023

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0075`。
  理由：本地文件追加由代理运行时执行。

> append_final_status_to_local_status_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 成功状态内容到达本地文件存储位置，承担 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加内容，属于 fs_write。

> append the final status to local status.txt

### ir_024

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0076`。
  理由：返回操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive.fetch 成功响应 body 提供给用户可见输出边界，承担 sink。

> return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `user_output`；依据 `source`，位置 `src_003`。
  理由：该最终返回将 body 提供给用户，属于 user_output。

> return that successful response's body value unchanged

### ir_025

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0081`。
  理由：本地文件追加由代理运行时执行。

> append_final_status_to_local_status_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 失败状态内容到达本地文件存储位置，承担 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地 status.txt 追加内容，属于 fs_write。

> append the final status to local status.txt

### ir_026

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0082`。
  理由：返回操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将 archive.fetch 错误提供给用户可见输出边界，承担 sink。

> return its error

- `effects` / 步骤 1（索引 0） / `user_output`；依据 `source`，位置 `src_003`。
  理由：该最终返回将错误提供给用户，属于 user_output。

> return its error

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
