# 受控回述：实际文本的事实保持证明

本实现把规范化 CFG 的完整记录投影为带中文标签、原子事实锚点和位置的受控文本。核对模型实际读取这份文本；Python 不另写一套打印模板。这里证明的是图记录经过表示转换仍可完整恢复，不证明原图与 Skill 原文语义相符，不证明模型理解正确，也不证明操作、约束或嵌入脚本的运行行为。

## 输入域和唯一文本

`SkillIR/ControlledGraph.lean` 的 `RichGraph` 保留入口、上下文声明、图约束、块 key/ID/名称/来源、全部指令 ID/opcode/draft ID、逐次输入输出、操作数种类/标识/语义标签/字面内容、块内指令次序、三级约束、metadata、控制边及可选条件。它不复用会把业务操作合并为 `business`、丢弃字面内容和约束的旧结构核心投影。

literal 和 metadata 以 Python 边界提供的规范 JSON **字符串**进入 Lean；`null` 字面量是字符串 `"null"`，没有 literal 字段则为 `none`。Lean 保持该不透明字符串，不对 JSON 或嵌入源码赋予行为解释。输入域是有限的富记录及合法 Lean 字符串；生产 JSON、Schema 归一化以及上述不透明字符串的产生不在本轮机器证明中。

`project` 生成可见 `FactDoc`；每条记录有中文类别、公开锚点、定位和槽位。`print`/`printAt` 是唯一实际打印器，包含缩进、引号及反斜杠/换行等转义。解析器读取的正是这些字符；没有隐藏原始 JSON 用作恢复捷径。

每个基本块还显示完整的操作 ID 顺序清单。结果引用按实际 identifier 展开到输出定义位置。语义标签不参与定义匹配；无条件、授权成功、I/O 成功等含义不能由名称、空条件或声明推导。

## 已完成的定理

| 定理 | 精确范围 |
| --- | --- |
| `parse_print`、`parse_printAt` | 实际打印字符串可以解析回原始受控记录树，包括 Unicode 内容、转义和缩进。 |
| `recover_project` | 富图投影为文档后，恢复得到相同的全部富记录字段。 |
| `recover_parse_print_project` | 组合上述两层，从实际打印文本解析、恢复得到原富图。 |
| `record_classification_location` | 文本往返保持记录类别、公开锚点及位置，而不仅保持其值。 |
| `constraint_scope_location`、`scoped_constraints_preserved` | 三级约束的类别、位置和富图中对应作用域的约束列表保持。 |
| `recorded_observation_preserved` | 完整记录的任意纯观察保持，包含操作/操作数顺序、标识、标签和不透明载荷。 |
| `links_sound` | 每个显示的引用链接来自实际输入和输出出现位置；两端都是 result 且 identifier 完全相同。不证明支配关系、运行可用性或路径可执行性。 |
| `parseGraph_renderGraph` | 每份规范打印文本均能由正式解析入口接受并恢复原富图。 |
| `parseGraph_sound` | 被接受的文本必须与所恢复富图的完整权威打印结果相等；类别、锚点、清单和派生链接不能单独被篡改。 |
| `renderGraph_injective` | 不同富图不能产生完全相同的规范受控文本。 |

`recover` 提取显式富图字段；正式 `parseGraph` 随后重新生成整份权威文本并比较，因此还检查派生操作清单、引用链接、标签和锚点。解析一份代表其他图的合法文本仍可成功，是否与本次原始 CFG 对应由 Python 逐次桥接验收判断。

以上是受控记录语言的表示保持命题。中文标签具有规定的记录含义，但没有因此证明人或模型会正确理解任意自由中文，更没有证明某个 opcode、条件文字或脚本满足某种执行语义。

## JSONL 接口

独立可执行文件为 `.lake/build/bin/skill_ir_retell.exe`（非 Windows 为 `skill_ir_retell`）。每个输入行是一条请求：

```json
{"command":"render","graph":{"entry":"b","contexts":[],"constraints":[],"blocks":[],"edges":[]}}
```

另一个命令为 `{"command":"parse","text":"实际受控文本"}`。`render`/`parse` 成功时均返回：

- `ok: true`、`protocol: "skill-ir-controlled-v1"`。
- `text`：实际文本；`recovered_graph`：从该文本解析恢复的富图。
- `units`：`{id,text,kind,ref}` 原子单元。单元 text 按实际层级打印，是全文的连续原始子串；容器不另设公开锚点。
- `links`：`{identifier,use_ref,definition_ref}`，位置均采用富图 JSON Pointer。

失败为 `{"ok":false,"error":"原因"}`，不是语义未通过，也不能当成受控文本已保真。最小例子的结构是否满足生产 CFG 规则不由这个独立 codec 判断；调用方先运行现有完整性校验。

富图 wire 协议如下。所有字段必有；可空值使用 JSON null：

```text
RichGraph = {entry, contexts[], constraints[], blocks[], edges[]}
Block = {key, id, name, source?, constraints[], instructions[]}
Instruction = {id, opcode, draft?, inputs[], outputs[], constraints[], metadata_json}
Operand = {kind, identifier?, semantic_name?, literal_json?}
Edge = {source, target, condition?}
```

公开锚点为 `fact:<富图位置>`；引用展开单元使用 `fact:<使用位置>:link`。Python 将这些位置对应回规范 CFG；模型只需要引用已出现的事实 ID。Python 对恢复的富图独立反解完整规范 CFG，逐字段比较，并检查单元正文、锚点、位置与引用链接。

## 构建、公理和信任边界

在本目录使用固定工具链运行：

```powershell
lake build
lake env lean ProofAudit.lean
```

工具链沿用 `lean-toolchain` 的 Lean 4.33.1。新增主定理均已通过内核检查，没有 `sorry`、`admit`、自定义公理或绕过内核检查的证明。实际公理审计中，文本 codec 及其组合定理依赖 `[propext, Classical.choice, Quot.sound]`；富图恢复与结果链接定理依赖 `[propext, Quot.sound]`。这属于明确列出的 Lean 标准公理基础，不应描述为“完全无公理”。

JSON 读取/写出、Python CFG Schema 和规范 JSON 投影、CLI 编译/运行、文件编码与实际模型请求封装仍是工程信任边界。必须对实际运行绑定源码、输入、可执行文件及发送文本摘要；从实际文本恢复并逐字段比较原 CFG。不能用有限差分通过替代 Python/JSON 的端到端形式证明，也不能只展示证明文件却发送另一份未经核验的摘要给模型。

原有 `Core`、`WF` 和结构重命名定理保持原证明范围，不被受控回述定理扩大。Lean 可执行文件仅属于独立离线回溯工具，不改变生产提取 pipeline 的依赖和执行入口。
