# Initial accepted GA4 CFG source-site audit

Initial accepted pre-source-review CFG snapshot only; not a final selected graph and not backend reached coverage.

Run: `document-guided-ga4-review-shared-v2-high-20261112-221242`. Accepted graph step: `calls/a002` after one structural correction. The invalid first response was not used as evidence.

Exact graph artifact: `graph/initial.json`; SHA-256 `dc39313b1f6cd70c81916fa097bd60944f3f8b1170edeae64e6b09b8aaf362c1`. Accepted step value identity: `c3f804c0c5782023d0821bb0dadbff6d12d7154a74d0df00ddcf60cc267fac73`.

The accepted snapshot has 237 blocks, 511 IR and 222 edges. All 13 physical remote client calls and all 25 physical saveResult calls map to 38 distinct IR. Each mapped instruction retains the exact physical call text and an appropriate call/response or save boundary. No source-site omission was found within these two denominators. This is representation coverage only; backend reached coverage is not available.

## Physical source-to-IR mapping

| Site | Frozen source | Function | IR | Boundary |
|---|---|---|---|---|
| remote_01 | `skill/scripts/src/api/bulk-lookup.ts:183` | getMetricsForUrls | `ir_184` | explicit remote call |
| remote_02 | `skill/scripts/src/api/indexing.ts:62` | requestIndexing | `ir_282` | explicit remote call |
| remote_03 | `skill/scripts/src/api/indexing.ts:119` | removeFromIndex | `ir_299` | explicit remote call |
| remote_04 | `skill/scripts/src/api/indexing.ts:152` | inspectUrl | `ir_317` | explicit remote call |
| remote_05 | `skill/scripts/src/api/metadata.ts:42` | getAvailableDimensions | `ir_219` | bundled acquisition |
| remote_06 | `skill/scripts/src/api/metadata.ts:64` | getAvailableMetrics | `ir_228` | bundled acquisition |
| remote_07 | `skill/scripts/src/api/metadata.ts:86` | getPropertyMetadata | `ir_237` | bundled acquisition |
| remote_08 | `skill/scripts/src/api/realtime.ts:28` | getActiveUsers | `ir_191` | bundled acquisition |
| remote_09 | `skill/scripts/src/api/realtime.ts:48` | getRealtimeEvents | `ir_198` | bundled acquisition |
| remote_10 | `skill/scripts/src/api/realtime.ts:68` | getRealtimePages | `ir_205` | bundled acquisition |
| remote_11 | `skill/scripts/src/api/realtime.ts:88` | getRealtimeSources | `ir_212` | bundled acquisition |
| remote_12 | `skill/scripts/src/api/reports.ts:100` | runReport | `ir_119` | explicit remote call |
| remote_13 | `skill/scripts/src/api/searchConsole.ts:102` | querySearchAnalytics | `ir_250` | explicit remote call |
| save_01 | `skill/scripts/src/api/bulk-lookup.ts:188` | getMetricsForUrls | `ir_186` | saveResult summary |
| save_02 | `skill/scripts/src/api/indexing.ts:76` | requestIndexing | `ir_291` | saveResult summary |
| save_03 | `skill/scripts/src/api/indexing.ts:101` | requestIndexingBatch | `ir_335` | saveResult summary |
| save_04 | `skill/scripts/src/api/indexing.ts:133` | removeFromIndex | `ir_308` | saveResult summary |
| save_05 | `skill/scripts/src/api/indexing.ts:189` | inspectUrl | `ir_321` | saveResult summary |
| save_06 | `skill/scripts/src/api/metadata.ts:51` | getAvailableDimensions | `ir_223` | saveResult summary |
| save_07 | `skill/scripts/src/api/metadata.ts:73` | getAvailableMetrics | `ir_232` | saveResult summary |
| save_08 | `skill/scripts/src/api/metadata.ts:91` | getPropertyMetadata | `ir_239` | saveResult summary |
| save_09 | `skill/scripts/src/api/realtime.ts:35` | getActiveUsers | `ir_193` | saveResult summary |
| save_10 | `skill/scripts/src/api/realtime.ts:55` | getRealtimeEvents | `ir_200` | saveResult summary |
| save_11 | `skill/scripts/src/api/realtime.ts:75` | getRealtimePages | `ir_207` | saveResult summary |
| save_12 | `skill/scripts/src/api/realtime.ts:95` | getRealtimeSources | `ir_214` | saveResult summary |
| save_13 | `skill/scripts/src/api/reports.ts:105` | runReport | `ir_121` | saveResult summary |
| save_14 | `skill/scripts/src/api/searchConsole.ts:118` | querySearchAnalytics | `ir_254` | saveResult summary |
| save_15 | `skill/scripts/src/index.ts:73` | siteOverview | `ir_345` | saveResult summary |
| save_16 | `skill/scripts/src/index.ts:104` | trafficAnalysis | `ir_353` | saveResult summary |
| save_17 | `skill/scripts/src/index.ts:135` | contentPerformance | `ir_361` | saveResult summary |
| save_18 | `skill/scripts/src/index.ts:162` | userBehavior | `ir_369` | saveResult summary |
| save_19 | `skill/scripts/src/index.ts:200` | compareDateRanges | `ir_377` | saveResult summary |
| save_20 | `skill/scripts/src/index.ts:222` | liveSnapshot | `ir_383` | saveResult summary |
| save_21 | `skill/scripts/src/index.ts:252` | searchConsoleOverview | `ir_392` | saveResult summary |
| save_22 | `skill/scripts/src/index.ts:272` | keywordAnalysis | `ir_399` | saveResult summary |
| save_23 | `skill/scripts/src/index.ts:292` | seoPagePerformance | `ir_406` | saveResult summary |
| save_24 | `skill/scripts/src/index.ts:316` | reindexUrls | `ir_421` | saveResult summary |
| save_25 | `skill/scripts/src/index.ts:343` | checkIndexStatus | `ir_433` | saveResult summary |

## Modeling caveats and omissions outside the site denominator

### summary_obligation_only

The graph repeats the saved-JSON read and Markdown summary obligation in constraint 7, but none of its 511 instructions names or represents summary generation, Markdown, tables/trends/recommendations or a summaries-path write. This omission is outside the 13 remote/25 saveResult denominators.

This is the initial CFG snapshot, not a final Task/review/DOE judgment. Later selected material must be checked independently.

### bundled_remote_acquisition

Four realtime and three metadata call sites combine client-getter/property-getter behavior and the SDK call into a single acquisition. Inputs include an external-resource description of cache/current settings; request field and first-response-element details are in metadata.

Source sites are represented, but credential provenance, current versus cached settings and interface input necessity require processing contracts; a CFG call label alone cannot establish these facts.

### save_summaries

All 25 source saveResult call sites are distinct call summaries with discarded returned paths. A separate public saveResult body contains write_json_replace at ir_454 and wrapper construction at ir_453. Their effects must be instantiated at each caller; their mere presence does not establish 25 reached storage observations.

Do not count an outputless save as unnecessary or claim its wrapper/path provenance is processed before backend records exist.

### unused_original_option_reads

ir_098 correctly retains filters/orderBy as unused metadata and copies the original destructuring. Its outputs include only dimensions, metrics, dateRange, limit and save, and the request construction has no filter/sort behavior. The source documents options that its actual request ignores.

The later assessment must preserve the original read/observation fact and distinguish a source mismatch from a contract error or deletion recommendation; no corrected request is invented here.

### loop_try_regions

The ordinary indexing batch uses a per-member call and append with uncaught failure. reindexUrls and checkIndexStatus combine per-item logging, API helper invocation and successful append into bounded try-region IR, then separate catch appends. The CFG retains save:false, actual URL/outcome pairing declarations, normal-completion dispatch and separate success/failure backedges.

A caught failure can precede or follow the remote boundary. The CFG declares this distinction; it does not by itself prove that processing records all may-effects, member correlations or observation order.

## Loop boundaries

| Loop | Source | Header | IR range |
|---|---|---|---|
| report_dimension_map | `skill/scripts/src/api/reports.ts:95-95` | `block_054` | `ir_103`–`ir_107` |
| report_metric_map | `skill/scripts/src/api/reports.ts:96-96` | `block_056` | `ir_108`–`ir_112` |
| normalize_urls | `skill/scripts/src/api/bulk-lookup.ts:64-75` | `block_077` | `ir_150`–`ir_159` |
| bulk_metric_map | `skill/scripts/src/api/bulk-lookup.ts:179-179` | `block_089` | `ir_177`–`ir_181` |
| request_indexing_batch | `skill/scripts/src/api/indexing.ts:94-98` | `block_165` | `ir_328`–`ir_333` |
| reindex_with_catch | `skill/scripts/src/index.ts:305-314` | `block_189` | `ir_413`–`ir_420` |
| inspect_with_catch | `skill/scripts/src/index.ts:328-341` | `block_195` | `ir_425`–`ir_432` |
| list_json_filter | `skill/scripts/src/core/storage.ts:131-132` | `block_220` | `ir_475`–`ir_481` |
| list_path_map | `skill/scripts/src/core/storage.ts:133-133` | `block_223` | `ir_482`–`ir_486` |
| latest_operation_filter | `skill/scripts/src/core/storage.ts:161-164` | `block_231` | `ir_498`–`ir_504` |

All ten headers have explicit has_member control and member/accumulator structure. Exact participating instructions and boundary edges are retained in the JSON audit. Processing support, duplicate-member correlation and per-occurrence effects have not yet been checked.

If source review later replaces this CFG, this document remains an initial-snapshot audit. The final selected graph requires a separate audit; its results must not be inferred from these mappings.
