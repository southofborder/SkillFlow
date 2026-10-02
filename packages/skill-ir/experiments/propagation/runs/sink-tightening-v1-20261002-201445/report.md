# Sink 收紧与可选参数：三例验证

本次复用冻结源文和既有 CFG，每例一次联合标注；网络分类须有机制依据，可选参数保留原字段和控制关系，sink 类型与等级由程序生成。传播及重放不调用 API。等级不是敏感度、必要性或 DOE 结论；任务内部等级 0 和删除仍保留传播关系。

| 样例 | 标注 | 传播 | Sink 位置 | 逻辑调用 | 审查入口 |
|---|---|---|---:|---:|---|
| 001 / N01 | not_run | not_run | 0 | 0 | [既有 CFG](cases/001/selected-analysis.json) |
| 010 / Q04 | not_run | not_run | 0 | 0 | [既有 CFG](cases/010/selected-analysis.json) |
| 013 / F01 | not_run | not_run | 0 | 0 | [既有 CFG](cases/013/selected-analysis.json) |

审查表分别展示纳入／排除、位置范围与留存、固定等级、当前操作的数据版本。工具默认 recipient 是契约保留的外部接收可能性，不是已测得的网络事实。
