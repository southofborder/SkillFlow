# 003 / N03 助手复核

程序状态：`complete`。标注记录完整，存在model_observe对应sink角色遗漏，以及执行者/网络效果依据不足。

12条IR均有profile；读取动作按EM02标注model_observe；筛选、字段提取和计数标transform但没有声称去敏；dispatch保持空roles/effects；本地写入为fs_write；空return未标user_output。

本复核没有修改模型标签或原图；逐条引文匹配通过不代表推断成立。

## 1. ir_001 — roles（漏标）

本profile已明确标注model_observe，并引用EM02说明内容进入LLM上下文，按sink定义这也是内容到达可见边界；roles却只有source。多角色契约支持同时标source和sink，当前记录遗漏观察边界角色。

- 源文：SKILL.md 表格第1项：读取用户提供的 events.json。
- 实际图：block_001/ir_001 read_events_json输出result_001(events_records)。
- 模型标注：actor=[tool], roles=[source], effects=[fs_read,model_observe]；model_observe理由“该工具输出 events_records，按 EM02 默认进入 LLM 上下文。”
- 后续建议：在保留model_observe解释的前提下补充sink角色及观察规则证据。后续验证可检查已确认effects与角色解释的一致性，但不要提前传播数据。

## 2. ir_003 — actor/effects（证据不足）

select_eligible_event_records被确定解释为“本地筛选、代理运行时执行”，但源文与图没有指定实现主体或模型不可见机制。transform动作本身有依据；由谁筛选以及是否因此发生模型观察仍缺执行映射。ir_005字段提取、ir_009计数也使用了同类确定本地解释。

- 源文：SKILL.md 表格第2项：仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。
- 实际图：block_002/ir_003 opcode=select_eligible_event_records，输入事件集合、输出eligible_records，metadata={}。
- 模型标注：actor=[agent_runtime], roles=[transformer], effects=[transform]；actor理由“该 IR 为本地筛选操作，由代理运行时执行。”；unresolved=[]。
- 后续建议：保留有依据的transform；不要仅凭可编程实现就断言实际由本地程序完成。后续固定执行映射或标注actor及观察边界未决。

## 3. ir_007 — effects（证据不足）

向recipient发送通知支持内容到达接收方，但没有独立远端网络依据。模型从通知语义推断“远端接收方”，未说明假设或记录未决。

- 源文：SKILL.md: 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。
- 实际图：block_004/ir_007 opcode=notify.send，参数为接收对象和body；metadata={}，无URL/协议。
- 模型标注：effects=[net_send]；理由“向记录的 recipient 发送通知内容，属于向远端接收方发送。”
- 后续建议：保留sink和工具调用事实；缺少工具部署契约时，将网络具体效果记为未决，不按工具名推测通信方式。

上述为助手复核意见，不冒充用户人工确认。证据不足项不计为已证实错误；仅003/ir_001的观察效果与sink角色缺失作为明确的局部标注不一致。
