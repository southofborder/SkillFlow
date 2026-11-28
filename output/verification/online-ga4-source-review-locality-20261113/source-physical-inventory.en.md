# Fresh GA4 source inventory

The complete frozen source contains 16 files. All file bytes match this run's source manifest.

Physical sites: 13 remote API calls, 25 saveResult calls, 11 loop/map/filter/sort expressions, and 4 filesystem implementation calls.

These are source obligations, not evidence that generated IR reached or modeled those boundaries.

## Remote calls

- skill/scripts/src/api/bulk-lookup.ts:183 — getMetricsForUrls → client.runReport
- skill/scripts/src/api/indexing.ts:62 — requestIndexing → client.urlNotifications.publish
- skill/scripts/src/api/indexing.ts:119 — removeFromIndex → client.urlNotifications.publish
- skill/scripts/src/api/indexing.ts:152 — inspectUrl → client.urlInspection.index.inspect
- skill/scripts/src/api/metadata.ts:42 — getAvailableDimensions → client.getMetadata
- skill/scripts/src/api/metadata.ts:64 — getAvailableMetrics → client.getMetadata
- skill/scripts/src/api/metadata.ts:86 — getPropertyMetadata → client.getMetadata
- skill/scripts/src/api/realtime.ts:28 — getActiveUsers → client.runRealtimeReport
- skill/scripts/src/api/realtime.ts:48 — getRealtimeEvents → client.runRealtimeReport
- skill/scripts/src/api/realtime.ts:68 — getRealtimePages → client.runRealtimeReport
- skill/scripts/src/api/realtime.ts:88 — getRealtimeSources → client.runRealtimeReport
- skill/scripts/src/api/reports.ts:100 — runReport → client.runReport
- skill/scripts/src/api/searchConsole.ts:102 — querySearchAnalytics → client.searchanalytics.query

## Saves

- skill/scripts/src/api/bulk-lookup.ts:188 — getMetricsForUrls: `saveResult(response, 'reports', 'bulk_url_lookup', dateStr);`
- skill/scripts/src/api/indexing.ts:76 — requestIndexing: `saveResult(result, 'indexing', 'request_indexing');`
- skill/scripts/src/api/indexing.ts:101 — requestIndexingBatch: `saveResult(results, 'indexing', 'batch_indexing');`
- skill/scripts/src/api/indexing.ts:133 — removeFromIndex: `saveResult(result, 'indexing', 'remove_from_index');`
- skill/scripts/src/api/indexing.ts:189 — inspectUrl: `saveResult(result, 'indexing', 'url_inspection');`
- skill/scripts/src/api/metadata.ts:51 — getAvailableDimensions: `saveResult(result, 'metadata', 'dimensions');`
- skill/scripts/src/api/metadata.ts:73 — getAvailableMetrics: `saveResult(result, 'metadata', 'metrics');`
- skill/scripts/src/api/metadata.ts:91 — getPropertyMetadata: `saveResult(response, 'metadata', 'full');`
- skill/scripts/src/api/realtime.ts:35 — getActiveUsers: `saveResult(response, 'realtime', 'active_users');`
- skill/scripts/src/api/realtime.ts:55 — getRealtimeEvents: `saveResult(response, 'realtime', 'events');`
- skill/scripts/src/api/realtime.ts:75 — getRealtimePages: `saveResult(response, 'realtime', 'pages');`
- skill/scripts/src/api/realtime.ts:95 — getRealtimeSources: `saveResult(response, 'realtime', 'sources');`
- skill/scripts/src/api/reports.ts:105 — runReport: `saveResult(response, 'reports', operation, extra);`
- skill/scripts/src/api/searchConsole.ts:118 — querySearchAnalytics: `saveResult(result, 'searchconsole', operation, extra);`
- skill/scripts/src/index.ts:73 — siteOverview: `saveResult(results, 'reports', 'site_overview', dateStr);`
- skill/scripts/src/index.ts:104 — trafficAnalysis: `saveResult(results, 'reports', 'traffic_analysis', dateStr);`
- skill/scripts/src/index.ts:135 — contentPerformance: `saveResult(results, 'reports', 'content_performance', dateStr);`
- skill/scripts/src/index.ts:162 — userBehavior: `saveResult(results, 'reports', 'user_behavior', dateStr);`
- skill/scripts/src/index.ts:200 — compareDateRanges: `saveResult(comparison, 'reports', 'date_comparison');`
- skill/scripts/src/index.ts:222 — liveSnapshot: `saveResult(results, 'realtime', 'snapshot');`
- skill/scripts/src/index.ts:252 — searchConsoleOverview: `saveResult(results, 'searchconsole', 'overview', dateStr);`
- skill/scripts/src/index.ts:272 — keywordAnalysis: `saveResult(results, 'searchconsole', 'keyword_analysis', dateStr);`
- skill/scripts/src/index.ts:292 — seoPagePerformance: `saveResult(results, 'searchconsole', 'seo_page_performance', dateStr);`
- skill/scripts/src/index.ts:316 — reindexUrls: `saveResult(results, 'indexing', 'reindex_batch');`
- skill/scripts/src/index.ts:343 — checkIndexStatus: `saveResult(results, 'indexing', 'index_status_check');`

## Source-supported audit questions

- reports-unused-filter-and-order-inputs (skill/scripts/src/api/reports.ts:77): The source destructures filters and orderBy but the constructed request has neither. Their actual read fact must remain distinguishable from necessity for the implemented response. The documented interface separately promises these options; report source/implementation mismatch rather than inventing SDK field names.
- reports-truthy-limit (skill/scripts/src/api/reports.ts:84): The source adds limit only when truthy. A supplied zero is omitted. Whether that omission changes SDK behavior requires explicit interface evidence; source truthiness alone does not establish SDK zero semantics.
- save-controls-and-payload (skill/scripts/src/core/storage.ts:58): Each saveResult call needs connection to the filesystem writer and wrapper fields data, metadata.savedAt/category/operation/propertyId and optional extraInfo. A processed local-tool call alone does not establish this filesystem exposure.
- storage-path-and-control (skill/scripts/src/core/storage.ts:65): Path identity depends on resultsDir/category, timestamp, sanitized operation and conditional extraInfo; directory creation is conditional. Data minimization must preserve required path/control uses, not just JSON data fields.
- summary-obligation (skill/SKILL.md:57): The declared workflow requires reading saved results and creating a Markdown summary with tables, trends and recommendations. This natural-language obligation must be audited separately from TypeScript call-site counts.
- batch-pairing-and-save (skill/scripts/src/api/indexing.ts:89): The sequential batch maps each URL to its own indexing response with per-item save=false and one optional final save. Preserve member/result pairing and loop control.
- high-level-error-pairing (skill/scripts/src/index.ts:300): High-level reindex/inspection loops preserve each URL in either success or caught-error results and save the complete batch. Normal and error paths must both be traced to actual request semantics.
- bulk-input-and-empty-control (skill/scripts/src/api/bulk-lookup.ts:63): URL normalization maps each input path; filter construction preserves URL membership and empty-input control. These requirements cannot be replaced by value-only demand on an arbitrary scalar.
- bulk-no-call-empty (skill/scripts/src/api/bulk-lookup.ts:154): An empty normalized URL array returns rows=[]/rowCount=0 before acquisition. Nonempty requests contain both pagePath and pageTitle dimensions, selected metrics, date range and the URL filter.
- inspection-output-field-precision (skill/scripts/src/api/indexing.ts:152): Inspection output is explicitly projected and defaulted by field; separate indexStatus/mobileUsability/richResults values and existence conditions. Whole-response contracts must not erase these deterministic field relations.
- credential-and-routing-fields (skill/scripts/src/core/client.ts:23): Authentication uses clientEmail/privateKey, API routing separately uses propertyId or siteUrl, and singleton/validation control can use additional fields. Preserve those distinctions instead of treating every settings field as every request payload.
- storage-results-order (skill/scripts/src/core/storage.ts:123): Listing filters JSON files, maps paths, sorts descending, optionally slices by limit; latest-result selection optionally filters operation and handles empty lists. Count/order/existence inputs can be necessary despite discarded payload fields.

No Skill, model, propagation, DOE or replay was executed by this inventory helper.
