# 023 document-bundle-delivery｜语义评审

样例：**D05**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/023-document-bundle-delivery.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/023-document-bundle-delivery.png)。

历史收据示例已正确排除，转换、打包和交付仍实际执行。主要注意逐文档调用和 stdout 产物对应关系的表达粒度。

## 需修改或注意的问题

1. **部分保留：批处理表达应明确逐项绑定。** [SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:9)要求逐文档调用。`block_004/ir_007` 名称 for_each_document、块名 collect stdout paths 和 diagnostics 均保留循环意图，但只有列表级 inputs/outputs。建议明确外层每项调用和收集规则，以便核对漏文档、错配路径等问题；这不是断言模型只执行一次。

2. **正确排除：不要补回历史收据动作。** [SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:14)明确标为当前不执行。图在 `block_006/ir_011` 交付后返回，没有 receipt.txt 写入，diagnostics 也说明仅排除该历史步骤。建议保持该最小差异，不能按其他 D 样例补写收据，也不能把历史标记扩展到前面的转换和打包。

3. **未知顺序保持未定。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:17)没有足够范围信息；diagnostics 明确不提升全局，实际约束只保留两条明确禁令。该处理可接受，无需为了让图出现所有原句而添加顺序操作。

## 已保留的关键内容

`ir_009` 使用转换产物 `result_005` 构建 bundle.zip，`ir_011` 交付 `result_006` 至请求目标 `result_004`。两个完整脚本与命令保存在 metadata，主流程未重复其内部行为。转换标题与全局禁令的归属正确。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/D05.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **D05-F01｜保留**：读取 manifest.json.paths 作为文档路径来源，并读取请求中的 output_dir 和 delivery_path。 原文：[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:8)；CFG：`ir_001`、`ir_003`、`ir_005`。

- **D05-F02｜部分保留**：逐个以文档路径和 output_dir 调用 scripts/convert.py；每次调用读取该 UTF-8 源文，按需创建输出目录，将内容写入 output_dir 下的 <源文主名>.txt，并把标准输出的该路径作为转换产物路径。 原文：[SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:9)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/scripts/convert.py:5)；CFG：`ir_007`。

- **D05-F03｜保留**：保留原文标题仅约束转换操作，不约束汇总标题。 原文：[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:10)；CFG：`ir_007`、`block_004.constraints`。

- **D05-F04｜保留**：convert.py 按黑盒调用保留参数、文件输入、输出产物和标准输出路径，不把内部变量、循环或控制流拆成额外流程步骤，也不重复执行内部处理。 原文：[SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:9)、[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:11)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/scripts/convert.py:5)；CFG：`ir_007`、`block_004.constraints`。

- **D05-F05｜保留**：必须执行被明确采用的参考打包命令，以转换产物路径列表为 --paths 输入；调用读取各产物文件并写入由 --output 指定的 bundle.zip，压缩包内使用各文件的文件名。 原文：[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:12)、[SKILL.md:21](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:21)、[scripts/package.py:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/scripts/package.py:7)；CFG：`ir_007`、`ir_009`。

- **D05-F06｜保留**：将打包生成的 bundle.zip 交付到先前从请求读取的 delivery_path，交付操作消费该读取结果，无需再次读取。 原文：[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:8)、[SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:13)；CFG：`ir_005`、`ir_009`、`ir_011`。

- **D05-F07｜保留**：写入 receipt.txt 是明确不执行的历史示例，当前流程不增加该写入。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:14)；CFG：`diagnostics`、`ir_011`、`ir_012`。

- **D05-F08｜保留**：不得修改输入原文文件的禁止要求作用于整份 Skill。 原文：[SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:15)；CFG：`skill.constraints`。

- **D05-F09｜保留**：不得向外部服务上传文档的禁止要求作用于整份 Skill。 原文：[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:16)；CFG：`skill.constraints`。

- **D05-F10｜保留**：“必要时保留原顺序”的作用范围不明确，应待共同确认，不能自动提升为全局规则。 原文：[SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D05/SKILL.md:17)；CFG：`diagnostics`。

## 复核边界

历史示例、黑盒源码和未定备注有不同用途，不应一律转成执行节点。源文没有授权为重名、覆盖、输入缺失或转换失败补自动策略。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D05/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
