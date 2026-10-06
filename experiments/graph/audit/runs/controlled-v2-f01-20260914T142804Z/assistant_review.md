# 五案例助手事后复核

本文件是助手复核意见，尚未经用户确认，不改写任何模型原始响应或有效判定。

## c01 · F01 原图

四组关键要求均有实际对应核对，没有观察到关键语义漏报或业务缺陷误报；不能将局部证据说明错误省略为完全正确。

**解释文字问题：finding_18 / evidence_description_location_error**

模型写法：“例如 result_002 来自 block_001/instructions/0”。

复核意见：result_002 由 block_002 的 ir_003 读取环境 FAST_KEY 后产生；rich 位置 /blocks/1/instructions/0/outputs/0，公共图位置 /blocks/block_002/instructions/0/outputs/0。

依据：[模型结果](parsed/c01.json)、[实际受控文本](inputs/c01/controlled.txt)、[当前图](inputs/c01/cfg.json)、[原始修改建议](suggestions/c01.md)。

## c02 · archive 额外接收密钥

错转与内部冲突是同一额外密钥输入的两方面，计一个目标缺陷。模型正确区分 archive.fetch 资源定位符与 source_id/FAST_KEY 业务输入。

建议的具体含义：建议修改 /blocks/block_011/instructions/0/inputs/2 对应的额外 result_002 输入；删除实际输入后重新生成受控文本及派生链接，不手工编辑 :link。保留 archive.fetch 资源定位符。

依据：[模型结果](parsed/c02.json)、[实际受控文本](inputs/c02/controlled.txt)、[当前图](inputs/c02/cfg.json)、[原始修改建议](suggestions/c02.md)。

## c03 · 失败返回前缺少状态追加

模型依据完整操作清单识别 block_014 只剩 ir_028 return，并明确标题及全局声明不能补回 append；其他失败返回语义分别判定保留。

建议的具体含义：在 /blocks/block_014/instructions/0 的现有 return 前添加状态追加操作。failure 只是可采用的状态值示例，源文未限定唯一存储格式。

依据：[模型结果](parsed/c03.json)、[实际受控文本](inputs/c03/controlled.txt)、[当前图](inputs/c03/cfg.json)、[原始修改建议](suggestions/c03.md)。

## c04 · 重试成功返回首次 body

返回输入实际为 result_004，链接到首次调用 body；重试结果为 result_008。判断引用实际输入、定义链接与成功边，具有不依赖块名的证据；本次响应仍不能证明模型内部不借助名称提示。

建议的具体含义：修改 /blocks/block_010/instructions/1/inputs/0 的完整结果引用：identifier=result_008，并同步 semantic_name=retry_fast_fetch_response_body；相应更新块名后再生成受控文本。单改名称不能修复绑定。

**解释文字问题：finding_2 / source_order_overstatement**

模型写法：“源文要求先读 request 中的 source_id，再读环境中的 FAST_KEY”。

复核意见：源文要求两项读取，用 and 连接，未指定它们必须先后执行；图将其记录为先读取 source_id，再读取 FAST_KEY。

依据：[模型结果](parsed/c04.json)、[实际受控文本](inputs/c04/controlled.txt)、[当前图](inputs/c04/cfg.json)、[原始修改建议](suggestions/c04.md)。

## c05 · 无依据增加两秒等待

模型识别实际 wait_for_seconds、literal 2 和明确 seconds 约束，并定位到 transient 检查后、dispatch 前；不是仅凭不透明名称猜测等待。源文未给出该新增动作依据。

建议的具体含义：删除 /blocks/block_007/instructions/1 的 ir_wait_1 记录及其附属输入/约束，保留原有检查和 dispatch，之后重新生成操作清单。两条后续分支前记录了等待，并不构成已观察到运行延迟的证明。

**解释文字问题：finding_7 / evidence_description_location_error**

模型写法：“fact:/blocks/5 检查并返回首次 fast.fetch body result_004；fact:/blocks/9 检查并返回 retry body result_008”。

复核意见：两个位置实际是追加状态和返回块；成功检查分别位于 fact:/blocks/4/instructions/0 和 fact:/blocks/8/instructions/0。返回在 fact:/blocks/5/instructions/1 和 fact:/blocks/9/instructions/1。

**解释文字问题：finding_8 / insufficient_cited_support_for_operation_claim**

模型写法：“archive.fetch 操作输入为 archive.fetch 资源定位符和 result_001 source_id，未包含 result_002 FAST_KEY；图中没有诊断输出操作。”。

复核意见：本条正式引用只有 fact:/constraints/0，足以支持禁止声明被保留，但不足以单独支持所有操作层说明；应同时引用 archive 输入与实际 key 使用/定义链接。

依据：[模型结果](parsed/c05.json)、[实际受控文本](inputs/c05/controlled.txt)、[当前图](inputs/c05/cfg.json)、[原始修改建议](suggestions/c05.md)。

## 统一边界

- 四个命中仅针对预先固定的开发反例；单次 F01 示范不支持统计显著性或泛化保证。
- 程序验证引用确实存在及引文一致，不证明自由说明准确或证据足够支持结论；c01/c04/c05 已出现相关问题。
- 没有模型 unknown 条目不意味着 I/O 成功、隐含副作用、条件实现或开放操作语义已获验证。
- 声明与动作分开保留；represented 仅为模型认为源要求在显式记录中有所对应。
- 受控语言冗长；本轮没有证明其在成本或模型理解准确性上优于直接读图。
- 所有修改建议待后续审查；本轮未编辑原图、重跑提取或补跑模型。
