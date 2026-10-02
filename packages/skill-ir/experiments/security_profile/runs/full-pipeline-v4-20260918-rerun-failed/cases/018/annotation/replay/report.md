# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`f47fb1a92cfa2a55ae485abd344b1943853cfb823e1de444ecad7e5cc8fac1d7`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_007` / `effects`：图仅记录fast.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。
- `ir_009` / `effects`：图仅记录fast.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。
- `ir_011` / `effects`：图仅记录archive.fetch为external_resource，未记录远端通信端点或网络机制，无法确定是否net_send/net_receive；依EM06不据工具名猜测。

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_request | agent_runtime | source | context_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | source | context_read |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_present | agent_runtime | [] | [] |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | tool | source, sink | model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | fast.fetch | tool | source, sink | model_observe |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Call archive.fetch with source_id

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | archive.fetch | tool | source, sink | model_observe |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_007 · Return the first fast.fetch summary and record success

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | extract_response_summary | agent_runtime | transformer | transform |
| ir_014 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_015 | return | agent_runtime | sink | [] |

### block_008 · Return the retry fast.fetch summary and record success

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | extract_response_summary | agent_runtime | transformer | transform |
| ir_017 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_018 | return | agent_runtime | sink | [] |

### block_009 · Return the archive.fetch summary and record success

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | extract_response_summary | agent_runtime | transformer | transform |
| ir_020 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_021 | return | agent_runtime | sink | [] |

### block_010 · Return the archive.fetch error and record failure

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | append_final_status_to_status_file | agent_runtime | sink | fs_write |
| ir_023 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该IR为读取请求上下文的运行时动作，由本地代理运行时执行。

> read_source_id_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从请求上下文读取source_id并将结果引入当前过程。

> source_id

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：输入类型为context_key，属于取得调用者输入或运行时上下文。

> context_key

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该IR为读取环境变量的运行时动作，由本地代理运行时执行。

> read_fast_key_from_environment

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：读取环境值并将FAST_KEY引入当前过程。

> FAST_KEY

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：输入类型为context_key，属于取得运行时环境上下文。

> context_key

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：存在性检查由本地代理运行时执行。

> check_fast_key_present

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0021`。
  理由：仅判断存在性用于分支，不引入、发送或变换内容。

> check_fast_key_present

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0021`。
  理由：纯控制条件检查，词表未覆盖为内容效果。

> check_fast_key_present

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该IR为fast.fetch工具调用，动作由工具执行。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：工具调用产生响应/错误结果，向当前过程引入工具返回内容。

> first_fast_fetch_response

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：调用参数被送至external_resource工具边界，内容到达接收方。

> external_resource

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认回传LLM上下文，形成模型观察。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该IR为fast.fetch工具重试调用，动作由工具执行。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：工具调用产生响应/错误结果，向当前过程引入工具返回内容。

> retry_fast_fetch_response

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：调用参数被送至external_resource工具边界，内容到达接收方。

> external_resource

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认回传LLM上下文，形成模型观察。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：该IR为archive.fetch工具调用，动作由工具执行。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：工具调用产生响应/错误结果，向当前过程引入工具返回内容。

> archive_fetch_response

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：调用参数被送至external_resource工具边界，内容到达接收方。

> external_resource

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容默认回传LLM上下文，形成模型观察。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch是控制流转移，由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制流转移，不向过程引入、发送或存储内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制流转移，无词表内读取、写入、网络、模型观察或变换效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：该IR为本地摘要提取动作，由代理运行时执行。

> extract_response_summary

- `roles` / `transformer`；依据 `cfg`，位置 `g_0045`。
  理由：从响应中提取摘要，处理并改变内容表示。

> extract_response_summary

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：摘要提取属于本地处理，标注transform。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：追加本地文件由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0046`。
  理由：将状态追加到本地文件，使内容到达存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0046`。
  理由：追加写入状态到本地文件，属于修改文件内容。

> append_final_status_to_status_file

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0047`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0047`。
  理由：将摘要返回给调用方，使内容到达接收边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return未证明直接展示给用户，且无其他词表内效果。

> 普通 return 不能单独证明面向用户输出

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：该IR为本地摘要提取动作，由代理运行时执行。

> extract_response_summary

- `roles` / `transformer`；依据 `cfg`，位置 `g_0052`。
  理由：从响应中提取摘要，处理并改变内容表示。

> extract_response_summary

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：摘要提取属于本地处理，标注transform。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0053`。
  理由：追加本地文件由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0053`。
  理由：将状态追加到本地文件，使内容到达存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0053`。
  理由：追加写入状态到本地文件，属于修改文件内容。

> append_final_status_to_status_file

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0054`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0054`。
  理由：将摘要返回给调用方，使内容到达接收边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return未证明直接展示给用户，且无其他词表内效果。

> 普通 return 不能单独证明面向用户输出

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0059`。
  理由：该IR为本地摘要提取动作，由代理运行时执行。

> extract_response_summary

- `roles` / `transformer`；依据 `cfg`，位置 `g_0059`。
  理由：从响应中提取摘要，处理并改变内容表示。

> extract_response_summary

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：摘要提取属于本地处理，标注transform。

> 本地字段筛选、遮蔽、加密、摘要等标注 transform

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0060`。
  理由：追加本地文件由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0060`。
  理由：将状态追加到本地文件，使内容到达存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0060`。
  理由：追加写入状态到本地文件，属于修改文件内容。

> append_final_status_to_status_file

### ir_021

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0061`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0061`。
  理由：将摘要返回给调用方，使内容到达接收边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return未证明直接展示给用户，且无其他词表内效果。

> 普通 return 不能单独证明面向用户输出

### ir_022

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0066`。
  理由：追加本地文件由代理运行时执行。

> append_final_status_to_status_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0066`。
  理由：将失败状态追加到本地文件，使内容到达存储位置。

> local status.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0066`。
  理由：追加写入状态到本地文件，属于修改文件内容。

> append_final_status_to_status_file

### ir_023

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0067`。
  理由：返回动作由代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0067`。
  理由：将错误返回给调用方，使内容到达接收边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return未证明直接展示给用户，且无其他词表内效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
