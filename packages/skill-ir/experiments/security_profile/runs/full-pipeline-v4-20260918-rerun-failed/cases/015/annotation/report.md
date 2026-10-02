# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`9f79230a22497d54d2a8ceba8a14ec0d642e8b987b52fca16a6c81819026a3ea`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_007` / `effects`：无法确定是否发生 net_send/net_receive：CFG 仅记录 fast.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。
- `ir_011` / `effects`：无法确定是否发生 net_send/net_receive：CFG 仅记录 fast.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。
- `ir_015` / `effects`：无法确定是否发生 net_send/net_receive：CFG 仅记录 archive.fetch 工具名与 external_resource，Skill 未明确远程通信，EM06 禁止仅凭工具名推断远程网络。

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

### block_004 · Call fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast_fetch | tool | source, sink | model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Append final status and return the first fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | append_final_status_to_local_file | agent_runtime | sink | fs_write |
| ir_010 | return | agent_runtime | sink | [] |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | fast_fetch | tool | source, sink | model_observe |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Append final status and return the retry response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | append_final_status_to_local_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | sink | [] |

### block_008 · Call archive.fetch with source_id

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | archive_fetch | tool | source, sink | model_observe |
| ir_016 | dispatch | llm | [] | [] |

### block_009 · Append final status and return the archive.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | append_final_status_to_local_file | agent_runtime | sink | fs_write |
| ir_018 | return | agent_runtime | sink | [] |

### block_010 · Append final status and return the archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_local_file | agent_runtime | sink | fs_write |
| ir_020 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 从上下文读取 source_id，执行者为本地代理运行时。

> read_source_id_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从 user_request 引入 source_id 到当前过程。

> user_request

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取运行时上下文 user_request。

> read_source_id_from_request

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 从环境上下文读取 FAST_KEY，执行者为本地代理运行时。

> read_fast_key_from_environment

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：从环境引入 FAST_KEY 到当前过程。

> read FAST_KEY from the environment

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：动作读取运行时环境上下文。

> read_fast_key_from_environment

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 为本地检查动作，执行者为本地代理运行时。

> check_fast_key_present

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：将 FAST_KEY 处理为存在性布尔结果，属处理/变换。

> check_fast_key_present

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：生成 fast_key_present 布尔表示，属计算/改变表示。

> check_fast_key_present

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：外部资源 fast.fetch 执行该工具调用。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：工具返回 body/error 引入当前过程。

> first_fast_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：调用参数 source_id/fast_key 发往 fast.fetch，使内容到达该工具。

> fast_key

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch 返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_final_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：写入本地 status.txt 使内容到达存储位置。

> status.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加最终状态到本地文件，属文件内容写入。

> append the final status to local status.txt

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：返回控制动作由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0034`。
  理由：将 body 交回调用方，构成到达接收方/边界。

> first_fast_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无用户输出、网络、文件、模型观察或变换效果依据。

> 普通 return 不能单独证明面向用户输出

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：外部资源 fast.fetch 执行该工具调用。

> fast.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：工具返回 body/error 引入当前过程。

> retry_fast_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：调用参数 source_id/fast_key 发往 fast.fetch，使内容到达该工具。

> fast_key

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：fast.fetch 返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_final_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：写入本地 status.txt 使内容到达存储位置。

> status.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加最终状态到本地文件，属文件内容写入。

> append the final status to local status.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：返回控制动作由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0046`。
  理由：将 body 交回调用方，构成到达接收方/边界。

> retry_fast_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无用户输出、网络、文件、模型观察或变换效果依据。

> 普通 return 不能单独证明面向用户输出

### ir_015

- `actor` / `tool`；依据 `cfg`，位置 `g_0051`。
  理由：外部资源 archive.fetch 执行该工具调用。

> archive.fetch

- `roles` / `source`；依据 `cfg`，位置 `g_0051`。
  理由：工具返回 body/error 引入当前过程。

> archive_body

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：调用参数 source_id 发往 archive.fetch，使内容到达该工具。

> source_id

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：archive.fetch 返回内容默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_016

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 为调度动作，由 LLM 参与。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：仅控制流转，未引入、送出或变换内容，无 source/sink/transformer。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、网络、模型观察、用户输出或变换效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_final_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：写入本地 status.txt 使内容到达存储位置。

> status.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加最终状态到本地文件，属文件内容写入。

> append the final status to local status.txt

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：返回控制动作由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0058`。
  理由：将 body 交回调用方，构成到达接收方/边界。

> archive_body

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无用户输出、网络、文件、模型观察或变换效果依据。

> 普通 return 不能单独证明面向用户输出

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：本地文件追加动作由本地代理运行时执行。

> append_final_status_to_local_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0063`。
  理由：写入本地 status.txt 使内容到达存储位置。

> status.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：追加最终状态到本地文件，属文件内容写入。

> append the final status to local status.txt

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：返回控制动作由本地代理运行时执行。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0064`。
  理由：将 error 交回调用方，构成到达接收方/边界。

> archive_error

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无用户输出、网络、文件、模型观察或变换效果依据。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
