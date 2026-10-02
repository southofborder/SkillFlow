# 006 conditional-notification｜语义评审

样例：**N06**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/006-conditional-notification.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/006-conditional-notification.png)。

本轮识别了本样例正文应取 record_id，而非其他通知样例中的 summary。9 项事实中 6 项保留、3 项部分保留；主要不足是集合载荷未明确逐条调用及空集跳过，且自行决定了计数口径。

## 需修改或注意的问题

1. **部分保留：逐条发送被压成集合操作。** [SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N06/SKILL.md:11) 要求每条选中记录调用一次，[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N06/SKILL.md:12) 要求 body 使用该记录的 record_id。`block_003/ir_005` 一次生成 notification_payloads 集合，`block_004/ir_007` 消费该集合，没有当前记录与逐项调用的显式绑定。opcode 为 notify_send_for_selected_records，且仍附“每条一次”，所以不能断言只发送一次；问题是图的执行粒度不足以验证每条记录对应一次调用。建议明确逐项 payload、recipient 与 record_id 的对应关系，并以循环或明确的映射语义表达调用次数。

2. **部分保留：空集零调用没有结构化。** [SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N06/SKILL.md:13) 禁止未选中记录调用。`block_002/ir_003` 先筛选确有保护作用，`ir_007` 也保留“不调用”约束，但 `block_002 → block_003 → block_004` 只有无条件边，没有空集跳过或映射零次执行的明确表达。建议补清这条语义边界，避免消费者把集合发送当作无条件单次调用；这不是已证实的误发。

3. **确定错转：计数输入提前选定口径。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N06/SKILL.md:16) 未说明处理条数统计什么；`block_005/ir_009` 虽名为 count_processed_records，实际只消费 selected_records，diagnostics 也采用选中且通知的数量。`block_006/ir_011` 位于发送后，尾部依赖保留，但统计对象已被擅定。建议保留独立写入及处理完成关系，把计数对象留作待明确；仅改操作名称不能修复该问题。

## 已保留的关键内容

`ir_003` 保留 opted_out 非 true 且（urgent 或 value ≥ 100），紧急例外仍局限于数值门槛。`ir_005.constraints` 明确 body 为 record_id 原值，未套用 summary，也没有字符串格式化或内容改写。token 禁令仍在 Skill 全局，载荷提取及发送之间的数据来源可追踪。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/N06.json)核对全部 9 项：

- **N06-F01｜保留**：`block_001/ir_001 → block_002/ir_003` 保留 events.json 来源。
- **N06-F02｜保留**：`block_002/ir_003` 按完整复合谓词实际产生 selected_records；发送粒度不足归 F04/F06。
- **N06-F03｜保留**：`ir_003.constraints` 保留 urgent 不豁免 opted_out。
- **N06-F04｜部分保留**：`ir_005 → ir_007` 有载荷与每条一次要求，逐项绑定及调用控制不足。
- **N06-F05｜保留**：`ir_005.constraints` 明确 record_id 原值，result_003 供 `ir_007`；逐项绑定不足见 F04。
- **N06-F06｜部分保留**：选中集合及 `ir_007` 禁止未选中调用的约束在，但无空集跳过边。
- **N06-F07｜保留**：`Skill.constraints` 全局禁止 token 外发，`ir_005` 仅指定 recipient／record_id。
- **N06-F08｜保留**：`ir_005 → ir_007` 原值传递，无摘要生成、改写或转换。
- **N06-F09｜部分保留**：`block_004 → block_005 → block_006` 保留尾部次序，`ir_009` 仅计选中集合。

## 复核边界

这里不将节点数量等同于真实调用次数，也不要求固定 loop 类型。旧逐事实评审把下游发送控制不足一并计入 F02；本次确认筛选操作已产出符合谓词的集合，因此 F02 保留，问题归 F04/F06。字段原值来源与逐项调度分开评估；缺失字段、通知失败和重试策略仍按未定义处理。已核对冻结源文、[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/N06/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。
