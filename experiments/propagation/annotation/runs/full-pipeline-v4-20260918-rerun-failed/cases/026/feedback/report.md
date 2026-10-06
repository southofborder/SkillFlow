# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：source quote does not match specified lines: src_105

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 8；错转 1；遗漏 3；无依据新增 1 | {"actionable_ids": ["finding_5", "finding_9", "finding_10", "finding_12", "finding_13"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_6", "finding_7", "finding_8", "finding_11", "finding_14", "finding_15"]}, "revision": 0, "semantic_items": 13, "status": "revise", "unknown_ids": []} |
| 1 | audit_error | 无有效业务核对项 | {"reason": "source quote does not match specified lines: src_105", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_5 · 错转

原文要求：若 `npx` 不可用，应暂停并让用户安装 Node.js/npm，且要逐字提供源文给出的验证/安装步骤，包括注释、空行和“如缺失则安装 Node.js/npm，然后……”这一条件说明。

当前回述：block_003 的 ask_user_to_install_nodejs 用 literal 记录 `node --version\nnpm --version\nnpm install -g @playwright/cli@latest\nplaywright-cli --help`，并在操作级约束写“Provide these steps verbatim.”；但 literal 省略了 `# Verify Node/npm are installed`、空行和 `# If missing, install Node.js/npm, then:`。随后 edge 3 无条件回到 npx 检查。

差异理由：动作和四条命令基本存在，但“逐字提供”的数据绑定未满足：源文代码块中的注释/空行/条件说明没有进入 literal；同时图中没有显式等待或用户完成安装条件，只有回边。

源文：`SKILL.md:20-20`（`src_045`）。

> If it is not available, pause and ask the user to install Node.js/npm

源文：`SKILL.md:22-30`（`src_046`）。

> ```bash

受控事实：`fact:/constraints/3`, `fact:/blocks/2/key`, `fact:/blocks/2/id`, `fact:/blocks/2/name`, `fact:/blocks/2/source`, `fact:/blocks/2/instructions`, `fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/constraints/0`, `fact:/blocks/2/instructions/0/metadata_json`, `fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/metadata_json`, `fact:/edges/3`

程序映射的当前图位置：`/constraints/3`, `/blocks/block_003/block_id`, `/blocks/block_003/block_name`, `/blocks/block_003/data_source_kind`, `/blocks/block_003/instructions`, `/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/constraints/0`, `/blocks/block_003/instructions/0/metadata`, `/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/metadata`, `/edges/3`

修改建议：将 literal_json 改为与源文代码块逐字一致，包含两段注释和空行；若只想提供命令，则同步修改逐字约束。

依据：当前 literal 与“Provide these steps verbatim.”冲突，缺少源文步骤的注释与条件说明。

当前目标事实：`fact:/blocks/2/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_003/instructions/0/inputs/0`

修改建议：若要求暂停等待用户安装完成，给回边增加“用户已完成安装/重新检查前等待”的显式条件或等待语义。

依据：源文说 pause and ask，当前边无条件立即回到检查，未表达等待条件。

当前目标事实：`fact:/edges/3`

当前目标图位置：`/edges/3`

### finding_9 · 遗漏

原文要求：在有帮助/有用时捕获 artifacts：screenshot、pdf、traces；且在 repo 中捕获时要使用 `output/playwright/` 并避免新增顶层 artifact 目录。

当前回述：block_009 的 execute_playwright_cli_wrapper 输入 result_002/pwcli_path 和 literal `screenshot/pdf/traces`，块级约束记录 `output/playwright/` 限制；但该块只由 edge 9 的“no resnapshot needed”进入，随后 edge 10 return。没有“when useful”守卫或条件，输出路径约束也只是声明未绑定到 capture 输入。

差异理由：捕获动作和 artifact 种类存在，但源文的“when useful”条件没有进入任何边条件或操作输入；按当前图，最终无 resnapshot 需求的路径会捕获 artifacts，而不是仅在有用时捕获。

源文：`SKILL.md:65-69`（`src_057`）。

> 1. Open the page.

受控事实：`fact:/blocks/8/key`, `fact:/blocks/8/id`, `fact:/blocks/8/name`, `fact:/blocks/8/source`, `fact:/blocks/8/constraints/0`, `fact:/blocks/8/instructions`, `fact:/blocks/8/instructions/0`, `fact:/blocks/8/instructions/0/inputs/0`, `fact:/blocks/8/instructions/0/inputs/1`, `fact:/blocks/8/instructions/0/metadata_json`, `fact:/blocks/8/instructions/1`, `fact:/blocks/8/instructions/1/metadata_json`, `fact:/edges/9`, `fact:/edges/10`, `fact:/blocks/8/instructions/0/inputs/0:link`

程序映射的当前图位置：`/blocks/block_009/block_id`, `/blocks/block_009/block_name`, `/blocks/block_009/data_source_kind`, `/blocks/block_009/constraints/0`, `/blocks/block_009/instructions`, `/blocks/block_009/instructions/0`, `/blocks/block_009/instructions/0/inputs/0`, `/blocks/block_009/instructions/0/inputs/1`, `/blocks/block_009/instructions/0/metadata`, `/blocks/block_009/instructions/1`, `/blocks/block_009/instructions/1/metadata`, `/edges/9`, `/edges/10`

修改建议：增加显式“when useful”条件/守卫，或把该条件绑定到 capture 操作；若输出目录是执行参数，应把 `output/playwright/` 绑定到 capture 的输入或保持为明确声明而不声称已实现。

依据：当前 capture 在 no-resnapshot 分支无条件发生，源文的 when useful 条件缺失；输出目录只有声明，没有操作绑定。

当前目标事实：`fact:/edges/9`, `fact:/blocks/8/instructions/0`

当前目标图位置：`/edges/9`, `/blocks/block_009/instructions/0`

### finding_10 · 无依据新增

原文要求：源文核心工作流结束于在有用时捕获 artifacts；未要求返回任何完成消息、状态字符串或返回载荷。

当前回述：block_010 的 return 输入 literal `"browser workflow completed"`，块名为“Return the completed browser workflow”；edge 10 从 capture 进入该 return。

差异理由：return 作为 IR 控制终结可以由图表达，但当前 return 携带了源文没有规定的返回值身份。源文检索未发现“browser workflow completed”或类似返回载荷。

源文：`SKILL.md:65-69`（`src_057`）。

> 1. Open the page.

受控事实：`fact:/blocks/9/key`, `fact:/blocks/9/id`, `fact:/blocks/9/name`, `fact:/blocks/9/source`, `fact:/blocks/9/instructions`, `fact:/blocks/9/instructions/0`, `fact:/blocks/9/instructions/0/inputs/0`, `fact:/blocks/9/instructions/0/metadata_json`, `fact:/edges/10`

程序映射的当前图位置：`/blocks/block_010/block_id`, `/blocks/block_010/block_name`, `/blocks/block_010/data_source_kind`, `/blocks/block_010/instructions`, `/blocks/block_010/instructions/0`, `/blocks/block_010/instructions/0/inputs/0`, `/blocks/block_010/instructions/0/metadata`, `/edges/10`

修改建议：删除未受源文支持的返回 literal，或改为无返回值的 return 终结操作。

依据：return 本身不表示向用户展示内容；源文没有定义该返回载荷，保留会新增未支持的业务结果身份。

当前目标事实：`fact:/blocks/9/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_010/instructions/0/inputs/0`

### finding_12 · 遗漏

原文要求：`references/cli.md` 写的是：除非 CLI 已经全局安装，否则使用 wrapper 脚本。

当前回述：受控只记录“全局安装可选”和“除非仓库已标准化为全局安装，否则优先 wrapper”，没有记录“CLI 已经全局安装”这一例外条件；block_004 总是设置 wrapper 路径，后续 execute 操作都使用 result_002。

差异理由：源文参考文件中的显式例外条件与受控 constraint 4/6 的条件不相同；该例外没有作为约束、分支或说明保留。

源文：`references/cli.md:3-3`（`src_083`）。

> Use the wrapper script unless the CLI is already installed globally:

受控事实：`fact:/constraints/4`, `fact:/constraints/6`, `fact:/blocks/3/instructions/0`

程序映射的当前图位置：`/constraints/4`, `/constraints/6`, `/blocks/block_004/instructions/0`

修改建议：增加“CLI 已全局安装”这一例外/条件，或明确说明该参考例外不适用于当前工作流；不要把它与“仓库标准化全局安装”混为同一条件。

依据：源文明确给出 already installed globally 的 wrapper 例外，受控仅保留另一条件。

当前目标事实：`fact:/constraints/6`, `fact:/blocks/3/instructions/0`

当前目标图位置：`/constraints/6`, `/blocks/block_004/instructions/0`

### finding_13 · 遗漏

原文要求：References 部分要求只打开需要的内容，并列明 CLI command reference: `references/cli.md` 和 Practical workflows and troubleshooting: `references/workflows.md`。

当前回述：受控图只有浏览器操作、wrapper 执行、约束和返回，没有打开/读取这两个参考文件的资源操作，也没有“only what you need”的条件分支；仅部分 workflows.md 中的 troubleshooting 条件被提升为约束。

差异理由：源文存在显式的按需引用资源指令，但当前图中没有对应的资源或条件动作可定位。

源文：`SKILL.md:132-132`（`src_075`）。

> ## References

源文：`SKILL.md:134-134`（`src_076`）。

> Open only what you need:

源文：`SKILL.md:136-137`（`src_077`）。

> - CLI command reference: `references/cli.md`

受控事实：`fact:/entry`, `fact:/blocks/4/instructions/0`

程序映射的当前图位置：`/entry_block_id`, `/blocks/block_005/instructions/0`

修改建议：在入口后或合适位置增加按需打开/读取 `references/cli.md`、`references/workflows.md` 的条件资源操作或分支，并保留“只打开需要内容”的条件。

依据：当前图未记录该显式资源访问要求。

当前目标事实：`fact:/entry`

当前目标图位置：`/entry_block_id`

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

第 1 轮执行错误：`{"message": "source quote does not match specified lines: src_105", "type": "ResponseValidationError"}`。


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
