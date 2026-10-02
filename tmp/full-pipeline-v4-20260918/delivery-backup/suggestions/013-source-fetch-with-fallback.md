# 013 source-fetch-with-fallback｜语义评审

样例：**F01**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/013-source-fetch-with-fallback.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/013-source-fetch-with-fallback.png)。

选定第 1 轮保留全部十项外置事实：凭据门控、一次瞬态重试、一次 archive 回退和原值返回均成立；每个最终出口均在返回前追加状态，未发现确定错转或遗漏。

## 需修改或注意的问题

1. **未知边界：状态文字是结果的表示，不是源文指定的固定格式。** [SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md:16) 只要求追加最终状态。`block_006/ir_011`、`block_010/ir_019`、`block_013/ir_025` 写 success，`block_014/ir_027` 写 failure；这些出口分别受真实成功或失败条件控制，覆盖关系正确。diagnostics 说明了文字未定义，因此不把这两种字面量本身判为错转。建议共同复核时保留这一未定项，不能再扩展日志字段、时间戳或新的格式要求。

2. **等价表达：错误判断的拆分没有增加重试。** [SKILL.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md:10)、[SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md:11) 要求仅首次瞬态失败重试一次。实际先在 `block_005` 分成功/失败，再在 `block_007/ir_013` 判断 transient；`block_007 → block_008` 仅瞬态，`block_007 → block_011` 非瞬态，`block_009 → block_011` 是重试失败。拆成多个判断块不改变次数；建议按这些边核对，不把“两个 fast 节点”误读成两次重试。

3. **等价表达：工具标识不算新增业务实参。** [SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/SKILL.md:12) 要求 archive 只传 source_id。实际 `block_011/ir_021` 的 inputs 还列有 external_resource 类型的 archive.fetch，这是被调用服务的身份；业务数据输入仅为已读 source_id，不包含 FAST_KEY。因此不能把这两个操作数简单计成两个 API 参数，也不能为了“只留一个”删掉服务定位。建议核对参数时区分工具标识与传递的数据，并沿结果标识确认 source_id 来自原请求。当前所有 archive 入口共享该调用，缺密钥支和失败回退支没有偷偷改变它的参数。

## 已保留的关键内容

- 请求来源与环境来源保持区别，读取结果贯穿首次调用和重试。`block_011/ir_021` 共享缺密钥、首次非瞬态失败、重试失败入口，但每条执行路径最多访问它一次。

- 成功的首次、重试和 archive 路径分别返回各自的 body；archive 失败返回自己的 error，没有误用首次失败或另一次调用的数据。

- 状态记录保留为独立操作并覆盖三个成功出口和一个失败出口。FAST_KEY 只用于门控和 fast 调用，未进入 archive 或状态文件输入。

## 逐项核对

以下按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/F01.json)的全部 10 项核对；状态只针对上述选定轮次。

- **F01-F01｜保留**：`block_001/ir_001` 读请求，`block_002/ir_003` 读环境；结果分别供工具和门控使用。

- **F01-F02｜保留**：`block_003 → block_004` 是有密钥支；`block_003 → block_011` 是缺密钥直达 archive 支。

- **F01-F03｜保留**：首次 `block_004/ir_007` 与重试 `block_008/ir_015` 均消费已读 source_id、FAST_KEY。

- **F01-F04｜保留**：`block_007 → block_008`（first fast.fetch failure was transient）及 `ir_015` 只允许一次重试；无返回 fast 的回边。

- **F01-F05｜保留**：首次非瞬态失败与重试失败两条路径都进入 `block_011/ir_021`。

- **F01-F06｜保留**：`block_011/ir_021` 只有 source_id 数据参数；最多一次约束和无回边的图相符。

- **F01-F07｜保留**：`ir_012`、`ir_020`、`ir_026` 分别返回本次成功 body；之后没有 fetch。

- **F01-F08｜保留**：archive 失败进入 `block_014/ir_028`，返回本次 error；无 archive 重试。

- **F01-F09｜保留**：Skill 全局禁止 FAST_KEY 进入 archive/diagnostic；`ir_021` 不接收该值。

- **F01-F10｜保留**：四个终态各先由 `ir_011/ir_019/ir_025/ir_027` 追加状态，再由对应 return 结束。

## 复核边界

FAST_KEY 的精确存在性测试、上游 transient 分类规则、工具响应的完整结构均未定义；本次不补错误码、等待时长、退避或第三次尝试。返回前追加状态不授权额外诊断内容。语义相同的共享 archive 节点、拆开的判断块及不同结果名称均可接受，判断依据是实际边和数据依赖。 成功后的“停止进一步获取”并不排除原文明示的返回前状态追加；历史示例样例则应直接返回。应逐条沿终态路径核对允许的末尾动作，不能只凭节点总数或块名作结论。

本评审同时检查了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/F01/deepseek-v4-flash-max/1/analysis.json)中的完整 CFG、diagnostics 和 metadata。PNG 的展示范围不包含 metadata；图上没有脚本正文或命令文本，不能据此判为提取遗漏。建议文件属于外置语义评审意见（由 Codex 复核），未写回 Skill 输入，也未修改 ZIP、PNG、生产 Prompt、IR 或提取流程。
