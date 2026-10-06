# 安全语义标注：repair

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v3`；摘要：`26cd7f0d607b13377dc5d93546b9844b02f37db89b8dd8554613ea60e5b878ce`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "8b63b77c85c01ea7e30310e566fa3a8601f1aad4b6f801caee87f858c91d2207",
  "observed": true,
  "requests": [
    {
      "request_parameters": {
        "model": "deepseek-v4-flash",
        "reasoning_effort": "max",
        "response_format": {
          "type": "json_object"
        },
        "stream": true,
        "stream_options": {
          "include_usage": true
        }
      },
      "request_body_sha256": "7eda99ad107007e4a3ecffee902b233263c8d6647555330836882e80dba69f2f"
    }
  ],
  "transport": "http"
}
```

没有记录执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_user_request | agent_runtime | source | 1. context_read<br>2. model_observe<br>3. transform |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | source | 1. context_read<br>2. model_observe<br>3. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_presence | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool | source, sink | 1. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_005 · Classify the first fast.fetch attempt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | classify_fast_fetch_outcome | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_010 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | fast.fetch | tool | source, sink | 1. model_observe |
| ir_012 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_007 · Classify the fast.fetch retry

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | classify_fast_fetch_outcome | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_014 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_008 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | archive.fetch | tool | source, sink | 1. model_observe |
| ir_016 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_009 · Classify the archive.fetch result

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_017 | classify_fetch_outcome | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_018 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_010 · Append status and return the first fast.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_020 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_011 · Append status and return the fast.fetch retry body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_021 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_022 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_012 · Append status and return the archive.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_023 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_024 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_013 · Append status and return the archive.fetch error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_025 | append_final_status_to_local_status_file | agent_runtime | sink | 1. fs_write |
| ir_026 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)

- 位置 `loc_user_request`：`runtime_context` / `user_request`。
- 位置 `loc_environment`：`runtime_context` / `environment`。
- 位置 `loc_status_txt`：`storage` / `status.txt`。
- 位置 `loc_fast_fetch`：`tool` / `fast.fetch`。
- 位置 `loc_archive_fetch`：`tool` / `archive.fetch`。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：3 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_user_request", "output": "user_request_content"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "user_request_content"}], "target": "__compiled_model_context__"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "user_request_content"}, "path": ["source_id"], "output": "source_id"}`
- output[0] ← `{"kind": "local", "name": "source_id"}`

### ir_002 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

次序：`fixed`；编译因果约束：3 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_environment", "output": "environment_content"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "environment_content"}], "target": "__compiled_model_context__"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "environment_content"}, "path": ["FAST_KEY"], "output": "fast_key"}`
- output[0] ← `{"kind": "local", "name": "fast_key"}`

### ir_004 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_key_present"}`
- output[0] ← `{"kind": "local", "name": "fast_key_present"}`

### ir_006 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "receive", "location": "loc_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_first_response"}`
- 事件 1：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "fast_fetch_first_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_response"}`

### ir_008 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_first_outcome"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_first_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_first_body"}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_011 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "receive", "location": "loc_fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_retry_response"}`
- 事件 1：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "fast_fetch_retry_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_response"}`

### ir_012 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_013 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_retry_outcome"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_retry_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_retry_body"}`

### ir_014 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_015 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "receive", "location": "loc_archive_fetch", "inputs": [{"kind": "input", "index": 1}], "output": "archive_fetch_response"}`
- 事件 1：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "archive_fetch_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_response"}`

### ir_016 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_017 · 事件与公开结果

次序：`fixed`；编译因果约束：3 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "archive_fetch_outcome"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "archive_fetch_body"}`
  - 操作 2：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["error"], "output": "archive_fetch_error"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_outcome"}`
- output[1] ← `{"kind": "local", "name": "archive_fetch_body"}`
- output[2] ← `{"kind": "local", "name": "archive_fetch_error"}`

### ir_018 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_019 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_020 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_021 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_022 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_023 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_024 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_025 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_txt", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_026 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文要求执行读取动作；该动作由运行 Skill 的 agent runtime 承担，未出现 LLM 或工具参与读取的证据。

> Read source_id from the user's request and read FAST_KEY from the environment.

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从用户请求引入 source_id 到当前流程，属于数据来源角色。

> Read source_id from the user's request and read FAST_KEY from the environment.

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `source`，位置 `src_003`。
  理由：从上下文键 user_request 读取用户请求内容，符合 context_read。

> Read source_id from the user's request and read FAST_KEY from the environment.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只规定从用户请求读取 source_id，没有本地隔离或受限返回机制，按契约默认模式处理；读取范围保留 user_request 整体。

> Read source_id from the user's request and read FAST_KEY from the environment.

- `effects` / 步骤 3（索引 2） / `transform`；依据 `source`，位置 `src_003`。
  理由：从读取到的用户请求内容中选出明确字段 source_id，保持原值。

> Read source_id from the user's request

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该指令是控制流分派，由运行 Skill 的 agent runtime 执行；未涉及内容处理。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：该分派不引入、输出或转换数据，无适用 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流分派，在 effects 词表中无适用效果；不强制标为 transform。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：读取环境变量的动作由运行 Skill 的 agent runtime 执行。

> Read source_id from the user's request and read FAST_KEY from the environment.

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从环境引入 FAST_KEY 到当前流程，属于数据来源角色。

> read FAST_KEY from the environment

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `source`，位置 `src_003`。
  理由：从运行时上下文环境读取 FAST_KEY，符合 context_read。

> read FAST_KEY from the environment

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只规定从环境读取 FAST_KEY，没有给出显式本地隔离、受限返回或凭据代理机制，因此不能据此声明 local 模式。

> read FAST_KEY from the environment

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：按 EM10，缺少显式本地执行及返回边界证据时采用 default 模式，读取输出 environment_content 保留为可能被模型观察的版本，而不是把可见版本收窄为单一键值。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 3（索引 2） / `transform`；依据 `source`，位置 `src_003`。
  理由：从环境内容中选出明确字段 FAST_KEY，保持原值。

> read FAST_KEY from the environment

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制流分派由运行 Skill 的 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：无数据来源、去向或转换，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流分派，无适用效果。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：判断 FAST_KEY 是否存在的动作由运行 Skill 的 agent runtime 执行。

> If FAST_KEY is present

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：根据 FAST_KEY 计算存在性布尔值，处理并改变表示，属于转换角色。

> If FAST_KEY is present

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文说明检查 FAST_KEY 是否存在；未规定本地隔离或模型处理，按默认模式。

> If FAST_KEY is present

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：计算 FAST_KEY 存在性，属于计算/转换效果。

> If FAST_KEY is present

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：分支分派由运行 Skill 的 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：分派仅控制流向，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流分派，无适用效果。

> dispatch

### ir_007

- `operator` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：IR 操作码为 fast.fetch，实际抓取动作由该工具执行，工具是参与执行者。

> fast.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：fast.fetch 返回响应内容，为当前流程引入外部数据，属 source。

> try fast.fetch first with source_id and FAST_KEY

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：调用时把 source_id 与 FAST_KEY 作为参数交给 fast.fetch 工具，使内容到达工具这一接收边界，属 sink。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文规定首次调用 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式保留可能的后续模型可见性。

> try fast.fetch first with source_id and FAST_KEY

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：控制流分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制流分派。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：分类与字段选取由运行 Skill 的 agent runtime 执行。

> On either tool's success, return that successful response's body value unchanged

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对工具响应进行分类并选出 body 字段，处理内容表示，属于转换角色。

> On either tool's success, return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文说明对成功响应分类并返回 body 原值；未规定本地隔离或模型处理，按默认模式。

> On either tool's success, return that successful response's body value unchanged

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：需要根据响应计算成功/失败分类，属于转换效果。

> first attempt fails with a transient error

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制流分派。

> dispatch

### ir_011

- `operator` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：重试同样由 fast.fetch 工具执行。

> fast.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：重试返回响应内容，引入外部数据，属 source。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：重试再次把 source_id 与 FAST_KEY 交给 fast.fetch，属 sink。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文规定条件重试 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制流分派。

> dispatch

### ir_013

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：重试响应的分类由 agent runtime 执行。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对重试响应分类并选出 body，属转换。

> On either tool's success, return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文说明重试后仍需判断结果；未规定本地隔离或模型处理，按默认模式。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：需要分类并选取字段，属转换效果。

> On either tool's success, return that successful response's body value unchanged

### ir_014

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制流分派。

> dispatch

### ir_015

- `operator` / `tool`；依据 `cfg`，位置 `g_0051`。
  理由：archive.fetch 工具执行回退抓取。

> archive.fetch

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：返回响应，引入外部数据，属 source。

> call archive.fetch with source_id

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把 source_id 作为唯一参数交给 archive.fetch，属 sink；FAST_KEY 未被传入。

> Call archive.fetch at most once and pass source_id as its only argument.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文规定调用 archive.fetch；未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。

> call archive.fetch with source_id

### ir_016

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制流分派。

> dispatch

### ir_017

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：对 archive.fetch 响应分类并选取字段由 agent runtime 执行。

> If archive.fetch fails, stop and return its error; do not retry archive.fetch.

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：分类并选出 body/error，属转换。

> On either tool's success, return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文说明对 archive.fetch 结果区分成功与失败并返回 body 或 error；未规定本地隔离，按默认模式。

> If archive.fetch fails, stop and return its error; do not retry archive.fetch.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：根据响应判断成功/失败并提取字段，属转换效果。

> If archive.fetch fails

### ir_018

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：分派由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制流分派。

> dispatch

### ir_019

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：追加状态到本地文件由运行 Skill 的 agent runtime 执行。

> Before returning from every success or failure path, append the final status to local status.txt.

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把最终状态写入 status.txt，使内容到达存储位置，属 sink。

> Before returning from every success or failure path, append the final status to local status.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地文件追加内容，符合 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt.

### ir_020

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：返回指令由 agent runtime 执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：普通内部返回，未规定用户输出或存储/接收边界，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：普通返回不是必然的用户输出，也无其他词表效果；按 EM06 不推断 user_output。

> ordinary return does not prove user-facing output

### ir_021

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：重试成功路径的追加由 agent runtime 执行。

> Before returning from every success or failure path, append the final status to local status.txt.

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把重试最终状态写入 status.txt，属 sink。

> Before returning from every success or failure path, append the final status to local status.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写入本地文件，符合 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt.

### ir_022

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0070`。
  理由：返回指令由 agent runtime 执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0070`。
  理由：普通内部返回，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：普通返回不是必然的用户输出，也无其他词表效果。

> ordinary return does not prove user-facing output

### ir_023

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 成功路径的追加由 agent runtime 执行。

> Before returning from every success or failure path, append the final status to local status.txt.

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把 archive.fetch 成功状态写入 status.txt，属 sink。

> Before returning from every success or failure path, append the final status to local status.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写入本地文件，符合 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt.

### ir_024

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0076`。
  理由：返回指令由 agent runtime 执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0076`。
  理由：普通内部返回，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：普通返回不是必然的用户输出，也无其他词表效果。

> ordinary return does not prove user-facing output

### ir_025

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：archive.fetch 失败路径的追加由 agent runtime 执行。

> Before returning from every success or failure path, append the final status to local status.txt.

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把 archive.fetch 失败状态写入 status.txt，属 sink。

> Before returning from every success or failure path, append the final status to local status.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写入本地文件，符合 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt.

### ir_026

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0082`。
  理由：返回指令由 agent runtime 执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0082`。
  理由：普通内部返回，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：普通返回不是必然的用户输出，也无其他词表效果。

> ordinary return does not prove user-facing output

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
