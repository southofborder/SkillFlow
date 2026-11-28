# 相关工作与对照实验

2026-11-18 新工作入口。用户选择优先采用**同模型、同一批 Skill**开展 Semia 对照。
本目录的研究记录不改变历史实验授权和封存状态。

2026-11-19：首例分析后已完成剩余三个样本，四例均已终止。010进入检测并得到零告警；001、013、GA4未生成合法表示，检测未运行。合计65次原生调用、2,840,131已知公开tokens，另一次超时请求用量未知。

- [截至 2026-11-24 的论文与会议进展](related-work-update-20261124.zh.md)：SkillPrivus、SkillCFI 等新稿，安全／SE／AI 会议身份核实，ToolMinimize 补漏及对研究定位的影响；附 [来源记录](related-work-update-20261124.sources.json)。
- [截至 2026-11-18 的类似项目更新](related-work-update-20261118.zh.md)：主要论文、公开实现、近期变化及研究定位。
- [四样本最终结果与失败原因](semia-cohort-results-20261119.zh.md)：实际完成情况、成本、协议与反馈缺口，以及同模型同源对照的边界。
- [Semia 对照协议](semia-comparison-protocol-20261118.zh.md)：共同分析问题、输入与模型对齐、指标和不可比较项。
- [实际复刻工作目录](../../experiments/baselines/semia-20261118/README.zh.md)：固定版本、隔离环境、官方离线测试、输入预处理。
- [完整输入清单](../../experiments/baselines/semia-20261118/input-manifest.json)：四个已有工程样本的逐文件哈希和原始来源。
- [受控调用首例](../../experiments/baselines/semia-20261118/pilot/001/)：实际状态以该目录的 `runtime.json`、`calls.json`、`finished.json` 为准；没有 `finished.json` 不能视作完成。
- [首例最终失败分析](../../experiments/baselines/semia-20261118/analysis/001-failure-audit.zh.md)：20候选无有效表示，公开376263 tokens；分析后才放行剩余样本。
- [010最终分析](../../experiments/baselines/semia-20261118/analysis/010-analysis.zh.md)：4次调用完成，检测零告警；明确区分引文覆盖、抽象数据流和精确参数语义。
- [013最终分析](../../experiments/baselines/semia-20261118/analysis/013-analysis.zh.md)：20候选均被校验拒绝，公开391811 tokens；没有将未运行的检测记成零告警。
- [GA4最终分析](../../experiments/baselines/semia-20261118/analysis/ga4-final-assessment.zh.md)：21次原生调用生成20份无效候选；一次2700秒超时的公开用量未知。
- [后续执行约定](semia-followup-20261118.zh.md)与[批次汇总](../../experiments/baselines/semia-20261118/analysis/cohort-summary.zh.md)：完整同输入适配、实际阶段和未运行项。

公开实现复刻、论文原数字复现、同模型配对评测是不同证据。首例只检查可运行性、输入覆盖与成本；四个既有调试样本没有独立金标，也不代表总体效果。历史 SkillFlow 输出保留各自版本身份，不能直接拼成当前版本的配对成绩。
