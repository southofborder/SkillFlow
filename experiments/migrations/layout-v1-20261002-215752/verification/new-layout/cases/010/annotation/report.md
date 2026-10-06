# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v5`；摘要：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

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
  "prompt_sha256": "c18777a08a39ea98eb8e6b06532b31636fe46ddfedb0ccbf0220d4940a11cb73",
  "observed": false,
  "requests": [],
  "transport": "injected"
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
| ir_007 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_007 / 2 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_007 / 4 / 0 | loc_index_search · tool / index.search | external_tool | 2 | recipient / None | — |
| ir_007 / 6 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
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
| ir_007 | index.search | agent_runtime, tool | source, sink, transformer | 1. model_observe<br>2. model_observe<br>3. model_observe<br>4. transform<br>5. model_observe |
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
  - 操作 0：`{"op": "read", "location": "loc_request_json", "output": "request_content"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "request_content"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "request_content"}`

### ir_002 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["term"], "output": "term"}`
- output[0] ← `{"kind": "local", "name": "term"}`

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

次序：`fixed`；编译因果约束：7 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 3}, {"kind": "input", "index": 5}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 2}], "target": "__compiled_model_context__", "when": {"kind": "input", "index": 3}}`
- 事件 2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 4}], "target": "__compiled_model_context__", "when": {"kind": "input", "index": 5}}`
- 事件 3：效果索引 3。
  - 操作 0：`{"op": "build", "parts": [{"path": ["query"], "value": {"kind": "input", "index": 1}, "when": null}, {"path": ["from_date"], "value": {"kind": "input", "index": 2}, "when": {"kind": "input", "index": 3}}, {"path": ["limit"], "value": {"kind": "input", "index": 4}, "when": {"kind": "input", "index": 5}}], "output": "request", "container": "object"}`
- 事件 4：无安全标签的数据关系。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "request"}], "target": "loc_index_search"}`
- 事件 5：无安全标签的数据关系。
  - 操作 0：`{"op": "receive", "location": "loc_index_search", "inputs": [{"kind": "local", "name": "request"}], "output": "response"}`
- 事件 6：效果索引 4。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "response"}`

### ir_008 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["total"], "output": "total"}`
- output[0] ← `{"kind": "local", "name": "total"}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_011 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["items"], "output": "items"}`
- output[0] ← `{"kind": "local", "name": "items"}`

### ir_012 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_007`。
  理由：该工作流指令要求读取用户提供的文件，由本地 agent_runtime 执行；未指定模型或工具参与读取。

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：读取将 request.json 内容引入当前流程，属于 source 角色。

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `source`，位置 `src_007`。
  理由：该指令读取文件 request.json 内容，符合 fs_read。

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，按默认模式分析读取输出。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_007`。
  理由：源文只要求读取文件，未说明本地或模型处理边界。

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该控制转移指令由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制转移，不引入、到达或处理内容，roles 无适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该字段提取指令由 agent_runtime 执行。

> extract_query_term

- `roles` / `transformer`；依据 `source`，位置 `src_008`。
  理由：选择并保留 request.term 字段，处理内容，属于 transformer。

> using request.term unchanged as its query argument

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，字段提取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_008`。
  理由：该指令从输入容器选择显式 term 字段并保持原值，属于 transform。

> using request.term unchanged as its query argument

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：该可选字段提取与存在性判断指令由 agent_runtime 执行。

> extract_optional_from_date

- `roles` / `transformer`；依据 `source`，位置 `src_009`。
  理由：提取可选值并计算其存在性，处理内容，属于 transformer。

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：提取可选 from_date 原值并计算存在性，属于 transform。

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0017`。
  理由：该可选字段提取与存在性判断指令由 agent_runtime 执行。

> extract_optional_limit

- `roles` / `transformer`；依据 `source`，位置 `src_009`。
  理由：提取可选 limit 值并计算其存在性，处理内容，属于 transformer。

> When limit is present, pass its value unchanged as the limit argument.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_009`。
  理由：提取可选 limit 原值并计算存在性，属于 transform。

> When limit is present, pass its value unchanged as the limit argument.

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0018`。
  理由：该控制转移指令由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：仅控制转移，不引入、到达或处理内容，roles 无适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_008`。
  理由：工作流运行时构造并调度该调用；未指定 LLM 参与。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `operator` / `tool`；依据 `cfg`，位置 `g_0023`。
  理由：CFG 将 index.search 标为外部资源操作码，实际搜索动作由该工具执行。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0023`。
  理由：调用返回搜索响应，将结果引入当前流程，属于 source。

> index.search response

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：实际参数被送到 index.search 工具边界，内容到达该边界，属于 sink。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `roles` / `transformer`；依据 `source`，位置 `src_008`。
  理由：该 IR 组合 query 与可选参数构造请求，属于 transformer。

> using request.term unchanged as its query argument

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_008`。
  理由：源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_008`。
  理由：源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 3（索引 2） / `model_observe`；依据 `source`，位置 `src_008`。
  理由：源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。

> Call index.search exactly once, using request.term unchanged as its query argument.

- `effects` / 步骤 4（索引 3） / `transform`；依据 `source`，位置 `src_009`。
  理由：将 term 及可选 from_date/limit 组合为调用参数对象，属于组合/表示转换；网络传输未建立，获取响应用 null-effect 事件表示。

> When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.

- `effects` / 步骤 5（索引 4） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 5（索引 4） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 5（索引 4） / `model_observe`；依据 `source`，位置 `src_008`。
  理由：源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。

> Call index.search exactly once, using request.term unchanged as its query argument.

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0024`。
  理由：该控制转移指令由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：仅控制转移，不引入、到达或处理内容，roles 无适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：该响应字段提取指令由 agent_runtime 执行。

> extract_response_total

- `roles` / `transformer`；依据 `source`，位置 `src_013`。
  理由：从搜索响应中选出 total 字段，处理内容，属于 transformer。

> After the search, write the response's total value to local count.txt.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_013`。
  理由：选择响应 total 原值，属于 transform。

> After the search, write the response's total value to local count.txt.

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0030`。
  理由：该文件写入指令由 agent_runtime 执行。

> write_count_file

- `roles` / `sink`；依据 `source`，位置 `src_013`。
  理由：将 total 写入本地 count.txt 存储位置，内容到达该位置，属于 sink。

> After the search, write the response's total value to local count.txt.

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_013`。
  理由：写入文件 count.txt，符合 fs_write。

> After the search, write the response's total value to local count.txt.

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0031`。
  理由：该响应字段提取指令由 agent_runtime 执行。

> extract_response_items

- `roles` / `transformer`；依据 `source`，位置 `src_014`。
  理由：选择响应 items 字段，处理内容，属于 transformer。

> Return the search response's items value unchanged.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_014`。
  理由：选择 items 原值，属于 transform。

> Return the search response's items value unchanged.

### ir_012

- `operator` / `agent_runtime`；依据 `source`，位置 `src_014`。
  理由：该普通 return 由 agent_runtime 执行。

> Return the search response's items value unchanged.

- `roles` / `空数组说明`；依据 `source`，位置 `src_014`。
  理由：普通 return 仅标识返回输入，不建立用户输出、网络交付或调用方位置，roles 无适用标签。

> Return the search response's items value unchanged.

- `effects` / `空数组说明`；依据 `source`，位置 `src_014`。
  理由：普通返回不一定是用户输出，也未建立其他词汇内 effect；空 effects 不表示无返回。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
