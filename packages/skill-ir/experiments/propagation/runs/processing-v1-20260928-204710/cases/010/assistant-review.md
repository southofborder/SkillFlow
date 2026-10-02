# 010 / Q04：本轮助手复核

**上一轮完整响应多余括号的问题本轮没有复现。**这次收到一个合法 JSON 对象，经过严格引用、引文和规格校验后完成编译与传播。下面同时审查数据关系；JSON 合法不代表模型标注已证明正确。

入口：[传播审查页](propagation/report.html) · [DOE 原始事实](propagation/doe-input.json) · [冻结 CFG](cfg-review.md) · [源文工作流](annotation/inputs/package/references/workflow.md) · [原始标注](annotation/audit/raw-annotation.json) · [编译映射](annotation/audit/compilation-map.json) · [请求及结果校验](annotation/result.json)。

## 工程结果

- 标注 complete，传播 complete；12 / 12 条 IR 形成记录，9 份 Data，模型未决和动态诊断均为 0。
- 恰好 1 次逻辑调用、1 次 HTTP 尝试。实际请求包含 `response_format={"type":"json_object"}`，同时保留 SSE 参数；请求体 SHA-256 与冻结配置核验通过。
- 请求模型 deepseek-v4-flash，服务实际返回名称 deepseek-flash。没有修剪括号、修复 JSON 或质量补跑。
- 8 个非空处理段全部为 default，没有把未规定实现的任务解释成 local 隔离。契约仍为 skillflow-abstract-runtime-v2。
- 本文为助手对保存材料的复核，不是另一个远程模型审查阶段；没有改写标注或 DOE 文件。

## 关键关系逐项审查

| 位置 | 实际记录 | 复核意见 |
|---|---|---|
| ir_001 | read(request.json) 后由编译器观察同一整体 | 来源整体保留；没有以 term 或其他业务字段代替文件来源。默认观察是契约下的可能行为。 |
| ir_003 | select_part(request, ["term"]) | 保持 query_term 的字段原值，没有做模糊扩展、归一化或不透明重计算。 |
| ir_004 / ir_005 | 分别 select_part from_date / limit，再 compute 存在性，两个输出独立绑定 | 值关系与存在性判断分开。存在性结果依赖 request 整体，未被冒充成参数明文。 |
| ir_007 | tool:index.search 上的 receive；实际参数位置依次为 input[1]、input[2]、input[4] | 响应保留新的获取来源及三个值的 possible 依赖；不是仅由查询值生成的 compute。未把工具名当成网络证据。 |
| ir_007 编译后的第二事件 | model_observe 接收刚取得的 response | 观察工具返回版本，不把三个请求参数当成响应内容。 |
| ir_009 / ir_011 | select_part(response, ["total"]) / select_part(response, ["items"]) | 两个字段明确来自同一工具响应，未退化为 opaque compute。 |
| ir_010 | 将 total 字段写入 count.txt | 写入值正确，没有把完整响应或请求文件写入；具体覆盖模式仍有推断边界，见下文。 |
| ir_012 | 普通 return，输入为 result_009，即响应 items | 原 CFG 返回身份保持；没有无依据增加 user_output。 |

共 7 处编译观察：文件取得之后、term/from_date/limit 处理之前、工具返回取得之后，以及 total/items 提取之前。同一整体在不同段重复出现表示分析边界，不表示创建了多份来源，也不是测得了七次真实模型调用。

可从以下真实 Data ID 检查来源和字段：

| 阅读名称 | Data ID |
|---|---|
| request.json 整体 | data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95 |
| term 原字段 | data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123 |
| from_date 原字段 | data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2 |
| limit 原字段 | data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7 |
| 工具响应整体 | data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14 |
| total 原字段 | data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543 |
| items 原字段 | data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70 |

响应整体的 acquired_from 为 tool:index.search；origin.inputs 是三个可能的业务参数值，dependencies 为 possible。total/items 通过 part_of 与 path 连接到这个响应。未知剩余仍保留，不能把已列出字段当成完整内容清单。

## 仍需明确的边界

1. **可选参数的存在条件保留在 CFG 和依据中，尚未成为传播记录中的条件化参数集。**ir_007 的 receive.inputs 只列值位置 1、2、4，不列存在性标志 3、5，因而没有把存在性标志错传为业务参数。但当前 may 分析不求值“缺失则省略”的条件，DOE 中三个输入同时列出不能读成每次调用都会传三个参数。模型理由也明确 from_date/limit 仅在存在时传入。这是当前条件精度边界，不能以传播 complete 证明条件执行已完全验证。
2. **write replace 比“写入”更具体。**原文要求把 total 写入 count.txt，未明确已有文件内容的保留方式。标注从单次写入选择 replace，记录形成强更新；这不等于源文已经证明覆盖旧内容的全部行为。实际写入值仍正确。
3. **执行主体的一些理由仍比材料具体。**例如 ir_007 称调用由“本地 agent runtime”执行；任务没有规定实现。该说明没有被用于 local 隔离，默认观察已经保留，但主体证据充分性仍是下一轮聚焦语义审查的候选。
4. **compute 存在性是派生关系，不是已求出的布尔值。**本轮没有真实 request 内容，也不执行条件判断。没有字段名单或运行数据不意味着没有敏感信息。

本轮未发现对 term、total、items 的原字段关系退化、请求参数与响应来源混同、存在性标志直接外传，或新增 index.delete、验证／归一化步骤。上述结论来自已保存关系的助手复核，不是形式证明；三份原始图和历史结果没有被追溯改写。
