# 三例正式在线复测

本轮复用冻结 Skill 和 CFG，采用当前冻结的结构纠正政策。实际模型响应、审查和修复原样保留；助手意见不回写业务事实。

**工程完成状态与语义正确性分开。以下调用数包含结构纠正；DOE 数量是静态信息范围结论，不是实测泄露次数。**

| 案例 | 正式链 | 审查状态 | 逻辑请求 | 结构纠正 | HTTP尝试 | Sink | DOE范围结论 |
|---|---|---|---:|---:|---:|---:|---|
| 001 | complete | review_passed | 5 | 3 | 5 | 6 | no_excess_established: 3, excess_supported: 1 |
| 010 | complete | review_passed | 5 | 1 | 5 | 12 | 无敏感范围结论／未生成，见案例状态 |
| 013 | failed | not_run | 1 | 0 | 3 | None | 无敏感范围结论／未生成，见案例状态 |

## 001：实质复核

本轮 6 个 sink 全部完成对照，声明了集合成员 access_token 的凭据敏感性；4 个匹配范围中，1 个为 excess_supported、3 个为 no_excess_established。支持的过量结论位于逐元素准备阶段的模型观察：recipient/summary 保持同元素原值，不需要观察该元素的 access_token。初审虽未报问题，助手仍发现两类前端需求缺口：读取文件被绑定为整个读取结果的 value 需求，形成过宽保留；通知字段和计数部分目标绑在生产位置，未完整绑定最终 deliver/write 载荷。另外，现有形状／基数需求匹配保守阻止了筛选及计数观察中的成员字段缩减，不能因此解释为计数需要凭据。

[助手实质复核](cases/001/assistant-review.html) · [阶段状态](cases/001/report.html) · [原始标注](cases/001/annotation/report.md) · [审查与修复](cases/001/refinement/report.html) · [传播](cases/001/propagation/report.html) · [传播事实](cases/001/propagation/doe-input.json) · [DOE审查页](cases/001/doe/report.html) · [DOE原始结果](cases/001/doe/doe-result.json)

## 010：实质复核

本轮 12 个 sink 完成对照，敏感声明为空，因此没有敏感范围 DOE 结论，不能称为所有内容安全。可选字段原值、存在性控制、请求构造及工具返回来源保持；请求侧需求包含 term、可选字段值及存在性，响应侧保留 items 和 total。初审误把原子操作消费槽位当作 IR 输入下标，提出错误修改建议；语义修复后的完整候选与原合法候选零字段差异，独立复审随后未报问题。这体现审查判断不一致，不是修复改变了错误关系。工具 sink 的请求需求仍通过 receive 的 external_request_retained 保守保留整请求，未直接关联查询和可选参数要求，边界需求绑定仍有改进空间。

[助手实质复核](cases/010/assistant-review.html) · [阶段状态](cases/010/report.html) · [原始标注](cases/010/annotation/report.md) · [审查与修复](cases/010/refinement/report.html) · [传播](cases/010/propagation/report.html) · [传播事实](cases/010/propagation/doe-input.json) · [DOE审查页](cases/010/doe/report.html) · [DOE原始结果](cases/010/doe/doe-result.json)

## 013：实质复核

本轮在首次联合标注的 DNS 解析阶段失败：1 次逻辑请求，3 次 HTTP 传输尝试，均未取得响应字节或模型返回。没有接受候选，未启动语义审查、传播或 DOE，当前案例没有旧成功文件残留。因此不能评价本轮凭据敏感性、反向需求或 DOE 是否改善，也不能将未生成结果理解为没有暴露。

[助手实质复核](cases/013/assistant-review.html) · [阶段状态](cases/013/report.html) · [原始标注](cases/013/annotation/report.md)

## JSON 格式成本与下一项改进

001 的 a002、a003 均是一个完整对象后多出单个 `}`。仅在离线副本中删除该字符后，两份候选均通过完整校验与编译；当前接受响应和请求链未被改写。

由这两个格式错误触发的 a003、a004 请求，服务端合计记录 136,049 tokens（60,631 prompt，75,418 completion；reasoning 已包含在 completion 内）。若 a002 当时经过受限归一化即可进入审查，这两个特定请求可以避免。后续审查对象会不同，因此这不是全链净节省预测，也不是货币费用。

当前 Prompt 已明确要求唯一对象、禁止多余括号；重复提醒不足以代替程序保证。建议新增受限、可重放的语法归一化：仅在完整传输、严格解析完整顶层对象、无重复键、剩余恰为一个多余闭括号时删除该字符，然后照常全校验。原响应保留，另存规则与变更审计。多对象、截断、缺字段、错引用及语义关系不自动猜修。

**本轮没有在运行中修改解析器。归一化已做离线可行性核验并形成建议，尚未接入生产流程。**

[详细规则与19类测试矩阵](json-cleanup-proposal.html) · [离线形式检查](audit/validation/format-inspection.jsonl)

## 重放与历史保护

[零 API 重放记录](audit/validation/actual-replay.json) · [调用及结构诊断统计](audit/validation/execution-metrics.json) · [历史摘要核验](audit/validation/preservation.json) · [上一轮封存回执](audit/validation/replacement.json)

其他 12648 个历史文件和上一轮 148 个失败运行文件摘要保持一致。当前入口使用本轮结果，没有回填旧成功文件。

分析仍依赖前端 Task、敏感性和处理关系声明以及受支持的需求规则。初审或复审未报问题不证明语义正确；无敏感声明不证明所有内容不敏感；possible 影响不等于敏感明文包含。
