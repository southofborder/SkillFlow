# 019 document-bundle-delivery｜语义评审

样例：**D01**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/019-document-bundle-delivery.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/019-document-bundle-delivery.png)。

选定第 1 轮的主要文件处理和交付链保留，但存在一项确定的约束范围错转，以及一项逐文档转换表达不足，建议共同复核后再确认其语义完整性。

## 需修改或注意的问题

1. **确定错转：范围未知的备注被升级为全局规则。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D01/SKILL.md:17) 的“必要时保留原顺序”没有指定条件、对象或操作。实际 CFG 将它放入 `Skill.constraints[2]`，且 diagnostics 为空；于是读者会把它与两条明确的全局禁令同等适用于全部流程，这超过原文证据。建议从确定的全局规则中移出，作为范围待确认的外置问题保留；不能自行决定约束转换、打包还是交付，更不要据此补排序步骤。

2. **部分保留：逐文档调用及每次 stdout 的绑定粒度不足。** [SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D01/SKILL.md:9) 要求逐个调用，而 [scripts/convert.py:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D01/scripts/convert.py:5) 至第 10 行表明单次脚本只接收一个文档，最终打印一个路径。实际 `block_004/ir_007` 一次消费整份 `document_paths/result_002` 和 output_dir，输出路径集合 `result_005`；有 each 的名称及原样命令，却没有当前文档与每次 stdout 的逐项绑定。这不足以单靠图验证列表中每个文档都对应一次调用及一项返回路径。建议在该操作的外层语义中明确逐项映射和收集关系，可用参数约束或外层控制表达；无需固定 loop 操作类型，也不要拆开脚本内部处理。此项不等同于断言模型只执行一次。

## 已保留的关键内容

- 清单文档路径、output_dir、delivery_path 均有实际读取结果。转换输出 `result_005` 同时供打包和 receipt.txt，收据没有误写 ZIP 路径。

- 核对两个完整脚本后，UTF-8 读取、按源主名写 .txt、标准输出路径，以及 ZIP 读取产物并用文件名入包，都保留在调用的 script_content 中；没有在主流程重复执行这些内部动作。

- 转换局部标题约束与不得改输入、不得外传的全局禁令分开保存；明确采用的参考命令作为真实打包动作，交付使用先前读取的目标，不重复读取请求。

## 逐项核对

以下按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/D01.json)的全部 10 项核对；状态只针对上述选定轮次。

- **D01-F01｜保留**：`block_001/ir_001 → block_002/ir_003` 建立清单路径来源；`ir_005` 读取两个请求目录。

- **D01-F02｜部分保留**：`block_004/ir_007` 保留单文档命令和完整脚本，但列表到逐次调用、stdout 收集绑定不够明确。

- **D01-F03｜保留**：`ir_007.constraints` 将保留标题限定于转换，未扩展至汇总或整份 Skill。

- **D01-F04｜保留**：`ir_007` 以黑盒保留脚本、参数和路径结果；内部目录创建、读写没有拆成主流程操作。

- **D01-F05｜保留**：`block_005/ir_009` 的命令及脚本明确 --paths、--output；ZIP 内使用 path.name。

- **D01-F06｜保留**：`ir_011` 消费打包结果 `result_006` 和早先读取的交付路径 `result_004`。

- **D01-F07｜保留**：`block_007/ir_013` 独立写 receipt.txt，内容引用转换路径 `result_005`。

- **D01-F08｜保留**：Skill 全局保留不得修改输入原文文件，未降低为仅转换阶段要求。

- **D01-F09｜保留**：Skill 全局保留不得向外部服务上传文档，没有生成上传操作。

- **D01-F10｜错转**：`Skill.constraints[2]` 擅自提升未定范围的原顺序备注，且无诊断保留该不确定性。

## 复核边界

“必要时”的条件与“原顺序”的对象仍须依据源文确认，不补排序或遍历顺序策略。重复文件名、输出与输入路径重合、路径不存在及转换失败的处理未定义，本次不替原文选择覆盖、去重或重试方案。脚本源码作为黑盒行为证据静态阅读，没有执行。对逐项转换的建议针对调用外层，不要求暴露脚本内部变量或控制流。

本评审同时检查了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D01/deepseek-v4-flash-max/1/analysis.json)中的完整 CFG、diagnostics 和 metadata。PNG 的展示范围不包含 metadata；图上没有脚本正文或命令文本，不能据此判为提取遗漏。建议文件属于外置语义评审意见（由 Codex 复核），未写回 Skill 输入，也未修改 ZIP、PNG、生产 Prompt、IR 或提取流程。
