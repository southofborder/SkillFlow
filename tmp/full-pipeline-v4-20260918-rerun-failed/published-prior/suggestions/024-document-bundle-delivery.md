# 024 document-bundle-delivery｜语义评审

样例：**D06**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/024-document-bundle-delivery.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/024-document-bundle-delivery.png)。

关键最小差异 archive_path 已正确转换；未定顺序备注仍被错误提升为全局限制，逐文档调用粒度也需补充。

## 需修改或注意的问题

1. **确定错转：顺序备注范围被扩大。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:17)未说明条件与对象，实际 `Skill.constraints[2]` 却作为整份流程规则保存，diagnostics 未保留该范围未知。建议将其作为外置待明确项，而非确认后的全局限制。

2. **部分保留：逐项调用与每次 stdout。** [SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:9)与 `block_004/ir_007` 的列表级调用之间缺少明确逐项绑定。操作名已含 for_each，不能认定只调用一次；建议在外层语义中说明每个文档产生一个该次 stdout 路径，并收集到 `result_005`，不要展开脚本内部步骤。

3. **正确差异：交付目的地应是 archive_path。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:8)仍读取 delivery_path，但 [SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:13)明确把交付目标改成 archive_path。实际 `block_006/ir_011` 读取 archive_path，`block_007/ir_013` 消费 `result_006`，diagnostics 记录 delivery_path 已读未用。额外读取 archive_path 有直接原文依据，不应“修正”为 delivery_path，也不能将两者混用。

## 已保留的关键内容

打包 `ir_009` 明确写 bundle.zip，后续用固定文件名交付可以表达文件副作用；`ir_015` 写 receipt.txt 的内容来自转换产物 `result_005`。标题保留仍限转换，两条明确禁令保持全局。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/D06.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **D06-F01｜保留**：读取 manifest.json.paths 作为文档路径来源，并读取请求中的 output_dir 和 delivery_path。 原文：[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:8)；CFG：`ir_001`、`ir_003`、`ir_005`。

- **D06-F02｜部分保留**：逐个以文档路径和 output_dir 调用 scripts/convert.py；每次调用读取该 UTF-8 源文，按需创建输出目录，将内容写入 output_dir 下的 <源文主名>.txt，并把标准输出的该路径作为转换产物路径。 原文：[SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:9)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/scripts/convert.py:5)；CFG：`ir_007`。

- **D06-F03｜保留**：保留原文标题仅约束转换操作，不约束汇总标题。 原文：[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:10)；CFG：`ir_007`、`ir_007.constraints`。

- **D06-F04｜保留**：convert.py 按黑盒调用保留参数、文件输入、输出产物和标准输出路径，不把内部变量、循环或控制流拆成额外流程步骤，也不重复执行内部处理。 原文：[SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:9)、[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:11)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/scripts/convert.py:5)；CFG：`ir_007`、`ir_007.constraints`。

- **D06-F05｜保留**：必须执行被明确采用的参考打包命令，以转换产物路径列表为 --paths 输入；调用读取各产物文件并写入由 --output 指定的 bundle.zip，压缩包内使用各文件的文件名。 原文：[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:12)、[SKILL.md:21](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:21)、[scripts/package.py:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/scripts/package.py:7)；CFG：`ir_007`、`ir_009`。

- **D06-F06｜保留**：从请求读取 archive_path，并将打包生成的 bundle.zip 交付到该读取结果指定的位置；先前明确要求读取的 delivery_path 仍保留，但不再用于交付。 原文：[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:8)、[SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:13)；CFG：`ir_003`、`ir_009`、`ir_011`、`ir_013`。

- **D06-F07｜保留**：单独将转换产物路径列表写入本地 receipt.txt，并保留对转换产物路径的依赖。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:14)；CFG：`ir_007`、`ir_015`。

- **D06-F08｜保留**：不得修改输入原文文件的禁止要求作用于整份 Skill。 原文：[SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:15)；CFG：`skill.constraints`。

- **D06-F09｜保留**：不得向外部服务上传文档的禁止要求作用于整份 Skill。 原文：[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:16)；CFG：`skill.constraints`、`ir_013`。

- **D06-F10｜错转**：“必要时保留原顺序”的作用范围不明确，应待共同确认，不能自动提升为全局规则。 原文：[SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:17)；CFG：`skill.constraints`。

## 复核边界

初始字段表与后续目标不一致已经说明，但源文并未定义 archive_path 缺失时的替代策略；不要默认回退到 delivery_path。未使用的已读值本身不等同于错转。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D06/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
