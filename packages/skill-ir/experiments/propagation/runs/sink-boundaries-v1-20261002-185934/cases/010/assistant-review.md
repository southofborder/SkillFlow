# 010／Q04 助手复核：工具边界成立，可选参数关系仍有精度损失

本次标注及传播均为 `complete`，12 条真实 IR 全部形成记录，传播诊断为空。程序生成了 10 个 sink：8 个模型观察、1 个外部工具交付、1 个持久文件写入。前九项等级为 2，文件写入等级为 1。这里的等级描述接收或保存边界，不是数据敏感度、任务必要性或 DOE 风险分数。

复核使用本目录的冻结源文、`selected-analysis.json`、原始标注、编译结果及 `propagation/doe-input.json`。这是助手对材料的静态复核，没有执行 Skill，没有修改候选，也没有重新调用模型。

## 1. 本轮边界补全正确表达的内容

| 关注点 | 本例实际表达 | 复核意见 |
| --- | --- | --- |
| 来源整体 | `ir_001` 从 `storage/request.json` 读取整体；后续 term、from_date、limit 都登记为该整体的组成部分 | 没有把所需字段替换成没有父容器的独立来源 |
| 请求交付 | 编译记录 `ir_007/events[1]/atomic_ops[1]` 是 `deliver → tool/index.search` | 与工具获取响应分开，形成真实的交付关系 |
| 工具返回 | 同一事件的 `atomic_ops[2]` 是 `receive → tool/index.search`；响应 Data 的 `acquired_from="tool:index.search"` | 返回内容保留新的获取边界，没有退化成仅由请求值生成的计算结果 |
| 返回后的模型观察 | `ir_007/events[2]/atomic_ops[0]` 观察刚取得的响应 Data | 观察绑定的是返回版本，没有把请求参数冒充响应 |
| 网络断言 | 本例没有 `net_send` 或 `net_receive`；工具位置为 `recipient/null` | 依据 EM12 保留未说明部署的外部接收可能性，没有虚构网络通信 |
| 响应字段原值 | `ir_009` 选取 `response.total`，`ir_011` 选取 `response.items` | 使用了 `select_part`，保持原字段关系 |
| 文件写入 | `ir_010` 将 total 原值写入 `count.txt`，文件位置为 `task/persistent` | `storage_write` 等级 1；不是把整个搜索响应写入文件 |
| 普通返回 | `ir_012` 在 CFG 中返回 items，传播事件及公开输出绑定均为空 | 没有为普通 return 虚构用户输出或调用者位置 |

位置属性有真实定位及契约依据：`request.json` 与 `count.txt` 的身份来自源文／CFG，默认持久属性引用 EM12；`index.search` 的外部接收可能性引用 EM12 的未说明部署规则。编译器生成的模型位置为 `recipient/null`。`null` 只表示未建模留存期限，不能解释为接收方不保存内容。

读取 request 后的整体模型观察是统一抽象运行时契约下的可能行为，不是实测运行日志。获取响应后的观察同样由处理段及编译规则落实。两种观察都不会自动改变工具实际收到的参数范围。

## 2. 仍需保留的实质精度问题：可选参数被合并成不透明计算

源文 `references/workflow.md` 第 10–13 行明确要求：from_date、limit 存在时原样传入，缺失时省略参数。冻结 CFG 也保留了字段值、存在性结果及这些调用约束。

上游字段关系已经保持正确：`ir_004` 用 `select_part` 取得 from_date，`ir_005` 用 `select_part` 取得 limit。但 `ir_007` 又将两个字段值及两个存在性结果合并为 `compute → optional_search_args`，四项依赖全部为 `possible`。原始标注理由甚至明确写道：

> 可选参数按存在性条件传入；用 compute 保守组合，所有依赖均为 possible，不声称精确原值传递。

具体位置如下：

- 原始标注：`annotation/audit/raw-annotation.json` 的 `/transfer_specs/ir_007/events/0/events/0/atomic_ops/0`。
- 最终业务记录：`propagation/doe-input.json` 的 `/records/ir_007/events/1/atomic_ops/0`。
- 工具交付：同一事件的 `atomic_ops[1]`，输入为 term 原字段和这个不透明组合结果。

因此，当前工具 sink 能回溯到相关输入的可能影响，但不能仅凭其载荷结构确认可选参数保留原值、按名字对应、缺失时省略。条件文字仍在 CFG 中，没有被删除；问题在于传递载荷没有继续保留已知的精确字段身份。下一阶段若只看 sink 和 Data 关系，容易把本来明确的参数关系当成未知计算。

这属于仍需澄清的标注选择及参数表达精度问题，不是本轮 sink 类型或等级计算失败。存在性条件确实需要保留；不能为了去掉 `compute` 而把两个可选字段无条件交付。后续应将“字段原值”和“控制其是否作为参数出现的条件”区别表达，避免把明确原值关系退化为不透明依赖。本轮没有改动该候选。

## 3. 同一工具调用的请求绑定尚未一致

工具 `deliver` 的实际输入列表是两个位置：term、optional_search_args。紧随其后的 `receive` 却将 term、from_date 值、from_date 存在性、limit 值、limit 存在性五项列为输入。对应响应 Data 的 `origin.inputs` 也采用后面这份五项列表。

这两份列表并不一致：一份表达交付载荷，一份把载荷影响因素及控制旗标展开后混列。存在性旗标可以影响参数是否出现，但它不等于原文要求传给工具的业务参数。若 `receive.inputs` 承担“实际请求输入”的契约，应与实际交付表达一致；额外的控制影响应保留为适当依赖关系，不能不加区分地当作请求内容。

定位：`/records/ir_007/events/1/atomic_ops/1/inputs` 与 `/records/ir_007/events/1/atomic_ops/2/inputs`；响应 Data 可从后者的 `outputs[0]` 找到，其 `origin.acquired_from` 为 `tool:index.search`。

这不证明两个存在性旗标已经被明文发送，也不证明整个 request 被发给工具。`possible` 只是可能影响，不能解释成明文包含。本例的确定结论是：工具边界和响应来源已建好，但实际参数内容与控制依赖的精度仍不足以直接作精确的参数级必要性判断。

## 4. 本例结论

本轮新增的边界表达可用：工具请求、工具返回、模型观察、持久写入彼此分开；没有凭工具名造网络效果；固定等级及数据版本关联正确。程序完整性校验通过不代表联合标注的所有关系都已精确。

本例可以作为带上述限制的诊断性 DOE 输入。后续重点应是可选参数的精确身份、条件与实际请求绑定，而不是继续扩大工具或模型观察范围。敏感性、必要性和 DOE 判断本轮尚未进行。
