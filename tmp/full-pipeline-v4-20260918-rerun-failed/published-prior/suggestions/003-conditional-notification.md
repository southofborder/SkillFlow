# 003 conditional-notification｜语义评审

样例：**N03**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/003-conditional-notification.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/003-conditional-notification.png)。

本轮保留了读取、筛选、原字段取值及尾部写入，但逐条发送的控制和数据绑定不够完整。9 项事实中 6 项保留、3 项部分保留；此外，“处理条数”被擅自限定为选中记录数量。

## 需修改或注意的问题

1. **部分保留：集合抽象不足以核验逐条执行。** [SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N03/SKILL.md:13) 要求每条选中记录调用一次，[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N03/SKILL.md:14) 要求正文属于该记录。实际 `block_003/ir_005` 从 eligible_records 一次产出 recipients、bodies 两组结果，`block_004/ir_007` 消费整组结果；没有当前记录、对应 payload 或逐项返回控制。其“每条一次”约束仍在，因此不能断言只执行一次，但也不能从两组输入确认逐项配对和调用次数。建议明确每条记录的 recipient—summary 绑定与逐项调用关系；允许等价的映射表达，不必限定某种 loop opcode。

2. **部分保留：空选中集合的跳过仅由约束表达。** [SKILL.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N03/SKILL.md:15) 禁止未选中记录发送。`block_002/ir_003` 确实按完整条件产生选中集合，但 `block_002 → block_003 → block_004` 均无条件，图未结构化表达空集不触发工具。影响是无法单靠路径验证零次调用。建议使逐项映射在空集时产生零次发送，或显式加空集跳过边；不要删除已有筛选及“不调用”约束，也不要直接宣称退订记录已经发送。

3. **确定错转：未定计数口径被补全。** [SKILL.md:18](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N03/SKILL.md:18) 未指定统计对象，`block_005/ir_009` 却用 count_selected_records，`block_006/ir_011` 写入其结果；diagnostics 也选择选中并发送的记录数。通知后写入的顺序已保留，但这种定义会排除未选中记录。建议保留尾部写入，把统计对象留作待明确，不自行改为总数或成功数。

## 已保留的关键内容

筛选 `ir_003` 同时保留 opted_out 非 true 和 urgent／value 条件，紧急只豁免数值门槛；summary 原值来源明确，提取后没有生成或转换。全局禁令仍覆盖 access_token。以上证据成立，不应因逐项调度不足而一并判为丢失。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/N03.json)核对全部 9 项：

- **N03-F01｜保留**：`block_001/ir_001 → block_002/ir_003` 维持 events.json 来源。
- **N03-F02｜保留**：`block_002/ir_003` 以完整复合谓词实际产生 eligible_records；发送粒度不足归 F04/F06。
- **N03-F03｜保留**：`block_002/ir_003.constraints` 保留紧急例外的局部限制。
- **N03-F04｜部分保留**：`ir_005 → ir_007` 有接收对象来源与每条一次约束，缺逐项配对和调度。
- **N03-F05｜保留**：`ir_005` 保留 summary 原值并经 result_004 供 `ir_007` 使用；逐项对应不足见 F04。
- **N03-F06｜部分保留**：`ir_003` 先筛选且 `ir_007` 禁止未选中发送，但无空集跳过路径。
- **N03-F07｜保留**：`Skill.constraints` 全局禁止 token 外发，`ir_007` 无 token 输入。
- **N03-F08｜保留**：`ir_005 → ir_007` 无摘要生成、改写或格式转换。
- **N03-F09｜部分保留**：`block_004 → block_005 → block_006` 顺序正确，`ir_009` 擅定统计口径。

## 复核边界

约束承载的“每条一次”仍具有语义效力，当前问题是表达不充分，不是已证明单次调用或误发。旧逐事实评审曾把发送阶段的缺口计入 F02；本次复核确认筛选已产生符合谓词的集合，因此 F02 保留，相关不足集中归入 F04/F06。缺失字段、失败及重试策略不由评审补充。已核对冻结包正文及[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/N03/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。
