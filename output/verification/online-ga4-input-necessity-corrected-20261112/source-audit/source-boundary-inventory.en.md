# GA4 fresh-source boundary inventory

This inventory was derived from the new frozen source package before inspecting generated answers. It is an assistant-authored finite checklist, not a human gold standard.

Source SHA: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. All 16 file hashes match the new source snapshot.

## Denominators

- source_files: 16
- awaited_application_sdk_sites: 13
- saveResult_call_sites: 25
- explicit_url_loops: 3
- exported_function_declarations: 53
- array_operation_sites: 9
- console_call_sites: 57
- interpolated_console_call_sites: 10
- supplemental_boundaries: 15

## API sites

| ID | Function | Source |
| --- | --- | --- |
| API-01 | getMetricsForUrls | scripts/src/api/bulk-lookup.ts:183 |
| API-02 | requestIndexing | scripts/src/api/indexing.ts:62 |
| API-03 | removeFromIndex | scripts/src/api/indexing.ts:119 |
| API-04 | inspectUrl | scripts/src/api/indexing.ts:152 |
| API-05 | getAvailableDimensions | scripts/src/api/metadata.ts:42 |
| API-06 | getAvailableMetrics | scripts/src/api/metadata.ts:64 |
| API-07 | getPropertyMetadata | scripts/src/api/metadata.ts:86 |
| API-08 | getActiveUsers | scripts/src/api/realtime.ts:28 |
| API-09 | getRealtimeEvents | scripts/src/api/realtime.ts:48 |
| API-10 | getRealtimePages | scripts/src/api/realtime.ts:68 |
| API-11 | getRealtimeSources | scripts/src/api/realtime.ts:88 |
| API-12 | runReport | scripts/src/api/reports.ts:100 |
| API-13 | querySearchAnalytics | scripts/src/api/searchConsole.ts:102 |

## Field necessity review checks

- **CHECK-01 — Settings demand must distinguish consumers:** Formatting a property ID needs propertyId; choosing Search Console site needs siteUrl; storage needs resultsDir and the actually serialized propertyId. Neither full settings reads nor credential presence automatically establish demand for unrelated fields.
- **CHECK-02 — Validation conditions must survive semantic minimization:** propertyId/clientEmail/privateKey presence affects validation.valid and errors. If a validation requirement is semantically wrong for one client, report the mismatch explicitly instead of pretending the source never checks it.
- **CHECK-03 — Documented filters and orderBy are ignored by actual runReport:** filters/orderBy are destructured but absent from request and all later computations. If the declared task requires filtering/sorting, report unsupported or missing behavior; deletion of these source inputs does not repair that behavior.
- **CHECK-04 — Output-specific metadata dependency:** getAvailableDimensions returns/saves only dimensions; getAvailableMetrics only metrics; getPropertyMetadata preserves the whole response. A whole-response transfer rule cannot stand in for either selective case. Source lacks a remote response projection parameter.
- **CHECK-05 — Inspection result demand is consumer-specific:** Standalone inspectUrl exposes indexStatus/mobileUsability/richResults/link. checkIndexStatus calls it with save=false and keeps verdict plus the whole indexStatus; other inspection fields have no use on this consumer path, but other consumers may require them.
- **CHECK-06 — Notification fallback and output pairing:** Output URL can derive from response or original URL. Time can derive from response or clock. reindexUrls object spread can overwrite the earlier url field; do not assume a fixed input-output URL equality unsupported by the source.
- **CHECK-07 — Repeated URL calls and error branches:** Three loops require occurrence/cardinality/order identity. requestIndexingBatch has no local catch; the two high-level loops append per-member error outcomes. Removing a URL can alter count, effects, status and console observations.
- **CHECK-08 — Bulk lookup empty input and membership:** Empty normalized URLs return rows=[]/rowCount=0 before client/API/save. Nonempty normalized members feed the filter. Preserve membership, caseSensitive=false, optional metrics and date range.
- **CHECK-09 — Storage action and return-value demand are separate:** The 25 saveResult call sites do not use its filepath return. Required persistence must still retain filename, payload and write action; unused return does not mean unused side effect.
- **CHECK-10 — Other consumers and acquisition control:** compareDateRanges retains both ranges and reports while disabling two inner saves. Report/analytics selectors may constrain acquisition but do not establish arbitrary response-field trimming. Union all applicable uses before deleting an input.
- **CHECK-11 — Documented output mismatch remains visible:** Markdown summary generation is declared but not implemented as a TypeScript writer. keywordAnalysis describes a query/device breakdown but invokes separate query and device reports; do not invent joint query-device rows.
- **CHECK-12 — Sensitivity and necessity remain separate:** Credential material, property/site identifiers, URLs/query strings, transactionId/revenue and analytics rows are candidate sensitivity boundaries. Source names alone do not establish actual sensitive values, unauthorized access or DOE.

## Later selected-material audit

1. Freeze selected source/CFG/processing/annotation/source-review/review-receipt identities after controller closure; provisional checks must be labeled.
2. For each finite API/save/loop boundary, distinguish represented, modeled, reached, processed, unresolved, and absent. Broad overlapping citations alone do not establish correct semantics.
3. Check request-response/auth/state/payload identities and scope, interface evidence separate from argument presence, and acquisition capabilities.
4. Check complete contract inventory and per-input/output scoped review; inspect wrong/missing input findings independently of unresolved labels.
5. Trace each required/deletable/unresolved input assessment to actual CFG inputs, task-output seeds, transfer rules, exact edit locations and preservation checks.
6. Use the twelve field checks to verify local demand versus retained forward observations, and union conditions/count/membership/pairing/other-consumer uses.
7. Report source-supported semantic limitations separately from generated-IR coverage; zero deletions or completed propagation does not prove no DOE.

## Limits

- This finite source checklist is not a human gold standard or a proof of exhaustive semantic coverage.
- Remote-site count excludes SDK internals, client/auth construction, setup package downloads and documentation examples.
- Save-site count excludes shared write internals and the declared markdown summary workflow.
- No actual secrets, runtime values, installed SDK implementation or external API documentation were accessed.
- Observed arguments are not used as proof that an interface requires every argument; necessity must have separate explicit source/interface semantics.
- No deletion or DOE finding is established before selected contracts, their review, demand and preservation evidence are checked.

The JSON inventory includes all exact quotes, source hashes, 25 save sites, three URL loops, supplemental boundaries, exported functions, array operations and console sites. All coverage statuses await selected-material inspection.
