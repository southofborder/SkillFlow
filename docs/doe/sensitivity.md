# 敏感范围与接收边界对照 v3

当前协议（2026-10-15）由独立 Task 提取确定任务基准；后续标注在固定 Task 下声明保持目标、处理事实、可见性和敏感范围。确定性分析联合前向暴露、逐 seed 反向需求和敏感关系，在每个实际形成记录的 sink 比较具体接收方取得的信息。不增加敏感性分类或最终 DOE 裁决模型调用。

## 声明与关系

敏感声明使用已有词法 `ValueRef`，保留 `value / path / property / label / evidences`。`property` 为 `value / presence / cardinality / shape / truth`；`path` 可以包含单层 `{kind: each}` 成员范围。普通输入、局部值、元素实例和版本不能混用，资源名不能冒充已读取内容，也不能预测未来 Data ID。

来源采用冻结文件及物理行号，程序验证其存在；真实引用不证明敏感性标签正确。空声明只表示没有显式声明，不表示未展开内容不敏感。当前覆盖范围限定为已有声明，不凭空创造其他凭据或标签。

传播区分直接内容、派生信息与可能影响。字段选取、排除、覆盖、构造和筛选保留明确局部关系；输入来源不能复活已删除字段。不透明处理可保留影响，但不能推断原始敏感明文必然在输出中。`possible` 不等于明文包含，处理名称也不能自行证明敏感性消除。

嵌套 `each`、缺失敏感值路径、未知生产记录等产生能力诊断；可以声明有效父对象下末级成员的敏感存在性，但不能创造缺失的中间容器。计数不自动复制成员凭据；成员出现的控制影响也不自动成为明文载荷。

## 每个 sink 的比较

比较以实际参数位置、接收方、元素、条件和数据版本为单位，不把同一 Data 在所有接收边界的需求合并。构造条件和条件观察的 guard 继续与实际载荷分开。

| 结果 | 限定含义 |
|---|---|
| `excess_supported` | 直接存在的敏感字段值与全部适用保持需求不重叠，且没有相关限制；当前规则支持所记录的字段排除建议。 |
| `possible_excess` | 仅建立派生或可能影响关系，不能据此断言原始敏感明文存在。 |
| `no_excess_established` | 当前未建立支持的缩减结论；不证明必要性或不存在 DOE。 |

没有正向需求不构成删除许可。全值、结构或成员范围也不自动对应字段删除。`action` 需求不会豁免全部参数；全部 sink 都保留在审计范围，包括不必要动作产生的暴露。

未表达要求、未解决的 Task 歧义／冲突，以及相关分析能力限制，都会约束缩减结论。当前未形式化 gap 的影响按全局保守处理；任意 model binding 不能证明局部。受限结果仍保留诊断计算，但不能升级为 `excess_supported`。

## 结果、审计和恢复

`skillflow-sensitivity-review-v3` 保存接收边界对照及必要推导闭包。需求推导保留 `seed_goal_id`；完整需求和来源映射在同一个正式 DOE run 的审计支持文件保存。Task 与敏感声明由接受的上游拥有；DOE 不回写冻结输入、处理事实和历史结果。

传播的 `provenance.kind=model_annotation` 只说明处理标注来自接受的响应，不能代替 Task 来源。`task_provenance` 单独记录 `independent_task_run / authored_fixture / unknown` 和精确 `task_sha256`；独立来源须来自完整核验的 Task run 引用，仅有描述性来源标签不能成立。正式 DOE metadata 与报告保留这项区别，并在加载时从受验证上游重新核对，不能通过重新封存 metadata 把人工 Task 改写成独立提取记录。模拟客户端即使拥有完整记录也不提供真实模型效果证据。

正式 DOE run 为 `skillflow-doe-run-v4`，保存单份 `doe-result.json`、索引、需求支持文件和报告。统一加载器检查完整依赖链、Task seal、编译映射、源行投影、推导引用和 artifact 摘要；加载不重新求解，replay 才按冻结输入重算。旧格式拒绝，不自动补造新版覆盖审查。 早期当前 v4 运行若没有新增的 `task_provenance` metadata，仍按原字段只读校验，来源只在加载返回视图中重新派生，缺字段不解释为独立来源，也不回写历史文件。

示例 `python -m examples.doe.joint_analysis_demo --show result` 使用独立校准记录，人工声明敏感 serial 和 label 结果需求，不联系模型，也不是实际 Skill 的语义评测。

## 工程与效果证据

结构测试、模拟客户端和离线重放证明协议及确定性规则按预期运行；不能证明模型能完整提取所有限制或拒绝所有过宽需求。真实语义效果需在独立人工基准上逐类报告遗漏、过宽目标、错误位置／版本／接收方的检出、漏检、误报和修复结果，包含真实全值要求及正确目标导致保守整值反推等反例。

单一审查、复审和更长提示词可能增加发现机会，但共同盲点仍在。敏感声明、CFG、处理关系、外部事实、路径可行性及全局最小性都没有因此得到证明。

## 历史版本（已被上文替换）

以下保存先前协议，便于解释历史实验；不作为当前接口或保证。旧的“同次生成 Task”、constraint/prohibit 正向 goal、仅 IR 清单审查和四调用分工均已由上文替换。

<details><summary>展开历史规范</summary>

# Sensitivity v1: declarations and sink-demand comparisons

Sensitivity v1 attaches evidenced information ranges to existing symbolic
values, propagates those declarations through recorded content relationships,
and compares them with task-driven demands at each sink. It does not run a
Skill, request a new model judgment during propagation, search all alternative
implementations, or prove sensitivity completeness.

The production path uses the same joint annotation for task interpretation,
processing relationships, and sensitivity declarations. An explicit offline
candidate remains available for reproducible examples and controlled tests.
The candidate's origin is always recorded; an assistant-authored reconstruction
is not relabelled as an accepted model response.

## Responsibilities

```text
Joint semantic annotation
├─ Task and evidenced preservation goals
├─ Existing processing operations and visibility boundaries
└─ Sensitivity declarations on lexical values and information ranges
             ↓
Deterministic analysis
├─ Recorded forward data and exposure relationships
├─ Backward demands under the supported task-preservation rules
└─ Declared sensitivity → sink payload → receiver-specific demand comparison
```

Task goals do not turn every existing payload into a requirement. A sensitive
field's parent, input provenance, or possible dependency does not create a new
content channel to the receiver. Both principles continue to apply when a
value is sensitive.

## A declaration refers to a value, not to an executed exposure

Declarations belong to an IR's lexical scope or an existing `for_each` scope.
They use the existing `ValueRef`; they do not invent future Data IDs or use a
resource identifier as if it were acquired content.

```text
SensitivityDeclaration
├─ value                  Existing input, local, literal or alternatives reference
├─ path                   Field/index path; {kind: each} denotes member ranges
├─ property               value / presence / cardinality / shape / truth
├─ label                  Evidenced English category; not a numeric risk score
└─ evidences[]            Frozen file + inclusive line range + explanation
```

For example, a declaration on a file-read local with the path
`[{"kind": "each"}, "access_token"]` identifies that field in members of the
original collection. It does not declare every record field sensitive, does
not identify the first runtime array item, and does not establish that all
members are actually sent. A declaration in a `for_each` body retains that
scope's element identity and cannot escape into another iteration's values.

Skill and independent user-request references use exact frozen spans. The program checks
that the file and range exist. A genuine excerpt does not itself prove that its
interpretation or chosen category is correct. No external policy input or policy evidence namespace is retained.

An empty declaration list means that no sensitive range was declared in that
scope. It is not a finding that the scope is nonsensitive. Unknown remainder
content remains unknown; the analyzer does not invent names for sensitive fields
that were never described.

## Propagation and comparison boundaries

Sensitivity propagation preserves the existing distinction between direct
content, derived information, and possible influence. Original values and
explicit field relations can retain a direct range. Filtering preserves member
content and element identity. Exclusion, replacement, and construction must
respect their recorded paths; an excluded or overwritten value cannot be
revived merely through its input provenance. Opaque processing can preserve
influence without asserting that plaintext survives.

Only a single member-range scope is supported; nested `each` declarations
produce a capability diagnostic. A whole-value declaration projected to an
otherwise unclassified proper subfield retains possible influence rather than
certifying that subfield as sensitive. Known-absent value paths are diagnosed;
an evidenced presence declaration may describe an absent final member of a
valid parent, but cannot create an absent intermediate container.

Existing supported expressions constrain influence: counting a collection does
not copy member credentials into the count, while explicitly declared sensitive
cardinality remains relevant. A sensitive build guard can influence inclusion
without becoming a plaintext member or a new independent sensitivity label.

The analysis compares the declaration with the actual payload slot at a
particular operation, receiver, scope and version. It does not union all demands
for the same Data ID across receivers. Build controls and conditional-observation
controls remain outside the delivered payload.

Three conclusion labels have deliberately limited meanings:

| Label | Interpretation |
|---|---|
| `excess_supported` | A directly retained field range has a supported field-exclusion reduction under the current task-demand rules and without a relevant analysis limitation. |
| `possible_excess` | An influence relationship may carry declared information beyond the established retention, without proof of plaintext content. |
| `no_excess_established` | The current analysis did not establish a supported reduction for this declared range. This is not a proof of necessity or of no DOE. |

Only `excess_supported` records an executable-shaped reduction description,
currently `{"kind": "exclude_field", "path": [...]}`. A direct whole value,
structure-only demand, missing positive demand basis, opaque retention, or a
relevant limitation cannot be promoted to supported field deletion merely
because no exact overlap was found. Actual missing analysis can make the run
partial. Ordinary conservative relations do not become an artificial failure.

These are conclusions relative to the recorded processing relationships and
supported demand rules. They do not claim global irreplacability, measured
runtime disclosure, or that an alternative implementation has been explored.

The first comparison rules deliberately retain a range under an overlapping
structure-only demand. In particular, a collection-cardinality demand can still
block deletion of a descendant field even when a more precise proof could show
that the deletion preserves length. This is a precision limitation, not a
finding that the field is indispensable. No new representation or transformation
is synthesized to overcome it.

## Result organization

```text
SensitivityReview
├─ schema_version = skillflow-sensitivity-review-v2
├─ status                         complete / partial
├─ sinks[]                        Every recorded sink, including empty comparisons
│  ├─ id / boundary / actual_payload
│  ├─ related_requirements
│  ├─ data_reviews[]
│  │  ├─ id / operation_id / input_index
│  │  ├─ derivation_id
│  │  ├─ conclusion / reason / reduction
│  │  └─ demand_refs
│  └─ limitations
├─ derivations
│  ├─ sensitivity                Shared declared-range propagation
│  └─ demand                     Shared task-demand derivations
├─ diagnostics
└─ coverage                       Declaration coverage, not nonsensitivity coverage
```

The compact v2 result has one owner for each information range. A data review
resolves `data_id`, `label`, `property`, `path`, `excluded_paths`, `relation`,
and `declaration_id` through `derivation_id`. Applicable limitations come from
its sink. These fields cannot be supplied again on the review, even with equal
values. `resolve_data_review` produces an isolated internal view for both
validation and rendering; it never rewrites the stored result. `input_index`
remains the original operation slot, including gaps for excluded control slots.

Sensitivity and demand derivation maps use their dictionary key as the identity;
their values do not repeat `id`. Loaders still verify complete receiver-specific
demand sets, parent closure, actual payload/version membership, every expected
sensitive-range review and the conclusion/reduction rule. Non-sensitive demand
support remains in the formal run's audit material, including cases with no
sensitivity declarations. Compactness does not authorize dropping unmet goals,
conservative demands or limitations.

Data IDs and original operation coordinates refer to the frozen fact input.
The result does not carry a second DataRegistry or copy source evidence into
each sink comparison. Declaration evidence lives in the frozen candidate/index,
and report excerpts are extracted from frozen source text. Counts are range
comparisons, not unique leaks or observations of actual executions.

## Formal service and offline tests

```python
materials = load_propagation_materials(propagation_run)
review = prepare_joint_sensitivity_review(materials, materials.annotation)
```

The formal persisted service is `run_doe(propagation_run, run_dir=...)`. It projects Task, demands, expressions and sensitivity from the same accepted joint annotation and computes demand only once. `annotate_skill(source, cfg, client=client, user_request=None)` keeps the injectable `complete(prompt)` interface; structural correction and at most one semantic repair remain distinct.

```text
python -m skillflow.doe run --propagation-run <run> --run-dir <new-directory>
python -m skillflow.doe replay --run-dir <directory>
```

DOE run identity is `skillflow-doe-run-v3`; the result remains `skillflow-sensitivity-review-v2`. It saves `doe-result.json`, reports, its manifest, `audit/index.json` and `audit/demand-support.json`. It references upstream rather than copying all source, CFG, accepted calls, annotations or final Data. Independent slice/Task/demand/sensitivity run wrappers and schedulers are retired; their underlying algorithms remain testable in memory.

The relative upstream address and manifest digest are explicit. Moving the complete dependency tree is supported; missing dependencies fail without name-based fallback. Ordinary loading checks content and declarations, while regeneration also checks implementation identity. Matching interrupted preparations can resume; no manifest commits partial results as complete. Replay is offline and does not save a second result.

## Three explicitly authored examples

The baseline uses the previously verified `backward-demand-v1-20261011-215237`
materials for 001, 010 and 013. Because the joint annotation format has changed,
the experiment reconstructs new current-format candidates with explicit
provenance and differences. It preserves the old verified receipts and original
historical bytes; it does not provide a production compatibility parser.

| Case | Declaration | Review emphasis |
|---|---|---|
| 001 | Original collection member's `access_token` value | Whole-input/model observations, filtering, original field delivery and element pairing. |
| 010 | No source-grounded sensitive category declared | Preserve all sinks and unknown remainder; do not manufacture a nonsensitivity certificate. |
| 013 | Environment's `FAST_KEY` value | Whole environment versus selected credential, preferred-tool use, fallback/status boundaries and possible response influence. |

`tools.doe.prepare_sensitivity_baseline` prepares the reconstructed demand inputs,
declared sensitivity analysis, zero-API replay, and a linked English overview.
The baseline never mutates the earlier Task, annotation, propagation, or demand
runs. Its candidate declarations and assistant opinions are not independent
ground truth.

The [frozen Sensitivity v1 baseline](../../experiments/doe/runs/sensitivity-v1-20261011-231751/index.html)
contains all 34 sinks and each case's result, source evidence, demand derivations,
reconstruction record and zero-API replay. Its range counts must not be read as
unique real-world disclosures. The earlier intermediate run is retained as
development history and is not this round's delivery.

The runtime contract's EM08 excludes *propagated sensitive-data sets* from model
annotation. It does not prohibit the evidenced symbolic declarations introduced
here: the model names an existing value and range; the deterministic analyzer
resolves which Data versions and sink slots carry that information. The runtime
contract itself is unchanged in this round. Model adherence to this distinction
has not been measured by a new remote experiment.

## Verification boundary

The joint schema is `security-profile-v12`, annotation runs use format 13, and
the processing compiler/mapping is v6. Current raw responses require one Task,
CFG task goals and CFG expressions. Per-IR semantics now have one `ir_semantics`
entry containing operators and ordered effect events; no parallel profile or
`roles` projection exists. Response-created operations carry their
own goals and supported expression. The compiler normalizes those declarations
into one `demand` and removes the raw-only wrappers from compiled operations.
No generated sensitivity or task evidence is copied into Data annotations.

Focused tests cover exact declaration spans, invalid scope/value references,
candidate projection, content/influence distinctions, every-sink coverage,
receiver-specific demand comparisons, exclusion and overwrite relations,
conditional payloads, deterministic replay, interruption, tamper rejection,
isolated output paths, and HTML/Markdown escaping. Rule and persistence tests
establish engineering consistency, not semantic completeness of the annotation.

The retained task restrictions remain review context when no executable rule
has been supplied. Neither source-reference validation nor a complete analysis
status proves those predicates, the accuracy of a sensitivity label, or the
absence of undeclared sensitive information.

</details>
