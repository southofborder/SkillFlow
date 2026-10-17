# Task 保持需求与逐 seed 反向推导 v3

当前协议（2026-10-15）以独立封存的 [Task v3](task-evidence.md) 为基准。标注模型声明逐项表达情况和正向保持目标，程序沿已声明的处理、控制、数据版本及读写关系反推各接收边界需要保留的信息。既有前向事实保持不变；不按动作必要性筛除任何 sink。

## 要求、表达情况与需求目标

每项 requirement 必须且只能有一份 realization：

```text
realizations[]
├─ requirement_id
├─ status: expressed / partial / retained_only / unmapped
├─ bindings[]: target / reason
└─ gaps[]: reason / evidences[]
```

`expressed` 表示已给出保持目标且未声明剩余表达缺口，仍待语义审查；`partial` 明确列出未表达部分；`retained_only` 保留要求但当前规则不能表达保持条件；`unmapped` 尚无合适图位置。非 `expressed` 必须有 gap；`unmapped` 不得宣称图绑定。前两类需要真实正向 goal，后两类不能附带正向种子。

图绑定只建立对应，不能因为有一个 goal 就断言整项要求已经表达或满足。需求仅支持六类 `preserve`：

| 类型 | 要保持的信息 |
|---|---|
| `value` | 指定值或字段内容 |
| `presence` | 存在性，缺失与存在的 `null` 不同 |
| `cardinality` | 集合数量 |
| `shape` | 相关集合结构 |
| `truth` | 条件结果及其所需信息 |
| `action` | 指定行为与相关控制、迭代结构 |

`constraint / prohibit` 已移出正向目标类型。禁止事项及未支持限制留在 Task 与 realization，不再以一个限制 goal 获得 `bound`。本版没有通用禁止项、次数、顺序、质量或路径可行性验证器。

`demands` 引用已有 requirement，保存真实目标、`preserve / path / expected / expected_path / reason`。CFG 目标直接引用真实输入／输出／操作；响应中新建的操作采用附着式 `self / input(index) / output`。编译坐标由程序生成，模型不预测内部 ID。

## 从履约位置播种

种子应放在任务要求保持的实际结果、动作、交付或条件位置。例如“返回 label 原值”在真实 return 输入或对应结果建立值目标，再沿 `select_part` 反推 `label`。不能因为字段选取目前消费整个 record，就把整个输入播种为精确任务需求。

任务若要求不透明计算的结果，先保持其结果，再由程序保守反推相关输入。模型主动声明的整值种子与后端因不透明关系保守保留整值，必须分开显示。真实全值要求也不能为了获得更小集合而被缩窄。

受限表达式支持 `ref / literal / field / present / count / eq / ne / lt / le / gt / ge / not / and / or`，用于反向依赖，不构成通用条件求值或路径求解。`count` 不自动代表成功处理条数；无法精确描述的计算或筛选保留相关输入并标记保守性。

## 稳定传播与种子来源

选择、构造、排除、字段更新、筛选、读写、请求／响应与局部返回继续使用已有关系；保留控制、数据版本、同元素及参数位置，不借来源登记或缓存创造额外输入通道。`possible` 关系不等于明文包含。

每条推导必须有 `seed_goal_id`。推导身份和队列携带 seed，同一 requirement 的多个种子即使在同一值处合流，也保持独立记录；parent 必须属于同一 seed。FIFO／LIFO 应产生相同结果。单元素作用域、递归路径和不透明计算的能力边界继续产生明确诊断或保守保留。

`skillflow-demand-v3` 的 `coverage.requirements` 保存 realization、gaps、goal IDs 和是否有可应用目标，不再使用含糊的 `bound/unbound`。编译映射保存 `raw_pointer → goal_id / requirement_id / target`，结果 `traceability` 保存 Task 引用、source accounting indices 和每个 seed 的完整推导 ID。

报告由程序生成“真实原文 → Task → realization／缺口 → 原始 demand 位置 → 编译 goal → 逐 seed 推导 → sink”。显式离线实验种子若不属于接受的原始标注，其 `raw_pointer` 为 `null`，不会伪装成模型响应中的声明。

## 未表达限制与结论

不允许仅凭模型任意绑定节点就把 gap 限为局部。当前没有通用、独立的局部影响范围证明；未完整表达的要求和未解决的 Task 问题均按全局阻断诊断保留，所有受影响 sink 不得产生 `excess_supported`。已有局部计算仍保存为诊断，不把缺需求当成删除许可。

这比未来可证明局部影响的规则更保守。只有来源明确、图边界可独立核验的范围证据成立时，才能安全放开不受影响的局部结论；目前不会由模型 bindings 自动得到这种证据。

工程验收覆盖同 requirement 多 seed、跨 seed parent 拒绝、真实原值／字段关系、版本、作用域、全局 gap、引用重放和历史文件保护。通过这些检查不证明任意需求最小、行为满足要求、路径可执行或不存在 DOE。

## 历史版本（已被上文替换）

以下保存先前协议，便于解释历史实验；不作为当前接口或保证。旧的“同次生成 Task”、constraint/prohibit 正向 goal、仅 IR 清单审查和四调用分工均已由上文替换。

<details><summary>展开历史规范</summary>

# Task-driven Backward Demand v1

This offline stage links evidenced task requirements to information demands and
compares those demands with every recorded sink. It does not label each IR as
necessary, prove that an action or value is irreplaceable, execute a reduced
Skill, or issue a sensitivity or Data Over-Exposure verdict.

```text
Task requirements and source evidence
    -> explicit preservation goals
    -> backward rules over processing, control, and storage relationships
    -> comparisons at all recorded sink boundaries
```

The forward facts remain immutable. The formal DOE run stores its own results and references verified propagation inputs. Source quotations retain their original
language; specifications, authoring rationales, and review pages use English.

## 1. Task requirements are the starting point

The existing [Task Evidence](task-evidence.md) bindings locate a requirement in
the graph. They do not directly say what information a backward rule must
preserve. The same joint response supplies `demands` and `expressions`:

```text
demands[]
├─ requirement_id        Existing Task requirement, without copied text/evidence
├─ target                Direct CFG reference, or an attached operation slot
├─ preserve              value / presence / cardinality / shape / truth /
│                        action / constraint / prohibit
├─ path                  Applicable information range
├─ expected / expected_path  Supported original-value relationship
└─ reason
expressions[]            target / expression / evidences (control only)
```

Existing CFG targets are referenced directly. Demands on response-created operations are attached to that operation with `self`, `input(index)` or `output`; compute/filter expressions also stay on the operation. Generated compiler positions and internal demand identities are program-owned. There is no second model-maintained candidate response or independent demand run.

An action goal preserves a prescribed action under its conditions. It does not
automatically preserve every current argument. For example, the actual body
argument is the target; the same element's `summary` is the expected original
value. A whole-record body cannot become required merely because it is present
in the current annotation.

Prohibitions and constraints remain linked to their requirements. They do not
create a positive demand to read or deliver prohibited content. Requirements
without a usable goal are reported rather than silently dropped. A retained
textual restriction is not automatically a proved executable predicate.
Reports distinguish demand-driving requirements from a shared retained-restrictions
section. Every sink links to that section; listing a restriction does not establish
its applicability to a particular sink or prove that it was satisfied.

Direct CFG targets and program-derived operation coordinates retain actual IR operands and raw specification positions, including repeated input uses and `for_each` scope. Candidate authors
do not predict generated model-observation indices. The verified compiler map
connects the raw positions to compiled operations.

### Explicit computation supplements

Existing `select_part`, `build`, exclusion, and update relationships are reused.
Only computations and predicates that are otherwise opaque need a supplement:

```text
ref / literal / field / present / count
eq / ne / lt / le / gt / ge
not / and / or
```

Expressions cite frozen source ranges. `present` distinguishes absence from a
present `null` value. Boolean conditions do not use implicit truth conversion.
`count` means collection cardinality; it does not silently mean successful
processing count. An unsupported or unspecified computation retains related
inputs conservatively. An invalid reference or malformed expression is an input
error, not an invitation to guess a rule from an opcode or output name.

## 2. What is propagated backward

Demands attach to operation inputs or outputs, their data versions, and scopes.
They are not one global set of necessary Data IDs. The same field can be required
for model-side filtering but unrelated to the notification tool's payload.

| Relationship | Backward treatment |
|---|---|
| Reference, public output, ordinary return | Preserve the actual referenced value and version; return needs no fabricated output or sink event. |
| Field selection | Translate the selected result demand to the corresponding parent path; do not demand the entire parent value. |
| Construction | Translate demanded members to their source values; keep inclusion guards separate from payload values. |
| Exclusion | Preserve demanded remaining content without reviving excluded fields. |
| Field update | Use replacement values for updated paths and the original base only for unaffected paths. |
| Filtering | Preserve demanded member content, the selection predicate, and relevant membership/order/pairing structure. |
| Cardinality | Preserve size and membership conditions, not automatically every member value. |
| Comparison and Boolean operations | Preserve the requested truth result; retain relevant operands conservatively where no finer rule is supported. |
| Opaque computation | Follow the required result back to its relevant inputs and mark conservative retention. |
| Read/write | Follow actual position and reaching-write relations; strong overwrite and deletion kill old associations, while weak updates retain candidates. |
| External response | Preserve acquisition and request association without projecting response field demand onto similarly named request fields. |
| Delivery | Use task parameter relationships or the receiving processing segment's demand, not all existing payload as a seed. |

The work queue joins demands from all task-relevant consumers and propagates
changes to a stable result. Paths and expressions are bounded by the supplied
materials; a relationship that cannot be closed precisely is retained
conservatively or reported as an explicit limitation. There is no success claim
based only on reaching an arbitrary iteration limit.

Excluded paths are relative to the current demanded value's root. Selection,
construction and field updates translate them between container frames; an
exclusion cannot silently keep the old outer path after entering a member.
Nested membership and cardinality demands likewise continue into constructed
members rather than stopping at a known outer object shape.

The v1 demand domain has one element scope. If a reverse selection would place
that scope below another container path, the analysis retains the selected
collection conservatively and emits a precision diagnostic. It does not flatten
that relation into a fictitious exact field path. An append whose earlier
content cannot be mapped precisely retains its added payload and reports the
prior-content limitation; it does not authorize deletion of earlier content.
Expression supplements cannot refer outside their indexed local scope; unsupported
future-local expressions are rejected rather than bypassing scope checks.

Control conditions are retained when they govern a demanded task result or
behavior. Branch candidates and partial order remain candidates. Element-local
recipient and body relationships are never recombined across instances.

### Downstream information must not disappear

Consider a model that filters on `urgent`, then passes `recipient` and `summary`
to a tool. The tool's payload demand can be limited to its two arguments. The
model-side demand must additionally include the information required for the
filter. The analysis cannot remove that information at the observation boundary
and continue using the original filter result.

This is an invariant of the backward rules, not a second reduction-verification
pipeline:

- A demanded intermediate output must retain the information required by its
  producer; cached original outputs do not bypass reverse dependencies.
- A whole Data object in the registry is not a new receiver input channel.
- Parent links, provenance, and `possible` influence describe relationships;
  they do not give a model or tool access to information it did not receive.
- Model observations are associated with actual raw processing segments and
  verified compiler mappings. The slicing layer's `observed_use` relation alone
  does not establish receiver availability.
- Explicit local processing with limited return values keeps internal demands
  on the local side. The analysis does not invent that isolation for a default
  or model segment.
- A cardinality demand does not authorize replacing a collection by an integer
  or assuming that counting already happened before the boundary.

## 3. Reading a sink comparison

Every actual sink is included regardless of boundary level or an
action-necessity prefilter. The output keeps three business sections: task
goals, shared derivations, and per-sink comparisons. Existing Data and operation
references are reused instead of copying full IN/OUT states or evidence chains.

The internal demand result remains `skillflow-demand-v2`. Its derivation map uses each key as identity, without a duplicate `id`. Task is v2. The formal DOE run saves demand support once in its audit directory, including non-sensitive demands; it does not create an independent demand run.

For each sink inspect:

1. The actual ordered payload slots and their candidate data versions.
2. The task requirements linked to this boundary.
3. The information demanded by supported relationships.
4. Conservative retention and explicit analysis limitations.

Distinguish these statements:

- **Supported demand:** a rule traces information to a task-preservation goal.
- **Conservative retention:** the current relation does not justify a smaller
  range; this is not proof of indispensability.
- **No established demand:** the covered analysis has not connected a range to
  a task goal; missing requirements or unsupported relations can prevent any
  deletion conclusion.

Saving may itself be a required task result even when no later read exists.
Earlier observation is not undone by later cleaning. An external response cannot
be treated as guaranteed unchanged after deleting part of its request. `possible`
influence is not proof of plaintext inclusion.

Sensitivity is not inferred here. An absent demand is not alone a DOE verdict,
and retaining every input conservatively is not a claim that the exposure is
minimal. New processing mechanisms are not synthesized or added to the facts.

## 4. Formal integration and offline testing

`prepare_demand_review(materials, task, annotation, candidate)` remains the read-only solver interface. `materials` is a verified `PropagationMaterials` object; the compiled annotation and source map connect demands to actual observation and operation positions. No string parsing of provenance substitutes for those relationships.

The formal `run_doe(propagation_run, run_dir=...)` projects demands from the accepted annotation and invokes the solver once. See [pipeline commands](joint-pipeline.md). The former demand prepare/replay command, run wrapper and baseline scheduler are retired. Tests may author explicit candidates in memory, but do not impersonate accepted model responses.

The final DOE manifest binds the exact relative propagation dependency. Ordinary reading checks content; recomputation additionally checks implementation identity. Replay calls no API and writes no duplicate final result. Historical three-case materials remain unchanged; current regression fixtures explicitly reconstruct equivalent declarations only for offline relationship checks.

## 5. Three-case review boundaries and acceptance

- **001:** Keep the selection predicate and same-element original fields.
  Processed count remains opaque because the source does not establish that it
  equals selected cardinality in every execution. This conservatism can keep
  more record content demanded than the notification arguments need.
- **010:** Keep optional values distinct from existence controls, omission
  distinct from `null`, and response `total` distinct from returned `items`.
  Presence supplements describe the existing flag computations only.
- **013:** Keep request/environment origins, credential routing, first/retry/
  archive identities, restrictions, and every terminal append. Outcome
  classifiers remain conservative instead of guessing a concrete response
  status schema.

Acceptance covers field and control rules, unchanged receiver scopes, genuine
source/target references, immutable input hashes, deterministic queue scheduling,
tamper detection, and zero-API replay. A true source span can still accompany a
wrong semantic interpretation; reference validation is not semantic validation.

The completion claim is limited to task-driven demand propagation and
traceable sink comparisons under the supported declared relationships. It is
not a proof of natural-language equivalence, action/value irreplaceability,
global minimum exposure, or final DOE correctness.

</details>
