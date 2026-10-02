# 一次联合标注修复

状态：`execution_error`；阶段：`repair`

IncompleteRead(0 bytes read)

最多完整修复一次；审查未提出问题不等于语义正确性证明。

最后结构有效候选：original

- 初审：`complete`；[阶段报告](initial-review/report.md)

  源文要求对 index.search 发起一次调用并取其响应（src_008；CFG 输出语义名 'index.search response'），该响应属于新获取的工具内容。按 EM09，已知工具获取且无网络证据时，应以 tool 位置（loc_index_search）上的 receive、在 null-effect 事件中表达，并保留实际请求输入与可能的依赖；工具返回内容的获取边界不能被查询输入穷尽，请求影响不能替代获取来源。但 transfer_specs/ir_007 的唯一原子操作是 op='compute'（inputs 1/2/4、dependencies='possible'、output='search_response'），既未引用 loc_index_search，也未建立任何 receive/获取关系：响应被表示成仅由请求参数计算出的值，'新获取的工具内容'这一来源身份与获取边界被丢失；该 IR 的 profile 证据（ann_0046）自称按 EM09 以 tool 位置 receive 表达，与实际 transfer_specs 相互矛盾。连带影响是生成的模型观察 obs_0005 把本段可能模型可见的版本绑定为请求参数（输入 1/2/4）；按 EM10，default 模式下可观察的是 read/receive 的输出，且不会仅因获取响应而观察 receive 的请求参数，因此修正获取表示后该绑定应落在获取到的响应版本（search_response）上。受影响的数据关系是：搜索响应的来源（新获取 vs 由请求参数计算）以及该段模型可见版本的绑定。

- 完整修复：`execution_error`；[阶段报告](repair/report.md)
