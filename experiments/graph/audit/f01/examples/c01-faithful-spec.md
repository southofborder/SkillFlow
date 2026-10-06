# c01 人工回述规格示例

**这是人工撰写的预期表达示例，不是模型输出、实测结果或固定唯一标准答案。不得将此示例传入回述器。**对应原始 F01 基线，示范如何把动作、绑定和声明分开说清楚。

图首先设置两个 context 获取块，分别读取 source_id 和 FAST_KEY，产生后续引用的两个结果。操作名称将前者描述为来自请求、后者描述为来自环境；这些来源文字来自图本身，未另行检查实际运行环境。

读取之后检查 key 是否存在。有 key 的条件边通向首次 fast.fetch 调用，列出的输入包括 fast.fetch 资源、source_id 的结果和 FAST_KEY 的结果；无 key 的条件边直接通向 archive.fetch。首次 fast 调用定义 body 和 error 两个结果，后续成功检查读取其 error 结果。

首次 fast 成功时，图先记录一次向 status.txt 追加 success 的操作，再返回首次调用定义的 body。首次 fast 失败时，进入失败类型检查：transient 条件边进入一次 retry_fast_fetch，non-transient 条件边转向 archive。重试调用仍引用 source_id 和 FAST_KEY，产生独立的重试 body/error；重试成功时追加 success 并返回重试 body，重试失败时转向 archive。

archive 调用列出的资源为 archive.fetch，唯一的 result 输入来自 source_id。它独立定义 archive body/error；成功分支先追加 success，再返回 archive body；失败分支先追加 failure，再返回 archive error。这些返回点无控制出边。success/failure 是图中的 literal 状态值，不把它们说成完整响应对象。

图级约束记录了不得将 FAST_KEY 传给 archive 或诊断输出、所有终态返回前应追加状态、成功后应返回同一 body 并停止后续 fetch。retry 指令的约束还明确记录只重试一次及非暂时性失败不得重试；archive 指令的约束记录最多一次、只传 source_id 和失败时停止不重试。

上述控制关系、输入和返回绑定可逐项从图定位。约束声明并不能证明开放操作内部绝无泄露，追加指令也不能证明本次文件 IO 必定成功；FAST_KEY presence 和 transient 分类的实现没有在此图中展开。

可核对位置包括 `/blocks/block_004/instructions/0`、`/blocks/block_008/instructions/0`、`/blocks/block_010/instructions/1/inputs/0`、`/blocks/block_011/instructions/0`、`/blocks/block_014/instructions`、`/edges` 和 `/constraints`。
