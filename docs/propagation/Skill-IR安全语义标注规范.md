# Joint IR semantics (v13)

The joint call reads the complete Skill, selected CFG and an optional user_request (a nonempty string or null). It declares Task requirements, executable demand goals, processing and visibility relationships, boundaries and sensitivity. Deterministic compilation adds observations and sinks; propagation and DOE do not make another semantic-labeling call.

The authoritative runtime is [`runtime_contract.py`](../../src/skillflow/propagation/contracts/runtime_contract.py), `skillflow-abstract-runtime-v7`; format responsibilities come from the shared [`format_instructions.py`](../../src/skillflow/propagation/contracts/format_instructions.py), not another per-Skill material. Prompt instructions use English; generated interpretations and evidence reasons use Chinese under the current project instructions. Source excerpts preserve their original language. A valid reference does not prove that it supports the claim.

## One IR record

```text
RawAnnotationResponse
├─ outcome = completed
├─ task                       purpose, source-backed requirements and CFG bindings
├─ demands                 direct existing CFG targets; preserve describes the required property
├─ expressions           supported expressions at existing CFG controls
├─ ir_semantics[IR ID]
│  ├─ operator                duplicate-free participating executors
│  ├─ operator_evidences      source/CFG/rule evidence plus value (label or null)
│  ├─ empty_effect_evidences  present only if no nested event has a non-null effect
│  ├─ order                   fixed / partial
│  ├─ events                  processing segments or single-level for_each
│  │  └─ processing.events[]
│  │     ├─ effect            one label or null
│  │     ├─ evidences         nonempty for a non-null effect
│  │     └─ atomic_ops        ordered primitive data operations
│  ├─ output_bindings         exactly the actual public outputs
│  └─ sensitivity             declarations scoped to this IR
├─ locations                  kind, name, operand_refs, access_scope, retention
└─ location_evidences         exactly one nonempty list per location ID
```

There is no `profiles`, `roles`, parallel `effects` list, `transfer_specs`, or `effect_index`. A repeated effect remains a distinct event with its own occurrence evidence. Executor order has no temporal meaning. Allowed executors remain `llm`, `agent_runtime`, `tool`, `human`; recipients and data sources are not automatically executors.

Allowed raw effects remain `context_read`, `context_write`, `fs_read`, `fs_write`, `net_send`, `net_receive`, `user_output`, `transform`; the compiler alone generates `model_observe`. A null-effect data event does not establish that the whole IR has no effect. It still needs its operation evidence; its empty effect-evidence list is omitted on normalization. An IR recursively without any non-null effect requires nonempty `empty_effect_evidences`, including an ordinary return. An IR with a non-null effect must omit this field, not fill it with null or an empty array.

Effects and operation evidence have different responsibilities. A tool delivery is not by itself evidence of networking. The effect's evidence supports classification and stage order; the operation's evidence supports the actual parameters and data relation. Do not infer missing semantic claims from reason keywords.

## Source and reference evidence

```text
SourceEvidence                 CFGEvidence              RuleEvidence
├─ file                        ├─ target: CFGTarget     ├─ rule_id
├─ start_line                  └─ reason                └─ reason
├─ end_line
└─ reason
```

Source ranges use exact frozen `skill/` paths or the optional request's logical address `task/user-request.txt`, with inclusive one-based physical lines. The request text appears only in `user_request`; it is not duplicated in source files. Policy-file input is no longer supported. The program extracts original text, including line endings; no quote, paragraph ID, digest or basis is supplied by the model.

CFGTarget has four canonical forms: `{instruction_id, side, index}` for a complete input/output operand; `{instruction_id, path}` for an IR or one of its fields; `{block_id, path}` for a block; `{path}` for graph-level constraints and edges. Empty path selects the anchored object. Paths preserve string keys and integer indexes. Do not address an IR by its enclosing instruction-list offset, or treat an operand's identifier string as the operand. Runtime evidence uses a real EM `rule_id`. Unknown references, legacy aliases and extra keys fail validation.

`operator_evidences` adds only `value` (an executor label or null) to these forms. Values cover the declared executors, or a confirmed empty list. References establish location, not semantic support.

The model receives readable source lines, the CFG, runtime contract and optional user request once. No source/graph/instruction/task-target registry or short alias mapping is persisted or sent. The program can build transient lookups. Review-only annotation and observation IDs remain for locating claims under review.

## Processing, value relations and compilation

Select mode by evidenced mechanism: explicit model processing uses `model`; explicit local execution **and** content-return/visibility boundaries allow `local`; otherwise use `default`. Local returns are explicit, including justified no-content return. A simple calculation, executor label or absent LLM mention does not justify isolation.

Existing fields use `select_part`, unchanged member filtering uses `filter_items`, and genuine computation uses `compute`. Keep same-element recipient/body pairing inside `for_each`, optional member controls separate from their original values, and one ordered request reference for delivery and corresponding receipt. [Processing and observation compilation](SkillFlow-字段关系与观察编译.md) describes the unchanged rules.

The compiled response replaces raw segments with compiled events, adds required `precedence`, normalizes Task, demands and expressions, and derives `sink_boundaries`. It keeps one `ir_semantics` table. A raw event can split into acquisition, observation and transform events; raw path, raw operation interval and compiled path remain essential. Independent occurrence evidence and causal edges survive the split. Compiled observations do not automatically add `llm` to operator.

`to_payload` explicitly projects **task, demands, expressions, ir_semantics, locations, sink_boundaries**. `outcome` and `location_evidences` remain in the complete response/audit. Propagation rejects the full response where the business payload is required; it does not silently strip fields.

Task bindings are graph correspondences, not executable goals. Keep them even for requirements the current demand domain cannot express. Model goals omit ID; canonical demand goals receive deterministic IDs from their enclosing raw positions. Supported expression/sensitivity scopes and file-span evidence remain independently checked.

## Validation, failure and recording

The parser checks exact JSON, schema, full IR coverage, source spans, typed references, operator and effect evidence coverage, output coverage, local definitions, member scope, mode/return rules, order constraints, operation/effect/boundary compatibility and derived sinks. It does not infer processing semantics from opcode names or evidence prose.

Unsupported necessary judgments use the distinct `cannot_assess` branch with reason, actual IR IDs and evidence. Open content, opaque possible dependencies and computable partial order are normal inputs; empty arrays cannot replace failure. `complete` is not a semantic proof or a global no-DOE result.

Standalone prepare/run/replay and the formal pipeline use the shared request chain: mechanical corrections are unbounded, semantic repair remains at most once, and accepted responses are not resent. JSON Output is annotation-specific. The audited single-extra-brace normalization is permitted; all remaining structure/reference checks still apply. [The formal pipeline](../doe/joint-pipeline.md) uses the existing focused review and at most one full repair.

Current identities: joint `security-profile-v13`, annotation run v16, compiler/mapping v7, runtime v7, Task v2. Data remains v4. See [the current field and artifact contract](../architecture/field-tightening.md) and [structural correction](../architecture/structural-correction.md) for the full version matrix. Earlier formats are rejected without aliases or history migration.


## Frozen input ownership

A base annotation owns the byte snapshot (`inputs/package/` and `snapshot.json`), `cfg.json`, `runtime-contract.json`, and the nullable string in `user-request.json`. Decoded source and the combined service material are reconstructed in memory; there is no `source.json` copy beside a byte snapshot and no `material.json` aggregate. `load_prepared_material(run_dir)` validates the sealed input owner and reconstructs the same service DTO.

Repair annotations reference the explicit refinement owner through `manifest.upstream`. The original candidate and validated `initial-review` reconstruct the repair context in memory; its digest and request kind are bound in the annotation manifest. There is no `inputs/repair-context.json` copy. The actual repair prompt remains preserved unchanged, and a durable repair without a checked owner is rejected. An accepted sidecar review references its annotation, saving only its generated targets, observations and actual prompt. An explicitly authored candidate retains that candidate and provenance; it either references the same owner or stores independently supplied components once. Preserved actual prompts and responses remain exact call records.


The annotation `result.json` retains run protocol fields (status, validation, counts, request chain and compilation certificate). It does not store the six compiled business fields. The single `audit/compiled-response.json` owns those facts; validated public loaders reconstruct the enriched in-memory result. Separate `ir-semantics.json`, `locations.json`, and `sink-boundaries.json` exports are no longer generated. Raw accepted response, raw normalized candidate and compiled response remain distinct audit stages rather than interchangeable copies.
