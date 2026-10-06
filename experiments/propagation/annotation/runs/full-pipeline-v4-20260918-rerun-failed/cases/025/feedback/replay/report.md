# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 遗漏 1；保留（模型判定） 13；错转 3 | {"actionable_ids": ["finding_3", "finding_8b", "finding_9b", "finding_11b"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": ["finding_6"], "represented_ids": ["finding_4", "finding_5", "finding_6", "finding_7", "finding_8a", "finding_9a", "finding_10", "finding_11a", "finding_12", "finding_13", "finding_14", "finding_15", "finding_16"]}, "revision": 0, "semantic_items": 17, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 23 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": ["finding_render_candidate_sources"], "represented_ids": ["finding_description", "finding_when_to_use", "finding_pdftoppm_availability", "finding_render_command", "finding_render_candidate_sources", "finding_inspect_pngs", "finding_no_delivery", "finding_confirm_cleanup", "finding_install_poppler", "finding_ask_user_review", "finding_generate_reportlab", "finding_apply_update", "finding_extract_text", "finding_missing_deps_check", "finding_no_missing_return", "finding_uv_check", "finding_uv_install", "finding_pip_install", "finding_temp_output", "finding_environment", "finding_quality", "finding_final_checks", "finding_dependency_global"]}, "revision": 1, "semantic_items": 23, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

### finding_render_candidate_sources · 保留（模型判定）

保守规则：`DEP-SOURCE`；候选事实：fact:/blocks/1/instructions/0/inputs/1, fact:/blocks/7/instructions/0/outputs/0, fact:/blocks/8/instructions/0/outputs/0

保留理由：源文工作流包含对原 PDF 的视觉审查、生成新 PDF 后验证、以及 meaningful update 后重新渲染；图中 render op 同时列出 input_pdf、result_006、result_007，且 edge7/edge8 支持生成/更新路径，故作为候选来源集合保守保留。

损失的区分：未区分初始 input_pdf、reportlab 生成的 result_006 和更新后的 result_007 分别在哪条路径作为渲染输入。；未表达这些候选是按路径择一，而不是同时作为实参传入。

原文要求：渲染操作可作用于初始输入 PDF、reportlab 生成的新 PDF、或 meaningful update 后的 PDF；源文未要求把三者精确区分为不同渲染操作。

当前回述：block_002 渲染操作输入同时列出 input_pdf、result_006(generated_pdf)、result_007(updated_pdf)，没有按路径区分具体选值。

差异理由：这是有依据的候选来源集合；不声称三者同时传递。

源文：`SKILL.md:18-18`（`src_037`）。

> 2. Use `reportlab` to generate PDFs when creating new documents.

源文：`SKILL.md:20-20`（`src_037`）。

> 4. After each meaningful update, re-render pages and verify alignment, spacing, and legibility.

受控事实：`fact:/blocks/1/instructions/0/inputs/1`, `fact:/blocks/1/instructions/0/inputs/2`, `fact:/blocks/1/instructions/0/inputs/3`, `fact:/blocks/7/instructions/0/outputs/0`, `fact:/blocks/8/instructions/0/outputs/0`, `fact:/blocks/1/instructions/0/inputs/2:link`, `fact:/blocks/1/instructions/0/inputs/3:link`, `fact:/edges/7`, `fact:/edges/8`

程序映射的当前图位置：`/blocks/block_002/instructions/0/inputs/1`, `/blocks/block_002/instructions/0/inputs/2`, `/blocks/block_002/instructions/0/inputs/3`, `/blocks/block_008/instructions/0/outputs/0`, `/blocks/block_009/instructions/0/outputs/0`, `/edges/7`, `/edges/8`

## 历史轮次差异

### 第 0 轮

### finding_3 · 遗漏

原文要求：When to use 要求：当任务涉及阅读、创建或审阅 PDF，且渲染/版式重要时使用本 Skill；创建 PDF 时需要可靠格式；交付前验证最终渲染。

当前回述：受控回述只有无条件入口 fact:/entry，未记录这些适用触发条件或任务类型区分。

差异理由：源文明确给出使用范围和交付前验证条件；受控图未在入口或图级声明中保留这些条件，仅靠后续块名不能替代触发条件。

源文：`SKILL.md:9-12`（`src_036`）。

> - Read or review PDF content where layout and visuals matter.

受控事实：`fact:/entry`

程序映射的当前图位置：`/entry_block_id`

修改建议：在入口或图级声明中补记“阅读/创建/审阅 PDF 且版式重要”的适用条件，以及交付前验证最终渲染的触发条件。

依据：当前入口无任何适用条件，无法从受控图判断何时应进入该 Skill。

当前目标事实：`fact:/entry`

当前目标图位置：`/entry_block_id`

### finding_8b · 错转

原文要求：文本提取工具是 `pdfplumber`（或 `pypdf`），即二者是替代关系。

当前回述：block_007 的操作名含 pdfplumber_or_pypdf，但输入列表把 pdfplumber 和 pypdf 记录为两个并列 external_resource 操作数。

差异理由：源文用“或”表达替代选择；受控输入列表按记录次序并列两个工具，未记录路径条件或候选选择关系，容易被理解为同一操作同时接收两个工具实参。

源文：`SKILL.md:19-19`（`src_037`）。

> 3. Use `pdfplumber` (or `pypdf`) for text extraction and quick checks; do not rely on it for layout fidelity.

受控事实：`fact:/blocks/7/instructions/0`, `fact:/blocks/7/instructions/0/inputs/0`, `fact:/blocks/7/instructions/0/inputs/1`

程序映射的当前图位置：`/blocks/block_008/instructions/0`, `/blocks/block_008/instructions/0/inputs/0`, `/blocks/block_008/instructions/0/inputs/1`

修改建议：将 pypdf 表示为 pdfplumber 的备选/回退条件，而不是同一操作下与 pdfplumber 并列的独立实参；若保留 opcode 中的 or，也不要把两个工具同时作为实际输入。

依据：源文只允许 pdfplumber 或 pypdf 二选一，当前并列输入没有对应条件，改变了工具绑定语义。

当前目标事实：`fact:/blocks/7/instructions/0/inputs/1`

当前目标图位置：`/blocks/block_008/instructions/0/inputs/1`

### finding_9b · 错转

原文要求：源文只要求在每次有意义的更新后重新渲染并核对，未规定由检查发现缺陷触发 apply_meaningful_pdf_update，也未规定该更新读取 inspection_findings。

当前回述：受控回述用 /edges/3 在“发现视觉或格式缺陷”时进入 block_005 apply update，并把 result_004 inspection_findings 作为 apply update 的输入。

差异理由：检查发现缺陷可以作为不交付的条件，但源文没有显式把 inspection_findings 绑定为更新输入或缺陷触发更新；该绑定改变了更新动作的触发和依赖来源。

源文：`SKILL.md:20-20`（`src_037`）。

> 4. After each meaningful update, re-render pages and verify alignment, spacing, and legibility.

受控事实：`fact:/edges/3`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/inputs/0:link`

程序映射的当前图位置：`/edges/3`, `/blocks/block_005/instructions/0/inputs/0`

修改建议：删除或改写缺陷触发边与 inspection_findings 到 apply update 的输入绑定；若保留修复循环，需要源文中明确的缺陷触发和输入依据。

依据：当前记录把检查发现作为更新动作的触发和输入，源文未明确支持。

当前目标事实：`fact:/blocks/4/instructions/0/inputs/0`, `fact:/edges/3`

当前目标图位置：`/blocks/block_005/instructions/0/inputs/0`, `/edges/3`

### finding_11b · 错转

原文要求：Dependencies 标题要求“install if missing”，即只有缺失依赖时才安装。

当前回述：受控回述只检查 uv_available，并直接依据 uv 是否可用进入 uv 或 pip 安装块；没有记录 reportlab、pdfplumber、pypdf 等依赖是否缺失的前置条件。

差异理由：源文把安装动作限定在依赖缺失时；受控记录把安装条件变成仅由 uv 可用性决定，遗漏了“缺失”这一关键守卫。

源文：`SKILL.md:27-27`（`src_039`）。

> ## Dependencies (install if missing)

源文：`SKILL.md:32-32`（`src_040`）。

> uv pip install reportlab pdfplumber pypdf

受控事实：`fact:/blocks/8/instructions/0`, `fact:/blocks/9/instructions/0`, `fact:/blocks/10/instructions/0`, `fact:/edges/7`, `fact:/edges/8`

程序映射的当前图位置：`/blocks/block_009/instructions/0`, `/blocks/block_010/instructions/0`, `/blocks/block_011/instructions/0`, `/edges/7`, `/edges/8`

修改建议：在分派到 uv/pip 安装前补记 Python 包缺失检查，或在安装操作上记录“if missing”条件；不能只用 uv_available 作为安装触发。

依据：当前图会在 uv 可用性满足时安装，而源文要求仅在依赖缺失时安装。

当前目标事实：`fact:/blocks/8/instructions/0`

当前目标图位置：`/blocks/block_009/instructions/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 3 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 5 |
| `counts.audit_execution_calls` | 2 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 5 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 1 |
| `counts.http_attempts` | 5 |
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
| 1 | complete / passed | passed | complete |

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |

最后有效图存在：是。

核对器通过图存在：是。

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
