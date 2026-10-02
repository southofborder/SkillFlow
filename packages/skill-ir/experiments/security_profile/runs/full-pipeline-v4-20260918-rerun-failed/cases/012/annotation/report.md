# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`796f48038215875de14e671b6380e9790eda72f22aea32e210a092cba82559be`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_006` / `effects`：无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive
- `ir_009` / `effects`：普通 return 未记录直接用户展示，无法确定 user_output 是否适用
- `ir_010` / `effects`：无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive
- `ir_013` / `effects`：普通 return 未记录直接用户展示，无法确定 user_output 是否适用
- `ir_014` / `effects`：无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive
- `ir_017` / `effects`：普通 return 未记录直接用户展示，无法确定 user_output 是否适用
- `ir_018` / `effects`：无通信依据，无法确定 index.search 是否向远端发送或接收内容；不能仅凭工具名称推断 net_send/net_receive
- `ir_021` / `effects`：普通 return 未记录直接用户展示，无法确定 user_output 是否适用

## 按块查看

### block_001 · Read request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Extract request fields

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_fields | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Choose index.search arguments

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | dispatch | llm, agent_runtime | [] | [] |

### block_004 · Call index.search with from_date and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_006 | index_search | tool | source, sink | model_observe |
| ir_007 | dispatch | agent_runtime | [] | [] |

### block_005 · Write total and return items for from_date and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | write_count_file | agent_runtime | sink | fs_write |
| ir_009 | return | agent_runtime | sink | [] |

### block_006 · Call index.search with from_date and default limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | index_search | tool | source, sink | model_observe |
| ir_011 | dispatch | agent_runtime | [] | [] |

### block_007 · Write total and return items for from_date and default limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | write_count_file | agent_runtime | sink | fs_write |
| ir_013 | return | agent_runtime | sink | [] |

### block_008 · Call index.search with omitted from_date and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | index_search | tool | source, sink | model_observe |
| ir_015 | dispatch | agent_runtime | [] | [] |

### block_009 · Write total and return items for omitted from_date and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | write_count_file | agent_runtime | sink | fs_write |
| ir_017 | return | agent_runtime | sink | [] |

### block_010 · Call index.search with omitted from_date and default limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | index_search | tool | source, sink | model_observe |
| ir_019 | dispatch | agent_runtime | [] | [] |

### block_011 · Write total and return items for omitted from_date and default limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | write_count_file | agent_runtime | sink | fs_write |
| ir_021 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 是本地文件读取动作，由代理运行时执行

> read_request_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取动作将 request.json 内容引入当前过程

> Read the user-supplied request.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取文件内容

> read_request_json

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地运行时解析并提取请求字段

> extract_request_fields

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：动作处理输入并产生各字段

> extract_request_fields

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：本地字段提取属于处理/变换内容

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_005

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该 dispatch 依据存在性标志选择分支，属于 LLM 调度

> LLM 调度不等于内容可见

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0021`。
  理由：仅根据存在性标志选择分支，不引入、变换或输出内容数据

> from_date_present

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0021`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_006

- `actor` / `tool`；依据 `cfg`，位置 `g_0026`。
  理由：该 IR 调用外部工具 index.search，由工具执行

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0026`。
  理由：工具返回结果进入当前过程，充当来源

> search_items_pp

- `roles` / `sink`；依据 `cfg`，位置 `g_0026`。
  理由：查询参数进入工具调用，到达接收边界

> Use request.term unchanged as query argument.

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 为工具调用，返回结果默认进入模型上下文

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0027`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0027`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0032`。
  理由：本地运行时执行文件写入

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0032`。
  理由：写入使内容到达本地存储位置

> Write the response's total value to local count.txt.

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0032`。
  理由：动作创建/修改本地文件内容

> write_count_file

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：运行时执行返回调用方

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：返回使 items 到达调用方/可见边界

> search_items_pp

### ir_010

- `actor` / `tool`；依据 `cfg`，位置 `g_0038`。
  理由：该 IR 调用外部工具 index.search，由工具执行

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0038`。
  理由：工具返回结果进入当前过程，充当来源

> search_total_pm

- `roles` / `sink`；依据 `cfg`，位置 `g_0038`。
  理由：参数进入工具调用，到达接收边界

> Pass 10 as limit argument because limit is missing.

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 为工具调用，返回结果默认进入模型上下文

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0039`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0039`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0044`。
  理由：本地运行时执行文件写入

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0044`。
  理由：写入使内容到达本地存储位置

> Write the response's total value to local count.txt.

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0044`。
  理由：动作创建/修改本地文件内容

> write_count_file

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：运行时执行返回调用方

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：返回使 items 到达调用方/可见边界

> search_items_pm

### ir_014

- `actor` / `tool`；依据 `cfg`，位置 `g_0050`。
  理由：该 IR 调用外部工具 index.search，由工具执行

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0050`。
  理由：工具返回结果进入当前过程，充当来源

> search_items_mp

- `roles` / `sink`；依据 `cfg`，位置 `g_0050`。
  理由：参数进入工具调用，到达接收边界

> Pass limit value unchanged.

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 为工具调用，返回结果默认进入模型上下文

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0051`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0051`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0056`。
  理由：本地运行时执行文件写入

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0056`。
  理由：写入使内容到达本地存储位置

> Write the response's total value to local count.txt.

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0056`。
  理由：动作创建/修改本地文件内容

> write_count_file

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：运行时执行返回调用方

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：返回使 items 到达调用方/可见边界

> search_items_mp

### ir_018

- `actor` / `tool`；依据 `cfg`，位置 `g_0062`。
  理由：该 IR 调用外部工具 index.search，由工具执行

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0062`。
  理由：工具返回结果进入当前过程，充当来源

> search_items_mm

- `roles` / `sink`；依据 `cfg`，位置 `g_0062`。
  理由：参数进入工具调用，到达接收边界

> Pass 10 as limit argument because limit is missing.

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 为工具调用，返回结果默认进入模型上下文

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：控制流跳转由代理运行时执行

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0063`。
  理由：纯控制跳转，不引入、变换或输出内容

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0063`。
  理由：纯控制操作，无词表匹配效果

> dispatch

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0068`。
  理由：本地运行时执行文件写入

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0068`。
  理由：写入使内容到达本地存储位置

> Write the response's total value to local count.txt.

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0068`。
  理由：动作创建/修改本地文件内容

> write_count_file

### ir_021

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0069`。
  理由：运行时执行返回调用方

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0069`。
  理由：返回使 items 到达调用方/可见边界

> search_items_mm

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
