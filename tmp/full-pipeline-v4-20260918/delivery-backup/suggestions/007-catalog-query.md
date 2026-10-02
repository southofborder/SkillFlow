# 007 catalog-query｜语义评审

样例：**Q01**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/007-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/007-catalog-query.png)。

本轮完整保留全部 11 项事实：读取请求、按可选字段的存在性准备调用、单次搜索、写响应 total 和原值返回 items 均有实际操作及数据依赖。未发现确定的语义错转或遗漏。

## 需修改或注意的问题

1. **等价表达：省略参数需要结合分支与约束读取。** [SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:12)、[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:14) 要求缺失时省略参数；`block_002 → block_004` 和 `block_004 → block_006` 跳过对应提取，`block_006/ir_009` 的 inputs 仍列出可选结果，同时明确附有缺失时 omit 的调用约束。这是有条件实参的表达，不足以断言发送了 null 或未定义值。建议保留存在性与 omit 的关联，后续执行解释不能无条件序列化这两个操作数，更不能新增默认日期或 limit。

2. **未知边界：日期格式要求不是校验步骤。** [SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:11) 给出 YYYY-MM-DD，[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:16) 明确参数说明不指示调用前校验或规范化。`block_003/ir_004` 只取字段，`block_006/ir_009` 保留格式及 unchanged 要求；未生成解析日期、纠正格式或拒绝请求的操作。建议保持此界限，显式 null、空串或畸形日期的处理仍未定义，不能把它们自动归为缺失，也不能因为没有校验节点而判遗漏。

3. **复核注意：尾部写入是当前有效动作。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:17) 明确要求搜索后写 total。`ir_009` 直接输出 response.total/result_007 和 response.items/result_008；`block_007/ir_011` 写 total，随后 `ir_012` 返回 items。两项结果均来自该次搜索，未以 items 长度代替服务给出的 total。建议保留写入与返回的先后次序，不将它误归为历史示例；同一块内先写再 return 已能承载顺序，无需为了图形分块而拆出额外操作。

## 已保留的关键内容

唯一 `ir_009` 使用请求 term 原值，并有 exactly once 约束；所有路径只到该搜索一次，没有回边或重试分支。[SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:8) 的模糊匹配能力说明没有变成扩展操作，[SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q01/SKILL.md:15) 的 index.delete 禁令仍位于 `Skill.constraints`。返回链没有过滤、排序、格式化或重建 items，保留了原值返回的含义。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q01.json)核对全部 11 项：

- **Q01-F01｜保留**：`block_001/ir_001` 读取 request.json，同时产生 term 和存在标记。
- **Q01-F02｜保留**：唯一 `block_006/ir_009` 使用 term 原值并要求 exactly once。
- **Q01-F03｜保留**：`block_003/ir_004` 取日期；`ir_009.constraints` 保留原值与格式。
- **Q01-F04｜保留**：`block_002 → block_004` 跳过日期提取，调用明确 omit。
- **Q01-F05｜保留**：`block_005/ir_007` 提取 limit，`ir_009` 要求原值传递。
- **Q01-F06｜保留**：`block_004 → block_006` 跳过 limit，调用省略且无默认常量。
- **Q01-F07｜保留**：`ir_009` 的 items/result_008 被 `block_007/ir_012` 原值返回。
- **Q01-F08｜保留**：`Skill.constraints` 禁止 index.delete，全图无该调用。
- **Q01-F09｜保留**：能力说明停留在约束，`ir_009` 前后无模糊扩展。
- **Q01-F10｜保留**：`ir_001` 产生存在标记，`ir_004/ir_007` 取原字段，没有日期转换。
- **Q01-F11｜保留**：`ir_009 → block_007/ir_011 → ir_012` 保留搜索、写 total、返回顺序。

## 复核边界

仅评估第 1 次；已核对冻结源文、[完整 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q01/deepseek-v4-flash-max/1/analysis.json) 的 CFG、diagnostics 与 metadata，并仅参考旧评审该轮逐事实 assessments。diagnostics 为空本身不证明正确，上述结论依据实际图及原文。未定义搜索失败或写入失败策略，不补重试、兜底值或结果变换。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。

