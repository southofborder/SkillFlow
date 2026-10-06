# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`836d34ef584eff7f9543661958c2d23614132db613fbaccf077fac57f7e50c56`

[四字段标注](profiles.json) · [位置声明](locations.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided events.json file

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | agent_runtime | source | 1. fs_read |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · Get the next event record

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | get_next_event_record | agent_runtime | transformer | 1. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · Evaluate whether the current record is selected for notification

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | evaluate_event_record_selection | agent_runtime | transformer | 1. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · Extract notification fields and send the selected record's notification

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_event_notification_fields | agent_runtime | transformer | 1. transform |
| ir_008 | notify_send | tool | sink | 1. net_send |
| ir_009 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · Write the number of processed records to count.txt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_010 | count_processed_event_records | agent_runtime | transformer | 1. transform |
| ir_011 | write_count_to_file | agent_runtime | sink | 1. fs_write |
| ir_012 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。

- 位置 `loc_events_json`：`storage` / `events.json`。
- 位置 `loc_count_txt`：`storage` / `count.txt`。
- 位置 `loc_notify_send`：`remote` / `notify.send`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "event_records"}`
- output[0] ← `{"kind": "local", "name": "event_records"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "current_record"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "has_more_records"}`
- output[0] ← `{"kind": "local", "name": "current_record"}`
- output[1] ← `{"kind": "local", "name": "has_more_records"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "is_selected"}`
- output[0] ← `{"kind": "local", "name": "is_selected"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["recipient"], "output": "recipient"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["summary"], "output": "summary"}`
- output[0] ← `{"kind": "local", "name": "recipient"}`
- output[1] ← `{"kind": "local", "name": "summary"}`

### ir_008 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_notify_send"}`

### ir_009 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_010 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "processed_count"}`
- output[0] ← `{"kind": "local", "name": "processed_count"}`

### ir_011 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_012 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该指令为本地文件读取动作，图中未显示外部工具或模型参与，按执行模型由 agent_runtime 执行。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该动作将外部文件内容引入当前处理流程，符合 source 角色。

> 读取用户提供的 events.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `source`，位置 `src_003`。
  理由：读取用户提供的 events.json 文件内容，属于 fs_read。

> 读取用户提供的 events.json

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：控制流分派由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流分派不引入、发送或变换内容，无适用 roles 标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流操作不产生本词汇表中的读取、写入、发送、接收、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地运行时执行记录迭代选择。

> get_next_event_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从事件记录集合中选择下一条记录并计算剩余标志，属于处理/变换。

> get_next_event_record

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择下一条事件记录并计算 has_more_records，属于 transform。

> get_next_event_record

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制流分派由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流分派不引入、发送或变换内容，无适用 roles 标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流操作不产生本词汇表中的读取、写入、发送、接收、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地运行时执行条件评估。

> evaluate_event_record_selection

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：根据字段条件计算选中状态，属于处理/变换。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：计算 is_selected 布尔结果，属于 transform。

> evaluate_event_record_selection

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：控制流分派由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流分派不引入、发送或变换内容，无适用 roles 标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流操作不产生本词汇表中的读取、写入、发送、接收、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地运行时执行字段提取。

> extract_event_notification_fields

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：从当前记录中提取 recipient 和 summary 字段，属于字段选择变换。

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：选择字段生成 recipient 和 summary，属于 transform。

> extract_event_notification_fields

### ir_008

- `operator` / `tool`；依据 `cfg`，位置 `g_0028`。
  理由：外部资源 notify.send 作为工具执行通知发送；该指令调用该工具。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将通知内容发送给 recipient 指定的接收对象，使内容到达外部接收边界，符合 sink 角色。

> 接收对象取该记录的 recipient 字段

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：调用 notify.send 发送通知请求，属于 net_send。

> 对每条选中记录调用一次 notify.send

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：控制流分派由 agent_runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制流分派不引入、发送或变换内容，无适用 roles 标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制流操作不产生本词汇表中的读取、写入、发送、接收、模型观察、用户输出或变换效果。

> dispatch

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：本地运行时执行计数计算。

> count_processed_event_records

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：统计处理条数，属于计算/变换。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0034`。
  理由：计算 processed_count，属于 transform。

> count_processed_event_records

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0035`。
  理由：本地运行时执行文件写入。

> write_count_to_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将处理条数写入本地文件，使内容到达存储位置，符合 sink 角色。

> 写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：写入本地 count.txt 文件内容，属于 fs_write。

> 将处理条数写入本地 count.txt

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0036`。
  理由：普通返回由运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0036`。
  理由：普通返回不引入、发送或变换内容，无适用 roles 标签。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0036`。
  理由：普通返回不是 user_output，也不产生本词汇表中其他效果。

> return

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
