# 独立 Task 与原文逐项登记 v3

当前协议（2026-10-15）先只根据完整冻结源文和可选独立用户任务建立 Task，再把固定 Task 交给标注阶段。模型负责解释语义；程序负责来源、行级登记、版本和引用的机械检查。行级覆盖、真实引用和封存校验不证明要求已经穷尽或语义正确。

## 来源隔离与唯一任务基准

Task 提取输入只有完整可读 Skill 文件、独立用户任务和程序确定的 `basis`，不含 CFG、现有参数／载荷、标注、传播和 DOE。Skill 源文本身仍可能混合功能与实现；独立调用不能消除这种偏差。

有独立用户任务时，以其为目的依据，并保留与目的相容的 Skill 精确限制；没有时相对 Skill 声明用途分析，不把声明视为真实用户授权。明确冲突保留双方证据、采用依据和理由；无法确定的歧义或冲突留在 `issues` 中。

```text
CandidateTask
├─ purpose: text / evidences[]
├─ requirements[]: id / text / evidences[]
├─ source_accounting[]
│  ├─ file / start_line / end_line
│  ├─ disposition / requirement_ids[] / issue_ids[]
│  └─ reason
└─ issues[]: id / kind / evidences[] / requirement_ids[] / resolution / reason
```

Task 是唯一的要求释义，不再另写重复的限制文本清单，也不包含图绑定。按可以独立遗漏或放宽的义务组织要求，保留原值、条件、范围、次数、顺序、质量、副作用、禁止项及同元素关系；拆分后不能丢失这些关系。能力说明、示例和实现事实不自动构成必要性；步骤中的精确限制也不能被当作实现细节删除。真实完整原值要求必须保留。

## 物理行处置与来源校验

文件名使用 `skill/<真实相对路径>`，独立用户任务使用 `task/user-request.txt`。行号为从 1 开始的闭区间，统一用 `splitlines(keepends=True)` 保留 CRLF、LF 和无末尾换行。模型只给来源位置及理由，报告中的原文由程序读取。

程序构造全部非空物理行全集，要求每一行恰好登记一次；连续且处置相同的行可以合并，范围内可以包含空行。同一行可以关联多个 requirement，一项 requirement 可以引用跨行、跨文件来源。处置类型为 `requirement / supporting_context / implementation_fact / capability / example / not_applicable / unresolved`。每项 requirement 和 issue 都必须出现在登记中；引用必须指向真实文件及范围。

这是一份物理覆盖账目，不能检验一行中的第二项语义限制是否漏掉。独立审查必须重新读取全部原文，不能把登记表当成完备性证明。

## 封存与下游接口

程序生成 `skillflow-task-v3`，添加 `basis / source_sha256 / user_request_sha256 / task_sha256`。`task_sha256` 绑定除自身外的完整内容，精确身份随用户任务和源文变化。`TaskReference` 是程序生成的版本引用。

标注输入显式接受固定 Task；原始响应只返回 `task_revision_id`，不能返回 Task 正文。编译响应保存 `task_ref` 与逐项 `realizations`。Task 由独立 Task run 拥有，下游清单引用该 owner；统一只读加载器解析成内存中的 `annotation["task"]`。提示词与报告中的展示是审计副本，不是另一份可编辑任务基准。

`skillflow.task` 提供 source-only material、提取／隔离修订、记录式 `prepare_task_run / run_task / load_task_run`。正式用户入口仍是 [完整分析链](joint-pipeline.md)。直接准备标注 run 必须提供已封存的 `task_run`；不得恢复旧的同次生成 Task 或历史总包兼容读取。

## Task 修订的隔离

审查发现 Task 问题时，只向修订器提供旧 Task、原始完整材料及闭合的 objection：有限 `code`、原文 `source_spans` 和已有 `requirement_ids`。不透传 finding 的自由文本解释、建议、CFG、操作、sink、载荷、goals 或 DOE。修订器必须独立核实主张，返回完整替换 Task 和全部处置记录。

Task 版本改变后，旧标注和需求失效，重新生成整份标注；不机械迁移旧 requirement 绑定。新旧版本与完整审查意见都保留在审计记录。

## 验收边界

工程检查包括缺行／重复行、跨文件引用、同一行多要求、图字段注入、封存和版本错配、跨阶段泄漏及离线重放。合成样例明确标为人工声明，历史三例的原始输入和结果不变。

语义检出率需要独立人工基准和真实模型评测；结构通过、登记齐全和模拟客户端运行成功均不能替代该实验。

## 历史版本（已被上文替换）

以下保存先前协议，便于解释历史实验；不作为当前接口或保证。旧的“同次生成 Task”、constraint/prohibit 正向 goal、仅 IR 清单审查和四调用分工均已由上文替换。

<details><summary>展开历史规范</summary>

# Task Evidence v2

Task records the Skill-level purpose, required outcomes, conditions and restrictions. It is generated in the same joint response as processing, demands and sensitivity. It is not a per-IR necessity judgment or a separate extraction call.

```text
task
├─ purpose: text / evidences
└─ requirements[]
   ├─ id / text
   ├─ evidences[]: file / start_line / end_line / reason
   └─ bindings[]: target / reason
```

The program adds `schema_version=skillflow-task-v2` and `basis=user_request|declared_skill`. An independent `user_request` establishes the purpose source; otherwise conclusions are relative to the declared Skill purpose, not proof of real user authorization. Purpose and every requirement need source evidence. Empty bindings remain explicit: they do not become usable demand seeds.

## Source spans

Readable files use `skill/<relative-path>`. An independent request has the evidence name `task/user-request.txt`; its text is stored once as `user_request`, not copied into the Skill source. No external policy input exists.

All stages use inclusive one-based physical lines from `str.splitlines(keepends=True)`. Evidence may cross former paragraph boundaries. The same function validates, extracts and displays spans while preserving LF, CRLF and missing final newlines. Boolean, zero, inverted and out-of-range indexes are rejected. Cross-file support requires separate spans. The model does not repeat quotations, hashes or paragraph identifiers.

Source-audit findings must collectively cover every nonblank physical line. This stricter reference-coverage check is specific to source audit, not a claim that Task annotations must turn all background text into requirements. Neither coverage nor a real quotation proves semantic support or completeness.

## Direct graph correspondence

```json
{"instruction_id":"ir_calibrate","side":"input","index":0}
```

Other targets use an existing instruction or block identity plus a relative `path`, or a graph-root path. There is no persisted graph-address directory or generated target-name table. Root paths cannot tunnel into instructions or operands. String keys and integer indexes remain distinct.

Task may correspond to metadata, constraints, a block or graph. `demands` has stricter capability checks: preserving a value requires a real value target, not the operand's name string or a whole IR. Ordinary return uses its real input and has no invented public output. A current oversized argument cannot become a requirement merely because it exists.

## Formal use

Use [pipeline](joint-pipeline.md) with optional `--request-file`. The former Task prepare/replay runner and baseline scheduler are retired. `prepare_task_review(materials, candidate, user_request=None)` remains an in-memory algorithm for controlled offline tests and report construction, using verified `PropagationMaterials`; it does not read an old standalone total package.

The independent executable example is `python -m examples.doe.joint_analysis_demo`. It uses a synthetic calibration scenario and identifies its authored provenance. Historical three-case results remain unchanged and are not accepted as current model responses.

**Source spans and target references are validated; semantic support and completeness are not proven.**

</details>
