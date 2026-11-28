# Final selected GA4 source and propagation coverage

The final annotation references the exact initial accepted CFG: `graph/initial.json`, SHA-256 `dc39313b1f6cd70c81916fa097bd60944f3f8b1170edeae64e6b09b8aaf362c1`. There was no semantic repair. Source review ended with structural_failure and has no accepted review, so the graph and annotation remain semantically unreviewed. Initial source/CFG audit files are preserved separately.

Finalized propagation has **487/511 processed IR, 4 unmodeled IR and 20 blocked IR**. These are static record statuses, not executed source coverage.

| Source denominator | CFG represented | IR processed | Expected boundary recorded | Important remainder |
|---|---:|---:|---:|---|
| 13 explicit remote API sites | 13 | 9 | 6 network_send sites | 3 processed sites replaced by local tools; 4 unmodeled |
| 25 explicit saveResult sites | 25 | 21 | 0 caller storage_write sites | 21 processed local-tool deliveries; 4 blocked |

The standalone storage utility separately records two storage_write positions: directory creation at ir_442 and file writing at ir_454. Neither proves that the 25 caller-specific payloads were persisted in the recorded model. Total recorded sinks are 58 model_observe, 8 network_send and 2 storage_write; the two additional network sends occur only in loop post-request-error cases.

## Remote physical sites

| Source | Function | IR | Solver | Recorded boundary |
|---|---|---|---|---|
| `skill/scripts/src/api/bulk-lookup.ts:183` | getMetricsForUrls | `ir_184` | processed | expected_boundary_recorded |
| `skill/scripts/src/api/indexing.ts:62` | requestIndexing | `ir_282` | processed | expected_boundary_recorded |
| `skill/scripts/src/api/indexing.ts:119` | removeFromIndex | `ir_299` | processed | expected_boundary_recorded |
| `skill/scripts/src/api/indexing.ts:152` | inspectUrl | `ir_317` | processed | expected_boundary_recorded |
| `skill/scripts/src/api/metadata.ts:42` | getAvailableDimensions | `ir_219` | unmodeled | unmodeled |
| `skill/scripts/src/api/metadata.ts:64` | getAvailableMetrics | `ir_228` | unmodeled | unmodeled |
| `skill/scripts/src/api/metadata.ts:86` | getPropertyMetadata | `ir_237` | unmodeled | unmodeled |
| `skill/scripts/src/api/realtime.ts:28` | getActiveUsers | `ir_191` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:48` | getRealtimeEvents | `ir_198` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:68` | getRealtimePages | `ir_205` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:88` | getRealtimeSources | `ir_212` | unmodeled | unmodeled |
| `skill/scripts/src/api/reports.ts:100` | runReport | `ir_119` | processed | expected_boundary_recorded |
| `skill/scripts/src/api/searchConsole.ts:102` | querySearchAnalytics | `ir_250` | processed | expected_boundary_recorded |

## saveResult physical sites

| Source | Function | IR | Solver | Recorded boundary |
|---|---|---|---|---|
| `skill/scripts/src/api/bulk-lookup.ts:188` | getMetricsForUrls | `ir_186` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/indexing.ts:76` | requestIndexing | `ir_291` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/indexing.ts:101` | requestIndexingBatch | `ir_335` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/indexing.ts:133` | removeFromIndex | `ir_308` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/indexing.ts:189` | inspectUrl | `ir_321` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/metadata.ts:51` | getAvailableDimensions | `ir_223` | blocked | blocked |
| `skill/scripts/src/api/metadata.ts:73` | getAvailableMetrics | `ir_232` | blocked | blocked |
| `skill/scripts/src/api/metadata.ts:91` | getPropertyMetadata | `ir_239` | blocked | blocked |
| `skill/scripts/src/api/realtime.ts:35` | getActiveUsers | `ir_193` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:55` | getRealtimeEvents | `ir_200` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:75` | getRealtimePages | `ir_207` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/realtime.ts:95` | getRealtimeSources | `ir_214` | blocked | blocked |
| `skill/scripts/src/api/reports.ts:105` | runReport | `ir_121` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/api/searchConsole.ts:118` | querySearchAnalytics | `ir_254` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:73` | siteOverview | `ir_345` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:104` | trafficAnalysis | `ir_353` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:135` | contentPerformance | `ir_361` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:162` | userBehavior | `ir_369` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:200` | compareDateRanges | `ir_377` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:222` | liveSnapshot | `ir_383` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:252` | searchConsoleOverview | `ir_392` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:272` | keywordAnalysis | `ir_399` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:292` | seoPagePerformance | `ir_406` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:316` | reindexUrls | `ir_421` | processed | local_tool_substitution_without_expected_boundary |
| `skill/scripts/src/index.ts:343` | checkIndexStatus | `ir_433` | processed | local_tool_substitution_without_expected_boundary |

## Exact unmodeled and blocked regions

- Realtime sources: unmodeled ir_212; blocked ir_213–ir_216, including save ir_214 at realtime.ts:95.
- Available dimensions: unmodeled ir_219; blocked ir_220–ir_225, including save ir_223 at metadata.ts:51.
- Available metrics: unmodeled ir_228; blocked ir_229–ir_234, including save ir_232 at metadata.ts:73.
- Full metadata: unmodeled ir_237; blocked ir_238–ir_241, including save ir_239 at metadata.ts:91.

Each unmodeled gap explicitly cites absent receiver/property request bindings in the grouped CFG acquisition. They are labeled source-origin processing gaps in the saved material; the underlying explanation concerns this CFG's representation. No IR is labeled failed in the finalized coverage table. All exact gap reasons, source citations and 24 nonprocessed positions are retained in the JSON audit.

## Loop and semantic fidelity caveats

### realtime_remote_substitution

Three processed physical runRealtimeReport sites contain only deliver/receive operations to task-local getActiveUsers/getRealtimeEvents/getRealtimePages tools. Their locations have task access and task retention. They have no network_send sink or concrete remote request at these coordinates.

These processed IR cannot be counted as faithfully modeled remote exposure sites; the standalone source contains real Google client calls.

### save_call_persistence_omitted

All 21 processed saveResult call sites contain a delivery to the save location, declared kind=tool, access_scope=task and retention=task. No storage_write sink appears at any of these callers. Four additional save sites are blocked. The separate public saveResult utility has directory creation at ir_442 and file write at ir_454.

A standalone public storage write does not instantiate persistence for each caller's report/aggregate/member version. Therefore 21 processed saves are not 21 source-supported persisted-result boundaries.

### successful_loop_remote_effects_omitted

The ordinary indexing-batch member call ir_331 is only a task-local toolkit requestIndexing tool. The normal submitted/inspected cases at ir_416/ir_428 also use local toolkit tools. Their explicit network_send records occur only in after_publish_entry/after_inspect_entry post_request_error cases (event 8/event 13).

All ten loop structures process, but successful per-member network effects are not faithfully expanded. Separate standalone API functions do not establish these callers' member/request provenance.

### summary_writer_still_absent

The unchanged CFG has no summary generation or Markdown writer IR. The selected processing gap at ir_511 explicitly states that source analysis entry points discard save paths and there is no binding from a particular analysis invocation to selected saved content, summary writer or user delivery.

The narrative summarize stage is not established by the physical 13/25 site counts or by standalone file reads.

### unused_original_option_reads_not_preserved_as_field_operations

The original destructuring reads filters and orderBy, and CFG metadata retains them as unused. Selected compiled processing only selects dimensions, metrics, dateRange and limit plus computes save; it contains no select_part for filters/orderBy and no explicit model-observation operation at this IR.

A claim that unused input reads were preserved at field level is not supported for these two source fields. Their documentation/implementation mismatch remains distinct from a task-preserving deletion conclusion.

### local_diagnostics_despite_processed_status

The finalized manifest records unresolved_path for one predecessor path at wrapper construction ir_453 and missing_part diagnostics for content/value on literal candidates at ir_460/ir_462. All three IR nevertheless have overall processed status and operation records.

Processed means the abstract solver produced a record, not that every predecessor/candidate path or source relationship is fully established.

## Loop processing status

| Source loop | Header | All mapped IR processed |
|---|---|---|
| report_dimension_map | `block_054` | True |
| report_metric_map | `block_056` | True |
| normalize_urls | `block_077` | True |
| bulk_metric_map | `block_089` | True |
| request_indexing_batch | `block_165` | True |
| reindex_with_catch | `block_189` | True |
| inspect_with_catch | `block_195` | True |
| list_json_filter | `block_220` | True |
| list_path_map | `block_223` | True |
| latest_operation_filter | `block_231` | True |

All ten structural loop groups have records, but this does not repair the omitted normal per-item remote effects described above. Each loop's exact instruction statuses, gaps, sink coordinates and relevant recorded case phases are retained in final-source-coverage.json.

This passive audit used only selected current artifacts and preserved earlier audits. It ran no validator, backend analysis, model, Skill, test or replay, and it makes no independent DOE deletion or necessity conclusion.
