# 012 catalog-query｜语义评审

样例：**Q06**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/012-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/012-catalog-query.png)。

选定第 1 轮保留全部外置事实，尤其正确表达 limit 缺失时传 10 的最小变化；count.txt 写入及 items 返回均来自同一次搜索响应，未发现确定错转或遗漏。

## 需修改或注意的问题

1. **等价表达：默认 10 是本样例的明确要求。** [SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:14) 规定缺失 limit 时传 10。CFG 的 `block_004 → block_006`（`limit is missing`）进入 `ir_012`，常量 10 经 `block_007/ir_014` 汇合为 `result_008`，再供搜索使用。此处增加参数选择操作落实了原文，并非凭空补默认值。建议保留与常规省略 limit 样例的差异，不把它改成 omit，也不把已有 limit 覆盖为 10。

2. **需注意的表达边界：汇合输入必须按分支选择。** [SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:13) 与 [SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:14) 分别描述已有值和缺失值；`ir_014 resolve_limit_argument` 同时列出两支的 `result_006/result_007` 及 `limit_present/result_005`。应理解为按存在性选取对应结果，并不要求两支都执行。日期缺失边 `block_002 → block_004` 同样跳过取值，而 `ir_016` 保留 omit 约束。建议在后续解释中沿用这套分支条件，不补空值或同时执行两支；当前不据此判定错转。

3. **未知边界：格式说明仍不是额外验证。** [SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:11)、[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:16) 不定义畸形日期、显式 null 或不合理 limit 的处理。实际图只有存在判断、值选择和搜索，没有日期解析或参数规范化，符合要求。建议保留这条边界；默认 10 只适用于原文的 missing 条件，不能扩展到“值不合法”。

4. **需保留的副作用区别：写 total 与返回 items 是两件事。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:17)、[SKILL.md:18](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q06/SKILL.md:18) 分别要求写计数和返回查询项。实际 `block_009/ir_018` 消费 `result_009`，产出 total 后由 `ir_019` 写入本地 count.txt；随后 `block_010/ir_021` 再从同一个响应提取 items，并由 `ir_022` 返回。两个消费者使用同一响应标识，能够核对它们不是来自两次搜索。建议保持这条先写后返回的路径，不把 count.txt 的内容替换成 items 数量的重新计算，不把 items 改成计数文件，也不能因另一历史示例样例不写文件而删除本轮的真实写入。

## 已保留的关键内容

- `block_001/ir_001` 读取 request.json，term 和两个可选字段均来自它；`block_008/ir_016` 是唯一搜索，query 原值及单次限制明确。

- `block_009/ir_018/ir_019` 先提取 `result_009` 的 total 并写 count.txt，再到 `block_010/ir_021/ir_022` 返回同一响应的 items。

- fuzzy 匹配仍是能力说明；禁止 index.delete 和不要求预校验的约束保持全流程范围，没有生成摘要、额外查询或写入以外的附加行为。

## 逐项核对

以下按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q06.json)的全部 11 项核对；状态只针对上述选定轮次。

- **Q06-F01｜保留**：`block_001/ir_001` 读取 request.json，后续字段均引用 `result_001`。

- **Q06-F02｜保留**：唯一 `block_008/ir_016` 以 `result_002` 搜索，调用与全局均保留次数要求。

- **Q06-F03｜保留**：`block_003/ir_006` 取 from_date；`ir_016` 保留原值及日期格式。

- **Q06-F04｜保留**：`block_002 → block_004`（`from_date is missing`）跳过取值；调用保留 omit。

- **Q06-F05｜保留**：`block_005/ir_010` 取请求 limit，`ir_014` 选择它；`ir_016` 要求 unchanged。

- **Q06-F06｜保留**：缺失支 `block_006/ir_012` 的 literal 10 经 `ir_014` 到 `ir_016`。

- **Q06-F07｜保留**：`block_010/ir_021/ir_022` 从同次 `result_009` 取 items 并直接返回。

- **Q06-F08｜保留**：Skill 全局禁止 index.delete，全部可达路径没有删除调用。

- **Q06-F09｜保留**：Skill 保留 capability note；`block_001–010` 不含 fuzzy 扩展操作。

- **Q06-F10｜保留**：存在判断和默认值选择只落实参数规则；图中没有新增验证或规范化。

- **Q06-F11｜保留**：`block_008 → block_009 → block_010` 保证先搜索、写 total、再返回 items。

## 复核边界

仅对 Q06 第 1 轮给出结论；默认值分支不是所有查询样例的共同规则。条件值选择属于语义表示，不在本次将它改造成可执行程序或新增 IR 规则。日期、limit 的非法值处理及搜索错误处理均未定义，继续留待原文补充。 本页所说“保留”指原文要求在操作、数据依赖或约束中有依据，并不要求每句文字都拥有独立节点；操作名称差异也不单独构成错误。

本评审同时检查了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q06/deepseek-v4-flash-max/1/analysis.json)中的完整 CFG、diagnostics 和 metadata。PNG 的展示范围不包含 metadata；图上没有脚本正文或命令文本，不能据此判为提取遗漏。建议文件属于外置语义评审意见（由 Codex 复核），未写回 Skill 输入，也未修改 ZIP、PNG、生产 Prompt、IR 或提取流程。
