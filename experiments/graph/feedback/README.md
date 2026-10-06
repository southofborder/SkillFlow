# F01 CFG 语义反馈实验

本目录保存有界语义反馈实验。通用实现位于 `src/skillflow/graph/feedback/`；这里仅调度五个已冻结图，不作为任意 Skill 的接口。当前新运行采用 v5 核对与反馈协议；历史响应和报告保持当时版本，不用新解析器重新解释。七类检查点仅作阅读提示，可选保守依赖说明不写入原图 IR。

固定输入为编号 013、F01、第 1 轮原图及四个反例：archive 多传密钥、失败出口缺少状态追加、重试成功返回首次结果、增加明确两秒等待。各例从实际 CFG 重新进行第 0 轮核对，不将变体构造前的 `raw_candidate` 当作变体输入。种子文件位于新运行的 `inputs/`，不改写历史输入。

## 执行

在仓库根目录运行：

```powershell
python -m tools.graph.feedback.run_f01 run --run-dir experiments/graph/feedback/runs/<new-id>
python -m tools.graph.feedback.run_f01 replay --run-dir experiments/graph/feedback/runs/<new-id>
```

`run` 可指定 `--env-file`，两个命令均可指定 `--renderer`。不指定运行目录时，在线模式创建 UTC 时间戳目录。请求固定为已有官方 DeepSeek 配置 `deepseek-v4-flash`，每次实际返回名、用量和传输尝试在调用记录中保存。命令从环境读取密钥，不把凭据写入配置清单。

每例最多 3 次语义修复，每次提取最多 3 次结构修复，五例合计最多 80 次逻辑调用，HTTP 重试另计。单例失败保留结果并继续其他例；中断后不启动后续例。`replay` 只处理新版闭环记录，零 API，不重新提取线上响应。

## 新运行目录

```text
runs/<run-id>/
  manifest.json                F01 来源、配置与五例种子身份
  inputs/c01-analysis.json     仅含该例实际 cfg；共五份
  cases/c01/                   通用反馈完整记录；共五例
  progress.json                已完成或停止的案例状态
  experiment-result.json       五例结果与事后评测候选
  report.md                    中文对照报告
  assistant-review.md          实际执行后的助手复核，单独标注
  replay/                      离线重放的汇总与报告
```

`assistant-review.md` 由实际查看新图和证据后的助手写入；生成器不会预先伪造人工确认。案例报告记录每轮差异、停止原因及最后建议。运行清单和调用内容受摘要、身份与互斥锁保护；重用目录须对应同一输入、配置和代码身份。

外置人工预期只在全部模型调度结束后读取。第 0 轮的类别、源文和图证据匹配只产生复核候选；重新提取后不再使用原指针判断是否修好。保留漏报、误报、新增问题、语义失败、修复失败与执行错误。

`audit_passed` 只表示**核对器通过**，其前提包括存在业务语义核对项且全部为 `represented`。结构通过、覆盖完整、全背景项或最终没有解析出的差异都不能替代这个条件。工程测试与 Lean 事实保持证明不保证模型的语义判断正确。

完整规范见仓库 `docs/graph/CFG构建语义反馈闭环.md`。
