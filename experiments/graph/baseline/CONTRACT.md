# 语义基线约束契约 v2

本契约实施《Skill 文档理解数据集与 PDF 共同复核方案》后续步骤 2。用户在 2026-09-10 确认修订事实与待共同确认部分后，才增加以下表达字段。它是已确认语义的表达能力迁移，不是根据模型结果形成的 Prompt 优化。

## 相对原契约 v1 的唯一模型扩展

| 作用范围 | 候选模型 | 正式 IR 模型 | 新增字段 |
| --- | --- | --- | --- |
| 整份 Skill | `IRAnalysisCandidate` | `ControlFlowGraph` | `constraints: list[str]` |
| 所属基本块 | `CandidateBlock` | `BasicBlock` | `constraints: list[str]` |
| 所属操作 | `CandidateInstruction` | `IRInstruction` | `constraints: list[str]` |

各字段使用独立的默认空列表。原先采用结果引用契约、未含 `constraints` 的候选与 CFG JSON 仍可读取；读取后对应层级为 `[]`。更早的已停用共享上下文字段不属于本次兼容承诺。v1 读取器不接受 v2 的新字段，因此不能把 v2 产物交给 v1 读取器解释。

每条约束直接保留来源文字，由所在层级表达归属。编译器逐层复制列表，不提升、展开、继承、去重、裁剪文字或改写作用范围；不会根据文字生成操作、输入输出、分支或诊断。字符串内部的空格、换行、中文、重复项均按提供内容保留。JSON Schema 只要求字符串列表，不引入分类字段、规则语言、effect 或审计结论。

无法从原文确定作用范围时，模型应在已有 `diagnostics` 中保留不确定性，不擅自挂成整份 Skill 的规则。真实的数据读取、处理与传递仍须表达为操作数及控制流；约束文字不能使未定义的结果可用，也不能代替运行时数据读取。约束本身不构成增添转换、校验或其他步骤的依据。编译器的结构成功不等于这些语义要求均被满足，语义落点仍需结果复核。

## Prompt 迁移边界

原生产快照保存在 `frozen/production/`。当前 Prompt 保持既有正文、两份完整示例、包文件拼接方式不变，仅在最后 JSON 返回说明前增加下面这一段契约说明：

```text
CONSTRAINTS: Preserve constraint wording from the source in constraints: list[str].
Place Skill-wide constraints on IRAnalysisCandidate, block-scoped constraints on
CandidateBlock, and operation-scoped constraints on CandidateInstruction. The
containing level expresses scope; use [] when none applies. If scope is unclear,
report that uncertainty in diagnostics rather than promoting it to a Skill-wide
rule. Actual data acquisition, processing, and transfer must still appear in
operands and control flow, not only in constraint text. A constraint alone does
not introduce a conversion, validation, or other execution step.
```

候选 JSON Schema 随三个候选模型自动新增可省略的字符串数组。没有新增样例专有名词、案例、Prompt 示例、格式判定技巧或优化规则。对应的文本／Schema 差异应单独保存在实验快照中，不能归因于后续 Prompt 优化。

执行 `python packages/skill-ir/experiments/semantics_baseline/tools/snapshot_contract.py` 可在离线环境核对迁移边界，并重建 `contract_v2/` 中的 v1／v2 候选 Schema、追加原文、六个生产文件差异及摘要清单。脚本检查 `extraction/`、`ir/` 和 `artifacts/`，会拒绝这些目录中迁移范围外的修改，或追加段落以外的 Prompt 正文、示例及 Schema 变化。实验运行器属于独立实现，不归入这项契约差异。

## 基线与后续版本的比较

原 Prompt 与原模型称为契约 v1，只保留为迁移前快照。正式首轮基线采用已追加上述最小说明的契约 v2；后续 Prompt 版本亦须采用相同 v2 候选、IR、编译和序列化契约。每版固定样例、开发／保留划分及每份 3 次提取设置。不能将“v1 不存在的约束字段在 v2 有了输出”计作 Prompt 优化收益。

本次没有修改生产提取流程、修复提示逻辑、LLM 客户端或 HTTP 重试策略。现有 `analysis_json.serialize_analysis_result`、候选序列化与 `ControlFlowGraph.to_json` 会保留新增层级；没有为约束增加另一套产物格式。结构修复、HTTP 重试与语义判定继续分别记录。

## 验证

`tests/extraction/test_constraints_contract.py` 覆盖旧 JSON 默认值、默认列表隔离、六个模型的类型边界、原文及归属编译保留、候选／CFG／基本块／analysis JSON 往返，以及约束不能定义结果或制造执行步骤。Prompt 测试检查最小契约说明，已有编译、IR 和 artifact 测试检查回归。测试中的固定候选只验证契约，不作为生产 Prompt 示例或语义基线结果。
