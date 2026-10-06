# 010-base 助手复核

结论：请求字段、工具新获取来源、响应字段和最终返回身份在本次事实中保持。初审没有重现上一轮普通 return 的过强“转发遗漏”判断；本次未确认需要修复的实质数据关系错误。

本页是助手对实际新产物的独立复核，不是用户／人工确认，也不是语义正确性证明。没有执行 Skill，没有计算 DOE 结论。已只读加载并核验完整传播运行；DOE 中源文、CFG 与冻结基线逐字段一致，审计中的原标注与本次重建候选一致。

本例初审一次逻辑调用、一次 HTTP 尝试，无重试；请求 `deepseek-v4-flash`，实际返回名 `deepseek-flash`。合法响应为 `outcome=completed、findings=[]`，因此没有调用修复或复审，选用 `original`。这里的 original 是本轮有差异清单的显式实验重建候选，不是伪造的一次新版标注响应。

## 实际数据链与观察

传播状态 `complete`，12/12 条 IR 形成记录，9 份 Data，动态诊断为空。零 API 重放为 `matched`，无差异。

| 关系 | 实际结果 |
|---|---|
| 请求来源 | D006 来自 storage:request.json，保留未知剩余，整体读取后被观察。 |
| 参数原值 | term=D007、from_date=D008、limit=D001，均为 D006 的明确部分；存在性结果 D009/D004 为计算结果，身份分开。 |
| 工具获取 | ir_007 receive 输入依次为 D007、D008、D001，边界 tool:index.search，输出 D003。D003 保留 acquired_from，以及请求值的 possible 依赖。 |
| 返回观察 | 获取后观察 D003；没有用请求值的观察替代响应观察。 |
| 写入值 | ir_009 取 D003.total → D005；ir_010 只写 D005 到 count.txt。 |
| 返回值 | ir_011 取 D003.items → D002；CFG ir_012 输入 result_009，在该条入口绑定到 D002。 |

完整记录中共 **7 个编译观察阶段**：请求整体获取后，三个请求字段处理前，工具响应获取后，响应 total 与 items 选取前。观察清单与实际记录对应。工具输入没有包含操作数 3、5 的存在性计算，也没有把工具标识当作请求内容。

## 普通 return 的误报排除

源文 `references/workflow.md:23 / src_014` 要求原样返回 items。CFG ir_012 已指向 `result_009=response_items`，实际入口状态对应 D002，其 `part_of=D003、path=["items"]`。return 没有公开输出，空 `events/output_bindings` 符合表示契约。

旧候选理由称转发关系在 transfer_specs 保留，措辞不准确，但完整事实中关系由 CFG 返回操作数承载，并没有消失。本轮没有为了迎合审查添加不存在的 output[0]、user_output 或无标签 deliver。初审空清单不能证明提示词一定消除了此类误报，只说明本次未再次报告它。

## 结论边界

- workflow.md:9–13、query.yaml 与 CFG 约束保留可选参数存在时传原值、缺失时省略的要求。当前 may 规格保留可能参数值，尚未完整编码逐参数动态条件；不能将 receive 的候选输入表读成每次执行必然同时传所有可选值，也不能据此证明每次调用已正确省略。
- tools 的请求影响与新返回来源已区分。possible 依赖不代表响应中明文包含全部请求字段。
- 未提供网络机制时使用 receive/tool 的无标签事件合法，不能为了填满效果表猜测 net_send/net_receive。
- “接口支持 fuzzy”不是执行 fuzzy 的请求；源文格式说明不是预校验。现标注没有添加归一化、额外检索或删除动作。

[初审](refinement/initial-review/report.html) · [传播页](propagation/report.html) · [DOE 原始事实](propagation/doe-input.json) · [零 API 重放](propagation/replay/summary.json)
