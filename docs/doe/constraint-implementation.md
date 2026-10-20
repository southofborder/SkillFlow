# Constraint implementation reference

Current implementation: 2026-10-19. This document records the bounded implementation of [constraint semantics](constraint-semantics.md), its [44-case semantic matrix](constraint-acceptance.md), and offline engineering evidence. It is not a claim that all source restrictions are expressible, all matrix preservation expectations are implemented, or a real Skill has been proven compliant. No remote model call or historical run migration was used for the measurements below.

## Ownership and analysis flow

The source-only Task remains sealed and unchanged. Fixed-Task annotation can express supported restrictions in the corresponding realization. The existing semantic reviewer checks those declarations together with source, requirements, positive demands and all IRs. There is no additional semantic model role or call. Four responsibilities remain distinct:

| Responsibility | Inputs and output | Boundary |
|---|---|---|
| Forward actual facts | Declared processing, compiled observations and frozen CFG produce actual abstract Data candidates, operations, scopes and exposure records. | A normative ban or count limit never deletes a field, inserts a guard, or prunes an actual operation. Static possible facts are not runtime observations. |
| Baseline constraint checker | Typed declarations plus the original fact index produce model-relative checks and witnesses. | The checker does not create demanded information, infer sensitivity, or rewrite the Task. |
| Backward positive demand | The six existing preservation properties seed per-goal demand derivations. | Pure constraints have no positive seed. Information inspected to check a ban does not become content the receiver must obtain. |
| Candidate preservation gate | An otherwise eligible exact `exclude_field` candidate is checked against every declared constraint using structural or forward-change rules. | Baseline compliance is not preservation. Failure to prove preservation is neither necessity nor a violation proof. |

The sensitivity comparison first applies all existing candidate requirements: a directly present declared sensitive field value, supported positive demands at that payload slot, disjointness under the existing rules, and no relevant blocking limitation. Only an otherwise supported field exclusion enters the constraint gate. If any required preservation result is missing, the candidate becomes `no_excess_established`; constraints do not broaden eligible actions or payload ranges.

Remaining realization gaps and unresolved Task issues retain their existing global conservative treatment. A supported declared constraint can have an unresolved baseline check and a separately complete preservation proof for one candidate. That proof does not release a different gap or certify the baseline.

## Declarations and references

The raw annotation gains only optional `realizations[i].constraints`. Empty lists are omitted by normalization. The enclosing realization owns `requirement_id`, source correspondence and gaps; each constraint contains no duplicate requirement text, evidence, ID or verdict. Strict validation rejects extra fields such as `safe_to_remove`, `proof` or model-created constraint IDs.

Every variant requires `scope`:

- `{"kind":"task"}` selects one task invocation, from the actual CFG entry.
- `{"kind":"element","instruction_id":"...","scope_path":["events",0]}` selects an existing single-level raw `for_each`. This is an existing member occurrence scope, not an arbitrary group key or a reset instruction.

`EventRef` reuses either `InstructionTarget` with `path: []`, or raw `OperationTarget` with `slot: {"kind":"self"}`. An operation path addresses the original annotation, including declared receive operations. It does not predict inserted observation positions. Event lists are nonempty and unique; one list cannot overlap a whole instruction with one of that instruction's atomic operations. A whole-instruction event counts that instruction occurrence once, regardless of how many request, response or observation steps its compilation contains.

Element-scoped event and expression references must resolve within that exact raw member scope. A whole-instruction target cannot stand for one member occurrence; use the corresponding raw member-body operation.

| `kind` | Fields in addition to `scope` | Meaning and validation |
|---|---|---|
| `forbid_information` | `source`, `path` (default `[]`), `receivers`, optional `events` (omitted/null means all applicable operations in scope) | Original-content prohibition over a scoped value/range. `source` is `{instruction_id, scope_path, value: ValueRef}`. Receiver selector is `{kind:"all"}`, `{kind:"locations", ids:[...]}`, or `{kind:"kind", value: LocationKind}`. |
| `only_if` | `events`, `condition: DemandTarget` | Each selected occurrence requires the referenced normalized Boolean expression. Its values must be available before that occurrence in the correct version and element scope. |
| `at_most` | `events`, `limit`, `unit`, optional `success` | `limit` is a strict nonnegative integer. `unit` is `attempt` or `success`; `success: DemandTarget` is required exactly for success counting. The expression is evaluated at the counted completion and may use that event's own output. |
| `requires_prior` | `before`, `after`, `matching` | Every selected `after` requires an earlier selected `before`; `matching` is `scope` or `request`. Request matching uses existing unique pairing, not predicted call IDs. |
| `forbid_after` | `triggers`, `events` | No selected event after a selected trigger in the declared scope. It does not require a trigger or event to occur. |

`source.scope_path` is `[]` for the IR frame or `["events", index]` for its existing member frame. Locals are checked against lexical definitions; an element local cannot escape into another member scope. Resource identities cannot stand for retrieved information content. Conditions and success references must resolve one existing normalized expression; copying an expression into a constraint is unnecessary. Structurally known non-Boolean literals are rejected; raw reference validation alone is not a proof that an indirectly resolved value is Boolean. Known or mixed non-Boolean Data candidates in a Boolean position yield `not_established` in the checker. Opaque Boolean predicates can remain abstract atoms; unsupported or unavailable values do not acquire invented truth values.

The receiver-kind alternatives are the existing `runtime_context`, `storage`, `model_context`, `remote`, `tool` and `user`. Named receiver IDs must exist in the raw locations table. Generated model observations can be selected by `model_context`; the model must not guess the compiler's generated location ID.

The `path` syntax reuses `SensitivityPath`, including field names, positions and `each`; its meaning here is neutral original-content membership, not a sensitivity classification. A ban on an original whole covers content projected from that whole. Exclusion and independent overwrite remove the old original range. Possible or derived influence is retained without becoming proof of plaintext containment. Nested `each` syntax is not a promise of checker support.

An explicitly selected child also remains original content of its original parent whole. A prohibition naming that child can therefore match an earlier observation of the whole. This is content identity through a declared selection relation, not reverse execution or resurrection of the child after exclusion/overwrite. The actual delivery version determines whether the old original range is still present.

`expressed` and `partial` realizations require a positive demand or a nonempty constraint list. `expressed` has no gap; `partial` retains its unsupported remainder. `retained_only` and `unmapped` carry neither demands nor constraints. A compound source requirement must account for both positive and restrictive parts; the existence of one declaration does not prove completeness.

## Compilation, review and persisted results

[Contract validation](../../src/skillflow/propagation/contracts/constraints.py) resolves raw CFG/operation references, lexical source scopes, normalized expressions and receiver identities. [Compilation](../../src/skillflow/propagation/annotation/compiler.py) keeps the constraint declarations in compiled realizations with their raw references intact. It adds mapping entries with exactly `constraint_id`, `requirement_id`, and `raw_pointer`. IDs are program-generated from the sealed Task identity and pointer, for example `/realizations/1/constraints/0`; they are not semantic proof IDs supplied by the model. Verified loading recompiles raw material instead of interpreting raw operation paths as compiled coordinates.

Review retains four coverage axes: source, requirement, declaration and IR. The third axis is now `declaration_checks`, covering both positive demands and constraints exactly once by raw pointer. Its `declaration_index` has discriminated `kind: demand|constraint` rows. A constraint row contains identity and pointer only; the body already exists in `raw_annotation`. Missing restrictions are reported through the requirement and existing realization parent, not an invented pointer. A faithful Task with a missing declaration is an annotation issue; a missing source restriction in Task follows the existing isolated source-only Task revision path.

The [demand result](backward-demand.md) stores `coverage.requirements[].constraint_ids`, not duplicate constraint bodies. `goal_ids`, `has_applicable_goal`, and `seed_goal_id` remain about positive demands.

The [sensitivity result](sensitivity.md) adds one shared `constraints` object:

| Map or reference | Stored content |
|---|---|
| `checks[constraint_id]` | Requirement ID, raw pointer, kind, baseline status, applicable operation IDs, reasons, operation witness, and a program-computed `structural` flag. |
| `preservation[preservation_id]` | Constraint ID, exact operation/input slot/Data ID/path, `preserved`, rule, reason, and `influence_refs`. |
| `influence[change_id]` | Existing `DemandNode` coordinates and Data references, changed path, rule, parent change IDs. This is a shared derivation table, not another Data snapshot or positive demand graph. |
| `data_reviews[].constraint_refs` | Preservation rows for that candidate, separate from positive `demand_refs`. |

Baseline statuses are `satisfied`, `potential_violation`, and `not_established`. Direct original-content candidates and abstract temporal bad paths both use `potential_violation`; their reasons distinguish what the facts support. A stored witness is a set/list of indexed operations, not an observed runtime trace. A `complete` analysis result means the required supported analysis completed; a potential violation can still be present.

The [result validator](../../src/skillflow/doe/sensitivity_material.py) reconstructs the read-only index from verified inputs and calls the same `ConstraintAnalysis` evaluator used by candidate generation. It checks baseline results, exact preservation coverage, references and shared change steps. This avoids a second, weaker acceptance predicate. It does not execute a changed Skill or solve a second set of positive demands. Frozen propagation facts remain unchanged; namespace-bound IDs may change when annotation identity changes, so fact-preservation regressions compare corresponding operation slots and Data relationships rather than assuming cross-annotation ID equality.

## Supported checks and preservation rules

[ConstraintEngine](../../src/skillflow/doe/constraint_engine.py) starts at the actual task entry. Disconnected propagation coverage roots remain auditable facts but do not become extra task invocations. It enumerates supported local partial orders and CFG alternatives, maintaining finite saturated counters or seen-event state. Alternative branches are not added together. Repeated data values do not collapse member occurrences. The default monitor state budget is 20,000; resource exhaustion yields an explicit incomplete result.

[BooleanFacts](../../src/skillflow/doe/constraint_control.py) interprets the supported normalized expression fragment, preserving value version, member identity and compatible predicate/negation assignments. A future local or a value from another invocation cannot justify an earlier guard. Unknown branches overapproximate possible behavior; an overflow state is a potential violation, not proof of a feasible execution. Task-wide counts through member collections depend on collection multiplicity, so even a satisfied empty-collection count is not marked structural.

A definitely absent field or invalid field access in a Boolean position is `not_established`, even in an expression shaped like a tautology. It cannot become an invented Boolean atom. A field whose value is opaque and unknown may remain an abstract Boolean under the supported expression contract; this does not supply a concrete truth value.

Operand checking is recursive through `ref`, `literal`, `field`, `present`, `count`, comparisons and Boolean operators. `present` alone converts a missing field to false; an existing null, false or zero value is present. Invalid field access is unsupported. A count consumes a list, not a known object or scalar, even when the count is nested inside a comparison or tautology. Existing transparent container facts and normalized producer expressions retain their known types. Internal typed-unknown markers carry type evidence without reconstructing JSON values; an opaque candidate stays unknown, and a known alternative never discards a separate opaque alternative. Equality preserves strict types recursively inside arrays and objects.

[ContentRanges](../../src/skillflow/doe/constraint_ranges.py) tracks original ranges independently of sensitivity labels. Information constraints include applicable internal writes and generated observations even when the operation is outside the DOE sink list. Their checks do not promote a level-0 operation into a sink. Proven complete empty scopes can satisfy a universal constraint; unresolved selectors or missing records cannot.

[ForwardInfluence](../../src/skillflow/doe/constraint_preservation.py) starts at the exact candidate boundary input and path, leaving the shared source and other receivers unchanged. It follows symbolic use, selection, construction, exclusion, overwrite, opaque output, control, public output, compiled observation, request/response, and reaching saved-write/read relations. Weak updates and ambiguous potential effects stay conservative. Changed values are not materialized as replacement Data and the reduced Skill is never executed.

Path overlap uses the existing symbolic member rules: an `each` range can affect a selected fixed member. Exclusion and overwrite stop propagation only when they directionally cover the changed range; replacing one fixed member cannot erase possible change to every member. These are change-propagation facts, not proof that each possible influence contains original plaintext.

The gate records one of three positive rules, or `not_established`:

- `structural`: a temporal property holds under the complete additional check abstracting away value guards, with fixed event identity/task scope and no changed member collection. It is not inferred from baseline `satisfied` alone; request matching and cardinality-dependent task counts do not receive this shortcut.
- `terminal_subset`: for an original-content prohibition, the exact delivery only loses content and the complete modeled effect closure contains no other affected operation. Generated observations and unpaired opaque tool/remote deliveries do not gain terminality from a missing response record.
- `no_influence`: a complete closure cannot affect the constraint's relevant content, evaluated condition, event occurrence, control, identity or scope. Payload change alone is not automatically an action occurrence change. A baseline violation or uncertainty remains visible when an independent candidate passes.

## Explicit limits

- Arbitrary grouping/reset keys, nested member quantification, cross-task counters, cross-member shared-state scheduling and task-wide member ordering are unsupported. Element-scope CFG revisits cannot be treated as fresh resets of the same member.
- Changed collections may create new occurrences, change multiplicity or invalidate member pairing. The raw member template is tracked even when baseline instances are empty. Such a change currently prevents a complete influence proof; baseline absence cannot discharge it.
- Request precedence needs a uniquely grounded pair and an earlier occurrence. Pairing alone is not order. Repeated CFG occurrences that need fresh invocation IDs are unsupported. Counting both a request and its paired response as separate selected attempts is ambiguous; a whole-instruction selector is counted once.
- Success conditions that require a later separate event need a deferred completion monitor, which is not implemented. A completion event's own output is supported; an unavailable future response is not assumed available.
- Any-causal-influence prohibition is stronger than original-content prohibition and is not expressible by adding an arbitrary field. Unsupported source meaning must remain a gap, not be silently weakened.
- Unresolved conditions, incomplete operation coverage, unknown collection multiplicity, unsupported nested content paths and finite resource limits remain explicit limitations. Unexpected implementation errors propagate rather than being converted into apparent semantic success.
- A declaration's selector cannot prove it covers every source occurrence. Semantic review remains responsible for omissions and wrong scope. Reference validation and deterministic tests do not prove that review or extraction is complete.

## Current versions

These are current interfaces; frozen older artifacts retain their own versions and are not automatically relabeled.

| Interface | Current version |
|---|---|
| Sealed Task / Task reference | `skillflow-task-v3` / `skillflow-task-reference-v1` (unchanged) |
| Abstract runtime contract | `skillflow-abstract-runtime-v7` (unchanged) |
| Annotation material and profile | `security-profile-v15` |
| Processing compiler / compilation mapping | `skillflow-processing-compiler-v9` / `skillflow-processing-compilation-v9` |
| Annotation run | `skill-ir-security-profile-v18`, format 18 |
| Review schema | `annotation-review-v7` |
| Review / refinement run | `skill-ir-annotation-review-v11`, format 11 / `skill-ir-annotation-refinement-v10`, format 10 |
| Propagation run | `skill-ir-propagation-v15`, format 15 |
| Demand result | `skillflow-demand-v4` |
| Sensitivity result | `skillflow-sensitivity-review-v4` |
| Formal DOE run | `skillflow-doe-run-v5`, format 5 |
| Source-to-DOE pipeline | `skillflow-analysis-run-v7`, format 7 |
| Joint pilot run | `skillflow-joint-pipeline-pilot-v8`, schema 8 |

No new exposure level, runtime execution mechanism, standalone reduced-program run, or model-authored result status is introduced.

## Measured synthetic material size

The complete English `envelope_restriction` fixture in [constraint_examples.py](../../src/skillflow/propagation/annotation/constraint_examples.py) was compiled locally with current `compile_response`. It contains two Task requirements, two positive goals for required label delivery, and one pure prohibition on `diagnostic_note`. The prohibition supplies none of those positive goals. These numbers were measured on 2026-10-19 using compact JSON (`ensure_ascii=False`, separators `(',', ':')`) and `len(text.encode('utf-8'))`; prompt rows measure the exact strings returned by the production prompt builders.

| Current artifact | Characters | UTF-8 bytes |
|---|---:|---:|
| Annotation model input projection | 16,882 | 16,882 |
| Normalized raw annotation | 3,776 | 3,776 |
| Compiled annotation | 5,876 | 5,876 |
| Compilation mapping | 1,762 | 1,762 |
| One normalized constraint object | 240 | 240 |
| One constraint mapping entry | 119 | 119 |
| Prepared review material | 32,817 | 32,817 |
| Full annotation prompt | 79,102 | 79,102 |
| Full review prompt | 91,742 | 91,742 |

These are current complete material sizes, not incremental old/new cost estimates. Review material and the rendered review input are different projections; a prompt includes format, rules and examples as well as its input. The rows overlap and must not be summed as a request total. This English fixture happens to have equal character and byte counts. No tokenizer, API usage, real-model success rate or corpus cost is inferred.

To reproduce, create `example = constraint_example()`, `material = example_material(example)`, then call `compile_response(example['annotation'], material)`, `prepare_review_material(material, raw)`, and the annotation/review `build_prompt` functions. Measure the named returned objects using the serializer above. Prompt changes can change the sizes even when the constraint representation is unchanged.

## Offline validation evidence

The final active suite used disjoint `tests/` partitions after the recursive type
audit and production-source freeze. All three partitions completed. Their
original results and the subsequent assertion corrections are recorded separately.

| Final partition | Command scope | Result | Log |
|---|---|---|---|
| DOE | `D:/anaconda3/python.exe -u -X utf8 -m pytest tests/doe -v --tb=short --disable-warnings --maxfail=12` | **595 passed in 1284.92 s (21:24), exit 0** | [pytest-doe.log](../../experiments/diagnostics/constraints-v1-20261019/pytest-doe.log) |
| Propagation | `tests/propagation` | **1555 passed, 2 failed in 4529.10 s, exit 1** (1557 collected) | [pytest-propagation.log](../../experiments/diagnostics/constraints-v1-20261019/pytest-propagation.log) |
| Core | `tests/common tests/graph tests/task` and all six root-level `tests/test_*.py` files | **1538 passed, 1 skipped in 4906.43 s (1:21:46), exit 0** (1539 collected) | [pytest-core.log](../../experiments/diagnostics/constraints-v1-20261019/pytest-core.log) |

The core partition's root-level files were `test_cli.py`, `test_installed_cli.py`, `test_pipeline_boundaries.py`, `test_pipeline.py`, `test_source_task_pipeline.py` and `test_task_preparation_boundary.py`. Its single skip was the existing platform-capability case `tests/common/test_upstream.py::test_symlink_input_or_parent_rejected`. The three-, five- and six-call recorded paths and task-preparation boundary cases passed.

Both propagation failures were stale assertions: `test_explicit_order.py` expected compiler v8 instead of v9, and `test_joint_evidence.py` expected the old heading `Goal checks` instead of `Declaration checks`. Only those two expected literals were updated. The complete rerun of both affected files is recorded separately below; it does not change the original partition's result. The durable constraint correction/interruption/resume/zero-API replay test passed in the full partition.

The following checks overlap the partition coverage and are recorded separately, without an aggregate sum:

| Batch | Observed result | Scope |
|---|---|---|
| Propagation assertion correction | 26 passed in 9.56 s, exit 0 | Complete `tests/propagation/annotation/test_explicit_order.py` and `tests/propagation/review/test_joint_evidence.py`; [corrective log](../../experiments/diagnostics/constraints-v1-20261019/pytest-propagation-corrective.log). |
| Final focused constraint batch after recursive type fixes | 128 passed in 52.70 s | One executed combined run: 104 baseline-checker instances (44 matrix component cases and 60 regressions), 22 preservation instances and 2 changed-member-scope instances. This is not a sum of prior batches. |
| Concurrent direct-baseline test update | 15 passed in 1.01 s, exit 0 | Complete `tests/doe/test_direct_baseline.py` after its unrelated concurrent edits; [separate log](../../experiments/diagnostics/constraints-v1-20261019/pytest-concurrent-direct-baseline.log). This is not added to the DOE partition count. |

A separate read-only peer audit of the final recursive helper checked 36 explicit operator cases with no remaining mismatch. Six real-pipeline audit assertions also passed: five invalid-use counterexamples remained `not_established`, and a mixed known-true/opaque field retained `potential_violation`. The discovered cases were provided to the maintained regression suite; these ad hoc audit counts are not added to pytest totals or treated as a complete type-soundness proof.

Final active-suite validation uses explicit `tests/` paths split into disjoint partitions. The initial repository-root discovery also collected an old test under historical `tmp/` material and failed on its retired source path. That collection failure is not an active-suite verdict. An earlier DOE run reported 159 passes and 8 identity failures while source versions were still being edited; it is not accepted as final validation. The first broad attempt, an early core attempt and an earlier propagation attempt were interrupted before final validation and are not counted as passes.

The final partition rows above supersede the earlier overlapping development batches as validation evidence. After the two assertion corrections, `compileall` over `src/skillflow` and `tools/doe`, and `git -c core.whitespace=cr-at-eol diff --check` over the full diff, passed. All local relative links in the three constraint documents resolve. Frozen historical artifacts were not modified by this task. The matrix's baseline IDs do not claim that all candidate-preservation halves or natural-language examples are fully supported.

Unrelated concurrent edits were observed in `tests/doe/test_direct_baseline.py`, `tools/doe/direct_baseline.py`, `tools/doe/direct_assessment.py` and `tools/doe/direct_results.py`; this work did not overwrite them. The production source under `src/` remained unchanged during the final partition window. The changed direct-baseline test was rerun separately as recorded above. Validation provenance distinguishes this production-source snapshot, the assertion corrections and the wider workspace; it does not claim that every monitored file stayed unchanged. Those external tools are outside the formal implementation identity.
