# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`ac4801c39e5d80d8c6ab91c27dcb53d21bc612b79d4469f14e4a1f6df0516dd7`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_012` / `effects`：无法确定 index.search 是否为远端网络服务；工具名和外部资源标识不足以证明 net_send/net_receive。
- `ir_017` / `effects`：普通 return 不能单独证明面向用户输出，无法确定是否产生 user_output。

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract term and check whether from_date is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | agent_runtime | transformer | transform |
| ir_004 | check_from_date_presence | agent_runtime | transformer | transform |
| ir_005 | dispatch | llm | [] | [] |

### block_003 · Pass from_date value unchanged when present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_006 | extract_from_date_value | agent_runtime | transformer | transform |
| ir_007 | dispatch | llm | [] | [] |

### block_004 · Check whether limit is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | check_limit_presence | agent_runtime | transformer | transform |
| ir_009 | dispatch | llm | [] | [] |

### block_005 · Pass limit value unchanged when present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | extract_limit_value | agent_runtime | transformer | transform |
| ir_011 | dispatch | llm | [] | [] |

### block_006 · Call index.search exactly once

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | index.search | tool | source, sink, transformer | transform, model_observe |
| ir_013 | dispatch | llm | [] | [] |

### block_007 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | extract_response_total | agent_runtime | transformer | transform |
| ir_015 | write_count_file | agent_runtime | sink | fs_write |
| ir_016 | extract_response_items | agent_runtime | transformer | transform |
| ir_017 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为本地读取 request.json 的动作，执行者为本地代理运行时。

> read_request_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部 request.json 会把请求数据引入当前过程，故为 source。

> request.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表示读取文件内容，产生 fs_read 效果。

> read_request_json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 为本地字段提取动作，由本地代理运行时执行。

> extract_request_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：提取字段属于处理/变换内容，扮演 transformer 角色。

> extract_request_term

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取字段属于计算/选择/改变表示，产生 transform 效果。

> extract_request_term

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：该 IR 为本地存在性检查动作，由本地代理运行时执行。

> check_from_date_presence

- `roles` / `transformer`；依据 `cfg`，位置 `g_0016`。
  理由：检查存在性并生成布尔结果，属于处理/变换内容。

> check_from_date_presence

- `effects` / `transform`；依据 `cfg`，位置 `g_0016`。
  理由：检查存在性属于计算/选择，产生 transform 效果。

> check_from_date_presence

### ir_005

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0017`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0017`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：该 IR 为本地字段提取动作，由本地代理运行时执行。

> extract_from_date_value

- `roles` / `transformer`；依据 `cfg`，位置 `g_0022`。
  理由：提取字段属于处理/变换内容，扮演 transformer 角色。

> extract_from_date_value

- `effects` / `transform`；依据 `cfg`，位置 `g_0022`。
  理由：提取字段属于计算/选择/改变表示，产生 transform 效果。

> extract_from_date_value

### ir_007

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0023`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0023`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：该 IR 为本地存在性检查动作，由本地代理运行时执行。

> check_limit_presence

- `roles` / `transformer`；依据 `cfg`，位置 `g_0028`。
  理由：检查存在性并生成布尔结果，属于处理/变换内容。

> check_limit_presence

- `effects` / `transform`；依据 `cfg`，位置 `g_0028`。
  理由：检查存在性属于计算/选择，产生 transform 效果。

> check_limit_presence

### ir_009

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0029`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：该 IR 为本地字段提取动作，由本地代理运行时执行。

> extract_limit_value

- `roles` / `transformer`；依据 `cfg`，位置 `g_0034`。
  理由：提取字段属于处理/变换内容，扮演 transformer 角色。

> extract_limit_value

- `effects` / `transform`；依据 `cfg`，位置 `g_0034`。
  理由：提取字段属于计算/选择/改变表示，产生 transform 效果。

> extract_limit_value

### ir_011

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0035`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0035`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_012

- `actor` / `tool`；依据 `cfg`，位置 `g_0040`。
  理由：opcode 与外部资源名表明该搜索动作由 index.search 工具执行。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0040`。
  理由：该动作输出 search_response，向当前过程引入搜索结果内容。

> search_response

- `roles` / `sink`；依据 `cfg`，位置 `g_0040`。
  理由：查询参数作为输入传给 index.search，使内容到达工具接收边界。

> request_term

- `roles` / `transformer`；依据 `cfg`，位置 `g_0040`。
  理由：搜索动作对查询参数执行匹配/选择并生成响应，属于内容变换。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0040`。
  理由：搜索执行计算/选择并生成响应，产生 transform 效果。

> index.search

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传 LLM 上下文，故搜索响应进入模型处理上下文。

> 默认进入 LLM 上下文

### ir_013

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该规则承认存在 LLM 调度；dispatch 是调度控制动作，故 llm 可标为参与者，但仅调度不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0041`。
  理由：纯调度控制不引入、变换或使内容到达接收方/存储位置，无适用 roles。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0041`。
  理由：纯调度控制不产生读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：该 IR 为本地字段提取动作，由本地代理运行时执行。

> extract_response_total

- `roles` / `transformer`；依据 `cfg`，位置 `g_0046`。
  理由：提取字段属于处理/变换内容，扮演 transformer 角色。

> extract_response_total

- `effects` / `transform`；依据 `cfg`，位置 `g_0046`。
  理由：提取字段属于计算/选择/改变表示，产生 transform 效果。

> extract_response_total

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0047`。
  理由：该 IR 为本地写文件动作，由本地代理运行时执行。

> write_count_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0047`。
  理由：该动作将内容写入本地 count.txt，到达存储位置。

> count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0047`。
  理由：opcode 表示创建或修改文件内容，产生 fs_write 效果。

> write_count_file

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0048`。
  理由：该 IR 为本地字段提取动作，由本地代理运行时执行。

> extract_response_items

- `roles` / `transformer`；依据 `cfg`，位置 `g_0048`。
  理由：提取字段属于处理/变换内容，扮演 transformer 角色。

> extract_response_items

- `effects` / `transform`；依据 `cfg`，位置 `g_0048`。
  理由：提取字段属于计算/选择/改变表示，产生 transform 效果。

> extract_response_items

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0049`。
  理由：该 IR 为流程返回控制动作，由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0049`。
  理由：返回动作将结果交给调用方，形成接收边界，故为 sink。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
