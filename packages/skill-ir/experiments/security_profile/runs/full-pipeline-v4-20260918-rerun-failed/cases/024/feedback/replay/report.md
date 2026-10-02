# CFG 构建语义反馈闭环

停止状态：**核对器通过**（`audit_passed`）。

停止原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。

解释契约：`skill-ir-semantic-contract-v2`；摘要：`bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1`。

“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。

## 逐轮差异与停止决策

每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。

| 语义轮次 | 状态 | 业务核对 | 决策 |
|---|---|---|---|
| 0 | revise | 保留（模型判定） 9；遗漏 2；未决 1 | {"actionable_ids": ["finding_5", "finding_7"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_6", "finding_8", "finding_9", "finding_10", "finding_11", "finding_14"]}, "revision": 0, "semantic_items": 12, "status": "revise", "unknown_ids": ["finding_12"]} |
| 1 | revise | 保留（模型判定） 12；遗漏 2 | {"actionable_ids": ["finding_5", "finding_13"], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "存在明确差异；按当前图和本轮证据重新完整提取，保留未决。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10", "finding_11", "finding_12", "finding_14", "finding_15"]}, "revision": 1, "semantic_items": 14, "status": "revise", "unknown_ids": []} |
| 2 | audit_passed | 保留（模型判定） 9 | {"actionable_ids": [], "contract_sha256": "bdee4d95241e67e861f74be279c5862df571ea3af208a81c8dab744e0b4f65d1", "contract_version": "skill-ir-semantic-contract-v2", "max_semantic_revisions": 3, "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。", "reason": "所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。", "representation_summary": {"conservative_ids": [], "represented_ids": ["finding_2", "finding_3", "finding_4", "finding_5", "finding_6", "finding_7", "finding_8", "finding_9", "finding_10"]}, "revision": 2, "semantic_items": 9, "status": "audit_passed", "unknown_ids": []} |

## 最后一轮差异、未决和修改建议

最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。

## 最后一轮保守保留的依赖

符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。

最后一轮无合法的保守保留项。

## 历史轮次差异

### 第 0 轮

### finding_5 · 遗漏

原文要求：源文第1条要求按 manifest.json 中的 paths 列表获取文档路径。

当前回述：block_003 记录 ir_005 extract_paths_from_manifest，输入 result_001 manifest_data，输出 result_004 document_paths；但未记录输入是 manifest_data 中的 paths 列表，也没有字段/键 paths 的显式绑定或约束。

差异理由：提取文档路径这一动作和结果存在，但源文明确的数据来源是 manifest 的 paths 列表；受控仅有开放 opcode 名称，不能仅凭名称补造其内部按 paths 取值。故该局部绑定遗漏。

源文：`SKILL.md:8-8`（`src_003`）。

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

受控事实：`fact:/blocks/2/key`, `fact:/blocks/2/id`, `fact:/blocks/2/name`, `fact:/blocks/2/source`, `fact:/blocks/2/instructions`, `fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`, `fact:/blocks/2/instructions/0/outputs/0`, `fact:/blocks/2/instructions/0/metadata_json`, `fact:/blocks/2/instructions/1`, `fact:/blocks/2/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_003/block_id`, `/blocks/block_003/block_name`, `/blocks/block_003/data_source_kind`, `/blocks/block_003/instructions`, `/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`, `/blocks/block_003/instructions/0/outputs/0`, `/blocks/block_003/instructions/0/metadata`, `/blocks/block_003/instructions/1`, `/blocks/block_003/instructions/1/metadata`

修改建议：在现有提取操作或其输入/约束上补充 manifest_data 的 paths 列表到 document_paths 的显式数据选择关系。

依据：当前仅记录从 manifest_data 提取 document_paths，未记录按 paths 列表这一源文绑定。

当前目标事实：`fact:/blocks/2/instructions/0`, `fact:/blocks/2/instructions/0/inputs/0`

当前目标图位置：`/blocks/block_003/instructions/0`, `/blocks/block_003/instructions/0/inputs/0`

### finding_7 · 遗漏

原文要求：源文第5条要求打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths；参考步骤命令为 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip。

当前回述：block_005 记录 run_package_script，输入 scripts/package.py、result_005 converted_paths、literal "bundle.zip"，输出 result_006 bundle_zip_path；操作级约束写“必须采用下方‘参考步骤’的命令，并将转换产物路径列表传给 --paths”。未记录参考步骤命令原文/代码块，也未显式记录 bundle.zip 绑定到 --output（或 python 解释器）。

差异理由：打包动作、脚本资源、转换路径输入、bundle.zip 字面量与 --paths 约束均存在，但“必须采用参考步骤命令”和 --output 参数绑定是源文显式要求；当前只能从字面量推断 bundle.zip 的用途，不能仅靠 metadata 或名称补齐，故该组合存在局部遗漏。

源文：`SKILL.md:12-12`（`src_003`）。

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文：`SKILL.md:21-23`（`src_005`）。

> ```sh
> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip
> ```

受控事实：`fact:/blocks/4/key`, `fact:/blocks/4/id`, `fact:/blocks/4/name`, `fact:/blocks/4/source`, `fact:/blocks/4/instructions`, `fact:/blocks/4/instructions/0`, `fact:/blocks/4/instructions/0/inputs/0`, `fact:/blocks/4/instructions/0/inputs/1`, `fact:/blocks/4/instructions/0/inputs/2`, `fact:/blocks/4/instructions/0/outputs/0`, `fact:/blocks/4/instructions/0/constraints/0`, `fact:/blocks/4/instructions/0/metadata_json`, `fact:/blocks/4/instructions/1`, `fact:/blocks/4/instructions/1/metadata_json`

程序映射的当前图位置：`/blocks/block_005/block_id`, `/blocks/block_005/block_name`, `/blocks/block_005/data_source_kind`, `/blocks/block_005/instructions`, `/blocks/block_005/instructions/0`, `/blocks/block_005/instructions/0/inputs/0`, `/blocks/block_005/instructions/0/inputs/1`, `/blocks/block_005/instructions/0/inputs/2`, `/blocks/block_005/instructions/0/outputs/0`, `/blocks/block_005/instructions/0/constraints/0`, `/blocks/block_005/instructions/0/metadata`, `/blocks/block_005/instructions/1`, `/blocks/block_005/instructions/1/metadata`

修改建议：在现有打包操作/约束中补充参考命令文本或至少显式记录 --paths→result_005、--output→literal "bundle.zip" 的参数绑定。

依据：源文要求采用参考步骤命令并传给 --paths；当前未显式记录参考命令和 --output 绑定。

当前目标事实：`fact:/blocks/4/instructions/0/constraints/0`, `fact:/blocks/4/instructions/0/inputs/2`

当前目标图位置：`/blocks/block_005/instructions/0/constraints/0`, `/blocks/block_005/instructions/0/inputs/2`

### finding_12 · 未决

原文要求：源文第10条备注：“必要时保留原顺序。”源文未明确该备注的作用域、是否为强制约束，或仅针对某些步骤。

当前回述：受控在 block_004（转换）和 block_005（打包）的块级约束中记录“必要时保留原顺序”；未在其他块或图级记录同一备注。

差异理由：受控把原备注文字放入两个具体块，但源文没有限定只应用于这两个块，也未明确其规范强度；无法判断该局部化是忠实解释还是范围改变，故未决。

源文：`SKILL.md:17-17`（`src_003`）。

> 10. 备注：必要时保留原顺序。

受控事实：`fact:/blocks/3/constraints/0`, `fact:/blocks/4/constraints/0`

程序映射的当前图位置：`/blocks/block_004/constraints/0`, `/blocks/block_005/constraints/0`

未决原因：源文备注作用域与规范强度不明确，且受控只将其放在两个块，无法裁决这种局部化是否忠实。

### 第 1 轮

### finding_5 · 遗漏

原文要求：把每次标准输出作为对应的转换产物路径。

当前回述：ir_007 仅记录聚合输出 result_005 converted_paths，没有记录该输出来自每次执行的标准输出，也没有记录 result_002 中各文档路径与对应转换产物路径的逐项对应。

差异理由：源文明确 stdout 是转换产物路径的数据来源并要求逐项对应；操作名和 converted_paths 标签不能替代该显式绑定，metadata 中的 print(output) 未被解释，不能作为图内绑定依据。

源文：`SKILL.md:9-9`（`src_003`）。

> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

受控事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/metadata_json`, `fact:/blocks/3/instructions/0/inputs/1`

程序映射的当前图位置：`/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/metadata`, `/blocks/block_004/instructions/0/inputs/1`

修改建议：在现有转换操作的声明/输出描述或 metadata 中明确记录 result_005 是每次执行 scripts/convert.py 的标准输出组成的转换产物路径集合，并与 result_002 中对应文档路径逐项对应。

依据：补上源文明确的数据来源和对应关系，不改变脚本黑盒边界。

当前目标事实：`fact:/blocks/3/instructions/0`, `fact:/blocks/3/instructions/0/outputs/0`

当前目标图位置：`/blocks/block_004/instructions/0`, `/blocks/block_004/instructions/0/outputs/0`

### finding_13 · 遗漏

原文要求：备注：必要时保留原顺序。

当前回述：受控图未在图级或操作级约束中记录“必要时保留原顺序”，也未在 result_002 document_paths、result_005 converted_paths 或后续打包/回执使用中声明顺序保持要求；仅以输入/输出列表按记录次序出现。

差异理由：源文虽以备注开头，但内容包含条件性顺序保持要求；列表按记录次序不等于声明保留从 manifest paths 取得或转换后的原顺序。

源文：`SKILL.md:17-17`（`src_003`）。

> 10. 备注：必要时保留原顺序。

受控事实：`fact:/blocks/1/instructions/0/outputs/0`, `fact:/blocks/3/instructions/0/inputs/1`, `fact:/blocks/3/instructions/0/outputs/0`, `fact:/blocks/4/instructions/0/inputs/2`, `fact:/blocks/7/instructions/0/inputs/0`

程序映射的当前图位置：`/blocks/block_002/instructions/0/outputs/0`, `/blocks/block_004/instructions/0/inputs/1`, `/blocks/block_004/instructions/0/outputs/0`, `/blocks/block_005/instructions/0/inputs/2`, `/blocks/block_008/instructions/0/inputs/0`

修改建议：在现有相关操作的声明约束或图级约束中补充：必要时保留原顺序，并明确该顺序适用于从 manifest paths 得到并用于后续转换/打包/回执的路径列表。

依据：补上遗漏的条件性顺序要求，锚定已有相关操作，不新增业务步骤。

当前目标事实：`fact:/blocks/1/instructions/0`, `fact:/blocks/3/instructions/0`, `fact:/blocks/4/instructions/0`

当前目标图位置：`/blocks/block_002/instructions/0`, `/blocks/block_004/instructions/0`, `/blocks/block_005/instructions/0`

## 工程执行与证据

| 计数或上限 | 实际记录 |
|---|---|
| `counts.extraction_logical_calls` | 3 |
| `counts.audit_logical_calls` | 3 |
| `counts.total_logical_calls` | 6 |
| `counts.audit_execution_calls` | 3 |
| `counts.audit_execution_retries` | 0 |
| `counts.total_execution_calls` | 6 |
| `counts.semantic_revisions` | 2 |
| `counts.structural_repairs` | 0 |
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
| 1 | complete / passed | passed | complete |
| 2 | complete / passed | passed | complete |

### 核对执行重试

一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。

| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |
|---|---|---|---|
| 0 | 1 | complete | 否 |
| 1 | 1 | complete | 否 |
| 2 | 1 | complete | 否 |

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
