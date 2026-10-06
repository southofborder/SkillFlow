# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 13；遗漏 2 | {"actionable_ids": ["finding_5", "finding_9"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_6", "finding_7", "finding_8", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14", "finding_15", "finding_16"]}, "revision": 0, "semantic_items": 15, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 12 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_13", "finding_14"]}, "revision": 1, "semantic_items": 12, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_5 · 遗漏

原文要求：按 manifest 中 paths 列表获取文档路径。

当前回述：ir_003 只接收 result_001 manifest_content；block_002 名称虽含 manifest paths list，但受控文本声明块名仅为标签；没有操作输入、字面量、context_key 或 metadata 明确记录 paths 列表/键。

差异理由：源文要求的特定数据来源是 manifest 的 paths 列表；当前图只记录从整个 manifest_content 提取文档路径，无法从操作数据绑定确认使用 paths 字段。

源文：`SKILL.md:10-10`（`src_003`）。

> | 1 | input | 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 |

受控事实：`fact:/blocks/1/instructions/0`, `fact:/blocks/1/name`, `fact:/blocks/1/instructions/0/inputs/0`

程序映射的当前图位置：`/blocks/block_002/instructions/0`, `/blocks/block_002/block_name`, `/blocks/block_002/instructions/0/inputs/0`

修改建议：在 ir_003 的输入或 metadata 中明确记录 manifest 的 paths 列表/键作为文档路径来源；若用操作数表达，可增加相应 literal/context_key 操作数。

依据：保留源文指定的 paths 字段绑定，避免仅靠块名标签。

当前目标事实：`fact:/blocks/1/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_002/instructions/0/inputs/0`

### finding_9 · 遗漏

原文要求：逐个执行脚本，并且每次标准输出作为对应的转换产物路径。

当前回述：ir_007 以复数 opcode 接收 document_paths 列表并输出 converted_artifact_paths 列表；没有记录逐文档执行次数/循环，也没有把每个文档路径与其对应 stdout 建立对应关系。metadata 只保留单文档命令模板和脚本内容，且 metadata 未被解释为执行记录。

差异理由：源文明确要求逐项执行和 stdout→对应产物路径；当前图只有一个批量输入和批量结果，丢失执行次数与逐项对应。

源文：`SKILL.md:11-11`（`src_003`）。

> | 2 | convert | 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。 |

受控事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/metadata_json`

程序映射的当前图位置：`/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/metadata`

修改建议：在现有 IR 中补充逐文档执行与 stdout→对应转换产物路径的记录，例如通过逐项操作/结果或 metadata 映射明确保留次数和对应关系。

依据：避免复数批处理隐含逐项执行，保留源文次数和结果绑定。

当前目标事实：`fact:/blocks/3/instructions/0`

当前目标图位置：`/blocks/block_004/instructions/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 2 |
| `counts.audit_logical_calls` | 2 |
| `counts.total_logical_calls` | 4 |
| `counts.audit_execution_calls` | 2 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 4 |
| `counts.semantic_revisions` | 1 |
| `counts.structural_repairs` | 0 |
| `counts.http_attempts` | 4 |
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
