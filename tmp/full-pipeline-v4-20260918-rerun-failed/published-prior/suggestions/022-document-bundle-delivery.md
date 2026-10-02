# 022 document-bundle-delivery｜语义评审

样例：**D04**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/022-document-bundle-delivery.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/022-document-bundle-delivery.png)。

跨文件采用的主流程基本完整，但未定范围的顺序备注被提升为全局限制；逐文档调用与 stdout 收集的对应粒度仍需明确。

## 需修改或注意的问题

1. **确定错转：不确定范围被固化。** [references/workflow.md:27](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:27)只说必要时保留原顺序。CFG 却把它列入 `Skill.constraints[3]`，没有留下其对象和适用条件未定的说明。建议移出确定的全局约束，单独保留范围待确认项，不能自行指定为转换、打包或交付顺序。

2. **部分保留：外层逐次调用的绑定不清。** [references/workflow.md:6](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:6)要求每个文档一次脚本调用并取该次 stdout。`block_004/ir_007` 的 for_each 名称和 diagnostics 保留这一意图，但 inputs 是路径集合，输出只有集合 `result_005`。建议明确每个输入路径、该次调用及该次返回路径的映射；不要求把脚本内部动作展开，也不宣称脚本只运行一次。

3. **跨文件内容没有因链接而丢失。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)明确采用工作流，实际 `ir_009` 使用 [references/workflow.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:16) 的打包命令，`ir_011` 用生成的 `result_006` 和已读交付目标 `result_003`。这种合并表达可接受；不要把 references 文件误当另一份必须在运行时读取的数据。

## 已保留的关键内容

标题限制附在转换操作，禁止改原文/外传保持全局；`ir_013` 独立写 receipt.txt 并使用转换路径。实际交付使用请求目标，没有把两份路径来源混淆。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/D04.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **D04-F01｜保留**：读取 manifest.json.paths 作为文档路径来源，并读取请求中的 output_dir 和 delivery_path。 原文：[references/workflow.md:3](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:3)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`ir_001`、`ir_003`、`ir_005`。

- **D04-F02｜部分保留**：逐个以文档路径和 output_dir 调用 scripts/convert.py；每次调用读取该 UTF-8 源文，按需创建输出目录，将内容写入 output_dir 下的 <源文主名>.txt，并把标准输出的该路径作为转换产物路径。 原文：[references/workflow.md:6](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:6)、[references/workflow.md:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:5)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/scripts/convert.py:5)；CFG：`ir_007`。

- **D04-F03｜保留**：保留原文标题仅约束转换操作，不约束汇总标题。 原文：[references/workflow.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:7)、[references/workflow.md:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:5)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`ir_007`、`ir_007.constraints`。

- **D04-F04｜保留**：convert.py 按黑盒调用保留参数、文件输入、输出产物和标准输出路径，不把内部变量、循环或控制流拆成额外流程步骤，也不重复执行内部处理。 原文：[references/workflow.md:6](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:6)、[references/workflow.md:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:5)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)、[references/workflow.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:9)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/scripts/convert.py:5)；CFG：`ir_007`、`ir_007.constraints`。

- **D04-F05｜保留**：必须执行被明确采用的参考打包命令，以转换产物路径列表为 --paths 输入；调用读取各产物文件并写入由 --output 指定的 bundle.zip，压缩包内使用各文件的文件名。 原文：[references/workflow.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:11)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)、[references/workflow.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:15)、[scripts/package.py:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/scripts/package.py:7)；CFG：`ir_007`、`ir_009`。

- **D04-F06｜保留**：将打包生成的 bundle.zip 交付到先前从请求读取的 delivery_path，交付操作消费该读取结果，无需再次读取。 原文：[references/workflow.md:3](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:3)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)、[references/workflow.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:19)；CFG：`ir_003`、`ir_009`、`ir_011`。

- **D04-F07｜保留**：单独将转换产物路径列表写入本地 receipt.txt，并保留对转换产物路径的依赖。 原文：[references/workflow.md:21](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:21)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`ir_007`、`ir_013`。

- **D04-F08｜保留**：不得修改输入原文文件的禁止要求作用于整份 Skill。 原文：[references/workflow.md:23](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:23)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`skill.constraints`。

- **D04-F09｜保留**：不得向外部服务上传文档的禁止要求作用于整份 Skill。 原文：[references/workflow.md:25](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:25)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`skill.constraints`、`ir_011`。

- **D04-F10｜错转**：“必要时保留原顺序”的作用范围不明确，应待共同确认，不能自动提升为全局规则。 原文：[references/workflow.md:27](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/references/workflow.md:27)、[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D04/SKILL.md:8)；CFG：`skill.constraints`、`ir_007`。

## 复核边界

采用外部工作流不等于其中每句备注的作用域已经确定。交付与收据当前顺序可以展示，但不应进一步臆造成功/失败依赖或重试。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D04/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
