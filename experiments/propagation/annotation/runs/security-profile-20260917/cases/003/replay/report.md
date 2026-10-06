# 安全语义标注：003

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`d47ccb19e8554f234a4f3a4c26e28d9b533723c15a592bb438d534066419ecd8`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · 读取 events.json 事件记录

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool | source | fs_read, model_observe |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · 按订阅状态、紧急标记和数值选择记录

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | select_eligible_event_records | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · 提取选中记录的接收对象和摘要原值

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_notification_recipient_and_body | agent_runtime | transformer | transform |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · 对每条选中记录调用 notify.send

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | notify.send | tool | sink | net_send |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · 统计已处理条数

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | count_selected_records | agent_runtime | transformer | transform |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · 将处理条数写入本地 count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | write_count_to_file | tool | sink | fs_write |
| ir_012 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 读取外部资源 events.json，按工具动作执行。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该动作从外部读取事件记录，向当前流程引入数据。

> 读取用户提供的 events.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表示读取 events.json 文件内容。

> read_events_json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：该工具输出 events_records，按 EM02 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 为代理运行时执行的控制流跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 仅控制流转，不引入、变换或落地数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是纯控制操作，未记录词表内数据效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地筛选操作，由代理运行时执行。

> select_eligible_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：按条件筛选记录，处理并选择内容。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：根据条件选择记录，改变记录集合表示。

> select_eligible_event_records

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 为代理运行时执行的控制流跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 仅控制流转，不引入、变换或落地数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是纯控制操作，未记录词表内数据效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为本地字段提取操作，由代理运行时执行。

> extract_notification_recipient_and_body

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：选择并提取 recipient 与 summary 字段，处理内容。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：选择/组合字段值，改变数据表示。

> 接收对象取该记录的 recipient 字段。

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 为代理运行时执行的控制流跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 仅控制流转，不引入、变换或落地数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是纯控制操作，未记录词表内数据效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：IR 中记录具体工具名 notify.send，执行发送动作。

> notify.send

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：使内容到达接收对象，构成 sink 角色。

> 对每条选中记录调用一次 notify.send。

- `effects` / `net_send`；依据 `source`，位置 `src_003`。
  理由：向记录的 recipient 发送通知内容，属于向远端接收方发送。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 为代理运行时执行的控制流跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 仅控制流转，不引入、变换或落地数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是纯控制操作，未记录词表内数据效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 为本地计数操作，由代理运行时执行。

> count_selected_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：统计已选记录条数，处理内容得到计数。

> count_selected_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：计算/组合记录数量，改变表示。

> count_selected_records

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 为代理运行时执行的控制流跳转。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 仅控制流转，不引入、变换或落地数据，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是纯控制操作，未记录词表内数据效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：该 IR 写入外部资源 count.txt，按工具动作执行。

> write_count_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将内容写入本地文件存储位置，构成 sink 角色。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0039`。
  理由：opcode 表示创建/写入 count.txt 文件内容。

> write_count_to_file

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：return 为代理运行时的控制返回。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：return 仅结束流程，不引入、变换或落地数据。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：该指令为控制返回，无数据效果；EM06 也排除仅凭 return 推断用户输出。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
