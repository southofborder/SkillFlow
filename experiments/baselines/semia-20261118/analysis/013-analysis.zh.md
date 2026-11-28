# SEMIA 013 只读跟进分析

观察时间：2026-11-18T11:13:11.356801+00:00。状态：**已终止**。

本分析读取 `comparison/013` 原始记录及固定源码，只向独立analysis目录写派生报告。没有模型调用、Skill执行、重跑scan、修改active artifacts或修改001已绑定审计。

本例为 `semia-379bc25f-controlled-complete-source-v1`，gpt-6.1-sol/high/openai、builtin检测器；5轮、每轮3次结构重试、2次provider错误重试，2700秒原生期限。源码/提示/checker/检测规则保持固定；完整源适配、无工具文本调用、独立请求目录及600→2700秒与原版差异均属于实验条件，不是原封不动论文或原生Codex路径复现。无独立gold，accuracy/F1/recall未评估。

## 运行与校验

完成回执：`{'exit_code': 2, 'error': None, 'elapsed_seconds': 5267.002, 'finished_at_utc': '2026-11-18T11:09:29.780497+00:00', 'native_starts': 20, 'cgrs_native_starts': 20, 'recommendation_native_starts': 0, 'calls_with_visible_usage': 20, 'source_and_input_unchanged': True, 'integrity_error': None, 'validation_receipts': 20, 'accuracy_evaluated': False, 'unexpected_tool_events': 0, 'recommendation_completed': False, 'note': 'CLI may catch synthesis errors; inspect console-stderr and exit_code. Recommendation failure is nonfatal upstream.'}`。

Semia管线exit=2，耗时5267.002秒；原生exit分布{'0': 20}。检测/报告/推荐状态分别为not_run/not_run/not_run。root提供的外层PowerShell会话回收exit=1，与Semia管线exit分别记录；回执绑定finished SHA=True。新鲜PID观察：记录21条，all_recorded_absent=False，直接子进程3、额外可观察后代4，观察晚于finished=True。

观察到 20 次原生启动、20 个候选文件、20 份validation快照；经提交身份和完整check内容绑定后有效validation 0 份，按提交facts哈希去重为 0 个有效候选（重复检查不重复计数）。直接读取所有stdout的turn.completed事件所得已知input小计=270665、output小计=121146，合计已知 **391811 tokens**。全请求精确公开合计=391811；未能获得完整input/output用量的已启动请求 0 个。逐字段缺失保留unknown，未填零；cached与reasoning是子计数，不再次相加，provider内部未披露用量仍未知。内部sampling retry日志 11 条，独立于native starts和上游provider retries。CGRS和recommendation成本分别保留在机器记录public_usage_by_phase中。

| 请求 | 阶段 | native exit | 秒 | input+output tokens |
| --- | --- | ---: | ---: | ---: |
| call-001 | cgrs | 0 | 454.931 | 18059 |
| call-002 | cgrs | 0 | 218.668 | 19722 |
| call-003 | cgrs | 0 | 266.919 | 21662 |
| call-004 | cgrs | 0 | 204.895 | 20267 |
| call-005 | cgrs | 0 | 145.773 | 18388 |
| call-006 | cgrs | 0 | 179.075 | 19933 |
| call-007 | cgrs | 0 | 422.534 | 20315 |
| call-008 | cgrs | 0 | 220.443 | 21284 |
| call-009 | cgrs | 0 | 458.747 | 18939 |
| call-010 | cgrs | 0 | 163.533 | 19233 |
| call-011 | cgrs | 0 | 156.377 | 19020 |
| call-012 | cgrs | 0 | 193.18 | 20081 |
| call-013 | cgrs | 0 | 387.783 | 18158 |
| call-014 | cgrs | 0 | 517.987 | 20585 |
| call-015 | cgrs | 0 | 192.248 | 20516 |
| call-016 | cgrs | 0 | 149.213 | 19026 |
| call-017 | cgrs | 0 | 113.859 | 17411 |
| call-018 | cgrs | 0 | 173.304 | 19716 |
| call-019 | cgrs | 0 | 489.15 | 20315 |
| call-020 | cgrs | 0 | 157.279 | 19181 |

| validation | 对应提交候选 | program_valid | errors | warnings | 代码 |
| --- | --- | --- | ---: | ---: | --- |
| check-001 | synthesis_attempt_0_0.dl | False | 3 | 2 | {'SDL003': 1, 'SDL061': 2} |
| check-002 | synthesis_attempt_0_1.dl | False | 2 | 0 | {'SDL061': 2} |
| check-003 | synthesis_attempt_0_2.dl | False | 15 | 24 | {'SDL003': 12, 'SDL061': 3} |
| check-004 | synthesis_attempt_0_3.dl | False | 2 | 0 | {'SDL061': 2} |
| check-005 | synthesis_attempt_1_0.dl | False | 15 | 26 | {'SDL003': 13, 'SDL061': 2} |
| check-006 | synthesis_attempt_1_1.dl | False | 4 | 4 | {'SDL003': 2, 'SDL061': 2} |
| check-007 | synthesis_attempt_1_2.dl | False | 16 | 28 | {'SDL003': 14, 'SDL061': 2} |
| check-008 | synthesis_attempt_1_3.dl | False | 17 | 28 | {'SDL003': 14, 'SDL061': 3} |
| check-009 | synthesis_attempt_2_0.dl | False | 15 | 26 | {'SDL003': 13, 'SDL061': 2} |
| check-010 | synthesis_attempt_2_1.dl | False | 11 | 18 | {'SDL003': 9, 'SDL061': 2} |
| check-011 | synthesis_attempt_2_2.dl | False | 15 | 26 | {'SDL003': 13, 'SDL061': 2} |
| check-012 | synthesis_attempt_2_3.dl | False | 3 | 2 | {'SDL003': 1, 'SDL061': 2} |
| check-013 | synthesis_attempt_3_0.dl | False | 4 | 4 | {'SDL003': 2, 'SDL061': 2} |
| check-014 | synthesis_attempt_3_1.dl | False | 4 | 2 | {'SDL003': 1, 'SDL061': 3} |
| check-015 | synthesis_attempt_3_2.dl | False | 3 | 2 | {'SDL003': 1, 'SDL061': 2} |
| check-016 | synthesis_attempt_3_3.dl | False | 3 | 2 | {'SDL003': 1, 'SDL061': 2} |
| check-017 | synthesis_attempt_4_0.dl | False | 4 | 2 | {'SDL003': 1, 'SDL050': 1, 'SDL061': 2} |
| check-018 | synthesis_attempt_4_1.dl | False | 2 | 0 | {'SDL061': 2} |
| check-019 | synthesis_attempt_4_2.dl | False | 17 | 28 | {'SDL003': 14, 'SDL061': 3} |
| check-020 | synthesis_attempt_4_3.dl | False | 15 | 26 | {'SDL003': 13, 'SDL061': 2} |

完整逐条诊断、提交facts SHA及对应候选保存在 `013-analysis.json`。必须同时满足实际submitted SHA=invocation SHA=return-payload SHA、复制facts一致、返回字段一致，并用固定源码纯函数重核完整check及alignment一致，才把validation计为可用。未绑定/异常/缺失的有效性和计数保持未知；未绑定validation数=0。未调用check_facts、scan或模型，也不修改原始候选。SDL003是参数schema错误；其他SDL项须按原消息区分模型协议；检测label、原生传输错误分别记录。

没有arity错误但仍被拒绝的validation：['check-002', 'check-004', 'check-018']。与初次prompt逐字节相同的请求：['call-001', 'call-005', 'call-009', 'call-013', 'call-017']。已完成原生耗时超过上游默认600秒的请求：[]；这里只记录观测，不模拟另一超时策略的反事实结果。

绑定候选中的诊断累计为{'SDL003': 125, 'SDL061': 44, 'SDL050': 1}；具体arity消息累计为{'action_trigger_evidence_text expects 3 args, got 2': 12, 'action_evidence_text expects 2 args, got 3': 6, 'call_evidence_text expects 2 args, got 3': 105, 'action_param_evidence_text expects 4 args, got 3': 2}。这是多份候选中的重复诊断次数，不是独立漏洞数量。

源码核验 360 文件，变更 0；输入变更 0 个文件。独立manifest/精确清单/输入大小/CLI/runner/helper核验全部通过=True。每次实际prompt的完整源唯一性、receipt SHA和实际argv均独立核对，不能仅依赖runner自己的source_payload_verified标记。

各阶段状态：{'pipeline': 'failed', 'pipeline_exit_code': 2, 'detector': 'not_run', 'report': 'not_run', 'recommendation': 'not_run', 'recommendation_failure_is_nonfatal_upstream': True, 'recommendation_evidence_conflict': False, 'recommendation_content_review': 'not_reached', 'recommendation_is_independent_model_opinion': True}。实际读取report.md、recommendation.md及推荐原始回答；推荐是可非致命失败的独立模型阶段，pipeline exit=0不等于推荐成功。没有检测artifact不能记成零发现或安全；已有推荐内容也须逐条语义审阅，不能冒充gold。终态计数对账={'native_starts': {'observed': 20, 'recorded': 20, 'match': True}, 'cgrs_native_starts': {'observed': 20, 'recorded': 20, 'match': True}, 'recommendation_native_starts': {'observed': 0, 'recorded': 0, 'match': True}, 'calls_with_visible_usage': {'observed': 20, 'recorded': 20, 'match': True}, 'validation_receipts': {'observed': 20, 'recorded': 20, 'match': True}}。进程观察=observed，仅在终态新查询记录controller/native PID及可观察直接子进程/后代，绑定finished SHA及观察时间，不导入旧PID快照。timeout清理记录数=0。



终态PID身份复核：21条原运行进程记录均已有退出证据：19个数值PID不存在，7480和23304已分别被终态之后11:13:09、11:13:10新建的pwsh/powershell进程复用。观察到的4个额外进程均在这些新父进程创建之后产生，属于新建进程树；没有观察到原运行存活的直接子进程或可追踪后代。原观察保留all_recorded_absent=false及no_observable_descendants=false，表示数值PID/当前父子关系仍存在，不能误读为原运行仍存活，也不能改写成所有数值PID均不存在。此解释只使用同一份新鲜终态观察，没有第二次进程查询。详见机器记录process_identity_review及audit-fixes/013-final-r5-20261118/process-identity-review.json。

## 与013源约束对应

源文要求：FAST_KEY决定首选工具是否可调用；fast.fetch仅首次transient失败可再试一次；非transient或重试失败转archive，archive至多一次且只接收source_id；任一成功后返回原body且停止取数；archive失败返回其error；FAST_KEY不可送archive或诊断；每条终止路径先追加status.txt。这些是源约束清单，不是人工gold标注。

20份候选全部被拒绝，原版5轮×4候选预算完整走完，终止消息为synthesis produced no valid candidate after 5 iteration(s)。每份候选都含FAST_KEY参与的fast首次/重试调用同时带显式untrusted与secret marker；拆出fast子action的第3、8、14、19份还各多一个内部call冲突，共44项SDL061。这是候选未满足原版建模协议，不是检测器发现44个漏洞，更不是执行Skill时实际泄漏。

第2、4、18份完全没有arity错误、没有warnings，evidence_match_rate与evidence_support_coverage均1.0，仍仅因两个SDL061拒绝，说明格式问题不是唯一阻断。其余17份合计125个SDL003，分别包含action/call evidence多一参、action_trigger/action_param evidence少一参，应按具体谓词区分。提示Evidence Sidecar通则要求镜像core参数，但action/call实体特例只接受ID加引文；这是已确认的不一致。Hard Rule 6对攻击者输入与凭据访问分别要求region marker，却没有说明混合场景优先级或用value标签保留属性的方式，是重复SDL061的诊断线索；不能由此断言源文逻辑必然不可表达。

第17份另有唯一一次SDL050：secret value 'fast_key'没有value_secret_allowed_action。其他19份未出现此项，因此这是一次候选遗漏，不能将禁止FAST_KEY送archive/诊断解释成合法fast使用也无法绑定action。allowed_action是action使用范围，不是外发许可；schema和Datalog可分别表达secret value来源、untrusted依赖和显式region，如何保持全部标签需进一步语义验证，当前没有修改候选或证明改善效果。

首两份被拒候选已列出presence/transient/nontransient分支、一次fast重试、archive和四种终止前append→return链，archive直接call_input只有source_id。这些仅是未接受表示的特征，不能记作已接受覆盖或完整工作流正确性。原版反馈返回errors/warnings整数和三个rate，未把完整诊断或上一份被拒facts纳入文本请求；每轮起点又清空反馈，五个轮首prompt相同。这与反复重新生成和错误回归一致，但没有因果消融，不能将失败单独归咎于提示、模型或任何一个机制。

全部原生文本请求正常返回与Semia结构失败必须分开：网络内部重连影响可观察成本，但本例没有因为无回答而缺少候选。未得到有效候选，确定性检测、报告和推荐均未运行；没有可审查的检测/推荐内容，不能把缺失结果当作零告警、安全或F1=0。本结论限于固定源码、同模型、完整源、无工具文本调用及2700秒deadline条件；未验证原生Codex读取邻近facts/check是否可补偿反馈缺口，也未做修正、反例测试、Skill执行或模型消融。

SDL的风险label与完整工作流正确性是不同目标。控制边和条件value存在，并不自动证明重试次数、错误分类、原body返回、每终止路径日志义务均已语义验证；需逐条对照事实和检测规则。recommendation是单独模型阶段，不计入确定性检测或CGRS候选成功数。

本报告、机器记录与终态进程观察已完成冻结；本轮不再更新。
