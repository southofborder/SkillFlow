# Assembly 与审查输入补充快照：运行中，只读检查

本记录检查 `document-guided-ga4-processing-restart-high-20261117-172228` 已保存的材料，源文审查仍在进行。没有执行校验器、项目分析代码、模型、Skill、后端或重放，也没有修复或修改冻结文件。

**assembly 标为 partial 的直接原因是 raw annotation 保留了八条 processing_gaps。**runner 的明确判断就是该列表非空时标记 partial。不是 assembly 抛错或新增隔离：manifest 已 ready，compiled outcome 为 completed，489 条 IR 全部存在；review 输入的 stage_failures 是空对象，Task、CFG、annotation 都可用。fragments 的三个 false 表示已提供合并 annotation，不表示三个成功阶段缺失。

八条缺口位于 ir_005、140、151、311、329、346、450、488，涉及 dotenv 后态、稀疏数组位置/长度、成员缓存与异常细节，以及尚无实现的调用所属保存文件/Markdown 总结链。编译后都为 unmodeled=false，但仍是明确保留的分析限制；表示完整不等于语义问题已经解决。

task-correspondence 首答接受；sensitivity 在修正 declarations 154–156 的三条 evidence-kind 记录后接受。49 条任务对应关系为 **29 expressed、18 partial、1 unmapped、1 retained-only**。92 条普通需求与39组操作需求编译为 **192 条 goal**；annotation 还有两个结构化表达式、62 个 sink 边界及684条输入契约记录。这些是已生成材料清单，不是已到达 sink 或已通过源文审查的数量。

审查包含 **684 个义务/契约 = 202 compute + 482 编译工具操作义务**，以及 **2,540 个范围**：required 1,177、remainder 678、interface 482、rule 202、unresolved_range 1。全部684个义务ID和2540个范围ID都在提示中。16份源文文本与冻结源文件逐字节相同，共155,170字节；每份完整编号行块都在提示中。本次只核对源文及ID覆盖，没有独立展开共享表示中的每一个契约字段。

初次审查核心提示 **992,274 字符**，加212字符适配器封装后为 **992,486**，比1,048,576上限少 **56,090**。这不保证未来可能的纠错提示也能容纳；本审计没有截断或改变输入。

现在已有实际任务输出子字段选择器：inspect_url 在 ir_302 输入0要求保留 indexStatus.verdict、coverageState、lastCrawlTime、mobileUsability、richResults；full_property_metadata 分别要求整个首个响应，以及 ir_248 请求参数的 name 字段。processing 中对应 inspection base、metadata 请求对象构造仍只有整值输出规则，因此此前的字段精度疑点已有具体任务/消费者依据。这里没有执行反向闭包，也不提前宣判将来的传递结果。

192条goal中127条有非空路径；属性分布为151 value、22 action、12 shape、5 truth、2 cardinality。这是目标行数，不是唯一字段数或必要性证明。凭据配置还明确保留环境输入与构造器字段，但这些独立任务种子不能代替真正的客户端到远程接收方依赖。

契约充分性、必要性、局部隔离及源文忠实度仍须正常源文审查。本快照没有已接受的审查检查、传播计数、输入评估、删除或DOE结论；到此停止，不干预正在运行的 review。
