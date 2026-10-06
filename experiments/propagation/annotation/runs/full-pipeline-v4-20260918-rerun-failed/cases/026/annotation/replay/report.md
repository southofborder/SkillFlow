# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`e90cb6ac662842e7465769f697da4308338388b9d67b7ca2d0624926a24a210a`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_019` / `effects`：IR只记录click/type/press/fill，未指明是否提交表单或触发远端请求，无法确定net_send/net_receive是否发生。

## 按块查看

### block_001 · Check whether npx is available

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | check_npx_availability | agent_runtime | source, transformer | context_read, transform |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Ask the user to install Node.js/npm

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | ask_user_to_install_nodejs | llm | sink | user_output |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Set the bundled Playwright CLI wrapper path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | set_playwright_cli_wrapper_path | agent_runtime | source, transformer | context_read, transform |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Read the optional Playwright CLI session name

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | read_playwright_cli_session | agent_runtime | source | context_read |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Choose reference guides to open as needed

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | assess_reference_need | llm | [] | [] |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Read the CLI command reference

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | read_reference_guide | agent_runtime, llm | source, sink | fs_read, model_observe |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_007 · Read the workflows and troubleshooting reference

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | read_reference_guide | agent_runtime, llm | source, sink | fs_read, model_observe |
| ir_014 | dispatch | agent_runtime | [] | [] |

### block_008 · Open the target browser page

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | execute_playwright_cli_wrapper | agent_runtime, tool | source, sink | net_send, net_receive |
| ir_016 | dispatch | agent_runtime | [] | [] |

### block_009 · Snapshot the page to obtain stable element refs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | execute_playwright_cli_wrapper | agent_runtime, tool, llm | source, transformer, sink | context_read, transform, model_observe |
| ir_018 | dispatch | agent_runtime | [] | [] |

### block_010 · Interact with the page using refs from the latest snapshot

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | execute_playwright_cli_wrapper | agent_runtime, tool, llm | sink | model_observe |
| ir_020 | dispatch | agent_runtime | [] | [] |

### block_011 · Determine whether another snapshot is needed

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | assess_need_for_resnapshot | llm | [] | [] |
| ir_022 | dispatch | agent_runtime | [] | [] |

### block_012 · Determine whether capturing artifacts is useful

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_023 | assess_artifact_usefulness | llm | [] | [] |
| ir_024 | dispatch | agent_runtime | [] | [] |

### block_013 · Capture browser artifacts when useful

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_025 | execute_playwright_cli_wrapper | agent_runtime, tool | source, sink, transformer | context_read, fs_write, transform |
| ir_026 | dispatch | agent_runtime | [] | [] |

### block_014 · Finish the browser workflow

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_027 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：本地可用性检查由代理运行时执行。

> check_npx_availability

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取PATH并把运行时环境引入当前检查过程。

> PATH

- `roles` / `transformer`；依据 `cfg`，位置 `g_0009`。
  理由：根据环境值计算npx是否可用的结果。

> npx_available

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取PATH环境上下文。

> PATH

- `effects` / `transform`；依据 `cfg`，位置 `g_0009`。
  理由：由环境信息计算可用性布尔结果。

> npx_available

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_003

- `actor` / `llm`；依据 `source`，位置 `src_045`。
  理由：Skill指示代理向用户发起安装说明，模型执行该用户交互。

> pause and ask the user to install Node.js/npm

- `roles` / `sink`；依据 `cfg`，位置 `g_0015`。
  理由：动作把安装步骤提供给用户，到达可见边界。

> ask_user_to_install_nodejs

- `effects` / `user_output`；依据 `source`，位置 `src_045`。
  理由：要求向用户逐字提供步骤，属于直接面向用户输出。

> Provide these steps verbatim:

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：本地运行时设置wrapper路径变量。

> set_playwright_cli_wrapper_path

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：读取CODEX_HOME等环境值并引入过程。

> CODEX_HOME

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：组合环境值计算wrapper路径。

> pwcli_path

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：读取HOME等环境上下文。

> HOME

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：计算并生成PWCLI路径表示。

> pwcli_path

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地运行时读取会话环境变量。

> read_playwright_cli_session

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：读取的环境变量值引入当前过程。

> PLAYWRIGHT_CLI_SESSION

- `effects` / `context_read`；依据 `cfg`，位置 `g_0027`。
  理由：取得运行时环境上下文。

> PLAYWRIGHT_CLI_SESSION

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_009

- `actor` / `llm`；依据 `cfg`，位置 `g_0033`。
  理由：该IR是模型对是否读取参考的判断。

> assess_reference_need

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0033`。
  理由：纯决策，不引入、送达或变换内容。

> assess_reference_need

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：仅选择参考，不产生内容读写或模型观察效果。

> LLM 调度不等于内容可见

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：运行时读取参考文件。

> read_reference_guide

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果进入模型上下文，模型参与处理。

> 默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：引入指定参考文件内容。

> references/cli.md

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：内容到达模型上下文边界。

> 默认进入 LLM 上下文

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0039`。
  理由：读取指定参考文件内容。

> references/cli.md

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：参考内容进入模型处理上下文。

> 默认进入 LLM 上下文

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：运行时读取参考文件。

> read_reference_guide

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果进入模型上下文，模型参与处理。

> 默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0045`。
  理由：引入指定参考文件内容。

> references/workflows.md

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：内容到达模型上下文边界。

> 默认进入 LLM 上下文

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0045`。
  理由：读取指定参考文件内容。

> references/workflows.md

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：参考内容进入模型处理上下文。

> 默认进入 LLM 上下文

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：运行时执行wrapper脚本。

> execute_playwright_cli_wrapper

- `actor` / `tool`；依据 `cfg`，位置 `g_0051`。
  理由：脚本调用playwright-cli工具。

> playwright-cli

- `roles` / `sink`；依据 `source`，位置 `src_053`。
  理由：open向远端目标发出请求，内容到达远端。

> "$PWCLI" open https://playwright.dev --headed

- `roles` / `source`；依据 `source`，位置 `src_053`。
  理由：open接收远端页面内容进入浏览器会话过程。

> "$PWCLI" open https://playwright.dev --headed

- `effects` / `net_send`；依据 `source`，位置 `src_053`。
  理由：打开远端URL发送网络请求和参数。

> "$PWCLI" open https://playwright.dev --headed

- `effects` / `net_receive`；依据 `source`，位置 `src_053`。
  理由：打开页面接收远端响应内容。

> "$PWCLI" open https://playwright.dev --headed

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_017

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0057`。
  理由：运行时执行wrapper脚本。

> execute_playwright_cli_wrapper

- `actor` / `tool`；依据 `cfg`，位置 `g_0057`。
  理由：脚本调用playwright-cli工具执行快照。

> playwright-cli

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：快照结果进入模型上下文，模型参与处理。

> 默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0057`。
  理由：从浏览器会话取得页面状态并引入过程。

> browser_session

- `roles` / `transformer`；依据 `source`，位置 `src_057`。
  理由：将页面状态转换为稳定引用。

> Snapshot to get stable element refs.

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：快照内容到达模型上下文边界。

> 默认进入 LLM 上下文

- `effects` / `context_read`；依据 `cfg`，位置 `g_0057`。
  理由：取得浏览器会话运行时上下文。

> browser_session

- `effects` / `transform`；依据 `source`，位置 `src_057`。
  理由：生成快照和引用表示，属于变换。

> Snapshot to get stable element refs.

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：快照结果进入模型处理上下文。

> 默认进入 LLM 上下文

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0058`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_019

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0063`。
  理由：运行时执行交互wrapper脚本。

> execute_playwright_cli_wrapper

- `actor` / `tool`；依据 `cfg`，位置 `g_0063`。
  理由：脚本调用playwright-cli工具执行浏览器交互。

> playwright-cli

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：交互结果进入模型上下文，模型参与处理。

> 默认进入 LLM 上下文

- `roles` / `sink`；依据 `execution_model`，位置 `EM02`。
  理由：交互结果到达模型上下文边界。

> 默认进入 LLM 上下文

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：交互结果进入模型处理上下文。

> 默认进入 LLM 上下文

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0064`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_021

- `actor` / `llm`；依据 `cfg`，位置 `g_0069`。
  理由：该IR是模型对是否重新快照的判断。

> assess_need_for_resnapshot

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0069`。
  理由：纯控制决策，不引入、送达或变换内容。

> assess_need_for_resnapshot

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：仅决定是否循环，不产生内容效果。

> LLM 调度不等于内容可见

### ir_022

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0070`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0070`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0070`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_023

- `actor` / `llm`；依据 `cfg`，位置 `g_0075`。
  理由：该IR是模型对是否捕获产物的判断。

> assess_artifact_usefulness

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0075`。
  理由：纯决策，不引入、送达或变换内容。

> assess_artifact_usefulness

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：仅选择是否捕获，不产生内容效果。

> LLM 调度不等于内容可见

### ir_024

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0076`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0076`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0076`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_025

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0081`。
  理由：运行时执行wrapper脚本。

> execute_playwright_cli_wrapper

- `actor` / `tool`；依据 `cfg`，位置 `g_0081`。
  理由：脚本调用playwright-cli工具捕获产物。

> playwright-cli

- `roles` / `source`；依据 `cfg`，位置 `g_0081`。
  理由：从浏览器会话取得页面状态作为产物内容来源。

> browser_session

- `roles` / `sink`；依据 `cfg`，位置 `g_0081`。
  理由：将产物写入指定存储位置。

> output/playwright/

- `roles` / `transformer`；依据 `source`，位置 `src_057`。
  理由：把页面状态转换为截图、PDF或trace表示。

> Capture artifacts (screenshot, pdf, traces) when useful.

- `effects` / `context_read`；依据 `cfg`，位置 `g_0081`。
  理由：读取浏览器会话状态以捕获产物。

> browser_session

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0081`。
  理由：在输出目录创建产物文件。

> output/playwright/

- `effects` / `transform`；依据 `source`，位置 `src_057`。
  理由：生成不同表示的产物。

> Capture artifacts (screenshot, pdf, traces) when useful.

### ir_026

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0082`。
  理由：dispatch是控制流路由，由代理运行时调度。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0082`。
  理由：纯控制路由，不引入、送达或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0082`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_027

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0087`。
  理由：return结束流程，由运行时控制。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0087`。
  理由：纯控制返回，不引入、送达或变换内容。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：return未被证明为面向用户输出或其他内容效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
