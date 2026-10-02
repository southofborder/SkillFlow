# 008 catalog-query｜语义评审

样例：**Q02**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/008-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/008-catalog-query.png)。

本轮完整保留全部 11 项事实：读取请求、按可选字段的存在性准备调用、单次搜索、写响应 total 和原值返回 items 均有实际操作及数据依赖。未发现确定的语义错转或遗漏。

## 需修改或注意的问题

1. **等价表达：省略参数需要结合分支与约束读取。** [SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:12)、[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:14) 要求缺失时省略参数；`block_003 → block_005` 和 `block_005 → block_007` 跳过对应提取，`block_007/ir_011` 的 inputs 仍列出可选结果，同时明确附有缺失时 omit 的调用约束。这是有条件实参的表达，不足以断言发送了 null 或未定义值。建议保留存在性与 omit 的关联，后续执行解释不能无条件序列化这两个操作数，更不能新增默认日期或 limit。

2. **未知边界：日期格式要求不是校验步骤。** [SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:10) 给出 YYYY-MM-DD，[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:16) 明确参数说明不指示调用前校验或规范化。`block_004/ir_006` 只取字段，`block_007/ir_011` 保留格式及 unchanged 要求；未生成解析日期、纠正格式或拒绝请求的操作。建议保持此界限，显式 null、空串或畸形日期的处理仍未定义，不能把它们自动归为缺失，也不能因为没有校验节点而判遗漏。

3. **复核注意：尾部写入是当前有效动作。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:16) 明确要求搜索后写 total。`ir_011` 返回 search_response/result_007；`block_008/ir_013` 和 `ir_014` 从同一响应分别提取 total 与 items，`ir_015` 写 total 后 `ir_016` 原值返回 items。没有把响应、查询词或 items 数量误作 count.txt 内容。建议保留写入与返回的先后次序，不将它误归为历史示例；同一块内先写再 return 已能承载顺序，无需为了图形分块而拆出额外操作。

## 已保留的关键内容

唯一 `ir_011` 使用请求 term 原值，并有 exactly once 约束；所有路径只到该搜索一次，没有回边或重试分支。[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:8) 的模糊匹配能力说明没有变成扩展操作，[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q02/SKILL.md:14) 的 index.delete 禁令仍位于 `Skill.constraints`。返回链没有过滤、排序、格式化或重建 items，保留了原值返回的含义。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q02.json)核对全部 11 项：

- **Q02-F01｜保留**：`block_001/ir_001 → block_002/ir_003` 读取并解析 request.json 的字段及存在标记。
- **Q02-F02｜保留**：唯一 `block_007/ir_011` 使用 term 原值并要求 exactly once。
- **Q02-F03｜保留**：`block_004/ir_006` 取日期；`ir_011.constraints` 保留原值与格式。
- **Q02-F04｜保留**：`block_003 → block_005` 跳过日期提取，调用明确 omit。
- **Q02-F05｜保留**：`block_006/ir_009` 提取 limit，`ir_011` 要求原值传递。
- **Q02-F06｜保留**：`block_005 → block_007` 跳过 limit，调用省略且无默认常量。
- **Q02-F07｜保留**：`block_008/ir_014 → ir_016` 直接返回同次 search_response 的 items。
- **Q02-F08｜保留**：`Skill.constraints` 禁止 index.delete，全图无该调用。
- **Q02-F09｜保留**：能力说明停留在约束，`ir_011` 前后无模糊扩展。
- **Q02-F10｜保留**：`ir_003` 是 JSON 字段解析，`ir_006/ir_009` 是取值，均非日期合法性校验。
- **Q02-F11｜保留**：`block_008/ir_013 → ir_015 → ir_016` 保留写响应 total 后再返回。

## 复核边界

仅评估第 1 次；已核对冻结源文、[完整 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q02/deepseek-v4-flash-max/1/analysis.json) 的 CFG、diagnostics 与 metadata，并仅参考旧评审该轮逐事实 assessments。diagnostics 为空本身不证明正确，上述结论依据实际图及原文。未定义搜索失败或写入失败策略，不补重试、兜底值或结果变换。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。

