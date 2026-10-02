# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`419ebdfa305fb171533662ca807f6e399ab21faafe087065dff05f9bc5711c24`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_003` / `effects`：无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。
- `ir_005` / `effects`：无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。
- `ir_007` / `effects`：无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。
- `ir_009` / `effects`：无法仅凭 index.search 工具名确定是否发生远端网络发送/接收（EM06）。
- `ir_012` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。
- `ir_014` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。
- `ir_016` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。
- `ir_018` / `effects`：普通 return 不能单独证明面向用户输出，无法确定 user_output 是否发生。

## 按块查看

### block_001 · Read request.json and choose optional parameter path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source, transformer | context_read, fs_read, transform |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Call index.search with from_date and limit present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | index.search | tool | source, sink, transformer | model_observe, transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Call index.search with only from_date present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | index.search | tool | source, sink, transformer | model_observe, transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Call index.search with only limit present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | tool | source, sink, transformer | model_observe, transform |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Call index.search with neither optional parameter present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | index.search | tool | source, sink, transformer | model_observe, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Write total and return items for both-present path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | write_total_to_count_file | agent_runtime | sink | fs_write |
| ir_012 | return | agent_runtime | sink | [] |

### block_007 · Write total and return items for from_date-only path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_total_to_count_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | sink | [] |

### block_008 · Write total and return items for limit-only path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | write_total_to_count_file | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | sink | [] |

### block_009 · Write total and return items for neither-present path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | write_total_to_count_file | agent_runtime | sink | fs_write |
| ir_018 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 表示本地读取请求文件，执行者为代理运行时。

> read_request_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从外部资源 request.json 引入请求数据。

> request.json

- `roles` / `transformer`；依据 `cfg`，位置 `g_0009`。
  理由：读取 JSON 并提取 term/from_date/limit，属于改变表示或选择。

> request.term

- `effects` / `context_read`；依据 `source`，位置 `src_007`。
  理由：读取用户提供的请求，属于取得调用者输入。

> Read the user-supplied request.json

- `effects` / `fs_read`；依据 `source`，位置 `src_007`。
  理由：读取本地文件内容。

> Read the user-supplied request.json

- `effects` / `transform`；依据 `cfg`，位置 `g_0009`。
  理由：解析并提取字段，属于处理/变换内容。

> request.term

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度选择路径，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无匹配的效果标签。

> dispatch

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 调用 index.search 工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：返回搜索结果，向当前过程引入数据。

> search response total

- `roles` / `sink`；依据 `cfg`，位置 `g_0015`。
  理由：调用参数到达 index.search 工具/服务。

> request_term

- `roles` / `transformer`；依据 `source`，位置 `src_006`。
  理由：工具执行搜索匹配，属于处理/选择内容。

> index.search supports fuzzy matching

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 是工具执行，返回的 total/items 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `source`，位置 `src_006`。
  理由：搜索匹配并生成结果，属于计算/选择。

> index.search supports fuzzy matching

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度选择路径，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无匹配的效果标签。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 调用 index.search 工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：返回搜索结果，向当前过程引入数据。

> search response total

- `roles` / `sink`；依据 `cfg`，位置 `g_0021`。
  理由：调用参数到达 index.search 工具/服务。

> request_term

- `roles` / `transformer`；依据 `source`，位置 `src_006`。
  理由：工具执行搜索匹配，属于处理/选择内容。

> index.search supports fuzzy matching

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 是工具执行，返回的 total/items 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `source`，位置 `src_006`。
  理由：搜索匹配并生成结果，属于计算/选择。

> index.search supports fuzzy matching

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度选择路径，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无匹配的效果标签。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该 IR 调用 index.search 工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：返回搜索结果，向当前过程引入数据。

> search response total

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：调用参数到达 index.search 工具/服务。

> request_term

- `roles` / `transformer`；依据 `source`，位置 `src_006`。
  理由：工具执行搜索匹配，属于处理/选择内容。

> index.search supports fuzzy matching

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 是工具执行，返回的 total/items 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `source`，位置 `src_006`。
  理由：搜索匹配并生成结果，属于计算/选择。

> index.search supports fuzzy matching

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度选择路径，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无匹配的效果标签。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 调用 index.search 工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：返回搜索结果，向当前过程引入数据。

> search response total

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：调用参数到达 index.search 工具/服务。

> request_term

- `roles` / `transformer`；依据 `source`，位置 `src_006`。
  理由：工具执行搜索匹配，属于处理/选择内容。

> index.search supports fuzzy matching

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 是工具执行，返回的 total/items 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `source`，位置 `src_006`。
  理由：搜索匹配并生成结果，属于计算/选择。

> index.search supports fuzzy matching

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度选择路径，LLM 可参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，不引入、发送或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无匹配的效果标签。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地写文件动作由代理运行时执行。

> write_total_to_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将 total 写入本地 count.txt，使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_013`。
  理由：写入本地文件 count.txt。

> write the response's total value to local count.txt

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：使 items 到达返回边界/调用者。

> Return the search response's items value unchanged

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地写文件动作由代理运行时执行。

> write_total_to_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将 total 写入本地 count.txt，使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_013`。
  理由：写入本地文件 count.txt。

> write the response's total value to local count.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：使 items 到达返回边界/调用者。

> Return the search response's items value unchanged

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：本地写文件动作由代理运行时执行。

> write_total_to_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将 total 写入本地 count.txt，使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_013`。
  理由：写入本地文件 count.txt。

> write the response's total value to local count.txt

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：使 items 到达返回边界/调用者。

> Return the search response's items value unchanged

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：本地写文件动作由代理运行时执行。

> write_total_to_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：将 total 写入本地 count.txt，使内容到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_013`。
  理由：写入本地文件 count.txt。

> write the response's total value to local count.txt

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_014`。
  理由：使 items 到达返回边界/调用者。

> Return the search response's items value unchanged

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
