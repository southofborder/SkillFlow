# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`929e959551310c9df3c4a2811da45bcc9775cc29c8a0cf8518731acead40fa33`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool, llm | source | fs_read, model_observe |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Get the next event record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | get_next_event_record | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Evaluate notification selection for the current record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | evaluate_notification_selection | agent_runtime | transformer | transform |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Send notify.send for the selected record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | read_recipient_field | agent_runtime | transformer | transform |
| ir_008 | read_summary_field | agent_runtime | transformer | transform |
| ir_009 | notify.send | tool | sink | net_send |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_005 · Write processed count to count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | count_processed_event_records | agent_runtime | transformer | transform |
| ir_012 | write_processed_count_to_file | tool | sink | fs_write |
| ir_013 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该IR读取外部资源 events.json，按工具执行读取动作。

> read_events_json

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：读取工具结果默认回传模型上下文，LLM作为接收/后续处理参与方。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从外部资源引入数据到当前流程，属于 source 角色。

> 读取用户提供的 events.json

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：明确读取 events.json 文件内容。

> 读取用户提供的 events.json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果默认进入模型处理上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 为控制流转动作，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流转不引入、不送出、不转换数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流转，词表效果均不适用。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该IR从已有记录集合中取下一记录并产出状态，属于本地运行时迭代操作。

> get_next_event_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从集合中选择当前记录并计算是否有下一条，属于处理/选择内容。

> get_next_event_record

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：迭代选择与状态计算属于 transform。

> get_next_event_record

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 为控制流转动作，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流转不引入、不送出、不转换数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流转，词表效果均不适用。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该IR执行条件筛选，按本地运行时逻辑处理。

> evaluate_notification_selection

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：根据条件选择记录，属于处理/选择内容。

> evaluate_notification_selection

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：本地条件筛选属于 transform；未证明模型实际读取处理，故不标注 model_observe。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 为控制流转动作，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流转不引入、不送出、不转换数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流转，词表效果均不适用。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：从当前记录中提取字段，属于本地运行时数据访问。

> read_recipient_field

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：选择/提取 recipient 字段，属于处理内容表示。

> read_recipient_field

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：字段选择/提取属于 transform。

> read_recipient_field

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：从当前记录中提取字段，属于本地运行时数据访问。

> read_summary_field

- `roles` / `transformer`；依据 `cfg`，位置 `g_0028`。
  理由：选择/提取 summary 字段，属于处理内容表示。

> read_summary_field

- `effects` / `transform`；依据 `cfg`，位置 `g_0028`。
  理由：字段选择/提取属于 transform。

> read_summary_field

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0029`。
  理由：该IR调用 notify.send 工具执行发送。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_004`。
  理由：使通知内容到达接收对象，属于 sink 角色。

> 对每条选中记录调用一次 notify.send

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：源描述明确发送通知，IR向 recipient 发送通知体，支持 net_send；不标注 net_receive。

> 发送通知

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0030`。
  理由：dispatch 为控制流转动作，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0030`。
  理由：纯控制流转不引入、不送出、不转换数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0030`。
  理由：纯控制流转，词表效果均不适用。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0035`。
  理由：对已有记录集合计数，属于本地运行时计算。

> count_processed_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0035`。
  理由：计算处理条数，改变/组合表示，属于 transformer。

> count_processed_event_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0035`。
  理由：计数/计算属于 transform。

> count_processed_event_records

### ir_012

- `actor` / `tool`；依据 `cfg`，位置 `g_0036`。
  理由：该IR写入本地文件 count.txt，按文件写入工具执行。

> write_processed_count_to_file

- `roles` / `sink`；依据 `source`，位置 `src_007`。
  理由：将内容写入存储位置，属于 sink 角色。

> 将处理条数写入本地 count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_007`。
  理由：创建/修改本地 count.txt 文件内容。

> 将处理条数写入本地 count.txt

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0037`。
  理由：return 为控制返回动作，由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0037`。
  理由：普通返回不引入、不送出、不转换数据，无 source/sink/transformer 角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 不能证明 user_output，且无其他效果依据。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
