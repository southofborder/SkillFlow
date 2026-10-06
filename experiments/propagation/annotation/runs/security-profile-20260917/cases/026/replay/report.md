# 安全语义标注：026

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`2bcf7673311de256277c489d9b135ef6de48f8c924968fd87226564bd1fc9748`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_013` / `effects`：未给出具体交互命令、输入数据或是否提交/导航，无法确定是否触发远端网络发送或接收。
- `ir_021` / `effects`：cli_args 未指定具体子命令，npx 也可能使用缓存，无法确定是否触发远端网络发送或接收。

## 按块查看

### block_001 · Check whether npx is available

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | check_npx_available | agent_runtime | source | context_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Ask the user to install Node.js/npm

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | ask_user_to_install_node | llm | sink | user_output |
| ir_004 | return | agent_runtime | [] | [] |

### block_003 · Resolve the bundled Playwright CLI wrapper path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | resolve_playwright_cli_wrapper_path | agent_runtime | source, transformer | context_read, transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Read the target page URL from the task

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | read_target_url_from_task | agent_runtime | source | context_read |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Open the target page in the browser

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | open_page | tool | source, sink | net_send, net_receive |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Snapshot the page to obtain stable element refs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | take_page_snapshot | tool | source, transformer, sink | transform, model_observe |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Interact with the page using refs from the latest snapshot

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | interact_with_element_refs | tool | sink | [] |
| ir_014 | dispatch | llm | [] | [] |

### block_008 · Re-snapshot after navigation or significant DOM changes

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | take_page_snapshot | tool | source, transformer, sink | transform, model_observe |
| ir_016 | dispatch | llm | [] | [] |

### block_009 · Capture browser artifacts when useful

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | capture_browser_artifacts | tool | source, transformer, sink | fs_write, transform |
| ir_018 | return | agent_runtime | [] | [] |

### block_010 · Read wrapper arguments and session environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | read_wrapper_arguments_and_session | agent_runtime | source | context_read |
| ir_020 | dispatch | llm | [] | [] |

### block_011 · Execute playwright-cli through npx

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | run_playwright_cli_wrapper | tool | source, sink | [] |
| ir_022 | return | agent_runtime | sink | model_observe |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该本地检查由代理运行时执行。

> check_npx_available

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取 PATH 上下文键，向当前过程引入运行时环境数据。

> PATH

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：取得 PATH 运行时上下文以判断 npx 是否可用。

> PATH

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `llm`；依据 `cfg`，位置 `g_0015`。
  理由：该动作生成并发出面向用户的安装请求，由模型参与。

> ask_user_to_install_node

- `roles` / `sink`；依据 `cfg`，位置 `g_0015`。
  理由：动作使安装步骤内容到达用户可见边界。

> ask the user to install Node.js/npm

- `effects` / `user_output`；依据 `cfg`，位置 `g_0015`。
  理由：直接向用户展示或提供安装步骤。

> ask the user to install Node.js/npm

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：该返回指令由本地运行时执行，结束安装请求分支。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：无输入输出内容，未引入、到达或变换数据。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅返回控制，未记录文件、网络、模型观察、用户输出或变换效果。

> return

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地运行时解析 wrapper 路径并设置环境变量。

> resolve_playwright_cli_wrapper_path

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：读取 CODEX_HOME/HOME 以引入路径上下文。

> CODEX_HOME

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：根据环境变量计算并设置 PWCLI 路径，改变路径表示。

> PWCLI

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：读取运行时上下文键 CODEX_HOME/HOME。

> CODEX_HOME

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：解析默认值并拼接 wrapper 路径，属于计算和组合。

> PWCLI

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该动作由本地运行时从任务上下文读取目标 URL。

> read_target_url_from_task

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：从调用者任务上下文引入目标 URL 数据。

> target_url

- `effects` / `context_read`；依据 `cfg`，位置 `g_0027`。
  理由：取得运行时调用者输入 target_url。

> target_url

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：通过 wrapper/CLI 工具驱动浏览器打开页面。

> playwright_cli_wrapper

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：向目标 URL 发起导航请求，使请求到达远端。

> target_page_url

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：浏览器加载目标页面会接收远端内容并引入过程。

> open_page

- `effects` / `net_send`；依据 `cfg`，位置 `g_0033`。
  理由：打开页面会向远端发送 HTTP 请求。

> target_page_url

- `effects` / `net_receive`；依据 `cfg`，位置 `g_0033`。
  理由：加载目标页面会接收远端响应内容。

> open_page

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：快照由浏览器自动化工具执行。

> take_page_snapshot

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：从当前页面提取元素引用并引入过程结果。

> element_refs

- `roles` / `transformer`；依据 `cfg`，位置 `g_0039`。
  理由：将页面状态转换为稳定元素引用表示。

> take_page_snapshot

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：快照结果默认回传模型上下文，到达模型可见边界。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0039`。
  理由：生成元素引用是对页面内容的表示变换。

> take_page_snapshot

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回的 element_refs 默认进入模型处理上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0045`。
  理由：浏览器自动化工具执行元素交互。

> interact_with_element_refs

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：交互命令送入浏览器页面边界，使内容到达接收方。

> interact_with_element_refs

### ir_014

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_015

- `actor` / `tool`；依据 `cfg`，位置 `g_0051`。
  理由：重新快照由浏览器自动化工具执行。

> take_page_snapshot

- `roles` / `source`；依据 `cfg`，位置 `g_0051`。
  理由：从更新后的页面提取元素引用并引入过程结果。

> updated_element_refs

- `roles` / `transformer`；依据 `cfg`，位置 `g_0051`。
  理由：将更新后的页面状态转换为元素引用表示。

> take_page_snapshot

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：更新后的快照结果默认回传模型上下文，到达模型可见边界。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0051`。
  理由：生成更新后的元素引用是对页面内容的表示变换。

> take_page_snapshot

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回的 updated_element_refs 默认进入模型处理上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_016

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_017

- `actor` / `tool`；依据 `cfg`，位置 `g_0057`。
  理由：浏览器自动化工具捕获产物。

> capture_browser_artifacts

- `roles` / `source`；依据 `cfg`，位置 `g_0057`。
  理由：从浏览器页面捕获产物并引入过程结果。

> capture_browser_artifacts

- `roles` / `transformer`；依据 `cfg`，位置 `g_0055`。
  理由：将页面状态转换为截图、PDF 或 trace 表示。

> screenshot

- `roles` / `sink`；依据 `cfg`，位置 `g_0055`。
  理由：产物写入指定输出目录，到达存储位置。

> output/playwright/

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0055`。
  理由：约束要求产物写入该目录，创建文件内容。

> output/playwright/

- `effects` / `transform`；依据 `cfg`，位置 `g_0055`。
  理由：截图、PDF 或 trace 属于表示转换。

> screenshot

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：本地运行时执行返回，结束捕获块。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：返回无输入输出内容，不引入、到达或变换数据。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：仅控制返回，未记录文件、网络、模型观察、用户输出或变换效果。

> return

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：本地运行时读取 wrapper 参数和会话环境。

> read_wrapper_arguments_and_session

- `roles` / `source`；依据 `cfg`，位置 `g_0063`。
  理由：从命令行参数引入参数数据。

> command_line_args

- `effects` / `context_read`；依据 `cfg`，位置 `g_0063`。
  理由：读取会话环境变量和调用参数等运行时上下文。

> PLAYWRIGHT_CLI_SESSION

### ir_020

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：该指令为分支调度，LLM 参与选择后续块；调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：纯控制分支，不引入、到达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：仅控制路由，未记录文件、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_021

- `actor` / `tool`；依据 `cfg`，位置 `g_0069`。
  理由：npx/playwright-cli 工具执行 wrapper。

> playwright-cli

- `roles` / `source`；依据 `cfg`，位置 `g_0069`。
  理由：执行命令产生 CLI 输出并引入结果。

> cli_output

- `roles` / `sink`；依据 `cfg`，位置 `g_0069`。
  理由：参数传入 npx/playwright-cli 执行边界。

> cli_args

### ir_022

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0070`。
  理由：本地运行时执行 wrapper 返回控制。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0070`。
  理由：返回 cli_output，使内容到达调用方或模型边界。

> cli_output

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：wrapper 返回的 cli_output 默认进入模型处理上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
