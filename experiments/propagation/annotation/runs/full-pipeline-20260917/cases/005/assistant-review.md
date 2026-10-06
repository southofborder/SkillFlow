# 005 本次全流程助手复核

反馈状态：`extraction_error`；标注状态：`complete`。

完整阅读 SKILL.md、第 0 轮有效图、9 个有效核对项和全部 11 条 profile。第 1 轮重新提取 DNS 失败，当前标注实际使用本次第 0 轮图，未读取或借用历史基线图。

1. **unrepaired_graph_omission**（ir_001, ir_005）：第 0 轮遗漏完整输入记录字段模式，record_id 不在图中，access_token 仅在禁传约束中，不能等同声明其存在于输入记录。核对器指出这一点合理；因为第 1 轮提取失败，当前被标注的第 0 轮图仍有该缺口，不能视为已经修复。

依据：源文第 1 条完整列出七个字段；ir_001 仅输出 event_records，metadata/constraints 均无字段集合。；ir_005 只输出 recipient、summary、value、urgent、opted_out 五个字段。；feedback.rounds[0].audit finding_4=omitted；rounds[1]=extraction_error；selection.revision=0。

2. **missing_role**（ir_001）：读取动作已经依据 EM02 标 model_observe，却仅给 source，漏掉本轮 sink 定义覆盖的模型可见边界角色。

依据：ir_001 roles=[source]；effects=[fs_read,model_observe]；理由明确工具内容默认进入模型上下文。

3. **actor_evidence_insufficient**（ir_002, ir_003, ir_004, ir_005, ir_006, ir_007, ir_008, ir_010, ir_011）：迭代、字段提取和条件判断被直接标为本地 agent_runtime，dispatch 直接标 llm。源文与图仅描述业务行为，没有指定执行分工；EM03/EM04 不能把可能或条件适用变成确定归属。应在 actor/模型处理边界保留未知，而不是给出全部确定标签。

依据：ir_005 理由称“本地字段提取”，证据只引用 extract_event_record_fields。；ir_007 理由称“本地条件判定”，证据只引用 check_notification_eligibility。；dispatch 的 llm 依据为 EM03 的“LLM 调度”，未有具体调度执行事实。

保留的正确表现：

- 第 9 条明确“历史示例（当前流程不执行）”，本次图没有 count.txt 写入，标注也没有 fs_write；核对器正确将它视为非当前执行内容。
- 显式逐记录循环、选中/未选中控制分支、recipient 与 summary 身份绑定保留，发送只走选中路径。
- 禁传声明没有被提升为真实脱敏动作；return 未被标 user_output。

复核边界：

- 当前图的已知遗漏未修复，annotation.complete 仅表示 11 条 profile 的记录合法完整。
- 未传播数据，不能依据缺字段模式或 model_observe 断言实际已经发生敏感数据泄露。

以上为助手复核，尚未获得用户确认；没有修改模型记录或将本报告回传模型。
