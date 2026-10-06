# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`41ef3caac05eae36e48aa57467e606ebc76ebe32de5252f67578ce6c85504681`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool | source | fs_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Iterate to next event record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | get_next_event | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Extract event fields for selection and notification

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_event_fields | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Select event records matching subscription and urgency/value rules

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | check_event_selection | agent_runtime | transformer | transform |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Send notification for selected event

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | notify.send | tool | sink | net_send |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Count processed event records

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | count_processed_records | agent_runtime | transformer | transform |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Write processed count to local count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_count_txt | tool | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为读取外部资源 events.json 的工具动作。

> read_events_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部资源将事件记录引入当前过程。

> events.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取 events.json 文件内容。

> read_events_json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：读取工具的输出事件记录默认回传模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地迭代操作由代理运行时执行。

> get_next_event

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从记录集合选择当前记录，承担变换角色。

> current_event

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择下一条记录属于计算/选择/改变表示。

> get_next_event

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地字段提取操作由代理运行时执行。

> extract_event_fields

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：提取/选择字段属于内容变换。

> extract_event_fields

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：字段提取是计算/选择/改变表示。

> extract_event_fields

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地条件判断与筛选由代理运行时执行。

> check_event_selection

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：筛选记录属于内容变换。

> check_event_selection

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：条件筛选是选择/计算操作。

> check_event_selection

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：调用通知服务工具执行发送。

> notify.send

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：发送使内容到达外部接收对象，承担 sink 角色。

> 接收对象取该记录的 recipient 字段

- `effects` / `net_send`；依据 `cfg`，位置 `g_0033`。
  理由：输入为外部通知服务，动作向其发送内容。

> notification service

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地计数操作由代理运行时执行。

> count_processed_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0039`。
  理由：计算处理条数，承担变换角色。

> processed_count

- `effects` / `transform`；依据 `cfg`，位置 `g_0039`。
  理由：计数属于计算/组合操作。

> count_processed_records

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：规则承认 LLM 可参与调度，本 IR 为 dispatch 控制流。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 为控制流，不引入、变换或送出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0045`。
  理由：本地文件写入工具执行写入。

> write_count_txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：写入本地文件，使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：创建/写入 count.txt 文件内容。

> write_count_txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：返回/结束控制流由代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯返回操作，无数据角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 不表明用户输出，也无其他词表效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
