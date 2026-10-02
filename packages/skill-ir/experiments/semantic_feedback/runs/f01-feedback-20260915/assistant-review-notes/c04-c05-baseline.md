# c04 / c05 初始图的独立助手复核

复核身份：**助手独立复核，未经过用户确认**。这是本轮实验的事后评测材料，不是模型输入、源文要求提取结果或自动评分答案。本记录依据完整冻结 `SKILL.md` 与本次实际 `inputs/c04-analysis.json`、`inputs/c05-analysis.json` 编写；未读取外置 oracle 或模型核对结论，未调用 API，未执行 Skill 中的操作。

## 复核对象与摘要

路径以仓库 `D:/projects/SkillFlow` 为基准。

| 对象 | 路径 | 原始文件 SHA-256 |
|---|---|---|
| 完整源文 | `packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md` | `90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495` |
| c04 初始图 | `packages/skill-ir/experiments/semantic_feedback/runs/f01-feedback-20260915/inputs/c04-analysis.json` | `be1ff433a3f4cb67d7f82546ed854dfb638d48a46ac243799eaf21291a9c6d49` |
| c05 初始图 | `packages/skill-ir/experiments/semantic_feedback/runs/f01-feedback-20260915/inputs/c05-analysis.json` | `9eb9c057f248795353718cbfe16b7d649feb242535afe13578422f262fffe763` |

两图均有 14 个块、15 条边，并通过当前 `ControlFlowGraph.validate_integrity()`。结构有效只说明记录满足当前结构规则，不消除下面的语义缺陷。

## 完整源文要求的复核范围

源文共 16 行。以下条目覆盖第 8–16 行的九项业务要求，同时保留名称、描述和标题作为背景，不将它们作为替代业务步骤。

| 源文行 | 本次逐图检查的内容 |
|---|---|
| 8 | `source_id` 来自用户请求，`FAST_KEY` 来自环境；后续操作使用这两个来源实际产生的结果。 |
| 9 | 密钥存在时先调用 fast；密钥缺失时直接进入 archive，不调用 fast。 |
| 10 | 仅首次 fast 失败且错误为 transient 时重试一次；首次 non-transient 失败不重试。 |
| 11 | 首次 non-transient 失败、重试发生任何失败，都进入 archive。 |
| 12 | archive 至多调用一次；业务参数只有 `source_id`。标明被调用资源的 `external_resource: archive.fetch` 不另算业务参数。 |
| 13 | 每一种成功路径返回本次成功响应的 body，不改值；成功后无进一步获取。首次 fast 和重试 fast 的结果身份不能互换。 |
| 14 | archive 失败后返回 archive 错误并停止，不重试 archive。 |
| 15 | 密钥不得传给 archive 或诊断输出，作用于整个流程。图中的声明应保留，但声明不等于运行时保证。 |
| 16 | 每条成功或失败返回路径，在返回前追加最终状态到本地 `status.txt`。状态的具体字符串格式未规定，文件写入成功未证明。 |

## c04：重试成功后的返回绑定错误

判定：**明确错转**；同时与图自身的成功返回约束存在冲突。两种表述描述的是同一个根本缺陷，不重复计算两个独立缺陷。

源文第 13 行要求：

> On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

实际定义与使用证据如下：

| 记录 | 实际位置与内容 |
|---|---|
| 首次 fast 的 body 定义 | `/blocks/block_004/instructions/0/outputs/0`：`ir_007` 的输出 `result_004`，标签 `fast_fetch_response_body`。 |
| 重试 fast 的 body 定义 | `/blocks/block_008/instructions/0/outputs/0`：`ir_015` 的输出 `result_008`，标签 `retry_fast_fetch_response_body`。 |
| 重试成功的控制入口 | `/edges/10`：`block_009 → block_010`，条件 `fast.fetch retry succeeded`。 |
| 重试成功返回的实际使用 | `/blocks/block_010/instructions/1/inputs/0`：`ir_020` 返回 `result_004`，不是重试定义的 `result_008`。 |
| 同一路径的状态记录 | `/blocks/block_010/instructions/0`：`ir_019` 在返回前追加 `success`。 |
| 图中约束声明 | `/constraints/2` 仍要求返回实际成功响应的 body。 |

关键问题由结果的定义—使用关系确定，不由相似名字推测：即使 `draft_instruction_id` 仍写着 `return_retry_fast_fetch_body`，返回操作实际引用的仍是首次调用产生的值。图中当前块标题也承认在重试成功后返回首次 body，但标题不是主要证据。

更不能把此缺陷误称为“没有重试”或“成功后又调用了一次工具”：实际图中仍然存在恰好一次重试，重试成功之后是状态追加和返回，没有进一步获取。错误是**返回了哪次调用的结果**。

后续重提取图应检查：从实际 fast 重试操作的输出重新追踪其成功出口的返回值；如果模型改为输出完整响应再投影 body，也需逐步核对投影来源。新图 ID 可以全部改变，不能靠看到 `result_008` 或旧图指针来宣布修好。只修改名字、只追加一条正确约束、删掉重试路径，均不算修复。

## c05：首次失败分类后无依据追加两秒等待

判定：**无依据新增操作**。源文没有等待时长、等待步骤或 backoff 要求；这不等于源文显式写了“禁止等待”。

新增操作位于 `/blocks/block_007/instructions/1`：

```json
{
  "id": "ir_wait_1",
  "opcode": "wait_for_seconds",
  "inputs": [{"type": "literal", "identifier": null, "literal_value": 2}],
  "outputs": [],
  "constraints": ["Wait for 2 seconds before continuing."],
  "metadata": {},
  "draft_instruction_id": null
}
```

该判断既有明确的操作文字 `wait_for_seconds`，也有数值 `2` 和明确单位的约束文字，不依赖对不透明操作名的猜测。

块内顺序是 `check_transient_error` → `wait_for_seconds(2)` → `dispatch`。因此，记录中的等待处在首次 fast 失败之后、按 transient/non-transient 分流之前：它同时影响准备重试的路径和直接回退 archive 的路径。不能只将其描述为“重试前的退避”，否则缩小了实际新增操作的作用范围。首次 fast 成功路径、密钥缺失后直接 archive 的路径不经过该等待块。

c05 的重试成功返回绑定是 `result_008`，与实际重试 body 定义一致；它没有 c04 的返回身份错误。后续重提取应删除无依据等待及其相关声明，并保持失败分类和两条合法出口。仅把等待移到 transient 分支、删除单位但留下操作、把等待改名，或将其保留为新约束，均未充分修复无依据新增。

## 两个案例后续均需复核的新图不变量

每轮从完整新图重新建立定义与使用关系，逐一检查以下内容；旧指针只用于解释初始缺陷。

1. 用户请求及环境来源是否保留，fast 的两个业务参数是否仍来自对应实际来源。
2. 密钥缺失路径是否完全绕过 fast；密钥存在时是否先调用 fast。
3. 首次错误分类是否使用首次 fast 的错误；仅 transient 首次失败进入一次重试。
4. 重试成功／失败分类是否使用重试的错误或明确结果；所有重试失败都进入 archive，不形成进一步 fast 重试。
5. archive 是否至多调用一次且只收到 `source_id`；密钥是否进入 archive、状态记录或其他诊断操作。
6. 首次 fast 成功、重试 fast 成功、archive 成功，三种出口是否各自返回其成功调用的 body；archive 失败是否返回自己的错误。
7. 每个实际返回前是否仍追加最终状态；不能因删除等待或重新组织分支而漏掉状态追加。
8. 成功后是否还有获取操作、回退或重试；终止路径是否意外连接回获取节点。
9. 是否出现新的等待、额外参数、数据处理、输出转换、状态格式强制条件或其他源文未要求的内容。

## 结论边界

目前只确认两个初始图的上述实际缺陷，以及其他相关记录在当前图中如何表达。没有读取后续模型核对结果，因此尚不判断模型命中、修复成功、误改或核对器假通过。

以上是对图明确记录的操作、引用、顺序、边和声明的人工式助手分析。没有证明开放操作的执行语义、条件穷尽性、所有路径可执行性、文件写入成功或密钥的实际运行时安全性；也不把受控回述的保真证明扩大为这些保证。
