# GA4 processing revision and ingress evidence

Run `150337` selected the original 489-instruction CFG and the revised annotation. Six field-level contract checks improved. All four previously excluded instructions remained unmodeled in the selected processing fragment. The controller reported a partial DOE result and a matching replay with zero new native starts. [Selection][selection] · [Controller closeout][closeout]

## Four historical processing failures

In the parent run, `ir_167` had five undefined output bindings and the three loop instructions had unsupported nested cases. In this run, the first processing answer explicitly declared whole-instruction gaps for all four. Its correction fixed seven evidence references elsewhere. The resulting fragment had 319 modeled instructions, 170 explicitly unmodeled instructions, three additional precision gaps and zero validation exclusions. This left no validation error at these four positions to trigger validation-based repair. [Parent exclusions][parent] · [Initial validation][validation] · [Accepted processing][processing]

| Instruction | Initial gap pointer | Actual revision authority and answer | Selected runtime coverage |
|---|---|---|---|
| ir_167 | /processing_gaps/38 | No direct finding or editable slot | Reached, unmodeled |
| ir_311 | /processing_gaps/90 | F061, editable, submitted `keep: unmodeled` | Blocked after unmodeled ir_305 |
| ir_329 | /processing_gaps/96 | F062, editable, submitted `keep: unmodeled` | Blocked after unmodeled ir_324 |
| ir_346 | /processing_gaps/104 | F063, editable, submitted `keep: unmodeled` | Blocked after unmodeled ir_341 |

The three editable positions came from sensitivity ingress findings assigned to processing. The revision answered all 86 slots on its first attempt, with 73 unmodeled keeps and 13 attachment edits. All 173 processing gaps were preserved. The selected runtime recorded 133 processed, 54 reached-unmodeled and 302 blocked instructions. [Initial review][initial-review] · [Signed slot inventory][scope] · [Actual dispositions][response] · [Selected coverage][coverage]

## Why 73 ingress gaps disappeared

The initial sensitivity fragment contained 35 declarations and 73 entry gaps. Its 73 distinct gap owners exactly match both the 73 processing keeps and the sensitivity plan's `removed_instruction_ids`. All 73 still exist in the unchanged CFG. None had a modeled processing record or a slot among the 34 editable sensitivity positions. The planner determined removal using the set of *modeled* instructions. The merge then excluded previous gaps belonging to that removal set. [Initial sensitivity][sensitivity] · [Sensitivity scope][sensitivity-scope] · [Planner, line 398][planner] · [Merge, line 464][merge]

Revised sensitivity preserved all 35 declarations and returned zero entry gaps. The initial review material included the 73 gaps. The revised review material omitted them while preserving the same 173 processing gaps. The smaller final finding count therefore gives no evidence that those 73 source relationships were repaired. A regression check should require every gap at a surviving CFG instruction to retain its owner until evidence resolves it. [Revised sensitivity][revised-sensitivity] · [Initial review inputs][initial-inputs] · [Revised review inputs][revised-inputs]

## Paired contract judgments

All 54 obligation IDs match between reviews. The 13 edited wire attachments were seven `demand_transfer` and six `input_contract` fields. One wire attachment can correspond to multiple compiled atomic paths. [Initial review][initial-review] · [Submitted edits][response] · [Selected review][final-review]

| Initial → selected | Count | Instructions and evidence |
|---|---:|---|
| Accepted → accepted | 35 | Same obligation IDs |
| Rejected → accepted | 6 | ir_009, ir_069, ir_071, ir_081, ir_135, ir_136 |
| Rejected → rejected | 12 | ir_099, ir_160, ir_173, ir_258, ir_270, ir_283. Final F004 identifies missing client-receiver provenance at all six SDK calls |
| Rejected → unresolved | 1 | ir_474. The transfer cannot isolate the selected ordered slice members from excluded members |

## Source checks on whole-instruction gaps

At `ir_337`, the source sends a literal completion message to the console after the aggregate save returns. The gap names both destination and condition. A declared console location and literal delivery can express that effect, but the initial fragment has no console location and the local revision freezes shared locations. At `ir_232`, the source constructs `{dimensions: response.dimensions || []}`. The gap states the field and fallback. A field projection, fallback computation and object construction can retain the relation. [Console delivery, line 317][console] · [Metadata projection, lines 46–48][metadata] · [Submitted gaps][processing] · [Read-only declarations][scope]

At `ir_005`, the packaged source shows a zero-argument `dotenv.config()` call. It does not specify the library's environment merge precedence. The call and post-call observation can be retained while that particular relationship stays unresolved. At `ir_260`, the source obtains a fresh clock value only when the response time is falsy. Restoring an earlier compute that omitted this acquisition would lose an actual effect. [Environment initialization, lines 5–9][dotenv] · [Conditional clock, lines 69–73][clock] · [Initial review F002][initial-review]

[selection]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/selection.json
[closeout]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/controller-finished.json
[parent]: ../online-ga4-lossless-delivery-20261119/coverage-parent-comparison.en.md
[validation]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/processing/calls/a001/validation.json
[processing]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/processing/value.json
[initial-review]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/review/result.json
[scope]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/revision/processing-scope.json
[response]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/revision-processing/calls/a001/response.json
[coverage]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/propagation/manifest.json
[sensitivity]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/sensitivity/value.json
[sensitivity-scope]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/revision/sensitivity-scope.json
[planner]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/implementation-snapshot/src/skillflow/document_guided/fragment_revision.py#L398
[merge]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/implementation-snapshot/src/skillflow/document_guided/fragment_revision.py#L464
[revised-sensitivity]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/revision-sensitivity/value.json
[initial-inputs]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/review/inputs.json
[revised-inputs]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/revision/review/inputs.json
[final-review]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/revision/review/result.json
[console]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/source/inputs/package/scripts/src/index.ts#L317
[metadata]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/source/inputs/package/scripts/src/api/metadata.ts#L46
[dotenv]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/source/inputs/package/scripts/src/config/settings.ts#L5
[clock]: ../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/source/inputs/package/scripts/src/api/indexing.ts#L69
