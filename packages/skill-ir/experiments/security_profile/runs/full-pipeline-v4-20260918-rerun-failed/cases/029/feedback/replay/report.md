# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：findings do not cover controlled units: ['fact:/blocks/6/instructions/0/constraints/0', 'fact:/constraints/14', 'fact:/constraints/15', 'fact:/constraints/18']

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 遗漏 8；保留（模型判定） 10；错转 1 | {"actionable_ids": ["finding_1", "finding_5", "finding_7", "finding_10", "finding_14", "finding_15", "finding_17", "finding_20", "finding_23"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_6", "finding_9", "finding_11", "finding_12", "finding_13", "finding_16", "finding_18", "finding_19"]}, "revision": 0, "semantic_items": 19, "status": "revise", "unknown_ids": []} |
| 1 | audit_error | 无有效业务核对项 | {"reason": "findings do not cover controlled units: ['fact:/blocks/6/instructions/0/constraints/0', 'fact:/constraints/14', 'fact:/constraints/15', 'fact:/constraints/18']", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_1 · 遗漏

原文要求：SKILL.md 前置元数据声明技能名 linear，描述在用户想要在 Linear 中读取、创建或更新 ticket 时使用；agents/openai.yaml 还声明 display_name、short_description、icon 和 default_prompt（使用 Linear 上下文 triage/update 并给出 next actions）。

当前回述：受控回述有入口读取 user_request 和 Linear 工作流，但未记录技能名、description、short-description、display_name、default_prompt 等触发/接口元数据。

差异理由：触发/使用范围属于源文语义元数据；当前只保留工作流步骤，无法从受控事实核对该 Skill 的使用条件和默认接口提示。

源文：`SKILL.md:1-6`（`src_034`）。

> name: linear

源文：`agents/openai.yaml:1-6`（`src_060`）。

> default_prompt: "Use Linear context to triage or update relevant issues for this task, with clear next actions."

受控事实：`fact:/entry`, `fact:/contexts`

程序映射的当前图位置：`/entry_block_id`, `/declared_context_keys`

修改建议：在入口上下文或技能元数据中补充 name、description/触发范围、short-description 与 default_prompt。

依据：这些是源文声明的使用触发和默认提示，缺失后无法从受控回述核对何时使用该 Skill。

当前目标事实：`fact:/contexts`

当前目标图位置：`/declared_context_keys`

### finding_5 · 遗漏

原文要求：Step 0 要求在 Linear MCP 尚未配置时进行设置；并在任何 MCP 调用因 MCP 未连接而失败时暂停并设置。

当前回述：受控回述把 Step0/失败设置文本记录为 /constraints/3、/constraints/4 和 block_007 的块约束，且 block_007 含 add/enable/login 操作；但控制流只在 read 失败边 edge3 和 write 失败边 edge5 进入 block_007，没有入口前或调用前的 not already configured 条件边，也没有覆盖其他 MCP 调用（如 login）失败的通用分支。

差异理由：要求文本被声明，但条件触发和作用域不完整；初始化设置分支缺失，失败触发仅覆盖读写两类调用。

源文：`SKILL.md:22-22`（`src_041`）。

> ### Step 0: Set up Linear MCP (if not already configured)

源文：`SKILL.md:24-24`（`src_042`）。

> If any MCP call fails because Linear MCP is not connected, pause and set it up:

受控事实：`fact:/constraints/3`, `fact:/constraints/4`, `fact:/blocks/6/constraints/0`, `fact:/blocks/6/constraints/1`, `fact:/edges/3`, `fact:/edges/5`

程序映射的当前图位置：`/constraints/3`, `/constraints/4`, `/blocks/block_007/constraints/0`, `/blocks/block_007/constraints/1`, `/edges/3`, `/edges/5`

修改建议：为 block_007 增加由入口或调用前触发的 not already configured 条件边/guard，并补充通用 MCP 调用失败进入设置块的分支。

依据：当前只有 read/write 失败边进入设置块，Step 0 的初始条件与 any MCP call 失败范围未在控制流中表达。

当前目标事实：`fact:/blocks/6/instructions`, `fact:/edges/3`, `fact:/edges/5`

当前目标图位置：`/blocks/block_007/instructions`, `/edges/3`, `/edges/5`

### finding_7 · 错转

原文要求：Step0 第2步：启用 remote MCP client，方式是设置 `[features] rmcp_client = true` 于 `config.toml`，或者运行 `codex --enable rmcp_client`。这是二选一。

当前回述：ir_017 `enable_remote_mcp_client` 同时把 config_toml、codex_cli 和字面量 `features.rmcp_client=true` 作为同一无分支操作的输入；约束文本保留 or，metadata 有 config 与 CLI script_content，但操作层没有条件/分支选择。

差异理由：二选一的执行条件在操作层被折叠为并列输入，可能表示同时使用 config.toml 和 CLI；metadata 完整保留不等于内部替代选择已建模。

源文：`SKILL.md:26-31`（`src_043`）。

> Set `[features] rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`

受控事实：`fact:/blocks/6/instructions/1`, `fact:/blocks/6/instructions/1/inputs/0`, `fact:/blocks/6/instructions/1/inputs/1`, `fact:/blocks/6/instructions/1/inputs/2`, `fact:/blocks/6/instructions/1/constraints/0`, `fact:/blocks/6/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_007/instructions/1`, `/blocks/block_007/instructions/1/inputs/0`, `/blocks/block_007/instructions/1/inputs/1`, `/blocks/block_007/instructions/1/inputs/2`, `/blocks/block_007/instructions/1/constraints/0`, `/blocks/block_007/instructions/1/metadata`

修改建议：将该操作拆分为按条件选择的 config.toml 设置或 codex --enable rmcp_client 两个分支，或明确只绑定实际选中的方法；不要把两个资源作为同一无分支操作的并列输入。

依据：源文明确为二选一，当前 IR 操作层未表达该选择，可能造成同时配置和命令行启用的错转。

当前目标事实：`fact:/blocks/6/instructions/1`

当前目标图位置：`/blocks/block_007/instructions/1`

### finding_10 · 遗漏

原文要求：重启/告知指令只在登录成功后触发（After successful login）。

当前回述：block_008 中 ir_019 后顺序执行 ir_020 return；没有登录成功 guard、失败分支或条件边，After successful login 只出现在约束/返回字面量，未成为控制条件。

差异理由：源文条件未在控制流中表达，return 可能在同一路径上无条件执行。

源文：`SKILL.md:33-33`（`src_044`）。

> After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.

受控事实：`fact:/blocks/7/constraints/0`, `fact:/blocks/7/instructions/0/outputs/0`, `fact:/blocks/7/instructions/1`, `fact:/blocks/7/instructions/1/inputs/0`

程序映射的当前图位置：`/blocks/block_008/constraints/0`, `/blocks/block_008/instructions/0/outputs/0`, `/blocks/block_008/instructions/1`, `/blocks/block_008/instructions/1/inputs/0`

修改建议：为 ir_020 return 增加登录成功条件或为 oauth_login_result 增加成功/失败分支，确保仅在成功后返回重启指令。

依据：源文明示 After successful login，当前顺序执行未把该 guard 记录为控制条件。

当前目标事实：`fact:/blocks/7/instructions/1`, `fact:/blocks/7/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_008/instructions/1`, `/blocks/block_008/instructions/0/outputs/0`

### finding_14 · 遗漏

原文要求：Available Tools 列出 Issue Management、Project & Team、Documentation & Collaboration 的具体 MCP 工具清单。

当前回述：受控回述只有泛化 ir_007 identify_linear_mcp_tools 和 result_005 required_mcp_tools；没有 list_issues、get_issue、create_issue 等工具清单或类别。

差异理由：Step2 要求识别所需工具，但源文提供的可选工具目录未进入受控事实，无法从回述核对识别范围和工具身份。

源文：`SKILL.md:55-55`（`src_050`）。

> ## Available Tools

源文：`SKILL.md:57-57`（`src_051`）。

> Issue Management: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_my_issues`, `list_issue_statuses`, `list_issue_labels`, `create_issue_label`

源文：`SKILL.md:59-59`（`src_052`）。

> Project & Team: `list_projects`, `get_project`, `create_project`, `update_project`, `list_teams`, `get_team`, `list_users`

源文：`SKILL.md:61-61`（`src_053`）。

> Documentation & Collaboration: `list_documents`, `get_document`, `search_documentation`, `list_comments`, `create_comment`, `list_cycles`

受控事实：`fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/outputs/0`

程序映射的当前图位置：`/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/outputs/0`

修改建议：把 Available Tools 的工具清单作为可选工具集合绑定到 identify_linear_mcp_tools 的输入/输出或上下文，而不是只留下泛化 required_mcp_tools。

依据：缺少工具目录使识别工具步骤无法核对对象和范围。

当前目标事实：`fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/outputs/0`

当前目标图位置：`/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/outputs/0`

### finding_15 · 遗漏

原文要求：Practical Workflows 列出 Sprint Planning、Bug Triage、Documentation Audit 等 9 类工作流及其步骤，Step2 要求据此选择合适 workflow。

当前回述：受控回述只有 ir_006 select_linear_workflow 和 result_004 selected_workflow，约束保留 see Practical Workflows below，但没有 workflow 目录、选项或各流程步骤。

差异理由：选择动作存在，但被选择对象的候选/内容缺失，无法核对选的是哪些 workflow。

源文：`SKILL.md:63-63`（`src_054`）。

> ## Practical Workflows

源文：`SKILL.md:65-73`（`src_055`）。

> - Sprint Planning: Review open issues for a target team, pick top items by priority, and create a new cycle (e.g., "Q1 Performance Sprint") with assignments.

受控事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/2/constraints/0`

程序映射的当前图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_003/constraints/0`

修改建议：为 select_linear_workflow 补充 Practical Workflows 的候选列表/选项来源，或把 workflow 目录绑定到 selected_workflow 的输入上下文。

依据：当前只有泛化选择操作，无法核对可选项和选择依据。

当前目标事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/outputs/0`

### finding_17 · 遗漏

原文要求：Step3：对 bulk operations，在应用变更前解释 grouping logic。

当前回述：该句只作为 /constraints/7 和 block_005 的块级约束 /blocks/4/constraints/1 存在；ir_012 写操作没有 bulk 条件、分组说明操作或应用前顺序 guard。

差异理由：显式条件动作仅以声明文本出现，未记录为操作/条件/顺序，不能视为已实现。

源文：`SKILL.md:46-50`（`src_048`）。

> - For bulk operations, explain the grouping logic before applying changes.

受控事实：`fact:/constraints/7`, `fact:/blocks/4/constraints/1`, `fact:/blocks/4/instructions/0`

程序映射的当前图位置：`/constraints/7`, `/blocks/block_005/constraints/1`, `/blocks/block_005/instructions/0`

修改建议：为 bulk operations 增加条件 guard，并在写操作前增加 explain grouping logic 的显式操作或输出；当前只有声明约束。

依据：源文要求在应用变更前执行解释动作，声明文本不能替代可定位的操作与顺序。

当前目标事实：`fact:/blocks/4/instructions/0`, `fact:/blocks/4/constraints/1`

当前目标图位置：`/blocks/block_005/instructions/0`, `/blocks/block_005/constraints/1`

### finding_20 · 遗漏

原文要求：Step4 的 call out remaining gaps or blockers 和 propose next actions (additional issues, label changes, assignments, follow-up comments)。

当前回述：这两部分只在 /constraints/8 和 block_006 约束文本中出现；ir_014 只命名为 summarize 并只输出 linear_workflow_summary，没有 gaps/blockers/next actions 的输出、操作或绑定。

差异理由：显式动作和对象未单独可定位，不能由汇总动作推断已包含。

源文：`SKILL.md:52-53`（`src_049`）。

> Summarize results, call out remaining gaps or blockers, and propose next actions (additional issues, label changes, assignments, or follow-up comments).

受控事实：`fact:/constraints/8`, `fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/outputs/0`, `fact:/blocks/5/instructions/1`

程序映射的当前图位置：`/constraints/8`, `/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/outputs/0`, `/blocks/block_006/instructions/1`

修改建议：为 gaps/blockers 和 next actions 增加显式输出/操作，或将 linear_workflow_summary 明确绑定为包含这些内容的结果。

依据：源文有并列的 call out 与 propose 要求，当前只有一个泛化 summary 输出。

当前目标事实：`fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/outputs/0`

### finding_23 · 遗漏

原文要求：agents/openai.yaml 声明依赖 mcp 工具 linear，description 为 Linear MCP server，transport 为 streamable_http，url 为 https://mcp.linear.app/mcp。

当前回述：受控回述以 external_resource linear_mcp 和 semantic_name Linear MCP server 表示该依赖，并通过 ir_016 的 URL 字面量保留 url；未记录 transport=streamable_http。

差异理由：URL 和描述有对应，但传输方式这一依赖元数据缺失。

源文：`agents/openai.yaml:8-14`（`src_061`）。

> transport: "streamable_http"

受控事实：`fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/6/instructions/0/inputs/2`, `fact:/blocks/6/instructions/0/constraints/0`

程序映射的当前图位置：`/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_005/instructions/0/inputs/0`, `/blocks/block_007/instructions/0/inputs/2`, `/blocks/block_007/instructions/0/constraints/0`

修改建议：在 MCP 依赖约束或 add_linear_mcp_server 相关输入中记录 transport=streamable_http。

依据：源文 yaml 明确声明的传输方式未在受控事实中表达。

当前目标事实：`fact:/blocks/6/instructions/0/constraints/0`, `fact:/blocks/3/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_007/instructions/0/constraints/0`, `/blocks/block_004/instructions/0/inputs/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 4 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 6 |
| `counts.audit_execution_calls` | 2 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 6 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 2 |
| `counts.http_attempts` | 6 |
| `counts.http_retries` | 0 |
| `counts.http_attempts_observed` | true |
| `counts.returned_models` | ["deepseek-flash"] |
| `counts.record_integrity_errors` | [] |
| `limits.max_semantic_revisions` | 3 |
| `limits.max_structural_repairs` | 3 |
| `limits.max_audit_execution_retries` | 2 |
| `limits.logical_call_bounds` | {"audit": 4, "extraction": 16, "total": 20} |
| `limits.execution_call_bounds` | {"audit": 12, "extraction": 16, "total": 28} |

| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |
|---|---|---|---|
| 0 | complete / passed | passed | complete |
| 1 | complete / passed | passed | 未执行 |

第 1 轮执行错误：`{"message": "findings do not cover controlled units: ['fact:/blocks/6/instructions/0/constraints/0', 'fact:/constraints/14', 'fact:/constraints/15', 'fact:/constraints/18']", "type": "ResponseValidationError"}`。


### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |

最后有效图存在：是。

核对器通过图存在：否。

未通过时，最后有效图只供检查，不作为成功结果。每轮候选、CFG、结构诊断、受控文本及证书、核对响应和反馈 Prompt 与 calls 中的请求记录一同保存。

## 事后复核与信任边界

- 受控往返保持规范化 CFG 中明确记录的事实，不证明开放操作的执行行为、路径可执行性或文件写入成功。
- 核对模型每轮独立比较完整原文和当前受控文本；提取模型收到的建议是待核实依据，原文始终优先。
- 模型可能误报、漏报或在修复后假通过；本报告不会把停止状态自动转换成方法正确率。
- 重新提取会重新赋号，旧图指针不证明新图已经修好；需结合新图、新证据及完整源文复核。
- 二进制、未解释内容以及源码摘要、打印器与进程传输的工程边界见运行清单。
- 助手复核和用户人工确认是不同状态；本生成报告不冒充任何人工确认。

本次输入的具体边界：

- 核对器通过不等于已证明源文与图语义等价。
- 受控文本仅保持图中明确记录的事实。
- 二进制或不透明内容不构成已完成行为理解或运行保证；见 inputs/snapshot.json。
