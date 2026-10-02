# 011 catalog-query｜语义评审

样例：**Q05**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/011-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/011-catalog-query.png)。

选定第 1 轮完整保留本样例的查询语义：单次搜索和原值返回仍实际执行，历史 count.txt 示例没有变成写文件操作；未发现确定错转或事实遗漏。

## 需修改或注意的问题

1. **等价表达：可选参数的省略依赖调用约束。** [SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:12)、[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:14) 要求缺失时省略参数；CFG 的 `block_002 → block_004`（`from_date missing`）及 `block_005 → block_007`（`limit missing`）跳过字段提取，但 `block_008/ir_014` 仍列出 `result_005/result_006`。这两个输入应结合调用上的 omit 约束读取，不能据此认定缺失时发送了 null。建议保留这两条省略约束及分支条件；若以后需要更精确的执行解释，应明确输入受相应存在性条件约束，而非补空值。

2. **未知边界：存在判断不等于日期校验。** [SKILL.md:11](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:11) 规定日期格式，[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:16) 又明确不要求调用前验证或规范化。`block_002/ir_004/ir_005` 只判断字段是否存在，`block_008/ir_014` 保留格式和原值约束，符合原文。显式 null、空字符串及畸形日期应如何处理仍未定义。建议保持未定，不增加解析、纠错、默认日期或失败分支。

3. **历史示例的排除范围正确。** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:17) 只把写 count.txt 标为不执行；`block_008 → block_009` 仍完成搜索和 items 返回。完整 analysis 的 diagnostics 也说明了这一排除。建议共同复核时不要把“没有 count 写入”误记为遗漏，更不能由此删除其余实际查询行为。

4. **等价表达：未执行的说明不要求独立节点。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:8) 的模糊匹配能力说明与 [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q05/SKILL.md:17) 的历史写入说明，均不是当前动作。实际 `block_001–009` 只有文件读取、取字段、条件分派、搜索和结果返回，diagnostics 分别解释了两类非执行内容的去向。因此，图中找不到“能力说明”节点或“历史示例”节点本身不是遗漏。建议把这些文本用于核对行为边界，而不是转成额外操作；与此同时，搜索响应仍须真正产生并供返回使用，不能用一个泛化的“支持查询”节点替代当前 `ir_014/ir_016/ir_017` 的数据链。当前图保留了这条链，未发现此类替代。

## 已保留的关键内容

- 读取 request.json 后，term 经 `ir_003` 产生 `result_002`，唯一 `ir_014` 搜索使用该值；图中不存在第二次搜索或回到搜索的边。

- from_date 的 YYYY-MM-DD、原值传递以及 limit 原值传递都附在实际调用上；未生成模糊扩展、规范化或 index.delete 操作。

- `ir_016` 从本次 `search_response/result_007` 提取 items，`ir_017` 原值返回；返回数据没有被历史 total 示例替换。

## 逐项核对

以下按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q05.json)的全部 11 项核对；状态只针对上述选定轮次。

- **Q05-F01｜保留**：`block_001/ir_001` 读取 request.json；`block_002/ir_003–005` 使用该读取结果。

- **Q05-F02｜保留**：唯一 `block_008/ir_014` 使用 `result_002`；Skill 约束保留 exactly once。

- **Q05-F03｜保留**：`block_003/ir_007` 提取日期；`ir_014` 附原值及 YYYY-MM-DD 约束。

- **Q05-F04｜保留**：缺失边 `block_002 → block_004` 跳过取值；`ir_014` 明确 omit。

- **Q05-F05｜保留**：存在边 `block_005 → block_006` 经 `ir_011` 取 limit；调用要求原值。

- **Q05-F06｜保留**：缺失边 `block_005 → block_007` 与 `ir_014` 省略约束一致，无默认常量。

- **Q05-F07｜保留**：`block_009/ir_016 → ir_017` 返回同次响应 items，保留 unchanged。

- **Q05-F08｜保留**：Skill 全局禁止 index.delete；全部操作没有该调用。

- **Q05-F09｜保留**：`block_001–009` 无 fuzzy 扩展；diagnostics 将能力说明留作非执行信息。

- **Q05-F10｜保留**：`ir_004/005` 是存在判断；全部图中无日期校验、规范化或内容转换。

- **Q05-F11｜保留**：`block_008 → block_009` 直接进入结果返回；无 total 提取或 count.txt 写入。

## 复核边界

本次仅评估 Q05 第 1 轮；“缺失”不擅自扩大为 null、空串或无效值。约束与控制边共同承载可选参数语义，不能只看 inputs 列表就推断实参一定发送。原文未定义搜索失败策略，不补重试或替代结果。 本页所说“保留”指原文要求在操作、数据依赖或约束中有依据，并不要求每句文字都拥有独立节点；操作名称差异也不单独构成错误。

本评审同时检查了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q05/deepseek-v4-flash-max/1/analysis.json)中的完整 CFG、diagnostics 和 metadata。PNG 的展示范围不包含 metadata；图上没有脚本正文或命令文本，不能据此判为提取遗漏。建议文件属于外置语义评审意见（由 Codex 复核），未写回 Skill 输入，也未修改 ZIP、PNG、生产 Prompt、IR 或提取流程。
