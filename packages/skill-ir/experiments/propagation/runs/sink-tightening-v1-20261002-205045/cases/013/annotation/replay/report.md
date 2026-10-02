# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v5`；摘要：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [Sink 边界](sink-boundaries.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "5e7b5c181ec020c327ab871388086931fc536512327c29097ad897819c9bf7d3",
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
      "request_body_sha256": "c4f6a434a9387ee0dae06f0313599934a99e1b648d8fc7f9d0f9de836b8cf855"
    }
  ],
  "transport": "http"
}
```

没有记录执行问题；不等于模型标注已经人工确认。

## Sink 边界与固定等级

类型和等级由程序按位置属性和具体交付／写入操作生成；等级仅表达边界访问及留存，不表示敏感度、危险程度、任务必要性或 DOE 结论。标注阶段关联符号操作，传播后由同一操作关联实际数据版本。

| IR / 事件 / 操作 | 边界 | 类型 | 等级 | 访问范围 / 留存 | 作用域 |
|---|---|---|---|---|---|
| ir_001 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_003 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_005 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_007 / 0 / 0 | loc_fast_fetch_tool · tool / fast.fetch | external_tool | 2 | recipient / None | — |
| ir_007 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_011 / 0 / 0 | loc_fast_fetch_tool · tool / fast.fetch | external_tool | 2 | recipient / None | — |
| ir_011 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_013 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_015 / 0 / 0 | loc_archive_fetch_tool · tool / archive.fetch | external_tool | 2 | recipient / None | — |
| ir_015 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_017 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_019 / 0 / 0 | loc_status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_021 / 0 / 0 | loc_status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_023 / 0 / 0 | loc_status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_025 / 0 / 0 | loc_status_file · storage / status.txt | storage_write | 1 | task / persistent | — |

任务内部且任务期限内的流动仍保留在传播说明中，等级 0 不进入 Sink 清单；删除绑定不交付旧内容。未进入清单不等于已证明没有数据风险。

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
| ir_007 | fast.fetch | agent_runtime, tool | source, sink | 1. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_005 · Classify the first fast.fetch attempt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | classify_fast_fetch_outcome | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_010 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | fast.fetch | agent_runtime, tool | source, sink | 1. model_observe |
| ir_012 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_007 · Classify the fast.fetch retry

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | classify_fast_fetch_outcome | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_014 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_008 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | archive.fetch | agent_runtime, tool | source, sink | 1. model_observe |
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

- 位置 `loc_user_request`：`runtime_context` / `user_request`；访问范围 `task`，留存 `task`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_environment`：`runtime_context` / `environment`；访问范围 `task`，留存 `task`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_fast_fetch_tool`：`tool` / `fast.fetch`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_archive_fetch_tool`：`tool` / `archive.fetch`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_status_file`：`storage` / `status.txt`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：3 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_user_request", "output": "user_request_content"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "user_request_content"}], "target": "__compiled_model_context__"}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "user_request_content"}, "path": ["source_id"], "output": "source_id_value"}`
- output[0] ← `{"kind": "local", "name": "source_id_value"}`

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
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "environment_content"}, "path": ["FAST_KEY"], "output": "fast_key_value"}`
- output[0] ← `{"kind": "local", "name": "fast_key_value"}`

### ir_004 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_key_present_value"}`
- output[0] ← `{"kind": "local", "name": "fast_key_present_value"}`

### ir_006 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_fast_fetch_tool"}`
  - 操作 1：`{"op": "receive", "location": "loc_fast_fetch_tool", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_first_response"}`
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
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_first_outcome_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_first_body_value"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_outcome_value"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_first_body_value"}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_011 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_fast_fetch_tool"}`
  - 操作 1：`{"op": "receive", "location": "loc_fast_fetch_tool", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_retry_response"}`
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
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_fetch_retry_outcome_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_retry_body_value"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_outcome_value"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_retry_body_value"}`

### ir_014 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_015 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}], "target": "loc_archive_fetch_tool"}`
  - 操作 1：`{"op": "receive", "location": "loc_archive_fetch_tool", "inputs": [{"kind": "input", "index": 1}], "output": "archive_fetch_response"}`
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
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "archive_fetch_outcome_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "archive_fetch_body_value"}`
  - 操作 2：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["error"], "output": "archive_fetch_error_value"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_outcome_value"}`
- output[1] ← `{"kind": "local", "name": "archive_fetch_body_value"}`
- output[2] ← `{"kind": "local", "name": "archive_fetch_error_value"}`

### ir_018 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_019 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_020 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_021 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_022 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_023 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_024 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_025 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_026 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：该读取是 Skill 工作流中的运行时动作，由本地 agent 运行时执行；源文未提及模型或人工参与。

> Read source_id from the user's request

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该操作从用户请求引入 source_id 内容进入当前流程，符合 source 角色。

> Read source_id from the user's request

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `source`，位置 `src_003`。
  理由：从用户请求这一运行时上下文获取调用方输入，属于 context_read。

> Read source_id from the user's request

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只描述从用户请求读取 source_id，未规定模型处理或显式本地隔离与限定回传，按默认模式标注。

> Read source_id from the user's request

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM01`。
  理由：无显式接口限制读取或返回范围，保留请求整体作为可能获取范围。

> Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content

- `effects` / 步骤 3（索引 2） / `transform`；依据 `source`，位置 `src_003`。
  理由：目标字段是既有的 source_id，按字段原值选出，不发明新值。

> Read source_id from the user's request

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：控制跳转指令由 agent 运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转不引入、转换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：词汇表内无适用 effect；该指令只改变控制流，不产生内容效应。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：环境读取由工作流运行时执行。

> read FAST_KEY from the environment

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从环境上下文引入 FAST_KEY 值进入当前流程。

> read FAST_KEY from the environment

- `effects` / 步骤 1（索引 0） / `context_read`；依据 `source`，位置 `src_003`。
  理由：读取环境上下文属于 context_read。

> read FAST_KEY from the environment

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只描述从环境读取 FAST_KEY，未规定模型处理或本地隔离与限定回传，按默认模式标注。

> read FAST_KEY from the environment

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM01`。
  理由：无显式接口限制读取或返回范围，保留环境上下文整体作为可能获取范围。

> Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content

- `effects` / 步骤 3（索引 2） / `transform`；依据 `source`，位置 `src_003`。
  理由：目标值是环境中的 FAST_KEY，按原值选出。

> read FAST_KEY from the environment

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制跳转指令由 agent 运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制跳转不引入、转换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：词汇表内无适用 effect；该指令只改变控制流。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：存在性检查由运行时在工作流中执行。

> If FAST_KEY is present

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对 FAST_KEY 值做存在性判定并产生新的布尔状态，属于对内容的处理。

> If FAST_KEY is present

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：存在性判定没有模型处理或本地隔离证据，按默认模式标注。

> If FAST_KEY is present

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：缺少本地隔离机制证据，不能声明 local 模式；默认模式保留非隔离转换输入的可能观察。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：计算存在性布尔是对输入值的计算，属 transform。

> If FAST_KEY is present

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：依据存在性标志的控制分支由运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：分支跳转不改变内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分支无词汇表内 effect。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：运行时发起 fast.fetch 调用并传递实际参数。

> try fast.fetch first with source_id and FAST_KEY

- `operator` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：指令以 fast.fetch 为外部资源，由该工具执行抓取动作。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：该调用返回的响应内容进入当前流程，符合 source 角色。

> fast_fetch_first_response

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：source_id 与 FAST_KEY 作为参数被送达 fast.fetch 边界，内容可能到达外部接收方。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM02`。
  理由：工具返回内容默认可能进入后续模型请求；未见隔离或限定路由机制，按默认模式标注。

> content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM09`。
  理由：fast.fetch 是已知工具但无网络传输机制证据，响应按工具边界获取。

> known tool acquisition without established networking uses receive at a tool location in a null-effect event

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：控制跳转指令由 agent 运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制跳转不引入、转换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：词汇表内无适用 effect。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：对首次响应做结果分类由运行时执行，用于区分成功、瞬时失败与非瞬时失败。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对响应内容分类并选出 body 字段，属于对内容的处理。

> return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：对首次响应分类的处理没有模型或本地隔离证据，按默认模式标注。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：缺少本地隔离机制证据，不能声明 local 模式；默认模式保留响应版本的可能观察。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：分类响应结果的计算属 transform。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：依据分类结果的控制分支由运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：分支跳转不改变内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分支无词汇表内 effect。

> dispatch

### ir_011

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：运行时按约束发起一次重试调用并传递参数。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `operator` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：重试由 fast.fetch 工具执行。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：重试响应内容进入当前流程。

> fast_fetch_retry_response

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：重试仍以 source_id 与 FAST_KEY 为参数送达 fast.fetch 边界。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM02`。
  理由：重试返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。

> content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM09`。
  理由：fast.fetch 为已知工具但无网络传输机制证据，重试响应按工具边界获取。

> known tool acquisition without established networking uses receive at a tool location in a null-effect event

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：控制跳转指令由 agent 运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制跳转不引入、转换或送达内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：词汇表内无适用 effect。

> dispatch

### ir_013

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：对重试响应分类由运行时执行，用于判断成功或转入 archive.fetch 路径。

> After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对重试响应分类并选出 body 字段，属内容处理。

> return that successful response's body value unchanged

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：对重试响应分类的处理无模型或本地隔离证据，按默认模式标注。

> After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：缺少本地隔离机制证据，不能声明 local 模式。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：识别重试结果为瞬时或非瞬时需要计算响应输入，属 transform。

> Retry fast.fetch exactly once only when its first attempt fails with a transient error

### ir_014

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：依据重试分类结果的控制分支由运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：分支跳转不改变内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制分支无词汇表内 effect。

> dispatch

### ir_015

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：运行时发起 archive.fetch 调用。

> call archive.fetch with source_id

- `operator` / `tool`；依据 `cfg`，位置 `g_0051`。
  理由：由 archive.fetch 工具执行抓取。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0051`。
  理由：archive.fetch 的响应内容进入当前流程。

> archive_fetch_response

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：source_id 作为唯一实参送达 archive.fetch 边界。

> Call archive.fetch at most once and pass source_id as its only argument

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM02`。
  理由：工具返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。

> content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM09`。
  理由：archive.fetch 部署方式未说明且无网络传输证据，响应按工具边界获取。

> known tool acquisition without established networking uses receive at a tool location in a null-effect event

### ir_016

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：控制跳转指令由 agent 运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制跳转不引入、转换或送达内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：词汇表内无适用 effect。

> dispatch

### ir_017

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：运行时对 archive.fetch 响应做成功/失败分类并提取对应值。

> If archive.fetch fails, stop and return its error

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：对响应分类并区分 body/error 输出，属内容处理。

> If archive.fetch fails, stop and return its error

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：对响应分类与提取的处理没有模型或本地隔离证据，按默认模式标注。

> If archive.fetch fails, stop and return its error

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：缺少本地隔离机制证据，不能声明 local 模式。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：分类计算与字段选取属 transform；body 与 error 按原值选取。

> If archive.fetch fails, stop and return its error

### ir_018

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：依据 archive 分类结果的控制分支由运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：分支跳转不改变内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制分支无词汇表内 effect。

> dispatch

### ir_019

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加由运行时执行。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：状态内容写入本地存储位置，内容到达存储边界，符合 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：向本地文件追加内容属 fs_write；写入输入状态原值，未添加 transform。

> Before returning from every success or failure path, append the final status to local status.txt

### ir_020

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：普通返回由运行时执行。

> return that successful response's body value unchanged

- `roles` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回不引入、转换内容或使其到达接收/存储边界；源文未说明用户直接展示，无适用角色。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回不代表用户输出或网络送达，词汇表内无适用 effect；返回身份由 CFG 输入保留。

> return that successful response's body value unchanged

### ir_021

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加由运行时执行。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：状态内容写入本地存储位置，符合 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写文件属 fs_write；写入原值。

> Before returning from every success or failure path, append the final status to local status.txt

### ir_022

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：普通返回由运行时执行。

> return that successful response's body value unchanged

- `roles` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回未说明用户展示或外发，无适用角色。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回无词汇表内 effect；返回身份由 CFG 输入保留。

> return that successful response's body value unchanged

### ir_023

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加由运行时执行。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：状态内容写入本地存储位置，符合 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写文件属 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt

### ir_024

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：普通返回由运行时执行。

> return that successful response's body value unchanged

- `roles` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回未说明用户展示或外发，无适用角色。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：普通返回无词汇表内 effect。

> return that successful response's body value unchanged

### ir_025

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件追加由运行时执行。

> append the final status to local status.txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：状态内容写入本地存储位置，符合 sink。

> append the final status to local status.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加写文件属 fs_write。

> Before returning from every success or failure path, append the final status to local status.txt

### ir_026

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：失败路径的普通返回由运行时执行。

> If archive.fetch fails, stop and return its error

- `roles` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：停止并返回错误属普通返回，未见用户直接展示或外发，无适用角色。

> If archive.fetch fails, stop and return its error

- `effects` / `空数组说明`；依据 `source`，位置 `src_003`。
  理由：错误返回不产生词汇表内 effect；CFG 输入标识返回的错误值。

> If archive.fetch fails, stop and return its error

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
