# GA4 source boundary and input-necessity expectations

Created 2026-11-11 from the verified original 16-file source selection. This is a finite, assistant-authored static audit for comparison after the new run closes. No generated run materials or historical model answers have been consulted. It is not a human gold standard, runtime execution, or whole-source semantic coverage proof.

**Source SHA256:** `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. The original 18-file donor was read without changes; only `_meta.json` and `skill-card.md` were excluded. The selected files total 155,170 bytes. Exact file hashes and line counts are in [ga4-source-manifest.json](ga4-source-manifest.json); machine-readable expectations and evidence spans are in [ga4-boundary-expectations.json](ga4-boundary-expectations.json).

The inventory covers **13 explicit awaited SDK call sites**, **25 saveResult invocation sites**, and **3 explicit URL loops**. These are finite source-site denominators, not execution counts. SDK-internal authentication/transport, setup commands, and documentation examples are outside the remote-site count. Alternative exported functions must not be treated as one necessarily executed sequence.

## Required fields, actual data and uncertainty

The local API reference explicitly requires report dimensions/metrics, URL arguments and arrays, and saveResult data/category/operation. The code provides exact query-field construction and operation constants. It does not include complete Google service schemas, so this audit does not equate every supplied SDK default with a universally mandatory remote field. No explicitly constructed remote request field is independently established as unnecessary here solely because it is optional.

The clearest extra-input expectations concern the eager settings object, unused documented report options, and response projections. These are local and output-specific. A credential needed by an authentication constructor is not thereby needed by a storage-path computation. A raw response being acquired does not establish every field as needed by every consumer.

## Remote call sites

| ID | Source call | Function / exact request information | Response use |
| --- | --- | --- | --- |
| R01 | `scripts/src/api/reports.ts:100` | `runReport`: `property`; `dateRanges[].startDate`; `dateRanges[].endDate`; `dimensions[].name`; `metrics[].name`; `limit` (only when options.limit is truthy) | The first SDK response is returned and optionally saved whole; the local cast does not strip fields. |
| R02 | `scripts/src/api/bulk-lookup.ts:183` | `getMetricsForUrls`: `property`; `dateRanges[].startDate`; `dateRanges[].endDate`; `dimensions[].name`; `metrics[].name`; `dimensionFilter.filter.fieldName`; `dimensionFilter.filter.inListFilter.values[]`; `dimensionFilter.filter.inListFilter.caseSensitive` | Whole first SDK response is returned/saved. Empty normalized input returns {rows:[],rowCount:0} before client construction, call or save. |
| R03 | `scripts/src/api/realtime.ts:28-32` | `getActiveUsers`: `property`; `dimensions[].name`; `metrics[].name` | Whole first SDK response is returned and saved only when save is true. |
| R04 | `scripts/src/api/realtime.ts:48-52` | `getRealtimeEvents`: `property`; `dimensions[].name`; `metrics[].name` | Whole first SDK response is returned and saved only when save is true. |
| R05 | `scripts/src/api/realtime.ts:68-72` | `getRealtimePages`: `property`; `dimensions[].name`; `metrics[].name` | Whole first SDK response is returned and saved only when save is true. |
| R06 | `scripts/src/api/realtime.ts:88-92` | `getRealtimeSources`: `property`; `dimensions[].name`; `metrics[].name` | Whole first SDK response is returned and saved only when save is true. |
| R07 | `scripts/src/api/metadata.ts:42-44` | `getAvailableDimensions`: `name` | Constructs only {dimensions: response.dimensions \|\| []}; other top-level response fields do not contribute to this result. Members are retained whole, not projected to only the interface type fields. |
| R08 | `scripts/src/api/metadata.ts:64-66` | `getAvailableMetrics`: `name` | Constructs only {metrics: response.metrics \|\| []}; other top-level response fields do not contribute to this result. Members are retained whole, not projected to only the interface type fields. |
| R09 | `scripts/src/api/metadata.ts:86-88` | `getPropertyMetadata`: `name` | Returns and optionally saves the complete SDK metadata response; the local reference expressly documents full metadata. |
| R10 | `scripts/src/api/searchConsole.ts:102-111` | `querySearchAnalytics`: `siteUrl`; `requestBody.startDate`; `requestBody.endDate`; `requestBody.dimensions[]`; `requestBody.rowLimit`; `requestBody.startRow` | Only response.data is returned/saved, not the outer SDK response envelope. data itself is forwarded whole. |
| R11 | `scripts/src/api/indexing.ts:62-67` | `requestIndexing`: `requestBody.url`; `requestBody.type` | Constructs {url,type,notifyTime}: response metadata URL or original URL; constant type; matching update/remove timestamp or fresh clock. Other response fields are unused. |
| R12 | `scripts/src/api/indexing.ts:119-124` | `removeFromIndex`: `requestBody.url`; `requestBody.type` | Constructs {url,type,notifyTime}: response metadata URL or original URL; constant type; matching update/remove timestamp or fresh clock. Other response fields are unused. |
| R13 | `scripts/src/api/indexing.ts:152-157` | `inspectUrl`: `requestBody.inspectionUrl`; `requestBody.siteUrl` | Projects data.inspectionResult into inspectionResultLink,indexStatus,mobileUsability,richResults. Nested defaults and optional branches are explicit; omitted source siblings must not reappear. |

Every R01-R13 row in the JSON includes exact request construction evidence, local documentation evidence where available, excluded local-control inputs, and specific unresolved-reference IDs. The request/response pair must retain its actual receiver and argument coordinates. Credentials are configured through SDK constructors (core/client.ts:35-40,67-78); the source does not show the private key copied into any of these explicit request bodies, nor does it establish SDK wire-level plaintext-secret disclosure.

## Local save sites

Every listed invocation discards saveResult's returned filepath. The file write is still an actual effect. A generated public output for an ignored return is not justified by these call sites. All saves use the common writer at `scripts/src/core/storage.ts:58-94`: it stores `{metadata,data}` with savedAt/category/operation/propertyId and truthy extraInfo, under a timestamped path. It does not write the entire settings object or credential values.

| ID | Source | Function | Data and storage operation | Guard |
| --- | --- | --- | --- | --- |
| S01 | `scripts/src/api/reports.ts:105` | `runReport` | `reports/dimensions.join('_') \|\| 'custom'`: Whole first SDK report response. | save (default true) |
| S02 | `scripts/src/api/bulk-lookup.ts:188` | `getMetricsForUrls` | `reports/bulk_url_lookup`: Whole first SDK report response. | nonempty normalized URLs and save (default true) |
| S03 | `scripts/src/api/realtime.ts:35` | `getActiveUsers` | `realtime/active_users`: Whole first SDK realtime response. | save (default true) |
| S04 | `scripts/src/api/realtime.ts:55` | `getRealtimeEvents` | `realtime/events`: Whole first SDK realtime response. | save (default true) |
| S05 | `scripts/src/api/realtime.ts:75` | `getRealtimePages` | `realtime/pages`: Whole first SDK realtime response. | save (default true) |
| S06 | `scripts/src/api/realtime.ts:95` | `getRealtimeSources` | `realtime/sources`: Whole first SDK realtime response. | save (default true) |
| S07 | `scripts/src/api/metadata.ts:51` | `getAvailableDimensions` | `metadata/dimensions`: Object with dimensions only; each source dimension member is retained. | save (default true) |
| S08 | `scripts/src/api/metadata.ts:73` | `getAvailableMetrics` | `metadata/metrics`: Object with metrics only; each source metric member is retained. | save (default true) |
| S09 | `scripts/src/api/metadata.ts:91` | `getPropertyMetadata` | `metadata/full`: Whole SDK metadata response, explicitly documented as full. | save (default true) |
| S10 | `scripts/src/api/searchConsole.ts:118` | `querySearchAnalytics` | `searchconsole/dimensions.join('_') \|\| 'query'`: Whole response.data, excluding the outer SDK response envelope. | save (default true) |
| S11 | `scripts/src/api/indexing.ts:76` | `requestIndexing` | `indexing/request_indexing`: Constructed {url,type,notifyTime}. | save (default true) |
| S12 | `scripts/src/api/indexing.ts:101` | `requestIndexingBatch` | `indexing/batch_indexing`: Array of paired per-URL notification results; sequential loop. | save (default true) |
| S13 | `scripts/src/api/indexing.ts:133` | `removeFromIndex` | `indexing/remove_from_index`: Constructed {url,type,notifyTime}. | save (default true) |
| S14 | `scripts/src/api/indexing.ts:189` | `inspectUrl` | `indexing/url_inspection`: Constructed inspectionResultLink,indexStatus,mobileUsability,richResults with conditional members. | save (default true) |
| S15 | `scripts/src/index.ts:73` | `siteOverview` | `reports/site_overview`: Constructed pageViews; trafficSources; demographics; events. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S16 | `scripts/src/index.ts:104` | `trafficAnalysis` | `reports/traffic_analysis`: Constructed sources; sessions; newVsReturning. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S17 | `scripts/src/index.ts:135` | `contentPerformance` | `reports/content_performance`: Constructed pages; landingPages; exitPages. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S18 | `scripts/src/index.ts:162` | `userBehavior` | `reports/user_behavior`: Constructed demographics; events; engagement. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S19 | `scripts/src/index.ts:200` | `compareDateRanges` | `reports/date_comparison`: Constructed period1.dateRange; period1.data; period2.dateRange; period2.data. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S20 | `scripts/src/index.ts:222` | `liveSnapshot` | `realtime/snapshot`: Constructed activeUsers; currentPages; currentEvents. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S21 | `scripts/src/index.ts:252` | `searchConsoleOverview` | `searchconsole/overview`: Constructed topQueries; topPages; devicePerformance; countryPerformance. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S22 | `scripts/src/index.ts:272` | `keywordAnalysis` | `searchconsole/keyword_analysis`: Constructed queries; deviceBreakdown. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S23 | `scripts/src/index.ts:292` | `seoPagePerformance` | `searchconsole/seo_page_performance`: Constructed topPages; countryBreakdown. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S24 | `scripts/src/index.ts:316` | `reindexUrls` | `indexing/reindex_batch`: Constructed each success: url,status plus notification fields; each failure: url,status,error. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |
| S25 | `scripts/src/index.ts:343` | `checkIndexStatus` | `indexing/index_status_check`: Constructed each success: url,indexed,status=indexStatus; each failure: url,indexed=false,status.error. | reached after preceding operations complete; the two URL loop wrappers also continue after locally caught per-member failures |

Default subreport saves and later aggregate saves remain separate actual sites. Conversely, compareDateRanges disables both child report saves (index.ts:180-192), requestIndexingBatch disables per-member saves (api/indexing.ts:95-101), and the two high-level URL loops disable child saves (index.ts:305-343). Do not revive a suppressed child save or collapse distinct unsuppressed saves. SKILL.md:60-64 declares automatic saving and a later markdown-summary phase; no summary-file writer is implemented in the audited TypeScript, so that source requirement must not be represented by invented existing code.

## Field-level comparison expectations

### N01 — Settings projections

**Basis:** `exact_source_dependency`. {"getPropertyId": ["settings.propertyId"], "getSiteUrl": ["settings.siteUrl"], "parseDateRange default": ["settings.defaultDateRange"], "saveResult write": ["settings.resultsDir", "settings.propertyId"], "saveResult returned path": ["settings.resultsDir"]}

Other getSettings members, including clientEmail/privateKey, do not affect these selected outputs; getSettings still eagerly reads them in actual forward facts.

Evidence: `scripts/src/config/settings.ts:40-48`, `scripts/src/core/client.ts:50-52`, `scripts/src/core/client.ts:130-132`, `scripts/src/api/reports.ts:47-55`, `scripts/src/core/storage.ts:64-94`.

### N02 — Settings validation versus authentication

**Basis:** `exact_source_dependency`. validateSettings.valid/errors depend on truthiness of propertyId,clientEmail,privateKey, not their full string content. SDK credential constructors consume clientEmail/privateKey values.

siteUrl,resultsDir,defaultDateRange are not validation inputs. No source proof that the private key is sent in plaintext in any of the 13 explicit request objects.

Evidence: `scripts/src/config/settings.ts:54-73`, `scripts/src/core/client.ts:23-42`, `scripts/src/core/client.ts:67-78`, `scripts/src/core/client.ts:87-122`.

### N03 — saveResult output-specific dependencies

**Basis:** `exact_source_dependency`. On the successful-write path, the returned filepath text is constructed from resultsDir/category/operation, truthiness and value of extraInfo when used, and filename clock components. Preserving the write action additionally needs data, propertyId and savedAt clock; content serialization/write failure can prevent return.

data and propertyId are absent from the filepath construction. This is not independence from write success or permission to delete the data needed by the save action. Credentials/defaultDateRange/siteUrl are absent from the saved wrapper. Every enumerated caller ignores filepath; preserving the write does not require a synthetic public return.

Evidence: `scripts/src/core/storage.ts:31-46`, `scripts/src/core/storage.ts:58-94`, `references/api-reference.md:360-371`.

### N04 — Metadata projections

**Basis:** `exact_source_dependency`. getAvailableDimensions selects response.dimensions or []; getAvailableMetrics selects response.metrics or []. Preserve their fallback conditions and entire selected member values.

The other top-level metadata branch and response.name do not determine the selected result. Do not assume SDK member objects contain only three declared TypeScript fields.

Evidence: `scripts/src/api/metadata.ts:38-76`.

### N05 — Inspection projections and wrapper use

**Basis:** `exact_source_dependency`. inspectUrl constructs selected fields with truthy/optional fallbacks; checkIndexStatus(save:false) requires only returned indexStatus, with verdict additionally determining indexed.

inspectionResultLink,mobileUsability,richResults are not used by checkIndexStatus; other raw inspectionResult siblings are not copied by inspectUrl.

Evidence: `scripts/src/api/indexing.ts:159-185`, `scripts/src/index.ts:328-339`.

### N06 — Unused documented report options

**Basis:** `exact_source_discrepancy`. References advertise filters/orderBy, and ReportOptions declares them; runReport destructures both without using them.

Neither field influences the implemented request/response/save. A task using documented filtering/sorting needs a missing-functionality finding; discarding those fields alone does not fulfill that declared task.

Evidence: `references/api-reference.md:37-43`, `scripts/src/api/reports.ts:20-28`, `scripts/src/api/reports.ts:77-108`.

### N07 — Optional presence, truthiness and defaults

**Basis:** `exact_source_dependency`. runReport.limit is emitted only when truthy; optional extraInfo is used only when truthy. Destructured defaults for save/dimensions/rowLimit/startRow apply when undefined. date parsing falls back for any falsy range.

Do not conflate known absence with false/0/empty-string values or mark every optional option as always mandatory. if_present on an actual request field is not a substitute for its source construction guard.

Evidence: `scripts/src/api/reports.ts:47-71`, `scripts/src/api/reports.ts:78-105`, `scripts/src/api/searchConsole.ts:90-110`, `scripts/src/core/storage.ts:73-86`.

### N08 — Closed aggregate output parts

**Basis:** `exact_source_dependency`. Each aggregate object in index.ts has the explicit component keys enumerated in S15-S23. A complete aggregate demand can preserve these parts and structural obligations.

Explicit wrapper keys do not prove exhaustive field coverage of nested opaque SDK responses. Type assertions are not transformations.

Evidence: `scripts/src/index.ts:55-203`, `scripts/src/index.ts:209-295`, `scripts/src/api/reports.ts:33-42`, `scripts/src/api/reports.ts:108`.

### N09 — Loop occurrence and exception pairing

**Basis:** `exact_source_dependency`. requestIndexingBatch, reindexUrls and checkIndexStatus each loop over supplied URLs. Preserve each URL/result or URL/error relationship, including duplicate occurrences; child saves are disabled.

Do not deduplicate URLs, pair one member URL with another response, infer unbounded actual calls from one static site, or fabricate full generic exception semantics.

Evidence: `scripts/src/api/indexing.ts:89-104`, `scripts/src/index.ts:301-345`.

### N10 — Source purposes and automatic saving

**Basis:** `source_supported_requirement`. SKILL declares analysis, timestamped auto-save and subsequent markdown summarization. Wrapper exports expose alternative capabilities; the caller selects among them.

No fixed external user task is imported. One aggregate and its default child saves are actual separate sites; their redundancy is not proof of unnecessary behavior under the declared all-results auto-save wording.

Evidence: `SKILL.md:28-64`, `SKILL.md:66-102`, `scripts/src/index.ts:1-23`.

## Specific unresolved semantics

| ID | Barrier | Missing evidence or interpretation |
| --- | --- | --- |
| U-SDK | The frozen package includes wrapper request objects and package dependencies, but not complete Google SDK/service schemas or remote implementation. Source supports named query/control roles; it does not prove that every supplied default/constant is required by the remote interface. | Exact service-required versus optional/default-equivalent fields where local reference does not settle that distinction. Evidence: `scripts/src/core/client.ts:6-9`, `scripts/src/api/reports.ts:92-100`, `scripts/src/api/searchConsole.ts:102-111`, `scripts/src/api/bulk-lookup.ts:175-183`. |
| U-FILTERS | The local public reference advertises filtering and sorting that the wrapper does not implement. | Whether a selected declared-purpose realization requires filters/orderBy and how that source mismatch is represented; do not invent their effects. Evidence: `references/api-reference.md:40-41`, `scripts/src/api/reports.ts:78-100`. |
| U-WHOLE | Several functions forward a complete SDK response, while public descriptions emphasize analytic rows/metrics. TypeScript response declarations are partial and casts do not strip fields. | Source-backed justification for a whole-response task demand, or an explicit complete output decomposition; unknown SDK siblings cannot be silently omitted or declared necessary. Evidence: `scripts/src/api/reports.ts:33-42`, `scripts/src/api/reports.ts:100-108`, `references/api-reference.md:45`, `scripts/src/api/searchConsole.ts:113-121`, `references/api-reference.md:213`. |
| U-TRUTHY | Source behavior uses truthiness in places where an interface description only calls a parameter optional, and time/fallback results are dynamic. | A precise guarded rule for each selected output including absence/false/zero/empty-string distinctions and fallback branches. External meaning of zero row limits is not defined locally. Evidence: `scripts/src/api/reports.ts:97`, `scripts/src/core/storage.ts:75-86`, `scripts/src/api/indexing.ts:69-72`, `scripts/src/api/indexing.ts:161-185`. |
| U-ACQUISITION | Local projections establish unused response branches for a particular consumer, but the same metadata/inspection endpoint returns a larger response. | Evidence that a narrower remote retrieval request or alternative method exists; unused acquired information alone does not prove the external API can return less. Evidence: `scripts/src/api/metadata.ts:42-48`, `scripts/src/api/metadata.ts:64-70`, `scripts/src/api/indexing.ts:152-185`, `scripts/src/index.ts:331-336`. |
| U-AUTH | GoogleAuth config requests both webmasters.readonly and indexing scopes and shared validation requires GA4_PROPERTY_ID for all client factories. External authorization behavior is not bundled. | Proof of per-client scope minimality, validity of GA4 property gating for Search Console/Indexing, and SDK credential-to-wire semantics. These are not inferred plaintext-secret disclosures. Evidence: `scripts/src/core/client.ts:67-78`, `scripts/src/core/client.ts:87-122`, `scripts/src/config/settings.ts:54-73`. |
| U-SAVE-SCOPE | The Skill says all results auto-save; high-level wrappers often keep default child saves as well as their combined save, but selected APIs explicitly disable child saves. | A source-supported interpretation of whether every intermediate save is part of a particular declared purpose; actual duplication alone does not establish a removable action. Evidence: `SKILL.md:55-64`, `scripts/src/index.ts:55-76`, `scripts/src/index.ts:180-200`, `scripts/src/api/indexing.ts:94-101`. |
| U-ERRORS | Two wrappers convert unknown caught SDK errors to strings and persist them with their paired URL. | Actual error schema and any source-supported sensitive fields in those strings; do not fabricate credential content or treat all failures as one fixed object. Evidence: `scripts/src/index.ts:305-312`, `scripts/src/index.ts:328-339`. |

## Comparison procedure after closure

For each of the 13 calls and 25 saves, locate generated CFG/processing operations and propagation records using physical source spans, then record represented, processed, unmodeled, blocked, not reached or absent separately. Preserve invocation/member/receiver pairing; one static call may have several generated instances.

For N01-N10, inspect the actual input contract, source-review check, immutable receipt, backward derivation and input assessment. Require the exact field, property, optional guard and output selector. Missing SDK knowledge must name U-SDK or a more specific source-backed fact; ordinary local projection should not be dismissed merely as opaque. A field marked deletable must still preserve the source-declared task and constraints, including a required save action.

Track disagreements rather than rewriting this inventory to match the generated run. A represented boundary is not proof of semantic correctness; a necessary input is not automatically sensitive; an unused input is not automatically an executed disclosure; completed propagation is not complete DOE. This inventory has not yet been compared with any new run.
