# 已确认语料的同契约语义基线

官方 DeepSeek 独立批次 `baseline-deepseek-v4-flash-max-20260910` 的 90 次计划已全部执行结束：**85 `complete`、5 `error`、0 未运行**，当前没有在线进程。请求模型为 `deepseek-v4-flash`、推理档 `max`，HTTP 返回名称保留为 `deepseek-flash`。5 条失败保持原状，批次状态因此为 `failed`；结构有效不代表语义通过。当前复现入口、统计和隔离规则见 [DEEPSEEK.md](DEEPSEEK.md)，最终执行检查点为 `operation_checkpoints/20260910T144548Z/`。下文 Sol 数据均为历史记录，与新模型分别保存。 本批次发现与后续处理顺序见 [RESULTS.md](RESULTS.md)。

本轮生产 Prompt、IR 模型和提取 pipeline 均未修改。最后全包离线测试为 **514 passed in 64.74s**；随后仅对 PDF 分页修正运行相关聚焦回归，**29 passed in 1.22s**，不将两次计数相加。30 份外置初审、891 项事实运行判定已校验完成；最终结果 PDF 为 **730 页**，已完成确定性重建、全量 110 dpi 渲染与全部页面的联合视觉检查，详见 [QA.md](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/QA.md) 和 [visual_qa.json](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/visual_qa.json)。结果册定位与读法见 [RESULTS.md](RESULTS.md)；模型结果和初审意见仍待用户共同复核。

本目录实施《Skill 文档理解数据集与 PDF 共同复核方案》的后续步骤。用户于 2026-09-10 明确共同确认二次复核修订及待确认部分，参考答案由此冻结。对原文未知范围的确认表示接受该边界，不把未知改写为确定运行策略。

**旧 Sol 批次因上游服务失败停止，90 次旧模型基线未完成。** 主要 SSE 批次 `baseline-sol-max-sse-20260910` 已提交 23 次试验：14 `complete`、9 `error`，剩余 67 `not_run`（开发集 43、保留集 24）。并发批次自动停止后等待数分钟，单并发 F02 第 2 次仍发生上游断流，因此停止追加请求。实际记录见 `runs/baseline-sol-max-sse-20260910/report.json`；`complete` 只表示结构有效，不表示语义通过。

该 SSE 部分批次共 29 次生成、6 次结构修复、34 次 HTTP 尝试、5 次 HTTP 重试，收到 20 条用量记录，已知输入 109,042、输出 102,395、合计 211,437 tokens。缺失请求用量保持 null，不能计为 0；9 条 `error` 均发生在 HTTP 200 之后，并保留 `remote_outcome_unknown`。已完成七份样例的正式格式初审，共 192 个判定：69 `preserved`、31 `partial`、66 `unassessable`、6 `contradicted`、20 `missing`。F02 未满三次，不作逐事实判定。这些是实际阶段性结果，仍待共同复核。

旧批次 `runs/baseline-sol-max-v1/` 的 HTTP 524、读取超时及 4 条远端结果未知记录完整保留。新批次通过 `--restart-of` 只读绑定旧 report 与运行身份摘要，没有删除旧记录、继承旧试验或把未知请求改成成功；旧执行状态 PDF 仅说明旧批次。

非流式重试批次 `runs/baseline-sol-max-retry-20260910/` 已软停止并排空，保留 13 条终态（4 `complete`、9 `error`）和 77 条 `not_run`，共 40 次 HTTP 尝试、24 次 HTTP 重试、16 次生成、3 次结构修复，已知用量 65,295 tokens。其 N01–N04 四份正式格式初审共 108 个判定及 `review_drafts/N05-run-1.json` 局部草稿均作为部分实验材料保留，不替换或拼入 SSE 三次重复。传输选择的原因、旧报告摘要与保持不变的输入/Prompt/模型等证据见 `runs/baseline-sol-max-sse-20260910/transport_decision.json`。

## 冻结与契约

- `approval.json` 逐条绑定 297 个已确认事实及标注摘要；确认不等于模型输出已经通过。
- `frozen/corpus/` 是已审语料的完整字节快照。只把其中单个 `inputs/` 包交给生产加载器；包外标注、复核意见、来源清单和 PDF 不进入模型输入。
- `frozen/production/`、`frozen/original_contract/` 保存原实现、候选 Schema、原 Prompt 及全部 30 份实际输入 Prompt。`frozen/review/` 保存已审材料。
- `freeze_manifest.json` 锁定所有内容。`tools/freeze.py` 离线校验；不得为迁就结果修改冻结答案。更改参考标准需建立新版本并共同复核。
- `CONTRACT.md` 与 `contract_v2/` 单独记录三层 `constraints: list[str]` 的迁移。基线使用仅适配该契约的原 Prompt，后续 Prompt 比较必须沿用同一契约，不能把新增字段归为优化收益。

旧 `semantics_review/` 的标注初始状态和 PDF 原件保留，本目录的 `approval.json` 是其有效确认记录。详细冻结结构见 `FREEZE.md`。

## 执行与恢复

每版固定 30 份样例、每份 3 次，共 90 次提取。开发集 22 份、66 次；保留集 8 份、24 次。三个旧回归示例不混入本批。原 Sol 协议沿用 `sol_max` 的模型与推理档；当前 DeepSeek 使用独立的显式配置和入口，详见 `DEEPSEEK.md`。密钥不写入配置或产物。

旧 Sol 批次已经停止。下面是其历史恢复说明；当前 DeepSeek 环境不可直接用于旧身份。曾使用原服务配置时，可从仓库根目录使用下面的预检及恢复示例，文档命令不会自动调度；恢复前需保持原身份，先检查停止文件与已提交记录：

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/freeze.py
$baselineRun = "packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910"
$previousRun = "packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-v1"
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --check --split development
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --split development --workers 1 --max-new-trials 1 --max-consecutive-errors 1
# 开发集执行完成、基线版本锁定后，再执行保留集。
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --split holdout --workers 4 --max-consecutive-errors 4
```

SSE 入口要求显式 `--run-dir`，恢复时保留相同 `--restart-of`。不要用非流式 `run_baseline.py` 恢复 SSE 目录，也不要把新输出写入任一非流式目录。`--max-new-trials 1 --workers 1 --max-consecutive-errors 1` 限制一次新的未运行 trial；该命令不会重发失败终态。剩余 `not_run` 可以在原身份下续跑，但要补足失败重复，须明确建立新的重复批次与关联，不能删除、覆盖既有 `error`/`uncertain` 或直接借用其他传输批次的结果。

创建 run 目录下的 `STOP` 文件可软停止：调度器每秒检查，只停止提交新 trial，排空在途 worker 及其既有 HTTP 重试。此前并发批次连续错误阈值为 4，最后一次单并发探测阈值为 1；SSE 入口默认阈值为 1，可用 `--max-consecutive-errors` 调整。结构 `degraded` 不计入该阈值。`report.scheduler` 记录停止原因和本次提交数，历次操作检查点另存 `operation_checkpoints/`。冻结内容检查之外，入口还对实际二次解析后的 case 路径、源文件集合及摘要、标准化输入摘要再次核验，禁止 dataset 重定向。

SSE 必须收到完整 `[DONE]` 事件和 choice 0 的结束状态才接受响应。收到 2xx 后断流、超时或格式错误，trial 终态为 `error`，但 `trace.json` 的 `calls[].http_attempts[].stream.outcome` 标记为 `remote_outcome_unknown`，保留已观察的 HTTP 状态及原始 SSE、残片和事件时间，不得自动重发。180 秒仍为读取非活动超时；持续事件可能延长总耗时，完全没有 SSE 时仍可能超时。传输变化独立记录，没有更改 Prompt、模型、推理档位、契约或生产提取流程。

实际运行与断点恢复规则见 `RUNNING.md`。完整/失败的终态不自动重跑；进程中断且未提交完整结果的请求在恢复时保留为 `uncertain`，正常提交的 SSE 断流则按上文保留 `error` 及远端未知标记。原始响应、生成轮次、结构修复、HTTP 重试、时间和服务返回用量分别记录。没有有效 CFG 的网络失败或结构失败不能计为语义通过或 Skill 理解错误。报告里的 `complete` 仅表示结构与引用校验完成。

## 结果初审与共同复核

`tools/review_results.py --export` 只在离线环境读取已结束的三次运行，导出 `runs/<run>/review_packets/<ID>.json`。文件包含冻结事实、原文路径和真实 CFG。为缩短初审材料，只对 `metadata.script_content` 展示长度与摘要；完整原文仍在对应 `analysis.json`，不改变模型产物。

人工或代理对照原文及实际 CFG 后，把逐事实三次初审写入 `runs/<run>/reviews/<ID>.json`。每条结果标为 `preserved`、`partial`、`missing`、`contradicted` 或 `unassessable`，附理由及真实块、指令、边或约束引用。review 文件绑定每次 `analysis.json` 和 `record.json` 的摘要，不使用关键词扫描自动判语义通过。

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/review_results.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910 --samples N01 N02 N03 N04 N05 N06 F01 --check
python packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910 --interim-results --output output/pdf/skill-ir-semantics-baseline-sse/skill-ir-baseline-interim-review.pdf
```

本次阶段性交付文件为 `output/pdf/skill-ir-semantics-baseline-sse/skill-ir-baseline-interim-review.pdf`。`--interim-results` 保留 90 条计划与缺失状态，仅详列已经尝试的真实结果、已具备三次终态的初审和实际 CFG；它是明确标注未完成的正式阶段性材料，不是完整基线结论。生成后还必须完整渲染、检查中文字形、表格和代码、页码与样例编号，机器文字检查不能代替视觉复核。结果结论继续等待共同确认。

完整结果模式仍要求 90 条试验及 891 项逐事实判定齐全，上述旧 Sol 部分批次会被拒绝；不能用 `--interim-results` 把阶段性结果宣称为完整结果。`--allow-partial` 仅用于布局预览；`--execution-status-only` 只说明实际请求状态。审计见 SSE 目录的 `transport_audit.json`，它没有发现本地响应串写证据，也不能定位服务端原因。两个旧批次、审计与操作检查点均保留。

参考事实不是所有真实包可选工作流的穷举。未列入事实表的操作仍需回查原文，不能自动判为新增。现有附加写入样例不覆盖互不相关组件及“不凭空连边”；这项能力不纳入本批已覆盖结论。

收到共同确认的基线结果后，才根据开发集的具体语义问题形成下一版 Prompt，再检查保留集。保留集不写进 Prompt 示例，不用于当前轮反复调参。关键行为遗漏、无依据新增、条件丢失和数据来源/去向错误尚未处理完之前，不进入语义回溯阶段。
