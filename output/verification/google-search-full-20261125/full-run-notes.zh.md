# `google-search` 全量图例

本次从两个原始源文件重新生成 Task、工作流、CFG 和标注，经修订复审后，对最终选定的产物运行前向传播、反向需求和 DOE 判定。整个流程到达 DOE，最终状态为 `partial`。图覆盖 38 个基本块、65 条 IR、42 条控制边和 60 处结果引用。65 条 IR 中有 38 条是块尾的 `dispatch` 或 `return`，其余 27 条表示数据获取、计算、交付等操作。

| 路径 | 前向传播 | 反向需求 |
| --- | --- | --- |
| 命令行入口 | `ir_025` 读取环境变量 `GOOGLE_API_KEY`，经 `ir_032` 传入函数体。`ir_034` 把密钥写入参数对象的 `key` 字段，`ir_036` 将请求发给 Google。 | R9 对 `ir_034` 输出 `key` 的需求经字段构造规则回溯到该操作的密钥输入，再回到 `ir_032` 的调用入参。 |
| 独立函数入口 | `ir_052` 接收形参 `api_key`。`ir_054` 构造参数对象，`ir_056` 把含有 `params.key` 的请求发给 Google。 | R9 对 `ir_054` 输出 `key` 的需求回溯到 `ir_052` 的 `api_key` 输入。 |

最终标注把 R9 绑定到两次调用的请求参数对象，并分别对 `ir_034` 和 `ir_054` 的构造结果提出字段级需求。上表的反向路径从构造结果上的 `key` 需求出发。`ir_037` 和 `ir_057` 的请求结果分支缺少可执行的语义记录，CLI 错误输出 `ir_050` 也缺少语义记录，本次未建立错误输出的暴露判断或可删减结论。

[全图概览](google-search-full-cfg-overview.svg) · [完整标注 CFG](google-search-full-cfg.svg) · [可搜索标注和双向分析记录](google-search-full-annotation.html) · [运行记录](../../../experiments/doe/runs/document-guided-google-search-full-high-20261125-172053/report.md)
