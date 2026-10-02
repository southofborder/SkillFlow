# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`4eb512c458d5c3da56765890eeb7bb7d21f75066331dce2a6fff400c964b3fcd`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_014` / `effects`：IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。
- `ir_016` / `effects`：IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。
- `ir_018` / `effects`：IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。
- `ir_020` / `effects`：IR 仅记录 external_resource index.search，未记录远端通信依据，无法确定 net_send/net_receive。
- `ir_025` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。
- `ir_029` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。
- `ir_033` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。
- `ir_037` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否适用；无其他可确定效果。

## 按块查看

### block_001 · Read the request JSON file

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_file | tool | source | fs_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract term and check optional parameter presence

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | llm | transformer | transform, model_observe |
| ir_004 | check_from_date_present | llm | transformer | transform, model_observe |
| ir_005 | check_limit_present | llm | transformer | transform, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_003 · Extract present from_date and limit values

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_request_from_date | llm | transformer | transform, model_observe |
| ir_008 | extract_request_limit | llm | transformer | transform, model_observe |
| ir_009 | dispatch | llm | [] | [] |

### block_004 · Extract present from_date value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | extract_request_from_date | llm | transformer | transform, model_observe |
| ir_011 | dispatch | llm | [] | [] |

### block_005 · Extract present limit value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | extract_request_limit | llm | transformer | transform, model_observe |
| ir_013 | dispatch | llm | [] | [] |

### block_006 · Call index.search with term, from_date, and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | index_search | tool | source, sink, transformer | model_observe, transform |
| ir_015 | dispatch | llm | [] | [] |

### block_007 · Call index.search with term and from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | index_search | tool | source, sink, transformer | model_observe, transform |
| ir_017 | dispatch | llm | [] | [] |

### block_008 · Call index.search with term and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | index_search | tool | source, sink, transformer | model_observe, transform |
| ir_019 | dispatch | llm | [] | [] |

### block_009 · Call index.search with term only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | index_search | tool | source, sink, transformer | model_observe, transform |
| ir_021 | dispatch | llm | [] | [] |

### block_010 · Write total and return items from search with both parameters

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | extract_search_total | llm | transformer | transform, model_observe |
| ir_023 | write_count_total_to_file | tool | sink | fs_write |
| ir_024 | extract_search_items | llm | transformer | transform, model_observe |
| ir_025 | return | llm | sink | [] |

### block_011 · Write total and return items from search with from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_026 | extract_search_total | llm | transformer | transform, model_observe |
| ir_027 | write_count_total_to_file | tool | sink | fs_write |
| ir_028 | extract_search_items | llm | transformer | transform, model_observe |
| ir_029 | return | llm | sink | [] |

### block_012 · Write total and return items from search with limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_030 | extract_search_total | llm | transformer | transform, model_observe |
| ir_031 | write_count_total_to_file | tool | sink | fs_write |
| ir_032 | extract_search_items | llm | transformer | transform, model_observe |
| ir_033 | return | llm | sink | [] |

### block_013 · Write total and return items from search with term only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_034 | extract_search_total | llm | transformer | transform, model_observe |
| ir_035 | write_count_total_to_file | tool | sink | fs_write |
| ir_036 | extract_search_items | llm | transformer | transform, model_observe |
| ir_037 | return | llm | sink | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 是读取 request.json 的工具动作，由工具执行。

> read_request_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取文件内容并输出结果，向当前过程引入数据。

> request_data

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取 request.json 文件内容。

> read_request_file

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果作为工具返回内容，默认进入模型上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `cfg`，位置 `g_0010`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_003

- `actor` / `llm`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 由模型按 Skill 从请求数据中提取 term。

> extract_request_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从请求数据中选择/提取字段，改变内容表示。

> extract_request_term

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：字段提取属于选择/表示变换。

> extract_request_term

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_004

- `actor` / `llm`；依据 `cfg`，位置 `g_0016`。
  理由：该 IR 由模型检查可选参数是否存在。

> check_from_date_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0016`。
  理由：检查存在性并产生布尔结果，属于计算/选择变换。

> check_from_date_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0016`。
  理由：存在性检查属于计算/选择变换。

> check_from_date_present

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_005

- `actor` / `llm`；依据 `cfg`，位置 `g_0017`。
  理由：该 IR 由模型检查可选参数是否存在。

> check_limit_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0017`。
  理由：检查存在性并产生布尔结果，属于计算/选择变换。

> check_limit_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0017`。
  理由：存在性检查属于计算/选择变换。

> check_limit_present

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_006

- `actor` / `llm`；依据 `cfg`，位置 `g_0018`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0018`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_007

- `actor` / `llm`；依据 `cfg`，位置 `g_0023`。
  理由：该 IR 由模型从请求数据中提取 from_date 值。

> extract_request_from_date

- `roles` / `transformer`；依据 `cfg`，位置 `g_0023`。
  理由：字段提取属于选择/表示变换。

> extract_request_from_date

- `effects` / `transform`；依据 `cfg`，位置 `g_0023`。
  理由：字段提取属于选择/表示变换。

> extract_request_from_date

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_008

- `actor` / `llm`；依据 `cfg`，位置 `g_0024`。
  理由：该 IR 由模型从请求数据中提取 limit 值。

> extract_request_limit

- `roles` / `transformer`；依据 `cfg`，位置 `g_0024`。
  理由：字段提取属于选择/表示变换。

> extract_request_limit

- `effects` / `transform`；依据 `cfg`，位置 `g_0024`。
  理由：字段提取属于选择/表示变换。

> extract_request_limit

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_009

- `actor` / `llm`；依据 `cfg`，位置 `g_0025`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0025`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0025`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_010

- `actor` / `llm`；依据 `cfg`，位置 `g_0030`。
  理由：该 IR 由模型从请求数据中提取 from_date 值。

> extract_request_from_date

- `roles` / `transformer`；依据 `cfg`，位置 `g_0030`。
  理由：字段提取属于选择/表示变换。

> extract_request_from_date

- `effects` / `transform`；依据 `cfg`，位置 `g_0030`。
  理由：字段提取属于选择/表示变换。

> extract_request_from_date

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_011

- `actor` / `llm`；依据 `cfg`，位置 `g_0031`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0031`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0031`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_012

- `actor` / `llm`；依据 `cfg`，位置 `g_0036`。
  理由：该 IR 由模型从请求数据中提取 limit 值。

> extract_request_limit

- `roles` / `transformer`；依据 `cfg`，位置 `g_0036`。
  理由：字段提取属于选择/表示变换。

> extract_request_limit

- `effects` / `transform`；依据 `cfg`，位置 `g_0036`。
  理由：字段提取属于选择/表示变换。

> extract_request_limit

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理请求数据内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_013

- `actor` / `llm`；依据 `cfg`，位置 `g_0037`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0037`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0037`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_014

- `actor` / `tool`；依据 `cfg`，位置 `g_0042`。
  理由：该 IR 调用 index.search 工具，由工具执行。

> index_search

- `roles` / `source`；依据 `cfg`，位置 `g_0042`。
  理由：外部检索响应作为输出引入当前过程。

> search_response_both

- `roles` / `sink`；依据 `cfg`，位置 `g_0042`。
  理由：调用把查询参数交给外部资源接收方，形成输出边界。

> index.search

- `roles` / `transformer`；依据 `cfg`，位置 `g_0042`。
  理由：检索动作根据查询选择/组合结果，属于变换。

> index_search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：检索响应作为工具返回内容默认进入模型上下文。

> 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0042`。
  理由：检索计算/选择结果，属于变换。

> index_search

### ir_015

- `actor` / `llm`；依据 `cfg`，位置 `g_0043`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0043`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0043`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_016

- `actor` / `tool`；依据 `cfg`，位置 `g_0048`。
  理由：该 IR 调用 index.search 工具，由工具执行。

> index_search

- `roles` / `source`；依据 `cfg`，位置 `g_0048`。
  理由：外部检索响应作为输出引入当前过程。

> search_response_from

- `roles` / `sink`；依据 `cfg`，位置 `g_0048`。
  理由：调用把查询参数交给外部资源接收方，形成输出边界。

> index.search

- `roles` / `transformer`；依据 `cfg`，位置 `g_0048`。
  理由：检索动作根据查询选择/组合结果，属于变换。

> index_search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：检索响应作为工具返回内容默认进入模型上下文。

> 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0048`。
  理由：检索计算/选择结果，属于变换。

> index_search

### ir_017

- `actor` / `llm`；依据 `cfg`，位置 `g_0049`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0049`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0049`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_018

- `actor` / `tool`；依据 `cfg`，位置 `g_0054`。
  理由：该 IR 调用 index.search 工具，由工具执行。

> index_search

- `roles` / `source`；依据 `cfg`，位置 `g_0054`。
  理由：外部检索响应作为输出引入当前过程。

> search_response_limit

- `roles` / `sink`；依据 `cfg`，位置 `g_0054`。
  理由：调用把查询参数交给外部资源接收方，形成输出边界。

> index.search

- `roles` / `transformer`；依据 `cfg`，位置 `g_0054`。
  理由：检索动作根据查询选择/组合结果，属于变换。

> index_search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：检索响应作为工具返回内容默认进入模型上下文。

> 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0054`。
  理由：检索计算/选择结果，属于变换。

> index_search

### ir_019

- `actor` / `llm`；依据 `cfg`，位置 `g_0055`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0055`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0055`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_020

- `actor` / `tool`；依据 `cfg`，位置 `g_0060`。
  理由：该 IR 调用 index.search 工具，由工具执行。

> index_search

- `roles` / `source`；依据 `cfg`，位置 `g_0060`。
  理由：外部检索响应作为输出引入当前过程。

> search_response_neither

- `roles` / `sink`；依据 `cfg`，位置 `g_0060`。
  理由：调用把查询参数交给外部资源接收方，形成输出边界。

> index.search

- `roles` / `transformer`；依据 `cfg`，位置 `g_0060`。
  理由：检索动作根据查询选择/组合结果，属于变换。

> index_search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：检索响应作为工具返回内容默认进入模型上下文。

> 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0060`。
  理由：检索计算/选择结果，属于变换。

> index_search

### ir_021

- `actor` / `llm`；依据 `cfg`，位置 `g_0061`。
  理由：该 IR 为调度/控制转移，LLM 可参与选择推进；调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0061`。
  理由：纯控制转移，不向过程引入数据、不使内容到达接收方或存储，也不变换内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0061`。
  理由：纯控制操作，词表无匹配效果；不因分支选择硬贴 transform。

> dispatch

### ir_022

- `actor` / `llm`；依据 `cfg`，位置 `g_0066`。
  理由：该 IR 由模型从搜索结果中提取 total。

> extract_search_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0066`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_total

- `effects` / `transform`；依据 `cfg`，位置 `g_0066`。
  理由：字段提取属于选择/表示变换。

> extract_search_total

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_023

- `actor` / `tool`；依据 `cfg`，位置 `g_0067`。
  理由：该 IR 是写入本地文件的工具动作，由工具执行。

> write_count_total_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0067`。
  理由：写入本地文件使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0067`。
  理由：创建/修改本地文件内容。

> write_count_total_to_file

### ir_024

- `actor` / `llm`；依据 `cfg`，位置 `g_0068`。
  理由：该 IR 由模型从搜索结果中提取 items。

> extract_search_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0068`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_items

- `effects` / `transform`；依据 `cfg`，位置 `g_0068`。
  理由：字段提取属于选择/表示变换。

> extract_search_items

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_025

- `actor` / `llm`；依据 `cfg`，位置 `g_0069`。
  理由：该 IR 由模型将结果返回给调用方。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0069`。
  理由：return 将结果提供给调用方，形成接收边界；不判断是否用户。

> search_items_both

### ir_026

- `actor` / `llm`；依据 `cfg`，位置 `g_0074`。
  理由：该 IR 由模型从搜索结果中提取 total。

> extract_search_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0074`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_total

- `effects` / `transform`；依据 `cfg`，位置 `g_0074`。
  理由：字段提取属于选择/表示变换。

> extract_search_total

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_027

- `actor` / `tool`；依据 `cfg`，位置 `g_0075`。
  理由：该 IR 是写入本地文件的工具动作，由工具执行。

> write_count_total_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0075`。
  理由：写入本地文件使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0075`。
  理由：创建/修改本地文件内容。

> write_count_total_to_file

### ir_028

- `actor` / `llm`；依据 `cfg`，位置 `g_0076`。
  理由：该 IR 由模型从搜索结果中提取 items。

> extract_search_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0076`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_items

- `effects` / `transform`；依据 `cfg`，位置 `g_0076`。
  理由：字段提取属于选择/表示变换。

> extract_search_items

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_029

- `actor` / `llm`；依据 `cfg`，位置 `g_0077`。
  理由：该 IR 由模型将结果返回给调用方。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0077`。
  理由：return 将结果提供给调用方，形成接收边界；不判断是否用户。

> search_items_from

### ir_030

- `actor` / `llm`；依据 `cfg`，位置 `g_0082`。
  理由：该 IR 由模型从搜索结果中提取 total。

> extract_search_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0082`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_total

- `effects` / `transform`；依据 `cfg`，位置 `g_0082`。
  理由：字段提取属于选择/表示变换。

> extract_search_total

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_031

- `actor` / `tool`；依据 `cfg`，位置 `g_0083`。
  理由：该 IR 是写入本地文件的工具动作，由工具执行。

> write_count_total_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0083`。
  理由：写入本地文件使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0083`。
  理由：创建/修改本地文件内容。

> write_count_total_to_file

### ir_032

- `actor` / `llm`；依据 `cfg`，位置 `g_0084`。
  理由：该 IR 由模型从搜索结果中提取 items。

> extract_search_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0084`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_items

- `effects` / `transform`；依据 `cfg`，位置 `g_0084`。
  理由：字段提取属于选择/表示变换。

> extract_search_items

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_033

- `actor` / `llm`；依据 `cfg`，位置 `g_0085`。
  理由：该 IR 由模型将结果返回给调用方。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0085`。
  理由：return 将结果提供给调用方，形成接收边界；不判断是否用户。

> search_items_limit

### ir_034

- `actor` / `llm`；依据 `cfg`，位置 `g_0090`。
  理由：该 IR 由模型从搜索结果中提取 total。

> extract_search_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0090`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_total

- `effects` / `transform`；依据 `cfg`，位置 `g_0090`。
  理由：字段提取属于选择/表示变换。

> extract_search_total

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_035

- `actor` / `tool`；依据 `cfg`，位置 `g_0091`。
  理由：该 IR 是写入本地文件的工具动作，由工具执行。

> write_count_total_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0091`。
  理由：写入本地文件使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0091`。
  理由：创建/修改本地文件内容。

> write_count_total_to_file

### ir_036

- `actor` / `llm`；依据 `cfg`，位置 `g_0092`。
  理由：该 IR 由模型从搜索结果中提取 items。

> extract_search_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0092`。
  理由：从搜索结果中选择/提取字段，改变内容表示。

> extract_search_items

- `effects` / `transform`；依据 `cfg`，位置 `g_0092`。
  理由：字段提取属于选择/表示变换。

> extract_search_items

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理搜索结果内容，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_037

- `actor` / `llm`；依据 `cfg`，位置 `g_0093`。
  理由：该 IR 由模型将结果返回给调用方。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0093`。
  理由：return 将结果提供给调用方，形成接收边界；不判断是否用户。

> search_items_neither

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
