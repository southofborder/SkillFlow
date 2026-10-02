# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：source quote does not match specified lines: src_015

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 13；遗漏 2；错转 1；无依据新增 1 | {"actionable_ids": ["finding_5", "finding_9", "finding_11", "finding_16"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_4", "finding_6", "finding_7", "finding_8", "finding_10", "finding_12", "finding_13", "finding_14", "finding_15", "finding_17", "finding_18", "finding_19", "finding_20"]}, "revision": 0, "semantic_items": 17, "status": "revise", "unknown_ids": []} |
| 1 | revise | 保留（模型判定） 11；错转 1 | {"actionable_ids": ["finding_7"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": ["finding_8"], "represented_ids": ["finding_1", "finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12"]}, "revision": 1, "semantic_items": 12, "status": "revise", "unknown_ids": []} |
| 2 | revise | 保留（模型判定） 12；内部冲突 1 | {"actionable_ids": ["finding_7"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": ["finding_9"], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14"]}, "revision": 2, "semantic_items": 13, "status": "revise", "unknown_ids": []} |
| 3 | audit_error | 无有效业务核对项 | {"reason": "source quote does not match specified lines: src_015", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_5 · 遗漏

原文要求：Inputs 要求 repo 是仓库内路径且默认 `.`；pr 是 PR number 或 URL，可选，默认当前分支 PR；还要求目标仓库主机上的 gh 认证。

当前回述：block_001 读取 context_key repo 和 pr，输出 result_001 repo_path、result_002 provided_pr；未在读取操作或上下文中记录 repo 默认 `.`、pr 可选及默认当前分支 PR。gh 认证由后续 block_002/003 处理。

差异理由：默认值和可选性属于输入绑定语义；当前读取操作只保留了键名和输出身份，后续解析约束或脚本 metadata 不能完全替代读取输入本身的默认/可选声明。

源文：`SKILL.md:18-20`（`src_040`）。

> - `repo`: path inside the repo (default `.`)
> - `pr`: PR number or URL (optional; defaults to current branch PR)
> - `gh` authentication for the repo host

受控事实：`fact:/blocks/0/key`, `fact:/blocks/0/id`, `fact:/blocks/0/name`, `fact:/blocks/0/source`, `fact:/blocks/0/instructions`, `fact:/blocks/0/instructions/0`, `fact:/blocks/0/instructions/0/inputs/0`, `fact:/blocks/0/instructions/0/inputs/1`, `fact:/blocks/0/instructions/0/outputs/0`, `fact:/blocks/0/instructions/0/outputs/1`, `fact:/blocks/0/instructions/0/metadata_json`, `fact:/blocks/0/instructions/1`, `fact:/blocks/0/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_001/block_id`, `/blocks/block_001/block_name`, `/blocks/block_001/data_source_kind`, `/blocks/block_001/instructions`, `/blocks/block_001/instructions/0`, `/blocks/block_001/instructions/0/inputs/0`, `/blocks/block_001/instructions/0/inputs/1`, `/blocks/block_001/instructions/0/outputs/0`, `/blocks/block_001/instructions/0/outputs/1`, `/blocks/block_001/instructions/0/metadata`, `/blocks/block_001/instructions/1`, `/blocks/block_001/instructions/1/metadata`

修改建议：在读取操作或上下文声明中补充 repo 默认 `.` 与 pr 可选/默认当前分支 PR 的绑定；不要只依赖后续解析约束或脚本 metadata。

依据：这些默认值和可选性是源文 Inputs 的明确绑定要求。

当前目标事实：`fact:/blocks/0/instructions/0`, `fact:/contexts`

当前目标图位置：`/blocks/block_001/instructions/0`, `/declared_context_keys`

### finding_9 · 遗漏

原文要求：Workflow 步骤 3 提供 Manual fallback：gh pr checks 使用指定字段；字段被拒时用 gh 报告的 available fields 重跑；对每个失败 check 从 detailsUrl 提取 run id，运行 gh run view 的 JSON 元数据和 --log；若 run log 说仍在进行中，则直接获取 job logs。

当前回述：受控 block_005 只记录首选 bundled script 的操作、约束和嵌入脚本 metadata；没有显式 manual fallback 分支、命令、字段拒绝重试条件或 job log 直接获取路径。嵌入脚本内部虽含类似 fallback 代码，但按 IR-OPAQUE 不等于显式建模 manual fallback。

差异理由：manual fallback 是源文明示的替代步骤和条件，不是单纯脚本内部实现细节；当前图缺少可定位的 manual fallback 操作或约束。

源文：`SKILL.md:39-46`（`src_044`）。

>    - Manual fallback:
>      - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
>        - If a field is rejected, rerun with the available fields reported by `gh`.
>      - For each failing check, extract the run id from `detailsUrl` and run:
>        - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
>        - `gh run view <run_id> --log`
>      - If the run log says it is still in progress, fetch job logs directly:
>        - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`

受控事实：`fact:/blocks/4/constraints/0`, `fact:/blocks/4/instructions/0`, `fact:/blocks/4/instructions/0/metadata_json`

程序映射的当前图位置：`/blocks/block_005/constraints/0`, `/blocks/block_005/instructions/0`, `/blocks/block_005/instructions/0/metadata`

修改建议：在现有 block_005 中补充 manual fallback 的显式约束或分支，至少记录字段拒绝重跑、按 detailsUrl 取 run id、run metadata/log 以及 pending 时 job log 获取；不要仅依赖 embedded metadata。

依据：源文明示了该替代路径及其条件，当前受控图中没有对应可定位记录。

当前目标事实：`fact:/blocks/4/instructions/0`, `fact:/blocks/4/constraints/0`

当前目标图位置：`/blocks/block_005/instructions/0`, `/blocks/block_005/constraints/0`

### finding_11 · 错转

原文要求：无失败 checks 时，脚本打印 `PR #<pr>: no failing checks detected.` 并返回 0；该路径不生成失败分析报告。

当前回述：block_006（Return no failing checks result）在 exit code 0 路径上 return result_006 inspection_report。result_006 是 run_inspect_pr_checks 的 inspection_report；源文无失败路径实际返回的是无失败消息和 0。边界条件使用 exit code，但 return 值身份不匹配。

差异理由：源文该路径的返回值/外部可见结果是 no failing checks 消息与退出码 0，不是 inspection_report；把 inspection_report 作为 return 输入会造成返回身份错转。

源文：`scripts/inspect_pr_checks.py:114-117`（`src_066`）。

>     failing = [c for c in checks if is_failing(c)]
>     if not failing:
>         print(f"PR #{pr_value}: no failing checks detected.")
>         return 0

受控事实：`fact:/blocks/5/key`, `fact:/blocks/5/id`, `fact:/blocks/5/name`, `fact:/blocks/5/source`, `fact:/blocks/5/instructions`, `fact:/blocks/5/instructions/0`, `fact:/blocks/5/instructions/0/inputs/0`, `fact:/blocks/5/instructions/0/metadata_json`, `fact:/edges/4`

程序映射的当前图位置：`/blocks/block_006/block_id`, `/blocks/block_006/block_name`, `/blocks/block_006/data_source_kind`, `/blocks/block_006/instructions`, `/blocks/block_006/instructions/0`, `/blocks/block_006/instructions/0/inputs/0`, `/blocks/block_006/instructions/0/metadata`, `/edges/4`

修改建议：将无失败路径的 return 输入改为记录无失败结果/消息或退出码 0，而不是 inspection_report；若仍保留报告，应说明其代表无失败检查结果且有源文依据。

依据：return 的 inputs 表示返回值，当前返回值身份与源文无失败路径不一致。

当前目标事实：`fact:/blocks/5/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_006/instructions/0/inputs/0`

### finding_16 · 无依据新增

原文要求：源文只要求请求批准，并只在明确批准后实施；没有要求未批准时返回未批准的 fix plan。

当前回述：block_011（Return the unapproved fix plan）在 edge_10 条件 not approved 下执行 return result_011 fix_plan，新增了一条未批准时返回计划的终止分支。

差异理由：从源文全文检索，未出现 return unapproved plan 或类似要求；源文只给出批准前不得实施的安全边界，这不能自动扩展为未批准时返回 fix_plan 的业务行为。

源文：`SKILL.md:55-56`（`src_044`）。

> 7. Implement after approval.
>    - Apply the approved plan, summarize diffs/tests, and ask about opening a PR.

受控事实：`fact:/blocks/10/key`, `fact:/blocks/10/id`, `fact:/blocks/10/name`, `fact:/blocks/10/source`, `fact:/blocks/10/instructions`, `fact:/blocks/10/instructions/0`, `fact:/blocks/10/instructions/0/inputs/0`, `fact:/blocks/10/instructions/0/metadata_json`, `fact:/edges/10`

程序映射的当前图位置：`/blocks/block_011/block_id`, `/blocks/block_011/block_name`, `/blocks/block_011/data_source_kind`, `/blocks/block_011/instructions`, `/blocks/block_011/instructions/0`, `/blocks/block_011/instructions/0/inputs/0`, `/blocks/block_011/instructions/0/metadata`, `/edges/10`

修改建议：删除或改写未批准分支的 return fix_plan，除非源文明确要求；至少应避免把“不实施”表达为返回未批准计划。

依据：源文没有规定未批准路径返回 fix_plan。

当前目标事实：`fact:/blocks/10/instructions/0`, `fact:/edges/10`

当前目标图位置：`/blocks/block_011/instructions/0`, `/edges/10`

### 第 1 轮

### finding_7 · 错转

原文要求：当没有失败 checks 时，脚本打印 `PR #<pr>: no failing checks detected.` 并返回 0；消息是标准输出，返回值或退出码才是 0。

当前回述：/blocks/6/instructions/0 是 return，inputs 同时列出 result_005 inspection_output 与 result_006 inspection_exit_code；constraint 0 记录了打印消息和返回 0。

差异理由：按 [IR-CONTROL]，return 的 inputs 记录返回值。源文脚本 main 只返回 0（退出码），打印消息不是返回值。把 result_005 列为 return 输入，会把标准输出错绑成返回值；constraint 中的打印描述不能修正该 return 输入身份。

源文：`scripts/inspect_pr_checks.py:115-117`（`src_066`）。

>     if not failing:
>         print(f"PR #{pr_value}: no failing checks detected.")
>         return 0

受控事实：`fact:/blocks/6/instructions/0`, `fact:/blocks/6/instructions/0/inputs/0`, `fact:/blocks/6/instructions/0/inputs/1`, `fact:/blocks/6/constraints/0`, `fact:/blocks/6/key`, `fact:/blocks/6/id`, `fact:/blocks/6/name`, `fact:/blocks/6/source`, `fact:/blocks/6/instructions`, `fact:/blocks/6/instructions/0/metadata_json`, `fact:/edges/5`, `fact:/blocks/6/instructions/0/inputs/0:link`, `fact:/blocks/6/instructions/0/inputs/1:link`

程序映射的当前图位置：`/blocks/block_007/instructions/0`, `/blocks/block_007/instructions/0/inputs/0`, `/blocks/block_007/instructions/0/inputs/1`, `/blocks/block_007/constraints/0`, `/blocks/block_007/block_id`, `/blocks/block_007/block_name`, `/blocks/block_007/data_source_kind`, `/blocks/block_007/instructions`, `/blocks/block_007/instructions/0/metadata`, `/edges/5`

修改建议：从该 return 的 inputs 中移除 result_005 inspection_output，仅保留 result_006 inspection_exit_code 作为返回值；无失败消息继续由约束/脚本输出记录，不要作为 return 返回值。

依据：避免把脚本标准输出错绑为返回身份，符合 [IR-CONTROL] 对 return inputs 的解释。

当前目标事实：`fact:/blocks/6/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_007/instructions/0/inputs/0`

### 第 2 轮

### finding_7 · 内部冲突

原文要求：脚本的退出语义：有失败时非零，但 main 在不在 git repo、gh 不可用或未认证、PR 解析失败、checks 获取失败等错误路径也 return 1；无失败 return 0。

当前回述：受控边 edges/6 将 block_005 的 non-zero 一律记为 exit code non-zero / failures remain 并路由到 scope/summarize；元数据中嵌入的脚本却显示多种 setup/API 错误也返回 1。

差异理由：嵌入脚本与边条件内部冲突：非零退出不等于 failures remain；受控记录缺少错误路径与 failures remain 的区分。

源文：`scripts/inspect_pr_checks.py:96-101`（`src_062`）。

>         return 1

源文：`scripts/inspect_pr_checks.py:103-104`（`src_063`）。

>         return 1

源文：`scripts/inspect_pr_checks.py:106-108`（`src_064`）。

>         return 1

源文：`scripts/inspect_pr_checks.py:110-112`（`src_065`）。

>         return 1

源文：`scripts/inspect_pr_checks.py:135-135`（`src_069`）。

>     return 1

源文：`scripts/inspect_pr_checks.py:114-117`（`src_066`）。

>         return 0

受控事实：`fact:/edges/6`, `fact:/blocks/4/instructions/1`, `fact:/blocks/4/instructions/1/inputs/0`, `fact:/blocks/4/instructions/0/metadata_json`, `fact:/blocks/4/instructions/0/outputs/1`, `fact:/blocks/7/instructions/0`

程序映射的当前图位置：`/edges/6`, `/blocks/block_005/instructions/1`, `/blocks/block_005/instructions/1/inputs/0`, `/blocks/block_005/instructions/0/metadata`, `/blocks/block_005/instructions/0/outputs/1`, `/blocks/block_008/instructions/0`

修改建议：将 edges/6 的条件收窄为 failures remain，并为脚本错误返回单独记录错误或终止路径；不要把全部 non-zero 都说明为 failures remain。

依据：源脚本存在多个非失败错误的 return 1 路径，当前边条件会错误合并它们。

当前目标事实：`fact:/edges/6`, `fact:/blocks/4/instructions/1`

当前目标图位置：`/edges/6`, `/blocks/block_005/instructions/1`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 8 |
| `counts.audit_logical_calls` | 4 |
| `counts.total_logical_calls` | 12 |
| `counts.audit_execution_calls` | 4 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 12 |
| `counts.semantic_revisions` | 3 |
| `counts.structural_repairs` | 4 |
| `counts.http_attempts` | 12 |
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
| 2 | complete / passed | passed | complete |
| 3 | complete / passed | passed | 未执行 |

第 3 轮执行错误：`{"message": "source quote does not match specified lines: src_015", "type": "ResponseValidationError"}`。


### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |
| 2 | 1 | complete | 否 |
| 3 | 1 | complete | 否 |

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
