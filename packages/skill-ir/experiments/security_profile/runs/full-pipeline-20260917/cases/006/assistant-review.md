# 006 本次全流程助手复核

反馈状态：`extraction_error`；标注状态：`complete`。

完整阅读 SKILL.md、第 0 轮有效图、12 个有效核对项和全部 12 条 profile。第 1 轮提取 DNS 失败，选中本次第 0 轮图；特别核对本样例 body 应取 record_id 而非 summary。

1. **unrepaired_graph_omission**（ir_001）：完整输入字段模式仍未记录，summary 完全缺失；虽然 body 正确改用 record_id，源文仍明确每条记录包含 summary。第 0 轮对此给 omitted 有依据，第 1 轮提取失败使该缺口留在当前标注图。

依据：源文第 1 条包含 summary；ir_001 只有“事件记录”结果，constraints/metadata 均为空。；feedback.rounds[0].audit finding_3=omitted；rounds[1]=extraction_error；selection.revision=0。

2. **actor_and_effect_evidence_insufficient**（ir_003, ir_005, ir_009）：筛选、参数提取和计数被一律视为工具动作，再按 EM02 从“有工具输出”推出 model_observe。证据只说明 opcode 命名该行为，并没有给出实际工具实现；这种先假定工具再推导模型观察的链条缺少前提。transform 本身有业务依据，但具体 actor 和 model_observe 归属应保留未决，不能把当前多处观察标签当作已证实的执行路径。

依据：ir_003 actor.tool 理由“opcode 命名筛选动作，由执行该动作的工具执行”。；ir_005、ir_009 用同样理由标 tool；各自 model_observe 理由据工具动作有输出且未标为本地不可见。；源文没有规定筛选/提取/计数必须由工具或由模型处理。

3. **missing_role**（ir_001, ir_003, ir_005, ir_009）：四处已标 model_observe 的动作，roles 只有 source 或 transformer，均没有体现已声称的模型可见边界 sink。对工具执行前提尚不清楚的动作，应先澄清观察证据，再保持角色与效果的一致性。

依据：ir_001 roles=[source] effects=[fs_read,model_observe]。；ir_003/005/009 roles=[transformer] effects=[transform,model_observe]。

4. **actor_evidence_insufficient**（ir_002, ir_004, ir_006, ir_008, ir_010）：dispatch 全部确定为 llm，仅由 EM03“可参与调度”支撑，仍缺少具体实际执行主体证据。

依据：相关 actor.llm 引文“LLM 调度”，理由“EM03 说明 LLM 可参与调度”。

保留的正确表现：

- 关键变更没有被旧模板覆盖：ir_005 的约束明确 body 直接取当前记录 record_id 原值，result_004 正确作为 ir_007 的 notification_bodies 输入；没有错绑 summary。
- 每条选中记录一次发送、未选中跳过、全局禁传 access_token、禁止摘要改写及计数写入要求仍有表示。
- 实际发送与文件写入分开标为 net_send 和 fs_write，普通 return 没有被标 user_output；未从禁传约束补造 sanitizer。

复核边界：

- 当前被标注的是未修复第 0 轮图；后续提取失败不能算缺陷已消失。
- 计数按 selected_records，源文没有细化统计口径；该点仍是解释边界。
- 本轮只标注动作，尚未计算容器数据或隐私风险。

以上为助手复核，尚未获得用户确认；没有修改模型记录或将本报告回传模型。
