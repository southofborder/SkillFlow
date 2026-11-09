# SkillFlow research and conversation handoff

Current status (2026-11-09): the main worktree contains the accepted interface-r4
implementation and the completed November 4 four-case validation. Start with
[Current version](current-version.md). All four generated graphs propagated and
all four sole zero-call replays matched; DOE remains partial. Reports are in
`output/verification/online-interface-r4-20261104/`. Its heartbeat is deleted;
old v9 remains paused. The user now authorizes Git organization, commit and push,
with no new model/Skill/experiment/replay runs and no import of the old external
`SkillFlow-staged` code. The dated launch notes below are preserved history.
Publication scope and the local historical-file inventory are documented in
[Repository publication](repository-publication-20261109.md); a remote checkout
of selected reports is not a complete replayable archive of all local runs.

The user subsequently added the three usual small Skills to this active task:
001 conditional-notification,010 catalog-query,013 source-fetch-with-fallback.
Fresh directories and exact source hashes are in
`output/verification/general-loops-v8-online-20261101/small-queue.json`.
One queue supervisor will launch them sequentially after GA4 closes; consult
queue-started.json/queue-live.json, never independently launch a queued case.
Same High model/version/two workers and fresh generation, one zero-call replay
per case, no history migration or answer imports. All four reports are pending.

Current new authorization (2026-11-01): one fresh full GA4 general-loops v8 run,
`experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322`,
gpt-6.1-sol/high/openai, the same 16 frozen files, two workers, seven normal requests.
Root is sole controller owner. Read its controller markers and
`output/verification/general-loops-v8-online-20261101/continuation-state.json`.
Do not start a duplicate, modify prompts/source during execution, run a probe,
execute the Skill or resume a historical run. After closure perform one zero-call
replay and source-grounded coverage/correctness/cost reporting. Current source
SHA a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b differs
from offline acceptance only in standalone graph-audit output guidance unused
by the guided request sequence; focused prelaunch checks are recorded separately.
The 2026-10-29 offline-only permission below is superseded for this one run only.


当前工作（2026-10-29）：通用循环与输出契约精简 v8 的实现和离线验收已完成，去重后 3,893 项通过、1 项 Windows 符号链接权限跳过、无未解决测试失败。初批失败与复测逐项保留，不能称为一次全仓绿色运行。最终实现 SHA 为 `fa02488dc9d01435b747284e0fa8f27ef9f1bea834e07cb6ade83230fc325a5b`。正常七调用、两个 worker 和隔离保持；七份模拟答复完成传播、DOE 与零调用重放，另有失败重放和独立配对复核。本轮没有新的真实分析模型调用，未执行 Skill 或续跑旧实验。报告见 `docs/doe/general-loops-v8-offline.zh.md`，设计见 `docs/doe/general-loop-analysis.md`，验收目录为 `output/verification/general-loops-v8/`。精确累计数组、多代关联与全局资源边界仍保留；真实速度／准确性未测。旧 v7 的 664 个原始文件字节核对通过。后续真实新运行需要新的用户指令。下列真实运行状态均为封存历史。
最新运行已关闭（2026-10-29）：`experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749`。
北京时间 10:18:12 启动、12:29:55 主分析结束、12:55:45 控制器关闭；PID 6528 已退出（exec session 4868）。
配置为 gpt-6.1-sol/high/openai、两个 worker、正常七请求。主分析耗时 7902.34070 秒，状态 failed，未生成 DOE。
选用图为 106 blocks／262 IR；批处理游标递增 ir_214 形成数据生成回边，传播返回 unsupported_feedback，全部 262 IR 为 not_solved。
DOE 随后报 `Demand collection output has no recorded member scope`，没有提交 doe-result.json。不得把零传播记录读成零暴露。
选用 processing 有 197 modeled、59 源文 unmodeled、6 个结构纠正后隔离的 IR；复审仍有 3 条 processing 问题。
两次审查均正常完成，实际提交 636534／768678 字符，输入容量已不是本轮阻断。
17 次 CLI 启动＝7 正常＋5 共享修复＋5 结构纠正；公开 tokens 为 2184745（input 1802022，其中 cached 288768；output 382723）。
外层传输重试 0、最终响应 usage 缺失 0；provider 内部 HTTP 次数未知。传播重放 matched；唯一一次全流程重放 failed，
原始错误为 `Replayed guided decisions differ from saved results`，耗时 1549.34942 秒、0 新请求。失败重放收据保留，不另跑覆盖。
详见本轮 `assessment.en.md`、`run-summary.json`、`metrics.json`、`replay-check.json`。完整源文与实现保持不变。
实施与离线验收已完成；485 个去重案例覆盖，主批次的一处旧示例视图兼容问题已修正并单独复测通过。
见 `docs/doe/compact-review-v7-offline.zh.md` 与 `output/verification/compact-review-v7/offline-acceptance.json`。
实现 SHA `8a7dfb5f2c1dc4d03aa4778816aaa3cf4e0118d0ba373dcc70d35c780c687d78`；同一完整 16 文件源包，
source SHA `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`。新目录归档实现与 transport。
新视图只从模型输入移除展开定位表与机械归属表；源文和语义材料保留。各生成阶段自查，不增加模型调用。
明确审查请求失败允许合法候选进入诊断计算，仍标记未审查；不掩盖工程错误，不增加自动切片。
本次单轮运行授权已用完，不再启动控制器、续跑、第二次重放或新增探针；后续修改或新运行依据新用户任务。
读取本轮 controller-finished 与报告，不把历史阶段标记误当作仍在生成。总交接状态在 `output/verification/compact-review-v7/continuation-state.json`。
下面 v5/v6 等记录是封存历史，不是当前运行进度。v6 于 2026-10-29 凌晨因审查输入超限结束，未执行传播/DOE，
其原始失败重放保留，未续跑。

当前真实运行（2026-10-28）：用户要求实施后新建一轮完整 GA4 运行，首先确认能否得到完整 DOE。
该轮现已结束：北京时间 19:46:33 主分析结束（78 分 8.21 秒），19:54:15 完成重放和收尾，PID 已退出。
最终 partial，未得到完整 DOE：126 IR 中 8 processed、2 unmodeled、116 blocked；已知 13 接收位置中
5 resolved、8 unresolved；14 条比较全部因限制未建立 excess，不能读成安全。最终审查保留两个
task-correspondence 语义错误（whole child response 和 summary whole input 被误当作全部必要）。
17 次实际 CLI 请求＝7 正常＋6 共享修复＋4 结构纠正；公开用量 1757935 tokens，另有一条 CLI 内部
timeout reconnect，未上报内部失败尝试用量未知，不能说完全无网络重连。重放 matched、0 新模型调用，
实现 SHA 保持 27c96e...835d8。该目录 assessment.en.md、run-summary.json、outcome-audit.json 为交付证据；
不续跑、不自动新增实验，后续修改须依据新的用户任务。
唯一目录为 experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527，
北京时间 18:28:25 启动，controller PID 38940；原 exec session 回执未保留于压缩交接，按文件和 PID 观察。
使用 gpt-6.1-sol/high/openai、两个 worker、正常七请求、一次共享语义修复、每阶段一次结构纠正。
完整冻结输入 16 files / 155170 bytes，source SHA 3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd；
实现 SHA 27c96eafa74c9c1f957df4116369198981f72833dd69d28b18ded84bf4c835d8，原实现和 transport 工具已归档。
不要开第二个控制器、修改目标提示或代码、续跑旧轮、执行 Skill。继续时读取该轮 continuation-state.json、
controller-started/finished、result.json 及实际本地进程，不用旧轮进度。控制器结束后自动汇总被动 metrics、
尝试零调用 replay，再由 root 核对传播／需求／敏感性和接收边界覆盖，生成英文 assessment 与中文交付。
没有新增模型环境确认或模型监控；本地 CLI help 和 renderer 路径检查均为零目标调用。

当前实施（2026-10-28）：文档入口已转为七次语义请求与程序组装 annotation。
processing、任务对应、敏感性各自产出带类型片段，不再调用模型重填整份标注；
独立 Task、并行及末尾源文审查保留。新协议 run/step/annotation 为 v5，
仅适用于新运行。局部未建模对象保留覆盖，停止相关 block OUT，独立分支继续；
Task 全局语义缺口保持原有政策，不新增通用缓存／异常执行器。
当前授权仅为实施和离线验收，真实模型调用为零；下面的八调用运行与失败保持历史身份。
见 [当前设计](doe/document-guided-analysis.md)；验收结论在七调用离线报告中单列。

2026-10-27 22:36 新运行：用户明确要求新建 GA4 八调用真实运行，使用 gpt-6.1-sol/high/openai。
当前唯一目录为 `experiments/doe/runs/document-guided-ga4-eight-call-high-v4-20261027-223547/`；
完整 16 文件源包与旧轮字节一致，Task/CFG/答案重新生成。此授权覆盖本次新运行及本地监控，
不授权续跑旧实验。默认配置仍为 max；high 在 prepare 时封存，不可在 run/replay 改档。
继续时先读该目录 `continuation-state.json` 与实际 controller/result 文件；不要启动第二个控制器。
监控不请求模型，完整/局部/未知用量分开。该轮已于 23:42 结束：cannot_assess，无 accepted
annotation、propagation 或 DOE。18 次 native 请求（8 正常 + 7 共享修复 + 3 结构纠正），
无传输重试；分析墙钟 3956.43 秒，完整公开回执 1,525,001 tokens，18/18 用量完整。
初始标注报告循环内共享客户端缓存写入能力限制；修订标注两份草稿仍不合法，最后为
source-only sensitivity/expression evidence 继承错误，且诊断无具体 JSON pointer。
末次部分复审还保留 .env 设置写入及 index 导入控制关系问题。零调用重放精确匹配，新增 native 0。
详见该目录 assessment.en.md、run-summary.json 与 metrics.json。不要自动重试或改写本次失败。
用户随后要求下一轮取消全局 cannot_assess 退出，并质疑当前工程复杂度；下一轮应要求交付
可分析部分、将未知定位到局部，不能用强制填满替代诚实的不确定性。本轮结果保持冻结。

2026-10-27 八调用收口：当前文档入口为 run/step/annotation v4，两个 worker 按依赖并行，
一份 flow、一份完整 CFG、扁平完整 annotation、稀疏统一源文审查。Task、任务对应与敏感性
隔离保持。为解决 GA4 的真实能力失败，单层 for_each 支持逐项 read/receive/call 及
yield/output 映射集合；不支持共享写入、嵌套循环或通用异常执行。正式入口不需要
confirm/preflight、profile 或 usage 回执，监控不调用模型。见
[当前设计](doe/document-guided-analysis.md)。本次仅实施与离线验收，不新增线上运行。

当前交接（2026-10-27）：目的依据仅为完整冻结 Skill，独立 Task 不接收外部任务；Skill 自身的用户交互、运行参数和输入仍参与分析。Task v5 删除固定依据标签与独立请求摘要，继续保留原文依据、冲突和版本身份。[文档引导式入口](doe/document-guided-analysis.md)采用继承短文档的独立请求，最终只有一份完整 CFG 和标注。本轮仅收口与离线验证，不继续旧实验或调用模型。

Experiment configuration update (2026-10-26): newly prepared GPT-6.1 Sol experiments use `max` instead of `ultra`, in both SkillFlow and direct-analysis arms. Frozen requests, receipts, results and stopped runs retain their original effort; do not resume them with a changed configuration or relabel them as Max runs. The hash-pinned legacy CLI-v2 adapter remains unchanged for historical verification; current CLI-v3/controlled entry points use Max. This change does not authorize model calls or experiments.

2026-10-24 的工作文档设计已由上述入口替换，业务分组和分批拼接不是当前流程。逐行 Task／审查表已经删除；真实文件与物理行引用仍严格校验。下面的日期性实验、提交及材料清单保留为历史交接记录，不代表当前运行状态或新增实验授权。

Updated: 2026-10-21. This is a structured reconstruction of the research discussion
and a read-only inspection of repository evidence, not a verbatim chat export,
an experiment authorization, or a claim that every local file has been uploaded.

## 1. Start here on the second computer

The user has chosen **GitHub plus a local checkout and this handoff**. Creating a
Codex Cloud environment is paused after unsuccessful setup attempts. No usable
Cloud environment or Linux Cloud verification has been established. The current
research pipeline is frozen for comparison: do not keep tuning prompts, redesign
the protocol, acquire more evaluation inputs, or dispatch model calls merely to
continue this handoff.

The 2026-10-21 submission request covered two tracked research files, this
handoff and a fast-forward of `codex/cloud-setup` into `main`. That historical
authorization excluded billing files and did not authorize experiments.
The package version `0.1.0` is not a research snapshot identifier; record the exact
Git revision with `git rev-parse HEAD`.

Read in this order:

1. [Repository instructions](../AGENTS.md) and this handoff.
2. [DOE goal baseline](doe/SkillFlow-DOE目标与设计原则.md).
3. [Current formal pipeline](doe/joint-pipeline.md).
4. [Constraint implementation and limits](doe/constraint-implementation.md).
5. [Comparison protocol and tools](../tools/doe/real_comparison/README.md).
6. [This submission's verification](research-handoff-verification.md) and
   [local-only material inventory](research-local-only-inventory.json).

The goal document establishes the research objective; its earlier introductory
version descriptions do not override the later constraint implementation.
Frozen reports describe their own runs, not the status of a newer implementation.

## 2. Research objective and unresolved contribution question

SkillFlow studies **task-related static data minimization for Agent Skills**.
It combines sensitive information, processing relationships, path conditions and
recipients to find unnecessary sensitive exposure. Both unnecessary actions and
surplus sensitive payloads inside necessary actions are in scope. A required
action does not make every carried value or sensitive field necessary.

An exposure boundary, a sensitive label, or a task-required action alone does not
establish DOE. The coverage objective is all unnecessary sensitive exposure; it
is not a demonstrated zero-miss guarantee. The implemented demand analysis keeps
functionality under the declared current relationships. It does not prove global
minimality, indispensability, or equivalence to every possible implementation.

The central open question is whether this structured analysis improves accuracy,
traceability and cost enough over a strong model reading the source directly,
or over a stronger taint/data-flow baseline with model assistance. The user and
advisor explicitly challenged whether the machinery makes the model's job harder.
No overall advantage over direct prompting or Semia has been established here.
Do not preserve complexity just because it exists; equally, do not discard the
implementation before the planned complex-Skill comparison supplies evidence.

The next research discussion should be driven by that comparison, not another
round of prompt additions based only on the three development cases.

## 3. Decisions carried forward from the conversation

| Topic | Current decision and important boundary |
|---|---|
| Graph | The three development-case pilots reused frozen CFGs. The formal same-model native comparison requires fresh graph construction under its protocol. Graph structure checks and controlled-text/Lean facts do not prove equivalence to natural-language intent. |
| Actual processing | Preserve whole values unless an actual selection, exclusion, replacement or other supported relation narrows them. A simple operation or absent LLM mention does not establish local isolation. |
| Default visibility | Apply the frozen runtime contract when mechanisms are unspecified. Explicit local execution and limited return mechanisms must be respected. Possible model observations are static relations, not observed execution. |
| Field identity | Explicit field selection, unchanged members, constructed payloads, computations and tool acquisition remain distinct. `possible` influence is not proof of literal content. |
| Conditional requests | Conditional build members preserve original values; absence controls are not payload fields. Paired request/response bindings preserve actual request identity. |
| Locations and sinks | Locations describe boundaries before Data is propagated. The program derives sink types and fixed exposure levels from operations and location properties. Level is boundary character, not sensitivity, authorization or risk. |
| Source evidence | Use frozen files and physical line ranges; the program extracts exact text. Line coverage proves references, not semantic completeness. Old paragraph indexes are retired from the active interface. |
| CFG evidence | Use real CFG identities and direct targets. A review target locates a candidate claim; it is not a CFG evidence address. CFG facts do not establish facts that exist only in the candidate or source. |
| Task | Extract and seal it only from the complete frozen Skill. Later annotation references that exact Task. No external purpose override or constant basis field remains; real runtime user inputs described by the Skill remain source semantics. Do not reconstruct purpose from the current graph's payloads. |
| Realization | State how each requirement is expressed, partly expressed, retained, or unmapped. A correct requirement does not imply all applicable receiver parameters have demand declarations. |
| Positive demands | Six properties: value, presence, cardinality, shape, truth and action. They are computational preservation starting points, not per-IR necessity scores. |
| Receiver demand | Required delivery content belongs at the actual receiving input and field range. An action or shape demand, or an upstream build/selection demand, cannot silently stand in for recipient content. |
| Reading versus requiring | Whole-value acquisition or observation does not justify a whole-value task demand. Narrow task demands do not retroactively narrow actual reading or visibility. |
| Backward demand | Trace actual inputs, outputs, versions, conditions and element scope. Downstream-required information cannot disappear and then be recovered from a global Data registry. Demands do not spread to unrelated recipients just because Data IDs match. |
| Sensitivity | Declare grounded information ranges on existing symbolic values; the program tracks them. No declaration does not mean no sensitive data. Derived/possible influence remains distinct from confirmed content. |
| Constraints | Check independently in the forward direction. A prohibition does not delete payload facts or become positive demand. Conditions/counts/order do not remove violating paths. |
| Reduction | Only supported `exclude_field` candidates are currently considered. Preserve positive requirements and separately justify relevant constraint preservation; keep original violations visible. |
| Review and repair | Independent four-axis review; one shared semantic repair budget. Task repair is isolated from graph/payload/free review text; annotation repair holds Task fixed. |
| Structural correction | Mechanical validation and semantic review remain separate. Production structural corrections have no count cap. Restricted JSON normalization preserves the original response and receipt. Transport/truncation/identity/implementation failures are not infinite semantic correction loops. |
| Language | Prompts, model work documents, synthetic examples and diagnostics use English. User-facing design/verification reports for the current work use Chinese. Genuine source, runtime input examples, quotations and frozen historical artifacts retain their original language. |
| Accounting | Record logical requests, structural corrections, HTTP attempts, usage and elapsed time separately. Unknown usage stays unknown. Reasoning/cache details must not be added again to totals that already include them. |

The earlier idea of generating Task inside one joint response was superseded by
independent source-only Task extraction. The earlier proposal to add constraint
dependencies generally to backward demand was superseded by independent forward
constraint checks. Do not revive either design by following an old chat excerpt.

The former `doe-input.json` total bundle and separate Task/demand/sensitivity
experiment wrappers are retired from the active production chain. Do not rebuild
them as prerequisites or migrate frozen old records. Each stage stores its own
outputs, binds the actual upstream stage, and uses public verified loaders.

## 4. Current implemented flow and code ownership

```text
Complete frozen Skill
    -> independent source-only Task extraction and seal
Existing CFG + frozen Task + source + runtime contract
    -> joint annotation of processing, boundaries, demands,
       realizations/constraints and sensitivity
    -> independent semantic review
       -> accept; or one annotation repair; or one isolated Task revision
          followed by new annotation
       -> independent re-review when repaired
    -> select the last legitimate candidate, retaining review status
    -> observation/sink compilation and forward propagation
    -> backward positive demand + sensitivity tracking
       + independent forward constraint checks
    -> sink comparisons and supported reduction-preservation evidence
```

The diagram starts at the downstream pipeline used by the development pilots.
The formal same-model native comparison also constructs its own fresh graph;
it must not import an old graph or a cross-repeat semantic cache.

Normal semantic paths use **3 / 5 / 6 calls** respectively. Structural correction
and HTTP retries are additional and separately counted. A structurally valid
candidate may still be diagnostically analyzed after review failure or a repair
limit; computational completion must not replace that status with semantic pass.

| Location | Responsibility |
|---|---|
| `src/skillflow/common/` | Frozen sources, references, strict JSON, model transport, call records and recovery |
| `src/skillflow/graph/` | CFG, construction, validation, source checking and bounded graph feedback |
| `src/skillflow/task/` | Independent Task extraction, sealing and isolated revision |
| `src/skillflow/propagation/` | Shared contracts, annotation/review/repair, observation compilation, Data and forward propagation |
| `src/skillflow/doe/` | Backward demands, information tracking, constraints, sink comparison and formal DOE runs |
| `tools/doe/real_comparison/` | Comparison preparation, calibration and execution orchestration; not core semantics |
| `formal/` | Existing Lean project and proof material |

Use `python -m skillflow --help` to inspect installed stage commands. The formal
entry points remain pipeline prepare/run/replay and the independent stages.
This handoff deliberately does not provide a dispatch command: preparation or
old recorded authorization is not permission to start an experiment now.

Current interface versions (2026-10-27; older experimental identities remain frozen):

| Interface | Version |
|---|---|
| Task / Task reference / extraction run | v5 / v3 / v3 |
| Runtime contract | v7 |
| Joint annotation profile | v17 |
| Processing compiler / mapping | v9 / v9 |
| Annotation run | v20 |
| Review response / review run / refinement run | v8 / v13 / v12 |
| Propagation run | v17 |
| Demand / sensitivity result | v5 / v4 |
| Formal DOE run / pipeline | v6 / v9 |
| Document-guided run / step / annotation | v3 / v3 / v3 |
| Structural correction protocol / Data | v5 / v4 |

Some run identity strings retain the historical `skill-ir-` prefix. This does not
restore an active `skill_ir` package. No historical records are migrated or
rehashed to claim these current identities.

The four constraint families use five bounded forms: `forbid_information`,
`only_if`, `at_most`, `requires_prior`, and `forbid_after`. They reuse Task evidence
and existing references. A constraint can be completely expressed while current
behavior potentially violates it. Unsupported scope, missing relationships and
incomplete coverage remain limitations. Neither restrictions nor their checking
dependencies are positive demand seeds.

## 5. Latest formal development-case evidence

The latest tracked three-case result is
[constraints-pipeline-v1-20261020-162606](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/index.html).
Read its [assistant review](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/assistant-review.md),
metrics and replay files together. The following is a research interpretation,
not an independent human gold standard:

| Case | Material outcome | Remaining substantive issue |
|---|---|---|
| 001 | No accepted annotation after final structural-correction transport failure; no DOE | Do not present an older successful DOE as this run's result. |
| 010 | Optional request construction preserved; diagnostic DOE is partial | Receiver-level absent-member demand attribution is incomplete, a deletion restriction remains unsupported, and no sensitivity declarations were supplied. Empty sensitive findings are not a safety claim. |
| 013 | Retry parameters and all four terminal status-write payload demands improved; semantic repair limit retained | Unsupported local transient classification, a late success-stop trigger and incomplete diagnostic prohibition receiver scope remain. Review also proposed a wrong operand change and duplicate sensitivity. |

Recorded totals are 17 logical calls, seven structural corrections and one
semantic repair, with 17 HTTP attempts and no HTTP retry. Reported usage is a
**1,065,598-token subtotal**, not a complete total: the final failed 001 request
has unknown usage. Zero-API replay preserved the saved decisions and failures.

010 has 12 sinks and two satisfied constraint checks. 013 has 16 sinks, 11
satisfied checks (10 structural) and five potential violations. Its 20
`no_excess_established` rows include duplicated sensitive declarations; they are
not 20 independently confirmed leaks. There were no supported field reductions.
The online runs therefore did **not** exercise a successful reduction-preservation
proof. Counts or an absence of reductions alone are not a quality evaluation.

Earlier prompt screens and the original 001/010/013 runs are development history.
They are not fresh held-out evidence after repeated prompt adjustment. Strict
replay may reject old producer identities; do not alter their hashes to obtain a
pass under current code.

## 6. Complex-Skill comparison: preparation versus execution

The intended comparison needs common inputs, clearly frozen task/evaluation
criteria, honest costs and comparable model access. Do not select easier inputs,
change thresholds after results, or treat assistant-authored semantic references
as independent human approvals. The current tools and recorded protocol, rather
than this narrative, govern any eventual authorized run.

There are three distinct preparation states:

1. **Tracked cloud-preparation snapshot.** The earlier source-selection report
   records 30 choices (24 selected plus six reserves) and 22 selected source
   clusters, pending root/human-reference checks. The cloud material audit's
   review counts and dependency seal describe that point in time.
2. **Newer local-only long preparation.**
   `experiments/doe/runs/real-same-model-long-v2-20261020-1340Z/` contains a separate
   source-selection seal and 30 offline-verified preparation packets; 65 source
   reviews were checked. Its state records **zero formal requests, zero human
   approvals, incomplete semantic references and dispatch disabled**. It is not
   included merely by committing this handoff's inventory.
3. **Newer local-only CLI v3 calibration.**
   `experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z/` records a calibration
   started after authorization in another conversation and then explicitly
   paused at `2026-10-20T14:14:15.778016+00:00`. The `gh-fix-ci` q001 attempt has no
   saved response or receipt and unverified usage. Processes were stopped and
   automatic dispatch is forbidden. **Do not resume it or delete locks.**

Thus the formal long comparison has not started, but it would be inaccurate to
say that no calibration attempt ever started. The older tracked CLI v2
calibration remains stopped after an execution-envelope mismatch and is not a
formal result. Cloud or another computer needs its own verified transport,
authentication and receipt behavior; do not copy Windows login files, inherit
Windows producer identity, or silently substitute a paid API.

The newer long bundles have reference sizes of 21,361-62,869 `o200k_base` tokens
(median 38,273; total 977,753). These are source size measurements from preparation,
not actual API usage or permission to dispatch. None is a measured strong-model
comparison result.

The reviewed selection helper now requires stronger evidence for an implicit
file connector. Some frozen older source reviews used directory-copy quotations.
Those records were not resealed or relabeled in this handoff. Before a future
selection verification or experiment, audit the evidence under the intended
implementation instead of relaxing the new guard or claiming historical success
automatically transfers to it.

## 7. What Git transfers, and what remains on the first computer

The prepared branch already contains current research implementation, tests,
documentation and the comparison materials enumerated by the
[cloud material audit](cloud-material-audit.md). The present submission reviews
and updates `long_selection.py` and its tests, then adds this handoff and its
verification/navigation. All previously tracked history remains intact.

The [local-only inventory](research-local-only-inventory.json) is metadata for
**1,054 files / 42,325,410 bytes** observed on 2026-10-21. It records exact relative
paths and hashes without submitting their contents:

| Local-only scope | Files | Bytes |
|---|---:|---:|
| Active CLI-v3/supervisor/preparation implementation, tests and docs | 15 | 241,428 |
| Long-cohort preparation | 785 | 34,106,614 |
| Paused CLI-v3 calibration | 230 | 2,347,116 |
| CLI-v3 proposal and adoption records | 17 | 75,847 |
| Supplemental selection audit | 7 | 5,554,405 |

This is an explicit scope inventory, not an inventory of all ignored files or all
historical experiments. Locks are presence metadata only, not resumable ownership.
These local-only source files require a separate review/submission or an explicitly
requested file transfer before the second computer can use that newer preparation.
If they are missing, stop that activity and report what is absent; do not synthesize
replacement receipts or recreate authorizations. The two requested tracked changes
must not be described as synchronizing this additional work.

The modified `output/pdf/bill-template.pdf` and `.tex` stay local and unchanged.
Their earlier tracked history is not rewritten. No credentials, authentication
files, virtual environments or account secrets are part of this handoff.

Keep `.gitattributes` byte-preservation rules. Frozen absolute report URLs may still
name the original Windows checkout. Use repository-relative navigation for new
work; do not rewrite frozen reports or producer manifests to hide the move. Move
an entire run with its explicit dependency closure, not isolated stage files.

## 8. Safe local setup and continuation

On the second Windows computer, install Git and a supported Python (3.10 or newer),
then use a short checkout path. After the main merge has been confirmed:

```powershell
git -c core.longpaths=true clone --branch main https://github.com/southofborder/SkillFlow.git
cd SkillFlow
git config core.longpaths true
git status --short
git rev-parse HEAD
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . pytest
.\.venv\Scripts\python.exe -m skillflow --help
```

Installation may download package dependencies; these commands do not authorize
or intentionally dispatch model work. For an existing checkout, inspect local
changes first, then `git fetch origin` and `git pull --ff-only`; do not overwrite
uncommitted work. Record the actual Python version and Git commit. Lean is optional
until a formal check is requested; its repository-pinned toolchain must be used.

Open this repository in Codex, read `AGENTS.md`, and start a new chat with the
message below. Git transfers committed files, **not the app's conversation**.
This document carries the important research context, decisions and exact places
to inspect. It does not preserve every chat turn or automatically migrate a live
task/session. If exact dialogue is needed, preserve it separately using the app's
available sharing/export facilities.

> Continue SkillFlow from this checkout. Read AGENTS.md and
> docs/research-chat-handoff.md before acting. Verify the current branch and Git
> revision, distinguish committed evidence from the local-only inventory, and
> summarize the research state and unresolved strong-model comparison. The
> pipeline is frozen: do not modify prompts or the research protocol, dispatch
> model calls, resume calibration, start long experiments, acquire new evaluation
> inputs, or reinterpret old run identities. The latest task is cross-computer
> research handoff. Ask for the specific next research decision after reporting
> available and missing materials. Do not treat absent local-only files as proof
> that preparation never occurred.

## 9. Decisions still needed before research execution resumes

- Review/transfer the 15 local-only implementation files and their required
  preparation materials if the newer CLI-v3 route is to be used.
- Resolve transport and receipt validity on the actual destination computer;
  prior authorization and old Windows identities do not settle this.
- Review the source-selection connector evidence affected by the tightened guard.
- Complete independent human reference/approval gates required by the comparison.
- Explicitly decide whether and how to resume the paused calibration, then the
  formal comparison. No permission is inferred from this list.
- Use the comparison to decide which semantic declarations help the model and
  backend, which can be generated deterministically, and which complexity should
  be removed. No redesign is prescribed by this handoff.

The immediate deliverable is a reviewed Git snapshot and a reliable continuation
record. Neither successful synchronization nor offline test completion establishes
semantic correctness, research superiority, or an absence of DOE.
