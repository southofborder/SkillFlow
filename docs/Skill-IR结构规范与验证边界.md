# Skill-IR 结构规范与验证边界

本规范定义 Skill 语义控制流图的第一阶段接受条件。它面向静态分析，不定义可执行 Skill 语言，也不以源码行为已经全部提取、条件可满足或操作实现正确为接受条件。语义回溯和传播分析属于后续阶段。

这里使用 **结构良构性（well-formedness）**，不是数学上的“良序性（well-ordering）”。良构表示对象按规定的语法、连接和引用规则组成；图可以有分支、循环和多个行为起点，不要求节点构成一个线性顺序。

## 1. 输入域与两个层次

原始候选、持久化 JSON 和调用方持有的 Python 模型均不自动视为可信。输入解析负责规定的归一化；完整接受还需要检查当前对象的全部字段与结构。模型构造成功不能替代 `validate_integrity()`。

**Schema 层**规定字段、来源类型、标识命名和操作数字段约定。指令 ID 遵守现有 `ir_…` 格式，块和结果标识为合法非空字符串；业务 opcode 仍是非空语义字符串。`literal` 承载字面内容，`context_key`、`result`、`external_resource` 分别表示上下文键、结果定义的引用和资源标识。非 literal 不得显式携带 `literal_value`，literal 不得携带非空 `semantic_name`。默认未设置的空字段与显式提供的字段不同。

**结构层**在该字段域上定义独立谓词 `WF(G)`，回答连接、指令排列和数据引用是否合法。它不解释业务 opcode、自然语言条件、约束、文字描述或脚本正文的行为含义。相关内容继续保存在原 IR 中，形式核心仅投影与本阶段规则有关的信息。

内存重验必须检查实际值，不能先调用会省略字段的 `to_json()`，也不能以校验副本中的归一化结果替换原对象。模型创建之后把标识改为空白、增加重复声明或添加禁止字段，均不能借重验被静默修复。校验失败也不修改对象。

## 2. 图与可达性的定义

记 `G = (B, E, entry, C)`。`B` 是以块标识为键的有限块集合，每块含自身 ID、来源类别和有序指令列表；`E` 是有向控制边列表，每条边含起点、终点和可选条件文字；`C` 是上下文声明列表。

每条指令含 ID、操作、输入及输出。结果 ID 标识一个定义点；结果被传给后续操作时引用该 ID，而不是逐块手写转交关系。上下文声明仅声明名称，实际读入操作才产生可引用结果。资源标识不等于工具返回数据，也不等于文件内容。

根集合由显式 `entry` 与所有无前驱块组成。控制边的条件不参与第一阶段的图遍历。可达关系包含零步到达自身；有限图中的检查使用至多 `|B|` 条边的可达闭包。该边数来自图大小，不是任意的运行次数上限，也不要求每条循环执行至多该次数。

`WF(G)` 的约束如下。各项独立于检查器的返回值陈述：

| 条款 | 结构条件 | Python 实现位置 | 基线正反测试 | 形式核心覆盖 |
| --- | --- | --- | --- | --- |
| W01 | `entry` 对应现有块；字典键与块自身 ID 一致 | `ir/validation.py` | `test_invalid_entry_and_edge_endpoints_are_rejected`、`test_block_key_must_match_block_id` | 图入口、块 key/ID |
| W02 | 指令 ID 全图唯一，结果 ID 全图只有一个定义点 | `ir/validation.py`、`ir/basic_block.py` | `test_integrity_rejects_duplicate_instruction_ids_across_blocks`、`test_integrity_rejects_duplicate_results_across_blocks` | 全图标识列表无重复 |
| W03 | 边的两端存在；完全相同的起点、终点、条件不得重复 | `ir/validation.py` | `test_duplicate_edges_are_rejected_but_distinct_guards_are_allowed` | 边端点及边无重复 |
| W04 | 块内至少一条指令；最后一条为 dispatch 或 return；前面无终结指令 | `ir/basic_block.py` | `test_terminator_must_be_the_final_instruction`、`test_terminator_and_edge_consistency` | 指令序列终结形状 |
| W05 | 输出只允许 result；dispatch/return 不产生结果 | `ir/basic_block.py`、`ir/instruction.py` | `test_outputs_must_be_value_references`、`test_dataflow_revalidation_rejects_fabricated_terminator_outputs` | 输出种类与终结输出 |
| W06 | 来源块恰有获取指令和终结指令，且获取产生至少一个结果 | `ir/basic_block.py` | `test_source_requires_one_acquisition_followed_by_terminator`、`test_source_acquisition_must_have_real_outputs` | 来源形状 |
| W07 | context 来源的获取输入非空且全部为 context_key；external 来源至少输入一个资源或结果 | `ir/basic_block.py` | `test_context_source_requires_nonempty_raw_context_inputs`、`test_external_source_requires_resource_or_value_input` | 来源输入类别 |
| W08 | 原始 context_key 仅出现在 context 获取位置，且在声明列表中 | `ir/basic_block.py`、`ir/validation.py` | `test_context_ref_outside_the_acquisition_is_rejected`、`test_raw_context_requires_declaration_and_real_import` | 原始键位置及声明成员关系 |
| W09 | 同块引用该块产生的结果时，定义必须严格位于读取之前 | `ir/basic_block.py` | `test_same_block_read_before_production_is_rejected_even_in_a_loop` | 局部定义顺序 |
| W10 | 每个 result 输入有定义；跨块定义所在块可沿控制边到达使用块 | `ir/validation.py` | `test_end_to_end_demo_rejects_a_read_no_path_can_satisfy`、`test_value_defined_by_a_predecessor_is_available` | 定义存在及跨块可达 |
| W11 | return 块无出边；dispatch 块有出边；多分支或带条件的 dispatch 声明非空输入 | `ir/validation.py` | `test_terminator_and_edge_consistency`、`test_guard_dependencies_must_be_explicit_dispatch_inputs` | 出边与终结一致性 |
| W12 | 所有块均能从某个根到达；声明列表不重复 | `ir/validation.py`、Schema 重验 | `test_rootless_cycle_rejected_but_independent_root_is_valid`、完整重验回归 | 根可达及声明无重复 |

表中的基线测试位于 `tests/ir/`，形式核心及新增差分测试还会逐项破坏这些条件。Schema 的字符串格式、Python 对象合法性、JSON 转换与业务载荷内容不包含在 Lean 核心图定理中；这些边界由字段校验、快照和桥接测试覆盖。

## 3. 允许的表达与未作的保证

结构接受是一种有意受限的承诺：

- 某结果只在一个分支产生，但在合流之后被引用，可以满足 W10；不证明所有路径上均可读取它。多个输入可能共同消费，也可能表示分支候选，具体含义要结合操作与条件解释，不由输入列表统一规定为 AND 或 OR。
- 跨块结果可能经回边到达读取点；不证明第一次进入循环时该值已存在。同块先读后定义仍违反 W09。
- 独立行为片段可以有各自的根；接受它们不等于每次调用都会执行全部片段，也不会自动创建片段之间的边。
- 保留条件文字不等于证明各分支互斥、覆盖所有情况或可满足。语法可达路径可能不可执行。
- 声明“仅批准后发送”不等于已经验证批准机制；保存脚本不等于证明脚本的副作用摘要正确。

例如，有密钥时产生 `fast_result`，无密钥时产生 `backup_result`，合流操作按实际分支返回结果。不能要求两种结果在每条路径都存在。若操作实际上无条件读取 `fast_result`，备用路径上的可用性问题仍需后续分析，而不能用结构通过消除它。

因此，本轮“完整”只指规定的结构规则都进入验证边界；不指 Skill 的行为覆盖完整，不指每条路径可执行，不指循环终止，不指数据传播已证明可靠。

## 4. 检查器、谓词与证明

`WF(G)` 是数学命题：“图 G 满足本规范的结构条件”。`check(G)` 是可运行函数，其返回值是布尔值。二者类型不同，所以严谨写法是：

```text
check(G) = true ↔ WF(G)
```

从左到右是健全性：参考检查器不会接受违反已形式化规则的核心图。从右到左是完备性：满足这些规则的核心图不会被参考检查器拒绝。这里的完备性不能解释为“原文的所有内容都提取到了”。

Lean 文件先以逻辑命题定义各结构条件及其合取 `WF`，再通过有限命题的可判定实例得到可执行 `check`，证明其反射等价。这是对声明式规范的可执行化和机器检查，不是把 `WF` 循环定义成 `check = true`；也不应包装为独立发明了一套新的优化检查算法。

ID 重命名定理限于结构身份的保持：对块、指令和结果各自一致地应用单射重命名，即可保持定义、引用和可达关系；合法双射是其中一种情况。映射回生产字符串时，仍须遵守 Schema 命名约定。业务名称、上下文键、资源名称、条件和载荷不会跟着结构编号重命名。

## 5. 信任边界与验收证据

证明的对象是规范化核心图及 Lean 参考检查器。生产图投影为核心图时，保留列表顺序、重复项、缺失定义所用的 ID、边条件的同一性及上下文键；不得先修复图，不得把 Python 已算好的可达表或规则结论注入核心代替检查。

自然语言、源码等不影响 W01–W12 的内容不参与核心计算，但仍留在原始 IR。投影忽略某字段只说明该字段超出本阶段定理范围，不代表该字段对后续语义分析不重要。

Python 与 Lean 的对照使用相同原始输入及对应投影。Schema 非法输入单独统计为入域拒绝，不能伪称已经交由 Lean 判为结构非法。正式 30 图从所选轮次的原始 `analysis.json` 读取并核对摘要；绘图过程的 `model_dump` 中间对象不是原始输入替代品。

完整验收需要：规则矩阵、Python 回归、Lean 核心构建与公理审计、固定种子的生成式差分与小图拓扑枚举、既有 30 图对照，以及受保护原件摘要核验。差分失败保存原例和缩减后的反例；没有对应解释的分歧不得算作通过。

输入解析、投影代码、Python 执行和工具链运行是明确列出的信任与测试边界。差分全部通过是在已测输入与已记录版本上的一致性证据，不是 Python 和桥接代码已获得端到端机器证明。

可复现命令、工具链版本、具体定理名与最新验收报告见 `packages/skill-ir/formal/README.md`。

## 6. 后续里程碑

第二步建立通用语义回溯，用源文证据核对遗漏、错转和无依据新增；回译不能读取源 Skill 或外置事实标注。第三步在明确操作解释和未知边界后，建立数据来源、处理历史与副作用的传播模型及有条件的健全性证明。本规范不提前规定 DOE 的字段、评分或业务判断。
