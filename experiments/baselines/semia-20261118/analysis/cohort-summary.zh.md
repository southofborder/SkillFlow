# Semia 对照批次观察汇总

观察时点（Asia/Shanghai）：2026-11-19T00:44:29.260878+08:00。本表是 as-of 快照；终态仅以各运行 finished.json 为依据。

这些运行属于受控、禁用工具的文本分析变体。历史 SkillFlow 的实现和 CLI 身份不同，仅作背景参考。无独立金标，不报告 F1 或方法胜负。

| case | 状态 | 已观察 native starts | 已知 input+output tokens | 未知 usage 调用 | 候选 / 有效已知 / 校验未知 | 接受的 iteration 记录 | prepared 文件 |
|---|---|---:|---:|---:|---|---:|---|
| 001 | failed | 20 | 376263 | 0 | 20 / 0 / 0 | 0 | 1/1 |
| 010 | completed | 4 | 61957 | 0 | 3 / 1 / 0 | 1 | 3/3 |
| 013 | failed | 20 | 391811 | 0 | 20 / 0 / 0 | 0 | 1/1 |
| ga4 | failed | 21 | 2010100 | 1 | 20 / 0 / 0 | 0 | 16/16 |

`—` 表示尚未运行；unknown 表示未得到测量。已知 token 总数不是最终总成本，cached/reasoning 子计数不重复相加。候选结构通过、被迭代接受和安全结论是不同指标。

逐字段证据路径、CGRS/recommendation 分阶段用量、候选校验错误按谓词归类、输入覆盖回执、检测/报告状态及版本身份见 [机器汇总](cohort-summary.json)。

- 001：[运行目录](../pilot/001)；[完成回执](../pilot/001/finished.json)。
  - 已知校验错误 SDL003：call_evidence_text expects 2 args, got 3，出现 59 次。
  - 已知校验错误 SDL050：secret value '<id>' has no value_secret_allowed_action，出现 20 次。
  - 已知校验错误 SDL061：call '<id>' has both untrusted and secret region annotations，出现 20 次。
  - 已知校验错误 SDL003：action_param_evidence_text expects 4 args, got 3，出现 11 次。
  - 已知校验错误 SDL003：action_trigger_evidence_text expects 3 args, got 2，出现 9 次。
  - 已知校验错误 SDL003：action_evidence_text expects 2 args, got 3，出现 7 次。
- 010：[运行目录](../comparison/010)；[完成回执](../comparison/010/finished.json)。
  - 已知校验错误 SDL003：call_evidence_text expects 2 args, got 3，出现 7 次。
  - 已知校验错误 SDL003：action_trigger_evidence_text expects 3 args, got 2，出现 1 次。
  - 已知校验错误 SDL003：action_param_evidence_text expects 4 args, got 3，出现 1 次。
  - 已知校验错误 SDL003：call_effect_evidence_text expects 3 args, got 2，出现 1 次。
- 013：[运行目录](../comparison/013)；[完成回执](../comparison/013/finished.json)。
  - 已知校验错误 SDL003：call_evidence_text expects 2 args, got 3，出现 105 次。
  - 已知校验错误 SDL061：call '<id>' has both untrusted and secret region annotations，出现 44 次。
  - 已知校验错误 SDL003：action_trigger_evidence_text expects 3 args, got 2，出现 12 次。
  - 已知校验错误 SDL003：action_evidence_text expects 2 args, got 3，出现 6 次。
  - 已知校验错误 SDL003：action_param_evidence_text expects 4 args, got 3，出现 2 次。
  - 已知校验错误 SDL050：secret value '<id>' has no value_secret_allowed_action，出现 1 次。
- ga4：[运行目录](../comparison/ga4)；[完成回执](../comparison/ga4/finished.json)。
  - 已知校验错误 SDL003：call_effect_evidence_text expects 3 args, got 2，出现 809 次。
  - 已知校验错误 SDL003：call_evidence_text expects 2 args, got 3，出现 625 次。
  - 已知校验错误 SDL003：action_trigger_evidence_text expects 3 args, got 2，出现 508 次。
  - 已知校验错误 SDL003：action_evidence_text expects 2 args, got 3，出现 221 次。
  - 已知校验错误 SDL003：call_code_evidence_text expects 3 args, got 2，出现 42 次。
  - 已知校验错误 SDL051：sensitive value '<id>' has no value_sensitive_allowed_action，出现 37 次。
  - 已知校验错误 SDL003：action_gate_evidence_text expects 3 args, got 2，出现 32 次。
  - 已知校验错误 SDL050：secret value '<id>' has no value_secret_allowed_action，出现 29 次。
