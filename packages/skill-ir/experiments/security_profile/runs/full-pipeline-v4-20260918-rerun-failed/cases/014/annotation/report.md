# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`13d9e80c7ecdb488709b6642a52c3802baa9e74653bde4f4940e40e7bfc73027`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

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
| ir_007 | fast.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Retry fast.fetch exactly once after a transient first failure

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | fast.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Call archive.fetch with source_id only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | archive.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Append success status and return the first fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | sink | [] |

### block_008 · Append success status and return the retry fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | sink | [] |

### block_009 · Append success status and return the archive.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_018 | return | agent_runtime | sink | [] |

### block_010 · Append failure status and return the archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_020 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为从请求读取 source_id 的上下文读取动作，由代理运行时取得调用者输入。

> read_source_id_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：输入类型为 context_key，读取 source_id 并向当前过程引入调用者输入。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：从请求上下文取得 source_id，属于 context_read。

> source_id

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：从环境读取 FAST_KEY，属代理运行时读取环境上下文。

> read_fast_key_from_environment

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：以 context_key 读取 FAST_KEY，向当前过程引入环境数据。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：从环境取得 FAST_KEY，属于 context_read。

> FAST_KEY

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：检查 FAST_KEY 是否存在，由本地运行时计算布尔结果。

> check_fast_key_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：基于 fast_key_value 计算存在性判断，充当变换者。

> fast_key_value

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：将值转换为存在性布尔结果，属于计算/选择/改变表示。

> fast_key_present

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：opcode 与 external_resource 均为 fast.fetch，当前动作由该工具执行。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：该调用输出 fast_fetch_body，向当前过程引入外部返回内容。

> fast_fetch_body

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：调用将 source_id 与 FAST_KEY 作为参数发给 fast.fetch，使内容到达外部接收方。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / `net_send`；依据 `source`，位置 `src_003`。
  理由：向外部工具发送 source_id 与 FAST_KEY 请求参数，构成 net_send。

> try fast.fetch first with source_id and FAST_KEY

- `effects` / `net_receive`；依据 `source`，位置 `src_005`。
  理由：成功响应体由工具返回，构成读取型请求的接收侧 net_receive。

> return that successful response's body value unchanged

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：EM02 假设工具结果默认回传 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该重试 IR 的 opcode 与 external_resource 为 fast.fetch，由该工具执行。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：该调用输出 fast_fetch_retry_body，向当前过程引入外部返回内容。

> fast_fetch_retry_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：重试调用仍以 fast_key_value 等结果作为输入发送给 fast.fetch。

> fast_key_value

- `effects` / `net_send`；依据 `cfg`，位置 `g_0033`。
  理由：重试 fast.fetch 时输入 fast_key_value 等参数，构成向外部发送请求参数。

> fast_key_value

- `effects` / `net_receive`；依据 `source`，位置 `src_005`。
  理由：成功响应体由工具返回，构成读取型请求的接收侧 net_receive。

> return that successful response's body value unchanged

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：EM02 假设工具结果默认回传 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：opcode 与 external_resource 均为 archive.fetch，当前动作由该工具执行。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：该调用输出 archive_fetch_body，向当前过程引入外部返回内容。

> archive_fetch_body

- `roles` / `sink`；依据 `source`，位置 `src_005`。
  理由：调用将 source_id 作为唯一参数发给 archive.fetch，使内容到达外部接收方。

> pass source_id as its only argument

- `effects` / `net_send`；依据 `source`，位置 `src_005`。
  理由：向外部工具发送 source_id 请求参数，构成 net_send。

> pass source_id as its only argument

- `effects` / `net_receive`；依据 `source`，位置 `src_005`。
  理由：成功响应体由工具返回，构成读取型请求的接收侧 net_receive。

> return that successful response's body value unchanged

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：EM02 假设工具结果默认回传 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 IR 为 dispatch 控制调度，由 LLM 参与选择后续路径。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：调度仅作控制转移，不引入、发送或变换内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制调度，词表没有匹配的执行效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地追加状态文件，由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将 success 状态写入 status.txt，使内容到达本地存储位置。

> status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：创建/追加写入本地文件内容。

> append_final_status_to_status_file

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：返回操作由代理运行时执行控制流。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0046`。
  理由：将 fast_fetch_body 返回给调用方边界，使内容到达接收方。

> fast_fetch_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未被词表直接覆盖，且不证明 user_output 或其他网络/文件/模型效果。

> 普通 return 不能单独证明面向用户输出

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：本地追加状态文件，由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将 success 状态写入 status.txt，使内容到达本地存储位置。

> status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：创建/追加写入本地文件内容。

> append_final_status_to_status_file

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：返回操作由代理运行时执行控制流。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0052`。
  理由：将 fast_fetch_retry_body 返回给调用方边界，使内容到达接收方。

> fast_fetch_retry_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未被词表直接覆盖，且不证明 user_output 或其他网络/文件/模型效果。

> 普通 return 不能单独证明面向用户输出

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：本地追加状态文件，由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：将 success 状态写入 status.txt，使内容到达本地存储位置。

> status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0057`。
  理由：创建/追加写入本地文件内容。

> append_final_status_to_status_file

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：返回操作由代理运行时执行控制流。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0058`。
  理由：将 archive_fetch_body 返回给调用方边界，使内容到达接收方。

> archive_fetch_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未被词表直接覆盖，且不证明 user_output 或其他网络/文件/模型效果。

> 普通 return 不能单独证明面向用户输出

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：本地追加状态文件，由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0063`。
  理由：将 failure 状态写入 status.txt，使内容到达本地存储位置。

> status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0063`。
  理由：创建/追加写入本地文件内容。

> append_final_status_to_status_file

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：返回操作由代理运行时执行控制流。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0064`。
  理由：将 archive_fetch_error 返回给调用方边界，使内容到达接收方。

> archive_fetch_error

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未被词表直接覆盖，且不证明 user_output 或其他网络/文件/模型效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
