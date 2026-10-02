# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 12；遗漏 3 | {"actionable_ids": ["finding_3", "finding_5", "finding_12"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_4", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_13", "finding_14", "finding_15", "finding_16"]}, "revision": 0, "semantic_items": 15, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 13 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4a", "finding_4b", "finding_4c", "finding_4d", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11"]}, "revision": 1, "semantic_items": 13, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_3 · 遗漏

原文要求：按 manifest 中的 paths 列表获取文档路径。

当前回述：block_002 记录 extract_document_paths_from_manifest，输入 result_001 manifest_content，输出 result_002 document_paths；记录中没有显式操作数、字段名或声明约束表明使用 manifest 的 paths 列表。

差异理由：开放 opcode 和块名只能说明从 manifest 提取文档路径，不能证明读取的是 paths 字段；该数据绑定在受控回述中缺失。

源文：`SKILL.md:8-8`（`src_003`）。

> 按其中 paths 列表获取文档路径

受控事实：`fact:/blocks/1/key`, `fact:/blocks/1/id`, `fact:/blocks/1/name`, `fact:/blocks/1/source`, `fact:/blocks/1/instructions`, `fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`, `fact:/blocks/1/instructions/0/outputs/0`, `fact:/blocks/1/instructions/0/metadata_json`, `fact:/blocks/1/instructions/1`, `fact:/blocks/1/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_002/block_id`, `/blocks/block_002/block_name`, `/blocks/block_002/data_source_kind`, `/blocks/block_002/instructions`, `/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`, `/blocks/block_002/instructions/0/outputs/0`, `/blocks/block_002/instructions/0/metadata`, `/blocks/block_002/instructions/1`, `/blocks/block_002/instructions/1/metadata`

修改建议：补充声明约束或显式字段绑定，说明 extract_document_paths_from_manifest 使用 manifest_content 中的 paths 列表得到 document_paths。

依据：源文明确要求按 paths 列表获取文档路径，当前只记录从 manifest 内容提取，缺少字段级绑定。

当前目标事实：`fact:/blocks/1/instructions/0`

当前目标图位置：`/blocks/block_002/instructions/0`

### finding_5 · 遗漏

原文要求：把每次标准输出作为对应的转换产物路径。

当前回述：ir_007 输出 result_005 converted_artifact_paths，且 constraints/1 说主流程只使用脚本输出路径；但没有显式记录标准输出通道，也没有记录每次调用输出与对应文档路径的一一对应关系。metadata 中虽有 print(output)，但 metadata 仅保留未解释，不能替代该业务绑定。

差异理由：源文明确把每次标准输出作为对应转换产物路径；受控图只给出脚本输出或产物路径列表，缺少 stdout 与 per-document 对应绑定。

源文：`SKILL.md:9-9`（`src_003`）。

> 把每次标准输出作为对应的转换产物路径

受控事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/constraints/1`, `fact:/blocks/3/instructions/0/metadata_json`

程序映射的当前图位置：`/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/constraints/1`, `/blocks/block_004/instructions/0/metadata`

修改建议：补充操作级声明约束，说明 ir_007 每次执行 scripts/convert.py 的标准输出作为对应文档的转换产物路径，结果收集为 result_005。

依据：当前只记录 converted_artifact_paths 结果和脚本输出路径约束，缺少源文明示的 stdout 到 per-document 产物路径绑定。

当前目标事实：`fact:/blocks/3/instructions/0`

当前目标图位置：`/blocks/block_004/instructions/0`

### finding_12 · 遗漏

原文要求：备注：必要时保留原顺序。

当前回述：图中只有块级顺序边 edges/0 到 edges/5 和列表操作数，未记录任何声明约束或条件来要求在必要时保留文档或路径的原顺序。

差异理由：源文将“必要时保留原顺序”列为第 10 项；受控回述没有对应约束、条件或作用域说明。不能仅由顺序边推得文档列表顺序保留。

源文：`SKILL.md:17-17`（`src_003`）。

> 10. 备注：必要时保留原顺序。

受控事实：`fact:/edges/0`, `fact:/edges/1`, `fact:/edges/2`, `fact:/edges/3`, `fact:/edges/4`, `fact:/edges/5`, `fact:/blocks/3/instructions/0/inputs/1`, `fact:/blocks/4/instructions/0/inputs/1`, `fact:/blocks/6/instructions/0/inputs/0`

程序映射的当前图位置：`/edges/0`, `/edges/1`, `/edges/2`, `/edges/3`, `/edges/4`, `/edges/5`, `/blocks/block_004/instructions/0/inputs/1`, `/blocks/block_005/instructions/0/inputs/1`, `/blocks/block_007/instructions/0/inputs/0`

修改建议：补充声明约束，说明在必要时保留 document_paths/converted_artifact_paths 的原顺序（例如转换、打包、写入 receipt 时保持对应顺序）。

依据：源文第 10 项要求必要时保留原顺序，当前图只有控制块顺序边，没有文档或路径列表顺序保留的声明或条件。

当前目标事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/4/instructions/0`, `fact:/blocks/6/instructions/0`

当前目标图位置：`/blocks/block_004/instructions/0`, `/blocks/block_005/instructions/0`, `/blocks/block_007/instructions/0`

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
