# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`761dbc57d1f21a39d32cdebebef08aefb1954c1924b1c13c368297c4071f7f66`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool | source | fs_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Get the next event record to process

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | next_event_record | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Extract notification fields from the current record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_event_record_fields | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Check whether the current record is selected for notification

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | check_notification_eligibility | agent_runtime | transformer | transform |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Send notification for the selected record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | notify.send | tool | sink | net_send |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Finish after all records are processed

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为读取外部资源 events.json 的动作，由工具执行。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取动作将文件数据引入当前过程，属于 source。

> 读取用户提供的 events.json

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：动作明确读取文件内容。

> 读取用户提供的 events.json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：按工具结果回传假设，读取工具返回内容默认进入模型上下文。

> 默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制调度，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表列出的数据效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地迭代选择下一条记录，由代理运行时执行。

> next_event_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从记录集合中选择并产出当前记录，属于内容处理。

> current_event_record

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：选择下一条记录属于计算/选择类变换。

> next_event_record

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 依据 has_more_records 调度，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分支，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为本地字段提取，由代理运行时执行。

> extract_event_record_fields

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：提取记录字段并改变表示，属于内容处理。

> record_summary

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：本地字段提取按执行模型标注 transform。

> 本地字段筛选

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制调度，无角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该 IR 为本地条件判定，由代理运行时执行。

> check_notification_eligibility

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：根据字段和阈值计算选择结果，属于内容处理。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：检查条件并计算 should_notify，属于计算/选择变换。

> check_notification_eligibility

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 依据 should_notify 调度，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分支，无角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 为调用 notify.send 工具的动作，由工具执行。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：发送动作使内容到达指定接收对象，属于 sink。

> 接收对象取该记录的 recipient 字段

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：Skill 描述该流程发送通知，具备发送通信依据。

> 发送通知

- `effects` / `net_send`；依据 `source`，位置 `src_003`。
  理由：明确调用发送工具向接收对象传递内容。

> 调用一次 notify.send

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制调度，无角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：该 IR 为结束控制，由代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0039`。
  理由：纯结束控制，无 source/sink/transformer 角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：return 不自动产生 user_output，IR 无其他效果记录。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
