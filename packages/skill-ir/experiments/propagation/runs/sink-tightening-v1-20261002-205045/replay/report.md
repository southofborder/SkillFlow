# Sink 收紧与可选参数：三例验证

本次复用冻结源文和既有 CFG，每例一次联合标注；网络分类须有机制依据，可选参数保留原字段和控制关系，sink 类型与等级由程序生成。传播及重放不调用 API。等级不是敏感度、必要性或 DOE 结论；任务内部等级 0 和删除仍保留传播关系。

| 样例 | 标注 | 传播 | Sink 位置 | 逻辑调用 | 审查入口 |
|---|---|---|---:|---:|---|
| 001 / N01 | complete | complete | 6 | 1 | [既有 CFG](../cases/001/selected-analysis.json) · [标注和位置属性](../cases/001/annotation/report.md) · [原始响应](../cases/001/annotation/audit/raw-annotation.json) · [编译 sink 清单](../cases/001/annotation/sink-boundaries.json) · [数据与边界审查](../cases/001/propagation/report.html) · [DOE 原始事实](../cases/001/propagation/doe-input.json) · [DOE 变化对照](../cases/001/doe-input-change.html) · [助手复核](../cases/001/assistant-review.md) |

001：标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。
| 010 / Q04 | complete | complete | 12 | 1 | [既有 CFG](../cases/010/selected-analysis.json) · [标注和位置属性](../cases/010/annotation/report.md) · [原始响应](../cases/010/annotation/audit/raw-annotation.json) · [编译 sink 清单](../cases/010/annotation/sink-boundaries.json) · [数据与边界审查](../cases/010/propagation/report.html) · [DOE 原始事实](../cases/010/propagation/doe-input.json) · [DOE 变化对照](../cases/010/doe-input-change.html) · [助手复核](../cases/010/assistant-review.md) |

010：标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。
| 013 / F01 | complete | complete | 16 | 1 | [既有 CFG](../cases/013/selected-analysis.json) · [标注和位置属性](../cases/013/annotation/report.md) · [原始响应](../cases/013/annotation/audit/raw-annotation.json) · [编译 sink 清单](../cases/013/annotation/sink-boundaries.json) · [数据与边界审查](../cases/013/propagation/report.html) · [DOE 原始事实](../cases/013/propagation/doe-input.json) · [DOE 变化对照](../cases/013/doe-input-change.html) |

013：标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

审查表分别展示纳入／排除、位置范围与留存、固定等级、当前操作的数据版本。工具默认 recipient 是契约保留的外部接收可能性，不是已测得的网络事实。
