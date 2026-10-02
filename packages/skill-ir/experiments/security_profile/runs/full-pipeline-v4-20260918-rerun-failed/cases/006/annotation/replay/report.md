# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`11e9fd59d162ba7ec62248faec3ff2a7ed7b4ccb02e72a331f07783c8d254d79`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_file | tool, llm | source | fs_read, model_observe |
| ir_002 | dispatch | llm, agent_runtime | [] | [] |

### block_002 · Select event records that meet the notification condition

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | filter_eligible_event_records | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm, agent_runtime | [] | [] |

### block_003 · Send notify.send for selected records

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | build_notification_requests | agent_runtime | transformer | transform |
| ir_006 | notify.send | tool | sink | net_send |
| ir_007 | dispatch | llm, agent_runtime | [] | [] |

### block_004 · Write the processed count to local count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | count_records | agent_runtime | transformer | transform |
| ir_009 | write_file | tool | sink | fs_write |
| ir_010 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：IR 的 opcode 为 read_file，表示由文件读取工具执行该动作。

> read_file

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：read_file 输出 event_records，未声明本地隔离或模型不可见，按 EM02 默认进入 LLM 上下文，因此 LLM 参与观察该结果。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：该动作从外部资源 events.json 读取事件记录并引入当前流程，起 source 作用。

> events.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 直接表示读取文件内容。

> read_file

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果未标记为本地隔离，按 EM02 默认进入模型上下文，产生 model_observe。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制转移动作，LLM 可参与选择下一块；该规则同时说明调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是本地控制流分派动作，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分派不向过程引入、变换或外送内容，无 source/sink/transformer 适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度不证明内容进入模型上下文；该 IR 也未记录文件、网络、用户输出或变换效果，故无匹配 effects。

> 仅选择或发起动作不足以标注 model_observe

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地筛选语义操作，未指定外部工具或模型处理，按代理运行时执行条件选择。

> filter_eligible_event_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：根据字段条件筛选记录，改变记录集合的选择结果，起 transformer 作用。

> filter_eligible_event_records

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：按该规则，本地字段筛选属于 transform；本动作正是按 opted_out/urgent/value 条件筛选记录。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制转移动作，LLM 可参与选择下一块；该规则同时说明调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是本地控制流分派动作，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分派不向过程引入、变换或外送内容，无 source/sink/transformer 适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度不证明内容进入模型上下文；该 IR 也未记录文件、网络、用户输出或变换效果，故无匹配 effects。

> 仅选择或发起动作不足以标注 model_observe

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为本地构造通知请求操作，由代理运行时执行组合。

> build_notification_requests

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：从选中记录构造通知请求对象，改变数据表示，起 transformer 作用。

> build_notification_requests

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：构造/组合请求对象属于计算、选择与改变表示，符合 transform。

> build_notification_requests

### ir_006

- `actor` / `tool`；依据 `cfg`，位置 `g_0022`。
  理由：该 IR 调用 notify.send 工具，发送动作由该工具执行。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该动作使内容发送到接收对象，到达可见边界，起 sink 作用。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / `net_send`；依据 `source`，位置 `src_003`。
  理由：明确以 recipient 为接收对象调用 notify.send 发送通知，构成向接收方发送内容的 net_send；不是仅凭工具名称。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_007

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度控制转移动作，LLM 可参与选择下一块；该规则同时说明调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0023`。
  理由：dispatch 是本地控制流分派动作，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0023`。
  理由：纯控制分派不向过程引入、变换或外送内容，无 source/sink/transformer 适用标签。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度不证明内容进入模型上下文；该 IR 也未记录文件、网络、用户输出或变换效果，故无匹配 effects。

> 仅选择或发起动作不足以标注 model_observe

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：该 IR 为本地计数操作，由代理运行时执行。

> count_records

- `roles` / `transformer`；依据 `cfg`，位置 `g_0028`。
  理由：统计选中记录数量，改变数据表示，起 transformer 作用。

> count_records

- `effects` / `transform`；依据 `cfg`，位置 `g_0028`。
  理由：计数属于计算/选择/组合，产生 processed_count，符合 transform。

> count_records

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0029`。
  理由：该 IR 调用 write_file 工具，写入动作由文件写入工具执行。

> write_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0029`。
  理由：将处理条数写入本地 count.txt，使内容到达存储位置，起 sink 作用。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0029`。
  理由：opcode 直接表示创建/修改文件内容，产生 fs_write。

> write_file

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0030`。
  理由：return 是控制流返回/结束动作，由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0030`。
  理由：返回动作不引入、变换或外送内容，无 source/sink/transformer 适用标签。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 仅为控制返回，不能据此标 user_output；图也未记录读写、网络、模型上下文或变换效果，故无匹配 effects。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
