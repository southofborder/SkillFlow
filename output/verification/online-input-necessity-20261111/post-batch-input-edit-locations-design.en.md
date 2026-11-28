# All-input modification recipes and locations: frozen audit and post-batch plan

Status: confirmed reporting gap; design only until the four frozen analyses and their sole replays close. No production code, source Skill, prompt, model request or current-run artifact was changed for this audit.

The current all-input result identifies the semantic range and its IR/operation/input slot, but does not provide a modification kind or a joined editable annotation/source location for every assessment. Distinct `remove_input` and `exclude_field` records exist only in sensitive `DataReview` comparisons. Therefore a nonsensitive unnecessary input can be correctly labeled deletable while its user-facing report lacks the explicitly requested edit type and concrete modification location.

## Current evidence

| Frozen code | Evidence |
|---|---|
| `src/skillflow/doe/input_assessments.py:21` | `AssessedRange` contains status, property, path, exclusions, evidence references and reason, but no modification recipe. |
| `src/skillflow/doe/input_assessments.py:32` | `InputAssessment` contains IR/operation/input indexes, data IDs, coverage and ranges, but no raw/wire/CFG/source location. |
| `src/skillflow/doe/sensitivity_results.py:45` | `FieldReduction` and `InputReduction` are attached to `DataReview`; they are not all-input assessment fields. |
| `src/skillflow/doe/sensitivity_material.py:45` | The sensitivity presentation index contains declarations only. With no sensitive declarations it is empty. |
| `src/skillflow/doe/formal_runner.py:150` | The persisted formal index snapshots only sensitivity declaration coordinates. |
| `src/skillflow/doe/formal_runner.py:191` | Formal report metadata provides source text, Task and demand, but no operation-to-raw-source modification map. |
| `src/skillflow/doe/sensitivity_report.py:185` and `:281` | HTML and Markdown print all-input assessment rows directly; their positions are compiled operation/IR IDs and slots. Only later per-sensitive comparison sections print a supported reduction. |
| `src/skillflow/doe/demand_material.py:116` and `src/skillflow/propagation/contracts/demand_index.py:111` | Standalone demand review includes raw targets, pointers and operation values. The all-input rows do not join their compiled operation IDs to this index; `/uses/N` entries are synthetic use coordinates, not necessarily writable JSON fields. |
| `src/skillflow/doe/demand_report.py:161` and `:218` | Standalone HTML/Markdown print the same un-enriched assessment records. A reference-index dump is not a direct modification location for each assessed use. |

This is a presentation/provenance gap, not a reason to recompute semantic necessity. Existing demand, constraint and original-observation records remain authoritative.

## Minimal data enrichment

Use one shared deterministic locator/recipe builder after assessments are computed. Both demand and sensitivity views consume its output; sensitivity must not have a separate interpretation of whether a slot or field can be removed.

```python
build_input_edit_locations(facts, annotation, assessment_rows) -> location_index
build_assessed_modification(assessment, assessed_range, location) -> recipe_or_none
validate_input_edit_locations(location_index, facts, annotation, assessments)
```

Persist the compact location index once in current demand support, keyed by assessment ID, and add a location reference plus typed modification to each deletable range. An inline location per assessment is also acceptable if simpler for the existing result validator; do not duplicate complete source text or full annotation objects into every range. The chosen public shape must be versioned with the already planned demand/DOE upgrade and checked on load without another demand solve.

Proposed location data:

```text
AssessmentLocation {
  assessment_id,
  instruction_id,
  operation_id: existing compiled ID | null,
  input_index,
  node_kind,
  cfg_pointer: existing instruction/operand JSON pointer,
  raw_annotation_sites: [{pointer, role}],
  wire_annotation_sites: [{pointer, role}],
  source_spans: [{file, start_line, end_line, evidence_origin}],
  source_resolution: "direct_span" | "inherited_span" | "annotation_only",
  generated_origin: "authored_use" | "processing_observation" | "acquisition_result",
  scope: existing occurrence/member/condition identity,
  reason
}
```

Every pointer must resolve against the selected immutable object. No source column, byte edit range, replacement text, line number or file path is invented. Source spans are the actual supplied evidence, including a broader inherited span when only that is available. If the selected material has no source span for this use, retain the exact annotation/CFG coordinate and label `annotation_only` with a concrete reason; do not pretend that an IR ID is an exact source-code location. The missing source locator is separate from the semantic necessity result.

## Concrete use locations

Use actual operation records and existing compilation mappings, not the textual spelling of a compiled operation ID.

- For explicit list inputs, locate the real `inputs/N` item; for scalar input fields, locate the actual `input` property.
- For construction/update/append/guard inputs, use the existing typed consumption roles, member indexes and recorded slot mapping to identify the actual `parts/N/value`, `parts/N/when`, `updates/N/value`, or other real field. A virtual `/uses/N` target is an audit reference, not an editable JSON pointer.
- For CFG inputs, retain the exact `blocks/.../instructions/.../inputs/N` operand and the actual consuming annotation sites. A shared IR input is removable only after the existing aggregated assessment says all applicable uses permit it.
- For flattened calls, use `wire_paths`/contract origins to locate the authored call input. Its expanded request and response remain separately identified as evidence; do not prescribe two unrelated source edits for one authored call.
- For generated model observations, the generated operation itself is not a source instruction to erase. Locate the raw processing input/return/use sites responsible for that observation, retain all relevant consuming sites and mark `processing_observation`. A recommendation must change the supplying context/use, not delete the observed fact from the analysis.
- Keep precise element/condition/receiver identities. Do not turn one member's local assessment into a whole-loop edit or merge two uses merely because their Data IDs match.

When a source operation consumes the same value in multiple raw fields, show all relevant exact sites and the assessed slot role. Do not guess a single edit site from value equality.

## Modification kinds

For input-use assessments, derive only the following semantic recipes from already verified deletion ranges:

| Assessed range | Modification | Display contract |
|---|---|---|
| Whole actual input slot, `path=[]`, no exclusions | `remove_input` | Remove this supplied input use at the listed site(s). This is not a field with an empty name/path. |
| Concrete field range with a nonempty final string field step | `exclude_field` with the exact path | Omit this field at this use while preserving the containing object/member and required fields. |
| Object remainder outside retained ranges | `keep_ranges` with explicit retained paths/properties and the original excluded-range expression | At this specific input use, keep the supported retained information and omit the proven unnecessary remainder. This is a range recipe, not an invented enumeration of unknown field names. |
| Integer/element/each terminal selector whose removal can change count/order/indexes | No structural deletion recipe | Keep the information assessment, but explicitly state that no member-removal/reindexing edit has been established. Do not output `exclude_field`, `remove_input`, or a fabricated array rewrite. |
| Required/unresolved/not-reached range | No deletion recipe | Display the retaining/limiting evidence and coverage. |

A `keep_ranges` recipe is allowed only for the already assessed object range and constraints. It preserves structural requirements too: do not translate a cardinality, presence, shape or condition demand into a fabricated value-only projection. If the current information ranges do not provide a supported content transformation preserving those properties, show the range conclusion and a specific recipe limitation rather than imply an executable rewrite.

Recipes remain recommendations for the reviewed semantic change. They do not edit a Skill, rewrite a frozen annotation, shift dependency/input indexes, or claim that an arbitrary programming-language parameter can be deleted without its source-level adjustment. The report includes the related source expression and annotation location so the user can make that adjustment concretely.

## Acquisition-result distinction

An `acquisition_output` is not an actual input slot to remove. Render its demanded/unused result ranges and downstream use sites separately:

```text
acquisition_use {
  kind: "omit_result_range_at_use",
  range,
  downstream_use_location_refs,
  acquisition_location_ref
}
retrieval_projection {
  status: "established" | "unestablished",
  capability_evidence_refs,
  request_parameter_location_refs,
  supported_output_range,
  reason
}
```

`omit_result_range_at_use` does not remove a mandatory read/call action and does not erase an earlier observation of the full acquired value. Full read/response facts remain visible.

Default projection is `unestablished`. A tool input requirement, actual request payload, or finding that the response needs only `items` is not evidence that the server supports a narrower fetch. `established` requires a selected source/interface capability claim identifying the actual acquisition, the real request selection parameter/mechanism and the supported returned range, with explicit source evidence and existing source-review acceptance. Never derive it solely from result usage or parameter names such as `fields`.

The frozen contract schema has no typed acquisition-projection capability. The schema and review agents have now coordinated the following smallest optional addition to the existing tool input contract, produced in the same processing request:

```text
ToolInputContract.acquisition_projections:
  list[AcquisitionProjectionCapability] = []   # omit empty in serialized form

AcquisitionProjectionCapability {
  selection_input_index: Index,
  selection_parameter_path: GoalPath,
  returned_range: InformationRequirement,      # property must be "value"
  reason: Text,
  evidences: TaskEvidence[1..]
}
```

The attachment identifies the real call/request; the program derives request/response operation coordinates from the existing mapping. `selection_input_index` must be a real supplied request operand. `selection_parameter_path` may identify an optional field currently absent inside that operand only when the cited interface explicitly permits the selector; do not create the field's runtime value. An absent whole selector argument with no real slot is not represented as an invented index by this minimal feature.

`returned_range` is relative to the exact paired raw receive value. If an SDK returns a tuple, `[0, "rows"]` is not interchangeable with `["rows"]` on a later local projection. Bind the existing request/response and lexical/member identities; equal arguments or Data IDs never establish a pair.

Each authored row claims support for only its exact returned range. A whole `[]` range does not imply that arbitrary child fields can be selected, and separate rows do not automatically establish an arbitrary joint mask/union. Display the exact separately supported ranges; do not construct a combined request or introduce a query-encoding DSL. A source-backed claim about one selection parameter must not be inferred from its name.

The existing seventh review exposes one program-generated optional scope per authored capability. Its scope ID binds the exact request/response pair, request input/path, returned selector and capability content. The scope receives accepted/rejected/unresolved plus the existing coordinated typed gap when needed. It is independent from necessity scopes: rejection of a claimed projection does not revoke an otherwise valid required-input relation. Absence of `acquisition_projections` creates no mandatory projection obligation and says only that no reviewed relation is supplied, not that the interface is incapable of projection.

The coordinated receipt query is:

```python
reviewed_acquisition_projections(
    receipt, request_ir, request_raw_path, response_ir, response_raw_path
) -> list[authored capability plus independent scoped review decision]
```

The helper returns checked relation/evidence only, performs no demand inference, and creates no task/action seed. Reporting intersects the accepted exact returned range with already established retained/unused result ranges and constraint-preservation evidence. A valid capability can be displayed even when a whole-value task requirement or a known source error prevents a narrower supported result selection; that limitation belongs to the selected-range recommendation. Review must also catch a capability claim contradicting an asserted independence of the same supplied selector; neither declaration silently overrides the other.

There is no concrete server-query string, selector argument value, API call, automatic rewrite, or capability discovery. The schema/receipt helper and the report operate within the existing processing/review requests. If no accepted exact relation is available, display explicit `unestablished` with its local reason and keep downstream-use minimization distinct.

## Persistence, validation and rendering

The builder uses the selected annotation, CFG, mapping, source evidence and already computed assessments. It does not re-solve demand, use unrelated caller metadata, read an external source version, or change a semantic conclusion.

The saved-result validator rederives locations and recipes from those bound materials, verifies assessment IDs/range identities and rejects tampered pointers, source spans, reduction kinds, source-column claims or fabricated projection evidence. A repaired annotation/mapping cannot reuse locations from an older receipt.

The all-input sections of both HTML and Markdown display, for every deletable use: **modification kind, exact range/retained complement, source span when available, raw/wire/CFG location, actual slot/role, scope and evidence chain**. These rows appear even when there are zero sensitive declarations. Sensitive DOE comparisons reference the same assessed modification rather than recomputing a separate reduction. Business JSON carries equivalent information; presentation metadata cannot hide or replace it.

Preserve original propagation/observations and old frozen result identities. Do not add or change task/action seeds as part of this presentation fix.

## Minimum offline regressions after closure

1. Zero sensitivity declarations with an unnecessary whole input yields a visible `remove_input`, resolvable raw/wire/CFG coordinates and genuine source span or explicit `annotation_only`; HTML, Markdown and JSON agree.
2. A partial object deletion yields `exclude_field` for the precise field and never uses empty path to mean whole input removal.
3. An opaque object complement yields a `keep_ranges` recipe retaining its supported paths/properties without inventing unknown field names.
4. Whole-output preservation, presence/cardinality/shape requirements and a constraint-blocked remainder cannot be rendered as an unsafe content-only keep-list.
5. Integer and member-terminal selectors produce no array-removal/reindexing recipe; nested per-member string-field exclusion preserves member/count identity.
6. Build conditional/value slots, updates and repeated equal-valued inputs map to their distinct real JSON fields and correct source uses.
7. A flattened tool call maps to its one authored input and exact request/response pair; unrelated calls with equal inputs are not joined.
8. A generated observation maps to responsible raw context/return/consumer sites and never suggests deleting a generated fact as a Skill edit.
9. An IR input used elsewhere remains required after aggregation; a local unused sink slot retains its distinct edit location.
10. Acquisition output unused fields show downstream-use recommendations while a required fetch action remains. Unsupported server projection is explicitly unestablished.
11. An explicit, reviewed field-projection capability yields established projection with actual request-parameter location and capability evidence; result-use patterns or a `fields`-like parameter name alone never do. An optional selector field may be absent inside a real operand without fabricating its value; a nonexistent whole operand index is rejected.
12. A source locator with only a broad genuine span is labeled inherited; no column offsets are invented. Missing spans preserve exact annotation coordinates without converting semantic deletability into global uncertainty.
13. Tampered/stale pointers, spans, recipe types and projection evidence fail saved-result validation; loading does not solve again or mutate original facts.
14. The same evidence and recipe identities survive FIFO/LIFO and report regeneration; no-sensitive and sensitive views share them.
15. Raw receive wrappers (including an SDK tuple), repeated equal-argument calls and member occurrences retain the exact paired response coordinate. A whole returned range cannot authorize unlisted descendant projections, and separate capability rows cannot imply a combined server mask.
16. A rejected/unresolved optional projection scope leaves independently accepted necessity scopes usable; absent capability material remains projection-unestablished without creating a new task gap or mandatory model request.

Owner after freeze: constraint/reporting integration agent, coordinated with root demand/result changes and the processing/review agents for capability evidence. This plan adds concrete reviewable guidance only; automatic source rewriting remains out of scope.
