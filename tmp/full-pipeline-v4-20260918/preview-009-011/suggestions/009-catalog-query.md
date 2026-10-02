# 009-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q03；运行：full-pipeline-v4-20260918；选图轮次：1
- 反馈停止：audit_error；原因：controlled unit does not exist: fact:/blocks/4/instructions/1/inputs/0
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：47e63e06f52fdd76f6a9e7b325ca6ee013a5219f4818a99df95477619d975721；源文 SHA-256：7c2332096f50b2ddde1c78cf0dce8b632e9a73a38a23e7427230ea6ebc06f409

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/009/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/009/annotation/result.json>)；本地审查页也可展开全文。

当前所选图没有合法的完整语义核对记录。不能由结构有效或其他轮次的发现推定通过。

## 安全标注未决

- {"instruction_id": "ir_012", "field": "effects", "reason": "IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。"}
- {"instruction_id": "ir_015", "field": "effects", "reason": "普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。"}
- {"instruction_id": "ir_016", "field": "effects", "reason": "IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。"}
- {"instruction_id": "ir_019", "field": "effects", "reason": "普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。"}
- {"instruction_id": "ir_022", "field": "effects", "reason": "IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。"}
- {"instruction_id": "ir_025", "field": "effects", "reason": "普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。"}
- {"instruction_id": "ir_026", "field": "effects", "reason": "IR 仅记录 external_resource/index.search，未明确远端网络通信；按 EM06 不能确定 net_send/net_receive。"}
- {"instruction_id": "ir_029", "field": "effects", "reason": "普通 return 可能面向调用方，但无法仅凭 return 确定 user_output；其他效果无依据。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：47e63e06f52fdd76f6a9e7b325ca6ee013a5219f4818a99df95477619d975721

助手复核：末图四种可选参数路径及各自返回来源清楚，核对因不存在的证据位置而失败；标注未决反映边界不足，主体推断和变换范围仍待收紧。

- 已读冻结 Q03 表格全文、r000 合法核对、r001 全部 29 条 IR/输入输出/控制边/约束、29 条 profile 全部证据及 8 项未决。r001 核对引用不存在的 fact:/blocks/4/instructions/1/inputs/0；实际该位置对应 block_005 第二条 ir_011 dispatch，inputs=[]。程序拒绝有事实依据，不能借助手复核或标注成功改判 audit_passed，也不是网络/本地持久化错误。
- 末图 ir_004/ir_005 取得 from_date/limit 存在性；from_date 分支后分别按 limit 分支，形成互斥四路：ir_012 输入 term/from_date/limit，ir_016 输入 term/from_date，ir_022 输入 term/limit，ir_026 仅 term。每条源文条件路径只到达一个 search，四个静态调用节点不等于运行四次；各调用约束保留 term 原值、from_date YYYY-MM-DD 与原值、limit 原值及对应缺失省略，未传 null 代替省略。
- 四路搜索结果各自绑定写 total 和返回 items：ir_012 的 result_007/008→ir_014/015；ir_016 的 result_009/010→ir_018/019；ir_022 的 result_012/013→ir_024/025；ir_026 的 result_014/015→ir_028/029。每路先写 count.txt 后原值返回本路 items，没有借其他分支结果或把 total/items 互换。fuzzy 仍为非执行能力说明，delete 禁止与不要求预校验/规范化均保留，实际只检查存在性而未加格式检查。
- r000 finding_6 将可选分支定义仍列在单一调用的输入依赖中直接判为缺失时仍传参；IR-PATH 不允许仅从部分路径未定义或输入列表存在就证明该运行含义，因此该冲突判定偏强，至少是依赖/实参解释边界。r001 通过展开四路解决了表示歧义并增加图规模，不应因末图更显式就倒推初轮一定有已证实的错误发送。末轮没有合法 audit，不能宣称核对器确认修复。
- 8 个 effects 未决对应四次静态 search 的网络边界与四个 return 的用户输出边界，是两类信息不足在不同 IR 上的逐项记录。未见远端地址或用户展示语义，保留这些未决合理。四搜索的 tool、source/sink 与 EM02 model_observe、各写入的 sink/fs_write、return 的调用方接收边界均有对应接口或固定假设依据。
- 四搜索 effects 只有 model_observe，roles 只有 source/sink；与 007/008 对同一 index.search 另标 transformer/transform 的口径不同。若词表把查询匹配/选择算动作变换，这里疑似漏标；若只记录黑盒外部边界，则应明确这一统一范围，不能按样例任意变化。不根据此疑点猜测工具内部实现。
- 读取/字段提取/存在性计算都被确定为本地 agent_runtime，而 dispatch 用 EM03 的“可能由LLM参与”直接列 llm actor；这些可能性不能替代实际执行归属证据。尤其 ir_001 的 context_read+fs_read 有调用者输入/文件来源支持，但不因此证明模型没有读取请求内容。标注 incomplete 与原未决保持，以上是助手意见，不是人工确认。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
