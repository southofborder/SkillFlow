# 021 document-bundle-delivery｜语义评审

样例：**D03**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/021-document-bundle-delivery.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/021-document-bundle-delivery.png)。

主要转换、打包、交付和收据语义保留；逐文档调用与每次标准输出的对应关系仍停留在批处理抽象，需要明确。顺序备注的未知范围已正确保留。

## 需修改或注意的问题

1. **部分保留：逐项调用与输出绑定。** [SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:11)要求逐个执行单文档脚本。`block_004/ir_007` 消费整份路径列表并产出 `result_005` 集合，块名含 each，但没有显式当前文档与每次 stdout 的绑定。建议补充外层逐项映射和收集语义，可以用操作约束表达，不要求固定循环结构，也不能据此断言实际只执行一次。

2. **可接受：固定文件副作用。** [SKILL.md:24](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:24)明确生成 bundle.zip。`ir_009` 的命令及脚本保存了写出动作，`block_005 → block_006` 后 `ir_011` 消费同名文件资源。outputs 为空不等于未生成文件；建议保留文件名、命令与前后依赖，不伪造脚本返回值。

3. **未知边界正确保留。** [SKILL.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:19)未说明“必要时”的条件和顺序对象。analysis diagnostics 明确说明范围不清而不建为约束，图中也没有任意扩大的全局顺序规则。不要因 PNG 隐藏 diagnostics 而判该未知边界丢失。

## 已保留的关键内容

清单路径、请求 output_dir/delivery_path 的来源清楚；转换路径 `result_005` 同时供打包和 receipt.txt，收据未误写 ZIP 路径。保留标题只约束转换；不得修改输入和不得外传仍为全局规则。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/D03.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **D03-F01｜保留**：读取 manifest.json.paths 作为文档路径来源，并读取请求中的 output_dir 和 delivery_path。 原文：[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:10)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`ir_001`、`ir_003`、`ir_005`。

- **D03-F02｜部分保留**：逐个以文档路径和 output_dir 调用 scripts/convert.py；每次调用读取该 UTF-8 源文，按需创建输出目录，将内容写入 output_dir 下的 <源文主名>.txt，并把标准输出的该路径作为转换产物路径。 原文：[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:11)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/scripts/convert.py:5)；CFG：`ir_007`、`block_004`、`edge_4`。

- **D03-F03｜保留**：保留原文标题仅约束转换操作，不约束汇总标题。 原文：[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:12)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`block_004.constraints`、`ir_007`。

- **D03-F04｜保留**：convert.py 按黑盒调用保留参数、文件输入、输出产物和标准输出路径，不把内部变量、循环或控制流拆成额外流程步骤，也不重复执行内部处理。 原文：[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:11)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)、[SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:13)、[scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/scripts/convert.py:5)；CFG：`block_004`、`ir_007`、`block_004.constraints`。

- **D03-F05｜保留**：必须执行被明确采用的参考打包命令，以转换产物路径列表为 --paths 输入；调用读取各产物文件并写入由 --output 指定的 bundle.zip，压缩包内使用各文件的文件名。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:14)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)、[SKILL.md:23](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:23)、[scripts/package.py:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/scripts/package.py:7)；CFG：`ir_009`、`block_005.constraints`。

- **D03-F06｜保留**：将打包生成的 bundle.zip 交付到先前从请求读取的 delivery_path，交付操作消费该读取结果，无需再次读取。 原文：[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:10)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)、[SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:15)；CFG：`ir_005`、`ir_009`、`ir_011`、`edge_5`。

- **D03-F07｜保留**：单独将转换产物路径列表写入本地 receipt.txt，并保留对转换产物路径的依赖。 原文：[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:16)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`ir_007`、`ir_013`。

- **D03-F08｜保留**：不得修改输入原文文件的禁止要求作用于整份 Skill。 原文：[SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:17)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`skill.constraints`。

- **D03-F09｜保留**：不得向外部服务上传文档的禁止要求作用于整份 Skill。 原文：[SKILL.md:18](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:18)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`skill.constraints`。

- **D03-F10｜保留**：“必要时保留原顺序”的作用范围不明确，应待共同确认，不能自动提升为全局规则。 原文：[SKILL.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:19)、[SKILL.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D03/SKILL.md:7)；CFG：`diagnostics`。

## 复核边界

路径重名、覆盖、转换失败与收据/交付失败的处理未定义，不补策略。脚本内部读写与 ZIP 循环保持黑盒，不应重复拆成主流程步骤。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D03/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
