# Fresh GA4 source baseline

Run: `document-guided-ga4-processing-shared-high-20261116-225414`.

All 16 frozen files match both the source manifest and this run's protocol hashes (155,170 bytes).
The source contains 13 direct remote API call sites and 25 saveResult call sites. These are physical source counts, not generated or processed coverage.

## Remote API sites

| Site | Source | Function | Remote method |
|---|---|---|---|
| remote_01 | skill/scripts/src/api/bulk-lookup.ts:183 | getMetricsForUrls | runReport |
| remote_02 | skill/scripts/src/api/indexing.ts:62 | requestIndexing | urlNotifications.publish |
| remote_03 | skill/scripts/src/api/indexing.ts:119 | removeFromIndex | urlNotifications.publish |
| remote_04 | skill/scripts/src/api/indexing.ts:152 | inspectUrl | urlInspection.index.inspect |
| remote_05 | skill/scripts/src/api/metadata.ts:42 | getAvailableDimensions | getMetadata |
| remote_06 | skill/scripts/src/api/metadata.ts:64 | getAvailableMetrics | getMetadata |
| remote_07 | skill/scripts/src/api/metadata.ts:86 | getPropertyMetadata | getMetadata |
| remote_08 | skill/scripts/src/api/realtime.ts:28 | getActiveUsers | runRealtimeReport |
| remote_09 | skill/scripts/src/api/realtime.ts:48 | getRealtimeEvents | runRealtimeReport |
| remote_10 | skill/scripts/src/api/realtime.ts:68 | getRealtimePages | runRealtimeReport |
| remote_11 | skill/scripts/src/api/realtime.ts:88 | getRealtimeSources | runRealtimeReport |
| remote_12 | skill/scripts/src/api/reports.ts:100 | runReport | runReport |
| remote_13 | skill/scripts/src/api/searchConsole.ts:102 | querySearchAnalytics | searchanalytics.query |

## saveResult caller sites

| Site | Source | Function |
|---|---|---|
| save_01 | skill/scripts/src/api/bulk-lookup.ts:188 | getMetricsForUrls |
| save_02 | skill/scripts/src/api/indexing.ts:76 | requestIndexing |
| save_03 | skill/scripts/src/api/indexing.ts:101 | requestIndexingBatch |
| save_04 | skill/scripts/src/api/indexing.ts:133 | removeFromIndex |
| save_05 | skill/scripts/src/api/indexing.ts:189 | inspectUrl |
| save_06 | skill/scripts/src/api/metadata.ts:51 | getAvailableDimensions |
| save_07 | skill/scripts/src/api/metadata.ts:73 | getAvailableMetrics |
| save_08 | skill/scripts/src/api/metadata.ts:91 | getPropertyMetadata |
| save_09 | skill/scripts/src/api/realtime.ts:35 | getActiveUsers |
| save_10 | skill/scripts/src/api/realtime.ts:55 | getRealtimeEvents |
| save_11 | skill/scripts/src/api/realtime.ts:75 | getRealtimePages |
| save_12 | skill/scripts/src/api/realtime.ts:95 | getRealtimeSources |
| save_13 | skill/scripts/src/api/reports.ts:105 | runReport |
| save_14 | skill/scripts/src/api/searchConsole.ts:118 | querySearchAnalytics |
| save_15 | skill/scripts/src/index.ts:73 | siteOverview |
| save_16 | skill/scripts/src/index.ts:104 | trafficAnalysis |
| save_17 | skill/scripts/src/index.ts:135 | contentPerformance |
| save_18 | skill/scripts/src/index.ts:162 | userBehavior |
| save_19 | skill/scripts/src/index.ts:200 | compareDateRanges |
| save_20 | skill/scripts/src/index.ts:222 | liveSnapshot |
| save_21 | skill/scripts/src/index.ts:252 | searchConsoleOverview |
| save_22 | skill/scripts/src/index.ts:272 | keywordAnalysis |
| save_23 | skill/scripts/src/index.ts:292 | seoPagePerformance |
| save_24 | skill/scripts/src/index.ts:316 | reindexUrls |
| save_25 | skill/scripts/src/index.ts:343 | checkIndexStatus |

## Source-supported questions for the new result

- **read_but_unforwarded_fields** (skill/scripts/src/api/reports.ts:77-108; skill/references/api-reference.md:31-42): runReport destructures filters and orderBy, but its request object and later body never consume them. The API reference promises these options. Does the current representation retain the actual field-read observations, distinguish their absent contribution to the implemented request/output, and report the documented capability mismatch without inventing SDK field encodings? This source observation alone is not a final task-relative deletability result.
- **truthy_limit** (skill/scripts/src/api/reports.ts:84-100): The request spreads limit only when truthy. Are the inclusion condition and parameter value represented separately? Source establishes zero omission but not external SDK behavior for a hypothetical supplied zero.
- **caller_to_storage_boundary** (skill/scripts/src/core/storage.ts:58-94): saveResult wraps data in metadata with savedAt, category, operation, propertyId and conditional extraInfo, serializes it, writes to a computed filepath and returns that path. Does each of the 25 caller sites connect its actual data/category/operation/extraInfo to the writer, payload and returned path? A generated or processed opaque saveResult call alone does not establish the filesystem boundary.
- **storage_control_and_identity** (skill/scripts/src/core/storage.ts:64-92): The filesystem identity depends on resultsDir/category, timestamp, sanitized operation and conditional extraInfo; directory creation depends on existence. Do necessary location and control requirements remain when payload fields are excluded?
- **natural_language_summary** (skill/SKILL.md:55-65): The workflow requires reading saved JSON files and writing a Markdown summary in results/summaries with data tables, trends and recommendations. Do Task, CFG and mapping retain this stated action and its source/read/write relationships? TypeScript physical-site counts cannot establish this separate obligation.
- **batch_member_pairing** (skill/scripts/src/api/indexing.ts:89-104; skill/scripts/src/index.ts:300-344): Batch requests are sequential, retain each URL/result relationship, use per-item save=false in requestIndexingBatch, and may save the final batch; high-level wrappers retain caught-error records. Are per-member pairing, conditions and normal/error alternatives represented and then reached by propagation?
- **bulk_empty_and_membership** (skill/scripts/src/api/bulk-lookup.ts:63-98; skill/scripts/src/api/bulk-lookup.ts:154-183): URLs are normalized to paths, an empty normalized array returns before the remote request, and a nonempty request includes a URL-membership filter, selected metrics, date range, pagePath and pageTitle dimensions. Does demand transfer preserve collection existence/membership/control and selected fields rather than substituting an arbitrary scalar dependency?
- **deterministic_inspection_projection** (skill/scripts/src/api/indexing.ts:152-185): The inspection result explicitly selects nested response fields with defaults and conditional mobileUsability/richResults objects. Do deterministic selectors and condition dependencies remain precise? An opaque whole-response contract must not override these real dependencies.
- **authentication_vs_routing** (skill/scripts/src/core/client.ts:23-52; skill/scripts/src/core/client.ts:70-132): Client authentication uses clientEmail/privateKey; API routing uses propertyId or siteUrl; caches and validation add separate state/control relationships. Does the generated graph distinguish authentication, cached receiver identity, routing and request payload fields?
- **storage_order_and_existence** (skill/scripts/src/core/storage.ts:123-171): Result listing filters JSON filenames, forms paths, sorts descending and optionally slices by limit. Latest-result retrieval optionally filters operation, handles no files and selects index zero. Are order, count, membership and existence preserved independently of retained data fields?

## Pending evidence

This preliminary baseline makes no claim that a generated graph reaches the sites, processing models them faithfully, propagation processes them, or DOE demonstrates a removable field. Those conclusions require new selected artifacts and their bound review and demand evidence.

No historical graph/answer was imported. No Skill, model, backend or replay was executed by this helper.
