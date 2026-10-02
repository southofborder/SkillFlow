# 001 conditional-notification｜语义评审

样例：**N01**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/001-conditional-notification.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/001-conditional-notification.png)。

本轮保留了逐条筛选、发送和结束后写文件的主链；9 项事实中 8 项保留，处理条数为部分保留。确定问题是把原文尚未定义的统计口径落实为选中记录数，不能因写入节点存在就判为完整保留。

## 需修改或注意的问题

1. **确定错转、事实部分保留：擅定计数口径。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:16) 只说处理完成后把“处理条数”写入 count.txt，没有说全部记录、选中记录还是成功发送记录。`block_005/ir_010` 明确采用 count_selected_event_records，重新消费全体 event_records 并附选中条件；`block_006/ir_012` 随后写入该结果。diagnostics 虽提示歧义，却仍选择“选中并调用通知”的数量。这会使读者把一种可能解释当成源文要求，尤其无法区分未选中记录是否计数、发送失败是否计数。建议保留独立尾部写入及其处理完成依赖，将计数对象标为待明确；不要直接改成另一种计数口径，也不要补成功响应或累计器策略。

2. **复核注意：紧急例外必须受退出订阅限制。** [SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:9)、[SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:10) 的组合语义是 opted_out 非 true 且（urgent 为 true 或 value ≥ 100）。`block_003/ir_006` 的约束与 `block_003 → block_004` 选中边共同实现该要求，未选中边 `block_003 → block_002` 跳过发送。当前没有此项错转；建议保留括号关系和局部例外，避免后续只读 urgent 分支而把退订记录也发出通知。

## 已保留的关键内容

[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:11)、[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N01/SKILL.md:12) 对当前记录的绑定可沿 `block_002/ir_003`、`block_003/ir_005`、`block_004/ir_008` 核对；发送后 `block_004 → block_002` 返回取下一条，故“每条一次”有实际循环支撑。全局禁令禁止发送 access_token，body 直接使用 summary，未添加摘要生成、改写或格式转换。无记录时也由结束边进入尾部写入；尾部没有反向影响筛选条件。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/N01.json)核对全部 9 项：

- **N01-F01｜保留**：`block_001/ir_001` 读取 events.json，`ir_003` 消费结果。
- **N01-F02｜保留**：`block_003/ir_006` 判定复合条件，`block_003 → block_004` 据此发送。
- **N01-F03｜保留**：`block_003/ir_006` 的局部约束明确 urgent 不豁免 opted_out。
- **N01-F04｜保留**：`ir_003` 逐条取值，`ir_008` 使用 result_007，发送后回到 `block_002`。
- **N01-F05｜保留**：`block_003/ir_005` 产生 summary 原值 result_008，`ir_008` 直接消费。
- **N01-F06｜保留**：`block_003 → block_002` 未选中路径绕过唯一发送操作。
- **N01-F07｜保留**：`Skill.constraints` 保留全局禁令，`ir_008` 没有 token 输入。
- **N01-F08｜保留**：`block_003/ir_005` 至 `ir_008` 无生成或转换操作，并有原值约束。
- **N01-F09｜部分保留**：`block_002 → block_005 → block_006` 保留结束依赖，`ir_010` 擅定计数对象。

## 复核边界

本页仅针对选定第 1 次；已核对冻结源文、[完整 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/N01/deepseek-v4-flash-max/1/analysis.json) 的 CFG、constraints、diagnostics 与 metadata，并参考旧评审该轮逐事实 assessments。源包声明记录包含各字段，缺失值、调用失败及重试策略仍未定义。这里的“保留”包括操作、控制边与约束共同承载的语义，不要求每句独立成节点。此文件为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未改动输入包、ZIP、PNG、生产流程或 API。

