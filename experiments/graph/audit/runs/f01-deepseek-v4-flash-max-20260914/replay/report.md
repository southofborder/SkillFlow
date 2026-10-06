# F01 语义回溯首次对照实验

运行：`f01-deepseek-v4-flash-max-20260914`；模式：`replay`。

本报告区分工程执行、模型判定和外置评测。模型判定尚不构成形式化保真证明；`unknown` 不按通过处理。

## 工程执行

计划 21 次逻辑调用，已留存 18 次；执行状态：`completed_with_errors`。
配置：`deepseek-v4-flash` / `max`；每个角色独立上下文，无自动修复或择优。

| 输入 | 连贯回译 | 源文→图 | 图→结构化 | 图→自然语言 |
|---|---|---|---|---|
| c01 | complete | execution_error | complete | complete |
| c02 | complete | execution_error | complete | complete |
| c03 | execution_error | execution_error | complete | blocked |
| c04 | execution_error | execution_error | complete | blocked |
| c05 | execution_error | execution_error | complete | blocked |

### 执行错误或依赖阻断

- `c01/source_graph`：graph reference does not exist: '/blocks/block_008/constraints/0'
- `c02/source_graph`：graph reference does not exist: '/blocks/block_008/constraints/0'
- `c03/narrative`：graph reference does not exist: '/blocks/block_011/constraints/0'
- `c03/source_graph`：graph reference does not exist: '/blocks/block_011/constraints/1'
- `c03/graph_narrative`：Narrative generation failed
- `c04/narrative`：graph reference does not exist: '/blocks/block_011/constraints/0'
- `c04/source_graph`：graph reference does not exist: '/blocks/block_011/constraints/1'
- `c04/graph_narrative`：Narrative generation failed
- `c05/narrative`：graph reference does not exist: '/blocks/block_011/constraints/0'
- `c05/source_graph`：graph reference does not exist: '/blocks/block_011/constraints/1'
- `c05/graph_narrative`：Narrative generation failed

## 差异与未决项

下表保留核对器的实际结论；不能直接当作已确认缺陷。保留项的完整判断、引文、定位与理由均在 `report.json` 和 `parsed/` 中。

### c01

**源文 → 图（两种回述共用）**

执行状态：`execution_error`。本层未取得有效核对结果。

**图 → 结构化回述**

保留 7。

**图 → 自然语言回译**

保留 6。

### c02

**源文 → 图（两种回述共用）**

执行状态：`execution_error`。本层未取得有效核对结果。

**图 → 结构化回述**

保留 32；内部冲突 1。

| ID / 类别 | 具体陈述及理由 | 证据位置 |
|---|---|---|
| finding_33 / 内部冲突 | 图中 archive.fetch 调用约束与实际输入是否一致，以及回述是否如实保留该冲突。<br>图级约束 /constraints/0 禁止向 archive.fetch 传 FAST_KEY；/blocks/block_011/instructions/0/constraints/1 要求 archive.fetch 仅以 source_id 为参数。但 /blocks/block_011/instructions/0/inputs/2 显式以 result_002（semantic_name 为 fast_key）为输入。回述 global_constraints 与 block:/block_011 同时原样列出这些声明和输入，未补写执行行为、未删除任一侧，因此这是图内冲突而非回述遗漏或错转。 | /constraints/0; /blocks/block_011/instructions/0/constraints/1; /blocks/block_011/instructions/0/inputs/2; text:global_constraints; text:block:/block_011 |

**图 → 自然语言回译**

保留 14；内部冲突 1；未决 1。

| ID / 类别 | 具体陈述及理由 | 证据位置 |
|---|---|---|
| finding_11 / 内部冲突 | unit_11 对 block_011、三个入口边、ir_021、ir_022、/edges/12 及操作级约束的叙述与图一致，同时保留 ir_021 的 result_002 输入与 FAST_KEY 禁令之间的未消解冲突。<br>图中 block_011 的 data_source_kind=external；入口边 /edges/3、/edges/8、/edges/11 的条件文字分别为 FAST_KEY is absent、first fast.fetch failure was non-transient、fast.fetch retry failed；操作级约束要求非 transient 首次失败或重试失败后调用 archive.fetch，最多一次且仅传 source_id，失败即停止返回错误；ir_021 显式输入为 archive.fetch、result_001、result_002，输出 result_011 与 result_012；ir_022 为 dispatch；/edges/12 的 condition_text 为 null，回述仅陈述其连接而未附加条件，相符。回述保留 result_002（fast_key）与 /constraints/0 及操作级 source_id-only 约束的冲突，未把约束当作已履行，也未删除或补回输入绑定。 | /blocks/block_011; /blocks/block_011/instructions/0; /blocks/block_011/instructions/0/inputs/2; /blocks/block_011/instructions/0/constraints/0; /blocks/block_011/instructions/0/constraints/1; /blocks/block_011/instructions/0/constraints/2; /blocks/block_011/instructions/1; /constraints/0; /edges/3; /edges/8; /edges/11; /edges/12; text:unit_11 |
| finding_16 / 未决 | 图级约束 /constraints/0 中 diagnostic output 部分是否映射到具体图操作，无法在操作层裁决。<br>图中 /constraints/0 明确包含不得向 diagnostic output 传递 FAST_KEY 的禁令，但图中没有显式 diagnostic output 操作、输入或输出标识可供核对；回述 unit_15 已说明当前图没有对应的显式操作标识，未补造诊断输出操作。因此该部分只能作为证据缺口处理。<br>未决原因：图中仅有 diagnostic output 约束文字，没有显式诊断输出操作及其输入、输出标识，无法裁决该约束是否已映射到具体图操作。 | /constraints/0; text:unit_15 |

### c03

**源文 → 图（两种回述共用）**

执行状态：`execution_error`。本层未取得有效核对结果。

**图 → 结构化回述**

保留 18；内部冲突 1。

| ID / 类别 | 具体陈述及理由 | 证据位置 |
|---|---|---|
| finding_19 / 内部冲突 | 图内失败路径追加状态约束与 block_014 实际指令缺失的冲突，回述是否保留而未补回。<br>global_constraints 要求每个成功或失败路径返回前追加最终状态到 status.txt；block_014 名称也提到追加失败状态，但其 instructions 仅含 ir_028 return result_012。回述同时保留该约束、块名标签和缺失操作，未新增 append 操作，因此图内冲突或证据缺口未被掩盖，但回述也未将其显式命名为冲突。 | /constraints/1; /blocks/block_014; /blocks/block_014/instructions/0; text:global_constraints; text:block:/block_014 |

**图 → 自然语言回译**

执行状态：`blocked`。本层未取得有效核对结果。

### c04

**源文 → 图（两种回述共用）**

执行状态：`execution_error`。本层未取得有效核对结果。

**图 → 结构化回述**

保留 18；内部冲突 1。

| ID / 类别 | 具体陈述及理由 | 证据位置 |
|---|---|---|
| finding_19 / 内部冲突 | 图级约束 On either tool's success, return that successful response's body value unchanged and make no further fetch calls 与 block_010 在 fast.fetch 重试成功后 return result_004 的绑定需要消解。<br>图中 block_008/ir_015 的 retry_fast_fetch 输出 result_008；block_010/ir_020 的 return 输入是 result_004，而 result_004 定义于 block_004/ir_007 的第一个输出。回述 global_constraints 与 block:/block_010 都忠实保留了原始声明和绑定，但未说明重试成功后为何返回首次 fast.fetch 的输出而非重试输出；这构成图内未消解冲突或证据缺口，不能据此判定回述错转。 | /constraints/2; /blocks/block_008/instructions/0/outputs/0; /blocks/block_010/instructions/1/inputs/0; /blocks/block_004/instructions/0/outputs/0; text:global_constraints; text:block:/block_010; text:block:/block_008 |

**图 → 自然语言回译**

执行状态：`blocked`。本层未取得有效核对结果。

### c05

**源文 → 图（两种回述共用）**

执行状态：`execution_error`。本层未取得有效核对结果。

**图 → 结构化回述**

保留 32。

**图 → 自然语言回译**

执行状态：`blocked`。本层未取得有效核对结果。

## 外置预期的证据匹配

这里只生成复核候选：类别一致且源文/图证据区域相交，并不判断理由的语义正确性，不计算准确率。

| 输入 | 人工预期 ID | 匹配状态 | 模型问题 ID |
|---|---|---|---|
| c01 | baseline-gold-r01 | execution_error |  |
| c01 | baseline-gold-r02 | execution_error |  |
| c01 | baseline-gold-r03 | execution_error |  |
| c01 | baseline-gold-r04 | execution_error |  |
| c02 | archive-receives-credential | execution_error |  |
| c03 | failure-status-append-missing | execution_error |  |
| c04 | retry-returns-first-body | execution_error |  |
| c05 | added-two-second-wait | execution_error |  |

## 边界与可复核材料

- 约束声明不等于运行保证；开放操作的内部副作用与文件写入成功未证明。
- 图中的错误与回述不忠实分别归层；忠实地回述错误图，不属于回述错误。
- F01 不含脚本 metadata；本轮没有验证通用脚本理解，也没有新增 Lean 证明。
- `inputs/`：摘要绑定的源文、五份当前 CFG、图证据及确定性结构化回述。
- `calls/`：每个角色的原始提示词、响应、摘要和 SSE 记录；`parsed/`：严格解析结果。
- `texts/`：连贯回译全文；`replay/`：严格离线重放结果（若已执行）。
- 工程测试结果和人工方法复核另见同目录 `acceptance.md`（完成复核后生成）。
