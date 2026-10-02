# 010 catalog-query｜语义评审

样例：**Q04**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/010-catalog-query.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/010-catalog-query.png)。

本轮完整保留全部 11 项事实。跨文件要求及静态省略配置均进入实际查询，四套 search 表达四种互斥参数组合，每条可达执行路径只调用一次；未发现确定错转或事实遗漏。

## 需修改或注意的问题

1. **等价表达：四个 search 节点不是四次调用。** [workflow.md:7](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/references/workflow.md:7) 规定 exactly once。`block_002/ir_006` 按日期和 limit 的存在性分四路：到 `block_003` 为两者都有，到 `block_006` 为只有日期，到 `block_009` 为只有 limit，到 `block_012` 为两者均缺失。这些条件互斥；分别到达 `ir_010/ir_016/ir_022/ir_026`，随后各自写入并返回，没有串行经过其他搜索的边。建议沿单条路径核对调用次数，不能按全图节点总数认定重复查询。

2. **配置范围正确，需保留“缺失时”的限定。** [SKILL.md:8](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/SKILL.md:8) 纳入流程说明，[workflow.md:15](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/references/workflow.md:15) 要求同次调用采用配置；[query.yaml:1](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/query.yaml:1) 至第 3 行把两个 omit 放在 missing_arguments 下。图将内容落实到调用约束，`ir_016` 不含 limit，`ir_022` 不含日期，`ir_026` 两者均不含；存在参数的分支仍传原值。建议保留此范围，不能把所有调用上的配置摘要误解成存在时也删参数。当前无需新增 YAML 运行时读取，冻结配置已经提供明确规则。

3. **未知边界：存在性分派并未定义非法值处理。** [workflow.md:10](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/references/workflow.md:10)、[workflow.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/references/workflow.md:19) 把日期格式留作调用要求，并不要求校验。`ir_004/ir_005` 仅生成存在标记；四路调用没有新增日期修正。建议保持显式 null、空串及畸形日期的行为未定，不将它们擅自映射到缺失分支或补默认值。

## 已保留的关键内容

四个终点分别消费各自搜索的 total 和 items，count.txt 写入先于返回，没有跨分支串用结果。全局 index.delete 禁令保留，引用块里的 fuzzy 能力说明没有被提升为模糊扩展动作。正文与配置来自实际冻结包，引用格式本身不妨碍它们成为有效要求。

## 逐项核对

按[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/Q04.json)核对全部 11 项：

- **Q04-F01｜保留**：`block_001/ir_001 → block_002/ir_003` 保留请求文件及 term 来源。
- **Q04-F02｜保留**：`block_002` 四路互斥；`ir_010/ir_016/ir_022/ir_026` 每条路径只执行其一。
- **Q04-F03｜保留**：`ir_007/ir_014` 提取日期；`ir_010/ir_016` 保留原值和 YYYY-MM-DD。
- **Q04-F04｜保留**：`ir_022/ir_026` 的实际输入省略 from_date，符合配置。
- **Q04-F05｜保留**：`ir_008/ir_020` 提取 limit，`ir_010/ir_022` 保留原值。
- **Q04-F06｜保留**：`ir_016/ir_026` 实际省略 limit，没有默认值。
- **Q04-F07｜保留**：`ir_013/ir_019/ir_025/ir_029` 返回各自同次响应 items，并有 unchanged。
- **Q04-F08｜保留**：`Skill.constraints` 全局禁止 index.delete，各路径无该操作。
- **Q04-F09｜保留**：能力说明只作约束，`ir_010/ir_016/ir_022/ir_026` 无 fuzzy 扩展。
- **Q04-F10｜保留**：`ir_004/ir_005` 仅检查存在，没有校验、规范化或转换步骤。
- **Q04-F11｜保留**：`ir_012/ir_018/ir_024/ir_028` 写同一路 total 后分别进入对应 return。

## 复核边界

已阅读主文件、references/workflow.md 和 query.yaml。本次结论限第 1 次；路径互斥成立不代表源文已定义异常值或调用失败策略，不新增重试、兜底或验证。 已核对冻结源文、[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/Q04/deepseek-v4-flash-max/1/analysis.json) 的完整 CFG、diagnostics 与 metadata，并仅参考旧评审第 1 次逐事实 assessments。本页为外置 Codex 语义评审意见，尚待共同复核，不代表人类已确认；未修改输入、ZIP、PNG、生产流程或 API。

