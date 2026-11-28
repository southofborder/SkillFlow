# 对照批次汇总器说明

从独立Semia实验目录执行：

```powershell
& .\.venv\Scripts\python.exe .\analysis\summarize_comparison.py
```

入口只读取 `pilot/001`、`comparison/010`、`comparison/013`、`comparison/ga4` 以及输入清单和已有校验审计；它不会运行模型、Skill、Semia分析器、旧SkillFlow或任何回放。重复运行仅刷新本目录的 `cohort-summary.json` 和 `cohort-summary.zh.md` 派生快照。

JSON的数值和状态通过 `value`、`status`、`evidence` 表示；证据路径相对于实验根目录。状态为 `not_run` 的case，其测量为null，不生成伪零调用或零告警。已启动但尚无完成回执标为 `in_progress`，并说明这是回执状态，不是对进程存活的独立证明。读取期间遇到JSON写入中间态或不可解析记录时，记录 `read_issues` 并保留未知。

`known_cohort_accounting` 与每例 `accounting` 聚合已观察到的原生开始数、缺用量请求、未退出请求、非零退出和已完成请求耗时。每个token字段分别记录 `known_sum` 和缺该字段的原生请求数。优先读取请求回执；若进程已输出公开 `turn.completed` 用量但回执尚未更新，则读取public stdout。Cached input和reasoning output只作为子计数展示，不重复加进input+output。未完成请求及provider未公开的内部使用量仍可能使总成本更高。

`phases` 分CGRS、recommendation与unknown。后续runner的显式phase优先；001缺少phase字段时，优先按recommendation prompt的字节哈希对应关系，否则依据明确的上游prompt首行分类，并将其标为inferred。分类依据随每个call保存，不暗称原始回执已有该字段。

候选以原始 `synthesis_attempt_*.dl` 文件计数。001使用已有离线只读审计结果，必须与候选SHA匹配；其他三例使用逐次validation中的submitted-facts SHA及成功返回标记。找不到绑定的详细校验就计入“校验未知”，不使用最后一份共享check代表全部候选，也不重新执行校验。错误按code、谓词（能从arity消息识别时）与去掉具体值ID后的消息模式聚合；每组保留校验来源。`accepted_iteration_records` 取上游metadata，与结构有效候选数分别记录。

覆盖记录取该次真实prepare的file inventory及complete-source receipt；仅提供了输入目录不等于模型看到全文。对后续runner，另统计实际请求中显式通过完整source payload检查的回执。001没有这一字段，统计为零仅表示没有该类型回执，不表示001源文被遗漏。

检测状态取 `detection_result.json` 的status，告警数只在存在findings数组时计算；报告和recommendation以实际产物是否出现表示。缺文件在运行中是“尚未观察”，终态是“未产出”，不会转换成安全判断。版本身份取各次runtime及终态完整性回执；001的源码提交可通过与固定source-manifest完全相同的文件哈希集合推断，并保留推断来源。

这些数据属于受控、无工具的文本分析变体。历史SkillFlow的实现、继承阶段和CLI身份不同，仅作为参考。汇总器不计算缺乏独立gold的精度、召回、F1，也不由结构检查通过或零检测结果宣称安全或领先。
