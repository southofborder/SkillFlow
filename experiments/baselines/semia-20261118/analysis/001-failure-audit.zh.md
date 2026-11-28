# Semia 001 首例失败机制核查

观察时间（UTC）：2026-11-18T09:40:06.164055+00:00。状态：**已取得完成回执**。

本核查只读取原始回答、候选、提示、回执及固定源码，用上游纯函数重新检查候选并写到独立 `analysis/001-audit/`，没有模型调用、Skill 执行或 active run 改动。全部重核记录保留候选 SHA-256。报告状态和统计可由 `audit_001.py` 再次只读更新。

适用范围是固定 `379bc25f / v0.1.3` 的 **Semia + controlled transport**，`gpt-6.1-sol / high / openai` 与 builtin 后端。本报告不把此配置的失败外推为所有模型下的 Semia 失败，也不冒称论文原配置复现。精确配置见 [runtime.json](../pilot/001/runtime.json)。

适配差异包括无工具文本调用、每请求独立工作目录、忽略用户/项目配置、记录公开事件，以及将单次timeout从上游默认600秒设为2700秒。builtin是官方支持的本地后端，但本机未完成Soufflé等价性验证。固定源码并不等于原封不动的论文、原生Codex或宿主插件路径复现；本轮结论仅适用于这些已列出的运行条件。

## 当前结果及成本

完成回执 exit_code=2，总耗时 5533.148 秒；终止消息：semia: synthesis produced no valid candidate after 5 iteration(s)。 合成/校验阶段没有得到有效候选；没有产生检测、报告或推荐结果。这里的检测结果是未运行，不能记成零告警或安全。 metadata保留 5 轮、accepted chain为空、selected_iteration=null，completed=false/stop_reason=null；这是原版在无有效候选时先抛异常、未走成功收尾路径的结果，不代表仍在运行。finished.error=null也不代表成功，应以exit_code和终止消息为准。

已观察 20 个原生请求目录，20 个候选，其中 0 个通过结构校验。已公开 input tokens=284065，output tokens=92198，合计 **376263**；reasoning tokens 是 output 的子计数，不重复相加。缺公开用量的已启动请求有 0 个，provider 内部未披露用量仍未知。

全部候选的错误累计为 {'SDL003': 86, 'SDL050': 20, 'SDL061': 20}；这是重复候选中的出现次数，不能当作独立漏洞数量。逐个参数错误按谓词统计：{'action_evidence_text expects 2 args, got 3': 7, 'call_evidence_text expects 2 args, got 3': 59, 'action_param_evidence_text expects 4 args, got 3': 11, 'action_trigger_evidence_text expects 3 args, got 2': 9}。原生内部 sampling retry 日志共 11 条，独立于上游provider重试及原生启动次数。

固定源码核验 360 个文件，变更 0 个；首例adapter未变=True。最终原版 synthesis_check 与最后候选离线重核的 errors、warnings、program_valid 均一致；原始check SHA-256为 `29559930edf20f849295c30631f00eadc89cf8c3ad5ea3b3669d140216c748f4`，副本与对照标记保存在analysis目录。

| 请求 | 阶段 | native exit | 耗时／秒 | 已知 input+output tokens |
| --- | --- | ---: | ---: | ---: |
| call-001 | synthesis | 0 | 181.056 | 16159 |
| call-002 | synthesis | 0 | 225.288 | 19182 |
| call-003 | synthesis | 0 | 441.774 | 18015 |
| call-004 | synthesis | 0 | 1092.23 | 19113 |
| call-005 | synthesis | 0 | 482.591 | 17699 |
| call-006 | synthesis | 0 | 278.854 | 34328 |
| call-007 | synthesis | 0 | 180.898 | 17996 |
| call-008 | synthesis | 0 | 252.498 | 18518 |
| call-009 | synthesis | 0 | 142.648 | 16720 |
| call-010 | synthesis | 0 | 191.375 | 18481 |
| call-011 | synthesis | 0 | 525.118 | 19075 |
| call-012 | synthesis | 0 | 188.135 | 18185 |
| call-013 | synthesis | 0 | 119.002 | 16540 |
| call-014 | synthesis | 0 | 202.374 | 18428 |
| call-015 | synthesis | 0 | 173.413 | 18182 |
| call-016 | synthesis | 0 | 155.92 | 17600 |
| call-017 | synthesis | 0 | 119.945 | 16311 |
| call-018 | synthesis | 0 | 174.486 | 18337 |
| call-019 | synthesis | 0 | 238.54 | 19098 |
| call-020 | synthesis | 0 | 166.61 | 18296 |

20个原生请求均正常退出并各产生1份候选，完整执行5轮×4次候选生成（15次结构重试）；本例未发生上游provider重新调用或2700秒原生超时。原生exit=0只表示文本请求完成，Semia总exit=2表示生成结果均未通过校验。

这些是工程首例成本，没有独立 gold，准确率与召回率为 `not_evaluated`。接收到模型回答和引文能够匹配，不等于候选结构有效或隐私结论正确。

表中 native 耗时包含CLI启动、传输/重连、模型处理和进程结束等阶段，不能全部解释为纯模型推理时间。旧SkillFlow参考运行不构成当前同版本、同预算的严格配对结果。

| 原始候选 | errors | warnings | 原版结构校验 | 错误代码 |
| --- | ---: | ---: | --- | --- |
| synthesis_attempt_0_0.dl | 8 | 12 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; action_evidence_text expects 2 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 5 |
| synthesis_attempt_0_1.dl | 12 | 17 | 拒绝 | SDL003×10, SDL050×1, SDL061×1; action_evidence_text expects 2 args, got 3 × 3; call_evidence_text expects 2 args, got 3 × 7 |
| synthesis_attempt_0_2.dl | 7 | 10 | 拒绝 | SDL003×5, SDL050×1, SDL061×1; call_evidence_text expects 2 args, got 3 × 5 |
| synthesis_attempt_0_3.dl | 10 | 14 | 拒绝 | SDL003×8, SDL050×1, SDL061×1; call_evidence_text expects 2 args, got 3 × 7; action_evidence_text expects 2 args, got 3 × 1 |
| synthesis_attempt_1_0.dl | 8 | 12 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; action_param_evidence_text expects 4 args, got 3 × 6 |
| synthesis_attempt_1_1.dl | 7 | 10 | 拒绝 | SDL003×5, SDL050×1, SDL061×1; action_evidence_text expects 2 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 4 |
| synthesis_attempt_1_2.dl | 8 | 12 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; action_evidence_text expects 2 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 5 |
| synthesis_attempt_1_3.dl | 3 | 2 | 拒绝 | SDL003×1, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1 |
| synthesis_attempt_2_0.dl | 8 | 12 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; action_param_evidence_text expects 4 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 4 |
| synthesis_attempt_2_1.dl | 10 | 15 | 拒绝 | SDL003×8, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; action_param_evidence_text expects 4 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 6 |
| synthesis_attempt_2_2.dl | 9 | 14 | 拒绝 | SDL003×7, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; action_param_evidence_text expects 4 args, got 3 × 1; call_evidence_text expects 2 args, got 3 × 5 |
| synthesis_attempt_2_3.dl | 8 | 12 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; call_evidence_text expects 2 args, got 3 × 5 |
| synthesis_attempt_3_0.dl | 3 | 2 | 拒绝 | SDL003×1, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1 |
| synthesis_attempt_3_1.dl | 4 | 4 | 拒绝 | SDL003×2, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; action_param_evidence_text expects 4 args, got 3 × 1 |
| synthesis_attempt_3_2.dl | 2 | 0 | 拒绝 | SDL050×1, SDL061×1;  |
| synthesis_attempt_3_3.dl | 3 | 2 | 拒绝 | SDL003×1, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1 |
| synthesis_attempt_4_0.dl | 2 | 0 | 拒绝 | SDL050×1, SDL061×1;  |
| synthesis_attempt_4_1.dl | 4 | 4 | 拒绝 | SDL003×2, SDL050×1, SDL061×1; action_trigger_evidence_text expects 3 args, got 2 × 1; action_param_evidence_text expects 4 args, got 3 × 1 |
| synthesis_attempt_4_2.dl | 2 | 0 | 拒绝 | SDL050×1, SDL061×1;  |
| synthesis_attempt_4_3.dl | 8 | 11 | 拒绝 | SDL003×6, SDL050×1, SDL061×1; call_evidence_text expects 2 args, got 3 × 6 |

## 已证实的失败链

首三份候选分别有 8/12/7 个 error：其中 6/10/5 个是 `action_evidence_text` 或 `call_evidence_text` 的三参数输出，而 schema 要求两个；其余均含 `v_access_token` 缺少 `value_secret_allowed_action`（SDL050）以及 `c_read_events` 同时标注 untrusted 与 secret（SDL061）。首轮 12 个 warning 对应六个错误 sidecar 未命中 core fact 和六个 core fact 缺 typed evidence，不是额外十二个独立语义遗漏。

第5份候选的六个 SDL003 则是**另一类**：`action_param_evidence_text` 期望4参、实给3参；不是 action/call evidence 的额外参数错误。SDL003只是统一错误代码，必须按具体谓词及期望/实际参数数目区分。分析者曾在中途消息中仅凭代码计数把第5份误概括为 entity evidence，已纠正；原始重核 JSON 从始至终保留了正确的逐条 message。

第15、17、19份候选（`synthesis_attempt_3_2.dl`、`synthesis_attempt_4_0.dl`、`synthesis_attempt_4_2.dl`）均已没有 SDL003，warnings=0、evidence_support_coverage=1.0，仍因 SDL050 与 SDL061 两项拒绝。这是原运行内直接观察到的证据：参数语法问题并非唯一阻断因素；它不是额外修正或消融实验，也不能当作语义内容已经全部正确。

1. **提示通则与 schema 特例矛盾。** 首请求 `prompt.txt` 的 Evidence Sidecar 通则要求参数镜像 core fact 并追加引文；但同一提示中的 action/call 示例只给实体 ID 与引文。固定 `schema.py` 的 `_ENTITY_EVIDENCE_ARITIES` 也明确 action/call 为2。模型在首三份回答反复采用了通则自然导出的3参写法。这能证明提示不一致与观察错误相符，尚不能证明它是所有失败的唯一原因。
2. **详细检查结果没有进入纠错输入。** `semia_core.pipeline.check_facts` 将详细 `CheckIssue` 写入 `synthesis_check.json`，但返回 payload 把 errors/warnings转为整数。`synthesis_loop._diagnostics` 虽能格式化列表，实际从 CLI adapter 收到的却是计数。因此后续请求的 Validation Feedback只有 errors/warnings数量和三个rate，没有错误代码、行号、谓词或消息。
3. **重试未带回被拒绝候选，跨轮还会清空反馈。** 合成循环用 `best_facts` 作为下一请求的当前候选；尚未接受任何候选时它保持 `None`。因此初轮结构重试并没有完整上一份被拒绝事实可供定点修正，又没有详细诊断，只能从源文重新生成。每个 iteration 起点又重置 `retry_feedback=None`；实际与首请求逐字节相同的prompt有 ['call-001', 'call-005', 'call-009', 'call-013', 'call-017']，SHA-256 为 `17a719050200c09fcf7c936e48c86968bf11913339816627b60ad31f6ec4921f`。这是原版循环内的重新生成，不应描述为逐轮累积反馈修复。这些是源码与请求证据，不等同于已做因果消融。
4. **secret/region 是另外两类候选建模协议问题。** 必须给secret绑定允许action，且同一call不能同时带两个显式untrusted/secret region标记，是原版checker明确规定。样本含用户提供的事件记录、access_token字段及禁止向任何接收者发送该字段的声明；现有候选未满足协议。不能把这两项直接归因于sidecar参数错误，更不能据此宣称源文不可表达或方法必然需要放宽权限。

`value_secret_allowed_action(src,a)` 的真实查询用途是 **action级使用范围**：`skill_dl_static_analysis.dl:314` 的一条 overreach 规则对未获准 action 中的秘密使用报警。它不是外发许可证；`label_implicit_egress_channels` 和另外的 egress overreach 分支（约275–307行）不读取这个 allowed-action 事实。因此依据源文允许的读取/处理给对应action绑定范围，并不会自动授权向接收者发送token。具体action划分和源引文是否足够，仍需对候选逐条核查；不应为了通过检查而无依据扩大范围。

SDL061检查的是**显式region标记集合的交集**，不是否认数据可同时具有不可信来源和秘密内容。Datalog分别可从`value(...,"secret")`建立secret源、从不可信读取/参数建立untrusted源；`call_in_untrusted_region`还可从输入依赖推导，不一定需要重复显式标记。schema也提供多个call及其input/output/控制关系，原则上允许源文支持的read/extract细分。故有源码支持的合法建模路径，不应写成“混合属性无法表达”；但不同编码是否保持全部标签尚未验证，例如`label_shadow_credentials`直接依赖显式secret region。这里只读了定义，没有修改候选、增加反例或证明修正效果。

提示 Hard Rule 6 同时要求：消费攻击者控制数据时设置 untrusted marker，读取凭据时设置 secret marker，读取敏感本地状态时设置 sensitive marker。它未说明混合场景的优先级、例外或如何用 value 标签保留属性并避免显式 marker 冲突。这与checker的互斥要求构成**潜在指导重叠**，是重复SDL061的诊断线索，尚非运行因果证明。对001而言，user-provided是否应视作attacker-controlled、读取access_token字段是否应标为凭据读取，都还有建模解释空间，不能宣布逻辑上必然不可满足。末尾outside-author提示位于`agent_call`与`net_write`说明段，限定的是送入agent的数据，不能泛化为所有本地`fs_read`必须标untrusted的规则。

上述反馈缺口首先是**本轮文本请求**的事实。原版Codex provider使用run目录作为工作目录且未禁工具，理论上模型可能自行读取旁边的check/facts；本轮受控适配禁工具并隔离每次请求目录。在反馈可见性上，它更接近上游HTTP provider只发送单条user prompt的信息边界（`llm_providers.py:289`），但不能由此声称传输或整体行为等同。没有测试原生工具访问能否补偿文本反馈缺口，因此不泛称所有原生Codex运行都绝对无法访问旧候选，也不把本轮失败只归于一个原因。

来源位置：固定源码 `packages/semia-core/src/semia_core/schema.py:38`、`pipeline.py:164`、`pipeline.py:660`、`checker.py:330`；`packages/semia-cli/src/semia_cli/synthesis_loop.py:123`、`synthesis_loop.py:468`。实际请求为 `pilot/001/transport/call-001/prompt.txt` 与后续纠错提示；原始 facts 及每份详细重核在本目录 JSON 中。

## 不能混淆的其他边界

前三次原生请求均正常退出并给出回答，所以其候选被拒绝的直接原因是结构检查，不是网络无回答。第4请求公开stderr出现内部 stream-disconnect retry，须独立计作同一原生请求内的传输事件，不能额外算成native start；其成本是否全部进入最终公开usage无法独立证明。每个请求也可能有“Code Mode unavailable”启动提示，它与源候选结构错误不同，现有公开事件未见实际命令或Skill执行。

`scan` 默认在确定性报告之后追加一个模型 recommendation，除非显式 `--no-recommendation`。原版5轮×4候选×3provider尝试给出60次合成上限，recommendation最多再3次，总上限63。首例runner冻结的全局上限是60；只有实际触及这个差异时才会影响结果，应据最终调用记录判定。recommendation必须单列，不能计作CGRS迭代或确定性检测本身。

最终只有 20 次原生启动，其中 recommendation=0；未达到60的冻结runner上限，因此60/63差异没有截断本例。

当前详细checks是按原始候选离线重核，不是新的语义生成，也没有手工修复候选。任何后续修正提示、反馈或输入过滤的变体，都应另存版本和结果；本轮原始失败应保留，不能用修订后的成绩覆盖。
