# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`a8698c8666a34110b4cdf88ca4191c2a9228fe39fb3fed37066d3f12b560c056`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool | source | fs_read, model_observe |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Get next event record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | get_next_event_record | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Extract fields and evaluate notification condition

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_notification_fields | agent_runtime | transformer | transform |
| ir_006 | evaluate_notification_condition | agent_runtime | transformer | transform |
| ir_007 | dispatch | agent_runtime | [] | [] |

### block_004 · Send notification for selected event

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | notify.send | tool | sink | net_send |
| ir_009 | dispatch | agent_runtime | [] | [] |

### block_005 · Finish processing

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 读取外部资源，按工具动作执行，工具为执行者。

> read_events_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：输入类型为外部资源，动作向当前过程引入数据。

> external_resource

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：源文要求读取用户提供的内容，对应读取文件内容效果。

> 读取用户提供的

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具执行返回内容默认进入模型上下文，支持模型观察效果。

> 默认进入 LLM 上下文

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：控制流分发由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分发，不引入、发送或变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地迭代取记录由代理运行时执行。

> get_next_event_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从已有记录集合中选择下一条，属于变换角色。

> get_next_event_record

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择下一条记录是本地选择/变换操作。

> get_next_event_record

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制流分发由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分发，不引入、发送或变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表效应。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地字段提取由代理运行时执行。

> extract_notification_fields

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：提取/选择字段属于变换。

> extract_notification_fields

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：字段提取是本地处理变换。

> extract_notification_fields

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：本地条件求值由代理运行时执行。

> evaluate_notification_condition

- `roles` / `transformer`；依据 `cfg`，位置 `g_0022`。
  理由：比较字段值并作出选择，属于变换。

> evaluate_notification_condition

- `effects` / `transform`；依据 `cfg`，位置 `g_0022`。
  理由：条件求值是计算/选择操作。

> evaluate_notification_condition

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0023`。
  理由：控制流分发由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0023`。
  理由：纯控制分发，不引入、发送或变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0023`。
  理由：纯控制操作，无词表效应。

> dispatch

### ir_008

- `actor` / `tool`；依据 `cfg`，位置 `g_0028`。
  理由：该 IR 为 notify.send 工具调用，工具是执行者。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：动作使通知内容到达接收对象，形成 sink 角色。

> 接收对象

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：源文描述发送通知给接收对象，构成向远端发送的效果。

> 发送通知

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0029`。
  理由：控制流分发由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制分发，不引入、发送或变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制操作，无词表效应。

> dispatch

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：流程返回由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回控制，不引入、发送或变换内容，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通返回无用户输出等效果依据；IR 无输入，无其他效应。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
