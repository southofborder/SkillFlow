# `google-search` 组会讲稿

图中截取 `google_search` 独立调用中与密钥直接相关的三条 IR。完整 CFG 包括脚本入口、函数入口以及正常和异常路径，共 35 个基本块、62 条 IR。

1. **语义标注。** `ir_003` 绑定函数形参 `api_key`，图上用 `K` 表示该敏感值。`ir_005` 构造请求参数，标注说明 `params.key` 取自 `api_key`。`ir_007` 将请求交付给 Google Custom Search。
2. **任务绑定。** 任务要求 R9 约束搜索请求的参数，其中对密钥的要求绑定到 `ir_007` 发送的数据中的 `params.key`。蓝色虚线表示这条绑定。
3. **双向分析。** 顺着绿色实线，前向传播确认 `K` 经 `params.key` 到达 Google。沿紫色虚线，反向分析从该请求需要保留的 `key` 出发，依据 `ir_005` 记录的字段关系，将需求回推到 `api_key`。同一条字段关系在两个方向上分别回答密钥去了哪里、请求为什么需要它。

这三步以线上生成的原始 CFG、任务和标注为输入，由本地分析程序求得。线上整轮停在修订复审的材料准备阶段。错误输出仍缺少可达性和字段需求依据，组会上只报告请求边界。 [线上结果](../../../experiments/doe/runs/document-guided-google-search-retry-high-20261125-161918/report.md) · [前向传播记录](from-original-online-selection/propagation/sinks.json) · [反向需求记录](from-original-online-selection/doe/audit/demand-support.json)
