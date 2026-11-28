# Fresh GA4 frozen-source inventory

Run: `document-guided-ga4-review-shared-v2-high-20261112-221242`.

This inventory was independently derived from this run's current frozen source only. All 16 raw source files match their current snapshot's hash and byte length. No generated answers or previous source judgments were imported, and no Skill, model, backend analysis or replay was executed.

The source contains 13 physical awaited Google client API calls, 25 physical saveResult calls, 7 direct filesystem calls, 57 console call sites (10 with interpolation), and 53 exported function definitions. These counts are source-site denominators, not runtime invocation counts and not generated-IR coverage results. A shared helper can be called by multiple workflows.

## Explicit remote API sites

| Site | Function | Method | Frozen source lines |
|---|---|---|---|
| remote_01 | getMetricsForUrls | `client.runReport` | `skill/scripts/src/api/bulk-lookup.ts:183-183` |
| remote_02 | requestIndexing | `client.urlNotifications.publish` | `skill/scripts/src/api/indexing.ts:62-67` |
| remote_03 | removeFromIndex | `client.urlNotifications.publish` | `skill/scripts/src/api/indexing.ts:119-124` |
| remote_04 | inspectUrl | `client.urlInspection.index.inspect` | `skill/scripts/src/api/indexing.ts:152-157` |
| remote_05 | getAvailableDimensions | `client.getMetadata` | `skill/scripts/src/api/metadata.ts:42-44` |
| remote_06 | getAvailableMetrics | `client.getMetadata` | `skill/scripts/src/api/metadata.ts:64-66` |
| remote_07 | getPropertyMetadata | `client.getMetadata` | `skill/scripts/src/api/metadata.ts:86-88` |
| remote_08 | getActiveUsers | `client.runRealtimeReport` | `skill/scripts/src/api/realtime.ts:28-32` |
| remote_09 | getRealtimeEvents | `client.runRealtimeReport` | `skill/scripts/src/api/realtime.ts:48-52` |
| remote_10 | getRealtimePages | `client.runRealtimeReport` | `skill/scripts/src/api/realtime.ts:68-72` |
| remote_11 | getRealtimeSources | `client.runRealtimeReport` | `skill/scripts/src/api/realtime.ts:88-92` |
| remote_12 | runReport | `client.runReport` | `skill/scripts/src/api/reports.ts:100-100` |
| remote_13 | querySearchAnalytics | `client.searchanalytics.query` | `skill/scripts/src/api/searchConsole.ts:102-111` |

## Explicit saveResult sites

| Site | Function | Frozen source line |
|---|---|---|
| save_01 | getMetricsForUrls | `skill/scripts/src/api/bulk-lookup.ts:188` |
| save_02 | requestIndexing | `skill/scripts/src/api/indexing.ts:76` |
| save_03 | requestIndexingBatch | `skill/scripts/src/api/indexing.ts:101` |
| save_04 | removeFromIndex | `skill/scripts/src/api/indexing.ts:133` |
| save_05 | inspectUrl | `skill/scripts/src/api/indexing.ts:189` |
| save_06 | getAvailableDimensions | `skill/scripts/src/api/metadata.ts:51` |
| save_07 | getAvailableMetrics | `skill/scripts/src/api/metadata.ts:73` |
| save_08 | getPropertyMetadata | `skill/scripts/src/api/metadata.ts:91` |
| save_09 | getActiveUsers | `skill/scripts/src/api/realtime.ts:35` |
| save_10 | getRealtimeEvents | `skill/scripts/src/api/realtime.ts:55` |
| save_11 | getRealtimePages | `skill/scripts/src/api/realtime.ts:75` |
| save_12 | getRealtimeSources | `skill/scripts/src/api/realtime.ts:95` |
| save_13 | runReport | `skill/scripts/src/api/reports.ts:105` |
| save_14 | querySearchAnalytics | `skill/scripts/src/api/searchConsole.ts:118` |
| save_15 | siteOverview | `skill/scripts/src/index.ts:73` |
| save_16 | trafficAnalysis | `skill/scripts/src/index.ts:104` |
| save_17 | contentPerformance | `skill/scripts/src/index.ts:135` |
| save_18 | userBehavior | `skill/scripts/src/index.ts:162` |
| save_19 | compareDateRanges | `skill/scripts/src/index.ts:200` |
| save_20 | liveSnapshot | `skill/scripts/src/index.ts:222` |
| save_21 | searchConsoleOverview | `skill/scripts/src/index.ts:252` |
| save_22 | keywordAnalysis | `skill/scripts/src/index.ts:272` |
| save_23 | seoPagePerformance | `skill/scripts/src/index.ts:292` |
| save_24 | reindexUrls | `skill/scripts/src/index.ts:316` |
| save_25 | checkIndexStatus | `skill/scripts/src/index.ts:343` |

## Input-necessity review topics

The following are source facts and review questions, not accepted semantic contracts or deletion conclusions. Exact source text and line spans are retained in source-audit-inventory.json.

### settings_field_selection: Settings fields and real validation controls

getSettings returns propertyId, clientEmail, privateKey, defaultDateRange, resultsDir and siteUrl. Validation checks propertyId, clientEmail and privateKey before client construction; private-key text normalizes escaped newlines.

Review question: Keep actual reads and credential validation facts. Field demand for a particular consumer must not become a whole-settings demand merely because the getter returned all fields; actual control requirements still count.

Source: `skill/scripts/src/config/settings.ts:40-73`, `skill/scripts/src/core/client.ts:23-42`.

### credential_clients: Credential construction, scopes, cache state and destinations

Client constructors select clientEmail/privateKey. Shared GoogleAuth carries both webmasters.readonly and indexing scopes. Three separate singleton slots short-circuit construction; resetClient clears all three.

Review question: Bind credential/client identities and interface field obligations to the real destination and call. Current constructor arguments alone do not prove every scope or settings field necessary. Preserve cache-hit versus miss controls.

Source: `skill/scripts/src/core/client.ts:23-42`, `skill/scripts/src/core/client.ts:67-80`, `skill/scripts/src/core/client.ts:88-123`.

### ignored_report_options: Declared report filters and orderBy are unused

runReport destructures filters and orderBy, but its request includes only property, dateRanges, dimensions, metrics and a truthy limit. Neither filters nor orderBy contributes to the request or returned response.

Review question: Check whether the generated facts preserve the actual unused reads and whether semantic review reports the conflict with the documented filter/sort options. Do not invent filtering/sorting or silently substitute a corrected request.

Source: `skill/scripts/src/api/reports.ts:20-27`, `skill/scripts/src/api/reports.ts:77-109`, `skill/references/api-reference.md:30-45`.

### date_range_branches: Date values, defaults and object pass-through

Absent/falsy ranges read the settings default. Object ranges are returned unchanged; shorthand strings select matched day counts, otherwise a 30-day default. Search Console computes ISO dates from separate current-Date values.

Review question: Keep control/existence relations and actual object pass-through. Do not remove extra object fields from forward facts merely because an interface contract later needs only startDate/endDate; do not merge distinct clock observations.

Source: `skill/scripts/src/api/reports.ts:47-72`, `skill/scripts/src/api/bulk-lookup.ts:103-128`, `skill/scripts/src/api/searchConsole.ts:51-83`.

### report_request_fields: Report dimensions, metrics, limits and whole responses

GA4 maps dimension and metric name arrays into request objects. Search Console preserves dimensions, rowLimit and startRow in requestBody. Standard/realtime report functions return their whole response; search analytics selects response.data.

Review question: Verify ordered member scopes, optional/truthy controls and actual response selection. Interface necessity must be justified independently of observing these actual arguments.

Source: `skill/scripts/src/api/reports.ts:77-109`, `skill/scripts/src/api/realtime.ts:24-98`, `skill/scripts/src/api/searchConsole.ts:89-121`.

### bulk_lookup_controls: URL normalization, membership and empty-input early return

URL normalization trims each string and prefixes a missing slash without removing trailing slashes. A nonempty URL list becomes a case-insensitive pagePath inListFilter. The empty normalized list returns rows=[]/rowCount=0 before client access, remote request or save.

Review question: Preserve per-member values/order and cardinality/existence controls; an empty-output branch must not fabricate a request or persistence event. Keep requested metrics, dateRange and save controls distinct.

Source: `skill/scripts/src/api/bulk-lookup.ts:64-98`, `skill/scripts/src/api/bulk-lookup.ts:149-192`.

### metadata_output_selection: Different metadata outputs have different field needs

getAvailableDimensions selects response.dimensions (default []); getAvailableMetrics selects response.metrics; getPropertyMetadata returns/saves the whole response. getAvailableFields logs dimensions/metrics counts and returns the whole metadata object.

Review question: Check output-specific value/presence/cardinality demand and retain full acquisition facts. A selected metadata field does not establish that the remote acquisition supports field projection.

Source: `skill/scripts/src/api/metadata.ts:38-95`, `skill/scripts/src/index.ts:355-361`.

### index_notification_side_effect: Index notification actions and conditional fallback values

Publish requests send the URL with URL_UPDATED or URL_DELETED. Returned url and notifyTime use response metadata with original-URL/current-time fallbacks. Saving is separately guarded by save.

Review question: Keep publish side effects even when no response field is demanded. Preserve request/response pairing, notification type and fallback controls; response-only analysis must not delete an action-required URL.

Source: `skill/scripts/src/api/indexing.ts:57-80`, `skill/scripts/src/api/indexing.ts:114-137`.

### inspection_output_fields: URL inspection field projection and conditional nested objects

inspectUrl requests inspectionUrl/siteUrl and explicitly constructs indexStatus, optional mobileUsability, optional richResults and inspectionResultLink from response.data.inspectionResult. checkIndexStatus invokes inspectUrl with save:false and stores only URL, verdict-derived indexed, and the full indexStatus object; catch stores an error status.

Review question: Verify exact field paths, default/presence conditions, URL-result member pairing and the distinction between standalone inspectUrl obligations and this narrower caller. Do not declare fields globally deletable from one consumer alone.

Source: `skill/scripts/src/api/indexing.ts:146-193`, `skill/scripts/src/index.ts:324-346`.

### batch_members_and_errors: Sequential batches, per-item outcomes and suppressed inner saves

requestIndexingBatch processes members sequentially and passes save:false to each request. reindexUrls and checkIndexStatus have per-item try/catch, preserve URL/outcome pairing, log URLs, and save one collected batch. requestIndexingBatch itself has no per-item catch.

Review question: Keep duplicate/member occurrence identities and different error control behavior. Preserve false inner save flags and required outer writes; console URL observations remain actual uses.

Source: `skill/scripts/src/api/indexing.ts:89-105`, `skill/scripts/src/index.ts:301-346`.

### aggregate_reports: Aggregate results, nested default saves and date-pair identity

High-level workflows collect named subresults and persist the aggregate; many nested report helpers retain their default save:true. compareDateRanges pairs range1 with period1 and range2 with period2, then saves both; it performs no arithmetic comparison.

Review question: Retain each real nested/aggregate save and period pairing. Task/source evidence must determine necessity rather than treating all similar writes as duplicates. Do not invent trend calculations in compareDateRanges.

Source: `skill/scripts/src/index.ts:55-224`, `skill/scripts/src/index.ts:235-295`.

### persistent_wrapper_and_filename: Persistence content and path depend on different inputs

saveResult writes the whole data argument wrapped with savedAt/category/operation/propertyId and optional extraInfo. The path uses resultsDir/category plus a timestamp and sanitized operation/extraInfo. Directory creation is conditional. The written timestamp and filename timestamp are generated separately.

Review question: Distinguish content fields, directory/path controls, optional metadata and separate clocks. Preserve the real propertyId metadata even for non-GA4 categories; do not treat an unused returned filepath as an absent storage side effect.

Source: `skill/scripts/src/core/storage.ts:31-94`.

### result_selection: Read/list/latest behavior and filename matching

loadResult checks existence then reads/parses, returning null on catch. listResults filters .json, joins paths, sorts descending by filename and optionally slices. getLatestResult optionally uses a sanitized operation substring, chooses the first file, then loads it.

Review question: Keep selection order, limits, existence and candidate filename conditions. A latest filename does not prove correlation with the current request; do not invent exact-operation matching or a current-run cache.

Source: `skill/scripts/src/core/storage.ts:103-171`.

### narrative_summary: Source-declared read-and-summary workflow

The workflow declares analysis, auto-save and reading saved JSON to create Markdown summaries containing tables, trends and recommendations under results/summaries. Tips separately suggest asking for a summary after pulling data.

Review question: Audit source modality and summary read/write obligations separately from TypeScript call-site counts. No summary implementation appears among the explicit API/saveResult call sites.

Source: `skill/SKILL.md:53-64`, `skill/SKILL.md:151-158`.

### examples_setup_and_entry: Executable bodies versus examples and setup

Source contains setup npm-install instructions, import examples and a direct-entry help branch. The direct index.ts branch prints help; examples do not cause every exported API function to execute together.

Review question: Keep declared alternatives/example modality. The 13 remote sites below count explicit client method calls, not installation package downloads or all runtime invocations of shared helpers.

Source: `skill/SKILL.md:8-50`, `skill/scripts/setup.sh:1-2`, `skill/scripts/src/index.ts:364-405`.

## Boundaries for the final source-versus-generated audit

A source citation that merely overlaps a broad function range does not establish that the corresponding call, request/response relation or write was modeled. Final mapping must inspect the selected CFG and processing operation, then distinguish represented, processed, blocked, unmodeled and absent positions. Each actual input assessment and reviewed contract must be tied back to that selected occurrence; a completed propagation percentage alone is not source coverage.

Setup npm installs and SDK authentication internals are outside the 13 explicit Google client-call denominator. The narrative read-and-Markdown-summary step is separately declared in SKILL.md:53-64; it is not an explicit TypeScript saveResult site. Indexing actions remain relevant even if their response has no positive output demand. Actual prior reads/observations must remain recorded when a field is judged unnecessary downstream.

The source clearly declares filters/orderBy options yet runReport does not use them in its outgoing request. This is a source-level documentation/implementation mismatch to test against the generated analysis. It is not permission to fabricate corrected request fields, and it does not alone establish a final task-preserving deletion recommendation.
