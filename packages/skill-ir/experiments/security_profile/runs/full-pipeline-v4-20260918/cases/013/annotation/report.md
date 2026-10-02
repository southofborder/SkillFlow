# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_005` / `effects`：无法仅凭工具名 fast.fetch 或 external_resource 判断是否向远端发送或接收；EM06 要求不据名称猜测网络通信。
- `ir_007` / `effects`：无法仅凭工具名 fast.fetch 或 external_resource 判断重试是否向远端发送或接收；EM06 要求不据名称猜测网络通信。
- `ir_009` / `effects`：无法仅凭工具名 archive.fetch 或 external_resource 判断是否向远端发送或接收；EM06 要求不据名称猜测网络通信。
- `ir_012` / `effects`：return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。
- `ir_014` / `effects`：return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。
- `ir_016` / `effects`：return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。
- `ir_018` / `effects`：return 的接收方未明确，无法确定是否进入模型上下文或面向用户输出；普通 return 不证明 user_output。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id | agent_runtime | source | context_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key | agent_runtime | source | context_read |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | fast.fetch | tool | source, sink | model_observe |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Retry fast.fetch once after a transient error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool | source, sink | model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Call archive.fetch with source_id only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | archive.fetch | tool | source, sink | model_observe |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Append success status and return fast.fetch body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | append_status_to_local_file | agent_runtime | sink | fs_write |
| ir_012 | return | agent_runtime | sink | [] |

### block_007 · Append success status and return fast.fetch retry body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | append_status_to_local_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | sink | [] |

### block_008 · Append success status and return archive.fetch body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | append_status_to_local_file | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | sink | [] |

### block_009 · Append failure status and return archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | append_status_to_local_file | agent_runtime | sink | fs_write |
| ir_018 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 从运行时上下文读取 source_id，由本地代理运行时执行。

> read_source_id

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取结果 result_001 将调用者输入引入当前过程。

> result_001

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：输入类型为 context_key，从运行时上下文取得调用者输入。

> context_key

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是 CFG 内部控制转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表无匹配效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 从运行时环境读取 FAST_KEY，由本地代理运行时执行。

> read_fast_key

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：读取结果将环境数据引入当前过程。

> result_002

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：输入类型为 context_key，取得运行时环境或上下文。

> context_key

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是 CFG 内部控制转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，词表无匹配效果。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：当前动作调用具体外部工具 fast.fetch，执行者为工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：工具返回 body/error/status，向当前过程引入数据。

> fast_fetch_first_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0021`。
  理由：将 result_002 等输入传给工具，内容到达工具边界。

> result_002

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具执行返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是 CFG 内部控制转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，词表无匹配效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：当前动作调用具体外部工具 fast.fetch，执行者为工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：工具返回 body/error/status，向当前过程引入数据。

> fast_fetch_retry_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：将 result_002 等输入传给工具，内容到达工具边界。

> result_002

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具执行返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是 CFG 内部控制转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，词表无匹配效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：当前动作调用具体外部工具 archive.fetch，执行者为工具。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：工具返回 body/error/status，向当前过程引入数据。

> archive_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：将 result_001 等输入传给工具，内容到达工具边界。

> result_001

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具执行返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是 CFG 内部控制转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，词表无匹配效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将状态写入本地存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0039`。
  理由：向本地文件追加内容。

> append_status_to_local_file

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：return 是工作流控制返回，由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0040`。
  理由：返回体使内容到达调用方边界。

> fast_fetch_first_body

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将状态写入本地存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：向本地文件追加内容。

> append_status_to_local_file

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：return 是工作流控制返回，由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0046`。
  理由：返回体使内容到达调用方边界。

> fast_fetch_retry_body

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将状态写入本地存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：向本地文件追加内容。

> append_status_to_local_file

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：return 是工作流控制返回，由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0052`。
  理由：返回体使内容到达调用方边界。

> archive_body

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：将状态写入本地存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0057`。
  理由：向本地文件追加内容。

> append_status_to_local_file

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：return 是工作流控制返回，由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0058`。
  理由：返回错误使内容到达调用方边界。

> archive_error

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
