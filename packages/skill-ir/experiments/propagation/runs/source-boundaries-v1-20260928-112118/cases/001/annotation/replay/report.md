# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · 读取用户提供的 events.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_file | agent_runtime | source, sink | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · 根据 opted_out、urgent 和 value 条件选中记录

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | select_notifiable_events | agent_runtime | transformer | 1. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · 对每条选中记录调用 notify.send

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | notify.send | tool | sink | 1. net_send |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · 统计已处理条数

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | count_processed_records | agent_runtime | transformer | 1. transform |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · 将处理条数写入本地 count.txt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | write_file | agent_runtime | sink | 1. fs_write |
| ir_010 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `loc_events_json`：`storage` / `用户提供的 events.json`。
- 位置 `loc_model_context`：`model_context` / `agent_llm_context`。
- 位置 `loc_notify_recipient`：`remote` / `symbolic:notify.send.recipient`。
- 位置 `loc_count_file`：`storage` / `count.txt`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "v_ir001_events"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "v_ir001_events"}], "target": "loc_model_context"}`
- output[0] ← `{"kind": "local", "name": "v_ir001_events"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "v_ir003_selected"}`
- output[0] ← `{"kind": "local", "name": "v_ir003_selected"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 1}], "dependencies": ["derived"], "output": "v_ir005_summary_values"}`
  - 操作 1：`{"op": "deliver", "inputs": [{"kind": "local", "name": "v_ir005_summary_values"}], "target": "loc_notify_recipient"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "v_ir007_count"}`
- output[0] ← `{"kind": "local", "name": "v_ir007_count"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_file", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_010 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：IR 中 read_file 由本地代理运行时执行文件读取，未见具名外部工具作为执行者。

> read_file

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该动作将用户提供的 events.json 内容引入当前流程，故为 source。

> 读取用户提供的 events.json

- `roles` / `sink`；依据 `execution_model`，位置 `EM03`。
  理由：读取结果按固定模型进入模型处理，使内容到达模型可见性边界，故该指令同时承担 sink 角色。

> For content acquired for the agent's natural-language processing, assume that content enters model processing unless an explicit local-only, model-invisible, or isolation boundary says otherwise.

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `source`，位置 `src_003`。
  理由：指令读取外部文件 events.json 内容，故第一效果为 fs_read。

> 读取用户提供的 events.json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`，位置 `EM03`。
  理由：事件记录用于后续自然语言条件处理，读取后进入模型处理，故在 fs_read 后记录 model_observe。

> For content acquired for the agent's natural-language processing, assume that content enters model processing unless an explicit local-only, model-invisible, or isolation boundary says otherwise.

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是控制流调度，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：该指令仅调度控制流，不引入、转换或交付内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制调度未产生词汇表中的读取、写入、网络、模型观察、用户输出或转换效果。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该指令对内部结果执行本地条件筛选，未见外部工具或模型执行证据，故由代理运行时执行。

> select_notifiable_events

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该动作根据字段条件筛选记录，处理并改变记录集合，故为 transformer。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `transform`；依据 `source`，位置 `src_003`。
  理由：按 opted_out、urgent、value 条件从事件记录中选择子集，属于选择/转换。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是控制流调度，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：该指令仅调度控制流，不引入、转换或交付内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制调度未产生词汇表中的读取、写入、网络、模型观察、用户输出或转换效果。

> dispatch

### ir_005

- `operator` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：IR 中具名通知发送工具 notify.send 执行发送动作，故 operator 为 tool。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该动作将内容发送给外部接收对象，使内容到达接收者/远程边界，故为 sink。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：指令实际调用 notify.send 并向接收对象发送选中记录的 summary 原值，构成 net_send。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是控制流调度，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：该指令仅调度控制流，不引入、转换或交付内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制调度未产生词汇表中的读取、写入、网络、模型观察、用户输出或转换效果。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该指令对内部选中记录执行本地计数，由代理运行时执行。

> count_processed_records

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：统计处理条数，将记录集合转换为计数，故为 transformer。

> 处理条数

- `effects` / 步骤 1（索引 0） / `transform`；依据 `source`，位置 `src_003`。
  理由：统计选中记录数量得到 processed_count，属于计算/转换。

> 处理条数

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是控制流调度，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：该指令仅调度控制流，不引入、转换或交付内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制调度未产生词汇表中的读取、写入、网络、模型观察、用户输出或转换效果。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地运行时执行将计数写入文件。

> write_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：内容写入本地文件存储位置 count.txt，故为 sink。

> 将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：指令创建/改写本地 count.txt 文件内容，故为 fs_write。

> 将处理条数写入本地 count.txt。

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：return 是控制返回，由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制返回不引入、转换或交付内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：return 未产生词汇表中的内容效果。

> return

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
