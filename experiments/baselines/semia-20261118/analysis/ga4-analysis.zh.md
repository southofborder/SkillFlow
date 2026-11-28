# GA4 完整源变体：只读观察与结果分析

观察时点：2026-11-19T00:44:21.477574+08:00（Asia/Shanghai）；pipeline状态：**failed**。终态以finished.json为准；没有终态回执时不将本稿称为最终结论。推荐层结果单独判断。

当前已观察 21 次native starts，公开input+output合计 2010100 tokens，1 次尚无用量回执。CGRS与recommendation分别为 21／0 次；cached和reasoning子计数不重复累加。

## 输入与传输

完整源变体包含 16/16 文件；相较原版14文件，补入scripts/package.json和scripts/package-lock.json。当前prepare共 3155 语义单元（原版623），prepared为 155964 字节。两个版本的覆盖率分母不同，不能把分值变化直接理解为语义质量变化。

每个实际请求均独立检查唯一完整的source围栏正文。输入进入prompt、请求成功返回、候选通过校验、产生正确安全判断是不同层次。大输入传输错误仅依据native返回/超时与公开事件判断；模型目录刷新超时等启动日志单独记录，不冒充主请求失败。

| 请求 | phase | prompt字节 | 完整正文 | returncode | 秒 |
|---|---|---:|---|---:|---:|
| call-001 | cgrs | 164013 | True | 0 | 1024.199 |
| call-002 | cgrs | 164515 | True | 0 | 1088.088 |
| call-003 | cgrs | 164515 | True | 0 | 1767.842 |
| call-004 | cgrs | 164513 | True | 0 | 801.218 |
| call-005 | cgrs | 164013 | True | 0 | 940.414 |
| call-006 | cgrs | 164496 | True | 0 | 965.505 |
| call-007 | cgrs | 164513 | True | 0 | 1876.113 |
| call-008 | cgrs | 164515 | True | 0 | 1049.752 |
| call-009 | cgrs | 164013 | True | 0 | 818.028 |
| call-010 | cgrs | 164496 | True | 0 | 761.203 |
| call-011 | cgrs | 164497 | True | 0 | 1038.351 |
| call-012 | cgrs | 164496 | True | 0 | 947.179 |
| call-013 | cgrs | 164013 | True | 0 | 882.777 |
| call-014 | cgrs | 164513 | True | 0 | 1003.921 |
| call-015 | cgrs | 164515 | True | 0 | 1400.822 |
| call-016 | cgrs | 164496 | True | 0 | 1318.155 |
| call-017 | cgrs | 164013 | True | 1 | 2700.142 |
| call-018 | cgrs | 164013 | True | 0 | 1045.941 |
| call-019 | cgrs | 164514 | True | 0 | 873.318 |
| call-020 | cgrs | 164496 | True | 0 | 1282.051 |
| call-021 | cgrs | 164515 | True | 0 | 953.933 |

## 独立证据对账

公开用量从每份stdout的全部turn.completed事件独立求和，并逐字段对照request.usage与public_turn_usages；缺字段保留unknown。已知input/output的部分和可报告，未知部分不填零；cached/reasoning子计数不重复计费。原生失败、预启动失败与内部采样重试分别记录，不能用native次数减候选数推算外层重试。

| 用量字段 | 已知和 | 缺完整字段的native calls | completion缺字段数 |
|---|---:|---:|---:|
| input_tokens | 1297907 | 1 | 0 |
| output_tokens | 712193 | 1 | 0 |
| cached_input_tokens | 522240 | 1 | 0 |
| cache_write_input_tokens | 0 | 1 | 0 |
| reasoning_output_tokens | 23168 | 1 | 0 |

manifest对runtime及首例固定身份、精确inventory、哈希/大小联合核验：True。source共360文件，输入共16文件；source manifest未记录大小，独立使用同一SHA绑定官方ZIP的file_size核对。运行生成的pycache排除项逐路径记录。每份实际argv、prepare回执SHA、完整source正文也独立对照。

原始candidate attempt文件20份／唯一SHA 20；通过且身份绑定的候选0份，候选校验未知0份。validation共20次，其中可用20次、独立识别最终selected facts复核0次、同SHA歧义校验0次。最终复核不会增加候选数。

候选可先写入文件，再因patch_unmatched跳过checker。因此不按同SHA贪心配对：实际invocation候选路径或唯一SHA才归属；同SHA且无法唯一定位时保持unknown。最终复核另用selected SHA、final facts路径及completed metadata写入早于invocation的顺序证据识别；文件时序不可靠时不强判。阶段用量另记录无completion的native调用和各字段缺失调用数，事件字段齐全不冒充整个阶段用量齐全。

每份validation要求实际submitted-facts SHA、invocation SHA、return-payload SHA、复制facts SHA一致，并核对returned无异常、check/payload合法性与错误/警告数；检查JSON自身SHA一并保存。不满足时program_valid及错误数保持unknown，陈旧共享文件不计有效。终态native/阶段/可见用量计数再与finished回执逐项对照。

## 候选校验与选择

| 检查 | 原版program_valid | errors | warnings | 引文匹配 | 事实支持 | 源单元覆盖 |
|---|---|---:|---:|---:|---:|---:|
| check-001 | False | 199 | 382 | 0.9765258215962441 | 0.7001569858712716 | 0.12024873688301593 |
| check-002 | False | 228 | 440 | 0.9867149758454107 | 0.7342995169082126 | 0.12942090944422852 |
| check-003 | False | 242 | 468 | 0.980498374864572 | 0.745928338762215 | 0.14154683249125535 |
| check-004 | False | 99 | 186 | 0.9757085020242915 | 0.8727770177838577 | 0.13618344345122424 |
| check-005 | False | 3 | 0 | 0.9814126394052045 | 1.0 | 0.13019821220365332 |
| check-006 | False | 81 | 146 | 0.9766206163655685 | 0.922422954303932 | 0.13159735717061796 |
| check-007 | False | 267 | 516 | 0.9831791421362489 | 0.7822784810126582 | 0.15709288767975127 |
| check-008 | False | 217 | 420 | 0.9828801611278952 | 0.7885196374622356 | 0.14520015546055187 |
| check-009 | False | 5 | 0 | 0.9809160305343512 | 1.0 | 0.12670034978624173 |
| check-010 | False | 11 | 0 | 0.9791666666666666 | 1.0 | 0.10967741935483871 |
| check-011 | False | 1 | 0 | 0.9893390191897654 | 1.0 | 0.14527788573649436 |
| check-012 | False | 29 | 50 | 0.9789227166276346 | 0.9707259953161592 | 0.14263505635445006 |
| check-013 | False | 208 | 401 | 0.9801980198019802 | 0.75093399750934 | 0.12631169840652934 |
| check-014 | False | 229 | 452 | 0.9830148619957537 | 0.7600849256900213 | 0.15180722891566265 |
| check-015 | False | 6 | 0 | 0.9857328145265889 | 1.0 | 0.14115818111154294 |
| check-016 | False | 52 | 98 | 0.9863013698630136 | 0.9310829817158931 | 0.11721725612125923 |
| check-017 | False | 172 | 342 | 0.980719794344473 | 0.7799227799227799 | 0.12024873688301593 |
| check-018 | False | 9 | 0 | 0.9785969084423306 | 1.0 | 0.12258064516129032 |
| check-019 | False | 248 | 488 | 0.9823100936524454 | 0.7460978147762747 | 0.14364554994170228 |
| check-020 | False | 69 | 123 | 0.9817007534983854 | 0.9380434782608695 | 0.13952584531675088 |

逐份sidecar还按唯一匹配单位重算reference覆盖率，并分开原14文件共享子集与新增子集；逐文件单位数、词项权重及SHA见JSON。它们是已保存引文的匹配统计，不代表代码操作/隐私语义覆盖，也不是模型计费tokens。
- check-001：匹配词项权重 1547 = 原共享子集 1509 + 新增子集 38；分母 12865，重算覆盖率与原sidecar一致：True。
- check-002：匹配词项权重 1665 = 原共享子集 1621 + 新增子集 44；分母 12865，重算覆盖率与原sidecar一致：True。
- check-003：匹配词项权重 1821 = 原共享子集 1775 + 新增子集 46；分母 12865，重算覆盖率与原sidecar一致：True。
- check-004：匹配词项权重 1752 = 原共享子集 1705 + 新增子集 47；分母 12865，重算覆盖率与原sidecar一致：True。
- check-005：匹配词项权重 1675 = 原共享子集 1636 + 新增子集 39；分母 12865，重算覆盖率与原sidecar一致：True。
- check-006：匹配词项权重 1693 = 原共享子集 1648 + 新增子集 45；分母 12865，重算覆盖率与原sidecar一致：True。
- check-007：匹配词项权重 2021 = 原共享子集 1963 + 新增子集 58；分母 12865，重算覆盖率与原sidecar一致：True。
- check-008：匹配词项权重 1868 = 原共享子集 1812 + 新增子集 56；分母 12865，重算覆盖率与原sidecar一致：True。
- check-009：匹配词项权重 1630 = 原共享子集 1593 + 新增子集 37；分母 12865，重算覆盖率与原sidecar一致：True。
- check-010：匹配词项权重 1411 = 原共享子集 1368 + 新增子集 43；分母 12865，重算覆盖率与原sidecar一致：True。
- check-011：匹配词项权重 1869 = 原共享子集 1798 + 新增子集 71；分母 12865，重算覆盖率与原sidecar一致：True。
- check-012：匹配词项权重 1835 = 原共享子集 1786 + 新增子集 49；分母 12865，重算覆盖率与原sidecar一致：True。
- check-013：匹配词项权重 1625 = 原共享子集 1587 + 新增子集 38；分母 12865，重算覆盖率与原sidecar一致：True。
- check-014：匹配词项权重 1953 = 原共享子集 1894 + 新增子集 59；分母 12865，重算覆盖率与原sidecar一致：True。
- check-015：匹配词项权重 1816 = 原共享子集 1779 + 新增子集 37；分母 12865，重算覆盖率与原sidecar一致：True。
- check-016：匹配词项权重 1508 = 原共享子集 1460 + 新增子集 48；分母 12865，重算覆盖率与原sidecar一致：True。
- check-017：匹配词项权重 1547 = 原共享子集 1505 + 新增子集 42；分母 12865，重算覆盖率与原sidecar一致：True。
- check-018：匹配词项权重 1577 = 原共享子集 1530 + 新增子集 47；分母 12865，重算覆盖率与原sidecar一致：True。
- check-019：匹配词项权重 1848 = 原共享子集 1804 + 新增子集 44；分母 12865，重算覆盖率与原sidecar一致：True。
- check-020：匹配词项权重 1795 = 原共享子集 1754 + 新增子集 41；分母 12865，重算覆盖率与原sidecar一致：True。

### 实际重试反馈

下表只依据保存的实际payload。分析者可读取详细checker文件，不等于模型获得这些详情；每次原生调用也不是延续上次会话。完整反馈文本及prompt/candidate SHA绑定在机器报告中。

| 请求 | 对应前一检查 | 反馈含SDL错误码 | 含前一完整候选 | 初始prompt前缀相同 |
|---|---|---|---|---|
| call-002 | check-001 | False | False | True |
| call-003 | check-002 | False | False | True |
| call-004 | check-003 | False | False | True |
| call-006 | check-005 | False | False | True |
| call-007 | check-006 | False | False | True |
| call-008 | check-007 | False | False | True |
| call-010 | check-009 | False | False | True |
| call-011 | check-010 | False | False | True |
| call-012 | check-011 | False | False | True |
| call-014 | check-013 | False | False | True |
| call-015 | check-014 | False | False | True |
| call-016 | check-015 | False | False | True |
| call-019 | check-017 | False | False | True |
| call-020 | check-018 | False | False | True |
| call-021 | check-019 | False | False | True |

### 首候选的策略错误与资源抽象

check-001的199项错误分为：call_evidence_text三参/应二参141项，action_evidence_text三参/应二参50项；5个secret缺value_secret_allowed_action（SDL050）；dotenvPath缺value_sensitive_allowed_action（SDL051）；loadRead和listRead同时标记untrusted与sensitive region（SDL060）2项。这些是候选合法性错误，不是199项安全风险。

call-002实际收到的新增反馈只有errors=199、warnings=382和三项覆盖率，没有详细错误码、出错ID或前一完整候选；其反馈前正文与call-001完全相同。这限制了可定位修复信息，不能以研究者读到完整诊断来声称模型已获完整反馈。

dotenvPath不是源中变量：settings.ts:8注释说从当前目录读取.env，:9为无参config()。候选用dotenvPath表示call_region并声明sensitive_local；内容另用dotenvCredentials/secret表示call_output。因此这是隐式文件地址/资源区域的敏感value抽象，不能说地址和内容已经被合并成同一ID。region引文在sidecar匹配su_3106（settings.ts:8）；内容引文GA4_PRIVATE_KEY=匹配su_9（SKILL.md:21），匹配分数仅1/6。

上游规则会由sensitive_local导出value_sensitive_source，因此该资源标识存在被按敏感value处理的抽象问题；但dotenvPath没有成为call_input或call_output，整份候选被拒，尚不能据此声称已发生资源-as-data传播错误或泄漏误报。SDL051只是在要求声明允许的action。本结论绑定check-001原始facts与sidecar，不与历史SkillFlow结果拼成跨版本实测比较。

已记录 20 份逐次校验。selected_iteration=unknown；stop_reason=unknown。具体错误消息、候选哈希及对应证据路径见机器报告。program_valid或evidence_match_rate通过均不能证明接收方、字段、条件和任务依据已经正确绑定。

## 完整源适配对覆盖分母和停止条件的影响

上游reference_unit_coverage按每个语义单元的词法词项数加权，不是简单的单位个数比例，更不是模型计费tokens。按(source_file, unit_type, text, line_start, line_end)多重集匹配，原14文件的623个单位全部保留、没有原单位消失或正文源行边界变化；它们的共同权重为3852。unit ID可随插入移动，因此没有用ID相等来冒充身份相等。

完整16文件权重为12865。新增2532个单位的权重9013来自：package-lock.json的2513单位/8955权重，package.json的17单位/51权重，以及两个新增文件标题的7权重。标题scripts/package-lock.json与scripts/package.json由上游标为SKILL.md的heading、line0；它们是生成的包装标题，不是新增SKILL.md正文。

条件计算：若原623单位全部匹配、新增单位完全未匹配，并且evidence_match_rate与evidence_support_coverage均为1，则评分为0.5+0.3+0.2×(3852/12865)≈0.8599，低于默认0.9提前停止阈值。这仅说明完整源适配会改变同一评分公式的分母及可能的停止行为，不是已观测候选、已经证明的失败原因或原版14文件Semia结果。本次未调整评分、阈值或重跑。两份单位文件及公式源码的SHA保存在机器报告。

## 检测与终态

detector status：unknown。未产出检测结果时，结论保持unknown；不能按零风险计数。报告与recommendation的实际产物状态见JSON。当前没有独立金标，不报告精度、召回、F1或SkillFlow优劣。

report.md状态：not_run；recommendation状态：not_run。实际文本、原始response的格式化一致性和非致命skipped错误分别保存。pipeline exit 0不代表推荐层成功；推荐文本仍需按源和detector逐项审阅，属于模型意见/条件建议，不自动升级为检测事实。

源文件、输入哈希、适配器、helper、CLI的只读一致性观察分别为：True、True、True、True、True。记录PID是否全部缺席：True；若有同PID进程，以启动时间区别PID重用。

进程观察时点：2026-11-18T16:44:22.787405+00:00；观察是否晚于终态：True。记录PID及当前可见子孙进程全部缺席：True。直接父子关系、启动时间、timeout cleanup flags及finished SHA随观察绑定；无法观察的已脱离祖先关系不宣称清零，root wrapper退出另需独立回执。

所有字段的机器值和来源见 [ga4-analysis.json](ga4-analysis.json)。本脚本只读取产物和查询记录PID，不启动模型、pipeline或回放，也不停止进程。
