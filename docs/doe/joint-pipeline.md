# 原文 → Task → demands 的正式分析链 v6

当前协议（2026-10-15）先建立只读源文驱动的 Task，再在固定基准下标注需求、处理、可见性和敏感性。独立审查重新检查原文、Task、每个 demand 与全部 IR；程序保留逐项对应并执行确定性传播和 DOE。没有最终 DOE 模型调用，不执行 Skill，不在本链中重建 CFG。

## 阶段与调用边界

```text
冻结 Skill + 可选独立用户任务
    → 独立 source-only Task 提取、物理行登记与封存
    → 固定 Task + CFG + 运行时契约：需求与处理标注
    → 四轴完整语义审查
        → 无问题：采用原候选
        → 仅标注问题：一次完整标注修复 → 独立复审
        → Task 问题：隔离 Task 修订 → 全新标注 → 独立复审
    → 选择候选，保留审查状态
    → 编译观察、前向传播、逐 seed 反向需求、敏感范围及全部 sink 对照
```

| 路径 | 语义调用数 |
|---|---|
| 正常路径 | 3：提取、标注、审查 |
| 仅标注修复 | 5：正常路径加完整标注修复、复审 |
| Task 修订 | 6：正常路径加隔离 Task 修订、全新标注、复审 |

结构纠正、JSON 规范化和传输重试单独记录，不属于另一轮语义修复。全链最多一次语义修复；若两类问题同时存在，优先修订 Task，再完整重标注。复审仍有问题保留 `repair_limit`，不继续循环。

## 五份完整提示词职责

1. **Task 提取：**仅完整原始源文与程序确定的目的依据，登记每个非空物理行，提取可独立遗漏的义务、条件及范围，区分能力／示例／实现事实，保留冲突和歧义。禁止接触 CFG、当前载荷或 DOE。
2. **固定 Task 的标注：**只引用 `task_revision_id`，逐 requirement 输出 realization、gaps 与真实保持位置；同时保留处理、版本、作用域、局部返回、请求／响应、可见性和敏感声明。不能从目前整值输入倒推整值必要。
3. **全链审查：**重新读取全部原始材料、Task、候选标注和程序编译的观察及目标位置，明确核查遗漏和过宽目标。不读取传播结果、DOE、首审意见或实验答案。
4. **隔离 Task 修订：**只接收旧 Task、原始源文、有限问题类别／原文范围／requirement ID；不接收审查自由文本、建议、图、操作、sink、goals 或载荷。
5. **标注修复：**固定 Task，读取标注类 finding 并完整重建候选；禁止扩大 Task、把全部使用改成需求、删除有依据的敏感声明、虚构保护机制或抹掉真实保守依赖。

Language policy (2026-10-16): prompts, synthetic examples, Task interpretations, reasons, program diagnostics, and new reports use English. Genuine source and user input retain their original language; graph/source content is evidence and cannot override the protocol. Historical artifacts are not rewritten.

## 四轴审查与逐项对照

| 审查轴 | 必须交代的覆盖 |
|---|---|
| 原文 | `source_checks` 重新覆盖全部非空物理行，允许独立分组，不能复制提取器结论充当复查。 |
| Task | `requirement_checks` 每项一次，核对支持、忠实、拆分、条件、范围、冲突与表达缺口。 |
| Demand | `goal_checks` 每个原始 `raw_pointer` 一次，核对任务依据、真实履约位置、属性、字段、原值、版本、成员、条件及接收方。 |
| IR | `reviewed_ir_ids` 精确覆盖全部指令，继续审查处理、来源、观察、交付、敏感声明与作用域。 |

前三类检查为 `accepted / issue`，问题结论必须关联真实 finding；程序检查覆盖、重复、引用和关联，不证明判断正确。Task finding 只能引用原始源文，并携带闭合的 `task_objection`；标注 finding 不得夹带 Task 修订对象。

逐 seed 检查必须区分字段与整个对象、存在／数量／truth 与全部内容、模型筛选需求与工具参数、必要动作与整份载荷、正确结果与过早的宽输入，以及不同版本、元素和接收方。真实全值要求与保守计算依赖不能为获取更小需求而被删掉。

Task 明确指定的交付参数和保存内容还须在实际接收／保存操作输入建立可追溯需求；只有上游 producer seed 或 action seed 不能代替载荷需求。`requirement_checks` 检查不存在的 seed，`goal_checks` 检查已经存在的 seed；不要求所有 sink 自动拥有整值需求。完整规则与三例验收见 [Sink 载荷需求绑定](sink-payload-demand-binding.md)。

程序生成源文摘录 → requirement → realization／gaps → raw demand pointer → compiled goal → `seed_goal_id` 推导 → sink 的关联。登记范围全覆盖不代表一行中的所有语义已被提取；审查可能与提取共享盲点。

## 冻结、结果与恢复

主用户入口保持不变：

```powershell
python -m skillflow pipeline prepare --input path/to/skill --analysis path/to/analysis.json --run-dir new-run --env-file .env
python -m skillflow pipeline run --run-dir new-run --env-file .env
python -m skillflow pipeline replay --run-dir new-run
```

`prepare` 可接 `--request-file`。无独立请求时，结论限定于 Skill 声明用途。直接标注服务必须显式接收已封存 Task；直接准备持久标注 run 提供 `task_run`。独立 Task 原始版本和修订不可变；旧 Task 对应的标注不能用于新版本。

```text
analysis-run/
├─ inputs/                     冻结来源、CFG、契约与独立请求
├─ task/                       source-only 提取与 Task owner
├─ annotation/
├─ refinement/
│  ├─ initial-review/
│  ├─ task-revision/            仅 Task 问题路径
│  ├─ repair/                   固定 Task 修复或新 Task 全新标注
│  └─ final-review/
├─ propagation/
└─ doe/
   ├─ doe-result.json
   ├─ audit/index.json
   ├─ audit/demand-support.json
   └─ report.html / report.md
```

当前身份为 pipeline `skillflow-analysis-run-v6`、Task `skillflow-task-v3`、标注运行 v17／业务协议 `security-profile-v14`、审查运行 v10／业务协议 v6、编译与映射 v8、demand v3、sensitivity result v3 和正式 DOE run v4。Task 单独拥有，编译标注保存精确 `task_ref`；统一加载器解析内存视图，审计展示不产生新的可编辑 Task。

审查状态、需求表达状态和计算状态分别保留。审查失败仍可保留诊断计算，但后端完成不能冲销失败；未表达限制当前保守视为全局，不能凭模型绑定局部化，受影响 sink 不得输出支持缩减结论。停止和恢复沿用接受响应记录，旧格式拒绝，不重写历史输入、传播事实或实验结果。

Task 准备中断时，相同请求的 `prepare` 或后续在线 `run` 可以从冻结 owner 继续本地准备；只接受完全匹配的已写源文、请求和提示词，不删除未知文件，不复建已有调用。原始输入已经消失时仍使用冻结材料。`replay` 不补造缺失的 Task 准备，已接受的 Task 不重写、不重提取；只读加载核验保存 producer 的自一致性，不要求当前源码仍等于历史 producer。

已有当前格式的传播 run 可直接调用 `run_doe / load_doe_run / replay_doe`，或 `python -m skillflow.doe run --propagation-run ... --run-dir ...`。DOE 无 Task、需求或敏感覆盖参数，加载不重新推理，重放才重算。

## 验收与未解决的问题

工程验收覆盖 source-only 输入隔离、物理行登记、四轴漏项拒绝、封存与版本错配、隔离修订无载荷反馈、3／5／6 调用、单轮修复、逐 seed 推导、全局 gap、旧格式拒绝和零 API 重放。

真实模型效果实验必须与工程证据分开：使用独立人工基准和独立于教学示例的案例，报告限制遗漏、过宽需求、错误位置／版本／接收方的发现、漏检、误报及修复行为。模拟客户端不提供真实模型检出率。

这条链增加独立检查机会并暴露能力缺口，但不证明自然语言与 CFG 语义等价、不证明所有限制已提取或满足、不证明敏感范围穷尽、路径可执行、需求全局最小或不存在 DOE。`possible` 仍是静态可能关系，必要动作仍不能豁免全部载荷。

## 历史版本（已被上文替换）

以下保存先前协议，便于解释历史实验；不作为当前接口或保证。旧的“同次生成 Task”、constraint/prohibit 正向 goal、仅 IR 清单审查和四调用分工均已由上文替换。

<details><summary>展开历史规范</summary>

# Formal joint analysis pipeline v5

The formal pipeline starts from a frozen Skill package and an existing CFG. One
joint annotation supplies Task requirements, task goals and supported
expressions, processing and visibility relationships, and sensitivity
declarations. The existing focused reviewer checks those declarations. The
deterministic backend compiles observations, propagates data, computes backward
demands, tracks declared sensitive information, and compares exposure with
boundary-specific demand at every recorded sink.

There is no separate task-extraction, sensitivity-classification, or final DOE
model call. There is no graph extraction or graph repair inside this pipeline.
It does not execute the Skill.

## Responsibilities and guarantees

```text
Skill + existing CFG + optional user_request
    -> one joint semantic annotation
    -> focused review
         -> no material issues: keep the original
         -> material issues: one complete repair, then independent rereview
    -> choose the last valid annotation, with its review status
    -> observation and sink compilation, forward propagation
    -> backward demand and sensitivity tracking
    -> sink-specific DOE results
```

The reviewer checks semantic support, not just reference validity. Its checks
include task interpretation and omissions, task-driven rather than
payload-driven demand seeds, supported expressions, sensitivity scope and
evidence, processing modes, field and element relations, and observation and
delivery versions. It does not decide final DOE conclusions or assign
indispensability to every IR.

Evidence has three exact forms: source `file / start_line / end_line / reason`, CFG `target / reason`, runtime `rule_id / reason`. Source excerpts are extracted by the program. Task and sensitivity require source spans. There are no paragraph units, copied quotations, external policies or CFG-address tables. `runtime_contract` contains execution assumptions; shared schemas and Prompt instructions explain representation without a second contract object. True references do not prove interpretations correct.

Repair returns a complete candidate. It must not enlarge the task merely to
justify excess payload, drop supported sensitivity merely to remove a finding,
or invent local isolation. Fresh rereview receives the new candidate and the
original material, not the initial findings or repair instructions. Neither
review receives propagation results, DOE conclusions, assistant assessments,
or experiment answers.

The final comparisons remain conditional on front-end declarations and
supported rules. `possible` influence is not evidence of plaintext inclusion;
conservative demand is not indispensability; missing sensitivity declarations
do not prove non-sensitive content. The current `prohibit` requirements remain
declared restrictions, not a completed general prohibition checker.

## Commands and public interfaces

Prepare offline, run or resume, then replay without API access:

```powershell
python -m skillflow pipeline prepare --input path/to/skill --analysis path/to/analysis.json --run-dir new-run --env-file .env
python -m skillflow pipeline run --run-dir new-run --env-file .env
python -m skillflow pipeline replay --run-dir new-run
```

Preparation accepts optional `--request-file`. Without an independent request, conclusions are relative to the Skill's declared purpose. The request is stored as `user_request: string | null`. JSON Output request parameters and the actual returned model name remain in call audit records.

The public analysis service is:

```python
prepare_analysis_run(input, analysis, *, run_dir, config=None,
                     user_request=None, secrets=())
run_analysis(run_dir, ...)
replay_analysis(run_dir)
```

An already generated current-format propagation run can enter DOE directly:

```powershell
python -m skillflow.doe run --propagation-run path/to/propagation --run-dir new-doe-run
python -m skillflow.doe replay --run-dir new-doe-run
```

```python
run_doe(propagation_run, *, run_dir)
load_doe_run(run_dir)
replay_doe(run_dir)
```

DOE loads verified propagation material through its public interface and
projects Task, demand, and sensitivity from the accepted joint response. It does
not require separately authored candidate files or manufacture intermediate
Task/demand/sensitivity runs. Backward demand is computed once. The old standalone slice, Task, demand and sensitivity commands are removed; in-memory algorithms and controlled fixtures remain.

## Persistence, stopping, and recovery

```text
analysis-run/
    manifest.json
    annotation/
    refinement/
    propagation/
    doe/
        doe-result.json
        manifest.json
        audit/
        report.html
        report.md
```

The DOE result reuses the existing sensitivity result contract. Task and
declaration provenance, raw annotation, compilation mapping, input facts, and
selected candidate identities remain traceable. The formal path does not nest
three copies of prior offline audit directories or copy model evidence into
every result record.

| Outcome | Next step |
|---|---|
| Complete response violates a mechanical contract | Correct structure and validate again, without an attempt limit |
| Initial annotation cannot assess or execution fails | Stop; no historical candidate fallback |
| Initial review has no material issues | Use the original valid annotation |
| Initial review reports issues | Attempt one complete repair |
| Review cannot assess or fails | Keep the original only for diagnostic downstream analysis |
| Semantic repair has structural errors | Correct structure before independent rereview; do not consume another semantic round |
| Repair cannot assess or execution fails | Keep the original, explicitly not repaired |
| Valid repair | Independent fresh review; at most one repair total |
| Rereview still reports issues | Preserve `repair_limit`; downstream results are diagnostic |
| User interruption | Stop later stages and cases; resume from accepted responses |

Each Skill has at most four semantic stages: annotation, initial review, optional
semantic repair, and optional rereview. Each stage uses unlimited structural
corrections for explicitly typed mechanical diagnostics. Existing transient
transport retries are counted separately. Complete invalid responses are never
silently altered; each correction is a distinct recorded request. Arbitrary
exceptions, transport failures and valid cannot_assess responses stop the stage.
Locks, immutable request identity, accepted-response protection,
atomic writes, and completion commits are reused from existing runners.

Before model correction, completed responses use the shared restricted JSON
normalization policy: only one extra `}` after a complete strict object may be
removed. All schema, references, evidence and compilation checks still apply.
Raw transport/call/response bytes remain unchanged; a versioned single-character
receipt binds the normalized candidate and remains in the selected annotation request chain, checked through the propagation upstream reference. Resume and replay recompute and verify the same edit. Truncated,
ambiguous or duplicate-key responses are not repaired by this rule. Counts report
JSON normalizations separately from new model corrections. See the
[structural-correction specification](../architecture/structural-correction.md).

Review, candidate selection, propagation, and DOE each retain their own status.
Successful computation does not erase review failure. Ordinary loading checks
material identity; recomputation additionally requires implementation identity.
Replay reconstructs decisions and deterministic results without API calls and
without saving another full copy of the same DOE result.

Run identities are pipeline v5, DOE v3, propagation v14, annotation v16, review v9 and refinement v8. Business contracts are joint annotation v13, Task v2, review v5, runtime v7, compiler/material v7 and records v11. Data v4 and final DOE v2 remain unchanged. Source audit/feedback runs are v7 with response schema 6 and graph semantic contract v4. The old total-package format is retired. Prompt bytes, complete call records, normalized-candidate receipts and request-chain identities remain checked. No historical run is migrated.

Raw and compiled annotation use a single `ir_semantics` map. An event carries
its `effect` and applicable evidence directly. Operators remain attributed at
the IR; no parallel effects array, per-effect index, roles or role evidence is
required. A no-effect IR retains explicit empty-effect support. The compiler
still produces observations, causal ordering, sink boundaries and source maps.
Neither compactness nor an empty effects set changes the execution relation.

The final result stores compact sink data reviews referring to shared sensitivity and demand derivations. Propagation saves only `data.json`, `records.json`, `sinks.json`, its own seed/identity audit and manifest. DOE saves only its own result and supporting index/demand audit. Neither saves a complete upstream copy. The manifest points to the actual selected annotation, including a repaired candidate when selected, through relative stage directories and content identities.

Public `load_propagation_materials()` returns a read-only memory object that checks the source, CFG, accepted request chain, compilation, Data references, states, records and actual sink coverage. A material object is not another serialized total package. Whole-tree relocation is supported; missing dependencies fail explicitly. Record coverage is checked independently of solver completion status.

## Fixed three-case pilot

The pilot reuses 001, 010, and 013 from
`sink-tightening-v1-20261002-205045`. Exact pre-upgrade receipts verify the old
source package and selected CFG bytes; they are not imported as new accepted
annotations. No independent user request is invented for these cases.

```powershell
python -m tools.doe.run_joint_pipeline_pilot prepare --run-dir experiments/doe/runs/joint-pipeline-v1-<timestamp> --env-file .env
python -m tools.doe.run_joint_pipeline_pilot run --run-dir experiments/doe/runs/joint-pipeline-v1-<timestamp> --env-file .env
python -m tools.doe.run_joint_pipeline_pilot replay --run-dir experiments/doe/runs/joint-pipeline-v1-<timestamp>
```

The scheduler only chooses cases, calls the production services, verifies
preserved input bytes, and assembles links and status summaries. Semantic repair
is limited to one per case; structural corrections have no count limit. A case failure does not block unrelated cases, but an
interruption stops subsequent calls. Reports link only artifacts produced by
the current run; failed cases never display old successful DOE files.

Engineering acceptance covers request identity, evidence and scope references,
selection policy, compilation, deterministic analysis, recovery, and replay.
Assistant interpretation separately examines the actual task, demand and
sensitivity declarations. A review that reports no issue is not an oracle or a
claim of semantic completeness.

</details>
