# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 12；遗漏 1 | {"actionable_ids": ["finding_8"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14"]}, "revision": 0, "semantic_items": 13, "status": "revise", "unknown_ids": []} |
| 1 | revise | 保留（模型判定） 12；错转 1；未决 1 | {"actionable_ids": ["finding_5"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13", "finding_14", "finding_18"]}, "revision": 1, "semantic_items": 14, "status": "revise", "unknown_ids": ["finding_15"]} |
| 2 | revise | 保留（模型判定） 11；错转 1 | {"actionable_ids": ["finding_13"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_15"]}, "revision": 2, "semantic_items": 12, "status": "revise", "unknown_ids": []} |
| 3 | audit_passed | 保留（模型判定） 12 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_13"]}, "revision": 3, "semantic_items": 12, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_8 · 遗漏

原文要求：打包时必须采用参考步骤命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip，并将转换产物路径列表传给 --paths。

当前回述：block_005 的 run_package_script 记录 scripts/package.py、result_005、字面量 bundle.zip；constraints/0 记录必须采用参考步骤命令并把列表传给 --paths。未把 bundle.zip 绑定到 --output，且参考命令文本本身未作为受控单元记录。

差异理由：源文对 --output bundle.zip 是显式命令参数；动作和字面量出现不等于数据绑定完整。metadata_json 虽保留 package.py 的 argparse 接口，但受控说明 metadata 完整保留、未解释、未执行，不能替代操作级输入绑定。

源文：`references/workflow.md:11-11`（`src_008`）。

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文：`references/workflow.md:16-16`（`src_010`）。

> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip

受控事实：`fact:/blocks/4/key`, `fact:/blocks/4/id`, `fact:/blocks/4/name`, `fact:/blocks/4/source`, `fact:/blocks/4/instructions`, `fact:/blocks/4/instructions/0`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/inputs/1`, `fact:/blocks/4/instructions/0/inputs/2`, `fact:/blocks/4/instructions/0/constraints/0`, `fact:/blocks/4/instructions/0/metadata_json`

程序映射的当前图位置：`/blocks/block_005/block_id`, `/blocks/block_005/block_name`, `/blocks/block_005/data_source_kind`, `/blocks/block_005/instructions`, `/blocks/block_005/instructions/0`, `/blocks/block_005/instructions/0/inputs/0`, `/blocks/block_005/instructions/0/inputs/1`, `/blocks/block_005/instructions/0/inputs/2`, `/blocks/block_005/instructions/0/constraints/0`, `/blocks/block_005/instructions/0/metadata`

修改建议：在打包约束或输入绑定中显式记录 --output bundle.zip，将 inputs/2 的 literal bundle.zip 绑定为 package 脚本的 --output 参数，同时保留 result_005 到 --paths 的绑定。

依据：源文要求采用参考命令，其中 --output bundle.zip 是显式参数；metadata 中的脚本接口不能替代操作级数据绑定。

当前目标事实：`fact:/blocks/4/instructions/0/constraints/0`, `fact:/blocks/4/instructions/0/inputs/2`

当前目标图位置：`/blocks/block_005/instructions/0/constraints/0`, `/blocks/block_005/instructions/0/inputs/2`

### 第 1 轮

### finding_5 · 错转

原文要求：按 manifest.json 中的 paths 列表获取文档路径。

当前回述：block_002 记录 extract_document_paths，输入 result_001(manifest_content)，输出 result_002(document_paths)；只有块名称标签提到 manifest paths list，操作输入没有 paths 列表或字段选择。

差异理由：动作存在，但源文明确的数据选择依据 paths 列表未在操作接口中可定位；按契约名称标签不能补造遗漏的数据绑定。

源文：`references/workflow.md:3-3`（`src_005`）。

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

受控事实：`fact:/blocks/1/key`, `fact:/blocks/1/id`, `fact:/blocks/1/name`, `fact:/blocks/1/source`, `fact:/blocks/1/instructions`, `fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`, `fact:/blocks/1/instructions/0/outputs/0`, `fact:/blocks/1/instructions/0/metadata_json`, `fact:/blocks/1/instructions/1`, `fact:/blocks/1/instructions/1/metadata_json`, `fact:/blocks/1/instructions/0/inputs/0:link`

程序映射的当前图位置：`/blocks/block_002/block_id`, `/blocks/block_002/block_name`, `/blocks/block_002/data_source_kind`, `/blocks/block_002/instructions`, `/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`, `/blocks/block_002/instructions/0/outputs/0`, `/blocks/block_002/instructions/0/metadata`, `/blocks/block_002/instructions/1`, `/blocks/block_002/instructions/1/metadata`

修改建议：在 ir_003 的输入/接口中显式记录从 result_001 的 paths 列表选择文档路径（例如增加表示 paths 列表选择依据的输入操作数）；不要让块名称标签独自承担该绑定。

依据：源文的 paths 列表是数据来源选择，必须可定位。

当前目标事实：`fact:/blocks/1/instructions/0`, `fact:/blocks/1/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_002/instructions/0`, `/blocks/block_002/instructions/0/inputs/0`

### finding_15 · 未决

原文要求：备注：必要时保留原顺序。源文没有明确限定该要求的阶段或范围。

当前回述：受控回述把它作为转换块 block_004 的块级约束 fact:/blocks/3/constraints/0，文本为“必要时保留原顺序。”

差异理由：文本一致，但源文未限定作用域；当前表示将作用域限定到转换块。若源文意图为全局顺序，则作用域缩小；若仅指转换顺序，则一致。给定文本不足以裁决。

源文：`references/workflow.md:27-27`（`src_014`）。

> 备注：必要时保留原顺序。

受控事实：`fact:/blocks/3/constraints/0`

程序映射的当前图位置：`/blocks/block_004/constraints/0`

未决原因：源文备注未明确作用域，受控回述将其限定到转换块，无法从现有文本判断是否忠实。

### 第 2 轮

### finding_13 · 错转

原文要求：源文末尾备注“必要时保留原顺序。”；该备注未写明仅适用于转换，且与明确“仅限转换”的标题要求不同。

当前回述：受控回述只把该文本记录为 block_004（转换块）的块级声明约束 /blocks/3/constraints/0。

差异理由：源文没有把“必要时保留原顺序”限定到转换块；它位于 workflow 末尾的备注，且源文对标题要求明确写了“仅限转换”。受控将其放在转换块级，缩小了作用域，可能影响打包、交付、回执等步骤的顺序要求。

源文：`references/workflow.md:27-27`（`src_014`）。

> 备注：必要时保留原顺序。

受控事实：`fact:/blocks/3/constraints/0`

程序映射的当前图位置：`/blocks/block_004/constraints/0`

修改建议：将该约束提升为图级约束，或按源文未限定转换的备注扩大作用域；不要仅保留在转换块下。

依据：源文备注没有转换限定，受控的块级作用域比源文更窄。

当前目标事实：`fact:/blocks/3/constraints/0`

当前目标图位置：`/blocks/block_004/constraints/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 6 |
| `counts.audit_logical_calls` | 4 |
| `counts.total_logical_calls` | 10 |
| `counts.audit_execution_calls` | 4 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 10 |
| `counts.semantic_revisions` | 3 |
| `counts.structural_repairs` | 2 |
| `counts.http_attempts` | 10 |
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
| 3 | complete / passed | passed | complete |

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |
| 2 | 1 | complete | 否 |
| 3 | 1 | complete | 否 |

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
