# 009 catalog-query｜语义评审

样例：**Q03**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/009-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/009-catalog-query.png)。

本轮完整保留全部 11 项事实。表格中的存在／缺失要求转为分支和调用约束，单次查询、写 total、返回 items 的顺序及来源正确，未发现确定错转或遗漏。

## 需修改或注意的问题

1. **等价表达：服务名和方法名需要一起读。** [SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:12) 要求调用 index.search；`block_006/ir_012` 的 external_resource 为 index，而 opcode 为 index.search，局部约束也明确该方法和 exactly once。不能仅因资源未写全方法名就判为换服务。建议复核时结合操作名、资源及约束，保持当前真实调用和请求 term 的数据依赖，不增加另一次 search 来“补齐”名称。

2. **等价表达：可选结果列在 inputs 中不等于缺失时传空值。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:16)、[SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:17) 的表格分别要求日期和 limit 缺失时 omit。`block_002 → block_004` 跳过日期提取，`block_004 → block_006` 跳过 limit 提取；`ir_012` 同时附存在时原值、缺失时省略的规则。建议保持条件与实参的关联，不把缺失结果序列化成 null，也不发明默认值。当前语义有约束依据，无需因没有四套调用而判遗漏。

3. **未知边界：存在判断不是格式校验。** [SKILL.md:21](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:21) 明确不指示调用前校验或规范化。`block_002/ir_004` 和 `block_004/ir_008` 仅检查字段存在，YYYY-MM-DD 保存在 `ir_012.constraints`。畸形日期或显式 null 如何处理未定，建议保持未定；不要补解析、纠错或拒绝分支，也不要把参数表格本身当成要求新增验证器。

## 已保留的关键内容

[SKILL.md:23](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:23) 的写入由 `block_007/ir_014 → ir_016` 实现，内容来自本次响应 total；[SKILL.md:25](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q03/SKILL.md:25) 的 items 经 `ir_015 → ir_017` 原值返回，写入在返回之前。唯一搜索无循环或回边，fuzzy 能力说明没有变成扩展行为，全局禁止 index.delete。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q03.json)核对全部 11 项：

- **Q03-F01｜保留**：`block_001/ir_001` 读取 request.json；`ir_003/ir_004/ir_008` 使用同一结果。
- **Q03-F02｜保留**：唯一 `block_006/ir_012` 使用 term/result_002，保留 exactly once 与 unchanged。
- **Q03-F03｜保留**：`block_003/ir_006` 提取日期；`ir_012.constraints` 保留格式和原值。
- **Q03-F04｜保留**：`block_002 → block_004` 缺失边跳过日期取值，`ir_012` 明确 omit。
- **Q03-F05｜保留**：`block_005/ir_010` 从请求取 limit，`ir_012` 原值传递。
- **Q03-F06｜保留**：`block_004 → block_006` 跳过 limit，调用省略且无默认常量。
- **Q03-F07｜保留**：`block_007/ir_015 → ir_017` 直接返回同次响应的 items。
- **Q03-F08｜保留**：`Skill.constraints` 全局禁止 index.delete，所有块无该调用。
- **Q03-F09｜保留**：`Skill.constraints` 保留能力说明，`ir_012` 前后无模糊扩展。
- **Q03-F10｜保留**：`ir_004/ir_008` 仅查存在，全图无日期校验或标准化。
- **Q03-F11｜保留**：`ir_014 → ir_016 → ir_017` 保留同次 total 写入后返回。

## 复核边界

本次只评第 1 次。字段缺失不自动涵盖 null、空串或无效值；操作名称差异不单独构成语义错误。搜索或文件写入失败的处理没有定义，不补重试或替代结果。 已核对冻结源文、[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q03/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。

