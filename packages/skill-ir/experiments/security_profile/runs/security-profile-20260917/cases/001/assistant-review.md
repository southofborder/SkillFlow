# 001 / N01 助手复核

程序状态：`complete`。标注记录完整，但执行者归属、隐含模型观察和网络依据仍需复核；不能认定语义标注正确。

13条IR均有profile；字段提取、条件计算和计数的transform有具体动作依据；没有将禁止发送access_token声明当成新过滤操作；dispatch未强贴transform；本地count.txt标fs_write；空return没有user_output。

本复核没有修改模型标签或原图；逐条引文匹配通过不代表推断成立。

## 1. ir_001 — actor/effects（证据不足）

模型把文件读取确定为仅由agent_runtime本地执行，进而没有model_observe且没有未决。原文和图未提供模型不可见或仅本地处理的机制；此执行者归属不能由read_events_file这个操作名独自推出。与003的同类读取被标tool并按EM02添加观察形成关键不稳定性。

- 源文：SKILL.md: 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。
- 实际图：block_001/ir_001: read_events_file，输入events.json，输出result_001(event_records)，metadata={}。
- 模型标注：actor=[agent_runtime], roles=[source], effects=[fs_read]；reason称“该 IR 为读取文件的本地运行时动作，IR 未给出具体工具名。”；unresolved=[]。
- 后续建议：后续版本明确抽象读取操作如何映射到执行模型；当前不应把未指明工具等同于确定的本地隔离。依据不足时保留actor/模型观察未决，不据此认定模型看不到文件。

## 2. ir_002 — actor（证据不足）

EM03仅区分调度与内容可见，不规定每条dispatch实际由LLM执行。“可参与调度”不足以支持确定actor=llm。相同推断还用于ir_004、ir_007、ir_009、ir_011。

- 源文：SKILL.md 描述条件与流程，没有指定控制分派由LLM还是运行时执行。
- 实际图：block_001/ir_002 opcode=dispatch，inputs=[]，outputs=[]，无执行主体元数据。
- 模型标注：actor=[llm]；evidence引用EM03“LLM 调度不等于内容可见”，reason为“该 IR 为调度分派，LLM 可参与调度。”
- 后续建议：保留控制操作roles/effects为空的正确处理；执行者需要明确绑定规则或未决，不能将可能性写成确定归属。

## 3. ir_008 — effects（证据不足）

发送通知可支持sink，但固定net_send要求向远端发送。当前引文只有通知发送与接收对象，模型理由自行加入“远端”；未明确网络实现，也未记录未决。不能认定必错，但网络效果证据不足。

- 源文：SKILL.md: 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。
- 实际图：block_004/ir_008 opcode=send_notification；external_resource为notify.send；无URL或网络协议/部署说明。
- 模型标注：effects=[net_send]；引文send_notification；理由“调用外部通知工具发送内容，属于向远端发送。”
- 后续建议：保留发送动作和sink；需工具契约或明确远端依据才能确定net_send，否则将部署/通信边界列为未决。不按名字补造net_receive。

上述为助手复核意见，不冒充用户人工确认。证据不足项不计为已证实错误；仅003/ir_001的观察效果与sink角色缺失作为明确的局部标注不一致。
