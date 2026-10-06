# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 5；遗漏 1；错转 1 | {"actionable_ids": ["finding_4", "finding_6"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_5", "finding_7", "finding_8"]}, "revision": 0, "semantic_items": 7, "status": "revise", "unknown_ids": []} |
| 1 | audit_passed | 保留（模型判定） 11 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_graph_constraints", "finding_read_manifest", "finding_extract_paths", "finding_request_settings_contexts", "finding_convert_flow", "finding_convert_script", "finding_package_command", "finding_package_script", "finding_bundle_delivery", "finding_control_order", "finding_history_receipt"]}, "revision": 1, "semantic_items": 11, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_4 · 遗漏

原文要求：从 manifest 中按 paths 列表获取文档路径。

当前回述：block_002 与 ir_003 表示从 manifest 提取 document_paths；ir_003 输入 result_001 manifest_content，输出 result_002 document_paths；ir_004 dispatch 进入下一块；未记录 paths 字段/列表的选择或绑定。

差异理由：源文明确路径来自 manifest 的 paths 列表，这是数据来源绑定；受控只有整个 manifest_content 输入，opcode 名 extract_document_paths_from_manifest 不能补出未记录的字段选择。

源文：`SKILL.md:8-8`（`src_003`）。

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

受控事实：`fact:/blocks/1/key`, `fact:/blocks/1/id`, `fact:/blocks/1/name`, `fact:/blocks/1/source`, `fact:/blocks/1/instructions`, `fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`, `fact:/blocks/1/instructions/0/outputs/0`, `fact:/blocks/1/instructions/0/metadata_json`, `fact:/blocks/1/instructions/1`, `fact:/blocks/1/instructions/1/metadata_json`, `fact:/blocks/1/instructions/0/inputs/0:link`

程序映射的当前图位置：`/blocks/block_002/block_id`, `/blocks/block_002/block_name`, `/blocks/block_002/data_source_kind`, `/blocks/block_002/instructions`, `/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`, `/blocks/block_002/instructions/0/outputs/0`, `/blocks/block_002/instructions/0/metadata`, `/blocks/block_002/instructions/1`, `/blocks/block_002/instructions/1/metadata`

修改建议：在 ir_003 的操作输入或操作级约束中显式记录按 manifest 的 paths 列表提取文档路径，例如增加字段/字面量操作数 paths（或等价的显式字段选择声明），不要只依赖 opcode 名称。

依据：补回源文明确的 data binding：文档路径来自 manifest 的 paths 列表。

当前目标事实：`fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`

### finding_6 · 错转

原文要求：逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径；转换期间保留原文标题；转换通过 scripts/convert.py 完成，主流程只使用脚本输出路径，不重复执行脚本内部处理。

当前回述：block_004 和 ir_007 convert_documents_with_convert_script 以 result_002 document_paths 列表和 result_003 output_dir 为输入，输出 result_005 conversion_artifact_paths；约束记录保留原文标题和通过 scripts/convert.py/不重复内部处理；metadata 保留 invocation_template 和 convert.py 完整脚本文本。没有显式逐文档重复执行，也没有逐次 stdout 到对应产物的绑定/顺序映射。

差异理由：脚本、输出目录、输出列表、标题保留和脚本边界已记录；但源文明确要求逐个文档执行并把每次 stdout 对应到该文档的转换产物。受控把该过程折叠为一个批量操作和 plural result，不能从 opcode 或未解释 metadata 中补出逐项调用和映射。因此该组合要求存在局部错转/遗漏，不能整项标为 represented。

源文：`SKILL.md:9-9`（`src_003`）。

> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文：`SKILL.md:10-10`（`src_003`）。

> 3. 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

源文：`SKILL.md:11-11`（`src_003`）。

> 4. 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

源文：`scripts/convert.py:1-1`（`src_006`）。

> """Convert one UTF-8 text document and print the output path."""

源文：`scripts/convert.py:5-5`（`src_007`）。

> source = Path(sys.argv[1])

源文：`scripts/convert.py:10-10`（`src_007`）。

> print(output)

受控事实：`fact:/blocks/3/key`, `fact:/blocks/3/id`, `fact:/blocks/3/name`, `fact:/blocks/3/source`, `fact:/blocks/3/instructions`, `fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/inputs/0`, `fact:/blocks/3/instructions/0/inputs/1`, `fact:/blocks/3/instructions/0/inputs/2`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/constraints/0`, `fact:/blocks/3/instructions/0/constraints/1`, `fact:/blocks/3/instructions/0/metadata_json`, `fact:/blocks/3/instructions/1`, `fact:/blocks/3/instructions/1/metadata_json`, `fact:/blocks/3/instructions/0/inputs/1:link`, `fact:/blocks/3/instructions/0/inputs/2:link`, `fact:/edges/3`

程序映射的当前图位置：`/blocks/block_004/block_id`, `/blocks/block_004/block_name`, `/blocks/block_004/data_source_kind`, `/blocks/block_004/instructions`, `/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/inputs/0`, `/blocks/block_004/instructions/0/inputs/1`, `/blocks/block_004/instructions/0/inputs/2`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/constraints/0`, `/blocks/block_004/instructions/0/constraints/1`, `/blocks/block_004/instructions/0/metadata`, `/blocks/block_004/instructions/1`, `/blocks/block_004/instructions/1/metadata`, `/edges/3`

修改建议：在 ir_007 或操作级约束中显式记录：对 result_002 的每个文档路径分别调用 scripts/convert.py，并将该次调用的 stdout 绑定为 result_005 中对应产物路径，且保持输入顺序；不要让单个批量 opcode 和 plural result 代替该逐项执行/映射。

依据：源文明确要求逐个执行并把每次标准输出作为对应产物路径，当前记录缺少逐项调用和 stdout→对应产物的绑定。

当前目标事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/constraints/0`, `fact:/blocks/3/instructions/0/constraints/1`

当前目标图位置：`/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/constraints/0`, `/blocks/block_004/instructions/0/constraints/1`

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
