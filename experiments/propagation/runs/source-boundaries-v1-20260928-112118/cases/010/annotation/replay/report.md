# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime, llm | source | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Extract request.term and optional from_date and limit

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_query_term | agent_runtime | transformer | 1. transform |
| ir_004 | extract_optional_from_date | agent_runtime | transformer | 1. transform |
| ir_005 | extract_optional_limit | agent_runtime | transformer | 1. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Call index.search once with the request term and optional arguments

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | agent_runtime, tool, llm | source, sink | 1. model_observe |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Write the response total to count.txt and return the response items

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_response_total | agent_runtime | transformer | 1. transform |
| ir_010 | write_count_file | agent_runtime | sink | 1. fs_write |
| ir_011 | extract_response_items | agent_runtime | transformer | 1. transform |
| ir_012 | return | agent_runtime | sink | 1. user_output |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `L_request_json`：`storage` / `request.json`。
- 位置 `L_model_context`：`model_context` / `agent_model_context`。
- 位置 `L_index_search`：`tool` / `index.search`。
- 位置 `L_count_txt`：`storage` / `count.txt`。
- 位置 `L_user`：`user` / `requesting_user`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "L_request_json", "output": "ir_001_request_contents"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "ir_001_request_contents"}], "target": "L_model_context"}`
- output[0] ← `{"kind": "local", "name": "ir_001_request_contents"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["term"], "output": "ir_003_term"}`
- output[0] ← `{"kind": "local", "name": "ir_003_term"}`

### ir_004 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["from_date"], "output": "ir_004_from_date_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "ir_004_from_date_present"}`
- output[0] ← `{"kind": "local", "name": "ir_004_from_date_value"}`
- output[1] ← `{"kind": "local", "name": "ir_004_from_date_present"}`

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["limit"], "output": "ir_005_limit_value"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "ir_005_limit_present"}`
- output[0] ← `{"kind": "local", "name": "ir_005_limit_value"}`
- output[1] ← `{"kind": "local", "name": "ir_005_limit_present"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：无匹配效果的保守计算。
  - 操作 0：`{"op": "receive", "location": "L_index_search", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}, {"kind": "input", "index": 3}, {"kind": "input", "index": 4}, {"kind": "input", "index": 5}], "output": "ir_007_search_response"}`
- 事件 1：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "ir_007_search_response"}], "target": "L_model_context"}`
- output[0] ← `{"kind": "local", "name": "ir_007_search_response"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["total"], "output": "ir_009_total"}`
- output[0] ← `{"kind": "local", "name": "ir_009_total"}`

### ir_010 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "L_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_011 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["items"], "output": "ir_011_items"}`
- output[0] ← `{"kind": "local", "name": "ir_011_items"}`

### ir_012 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "L_user"}`

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该指令由本地代理运行时执行文件读取。

> read_request_json

- `operator` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：读取的 request.json 用于自然语言处理，模型参与观察该内容。

> content enters model processing

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：该操作从外部文件引入请求数据到当前流程。

> Read the user-supplied request.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：指令读取 request.json 文件内容。

> read_request_json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`，位置 `EM03`。
  理由：读取内容用于自然语言工作流，按执行模型进入模型处理上下文，位置在文件读取之后、字段选择之前。

> content enters model processing

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是本地控制流跳转，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：该指令无输入输出内容，不充当 source、sink 或 transformer。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流跳转不属于本词汇表效果。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地运行时执行字段提取。

> extract_query_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从容器中选择 term 字段，属于处理或转换内容。

> extract_query_term

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择 term 字段改变内容表示或选择结果。

> extract_query_term

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：本地运行时执行可选字段提取。

> extract_optional_from_date

- `roles` / `transformer`；依据 `cfg`，位置 `g_0016`。
  理由：选择可选 from_date 并计算存在性，属于处理内容。

> extract_optional_from_date

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0016`。
  理由：选择可选字段并计算存在性，改变内容表示。

> extract_optional_from_date

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0017`。
  理由：本地运行时执行可选字段提取。

> extract_optional_limit

- `roles` / `transformer`；依据 `cfg`，位置 `g_0017`。
  理由：选择可选 limit 并计算存在性，属于处理内容。

> extract_optional_limit

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0017`。
  理由：选择可选字段并计算存在性，改变内容表示。

> extract_optional_limit

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0018`。
  理由：dispatch 是本地控制流跳转，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：该指令无输入输出内容，不充当 source、sink 或 transformer。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制流跳转不属于本词汇表效果。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_008`。
  理由：工作流要求执行该调用，代理运行时发起调用。

> Call index.search exactly once

- `operator` / `tool`；依据 `cfg`，位置 `g_0023`。
  理由：该外部资源作为工具执行搜索。

> index.search

- `operator` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容进入 LLM 上下文，模型参与观察。

> enters the LLM context by default

- `roles` / `source`；依据 `cfg`，位置 `g_0023`。
  理由：该调用获取搜索响应，引入新内容到当前流程。

> index.search response

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：查询参数被传到 index.search 工具边界，形成 sink。

> using request.term unchanged as its query argument

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：搜索响应作为工具返回内容进入模型处理上下文，位置在工具接收之后。

> enters the LLM context by default

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0024`。
  理由：dispatch 是本地控制流跳转，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：该指令无输入输出内容，不充当 source、sink 或 transformer。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制流跳转不属于本词汇表效果。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：本地运行时提取响应中的 total。

> extract_response_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0029`。
  理由：从搜索响应中选择 total 字段，属于处理内容。

> extract_response_total

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0029`。
  理由：选择 total 字段并改变内容表示。

> extract_response_total

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0030`。
  理由：本地运行时执行文件写入。

> write_count_file

- `roles` / `sink`；依据 `source`，位置 `src_013`。
  理由：内容写入文件存储，形成 sink。

> write the response's total value to local count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_013`。
  理由：创建或修改 count.txt 文件内容。

> write the response's total value to local count.txt

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0031`。
  理由：本地运行时提取响应中的 items。

> extract_response_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0031`。
  理由：从搜索响应中选择 items 字段，属于处理内容。

> extract_response_items

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0031`。
  理由：选择 items 字段并改变内容表示。

> extract_response_items

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0032`。
  理由：代理运行时执行最终返回。

> return

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：将 items 提供给用户或调用方，形成输出边界。

> Return the search response's items value unchanged.

- `effects` / 步骤 1（索引 0） / `user_output`；依据 `source`，位置 `src_014`。
  理由：最终返回 items，结合用户提供请求的场景，视为向用户直接提供内容。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
