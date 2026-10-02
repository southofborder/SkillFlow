# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`49d22c84f47e95f338d448674c38b5ebdb1a30b8c1ad4bfff98ad17bc2a811b6`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | tool | source | fs_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Select records meeting opted_out, urgent, and value conditions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | select_notifiable_event_records | tool | transformer | transform, model_observe |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Extract notify.send parameters from selected records

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_notification_parameters | tool | transformer | transform, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Send one notify.send call for each selected record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | notify.send | tool | sink | net_send |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Count the selected records that were processed

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | count_processed_event_records | tool | transformer | transform, model_observe |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Write the processed count to local count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | write_count_file | tool | sink | fs_write |
| ir_012 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 命名读取事件文件的动作，由执行该动作的工具执行。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该动作从外部文件引入事件记录数据到当前流程。

> 读取用户提供的 events.json

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：读取 events.json 文件内容，属于文件读取。

> 读取用户提供的 events.json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：该工具动作有输出事件记录且未标为本地不可见，默认回传进入模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制动作，EM03 说明 LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯调度控制，不向当前过程引入数据，不使内容到达接收方或存储位置，也不变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：opcode 命名筛选动作，由执行该动作的工具执行。

> select_notifiable_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：按条件筛选记录，处理并改变记录集合。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：条件筛选和选择记录属于 transform。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：该工具动作有输出选中的事件记录且未标为本地不可见，默认回传进入模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制动作，EM03 说明 LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯调度控制，不向当前过程引入数据，不使内容到达接收方或存储位置，也不变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：opcode 命名提取参数动作，由执行该动作的工具执行。

> extract_notification_parameters

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：从记录中提取和选择字段值，处理并改变表示。

> 接收对象取该记录的 recipient 字段。

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：字段提取和选择属于 transform。

> 接收对象取该记录的 recipient 字段。

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：该工具动作有输出接收对象列表和 body 原值列表且未标为本地不可见，默认回传进入模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制动作，EM03 说明 LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯调度控制，不向当前过程引入数据，不使内容到达接收方或存储位置，也不变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：opcode 命名通知发送工具，由该工具执行发送动作。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：使通知内容到达 recipient 接收对象和可见边界。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / `net_send`；依据 `source`，位置 `src_003`。
  理由：调用 notify.send 向 recipient 发送通知，存在通信依据。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制动作，EM03 说明 LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯调度控制，不向当前过程引入数据，不使内容到达接收方或存储位置，也不变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：opcode 命名计数动作，由执行该动作的工具执行。

> count_processed_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：对选中记录计数，处理并改变表示。

> count_processed_event_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：计数计算属于 transform。

> count_processed_event_records

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：该工具动作有输出处理条数且未标为本地不可见，默认回传进入模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制动作，EM03 说明 LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯调度控制，不向当前过程引入数据，不使内容到达接收方或存储位置，也不变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：opcode 命名写入计数文件动作，由执行该动作的工具执行。

> write_count_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：使处理条数内容到达本地存储位置。

> 将处理条数写入本地 count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：写入本地 count.txt 文件内容，属于文件写入。

> 将处理条数写入本地 count.txt

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：return 是控制流返回，由本地代理运行时处理。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制返回，不引入、变换或送达数据。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制返回，无读取、写入、网络、模型观察、用户输出或变换效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
