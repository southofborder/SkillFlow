# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v2`；摘要：`12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "60e0b51a739a6e70bdcfe68eb5653cde61fac4b6b49dde41231be1c620d688fc",
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
      "request_body_sha256": "968ad62efbe5f65172c8c37916df0c2916a977473821cbd5a4d3de8f0c1dd113"
    }
  ],
  "transport": "http"
}
```

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Extract request.term and optional from_date and limit

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_query_term | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_004 | extract_optional_from_date | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_005 | extract_optional_limit | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Call index.search once with the request term and optional arguments

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | agent_runtime, tool | source, sink | 1. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Write the response total to count.txt and return the response items

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_response_total | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_010 | write_count_file | agent_runtime | sink | 1. fs_write |
| ir_011 | extract_response_items | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_012 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)

- 位置 `loc_request_json`：`storage` / `request.json`。
- 位置 `loc_count_txt`：`storage` / `count.txt`。
- 位置 `loc_index_search`：`tool` / `index.search`。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_request_json", "output": "request_data"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "request_data"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "request_data"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["term"], "output": "query_term"}`
- output[0] ← `{"kind": "local", "name": "query_term"}`

### ir_004 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["from_date"], "output": "from_date_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "from_date_present"}`
- output[0] ← `{"kind": "local", "name": "from_date_value"}`
- output[1] ← `{"kind": "local", "name": "from_date_present"}`

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["limit"], "output": "limit_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "limit_present"}`
- output[0] ← `{"kind": "local", "name": "limit_value"}`
- output[1] ← `{"kind": "local", "name": "limit_present"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：无安全标签的数据关系。
  - 操作 0：`{"op": "receive", "location": "loc_index_search", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}, {"kind": "input", "index": 4}], "output": "search_response"}`
- 事件 1：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "search_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "search_response"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["total"], "output": "response_total"}`
- output[0] ← `{"kind": "local", "name": "response_total"}`

### ir_010 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_011 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["items"], "output": "response_items"}`
- output[0] ← `{"kind": "local", "name": "response_items"}`

### ir_012 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：CFG 以读取类 opcode 表示该步骤；源文未指定 LLM、工具或人工执行者，读取 request.json 由本地 agent runtime 执行。

> read_request_json

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：该读取把 request.json 的内容带入当前流程，是数据引入点，故为 source。

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：该指令读取外部资源 request.json 并把文件内容作为首个输出，符合读取文件内容的 fs_read。

> read_request_json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文没有写明本地隔离执行及受限回传机制，也没有针对该文件读取的接口说明，因此不能按 local 处理；按决策顺序使用 default。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM03`。
  理由：该读取为后续代理处理获取内容，源文未规定隔离或受限路由，故保留所得版本可能被模型观察的默认可能，而非声称已经发生观察。

> no explicit isolation or restricted routing

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转不属于效果词汇表任何类别，该指令也没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：字段提取由本地运行时执行；源文未提及 LLM、工具或人工参与。

> extract_query_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：该指令对请求数据做字段选择处理，属于对内容的加工，故为 transformer。

> extract_query_term

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：该字段选择没有本地隔离或限定回传的接口证据，按契约使用 default；选择结果按默认模式可能被后续处理观察到。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_008`。
  理由：从请求数据中选出已有 term 值并保持不变，符合 transform 的选择语义。

> using request.term unchanged as its query argument

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：可选字段取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。

> extract_optional_from_date

- `roles` / `transformer`；依据 `cfg`，位置 `g_0016`。
  理由：该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。

> extract_optional_from_date

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：源文要求存在时原样传值，本指令据此提取已有 from_date 字段值并派生存在性判断，符合 transform。

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0017`。
  理由：可选 limit 取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。

> extract_optional_limit

- `roles` / `transformer`；依据 `cfg`，位置 `g_0017`。
  理由：该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。

> extract_optional_limit

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：源文要求存在时原样传值，本指令据此提取已有 limit 字段值并派生存在性判断，符合 transform。

> When limit is present, pass its value unchanged as the limit argument.

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0018`。
  理由：该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_008`。
  理由：工作流由本地 agent runtime 执行，并据此发起这次调用。

> Call index.search exactly once

- `operator` / `tool`；依据 `cfg`，位置 `g_0023`。
  理由：CFG 把 index.search 作为被调用的外部资源，实际执行检索的工具参与该动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0023`。
  理由：该调用把检索响应作为新内容引入当前流程，充当 source。

> index.search response

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：请求参数被交给 index.search 这一接收边界，内容到达接收方，充当 sink。

> using request.term unchanged as its query argument

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：该段获取检索响应；源文未规定隔离或受限路由，按 default 其获取结果可能在获取后进入模型可见范围。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM02`。
  理由：工具返回内容默认可能进入下一次模型请求；源文没有提供内容路由或隔离机制来限制它，因此使用 default 而不选 local。

> content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0024`。
  理由：该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：从检索响应中取出 total 由本地运行时执行；无 LLM、工具或人工执行者证据。

> extract_response_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0029`。
  理由：该指令对响应内容做字段选择处理，属于内容加工。

> extract_response_total

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：该取值没有本地隔离或限定回传的接口证据，按决策顺序使用 default。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_013`。
  理由：源文明确要处理的是响应中已有 total 值，本指令只是把它取出，符合 transform 的选择语义。

> the response's total value

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0030`。
  理由：写本地文件由运行时执行；源文未指定 LLM、工具或人工执行者。

> write_count_file

- `roles` / `sink`；依据 `source`，位置 `src_013`。
  理由：total 值被写入储存位置 count.txt，内容到达存储边界，充当 sink。

> write the response's total value to local count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_013`。
  理由：该指令把 total 值写入本地文件 count.txt，创建/修改文件内容，符合 fs_write；写入本身不自动构成 transform。

> write the response's total value to local count.txt

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0031`。
  理由：从响应中取出 items 由本地运行时执行；无 LLM、工具或人工执行者证据。

> extract_response_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0031`。
  理由：该指令对响应内容做字段选择处理，属于内容加工。

> extract_response_items

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：该字段选择没有本地隔离或限定回传的接口证据，使用 default。

> Local mode requires explicit source or code/interface evidence and an explicit returns list

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_014`。
  理由：源文明确 items 是响应中已有字段且原样返回，本指令只是选出该字段，符合 transform 的选择语义。

> Return the search response's items value unchanged.

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0032`。
  理由：返回动作由本地运行时执行；源文未提及 LLM、工具或人工执行者。

> return

- `roles` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：该指令只是把 items 原样交回调用方，源文未指明接收方或可见性边界，普通返回不证明面向用户的输出，因此没有已证据化的角色标签。

> ordinary return does not prove user-facing output

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：依据同一规则，交回已有值不构成 user_output，也不属于其他效果类别；其未变更的值转发关系在 transfer_specs 中按输入操作数保留。

> ordinary return does not prove user-facing output

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
