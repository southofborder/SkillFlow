# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`0d056b6699347c199da8e08c3d7cb7d3939c0db87dd1f0c1f463c5f08c059858`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_013` / `effects`：普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。
- `ir_014` / `effects`：普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。
- `ir_015` / `effects`：普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。
- `ir_016` / `effects`：普通 return 是否直接面向用户输出无法由该 IR、源文或执行模型确定；除可能 user_output 外无其他已确定效果。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_request | agent_runtime | source | context_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | source | context_read |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_present | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | agent_runtime, tool | source, sink | net_send, net_receive, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Retry fast.fetch once after a transient first failure

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | fast.fetch | agent_runtime, tool | source, sink | net_send, net_receive, model_observe |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Call archive.fetch with source_id

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | archive.fetch | agent_runtime, tool | source, sink | net_send, net_receive, model_observe |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Return fast.fetch success body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | return | agent_runtime | sink | [] |

### block_008 · Return fast.fetch retry success body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | return | agent_runtime | sink | [] |

### block_009 · Return archive.fetch success body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | return | agent_runtime | sink | [] |

### block_010 · Return archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为本地从调用者上下文读取字段，由 agent_runtime 执行。

> read_source_id_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从调用者输入取得字段，将数据引入当前过程。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：该动作取得运行时上下文或调用者输入。

> read_source_id_from_request

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是控制分发或调度，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分发，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分发，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地读取环境上下文，由 agent_runtime 执行。

> read_fast_key_from_environment

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：从环境上下文取得字段，将数据引入当前过程。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：该动作取得运行时环境上下文。

> read_fast_key_from_environment

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是控制分发或调度，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分发，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分发，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为本地存在性检查，由 agent_runtime 执行。

> check_fast_key_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：根据输入计算或选择输出布尔值，处理内容表示。

> check_fast_key_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：计算存在性布尔值，属于计算、选择或改变表示。

> check_fast_key_present

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：条件分发仍属调度选择，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：条件分发仍是控制操作，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：条件分发仍是控制操作，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该 IR 为工具调用，由本地代理运行时发起或执行调用。

> fast.fetch

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：外部资源 fast.fetch 是执行该调用的工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：工具响应内容被引入当前过程。

> fast.fetch

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：调用外部工具使请求参数到达外部接收方。

> fast.fetch

- `effects` / `net_send`；依据 `cfg`，位置 `g_0027`。
  理由：向远端工具发送请求或参数。

> fast.fetch

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0027`。
  理由：接收远端工具返回内容。

> fast.fetch

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传并进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：根据状态进行分发属于调度选择，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：条件分发是控制操作，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：条件分发是控制操作，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：该重试 IR 为工具调用，由本地代理运行时发起或执行调用。

> fast.fetch

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：外部资源 fast.fetch 是执行该重试调用的工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：工具响应内容被引入当前过程。

> fast.fetch

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：调用外部工具使请求参数到达外部接收方。

> fast.fetch

- `effects` / `net_send`；依据 `cfg`，位置 `g_0033`。
  理由：向远端工具发送请求或参数。

> fast.fetch

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0033`。
  理由：接收远端工具返回内容。

> fast.fetch

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传并进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：根据重试状态进行分发属于调度选择，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：条件分发是控制操作，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：条件分发是控制操作，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：该 IR 为工具调用，由本地代理运行时发起或执行调用。

> archive.fetch

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：外部资源 archive.fetch 是执行该调用的工具。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：工具响应内容被引入当前过程。

> archive.fetch

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：调用外部工具使请求参数到达外部接收方。

> archive.fetch

- `effects` / `net_send`；依据 `cfg`，位置 `g_0039`。
  理由：向远端工具发送请求或参数。

> archive.fetch

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0039`。
  理由：接收远端工具返回内容。

> archive.fetch

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传并进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：根据归档获取状态进行分发属于调度选择，LLM 可参与调度决策；该规则同时说明调度不证明内容可见。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：条件分发是控制操作，不向过程引入数据，也不使内容到达接收方或进行变换。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：条件分发是控制操作，无词表内读取、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：该 IR 为工作流终止返回，由 agent_runtime 执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将输入值返回调用边界，使内容到达接收方或可见边界。

> return

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0050`。
  理由：该 IR 为工作流终止返回，由 agent_runtime 执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0050`。
  理由：将输入值返回调用边界，使内容到达接收方或可见边界。

> return

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0055`。
  理由：该 IR 为工作流终止返回，由 agent_runtime 执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0055`。
  理由：将输入值返回调用边界，使内容到达接收方或可见边界。

> return

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0060`。
  理由：该 IR 为工作流终止返回，由 agent_runtime 执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0060`。
  理由：将输入值返回调用边界，使内容到达接收方或可见边界。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
