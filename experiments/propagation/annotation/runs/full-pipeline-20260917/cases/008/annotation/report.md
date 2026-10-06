# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`486d8e42d991fb323a9c6d4fddb4b82e8f152da21693399b163958a09ec16324`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_016` / `effects`：return 仅表明将 items 交给调用方，未明确接收方是用户还是模型，无法确定 user_output 或 model_observe 是否适用。

## 按块查看

### block_001 · Read user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract request.term

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Check whether from_date is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | check_from_date_presence | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Extract from_date value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_from_date_value | agent_runtime | transformer | transform |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Check whether limit is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | check_limit_presence | agent_runtime | transformer | transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Extract limit value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | extract_limit_value | agent_runtime | transformer | transform |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Call index.search with request parameters

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | index.search | tool | source, sink | net_send, net_receive, model_observe |
| ir_014 | dispatch | llm | [] | [] |

### block_008 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | write_search_total_to_file | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为本地文件读取动作，由代理运行时执行。

> read_request_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部文件将数据引入当前过程。

> request.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取文件内容。

> read_request_file

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地字段提取由代理运行时执行。

> extract_request_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从请求数据中选择 term 字段，属处理/变换。

> extract_request_term

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取/选择字段改变内容表示或选择。

> extract_request_term

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地存在性检查由代理运行时执行。

> check_from_date_presence

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：检查字段是否存在并产生布尔结果，属处理/计算。

> check_from_date_presence

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：计算存在性结果属于变换。

> check_from_date_presence

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地字段提取由代理运行时执行。

> extract_from_date_value

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：从请求数据中选择 from_date 字段值，属处理/变换。

> extract_from_date_value

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：提取/选择字段改变内容表示或选择。

> extract_from_date_value

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地存在性检查由代理运行时执行。

> check_limit_presence

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：检查字段是否存在并产生布尔结果，属处理/计算。

> check_limit_presence

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：计算存在性结果属于变换。

> check_limit_presence

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地字段提取由代理运行时执行。

> extract_limit_value

- `roles` / `transformer`；依据 `cfg`，位置 `g_0039`。
  理由：从请求数据中选择 limit 字段值，属处理/变换。

> extract_limit_value

- `effects` / `transform`；依据 `cfg`，位置 `g_0039`。
  理由：提取/选择字段改变内容表示或选择。

> extract_limit_value

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0045`。
  理由：具体工具 index.search 执行该搜索调用。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0045`。
  理由：接收远端返回的 items/total 并引入当前过程。

> items

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：向外部服务发送查询参数，使内容到达接收方。

> service

- `effects` / `net_send`；依据 `cfg`，位置 `g_0045`。
  理由：调用外部服务发送请求/参数。

> service

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0045`。
  理由：接收远端返回内容。

> items

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 为工具调用，返回结果默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_014

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度/控制转移，LLM 可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制转移，不引入、输出或变换数据，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：本地写入动作由代理运行时执行。

> write_search_total_to_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：写入本地文件形成存储位置，使内容到达存储边界。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：创建/修改文件内容。

> write_search_total_to_file

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `source`，位置 `src_008`。
  理由：将 items 交给调用方/输出边界，使内容到达接收方。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
