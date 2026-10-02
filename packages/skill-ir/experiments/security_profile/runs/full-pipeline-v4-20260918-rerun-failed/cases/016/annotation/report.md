# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`e7e3d42c2280d4c534c66a0380c5727c1a69085f4ed426df4ca420b2724d882d`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_user_request | llm | source | context_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | source | context_read |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | fast.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Retry fast.fetch exactly once with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Call archive.fetch with source_id as its only argument

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | archive.fetch | tool | source, sink | net_send, net_receive, model_observe |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Append final status and return the first fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | append_final_status_to_local_status_txt | agent_runtime | sink | fs_write |
| ir_012 | return | llm | sink | [] |

### block_007 · Append final status and return the retried fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | append_final_status_to_local_status_txt | agent_runtime | sink | fs_write |
| ir_014 | return | llm | sink | [] |

### block_008 · Append final status and return the archive.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | append_final_status_to_local_status_txt | agent_runtime | sink | fs_write |
| ir_016 | return | llm | sink | [] |

### block_009 · Append final status and return the archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | append_final_status_to_local_status_txt | agent_runtime | sink | fs_write |
| ir_018 | return | llm | sink | [] |

## 标注依据

### ir_001

- `actor` / `llm`；依据 `cfg`，位置 `g_0009`。
  理由：该IR为工作流读取用户请求的步骤，执行该工作流的LLM参与读取。

> read_source_id_from_user_request

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从用户请求向当前过程引入source_id数据。

> source_id

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：该动作读取调用者输入或运行时上下文。

> read_source_id_from_user_request

- `effects` / `model_observe`；依据 `cfg`，位置 `g_0009`。
  理由：LLM读取用户请求内容，使内容进入模型处理上下文。

> read_source_id_from_user_request

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch为调度或控制转移，EM03表明LLM可参与调度。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制跳转，不引入、变换或送达内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表效果均不适用。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `execution_model`，位置 `EM04`。
  理由：读取环境变量FAST_KEY属于本地运行时上下文访问，由代理运行时执行。

> 本地处理与模型处理分开

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：从环境向当前过程引入FAST_KEY值。

> FAST_KEY

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：读取运行时环境上下文。

> read_fast_key_from_environment

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch为基于FAST_KEY存在性的调度或控制转移，LLM可参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分支，无数据角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：无内容读取、写入、变换、网络、模型观察或用户输出效果。

> dispatch

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：该IR opcode或外部资源为fast.fetch，执行者为该工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：工具返回body或error，向当前过程引入响应数据。

> fast_fetch_attempt_1_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0021`。
  理由：将source_id与FAST_KEY作为参数传给外部工具，内容到达接收方或边界。

> fast_key_value

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：凭据门控fetch工具接收source_id与FAST_KEY请求参数，构成外部请求发送。

> credential-gated preferred tool

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0021`。
  理由：输出response body或error，表明接收外部响应内容。

> fast_fetch_attempt_1_body

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch返回内容默认回传模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch为基于fast.fetch首次结果的调度或控制转移，LLM可参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分支，无数据角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：无内容效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该IR opcode或外部资源为fast.fetch，执行者为该工具。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：工具返回body或error，向当前过程引入响应数据。

> fast_fetch_retry_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：将source_id与FAST_KEY作为参数传给外部工具，内容到达接收方或边界。

> fast_key_value

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：凭据门控fetch工具接收source_id与FAST_KEY请求参数，构成外部请求发送。

> credential-gated preferred tool

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0027`。
  理由：输出response body或error，表明接收外部响应内容。

> fast_fetch_retry_body

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch返回内容默认回传模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch为基于fast.fetch重试结果的调度或控制转移，LLM可参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分支，无数据角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：无内容效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该IR opcode或外部资源为archive.fetch，执行者为该工具。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：工具返回body或error，向当前过程引入响应数据。

> archive_fetch_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：将source_id作为参数传给外部archive.fetch，内容到达接收方或边界。

> source_id_value

- `effects` / `net_send`；依据 `source`，位置 `src_001`。
  理由：archive.fetch作为取数回退工具，调用时传入source_id，构成外部请求发送。

> bounded archive fallback

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0033`。
  理由：输出response body或error，表明接收外部响应内容。

> archive_fetch_body

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：archive.fetch返回内容默认回传模型上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch为基于archive.fetch结果的调度或控制转移，LLM可参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分支，无数据角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：无内容效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `execution_model`，位置 `EM04`。
  理由：追加本地status.txt属于本地运行时文件操作。

> 本地处理与模型处理分开

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将状态写入本地文件存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0039`。
  理由：该动作向本地status.txt追加内容。

> append_final_status_to_local_status_txt

### ir_012

- `actor` / `llm`；依据 `source`，位置 `src_010`。
  理由：Skill指示工作流执行者返回响应体，LLM参与该返回动作。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_010`。
  理由：将成功响应体返回给调用方，内容到达接收方。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无直接用户输出证据，无其他词表效果。

> 普通 return 不能单独证明面向用户输出

### ir_013

- `actor` / `agent_runtime`；依据 `execution_model`，位置 `EM04`。
  理由：追加本地status.txt属于本地运行时文件操作。

> 本地处理与模型处理分开

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将状态写入本地文件存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：该动作向本地status.txt追加内容。

> append_final_status_to_local_status_txt

### ir_014

- `actor` / `llm`；依据 `source`，位置 `src_010`。
  理由：Skill指示工作流执行者返回响应体，LLM参与该返回动作。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_010`。
  理由：将成功响应体返回给调用方，内容到达接收方。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无直接用户输出证据，无其他词表效果。

> 普通 return 不能单独证明面向用户输出

### ir_015

- `actor` / `agent_runtime`；依据 `execution_model`，位置 `EM04`。
  理由：追加本地status.txt属于本地运行时文件操作。

> 本地处理与模型处理分开

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将状态写入本地文件存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：该动作向本地status.txt追加内容。

> append_final_status_to_local_status_txt

### ir_016

- `actor` / `llm`；依据 `source`，位置 `src_010`。
  理由：Skill指示工作流执行者返回响应体，LLM参与该返回动作。

> return that successful response's body value unchanged

- `roles` / `sink`；依据 `source`，位置 `src_010`。
  理由：将成功响应体返回给调用方，内容到达接收方。

> return that successful response's body value unchanged

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无直接用户输出证据，无其他词表效果。

> 普通 return 不能单独证明面向用户输出

### ir_017

- `actor` / `agent_runtime`；依据 `execution_model`，位置 `EM04`。
  理由：追加本地status.txt属于本地运行时文件操作。

> 本地处理与模型处理分开

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：将状态写入本地文件存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0057`。
  理由：该动作向本地status.txt追加内容。

> append_final_status_to_local_status_txt

### ir_018

- `actor` / `llm`；依据 `source`，位置 `src_011`。
  理由：Skill指示工作流执行者返回错误，LLM参与该返回动作。

> return its error

- `roles` / `sink`；依据 `source`，位置 `src_011`。
  理由：将archive.fetch错误返回给调用方，内容到达接收方。

> return its error

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return不必然面向用户输出，无其他词表效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
