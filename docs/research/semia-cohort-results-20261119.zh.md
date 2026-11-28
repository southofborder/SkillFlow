# Semia 四样本工程对照：2026-11-19 结果

**四例均已终止：010完成检测；001、013、GA4因未生成合法表示而停止，检测未运行。** 首例分析完成后才放行其余三个样本，原始失败和回答全部保留。相关项目情况见已完成的 [11月18日定向更新](related-work-update-20261118.zh.md) 与 [来源记录](related-work-update-20261118.sources.json)。

本轮是**同模型请求配置、同原始 source 的工程对照**：`gpt-6.1-sol / high / openai`，固定 Semia `379bc25fe99833eb185efe56a38fe15f0235799c`，使用 builtin 后端。四包在看到 Semia 结果前选定，共21个源文件：001为1个、010为3个、013为1个、GA4为16个。逐文件身份和历史来源见[输入清单](../../experiments/baselines/semia-20261118/input-manifest.json)及[比较协议](semia-comparison-protocol-20261118.zh.md)。这些是开发用例，不是随机或代表性评测集。

| 样本 | native starts（CGRS＋推荐） | 合成候选 | 有效候选 | 已知公开 input＋output tokens | 端到端秒 | 检测／推荐状态 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 001 | 20（20＋0） | 20 | 0 | 376,263 | 5,533.148 | 管线exit 2；检测、报告、推荐未运行 |
| 010 | 4（3＋1） | 3 | 1 | 61,957 | 379.664 | 管线exit 0；builtin完成、0告警；推荐完成 |
| 013 | 20（20＋0） | 20 | 0 | 391,811 | 5,267.002 | 管线exit 2；检测、报告、推荐未运行 |
| GA4 | 21（21＋0） | 20 | 0 | 2,010,100，另1次请求未知 | 24,869.019 | 管线exit 2；检测、报告、推荐未运行 |

四例合计65次原生启动，其中64次CGRS、1次推荐；实际生成63份候选，1份通过校验。已知公开input＋output合计**2,840,131 tokens**，64次有完成用量记录，GA4超时请求的公开用量及provider内部未披露用量仍未知，完整总成本不可得。只有010进入检测，不能把另外三例的缺失告警记成阴性。

四例终态分析均已完成，原始失败、回答与选中结果分别保留。GA4的677个封存文件及CLI哈希和大小通过[独立只读复核](../../experiments/baselines/semia-20261118/analysis/ga4-terminal-independent-review.json)；进程结论复用同一终态快照，不通过重复查询消除PID复用记录。全批次身份、逐例结案与已知用量绑定在[root批次结案](../../experiments/baselines/semia-20261118/analysis/cohort-closeout.json)。

候选数只计实际合成候选；010的第4份validation是选中候选复核，不是第4个候选。推荐是独立模型阶段，不计入CGRS。公开token不重复加上cached或reasoning子计数；provider内部未披露用量仍未知。耗时包含传输、重连和进程等开销，不是纯模型推理时间。**未运行不能记作零告警；零告警也不能记作安全。** 无独立gold，准确率、召回率和F1均未评估。

Semia保留5个iteration、每轮3次结构重试和2次provider错误重试，并可提前停止；5个iteration不等于5次调用。001冻结runner的全局上限60与后续包含推荐的63不同，但首例只用20次，没有触及这一差异。

三例的冻结依据分别为：[001报告](../../experiments/baselines/semia-20261118/analysis/001-failure-audit.zh.md)与[closeout](../../experiments/baselines/semia-20261118/analysis/001-closeout.json)、[010报告](../../experiments/baselines/semia-20261118/analysis/010-analysis.zh.md)与[closeout](../../experiments/baselines/semia-20261118/analysis/010-closeout.json)、[013报告](../../experiments/baselines/semia-20261118/analysis/013-analysis.zh.md)与[冻结清单](../../experiments/baselines/semia-20261118/analysis/013-audit-freeze.json)。原始回答、被拒候选和失败均保留，未用修订后结果覆盖。

**001暴露了前端协议与反馈问题。** 20次原生文本请求均正常返回，但没有候选通过校验。Evidence Sidecar通则要求镜像core参数，action/call实体特例却只接受ID加引文；候选反复出现参数数目错误。原版详细诊断写到了文件，实际纠错文本只得到错误／警告数量和比率；尚无有效候选时，上一份被拒facts也未带回，跨iteration还会重置反馈。五个轮首prompt相同。这些是源码和实际请求共同支持的机制，尚未通过因果消融证明它们分别贡献多少失败。

001还持续缺少secret的allowed-action事实，并把同一读取call标成untrusted和secret。`value_secret_allowed_action`是action使用范围，不是外发许可证；SDL061约束显式region标记，不等于数据不能同时具有不可信来源和秘密属性。因此只能认定候选未满足协议，不能据此断言源文不可表达或必须放宽权限。

**010跑通了工程链路，但没有验证完整源语义。** 前两候选分别有3、7项参数错误，第三候选通过并触发分数ceiling。0.930208是证据匹配／支持／参考覆盖组合分，不是准确率；参考token覆盖65.104%也不代表只发送了65.104%的源文，三个完整文件均已进入实际prompt。

选中core主要保留可能的输入和调用关系。`from_date`、`limit`的存在／省略原句虽被sidecar引用，ID中的`_if_present`并不是检测规则解释的守卫；原值直传、精确调用次数、禁止`index.delete`及原样返回等约束也没有得到完整形式验证。builtin的11个label关系为空，另外2个关系是可达性辅助结果，不能称为13类安全检查全部通过。独立推荐给出“Recommend with caution”；关于count.txt覆盖方式和缺limit时服务默认值的提醒是条件性建议，不是已证实漏洞。不能把该例的结构有效或0告警当作方法准确性优势。

**013重复出现region冲突。** 20份候选均被拒绝，累计125项SDL003、44项SDL061；这些是重复候选的诊断次数，不是漏洞数。第2、4、18份已无arity错误和warnings、证据匹配／支持率均为1.0，仍因fast首次／重试call同时标注untrusted和secret而失败，说明格式错误不是唯一阻断。第17份另有一次SDL050：`fast_key`遗漏allowed-action；其他19份没有此项。没有有效候选，故本例不能评价检测结果是否对应重试、fallback、秘密使用或终止前日志义务。

**GA4在5轮、20份候选后结束，仍无合法表示。** 21次原生请求中有一次传输超时；20次完成事件独立合计input 1,297,907、output 712,193，即2,010,100公开tokens。总耗时24,869.019秒（约6小时54分29秒），最后一份候选仍有69项校验错误，最终metadata的selected iteration为null。详见[GA4最终原因分析](../../experiments/baselines/semia-20261118/analysis/ga4-final-assessment.zh.md)、[逐字段终态审计](../../experiments/baselines/semia-20261118/analysis/ga4-analysis.zh.md)和[冻结清单](../../experiments/baselines/semia-20261118/analysis/ga4-freeze.json)。

20份候选累计2,375条错误记录，其中SDL003参数数量错误2,261条、SDL051敏感值缺allowed-action 37条、SDL050秘密值缺allowed-action 29条、SDL060显式untrusted／sensitive region冲突28条、SDL032 action没有root call 17条、SDL030重复fact 3条。这是重复候选的诊断计数，不是独立漏洞数。6份候选没有参数数量错误仍被拒；第5份仅剩3项root-call错误，第11份仅剩1项region冲突，之后又出现大量arity错误，不能称稳定收敛。修复请求只有数量和三项覆盖率，未携带具体诊断或前一被拒候选；新一轮又回到相同初始prompt。直接阻断选择的是合法性校验，低覆盖分数尚不能认定为本次失败的决定原因。

[call017回执](../../experiments/baselines/semia-20261118/comparison/ga4/transport/call-017/request.json)记录2700.142秒超时、退出码1，stdout没有完成事件、响应文件为空。7条内部sampling retry日志包括5条WebSocket重试及回落HTTP后的2条重试；内部日志不等于额外native启动次数，也无法据此核算费用。call018以相同prompt自动重试并生成第17份候选，因此最终是21次原生调用、20份候选。网络问题明确增加了等待与未知成本，不能解释其余20份候选均未通过校验。root已经回收原启动会话，PowerShell wrapper退出码1与Semia管线退出码2分别记录。

比较边界必须保留：本轮没有以同一当前SkillFlow版本做双方全新重跑；历史SkillFlow的版本、继承、CLI和预算不同，仅作同源背景，不形成方法胜负或同预算结论。Semia原始prompt、schema、checker、选择和检测机制保留，但运行采用受控无工具文本调用、独立请求目录、忽略额外配置、2700秒deadline（上游默认600秒）。010／013／GA4使用单独命名的完整源适配；GA4补入默认排除的package.json和package-lock.json，参考单元从623变为3155，覆盖分母随之变化。builtin也未在本机证明与论文Soufflé结果等价。这是明确适配条件下的工程复刻，不是论文原配置或原生Codex宿主路径的原封不动复现。

相关工作更新已把Semia、SCS列为直接结构方法对照，并指出MalSkills、AgentSecGraph和RuntimeTickets在跨文件分析、边界防护及任务条件方面的竞争。因此不能仅凭更细的表示、更多合同或静态告警数主张贡献；需要共同性质、源文忠实度和独立标注支持。

**后续仅为proposal，未经新用户指令不执行。** 先离线评估错误定位反馈是否完整携带谓词、行号、具体消息和被拒候选，并核查提示arity与schema的一致性；保持严格校验，结合源约束检查secret／region建模，不为提高通过率无依据放宽范围。若获授权，再独立命名修复变体，固定源包、模型、输入可见性和预算，与保留的原始变体做对照及消融；另行规划当前SkillFlow的正式配对版本、共同威胁假设和盲标gold。结构接受率改善必须与语义正确性分开评估。本稿不授权实现修复、增补模型请求或重跑历史实验。
