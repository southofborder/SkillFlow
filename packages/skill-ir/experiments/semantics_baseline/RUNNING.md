# 首轮同契约基线运行与恢复

官方 DeepSeek 独立批次 `baseline-deepseek-v4-flash-max-20260910` 的 90 次计划已全部执行结束：**85 `complete`、5 `error`、0 未运行**，当前没有在线进程。请求模型为 `deepseek-v4-flash`、推理档 `max`，HTTP 返回名称保留为 `deepseek-flash`。5 条失败保持原状，批次状态因此为 `failed`；结构有效不代表语义通过。当前复现入口、统计和隔离规则见 [DEEPSEEK.md](DEEPSEEK.md)，最终执行检查点为 `operation_checkpoints/20260910T144548Z/`。下文 Sol 数据均为历史记录，与新模型分别保存。 本批次发现与后续处理顺序见 [RESULTS.md](RESULTS.md)。

本轮生产 Prompt、IR 模型和提取 pipeline 均未修改。最后全包离线测试为 **514 passed in 64.74s**；随后仅对 PDF 分页修正运行相关聚焦回归，**29 passed in 1.22s**，不将两次计数相加。30 份外置初审、891 项事实运行判定已校验完成；730 页结果 PDF 已完成确定性重建、全量 110 dpi 渲染及联合视觉检查，证据见 [QA.md](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/QA.md) 和 [visual_qa.json](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/visual_qa.json)。不会自动新增在线试验或重放五条失败，模型结果和初审意见仍待用户共同复核。

下文记录此前 Sol 基线的运行和恢复方法。本目录使用用户已经共同确认的冻结语料，运行 `constraints-v2` 契约下的首轮基线。`baseline.json` 继承原 `sol_max.json` 的模型、推理力度与结构修复上限：`gpt-5.6-sol`、`max`、最多 3 轮结构修复。服务地址、密钥、HTTP 超时和重试参数仍由现有环境解析器读取；密钥不会写入结果。

`dataset.json` 只包含 30 个样例编号和独立 Skill 输入目录。每个输入目录都位于 `frozen/corpus/inputs` 下；事实标注、清单、来源和复核意见在包外。实验代码使用现有加载器和提取流程，不执行 Skill 内的脚本、工具或部署指令。

2026-09-10 旧 Sol 继续执行当时仍因上游服务失败未完成其 90 次基线，随后停止。旧主要 SSE 批次 `runs/baseline-sol-max-sse-20260910/` 已提交 23 次试验：14 `complete`、9 `error`，剩余 67 `not_run`，其中开发集 43 次、全部保留集 24 次。并发批次自动停止后等待数分钟，单并发 F02 第 2 次仍断流，故停止追加请求；没有把失败重试成成功或改写原记录。

SSE 共 29 次生成、6 次结构修复、34 次 HTTP、5 次 HTTP 重试，收到 20 条 usage，已知输入 109,042、输出 102,395、总计 211,437 tokens。缺失请求用量保持 null，不视为 0。9 条失败均在 HTTP 200 之后，trace 标记 `remote_outcome_unknown`。原始 `runs/baseline-sol-max-v1/` 的 4 条 `uncertain` 与非流式重试 `runs/baseline-sol-max-retry-20260910/` 的全部日志均只读保留，不能与 SSE 重复混合。

`runs/baseline-sol-max-sse-20260910/transport_decision.json` 记录非流式长请求反复失败后的传输调整原因、旧报告 SHA 和输入/Prompt/模型/生产源码保持一致的证据。非流式重试最终保留 13 条终态：4 `complete`、9 `error`，另有 77 `not_run`；共 40 次 HTTP、24 次 HTTP 重试、16 次生成、3 次结构修复，已知总用量 65,295 tokens。其 N01–N04 四份初审共 108 个判定及 N05 第一次局部草稿是独立的部分实验材料，不能作为 SSE 某次重复的替代品。

## 执行命令

下面是服务恢复后的预检和未运行试验续跑示例，使用安装了本包依赖的 Python，在仓库根目录执行。当前已停止在线任务，文档命令不会自动执行：

```powershell
$baselineRun = "packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910"
$previousRun = "packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-v1"
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --check --split development
# 服务恢复后先新增一个尚未运行的完整 trial；不会覆盖任何失败终态。
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --split development --workers 1 --max-new-trials 1 --max-consecutive-errors 1
```

`--check` 验证冻结内容、样例划分、输入清单和有效配置，不发起网络请求。除预检外，实际执行器再次解析配置后、写入运行记录与请求前还核验 `resolved.cases`：dataset 必须是本目录 `dataset.json`；编号和路径顺序必须对应冻结 corpus；输入的完整文件集合及 SHA 必须匹配冻结清单；实际加载 package 与规范化输入摘要也必须一致。只检查一个清单文件后将请求重定向到另一个 dataset 的路径被拒绝。

正式运行先完成开发集的 22 × 3 = 66 次。保留集保持 8 × 3 = 24 条 `not_run` 记录。基线版本锁定后，在同一结果目录执行：

```powershell
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --split holdout --workers 4 --max-consecutive-errors 4
```

`holdout` 和 `held_out` 等价；`--split all` 包含全部 90 次，每个样例固定重复 3 次。SSE 入口默认开发集、1 个 worker 和连续错误阈值 1；此前并发使用 4 个 worker、阈值 4，最后一个有界单并发探测使用阈值 1。可用 `--env-file <path>` 明确指定环境文件；没有此参数时保留现有环境发现行为。SSE 入口必须显式传入 `--run-dir`，已有非流式身份会被拒绝。**不要使用原非流式 `run_baseline.py` 恢复当前 SSE 目录。**

`--restart-of` 是只读来源证明，不是自动重试或继承结果开关。它要求来源运行没有成功 generation，也没有 `complete`/`degraded` 试验，并在新身份里记录来源路径、report SHA、experiment SHA、旧状态计数和 `inherited_trials: 0`。来源和目标必须是互不包含的独立目录；恢复同一新批次时必须保持相同参数，不能移除或更换该证明。旧请求的远端未知状态继续保留，用户此次继续执行的授权不能使未知结果变成已知。

完整输入试跑使用如下形式；本次 N01 首次试跑已执行，下面是可复现的限额用法，并非要求再次发送已经完成的 trial：

```powershell
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_streaming_baseline.py --run-dir $baselineRun --restart-of $previousRun --split development --workers 1 --max-new-trials 1 --max-consecutive-errors 1
```

`--max-new-trials` 限制本次进程新增调度的 trial 数，不是 HTTP 次数或结构修复次数，也不改变固定 90 条协议。未提交的 trial 保持 `not_run`。正常恢复去掉该限制，已经完成的试跑不会再次请求。

原身份恢复只继续 `not_run`，不会补足已经提交为 `error`/`uncertain` 的重复。未来若需要补做失败重复，应明确建立新的重复批次、来源关联和分析口径，保留原记录，不通过删除记录、改写状态或复制其他传输批次产物达到表面上的三次齐全。当前 `--restart-of` 仅支持来源零成功的关联，不是对已有部分成功批次的通用重试工具。

本轮首先交付基线结果和逐项初审供共同确认，不依据尚未确认的结果反复优化 Prompt。保留集不用于编写示例或本轮反复调参。

## 每次调用的持久化材料

结果目录布局：

```text
experiment.json                  冻结身份、有效配置、逐样例输入和 Prompt 摘要
dataset.json                     独立输入目录和加载器读取的文件清单
report.json                      全部 90 条记录与分开发／保留集结构指标
summary.csv                      可比较的结构／HTTP／耗时／token 指标
trials/<样例编号>/sol-max/<1..3>/
    record.json                  此次提取的原子提交记录
    trace.json                   完整生成 Prompt、响应及每次 HTTP 尝试
    analysis.json                提取输出，包括 CFG、约束、操作和数据引用
    candidate.json               有可解析候选时保存
    graph.mmd                    有通过结构校验的 CFG 时保存
```

每条生成 trace 包含开始时间、耗时、返回模型、request ID、usage 和 HTTP 尝试；每次 HTTP 尝试保留状态码、响应和耗时。`generation_attempts` 是初次生成加结构修复生成的总数，`repair_attempts` 单列额外结构修复数；`http_attempts` 和 `http_retries` 单列传输层尝试与重试。三次重复运行是三条独立 trial，不计入上述两种重试。

SSE 的 `calls[].http_attempts[].stream` 额外保存 `raw_sse`、`wire_sha256`、`received_bytes`、`partial_content`，以及 headers、首字节、首事件、首文本和末事件时间。原始记录继续采用统一密钥脱敏；畸形 UTF-8 的诊断文本使用转义形式。正常结束须同时收到完整 SSE `[DONE]` 事件和 choice 0 非空 `finish_reason`，才聚合为原有 Chat Completion 内容并进入原 pipeline；中间事件和扩展推理字段不会作为候选 JSON 解析。

请求只增加 `stream: true` 与 `stream_options: {"include_usage": true}`，没有修改模型、推理档位、完整 Prompt 或契约。SSE 用量事件可能具有空 `choices`；缺失 usage 保持 null。服务拒绝 `include_usage` 时明确保留失败，不静默移除参数重试。原 180000 ms 参数作为阻塞读取的非活动超时，不是整个生成的绝对截止时间；收到持续事件会延长总耗时，首事件前或事件之间长时间无数据仍可能 524/超时。

每个 worker 只原子更新自己的 trace。主线程在每条 trial 完成或失败后，先原子提交 `record.json`，再更新汇总。`record.json` 是恢复的依据，汇总文件丢失或写入中断不导致重新发送已提交的 trial。输出附有文件摘要；恢复时拒绝已提交产物被修改的目录。

## 中断与恢复规则

服务恢复后，再次执行带相同运行目录和来源证明的命令即可续跑未运行 trial，无需额外 `--resume` 参数。可以改变并发数、每次新增 trial 上限和停止阈值，或从开发集切换到保留集；两次执行共享全部 90 条记录。操作系统文件锁阻止两个 runner 同时写入同一目录，进程退出后锁自动释放。当前没有在线提取进程；将来已有进程运行时，只查看进程输出的进度，不另开第二个写入进程；Windows 在线阶段不要打开活动 report/trace，避免临时文件原子替换的读取句柄冲突。排空后再读取终态报告。

- `complete`、`degraded`、`error` 都是已提交终态。恢复时保留结果，失败记录也不会自动重发。
- 尚未发出的 trial 从 `not_run` 继续。
- 如果 trial 中断，但其 trace 中的生成均有完整响应，则将这些响应重放给同一提取流程；仅确实尚未发出的后续结构修复会继续请求。已成功的生成不会再次请求。
- 若进程中断且未提交 trial，而 trace 中存在无完整结果的请求，恢复时标为 `uncertain`，自动重发被禁用。需要根据 trace 和服务记录判断结果；不能把删除记录后重跑当作无重复保证。
- SSE 已收到 2xx 后发生断流、EOF、超时或协议错误，正常持久化的 trial 为 `error`，trace 的 `stream.outcome` 为 `remote_outcome_unknown`，并保留实际 HTTP 状态、原始 SSE 和残片。该 `error` 表示客户端未获得完整输出，不表示远端确定未生成；它不得自动重发，也不能把残片送入结构修复。收到 2xx 之前的 524 等错误仍沿用既有有限 HTTP 重试。
- Ctrl+C 停止安排后续 trial，已经在请求中的 worker 会完成其持久化流程。直接终止进程可能留下上述 `uncertain` 状态。

推荐使用包外 STOP 文件软停止：

```powershell
New-Item -ItemType File -Path (Join-Path $baselineRun "STOP") -Force
```

默认路径为当前 run 目录的 `STOP`；也可使用 `--stop-file <path>`，但该路径必须在所有 Skill 输入包外。主调度最长每秒检查一次文件是否存在；一旦观察到，就停止新增提交并排空在途 worker，保留其完整响应、既有 HTTP 重试和结构修复流程。它不是取消远程请求，进程不会立刻退出。恢复前可移走该 STOP 文件；若仍存在，恢复命令也不会提交新 trial。

此前 SSE 并发批次显式设置连续 4 条基础设施 `error` 时停止新调度；最后一个单并发探测阈值为 1。SSE 入口默认阈值为 1，可用 `--max-consecutive-errors N` 调整。`degraded` 是模型候选结构失败，不计入该阈值，并重置连续计数。阈值在当前进程内计数，不把已提交旧失败再次计算。阈值触发时已有 worker 继续排空，因此实际错误数可能超过阈值。`report.scheduler` 记录最后一次调用的阈值、STOP 路径、本次提交数和停止原因；并发批次检查点另存 `operation_checkpoints/20260910T112529Z/`。恢复后失败终态仍保留，不会自动重发。

恢复前核对冻结清单摘要、全部输入及生成 Prompt 摘要、有效模型配置、生产与实验代码摘要和运行时版本。任一项改变均拒绝混写既有目录，应另立可区分的实验版本。这也避免把约束字段迁移与后续 Prompt 改动混算为收益。

SSE 身份另外绑定 `tools/stream_transport.py`、`tools/run_streaming_baseline.py` 的 SHA 和传输规则。独立入口在专用进程、worker 创建前选择实验客户端，worker 排空后恢复；没有修改生产 HTTP 客户端。运行期间不得编辑这两个已锁定工具、既有入口或 `src/skill_ir/*.py`。

## 结构通过与语义复核

`complete`、`structural_pass_rate` 和 `first_pass_rate` 只描述结构校验。每条 trial 和汇总的 `semantic_review_status` 保持 `pending_joint_review`，不会因为 CFG 可编译或 pipeline 的 `requires_review=false` 就记为语义通过。外置逐项初审及共同确认必须同时检查关键行为、无依据新增操作、条件、数据来源与去向、约束落点，以及三次运行差异。

SSE 当前七份样例的正式格式初审共 192 个判定：69 `preserved`、31 `partial`、66 `unassessable`、6 `contradicted`、20 `missing`。F02 尚未具备三次终态，不作逐事实判断。`unassessable` 不能当作语义通过，也不能用无完整响应的基础设施失败计算 Skill 理解错误率。实际初审继续等待共同确认，之前不修改 Prompt。

阶段性实际结果使用独立交付模式生成：

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910 --interim-results --output output/pdf/skill-ir-semantics-baseline-sse/skill-ir-baseline-interim-review.pdf
```

`--interim-results` 明确标注基线尚未完成，保留 90 条计划和全部未运行/失败状态，只详列实际尝试及已有充分依据的初审；未满三次的样例不补造事实判定。完整模式要求 90 次结果和 891 项事实运行判断，旧 Sol SSE 批次不满足，而已结束的 DeepSeek 批次已满足。该模式与 `--allow-partial` 的布局预览、`--execution-status-only` 的状态说明分开。本次旧 SSE 阶段性 PDF 为 99 页，已完成全页 110 dpi 渲染和联合视觉检查，重点检查中文、代码、表格、CFG、页码与样例编号；正文空页检查通过，确定性重建 SHA256 一致。外置 QA 记录位于 `output/pdf/skill-ir-semantics-baseline-sse/visual_qa.json` 与 `QA.md`。

`transport_decision.json` 记录采用 SSE 的原因；`transport_audit.json` 记录 N02 第 3 次、N01 第 1 次的请求/响应摘要及四并发本地模拟，未发现本地串写证据，但不能定位服务端原因。两个旧批次、外置初审与所有审计/操作检查点继续保留。

## 聚焦测试

```powershell
python -m pytest packages/skill-ir/tests/experiments/test_resumable.py packages/skill-ir/tests/experiments/test_semantics_resumable_audit.py packages/skill-ir/tests/experiments/test_runner.py -q
python -m pytest packages/skill-ir/tests/experiments/test_semantics_stream_transport.py -q
```

测试使用本地模拟响应，禁止真实网络。覆盖并发、开发／保留划分续跑、成功响应重放、未发修复续跑、不确定请求不重发、已提交失败保留、身份与产物变更拒绝、汇总恢复、结构修复／HTTP 重试区分、输出隔离和密钥脱敏；另外覆盖试跑限额续跑、STOP 排空已有重试、连续基础设施错误阈值、实际解析输入核验与只读重启来源证明。

旧 SSE 阶段最终完整包检查为 `470 passed in 69.66s (0:01:09)`。SSE 测试覆盖中文增量、空 choices 用量事件、结束标记、断流保真、收到 200 后禁止重发、恢复后累计请求数不变、原 pipeline 修复/重放和密钥脱敏；PDF 测试包括阶段性范围、产物完整性及排除页眉页脚后的正文空页拒绝。此处引用已完成的既有测试运行，本次视觉 QA 不重复运行测试。这些离线结果不计入线上 90 次试验，也不证明语义正确。
