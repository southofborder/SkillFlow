# Initial GA4 CFG: generated representation audit

Run: `document-guided-ga4-processing-shared-high-20261116-225414`. The saved graph step accepted `calls/a002` after one structural correction.

The accepted initial graph contains **237 blocks, 521 IR and 217 edges**. It represents all **13 remote call sites**, all **25 saveResult caller sites**, and all **11 loop/map/filter/sort source sites**. These are generated representations, not processing or propagation coverage. At this observation no final selection.json exists.

All 294 supplied source-span copies match the frozen source bytes exactly. Source citations support location, not automatic semantic correctness.

## The filter correction

The first candidate had 519 IR. Its two filter-head merges read their own output as the rejected-member incoming value, producing two RESULT_READ_BEFORE_DEFINITION errors and secondary missing-edge-endpoint diagnostics. The corrected graph adds ir_482 and ir_501, each retaining the incoming accumulator under a separate result identity. The false branch carries that retained value to the head; the true branch still appends a matching member. Initial, retained and updated values remain separate incoming versions. The 217-edge array is unchanged.

This fixes the reported source filter state-flow error without removing the filter branches. It does not establish that processing can encode both loops or that the backend will complete them. The whole replacement also changed 110 raw block objects, including metadata wording; the saved validator pass does not certify every semantic change.

## Remote boundary detail

| Source | IR | Representation |
|---|---|---|
| skill/scripts/src/api/bulk-lookup.ts:183 | ir_164 | explicit_receiver_and_request_inputs |
| skill/scripts/src/api/indexing.ts:62 | ir_262 | explicit_receiver_and_request_inputs |
| skill/scripts/src/api/indexing.ts:119 | ir_279 | explicit_receiver_and_request_inputs |
| skill/scripts/src/api/indexing.ts:152 | ir_297 | explicit_receiver_and_request_inputs |
| skill/scripts/src/api/metadata.ts:42 | ir_199 | composite_acquisition_effect_text |
| skill/scripts/src/api/metadata.ts:64 | ir_208 | composite_acquisition_effect_text |
| skill/scripts/src/api/metadata.ts:86 | ir_217 | composite_acquisition_effect_text |
| skill/scripts/src/api/realtime.ts:28 | ir_171 | composite_acquisition_effect_text |
| skill/scripts/src/api/realtime.ts:48 | ir_178 | composite_acquisition_effect_text |
| skill/scripts/src/api/realtime.ts:68 | ir_185 | composite_acquisition_effect_text |
| skill/scripts/src/api/realtime.ts:88 | ir_192 | composite_acquisition_effect_text |
| skill/scripts/src/api/reports.ts:100 | ir_099 | explicit_receiver_and_request_inputs |
| skill/scripts/src/api/searchConsole.ts:102 | ir_230 | explicit_receiver_and_request_inputs |

Six remote IR expose receiver results plus request/body operands. Four realtime and three metadata acquisitions instead describe getClient/getPropertyId inside effect text, with only external API resource/literal fields as direct operands. Those seven sites are represented, but their credential, cached-handle and property dependencies need processing evidence before they qualify as complete source-faithful boundaries.

## Storage, fields and summary

All 25 saveResult calls have their own source-matched IR. The independent saveResult implementation includes wrapped serialization (ir_452) and the filesystem write (ir_453). Caller-to-writer transfer still requires inspection of processing and propagation; shared names and citations are insufficient.

ir_089 records filters/orderBy only in unused_destructured_fields metadata and does not produce separate values for them. The outgoing request correctly omits them as the source does. The next audit must check preservation of actual read observations and the discrepancy with documented filtering/sorting behavior; this graph alone establishes no deletion verdict.

The required saved-JSON read, Markdown composition and write appear as ir_517/519/520. The graph explicitly retains unresolved invocation-to-file provenance and an unspecified summary filename/writer. These gaps must remain specific instead of being replaced with an invented save/read association.

## Iteration representation

| Source | Form | Generated instruction IDs with source-span coverage |
|---|---|---|
| skill/scripts/src/api/bulk-lookup.ts:65 | explicit_member_loop_or_combined_filter_map | ir_130, ir_133, ir_134, ir_140 |
| skill/scripts/src/api/bulk-lookup.ts:179 | opaque_pure_array_transform | ir_162 |
| skill/scripts/src/api/indexing.ts:95 | explicit_member_loop_or_combined_filter_map | ir_319, ir_320, ir_325 |
| skill/scripts/src/api/reports.ts:95 | opaque_pure_array_transform | ir_093 |
| skill/scripts/src/api/reports.ts:96 | opaque_pure_array_transform | ir_093 |
| skill/scripts/src/core/storage.ts:132 | explicit_member_loop_or_combined_filter_map | ir_477, ir_480, ir_481, ir_482, ir_483, ir_484 |
| skill/scripts/src/core/storage.ts:133 | explicit_member_loop_or_combined_filter_map | ir_477, ir_480, ir_482, ir_484 |
| skill/scripts/src/core/storage.ts:134 | opaque_pure_array_transform | ir_486 |
| skill/scripts/src/core/storage.ts:163 | explicit_member_loop_or_combined_filter_map | ir_494, ir_495, ir_496, ir_499, ir_500, ir_501, ir_502, ir_503 |
| skill/scripts/src/index.ts:305 | explicit_member_loop_or_combined_filter_map | ir_407, ir_408 |
| skill/scripts/src/index.ts:328 | explicit_member_loop_or_combined_filter_map | ir_423, ir_424 |

Seven iteration source sites use explicit member loops or the combined filter/map representation. Three name-to-object maps and one sort remain opaque pure-array transformations. No iteration completion, ordering, pairing or demand claim is inferred from that classification.

No Skill, model, validator, renderer, backend or replay was executed for this passive audit. Further changes should be proposed only after the new processing/source-review and final selected results are available.
