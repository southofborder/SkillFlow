# CFG 构建语义反馈闭环

停止状态：**核对执行错误**（`audit_error`）。

停止原因：Saved call is incomplete; no automatic resend is permitted

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 11；错转 3；内部冲突 1 | {"actionable_ids": ["finding_7", "finding_13", "finding_14", "finding_16"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_4", "finding_5", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_15", "finding_17", "finding_18", "finding_19"]}, "revision": 0, "semantic_items": 15, "status": "revise", "unknown_ids": []} |
| 1 | audit_error | 无有效业务核对项 | {"reason": "Saved call is incomplete; no automatic resend is permitted", "status": "audit_error"} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_7 · 错转

原文要求：缺 key 时要指示用户在 OpenAI platform UI 创建 key，并在 shell 中 export；同时不得要求用户在聊天中粘贴完整 key。

当前回述：block_003 的 ask_user_to_set_openai_api_key 输入 literal 仅说 Set OPENAI_API_KEY in your shell. Do not paste the full key in chat.；constraints 文本包含 create one in the OpenAI platform UI and export it in their shell，但该创建 UI 指令未绑定到实际 ask 操作的 message；return literal 只是 OPENAI_API_KEY is not set.，不是用户消息。

差异理由：约束声明不能替代 ask 操作的对象内容；源文要求实际指示创建 key，当前 ask 消息缺少该局部语义。

源文：`SKILL.md:41-42`（`src_042`）。

> - If the key is missing, instruct the user to create one in the OpenAI platform UI and export it in their shell.

源文：`SKILL.md:13-13`（`src_037`）。

> 2. Verify `OPENAI_API_KEY` is set. If missing, ask the user to set it locally (do not ask them to paste the key).

受控事实：`fact:/blocks/2/key`, `fact:/blocks/2/id`, `fact:/blocks/2/name`, `fact:/blocks/2/source`, `fact:/blocks/2/instructions`, `fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/constraints/0`, `fact:/blocks/2/instructions/0/constraints/1`, `fact:/blocks/2/instructions/0/metadata_json`, `fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/inputs/0`, `fact:/blocks/2/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_003/block_id`, `/blocks/block_003/block_name`, `/blocks/block_003/data_source_kind`, `/blocks/block_003/instructions`, `/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/constraints/0`, `/blocks/block_003/instructions/0/constraints/1`, `/blocks/block_003/instructions/0/metadata`, `/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/inputs/0`, `/blocks/block_003/instructions/1/metadata`

修改建议：将 ask_user_to_set_openai_api_key 的消息字面量补充为同时指示用户在 OpenAI platform UI 创建 key 并在 shell 中 export；若保持现有消息，应另将创建 UI 的指令绑定到实际 ask 操作。

依据：源文要求缺 key 时实际指示创建 key 并 export，而当前 ask 操作的消息只覆盖 shell 设置和不要粘贴。

当前目标事实：`fact:/blocks/2/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_003/instructions/0/inputs/0`

### finding_13 · 错转

原文要求：dry-run 时 _ensure_api_key 允许缺少 key（仅警告并继续）；main 打印 payload 并返回，不创建 client、不调用 API、不写出文件。

当前回述：受控记录 dry_run context -> result_011 -> chosen_dry_run result_024 -> run 输入 result_024；但 key 缺失分支仍直接 ask/return，且 run 后无 dry_run 分支，仍连接 validate/save，run 输出 transcript/written paths。

差异理由：dry_run 被当作运行输入保留，但其对 key 校验、API 调用和输出终止的条件作用未在控制流/操作输出中体现，局部语义错转。

源文：`scripts/transcribe_diarize.py:33-40`（`src_061`）。

>     if dry_run:

源文：`scripts/transcribe_diarize.py:189-228`（`src_074`）。

>         help="Validate inputs and print payload without calling the API",

源文：`scripts/transcribe_diarize.py:257-259`（`src_081`）。

>     if args.dry_run:

受控事实：`fact:/contexts`, `fact:/blocks/0/instructions/0/inputs/10`, `fact:/blocks/0/instructions/0/outputs/10`, `fact:/blocks/6/instructions/0/outputs/6`, `fact:/blocks/7/instructions/0/inputs/13`, `fact:/blocks/1/instructions/1`, `fact:/edges/1`, `fact:/edges/2`, `fact:/blocks/8/instructions/0`, `fact:/blocks/9/instructions/0`

程序映射的当前图位置：`/declared_context_keys`, `/blocks/block_001/instructions/0/inputs/10`, `/blocks/block_001/instructions/0/outputs/10`, `/blocks/block_007/instructions/0/outputs/6`, `/blocks/block_008/instructions/0/inputs/13`, `/blocks/block_002/instructions/1`, `/edges/1`, `/edges/2`, `/blocks/block_009/instructions/0`, `/blocks/block_010/instructions/0`

修改建议：补充 dry_run 条件分支：dry_run 为真时允许缺少 key，构建并输出 payload 后终止，不进入 API 调用、输出验证和文件写出；dry_run 为假时才走现有 key 校验与运行保存路径。

依据：源脚本明确规定 dry-run 不调用 API、不写出文件，并允许缺 key；当前控制流仅把 dry_run 当普通输入传递。

当前目标事实：`fact:/blocks/1/instructions/1`, `fact:/blocks/7/instructions/0`, `fact:/blocks/9/instructions/0`

当前目标图位置：`/blocks/block_002/instructions/1`, `/blocks/block_008/instructions/0`, `/blocks/block_010/instructions/0`

### finding_14 · 错转

原文要求：--stdout 将 transcript 写到 stdout 而不是文件；--stdout 不能与 --out/--out-dir 同用；--stdout 仅支持单 audio；--out 仅支持单 audio。

当前回述：受控记录 stdout/out_path/out_dir 输入、chosen_stdout/chosen_out_path/chosen_output_dir 输出，并在 run op 接收；但 block_010 write_transcript_to_output_directory 在验证后无条件写出到 output_dir，无 stdout 跳过写文件的分支，也无互斥/单文件约束。

差异理由：stdout/out 的终止/互斥条件未保留；尤其 stdout 模式下仍存在写文件步骤，和 instead of a file 冲突。

源文：`scripts/transcribe_diarize.py:219-223`（`src_074`）。

>         help="Write transcript to stdout instead of a file",

源文：`scripts/transcribe_diarize.py:234-239`（`src_076`）。

>     if args.stdout and (args.out or args.out_dir):

源文：`scripts/transcribe_diarize.py:263-272`（`src_083`）。

>         if args.stdout:

受控事实：`fact:/blocks/0/instructions/0/inputs/7`, `fact:/blocks/0/instructions/0/inputs/8`, `fact:/blocks/0/instructions/0/inputs/9`, `fact:/blocks/0/instructions/0/outputs/7`, `fact:/blocks/0/instructions/0/outputs/8`, `fact:/blocks/0/instructions/0/outputs/9`, `fact:/blocks/6/instructions/0/outputs/3`, `fact:/blocks/6/instructions/0/outputs/4`, `fact:/blocks/6/instructions/0/outputs/5`, `fact:/blocks/7/instructions/0/inputs/10`, `fact:/blocks/7/instructions/0/inputs/11`, `fact:/blocks/7/instructions/0/inputs/12`, `fact:/blocks/9/instructions/0`, `fact:/blocks/9/instructions/0/inputs/0`, `fact:/blocks/9/instructions/0/inputs/1`, `fact:/blocks/9/instructions/0/inputs/2`, `fact:/blocks/9/instructions/0/outputs/0`

程序映射的当前图位置：`/blocks/block_001/instructions/0/inputs/7`, `/blocks/block_001/instructions/0/inputs/8`, `/blocks/block_001/instructions/0/inputs/9`, `/blocks/block_001/instructions/0/outputs/7`, `/blocks/block_001/instructions/0/outputs/8`, `/blocks/block_001/instructions/0/outputs/9`, `/blocks/block_007/instructions/0/outputs/3`, `/blocks/block_007/instructions/0/outputs/4`, `/blocks/block_007/instructions/0/outputs/5`, `/blocks/block_008/instructions/0/inputs/10`, `/blocks/block_008/instructions/0/inputs/11`, `/blocks/block_008/instructions/0/inputs/12`, `/blocks/block_010/instructions/0`, `/blocks/block_010/instructions/0/inputs/0`, `/blocks/block_010/instructions/0/inputs/1`, `/blocks/block_010/instructions/0/inputs/2`, `/blocks/block_010/instructions/0/outputs/0`

修改建议：补充 stdout 条件：chosen_stdout 为真时只输出到 stdout，跳过 write_transcript_to_output_directory；补充 --stdout 与 --out/--out-dir 互斥及单 audio 限制的约束或条件。

依据：源脚本明确 stdout instead of a file，并对 --out、--stdout 与多文件组合进行拒绝；当前受控写出路径无条件执行。

当前目标事实：`fact:/blocks/9/instructions/0`, `fact:/blocks/7/instructions/0`, `fact:/blocks/6/instructions/0`

当前目标图位置：`/blocks/block_010/instructions/0`, `/blocks/block_008/instructions/0`, `/blocks/block_007/instructions/0`

### finding_16 · 内部冲突

原文要求：如有需要，用一次针对性修改迭代。

当前回述：block_009 的 constraint0 文本包含 iterate with a single targeted change if needed，但 block_009 只有 validate 操作，紧接 dispatch_to_save，图中无回退到 choose/run 或再次 validate 的操作/边。

差异理由：约束声明了迭代，但控制/操作记录没有对应条件回退；声明与操作记录不一致。

源文：`SKILL.md:15-15`（`src_037`）。

> iterate with a single targeted change if needed.

受控事实：`fact:/blocks/8/instructions/0`, `fact:/blocks/8/instructions/0/constraints/0`, `fact:/blocks/8/instructions/1`, `fact:/blocks/8/instructions/1/metadata_json`, `fact:/edges/7`, `fact:/edges/8`

程序映射的当前图位置：`/blocks/block_009/instructions/0`, `/blocks/block_009/instructions/0/constraints/0`, `/blocks/block_009/instructions/1`, `/blocks/block_009/instructions/1/metadata`, `/edges/7`, `/edges/8`

修改建议：在已有 validate 操作后补充基于 validation_notes 的条件回退到已有 choose/run/validate 容器；若不需要回退则终止到保存；不要只保留 iterate 声明。

依据：源文要求必要时进行单次针对性修改迭代，当前只有约束声明而没有对应控制操作。

当前目标事实：`fact:/blocks/8/instructions/0`, `fact:/blocks/8/instructions/1`

当前目标图位置：`/blocks/block_009/instructions/0`, `/blocks/block_009/instructions/1`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 4 |
| `counts.audit_execution_calls` | 3 |
| `counts.audit_execution_retries` | 1 |
| `counts.total_execution_calls` | 5 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
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
| 1 | complete / passed | passed | 未执行 |

第 1 轮执行错误：`{"message": "Saved call is incomplete; no automatic resend is permitted", "type": "IncompleteResponse"}`。


### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | incomplete_accepted_stream | 是 |
| 1 | 2 | complete_interrupted_or_uncertain_call | 否 |

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
