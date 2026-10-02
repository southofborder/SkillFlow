# F01 语义反馈首次对照实验

五例分别以冻结原图或结构有效反例开始，每例最多三次语义修复；提取与核对上下文独立。下列名称仅用于事后报告，不进入模型输入。

## 实际停止结果

| 案例 | 停止状态 | 修复轮数 | 最后一轮业务核对 | 原因 |
|---|---|---|---|---|
| [c01 · F01 原图](cases/c01/report.md) | 核对执行错误 | 0 | 无有效业务核对项 | IncompleteRead(0 bytes read) |
| [c02 · archive 增加密钥输入](cases/c02/report.md) | 核对器通过 | 1 | 保留（模型判定） 9 | 所有业务项均为 represented，且没有明确差异或未决。 |
| [c03 · 删除失败出口状态追加](cases/c03/report.md) | 核对器通过 | 1 | 保留（模型判定） 10 | 所有业务项均为 represented，且没有明确差异或未决。 |
| [c04 · 重试成功返回首次结果](cases/c04/report.md) | 提取执行错误 | 1 | 无有效业务核对项 | Incomplete SSE response: both [DONE] and choice finish_reason are required |
| [c05 · 增加明确两秒等待](cases/c05/report.md) | 核对器通过 | 1 | 保留（模型判定） 11 | 所有业务项均为 represented，且没有明确差异或未决。 |

已知记录的提取逻辑调用：4；核对逻辑调用：8；HTTP 尝试：12。五例默认逻辑调用上限为 80，HTTP 重试另计。

## 外置预期与复核状态

仅在全部在线调度结束后读取外置预期。第 0 轮的类别与证据区域匹配只是复核候选；重新提取后不会使用旧图指针自动认定缺陷已修复。

| 案例 | 外置预期 | 初轮候选核对项 | 最终修复复核 |
|---|---|---|---|
| c01 | baseline-gold-r01 | 无匹配候选 | assistant_review_pending |
| c01 | baseline-gold-r02 | 无匹配候选 | assistant_review_pending |
| c01 | baseline-gold-r03 | 无匹配候选 | assistant_review_pending |
| c01 | baseline-gold-r04 | 无匹配候选 | assistant_review_pending |
| c02 | archive-receives-credential | finding_7 | assistant_review_pending |
| c03 | failure-status-append-missing | finding_9 | assistant_review_pending |
| c04 | retry-returns-first-body | finding_8 | assistant_review_pending |
| c05 | added-two-second-wait | finding_8 | assistant_review_pending |

## 方法判断边界

各案例 report.md 给出逐轮差异、未决、建议和停止原因。完整 result.json 及 rounds、calls 保存实际候选、图、受控文本、响应与证据。

工程结果是执行、保真、记录、恢复和停止控制是否符合规范；方法结果需进一步核查模型是否识别了真实问题、是否误改、是否引入新问题，以及是否出现核对器假通过。

生成报告不把‘核对器通过’自动视为修复正确；助手复核记录应另存 assistant-review.md，并明确尚未由用户确认。F01 五例不支持统计显著性或通用正确性结论。
