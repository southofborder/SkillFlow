# GA4 SEMIA 完整源变体终态分析

本次唯一运行已结束：上游 pipeline exit **2**，root 的 PowerShell wrapper exit **1**；两者是不同层级的退出码。终态时间 **2026-11-19 00:43:10（Asia/Shanghai）**，elapsed **24,869.019 秒**，约 **6 小时 54 分 29 秒**。

**5轮、20份候选全部未通过校验，0份选中。** 上游stderr为 `synthesis produced no valid candidate after 5 iteration(s)`。synthesis metadata仍如实保留 `completed=false`、`stop_reason=null`、`selected_iteration=null`；终态由finished回执及退出错误确认，不能改写这些上游字段。

## 次数、用量与传输

- 实际 **21 CGRS native starts**：20个逻辑结构尝试，其中call-017超时后，call-018以相同phase/prompt作一次provider重试。20个成功返回的响应分别SHA绑定20份候选和20次校验；没有最终selected-facts复核。
- stderr共有 **25条内部sampling retry日志**，不能算作额外native starts，也不是20个候选之外再追加的结构尝试。
- 独立读取全部stdout completion事件：input **1,297,907**、output **712,193**，已知公开总计 **2,010,100 tokens**。cached input **522,240**、reasoning output **23,168**为子计数，不重复相加。
- call-017无公开completion/usage，response文件为0字节；该请求与未公开内部采样费用未知。阶段完整总量保留null，以上是已知下界。全部20份可见usage与request汇总逐字段一致，终态计数也一致。
- call-017耗时2700.142秒，timed_out=true，native退出1，tree cleanup退出0，unresolved字段缺省。它先出现5条WebSocket内部重试并回落HTTP，再出现2条HTTP响应体解码重试；最终被adapter时限终止。call-018随后返回attempt4_0。这增加了时间/未知费用，但并未阻止20个结构尝试全部用完。

## 失败分布及可以支持的原因

20份候选累计 **2375条错误记录**，它们包含各候选中重复出现的问题，不是独立漏洞数。

|校验类别|累计记录|含义|
|---|---:|---|
|SDL003|2261|evidence谓词参数数量错误|
|SDL051|37|敏感value缺少允许action策略|
|SDL050|29|secret value缺少允许action策略|
|SDL060|28|同一call兼有untrusted与sensitive region|
|SDL032|17|action内没有root call|
|SDL030|3|重复fact|

14/20份候选有参数数量错误；另外6份没有SDL003，仍被策略或图结构校验拒绝。check-005只剩3个无root的action；其候选将批处理循环连成没有入口的环。check-011只剩load_read_json的一项SDL060，随后check-012又出现25项参数数量错误。末两份check-019/020分别有248/69项错误，不能描述为稳定收敛或已经得到可检测模型。

全部 **15个修复prompt**只添加错误/警告计数和三项覆盖率；正文前缀与初始prompt相同，没有详细SDL错误码或上一完整候选。该观察支持“反馈不利于定位修复”，不证明换prompt一定成功。若干主要谓词的固定prompt示例本身具有正确参数数量，因此也不能把所有参数错误归因于错误schema示例。

## 完整输入、覆盖与未运行下游

21/21个实际payload均包含完整16文件，prepare回执SHA及实际CLI argv也全部匹配。官方原版默认只含14文件；本次明确是Semia+complete-source受控变体。新增两份package文件改变词法权重覆盖分母：原共享623单位权重3852，完整3155单位权重12865；两份单位文件SHA与条件公式保留在机器报告。

“原共享单位全覆盖、新增单位不覆盖、另外两项分数都为1”时分数约0.8599，低于0.9阈值。这是适配的条件效应，不能据此断言本次没有selected是覆盖分母导致：**本次所有候选首先因合法性失败被拒。** 实际引文匹配率约97.57%—98.93%，reference单位覆盖约10.97%—15.71%，都不是语义正确性或安全准确率。

Detector、上游report与recommendation均为 **not_run**，findings为 **null**；不能填零风险。recommendation native starts确实为0。没有独立金标，不报告F1或SkillFlow优劣；历史SkillFlow的实现/CLI不同，仅可参考。

## 终态身份与进程证据

一次终态审计在 **2026-11-19 00:44:22（Asia/Shanghai）**作只读CIM快照：**22个记录PID及当时可见后代全部缺席**。保留timeout cleanup flags，并与root的wrapper退出回执绑定；未再次查询或干预进程。360个官方source、16个input的inventory/hash/size、source/input manifest、runner/helper/CLI身份均通过。已接受审计脚本SHA保持 `63055c076c9f203de128064233c6aa037348287ebce8c65cf958e377d3030f82`。

逐候选→validation→native响应SHA映射、公开用量、失败类别与来源见 [ga4-final-assessment.json](ga4-final-assessment.json)；完整逐字段审计见 [ga4-analysis.json](ga4-analysis.json)，同一进程快照见 [ga4-process-observation.json](ga4-process-observation.json)。原始运行、脚本及报告由新的ga4-freeze.json清单封存，不改变其他三例或root负责的汇总文件。
