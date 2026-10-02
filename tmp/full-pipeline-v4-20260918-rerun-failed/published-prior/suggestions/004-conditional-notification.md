# 004 conditional-notification｜语义评审

样例：**N04**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/004-conditional-notification.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/004-conditional-notification.png)。

本轮正确纳入被主文件要求执行的流程说明，逐条循环和原值发送成立；9 项事实中 8 项保留、计数 1 项部分保留。另有固定包内配置被表达为运行时外部读取的边界问题。两项建议分别针对未定义口径和依赖来源，不应扩大为筛选逻辑、逐条次数或正文原值均已丢失。

## 需修改或注意的问题

1. **确定错转：预先限定了未定义的计数对象。** [workflow.md:21](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/references/workflow.md:21) 只规定处理结束后写处理条数。`block_004/ir_007` 在循环前使用 count_selected_records，`block_007/ir_015` 在 `block_005 → block_007` 结束边后写该结果。写入时机正确；错误在于把未知口径固定成选中数，不能仅因计数提前就判为写入提前。建议保留循环结束后的写入依赖，把计数对象留作待明确；不要擅改成全部数或成功数。

2. **额外行为／依赖边界：包内固定配置运行时化。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/SKILL.md:8) 纳入流程说明；[workflow.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/references/workflow.md:13) 引用包内 payload.json，其 [payload.json:2](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/payload.json:2) 已明确 body_from 为 summary。`block_002/ir_003` 却把 payload.json 作为 external_resource 读取，再将动态字段名 result_002 传给 `block_006/ir_012`。这增加了运行时依赖，也使字段来源看似可以变化。当前 `ir_012.constraints` 仍明确 summary 原值，因此 F05 保留；建议把固定配置内容作为抽取依据，直接绑定 summary。若坚持保留读取，应明确它指向同一冻结包配置，不能自由替换成任意同名文件。

## 已保留的关键内容

[workflow.md:6](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/references/workflow.md:6)、[workflow.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/N04/references/workflow.md:7) 的条件由 `ir_005` 实际筛选；`block_005/ir_009` 逐条取选中记录，`block_006/ir_011`、`ir_012` 从同一当前记录取 recipient 和 summary，`ir_013` 发送后返回 `block_005`。空集直接结束，没有通知调用。全局 token 禁令及不得生成、改写、转换的限制仍在。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/N04.json)核对全部 9 项：

- **N04-F01｜保留**：`block_001/ir_001` 读取 events.json，`ir_005` 使用该记录结果。
- **N04-F02｜保留**：`block_003/ir_005` 筛选复合条件，`ir_009` 只迭代选中集合。
- **N04-F03｜保留**：`ir_005.constraints` 明确紧急不豁免 opted_out。
- **N04-F04｜保留**：`ir_009 → ir_011 → ir_013` 保留当前记录接收对象及每条一次循环。
- **N04-F05｜保留**：`ir_012` 明确 summary 原值，`ir_013` 消费 result_008；配置依赖另列问题。
- **N04-F06｜保留**：`block_005 → block_007` 在无下一条时跳过发送。
- **N04-F07｜保留**：`Skill.constraints` 全局禁止发送 access_token，`ir_013` 无该输入。
- **N04-F08｜保留**：`ir_012 → ir_013` 直接传原值，无生成、改写或转换。
- **N04-F09｜部分保留**：`ir_015` 在循环结束后写 count.txt，但 `ir_007` 擅定选中数。

## 复核边界

已阅读主文件、references/workflow.md 与 payload.json；跨文件纳入本身有源文授权。未执行通知或配置读取。缺失字段及失败处理没有定义，不增加校验、默认值或重试。 已核对冻结包正文及[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/N04/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。
