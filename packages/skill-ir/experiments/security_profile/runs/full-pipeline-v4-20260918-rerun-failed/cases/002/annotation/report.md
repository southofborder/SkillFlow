# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`900e7b1665d4ddb3270499ce28034e505c93e464a23a17c72532a5931b4b2e96`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · 读取用户提供的 events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · 筛选需要通知的事件记录

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | select_eligible_event_records | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · 遍历选中的事件记录

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | get_next_selected_record | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · 发送 notify.send 通知

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_record_recipient | agent_runtime | transformer | transform |
| ir_008 | extract_record_summary | agent_runtime | transformer | transform |
| ir_009 | notify.send | tool | sink | net_send |
| ir_010 | dispatch | llm | [] | [] |

### block_005 · 统计处理条数并写入 count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | count_processed_records | agent_runtime | transformer | transform |
| ir_012 | write_processed_count | agent_runtime | sink | fs_write |
| ir_013 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该指令读取事件文件，由本地代理运行时执行文件读取。

> read_events_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从外部资源 events.json 引入事件记录数据，充当 source。

> events.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取文件内容，匹配 fs_read。

> read_events_json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度控制动作，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转不引入数据、不使内容到达接收方或存储、不处理内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表未覆盖为效果，故无匹配标签。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：按条件筛选记录属本地数据处理，由代理运行时执行。

> select_eligible_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：该动作筛选记录子集，改变数据集合，属 transformer。

> select_eligible_event_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：筛选/选择子集属计算或选择变换，匹配 transform。

> select_eligible_event_records

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度控制动作，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制跳转不引入数据、不使内容到达接收方或存储、不处理内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，词表未覆盖为效果，故无匹配标签。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：迭代取出下一条选中记录属本地运行时处理。

> get_next_selected_record

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：从已有记录集合中取出一条记录，属选择/变换。

> get_next_selected_record

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：选择下一条记录并输出，属选择变换。

> get_next_selected_record

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度控制动作，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制跳转不引入数据、不使内容到达接收方或存储、不处理内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，词表未覆盖为效果，故无匹配标签。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：字段提取属本地运行时处理。

> extract_record_recipient

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：从记录中提取 recipient 字段，属字段选择/变换。

> extract_record_recipient

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：提取字段并改变表示，匹配 transform。

> extract_record_recipient

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：字段提取属本地运行时处理。

> extract_record_summary

- `roles` / `transformer`；依据 `cfg`，位置 `g_0028`。
  理由：从记录中提取 summary 字段，属字段选择/变换。

> extract_record_summary

- `effects` / `transform`；依据 `cfg`，位置 `g_0028`。
  理由：提取字段并改变表示，匹配 transform。

> extract_record_summary

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0029`。
  理由：notify.send 为具体工具，执行通知发送动作。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_004`。
  理由：使内容到达 recipient 接收方，属 sink。

> 接收对象取该记录的 recipient 字段

- `effects` / `net_send`；依据 `source`，位置 `src_004`。
  理由：调用通知发送工具向接收对象发送内容，构成发送效果。

> 调用一次 notify.send，接收对象取该记录的 recipient 字段

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度控制动作，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0030`。
  理由：纯控制跳转不引入数据、不使内容到达接收方或存储、不处理内容，故无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0030`。
  理由：纯控制操作，词表未覆盖为效果，故无匹配标签。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0035`。
  理由：统计处理条数属本地计算处理。

> count_processed_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0035`。
  理由：对已有记录集合计数，属计算/变换。

> count_processed_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0035`。
  理由：计数属计算变换，匹配 transform。

> count_processed_records

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0036`。
  理由：写入本地文件由代理运行时执行。

> write_processed_count

- `roles` / `sink`；依据 `source`，位置 `src_007`。
  理由：内容到达本地存储位置 count.txt，属 sink。

> 将处理条数写入本地 count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0036`。
  理由：动作为写入文件内容，匹配 fs_write。

> write_processed_count

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0037`。
  理由：返回为流程控制，由本地代理运行时结束执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0037`。
  理由：纯返回不引入数据、不使内容到达边界、不处理内容，故无角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0037`。
  理由：普通 return 不是用户输出，亦无其他词表效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
