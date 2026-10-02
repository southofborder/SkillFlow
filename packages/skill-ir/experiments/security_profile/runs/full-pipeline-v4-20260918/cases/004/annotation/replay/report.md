# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`2607ff59d03557a3f205469b642669d7a5595e74e5cfa0240add754c3df31906`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_file | tool | source | fs_read, model_observe |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Select event records eligible for notification

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | filter_notifiable_events | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Read body_from configuration from payload.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_payload_body_from | tool | source, transformer | fs_read, transform, model_observe |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Get the next selected record to notify

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | get_next_selected_record | agent_runtime | [] | [] |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Send notification for the current selected record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_recipient_from_record | agent_runtime | transformer | transform |
| ir_010 | resolve_configured_body_value | agent_runtime | transformer | transform |
| ir_011 | notify.send | tool | sink | net_send |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_006 · Write processed record count to count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | count_processed_selected_records | agent_runtime | transformer | transform |
| ir_014 | write_count_file | tool | sink | fs_write |
| ir_015 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表示读取 events.json 的文件动作，由文件工具执行。

> read_events_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从外部资源 events.json 读取事件记录并引入当前流程。

> events.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取 events.json 文件内容。

> read_events_file

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具读取返回的事件记录默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：无工具或模型处理依据，调度转向由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转向，未引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表所列效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地筛选动作，无工具或模型处理依据，由运行时执行。

> filter_notifiable_events

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：按条件筛选记录，属于内容选择/变换。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：筛选选择符合条件的记录，标注变换效果。

> filter_notifiable_events

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：无工具或模型处理依据，调度转向由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转向，未引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表所列效果。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：opcode 表示读取 payload.json 字段，由文件/配置读取工具执行。

> read_payload_body_from

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：从外部配置 payload.json 引入 body_from 值。

> payload.json

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：按字段名提取配置值，属于选择/变换。

> body_from

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0021`。
  理由：读取 payload.json 文件内容。

> read_payload_body_from

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：选择并取值 body_from 字段，属于字段选择变换。

> body_from

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回的配置字段值默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：无工具或模型处理依据，调度转向由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转向，未引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表所列效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地迭代取记录，由运行时执行。

> get_next_selected_record

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0027`。
  理由：仅从已选列表取出下一条记录，属于控制/迭代，无引入、输出或变换内容。

> get_next_selected_record

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0027`。
  理由：纯控制/取项操作，未执行词表效果。

> get_next_selected_record

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：无工具或模型处理依据，调度转向由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转向，未引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表所列效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地字段提取，由运行时执行。

> extract_recipient_from_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：选择记录中的 recipient 字段，属于字段选择/变换。

> 接收对象取该记录的 recipient 字段。

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：提取字段值，标注变换效果。

> extract_recipient_from_record

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：本地按配置解析字段值，由运行时执行。

> resolve_configured_body_value

- `roles` / `transformer`；依据 `cfg`，位置 `g_0034`。
  理由：按配置选择记录字段值，属于选择/变换。

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

- `effects` / `transform`；依据 `cfg`，位置 `g_0034`。
  理由：解析并选择字段值，标注变换效果。

> resolve_configured_body_value

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0035`。
  理由：调用 notify.send 工具执行发送。

> notify.send

- `roles` / `sink`；依据 `cfg`，位置 `g_0035`。
  理由：内容到达外部接收对象，构成 sink。

> 接收对象取该记录的 recipient 字段

- `effects` / `net_send`；依据 `cfg`，位置 `g_0035`。
  理由：调用发送工具并指定接收对象，构成向远端发送请求/内容。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0036`。
  理由：无工具或模型处理依据，调度转向由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0036`。
  理由：纯控制转向，未引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0036`。
  理由：纯控制操作，无词表所列效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0041`。
  理由：本地计数，由运行时执行。

> count_processed_selected_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0041`。
  理由：计算已处理记录条数，属于计算/变换。

> count_processed_selected_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0041`。
  理由：计数计算，标注变换效果。

> count_processed_selected_records

### ir_014

- `actor` / `tool`；依据 `cfg`，位置 `g_0042`。
  理由：文件写入动作由文件工具执行。

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0042`。
  理由：内容到达本地存储位置 count.txt，构成 sink。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0042`。
  理由：创建/写入 count.txt 文件内容。

> write_count_file

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0043`。
  理由：返回控制由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0043`。
  理由：纯返回控制，无数据角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0043`。
  理由：普通 return 不必然面向用户输出，也无其他词表效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
