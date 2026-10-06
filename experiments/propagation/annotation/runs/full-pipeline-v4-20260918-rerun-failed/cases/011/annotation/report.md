# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`225d1248a792c18d51ded4987b7a8a85494a04290d5c6667c85d2014772add55`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_003` / `effects`：无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定
- `ir_005` / `effects`：无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定
- `ir_007` / `effects`：无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定
- `ir_009` / `effects`：无法从 index.search 工具名与现有 IR 判断是否进行远程通信，net_send/net_receive 不确定
- `ir_012` / `effects`：普通 return 无法确定接收方是否直接为用户，user_output 不确定

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_user_supplied_request_json | agent_runtime | source, transformer | fs_read, transform |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Call index.search with from_date and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | index.search | tool | source, sink, transformer | transform, model_observe |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Call index.search with from_date but without limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | index.search | tool | source, sink, transformer | transform, model_observe |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Call index.search without from_date but with limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | index.search | tool | source, sink, transformer | transform, model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Call index.search without from_date and without limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | index.search | tool | source, sink, transformer | transform, model_observe |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Return the search response's items value unchanged

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | extract_items_from_search_response | agent_runtime | transformer | transform |
| ir_012 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为读取本地 request.json 的文件操作，由代理运行时执行。

> read_user_supplied_request_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取 request.json 将外部请求数据引入当前过程。

> Read the user-supplied request.json

- `roles` / `transformer`；依据 `cfg`，位置 `g_0009`。
  理由：输出存在性布尔值等字段，包含计算/选择/表示改变。

> whether from_date is present

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：从 request.json 读取文件内容。

> Read the user-supplied request.json

- `effects` / `transform`；依据 `cfg`，位置 `g_0009`。
  理由：计算 from_date 是否存在并产出字段结果，属于 transform。

> whether from_date is present

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：条件分派为本地控制流，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分派不引入、处理或输出内容，无 source/sink/transformer 适用。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅根据存在性布尔值选择路径，未记录读取/写入/网络/模型/用户输出/变换效果。

> dispatch

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 调用外部工具 index.search，由工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：搜索响应作为工具结果引入当前过程。

> search response

- `roles` / `sink`；依据 `cfg`，位置 `g_0015`。
  理由：query 等参数被传给工具，到达接收方。

> query

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：工具对查询执行检索/选择。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：搜索是对查询的选择/计算操作。

> index.search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传至 LLM 上下文，搜索响应进入模型处理上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：条件分派为本地控制流，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分派不引入、处理或输出内容，无 source/sink/transformer 适用。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅根据存在性布尔值选择路径，未记录读取/写入/网络/模型/用户输出/变换效果。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 调用外部工具 index.search，由工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：搜索响应作为工具结果引入当前过程。

> search response

- `roles` / `sink`；依据 `cfg`，位置 `g_0021`。
  理由：query 等参数被传给工具，到达接收方。

> query

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：工具对查询执行检索/选择。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：搜索是对查询的选择/计算操作。

> index.search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传至 LLM 上下文，搜索响应进入模型处理上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：条件分派为本地控制流，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分派不引入、处理或输出内容，无 source/sink/transformer 适用。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅根据存在性布尔值选择路径，未记录读取/写入/网络/模型/用户输出/变换效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该 IR 调用外部工具 index.search，由工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：搜索响应作为工具结果引入当前过程。

> search response

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：query 等参数被传给工具，到达接收方。

> query

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：工具对查询执行检索/选择。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：搜索是对查询的选择/计算操作。

> index.search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传至 LLM 上下文，搜索响应进入模型处理上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：条件分派为本地控制流，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分派不引入、处理或输出内容，无 source/sink/transformer 适用。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅根据存在性布尔值选择路径，未记录读取/写入/网络/模型/用户输出/变换效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 调用外部工具 index.search，由工具执行搜索动作。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：搜索响应作为工具结果引入当前过程。

> search response

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：query 等参数被传给工具，到达接收方。

> query

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：工具对查询执行检索/选择。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：搜索是对查询的选择/计算操作。

> index.search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传至 LLM 上下文，搜索响应进入模型处理上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：条件分派为本地控制流，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分派不引入、处理或输出内容，无 source/sink/transformer 适用。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅根据存在性布尔值选择路径，未记录读取/写入/网络/模型/用户输出/变换效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：该 IR 为本地提取 items 的数据操作，由代理运行时执行。

> extract_items_from_search_response

- `roles` / `transformer`；依据 `cfg`，位置 `g_0039`。
  理由：从搜索响应中提取 items，属于选择/改变表示。

> extract_items_from_search_response

- `effects` / `transform`；依据 `cfg`，位置 `g_0039`。
  理由：提取 items 字段是对搜索响应的选择/表示改变。

> extract_items_from_search_response

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：返回调用方的控制动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0040`。
  理由：将 items 返回给调用方，使内容到达接收边界；未证明直接面向用户。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
