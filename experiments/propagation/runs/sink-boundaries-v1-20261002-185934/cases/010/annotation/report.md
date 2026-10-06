# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v4`；摘要：`1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [Sink 边界](sink-boundaries.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "8a609fbacba8255bce989bdf6cc674bc770d5e91d0f87faf7bc1f74d578b1dc1",
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
      "request_body_sha256": "f376553784775d7212c6e27e2f330c8a7ff31bb49f743b877daa98a948040711"
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
| ir_003 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_004 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_005 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_007 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_007 / 1 / 1 | loc_index_search · tool / index.search | external_tool | 2 | recipient / None | — |
| ir_007 / 2 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_010 / 0 / 0 | loc_count_txt · storage / count.txt | storage_write | 1 | task / persistent | — |
| ir_011 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |

任务内部且任务期限内的流动仍保留在传播说明中，等级 0 不进入 Sink 清单；删除绑定不交付旧内容。未进入清单不等于已证明没有数据风险。

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_002 · Extract request.term and optional from_date and limit

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_query_term | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_004 | extract_optional_from_date | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_005 | extract_optional_limit | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_003 · Call index.search once with the request term and optional arguments

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | agent_runtime, tool | source, sink, transformer | 1. model_observe<br>2. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_004 · Write the response total to count.txt and return the response items

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_response_total | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_010 | write_count_file | agent_runtime | sink | 1. fs_write |
| ir_011 | extract_response_items | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_012 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)

- 位置 `loc_request_json`：`storage` / `request.json`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_index_search`：`tool` / `index.search`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_count_txt`：`storage` / `count.txt`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_request_json", "output": "request_json_contents"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "request_json_contents"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "request_json_contents"}`

### ir_002 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["term"], "output": "query_term"}`
- output[0] ← `{"kind": "local", "name": "query_term"}`

### ir_004 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["from_date"], "output": "from_date_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "from_date_present"}`
- output[0] ← `{"kind": "local", "name": "from_date_value"}`
- output[1] ← `{"kind": "local", "name": "from_date_present"}`

### ir_005 · 事件与公开结果

次序：`fixed`；编译因果约束：2 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["limit"], "output": "limit_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "limit_present"}`
- output[0] ← `{"kind": "local", "name": "limit_value"}`
- output[1] ← `{"kind": "local", "name": "limit_present"}`

### ir_006 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

次序：`fixed`；编译因果约束：4 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 2}, {"kind": "input", "index": 3}, {"kind": "input", "index": 4}, {"kind": "input", "index": 5}], "target": "__compiled_model_context__"}`
- 事件 1：无安全标签的数据关系。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 2}, {"kind": "input", "index": 3}, {"kind": "input", "index": 4}, {"kind": "input", "index": 5}], "dependencies": ["possible", "possible", "possible", "possible"], "output": "optional_search_args"}`
  - 操作 1：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "local", "name": "optional_search_args"}], "target": "loc_index_search"}`
  - 操作 2：`{"op": "receive", "location": "loc_index_search", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}, {"kind": "input", "index": 3}, {"kind": "input", "index": 4}, {"kind": "input", "index": 5}], "output": "search_response"}`
- 事件 2：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "search_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "search_response"}`

### ir_008 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["total"], "output": "response_total"}`
- output[0] ← `{"kind": "local", "name": "response_total"}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_011 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["items"], "output": "response_items"}`
- output[0] ← `{"kind": "local", "name": "response_items"}`

### ir_012 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_007`。
  理由：源文指示工作流读取 request.json，该动作由 agent runtime 执行。

> Read the user-supplied request.json

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：读取操作将 request.json 内容引入当前流程，作为数据源。

> Read the user-supplied request.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：CFG 操作码表明读取外部文件内容，对应 fs_read。

> read_request_json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未声明模型处理或本地隔离边界，按 EM10 默认模式处理，读取输出按契约可能被模型观察。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该指令为控制流分发，由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_008`。
  理由：提取 query term 是工作流中由 agent runtime 执行的步骤。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `roles` / `transformer`；依据 `source`，位置 `src_007`。
  理由：从请求容器中选出 term 字段，属于处理内容。

> which contains term

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文只规定字段选择关系，未声明模型处理或本地隔离，按 default 模式。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_008`。
  理由：字段选择/提取是 transform 效果，且保持原值。

> using request.term unchanged as its query argument.

### ir_004

- `operator` / `agent_runtime`；依据 `source`，位置 `src_009`。
  理由：提取可选 from_date 参数由 agent runtime 执行。

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

- `roles` / `transformer`；依据 `source`，位置 `src_007`。
  理由：从请求中提取可选字段并判断存在性，属于处理内容。

> may contain from_date and limit

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未声明模型处理或本地隔离边界，按 default 模式。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：字段提取及存在性判断是 transform 效果。

> When from_date is present, pass its value unchanged;

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_009`。
  理由：提取可选 limit 参数由 agent runtime 执行。

> When limit is present, pass its value unchanged as the limit argument.

- `roles` / `transformer`；依据 `source`，位置 `src_007`。
  理由：从请求中提取可选字段并判断存在性，属于处理内容。

> may contain from_date and limit

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未声明模型处理或本地隔离边界，按 default 模式。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：字段提取及存在性判断是 transform 效果。

> When limit is present, pass its value unchanged as the limit argument.

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0018`。
  理由：该指令为控制流分发，由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_008`。
  理由：工作流指令由 agent runtime 发起对工具的调用。

> Call index.search exactly once

- `operator` / `tool`；依据 `cfg`，位置 `g_0023`。
  理由：CFG 操作码表明工具 index.search 执行搜索动作。

> index.search

- `roles` / `source`；依据 `source`，位置 `src_013`。
  理由：工具返回搜索响应，将内容引入当前流程，作为 source。

> After the search, write the response's total value

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：请求参数被交付到 index.search 工具边界，作为 sink。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `roles` / `transformer`；依据 `source`，位置 `src_006`。
  理由：该能力说明 index.search 对查询进行匹配处理，作为 transformer。

> index.search supports fuzzy matching

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0024`。
  理由：该指令为控制流分发，由 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_013`。
  理由：提取响应 total 由 agent runtime 执行。

> After the search, write the response's total value

- `roles` / `transformer`；依据 `source`，位置 `src_013`。
  理由：从响应中选出 total 字段，属于处理内容。

> write the response's total value

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未声明模型处理或本地隔离边界，按 default 模式。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_013`。
  理由：字段选择是 transform 效果。

> write the response's total value

### ir_010

- `operator` / `agent_runtime`；依据 `source`，位置 `src_013`。
  理由：工作流指令由 agent runtime 执行写文件。

> write the response's total value to local count.txt.

- `roles` / `sink`；依据 `source`，位置 `src_013`。
  理由：将内容写入本地文件存储，作为 sink。

> write the response's total value to local count.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_013`。
  理由：创建或修改文件内容，对应 fs_write。

> write the response's total value to local count.txt.

### ir_011

- `operator` / `agent_runtime`；依据 `source`，位置 `src_014`。
  理由：提取响应 items 由 agent runtime 执行。

> Return the search response's items value unchanged.

- `roles` / `transformer`；依据 `source`，位置 `src_014`。
  理由：从响应中选出 items 字段，属于处理内容。

> Return the search response's items value unchanged.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未声明模型处理或本地隔离边界，按 default 模式。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_014`。
  理由：字段选择是 transform 效果。

> Return the search response's items value unchanged.

### ir_012

- `operator` / `agent_runtime`；依据 `source`，位置 `src_014`。
  理由：普通返回由 agent runtime 执行。

> Return the search response's items value unchanged.

- `roles` / `空数组说明`；依据 `source`，位置 `src_014`。
  理由：普通返回不引入新源、不写入存储、不执行变换，无适用角色。

> Return the search response's items value unchanged.

- `effects` / `空数组说明`；依据 `source`，位置 `src_014`。
  理由：普通返回不是用户输出或网络发送，且没有适用的效果词汇；按 REP02 事件和绑定可为空。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
