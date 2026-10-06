# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`836d34ef584eff7f9543661958c2d23614132db613fbaccf077fac57f7e50c56`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

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
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "l_ir001_event_records"}`
- output[0] ← `{"kind": "local", "name": "l_ir001_event_records"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "l_ir003_current_record"}`
  - 操作 1：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "l_ir003_has_more"}`
- output[0] ← `{"kind": "local", "name": "l_ir003_current_record"}`
- output[1] ← `{"kind": "local", "name": "l_ir003_has_more"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "l_ir005_is_selected"}`
- output[0] ← `{"kind": "local", "name": "l_ir005_is_selected"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["recipient"], "output": "l_ir007_recipient"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["summary"], "output": "l_ir007_summary"}`
- output[0] ← `{"kind": "local", "name": "l_ir007_recipient"}`
- output[1] ← `{"kind": "local", "name": "l_ir007_summary"}`

### ir_008 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "loc_notify_send"}`

### ir_009 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_010 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "l_ir010_processed_count"}`
- output[0] ← `{"kind": "local", "name": "l_ir010_processed_count"}`

### ir_011 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_012 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 表示由本地 agent runtime 执行的文件读取操作，未出现具名工具。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取动作把外部文件内容引入当前流程，作为数据来源。

> 读取用户提供的 events.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `source`，位置 `src_003`。
  理由：读取外部文件内容，符合 fs_read；没有证据表明读取结果进入模型上下文或远程通信。

> 读取用户提供的 events.json

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是控制流分派，由本地 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分派，不引入、发送或变换数据内容，因此 roles 无适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：控制分派本身不产生词汇表中的效果；分派或调度也不推断模型观察。

> merely selecting or initiating an action is insufficient for model_observe

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该指令在本地流程中获取下一条记录，由 agent runtime 执行。

> get_next_event_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从事件记录集合中选择下一条并计算是否还有记录，处理或改变数据表示。

> get_next_event_record

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择下一条记录并计算 has_more_records，属于选择或计算型 transform。

> get_next_event_record

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是控制流分派，由本地 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分派，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：控制分派本身无词汇表效果；不因调度推断模型观察。

> merely selecting or initiating an action is insufficient for model_observe

### ir_005

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该条件评估操作在本地 agent runtime 中执行，未出现具名工具或模型内容处理证据。

> evaluate_event_record_selection

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：根据记录字段进行条件判断，处理或改变数据以产生选择结果。

> 选中该记录

- `effects` / 步骤 1（索引 0） / `transform`；依据 `source`，位置 `src_003`。
  理由：评估条件并计算 is_selected，属于计算或选择型 transform。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是控制流分派，由本地 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分派，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：控制分派本身无词汇表效果；不因调度推断模型观察。

> merely selecting or initiating an action is insufficient for model_observe

### ir_007

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该字段提取操作在本地 agent runtime 中执行，未出现具名工具。

> extract_event_notification_fields

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：从记录中选择字段，改变数据表示，属于处理或变换。

> 接收对象取该记录的 recipient 字段

- `effects` / 步骤 1（索引 0） / `transform`；依据 `source`，位置 `src_003`。
  理由：提取 recipient 和 summary 字段，保留原值但改变表示，属于 transform；源约束排除摘要生成或内容改写。

> notify.send 的 body 参数直接取该记录的 summary 字段原值

### ir_008

- `operator` / `tool`；依据 `cfg`，位置 `g_0028`。
  理由：IR 调用外部资源 notify.send，具名工具执行通知发送动作。

> notify_send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该动作使 recipient 与 summary 内容到达 notify.send 的远程接收边界，属于 sink。

> 对每条选中记录调用一次 notify.send

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：调用 notify.send 将 recipient 作为接收对象参数发送到远程通知边界。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 1（索引 0） / `net_send`；依据 `source`，位置 `src_003`。
  理由：summary 原值作为 body 参数随 notify.send 发送，支持 net_send 的内容参数。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：dispatch 是控制流分派，由本地 agent runtime 执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制分派，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：控制分派本身无词汇表效果；不因调度推断模型观察。

> merely selecting or initiating an action is insufficient for model_observe

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：计数操作在本地 agent runtime 中执行，未出现具名工具。

> count_processed_event_records

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：计算处理条数，属于处理或计算数据。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `transform`；依据 `cfg`，位置 `g_0034`。
  理由：对事件记录进行计数得到 processed_count，属于计算型 transform。

> count_processed_event_records

### ir_011

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0035`。
  理由：本地文件写入由 agent runtime 执行，未出现具名工具。

> write_count_to_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：将内容写入本地文件存储位置，属于 sink。

> 写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：创建或修改本地 count.txt 文件内容，符合 fs_write；文件写入不自动添加 context_write。

> 处理完成后，将处理条数写入本地 count.txt。

### ir_012

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0036`。
  理由：return 是控制返回，由本地 agent runtime 执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0036`。
  理由：普通返回无数据角色；未显示向用户或存储提供内容。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通返回不证明 user_output，也无其他词汇表效果证据；控制返回本身不在效果词汇表中。

> an ordinary return alone does not prove user-facing output

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
