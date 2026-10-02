# 005 conditional-notification｜语义评审

样例：**N05**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/005-conditional-notification.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/005-conditional-notification.png)。

本轮完整保留全部 9 项事实。通知仍按当前记录的条件逐条执行，明确不执行的历史 count.txt 示例没有进入实际流程；未发现确定错转或遗漏。

## 需修改或注意的问题

1. **等价且正确：没有 count 节点不是遗漏。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:16) 把写入 count.txt 明确限定为历史示例。实际 `block_002 → block_005` 在记录处理完毕后直接到 `ir_011` 返回，所有块均无计数或写文件操作，diagnostics 也说明只排除第 9 条。这保留了非执行范围。建议后续继续以此限定为准，不为补齐步骤编号重新插入计数、写入，也不要扩大成整份通知流程均不执行。

2. **复核注意：紧急例外与原值发送应合并检查。** [SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:9)、[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:10) 的筛选要求在 `block_003/ir_006` 保留；[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:11)、[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:12) 对 recipient 和 summary 的来源由 `block_004/ir_008 → ir_009` 实现。条件并非只存成说明，而经 `ir_007` 分派；通知也真实消费当前记录字段。建议保持这两段因果链：urgent 不能绕过 opted_out，summary 字段不能因名称含“摘要”而被改成新生成的摘要。

3. **未知边界：不要补缺失值与失败策略。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N05/SKILL.md:8) 已声明事件包含相关字段，`block_003/ir_005` 直接取这些字段，`ir_009` 是无返回值的副作用表达。源文没有定义字段缺失、服务失败或重试。当前未生成默认值或重复发送分支是合理的；建议保留未知，不以健壮性为由补充会改变“一次”要求的调用。

## 已保留的关键内容

`ir_003` 每次产生 current_event；未选中沿 `block_003 → block_002` 跳过发送，选中进入唯一通知块，发送后 `block_004 → block_002` 回到下一条。空输入也可直接结束。全局禁止把 access_token 发送给任何接收对象，通知实际只消费 recipient 与 summary；全图没有内容改写、格式转换或隐藏的尾部写入。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/N05.json)核对全部 9 项：

- **N05-F01｜保留**：`block_001/ir_001` 实际读取 events.json，`ir_003` 迭代读取结果。
- **N05-F02｜保留**：`ir_005/ir_006/ir_007` 计算并分派复合条件。
- **N05-F03｜保留**：`ir_006.constraints` 保留紧急只豁免数值的局部语义。
- **N05-F04｜保留**：`ir_003 → ir_008 → ir_009` 保留逐条 recipient 绑定，发送后回到 `block_002`。
- **N05-F05｜保留**：`ir_008` 产出 result_009，`ir_009` 将其作为 summary 原值发送。
- **N05-F06｜保留**：`block_003 → block_002` 未选中边绕过通知。
- **N05-F07｜保留**：`Skill.constraints` 全局禁止 token 外发，`ir_009` 无 token 输入。
- **N05-F08｜保留**：`ir_008 → ir_009` 无生成、改写或额外转换。
- **N05-F09｜保留**：`block_002 → block_005/ir_011` 直接结束，历史 count 不执行。

## 复核边界

本次结论针对第 1 次图，不推及其他轮次。历史示例的统计口径不属于当前执行问题，不需要为它选择总数、选中数或成功数。 已核对冻结源文、[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/N05/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。

