# 方案后续步骤执行状态

官方 DeepSeek 独立批次 `baseline-deepseek-v4-flash-max-20260910` 的 90 次计划已全部执行结束：**85 `complete`、5 `error`、0 未运行**，当前没有在线进程。请求模型为 `deepseek-v4-flash`、推理档 `max`，HTTP 返回名称保留为 `deepseek-flash`。5 条失败保持原状，批次状态因此为 `failed`；结构有效不代表语义通过。当前复现入口、统计和隔离规则见 [DEEPSEEK.md](DEEPSEEK.md)，最终执行检查点为 `operation_checkpoints/20260910T144548Z/`。下文 Sol 数据均为历史记录，与新模型分别保存。 本批次发现与后续处理顺序见 [RESULTS.md](RESULTS.md)。

日期：2026-09-10。

本轮生产 Prompt、IR 模型和提取 pipeline 均未修改。最后全包离线测试为 **514 passed in 64.74s**；随后仅对 PDF 分页修正运行相关聚焦回归，**29 passed in 1.22s**，不将两次计数相加。30 份外置初审、891 项事实运行判定已校验完成；最终结果 PDF 为 **730 页**，确定性重建、全量 110 dpi 渲染及联合视觉检查均已完成，证据见 [QA.md](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/QA.md) 和 [visual_qa.json](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/visual_qa.json)。以下旧批次的测试与未完成状态保留为历史记录；新基线模型结果和初审意见仍待用户共同复核。

**旧 Sol 批次因上游服务失败未完成 90 次基线，旧批次已经停止。** 主要 SSE 批次 `runs/baseline-sol-max-sse-20260910/` 已提交 23 次试验，其中 14 次结构有效、9 次失败；67 次未运行。并发批次自动停止后等待数分钟，单并发 F02 第 2 次仍遭上游断流，因此停止追加请求，转为交付真实阶段性结果供共同复核。

## 已完成

1. 用户共同确认已记录在 `approval.json`。206 个文件的冻结清单包含 30 份样例、297 条事实、原生产实现及原 Prompt、原候选 Schema、30 份原始实际 Prompt 和已审 PDF。22/8 划分与每份 3 次协议不变。全部 82 个 Skill 输入字节不变。
2. 已独立实现约束契约 v2，六个候选/IR 模型的 Skill、块、操作层级具有 `constraints: list[str]`。原 Prompt 只追加契约段及自动 Schema 字段，两份示例未改。迁移差异验证通过，不计作 Prompt 优化收益。
3. 已实现固定 90 条试验、有限并发、原子落盘、断点恢复、成功响应离线重放和未知请求不重发。实际输入、Prompt、配置和实现摘要绑定运行身份。结构修复与 HTTP 重试分别记录。
4. 已实现外置逐事实初审导出与校验，以及正式结果复核 PDF 生成器。正式模式要求 30 份初审、297 x 3 个判定与对应真实产物摘要一致；没有足够结果时拒绝生成完整结论。
5. 旧 SSE 阶段最终完整包检查为 `470 passed in 69.66s (0:01:09)`。覆盖冻结清单、契约最小差异、实际输入/Prompt 隔离、SSE 结束与断流规则、产物完整性、阶段性 PDF 范围，以及排除页眉页脚后的正文空页拒绝。该既有离线测试结果不作为线上运行完成或语义正确的证明。
6. 继续执行前补齐了每次新增 trial 限额、包外 STOP 软停止、连续基础设施错误阈值和实际解析输入二次校验。实际调度前核对 frozen/corpus 样例路径、完整源文件集合与摘要、规范化输入摘要，禁止 dataset 重定向。这些是实验执行控制，没有修改 Prompt、IR、编译器、提取 pipeline 或 HTTP client。
7. 新增独立 SSE 实验工具与入口，在专用进程中复用原 pipeline、结构修复和持久化逻辑。原始 SSE、片段、事件时间、用量和结束标记进入 trace；传输工具摘要与重试/超时规则绑定新身份。未修改生产 client，未混入非流式运行结果。

测试使用本地模拟响应，不计入线上基线试验，也不证明模型语义正确。

## SSE 部分批次已停止

目录：`runs/baseline-sol-max-sse-20260910/`。请求使用 `https://xiaomuai.cn/v1/chat/completions`、`gpt-5.6-sol`、`max`；HTTP 超时 180000 ms、最多两次额外 HTTP 重试、最多三轮结构修复均保持原配置。仅新增 SSE 传输参数，没有更换服务、模型、推理档位、完整 Prompt 或契约。

| SSE 实际记录 | 数量 |
| --- | ---: |
| 计划提取 / 已尝试 | 90 / 23 |
| `complete` / `error` / `not_run` | 14 / 9 / 67 |
| 开发集未运行 / 保留集未运行 | 43 / 24 |
| 生成 / 结构修复 | 29 / 6 |
| HTTP 尝试 / HTTP 重试 | 34 / 5 |
| 返回用量记录 | 20 |
| 已知输入 / 输出 / 总 tokens | 109,042 / 102,395 / 211,437 |

9 条 `error` 均发生在收到 HTTP 200 之后，trace 保留 `remote_outcome_unknown`、原始 SSE 和事件时间。未返回的用量保持 null，211,437 只是已知用量合计，不保证涵盖失败请求的远端消耗；不能把缺失字段算成 0。全部保留集 24 次仍为 `not_run`。

完整 N01 的 SSE 试跑收到 HTTP 200，首 headers、字节及事件于 10:52:28 UTC（北京时间 18:52:28）开始到达，总耗时约 341.25 秒，经 3 次生成、2 次结构修复、3 次 HTTP 尝试且无 HTTP 重试，提交为 `complete`。这只说明该 trial 的流式请求与结构流程交付了有效产物，不证明样例语义正确或后续请求全部稳定。开发集续跑于 11:01:17 UTC（北京时间 19:01:17）在同一 SSE 批次以 4 个 worker 启动，原试跑记录保留，没有重发。

并发执行中观察到 SSE 仍遇到上游故障，例如 N02 第一次收到 HTTP 200 和中间事件后，服务返回 `upstream_http2_stream_error`，没有完整内容、`[DONE]` 或 choice 结束状态。并发批次随后达到连续错误阈值并排空 worker；检查点保存在 `operation_checkpoints/20260910T112529Z/`。等待数分钟后仅新增一个单并发 F02 第 2 次探测，仍因上游断流失败，因此没有继续提交剩余任务。SSE 缓解长时间没有中间响应的问题，并未消除上游错误；这不能由一次试跑成功推断。

新执行器摘要与旧运行不同，因此使用独立目录。`--restart-of runs/baseline-sol-max-v1` 将旧 report、experiment 的 SHA 及状态计数写入新运行的 provenance，要求旧运行无成功 generation 和有效/降级结果；继承 trial 数为 0。旧日志只读保留，远端未知请求仍为未知。这是用户授权后的新执行，不是删除旧记录后伪装成没有发生过请求。

`runs/baseline-sol-max-sse-20260910/transport_decision.json` 另外关联已结束的非流式重试批次及报告 SHA，说明这次调整只针对传输可靠性，逐样例输入和 Prompt 摘要、模型/推理配置及生产源码均保持不变。非流式重试已有成功输出，不符合 `--restart-of` 的零成功限制，因此来源证明继续指向原始无成功批次，非流式重试关联由该外置决策记录承担。

未来服务恢复后的未运行续跑命令见 `RUNNING.md`，使用 `tools/run_streaming_baseline.py`，必须显式指定 SSE `--run-dir` 并保留同一 `--restart-of`。`--max-new-trials 1` 仅限制一个尚未运行的 trial，不重发失败终态。此前并发阈值为 4，最后的单并发探测阈值为 1；`report.scheduler` 记录最后一次调用，较早检查点另存。STOP 文件可让主调度每秒检查并停止新增提交，排空在途 worker 及既有重试。

SSE 正常接受必须同时具备完整 `[DONE]` 事件和 choice 0 非空结束状态。收到 2xx 后断流/超时/协议错误的 trial 为 `error`，但 trace 中 `calls[].http_attempts[].stream.outcome` 为 `remote_outcome_unknown`，保留原始 SSE 和残片且不得自动重发；残片不送入结构修复。180 秒为阻塞读取非活动超时，持续事件可能延长总耗时，完全无 SSE 时仍可能超时或 524。进程中断且未提交的请求由既有恢复逻辑标为 `uncertain`，与上述已正常提交的 `error` 分开记录。

旧 Sol 批次已无在线进程。原身份仅能继续 `not_run`；要补足失败重复，未来必须明确建立新的重复批次和来源关联，不覆盖 `error`/`uncertain`，不删除日志，也不从旧传输批次复制结果。既有 `--restart-of` 只适用于来源零成功的关系，不能伪装成对已有成功批次的结果继承。

`transport_audit.json` 已绑定实际 N02 第 3 次及 N01 第 1 次的 record/trace、请求体和响应摘要，确认四轮请求/响应在本地对应，四并发模拟调用无串写且远程调用为 0。该有界审计没有发现本地并发串写证据，不能定位服务端原因或据此声称 provider 串包。全部锁定代码、两个旧批次、审计和操作检查点继续保留。

## 已有初审与阶段性 PDF

N01–N06、F01 七份 SSE 样例已具有三次终态并完成正式格式初审，共 192 个事实运行判定：

| 判定 | 数量 |
| --- | ---: |
| `preserved` | 69 |
| `partial` | 31 |
| `unassessable` | 66 |
| `contradicted` | 6 |
| `missing` | 20 |

这些是外置初审，不是用户已确认的模型结论。66 个 `unassessable` 不能计为语义通过，也不能按基础设施失败推断 Skill 理解错误。F02 未满三次，不作逐事实判断。

本次交付 `output/pdf/skill-ir-semantics-baseline-sse/skill-ir-baseline-interim-review.pdf`，以 `--interim-results` 生成明确未完成的真实阶段性材料，保留 90 条计划、未运行与失败状态，仅详列实际尝试、充分依据的初审及真实 CFG。复现命令：

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-sol-max-sse-20260910 --interim-results --output output/pdf/skill-ir-semantics-baseline-sse/skill-ir-baseline-interim-review.pdf
```

这份阶段性 PDF 不替代完整结果模式。完整模式仍要求 90 次结果及 891 项逐事实判定齐全，不能降低要求来宣称基线完成。`--allow-partial` 仅供布局预览；旧 `--execution-status-only` 报告只说明旧中断批次。交付 PDF 已生成 99 页，并完成全部页面的 110 dpi 渲染及联合视觉检查；另放大检查中文、代码、密集表格、CFG、页码和样例编号。两张正文空白页与孤立索引页已修正，确定性重建 PDF 字节摘要一致。外置 `output/pdf/skill-ir-semantics-baseline-sse/visual_qa.json` 和 `QA.md` 记录检查范围与摘要。

## 已结束的非流式重试批次

目录：`runs/baseline-sol-max-retry-20260910/`。完整 N01 试跑曾返回有效结构结果，但继续并发后反复出现 HTTP 524、180 秒读取超时及连接关闭。写入 STOP 后已排空在途 worker，原记录均保留。

| 该非流式批次实际记录 | 数量 |
| --- | ---: |
| 已提交终态 | 13 |
| `complete` / `error` / `not_run` | 4 / 9 / 77 |
| HTTP 尝试 / HTTP 重试 | 40 / 24 |
| 生成 / 结构修复 | 16 / 3 |
| 已知输入 / 输出 / 总 tokens | 42,092 / 23,203 / 65,295 |

这些是该已结束部分批次的记录，不是当前 SSE 批次的最终统计。缺失用量仍为 null，已知 token 合计不保证涵盖失败请求的远端用量。N01–N04 的 `reviews/` 中四份正式格式初审包含 108 个逐事实判定，另有 `review_drafts/N05-run-1.json` 局部草稿；它们只审阅各自绑定的非流式产物，不代表共同确认，也不能替换或合并 SSE 的三次重复。

## 旧批次故障与保留记录

运行目录：`runs/baseline-sol-max-v1/`。请求配置沿用既有 `https://xiaomuai.cn/v1/chat/completions`、`gpt-5.6-sol`、`max`；每次 HTTP 超时 180000 ms、最多两次额外 HTTP 重试，结构修复上限仍为三轮。没有擅自切换服务、模型或降低推理档位。

开发集首批并发请求持续出现 HTTP 524 和网络超时后，批次被中断。进程退出后使用 `tools/reconcile_interrupted.py` 持有独占锁离线对账，保留原 trace，未补发请求。

| 实际记录 | 数量 |
| --- | ---: |
| 计划提取试验 | 90 |
| 开始的提取/生成会话 | 4 |
| HTTP 尝试记录 | 12 |
| HTTP 524 | 3 |
| 网络读取超时 | 5 |
| 中断后远端结果未知 | 4 |
| HTTP 重试 | 8 |
| 结构修复 | 0 |
| 完整模型响应 / 已接受 CFG | 0 / 0 |
| 不确定试验 / 未运行试验 | 4 / 86 |

受影响试验为 N01 的三次及 N02 第一次。旧批次保留集的 24 次均未开始。旧 `report.json` 状态为 `needs_attention`；`reconciliation.json` 及带时间的审计副本锁定全部 90 个 record 和 4 个 trace。中断精确时刻未记录，保存为 null；对账观察时间有实际记录。上述表格只说明旧批次，不能与新批次累计为一次 90 条协议结果。

旧批次用量没有返回，token 字段保持 null，不能解释成零用量。报告器的通用结构完成比例此时仅反映没有交付有效 CFG；由于没有返回候选，**不能据此判定模型的结构或语义通过率为零**。旧批次没有可用于逐事实初审的输出，新批次的真实产物将在各样例三次结果齐备后逐项初审。

## 当前剩余步骤

- DeepSeek 的 90 次试验、全部 891 项事实运行初审与三次差异分析均已完成；730 页最终结果 PDF 的分页修正、两次确定性重建、全部页面视觉检查和交付证据登记均已完成。
- 新基线的模型结果及外置初审仍待用户共同复核。旧 `--execution-status-only` 和 SSE 阶段性 PDF 仅说明各自旧批次，不能代替 DeepSeek 完整结果册。
- 本轮没有修改生产 Prompt、IR 模型或提取 pipeline，没有用保留集反复调参。后续 Prompt 修改须在结果共同确认后仅依据开发集推进，语义回溯阶段尚未开始。

当前没有在线任务，不会自动重放五条失败。若后续补测，应另建有来源关联的补充批次，保留本次终态记录。旧 Sol 批次仍保持未完成的历史状态，其未运行或失败重复不混入已执行完毕的 DeepSeek 基线。
