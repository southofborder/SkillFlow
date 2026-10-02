# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`6d204e82c960e8d2c1f3d8a977d5b00b24bb200f467431e7ce5f892fdca38b17`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Select records that are not opted out and are urgent or high value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | filter_event_records | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read body_from from payload.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_payload_config | agent_runtime | source | fs_read |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Send notify.send once for each selected record

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | notify_send_selected_records | tool | sink | net_send |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Write the processed count to local count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | write_processed_count_to_count_txt | agent_runtime | sink | fs_write |
| ir_010 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为读取外部文件的本地操作，由本地代理运行时执行。

> read_events_json

- `roles` / `source`；依据 `source`，位置 `src_006`。
  理由：该动作把外部事件数据引入当前流程，充当 source。

> 读取用户提供的 events.json

- `effects` / `fs_read`；依据 `source`，位置 `src_006`。
  理由：读取 events.json 文件内容，产生 fs_read 效果。

> 读取用户提供的 events.json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为控制调度，LLM 可参与选择或发起下一步。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入数据、不使内容到达接收方或存储、也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地字段筛选计算，由代理运行时执行。

> filter_event_records

- `roles` / `transformer`；依据 `source`，位置 `src_007`。
  理由：按条件筛选记录属于处理或选择内容，充当 transformer。

> 筛选

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：本地字段筛选是选择或变换操作，产生 transform 效果。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为控制调度，LLM 可参与选择或发起下一步。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不引入数据、不使内容到达接收方或存储、也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为读取本地配置文件，由代理运行时执行。

> read_payload_config

- `roles` / `source`；依据 `source`，位置 `src_010`。
  理由：读取 payload.json 的配置值并引入流程，充当 source。

> 按该字段直接取值

- `effects` / `fs_read`；依据 `source`，位置 `src_010`。
  理由：动作读取 payload.json 文件内容，产生 fs_read 效果。

> 正文配置同时由 [发送配置](../payload.json) 的 body_from 字段声明

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为控制调度，LLM 可参与选择或发起下一步。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移，不引入数据、不使内容到达接收方或存储、也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：IR 指定由 notify.send 工具执行发送动作，故 actor 为 tool。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：该动作使内容发送给接收对象，充当 sink。

> 接收对象取该记录的 recipient 字段

- `effects` / `net_send`；依据 `source`，位置 `src_008`。
  理由：调用发送工具并指定接收对象，属于向远端发送内容。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为控制调度，LLM 可参与选择或发起下一步。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移，不引入数据、不使内容到达接收方或存储、也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 为本地写文件操作，由代理运行时执行。

> write_processed_count_to_count_txt

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：动作使内容到达本地存储位置，充当 sink。

> 将处理条数写入本地 count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_014`。
  理由：写入 count.txt 文件内容，产生 fs_write 效果。

> 写入本地 count.txt

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：该 IR 为流程返回控制，由本地代理运行时结束执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制返回，不引入数据、不使内容到达接收方或存储、也不变换内容，无适用角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：该指令无输入输出，纯控制返回，不产生词表效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
