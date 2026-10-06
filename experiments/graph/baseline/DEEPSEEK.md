# 官方 DeepSeek V4 Flash 独立基线

2026-09-10，用户明确要求切换至官方 DeepSeek API，并继续被中断的复核。新批次请求 `https://api.deepseek.com/chat/completions`，模型参数为 `deepseek-v4-flash`，`reasoning_effort=max`。使用相同的冻结 30 个 Skill 包、22/8 数据划分、每包 3 次重复、constraints-v2 契约和完整 Prompt。生产 Prompt、IR、编译器、提取流程与已确认的输入不因这次切换而改变。

这是新的模型与服务商基线，共 90 个新 trial。旧 Sol 批次的成功、失败、未知结果及外部复核全部保留；不将它们拼接为 DeepSeek 的 3 次重复。`deepseek_provider_change.json` 保存用户授权摘要、官方文档出处、3 个旧批次的身份和报告 SHA256，以及两次服务检查的证据哈希。实际实验身份还绑定新入口、配置、manifest、SSE 适配器、所有生产 Python 源码、30 个输入及完整 Prompt 的哈希。

官方 `/models` 清单返回 `deepseek-flash` 和 `deepseek-v4-pro`，没有列出请求名 `deepseek-v4-flash`。随后使用精确请求名和 `reasoning_effort=max` 的短测试获得 HTTP 200、`OK`、`finish_reason=stop`，服务端返回模型标识 `deepseek-flash`。因此保留用户指定的请求名，并在每次 HTTP 记录中保留实际返回名。这次短测试位于 `provider_checks/`，与 90 次冻结输入试验分别计数；其已知 44 tokens 不计入基线用量。

官方 [Chat Completions 文档](https://api-docs.deepseek.com/) 与 [思考模式文档](https://api-docs.deepseek.com/guides/thinking_mode/) 于 2026-09-10 核对。`reasoning_effort=max` 受支持，思考模式默认启用；现有客户端不额外发送 `thinking`。SSE 原始文本保留 `reasoning_content`，候选 IR 仅取 `content`，已有适配器保持不变。

## 执行和恢复

以下命令在仓库根目录运行。密钥通过本地根 `.env` 的 `LLM_API_KEY` 读取，不写入 Skill 包、实验配置、Prompt 或报告。新配置显式固定 endpoint、model、reasoning、超时、HTTP 重试与结构修复轮数，避免环境中残留的旧模型设置影响实验。

离线检查不读取密钥或 `.env`，不发起网络请求，也不创建运行目录：

```powershell
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_deepseek_baseline.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910 --split all --check
```

首次执行一个完整 Skill 输入，验证真实响应、SSE 完整性和原生产管线：

```powershell
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_deepseek_baseline.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910 --env-file .env --workers 1 --max-new-trials 1
```

在相同身份下继续全部剩余 trial；已经结束的第一次试验不会重复：

```powershell
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/run_deepseek_baseline.py --run-dir packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910 --env-file .env --workers 4 --split all
```

若分开执行，默认 `--split development` 对应 66 次；`--split held_out` 对应另外 24 次。无论调用选择哪个子集，身份和报告始终保留全部 90 个 trial 的计划。正式结果需在全部 90 次结束后进行 297 条外部事实 × 3 次的独立复核；生成候选 CFG 和结构验证通过均不代表语义正确。

程序每次恢复都验证固定身份，不改变已经结束的记录。新入口拒绝将输出写进 `frozen/`、3 个旧批次或其它 provider 的运行目录。身份匹配的同批次只会执行 `not_run`；HTTP 200 后不完整的流记录为远程结果未知，不自动重发。需要停止时，在运行目录创建 `STOP` 文件，调度器停止新增任务并等待在途请求结束；恢复前检查原因并移走该文件。默认连续 1 次基础设施错误触发停止新增，已在运行的任务仍会排空。

重试与结构修复保持原设置：HTTP 超时 180000 ms，最多 2 次 HTTP 重试，退避基础值 500 ms、上限 8000 ms；最多 3 轮候选结构修复。SSE 的超时按无数据等待时间计算，持续收到数据时，总生成时间可以超过 180 秒。所有收到的流片段和用量、请求名与返回名均由记录保留；没有完整结束标记的响应不会作为有效候选继续处理。

## 本地验证

新增 `tests/experiments/test_semantics_deepseek_baseline.py` 的 16 个测试在完全禁用真实网络的条件下通过，覆盖以下边界：

- 30 个冻结输入及原始完整 Prompt 的身份一致，外部事实标注不进入模型输入；全部 90 次重复计划保留。
- provider 参数显式覆盖残余环境设置；模型、endpoint、reasoning 或重试设置漂移会被拒绝。
- 拒绝冻结目录、旧批次及其它实验身份；旧报告、旧身份和认证证据篡改会被发现。
- DeepSeek 风格的思考流不会污染候选内容，返回别名和用量进入真实记录结构。
- 本地模拟下，相同身份恢复从下一次重复继续，已完成记录字节不变，密钥被脱敏。

```powershell
python -m pytest packages/skill-ir/tests/experiments/test_semantics_deepseek_baseline.py -q
```

测试通过证明实现边界和兼容行为。在线执行状态、有效 CFG 数与事实复核判断以该 DeepSeek 批次的 `report.json` 和外部复核文件为准。

## 本次执行检查点

最小官方调用返回 HTTP 200、`OK`，用量为 44 tokens；它不属于 90 次语料基线。
首个完整 N01 输入用一次生成取得有效 CFG，0 次结构修复、0 次 HTTP 重试，
耗时约 100.99 秒。之后先使用 4 个 worker；在
`operation_checkpoints/20260910T135610Z/` 排空保存了 17 条终态
（16 `complete`、1 `error`）及 73 条 `not_run`，并导出 N01–N05 的复核材料。
下一段采用 8 个 worker、最多新增 27 次，以便在再次排空后导出更多复核材料。
并发度与调度限制保存在每次检查点；有效模型、推理档位和每次试验的语义身份不变。

N01 第 3 次的失败是本地 Windows 临时文件替换 `trace.json` 时出现
`WinError 5`。SSE 层把该异常包装为网络失败，但这一记录本身不能证明
DeepSeek 服务失败。收到 HTTP 200 后未取得完整结束，故仍保留原始
`error` 与 `remote_outcome_unknown`，不重发、不伪造有效结果。
具体锁持有者未确定；此前读取活动日志可能产生冲突，不能认定为已证实原因。
在线阶段只查看运行进程的进度输出，不打开活动 `report.json` 或 `trace.json`。
需要事实复核时，先软停止并排空，再读取和导出不可变的终态材料；继续运行时
仅消费已导出的复核包。不要用可能保持文件句柄的实时预览器打开活动日志。

DeepSeek 入口与此前代码的全套离线验证为 **486 passed in 152.72s**。
其后 PDF 运行身份展示的独立检查为 38 项通过；两者有重叠，不能相加。

第二段 27 次在聊天中断期间正常排空，检查点 `20260910T141043Z/` 累计 39 `complete`、5 `error`、46 `not_run`。新增四条错误均已收到 HTTP 200，但流结束前发生 `IncompleteRead`，用量未返回；来源无法定位到服务端或中间网络。随后用户要求继续，保持同一身份，以 4 个 worker 再执行 28 次，完成后计划仅余六份真实包的 18 次。


## 最终执行记录

第三段在 `20260910T142626Z/` 检查点排空，24 份控制样例的 72 次全部终态：67 `complete`、5 `error`。随后按同一身份、4 个 worker 执行最后 18 次真实包提取，全部取得结构有效结果；最终检查点为 `20260910T144548Z/`。运行器已退出，没有未运行或在途 trial。

| 记录 | 全部 | 开发集 | 保留集 |
| --- | ---: | ---: | ---: |
| 计划 / 已执行 | 90 / 90 | 66 / 66 | 24 / 24 |
| 结构有效 | 85 | 62 | 23 |
| 失败 | 5 | 4 | 1 |
| 生成尝试 | 104 | 76 | 28 |
| 结构修复 | 14 | 10 | 4 |
| HTTP 尝试 | 104 | 76 | 28 |
| HTTP 重试 | 0 | 0 | 0 |
| usage 记录 | 99 | 72 | 27 |
| 已知总 tokens | 3,526,952 | 2,531,501 | 995,451 |

已知输入 803,598 tokens、输出 2,723,354 tokens。缺失用量仍为 null，合计不是完整费用记录，不含 44 tokens 的预检，也不含旧 Sol 批次。所有五条失败仍为 `error`，其 HTTP 200 后的远端状态保持 `remote_outcome_unknown`，不会以重发或复制结果补成成功。

失败分别是 N01 第 3 次的本地 Windows trace 替换异常，以及 Q03 第 2 次、F02 第 3 次、F03 第 1/2 次的 SSE `IncompleteRead`。本地异常不能归咎于 DeepSeek；其余断流也不能仅凭客户端记录定位到服务端或中间网络。

最后全包离线测试为 **514 passed in 64.74s**，包括冻结及输入/标注隔离、独立 provider 身份、恢复与失败保留、外置事实初审完整性、结果 PDF 来源绑定，以及脚本行数组的摘要展示边界。随后只修改 PDF 的短终结操作分页，并运行分页相关聚焦回归：`python -m pytest packages/skill-ir/tests/experiments/test_semantics_result_integrity.py -q`，**29 passed in 1.22s**；没有再次运行全包测试，两次结果不相加。这些测试不发起真实 API 请求，也不作为语义通过结论。

结果复核保持 297 条冻结事实 × 3 次 = 891 项，逐条绑定本批次实际输出和记录的 SHA256。使用以下命令离线校验并重建完整结果 PDF，不调用远程 API：

```powershell
$deepseekRun = "packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910"
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/review_results.py --run-dir $deepseekRun --check
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --run-dir $deepseekRun --variant deepseek-v4-flash-max --output output/pdf/skill-ir-semantics-baseline-deepseek/skill-ir-baseline-results.pdf
```

PDF 构建需要 ReportLab、pypdf 及生成器所列字体；本次使用 bundled Python 3.12、ReportLab 4.4.9 与 pypdf 6.10。完整计划终态与完整初审允许展示 5 条失败，不表示取得 90 份有效 CFG，也不表示用户已经共同确认模型结果。本轮 90 次在线试验已经结束，当前没有在线任务；生产 Prompt、IR 模型和提取 pipeline 本轮均未修改，也没有依据保留集调整 Prompt。最终 PDF 已完成分页修正、确定性重建和联合视觉检查；模型结果及初审意见仍待用户共同复核。

结果册位于仓库根目录下 `output/pdf/skill-ir-semantics-baseline-deepseek/skill-ir-baseline-results.pdf`，最终重建为 **730 页**：第 **1–168 页**为概览及逐事实初审，第 **169–172 页**为附录索引，第 **173–730 页**为实际 CFG、边条件及全部操作明细。连续两次重建的 PDF 字节与来源清单一致，PDF SHA256 为 `d7e800a17608180900afc0f2cded045c2738e6d514ac89a2eb21313155f126ed`。全册已按 110 dpi 渲染；机器内容检查见同输出目录的 [content_qa.json](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/content_qa.json)。704 页以页脚页码数字之外的像素一致性承接既有视觉检查，26 个变化页全部完成全尺寸补验，联合视觉检查覆盖全部 730 页，未发现阻断交付的视觉缺陷；最终证据见 [QA.md](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/QA.md) 和 [visual_qa.json](../../../../output/pdf/skill-ir-semantics-baseline-deepseek/visual_qa.json)。
