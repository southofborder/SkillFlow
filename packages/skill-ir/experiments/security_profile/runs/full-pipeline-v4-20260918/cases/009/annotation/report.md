# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`47e63e06f52fdd76f6a9e7b325ca6ee013a5219f4818a99df95477619d975721`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_012` / `effects`：IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。
- `ir_015` / `effects`：普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。
- `ir_016` / `effects`：IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。
- `ir_019` / `effects`：普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。
- `ir_022` / `effects`：IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。
- `ir_025` / `effects`：普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。
- `ir_026` / `effects`：IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。
- `ir_029` / `effects`：普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。

## 按块查看

### block_001 · Read user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | context_read, fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract search term and check optional parameter presence

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_term_from_request | agent_runtime | transformer | transform |
| ir_004 | check_from_date_present | agent_runtime | transformer | transform |
| ir_005 | check_limit_present | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_003 · Extract from_date value when present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_from_date_from_request | agent_runtime | transformer | transform |
| ir_008 | dispatch | llm | [] | [] |

### block_004 · Omit from_date argument and check limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | dispatch | llm | [] | [] |

### block_005 · Extract limit value when present with from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | extract_limit_from_request | agent_runtime | transformer | transform |
| ir_011 | dispatch | llm | [] | [] |

### block_006 · Call index.search with term, from_date, and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | index.search | tool | source, sink | model_observe |
| ir_013 | dispatch | llm | [] | [] |

### block_007 · Write total and return items for the from_date-and-limit search

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | write_total_to_count_txt | agent_runtime | sink | fs_write |
| ir_015 | return | agent_runtime | sink | [] |

### block_008 · Call index.search with term and from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | index.search | tool | source, sink | model_observe |
| ir_017 | dispatch | llm | [] | [] |

### block_009 · Write total and return items for the from_date-only search

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | write_total_to_count_txt | agent_runtime | sink | fs_write |
| ir_019 | return | agent_runtime | sink | [] |

### block_010 · Extract limit value when present without from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | extract_limit_from_request | agent_runtime | transformer | transform |
| ir_021 | dispatch | llm | [] | [] |

### block_011 · Call index.search with term and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | index.search | tool | source, sink | model_observe |
| ir_023 | dispatch | llm | [] | [] |

### block_012 · Write total and return items for the limit-only search

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_024 | write_total_to_count_txt | agent_runtime | sink | fs_write |
| ir_025 | return | agent_runtime | sink | [] |

### block_013 · Call index.search with term only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_026 | index.search | tool | source, sink | model_observe |
| ir_027 | dispatch | llm | [] | [] |

### block_014 · Write total and return items for the term-only search

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_028 | write_total_to_count_txt | agent_runtime | sink | fs_write |
| ir_029 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为本地读取 request.json，由代理运行时执行。

> read_request_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：动作将 request.json 内容引入当前过程。

> request.json

- `effects` / `context_read`；依据 `source`，位置 `src_004`。
  理由：读取用户提供的请求输入。

> Read the user-supplied request.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取 request.json 文件内容。

> read_request_json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地字段提取操作由代理运行时执行。

> extract_term_from_request

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从请求对象中选择 term 字段。

> extract_term_from_request

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取/选择 term 字段并改变数据表示。

> request_term

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：本地存在性检查由代理运行时执行。

> check_from_date_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0016`。
  理由：计算 from_date 是否存在。

> check_from_date_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0016`。
  理由：计算存在性布尔值。

> from_date_present

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0017`。
  理由：本地存在性检查由代理运行时执行。

> check_limit_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0017`。
  理由：计算 limit 是否存在。

> check_limit_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0017`。
  理由：计算存在性布尔值。

> limit_present

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0023`。
  理由：本地字段提取操作由代理运行时执行。

> extract_from_date_from_request

- `roles` / `transformer`；依据 `cfg`，位置 `g_0023`。
  理由：从请求对象中选择 from_date 字段。

> extract_from_date_from_request

- `effects` / `transform`；依据 `cfg`，位置 `g_0023`。
  理由：提取/选择 from_date 值。

> from_date_value

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0024`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_009

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：本地字段提取操作由代理运行时执行。

> extract_limit_from_request

- `roles` / `transformer`；依据 `cfg`，位置 `g_0034`。
  理由：从请求对象中选择 limit 字段。

> extract_limit_from_request

- `effects` / `transform`；依据 `cfg`，位置 `g_0034`。
  理由：提取/选择 limit 值。

> limit_value_with_from_date

### ir_011

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0035`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0035`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_012

- `actor` / `tool`；依据 `cfg`，位置 `g_0040`。
  理由：IR 调用具名工具 index.search。

> index.search

- `roles` / `sink`；依据 `cfg`，位置 `g_0040`。
  理由：查询参数作为调用参数发送给工具，使内容到达接收方。

> Use request.term unchanged as its query argument.

- `roles` / `source`；依据 `cfg`，位置 `g_0040`。
  理由：工具返回结果引入当前过程。

> search_items_with_from_date_and_limit

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果回传默认进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_013

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0041`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0041`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：本地写文件操作由代理运行时执行。

> write_total_to_count_txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0046`。
  理由：将 total 写入 count.txt 存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0046`。
  理由：创建或修改 count.txt 文件内容。

> write_total_to_count_txt

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0047`。
  理由：return 操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0047`。
  理由：返回 items 使内容到达调用方或输出边界。

> Return the search response's items value unchanged.

### ir_016

- `actor` / `tool`；依据 `cfg`，位置 `g_0052`。
  理由：IR 调用具名工具 index.search。

> index.search

- `roles` / `sink`；依据 `cfg`，位置 `g_0052`。
  理由：查询参数作为调用参数发送给工具，使内容到达接收方。

> Use request.term unchanged as its query argument.

- `roles` / `source`；依据 `cfg`，位置 `g_0052`。
  理由：工具返回结果引入当前过程。

> search_items_with_from_date_only

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果回传默认进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_017

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0053`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0053`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：本地写文件操作由代理运行时执行。

> write_total_to_count_txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0058`。
  理由：将 total 写入 count.txt 存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0058`。
  理由：创建或修改 count.txt 文件内容。

> write_total_to_count_txt

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0059`。
  理由：return 操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0059`。
  理由：返回 items 使内容到达调用方或输出边界。

> Return the search response's items value unchanged.

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：本地字段提取操作由代理运行时执行。

> extract_limit_from_request

- `roles` / `transformer`；依据 `cfg`，位置 `g_0064`。
  理由：从请求对象中选择 limit 字段。

> extract_limit_from_request

- `effects` / `transform`；依据 `cfg`，位置 `g_0064`。
  理由：提取/选择 limit 值。

> limit_value_without_from_date

### ir_021

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0065`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0065`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_022

- `actor` / `tool`；依据 `cfg`，位置 `g_0070`。
  理由：IR 调用具名工具 index.search。

> index.search

- `roles` / `sink`；依据 `cfg`，位置 `g_0070`。
  理由：查询参数作为调用参数发送给工具，使内容到达接收方。

> Use request.term unchanged as its query argument.

- `roles` / `source`；依据 `cfg`，位置 `g_0070`。
  理由：工具返回结果引入当前过程。

> search_items_with_limit_only

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果回传默认进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_023

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0071`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0071`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_024

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0076`。
  理由：本地写文件操作由代理运行时执行。

> write_total_to_count_txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0076`。
  理由：将 total 写入 count.txt 存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0076`。
  理由：创建或修改 count.txt 文件内容。

> write_total_to_count_txt

### ir_025

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0077`。
  理由：return 操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0077`。
  理由：返回 items 使内容到达调用方或输出边界。

> Return the search response's items value unchanged.

### ir_026

- `actor` / `tool`；依据 `cfg`，位置 `g_0082`。
  理由：IR 调用具名工具 index.search。

> index.search

- `roles` / `sink`；依据 `cfg`，位置 `g_0082`。
  理由：查询参数作为调用参数发送给工具，使内容到达接收方。

> Use request.term unchanged as its query argument.

- `roles` / `source`；依据 `cfg`，位置 `g_0082`。
  理由：工具返回结果引入当前过程。

> search_items_with_term_only

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果回传默认进入 LLM 上下文。

> 默认进入 LLM 上下文

### ir_027

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度/控制选择，可能由 LLM 参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0083`。
  理由：纯控制转移，不引入、变换或输出内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0083`。
  理由：纯控制操作，无词表内效果。

> dispatch

### ir_028

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0088`。
  理由：本地写文件操作由代理运行时执行。

> write_total_to_count_txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0088`。
  理由：将 total 写入 count.txt 存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0088`。
  理由：创建或修改 count.txt 文件内容。

> write_total_to_count_txt

### ir_029

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0089`。
  理由：return 操作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0089`。
  理由：返回 items 使内容到达调用方或输出边界。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
