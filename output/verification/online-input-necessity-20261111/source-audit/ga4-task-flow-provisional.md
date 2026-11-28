# GA4 provisional Task and flow source audit

Status: **PROVISIONAL; the fresh run is still active.** Captured 2026-11-11T17:50:42.605099+08:00.

This assistant-authored read-only audit compares the accepted initial Task and flow with the independent original-source inventory. It was not fed back into the running pipeline. No model calls, Skill execution or replay were performed for this audit. Final source review and input contracts are still pending.

The Task contains 61 declarations and 12 issues, including 3 unresolved issues. All 174 physical source references are in range; the original 16 source files remain byte-identical and the source SHA matches. The flow descriptively covers the finite inventory of 13 explicit awaited remote calls, 25 saveResult sites and 3 URL loops. These are descriptive mentions, not generated-IR or propagation coverage.

The central pending questions are whether final mapping treats the generic saved-wrapper format as requiring a populated GA4 property identifier for non-GA4 tasks, and whether actual whole SDK response forwarding is incorrectly promoted into whole-value task necessity. Neither is a confirmed final finding at this stage.

## Source comparisons

### P01 — aligned

The purpose and analysis-results declaration select appropriate operations for a request rather than requiring all exports on every invocation. Three-phase analysis, saving and summary is explicitly documented. Setup and per-operation purposes remain separately scoped.

Task declarations: analysis-results. Flow document lines: 5, 34, 62.

Original source: `SKILL.md:28-37`; `SKILL.md:53-64`.

### P02 — aligned_with_pending_mapping

GA4 property scope is confined to GA4 operations in ga4-property. The shared-ga4-validation issue explicitly gives no separate task purpose for a populated GA4 property in standalone Search Console or indexing. This agrees with the source-only distinction between actual validation and task purpose.

Task declarations: ga4-property, search-console-site, api-prerequisites. Flow document lines: 7, 9, 29, 30.

Original source: `scripts/src/config/settings.ts:40-73`; `scripts/src/core/client.ts:23-52`; `scripts/src/core/client.ts:67-132`.

### P03 — source_conflict_preserved

Task retains documented filters and ordering as requirements while its ga4-custom-options-unused issue records that the request implements neither. Flow states the same omission. Later absence of demand for these options cannot certify fulfillment of the declared filtering or ordering.

Task declarations: custom-ga4-filtering, custom-ga4-ordering. Flow document lines: 15.

Original source: `references/api-reference.md:31-45`; `scripts/src/api/reports.ts:20-28`; `scripts/src/api/reports.ts:78-100`.

### P04 — aligned_with_pending_mapping

Projected metadata declarations require all members with apiName, uiName and description. Flow correctly describes the dimensions-only or metrics-only wrapper and the whole response of getPropertyMetadata. A whole response is explicitly documented for the full metadata operation. This does not authorize every property of every projected member or the unselected top-level branch.

Task declarations: metadata-dimensions, metadata-metrics, metadata-full. Flow document lines: 28, 46.

Original source: `references/api-reference.md:165-193`; `scripts/src/api/metadata.ts:11-33`; `scripts/src/api/metadata.ts:38-95`.

### P05 — aligned_with_pending_mapping

Flow states that checkIndexStatus keeps only indexStatus from inspectUrl, with the supplied URL and verdict-derived flag. Task scopes its workflow requirement accordingly. Mobile usability, rich results and inspection link are not demanded by that workflow declaration, although direct inspectUrl has its own broader output purpose.

Task declarations: indexing-inspection, indexing-status-workflow. Flow document lines: 30, 54.

Original source: `references/api-reference.md:304-313`; `scripts/src/api/indexing.ts:146-193`; `scripts/src/index.ts:324-345`.

### P06 — aligned_with_pending_mapping

The public saveResult declaration includes a returned path, which is supported for direct use of that exported helper. Flow explicitly records that all API/orchestrator callers discard it and return their data. Mapping this path as a public output of every internal save would contradict flow and source.

Task declarations: result-wrapper. Flow document lines: 58.

Original source: `references/api-reference.md:360-371`; `scripts/src/core/storage.ts:58-95`; `scripts/src/api/reports.ts:100-108`; `scripts/src/index.ts:59-76`.

### P07 — scope_watchpoint

The result-wrapper declaration makes propertyId part of every saved wrapper, based on the declared storage interface and the current writer. The public reference promises a metadata wrapper but does not enumerate propertyId. This is explicit source format support, not independent evidence that a populated GA4 identifier is needed for standalone Search Console or indexing purposes; the Task shared-ga4-validation issue acknowledges that distinction. Final mapping must expose whether it treats the format contract as an exact preservation requirement or incorrectly generalizes a GA4 resource purpose. No unsupported-field conclusion is made yet.

Task declarations: result-wrapper, ga4-property. Flow document lines: 58.

Original source: `references/api-reference.md:360-371`; `scripts/src/core/storage.ts:9-26`; `scripts/src/core/storage.ts:79-94`.

### P08 — scope_watchpoint

Task describes structured rows/selected values for ordinary reports and Search Console; it does not explicitly require each opaque SDK response field. Flow accurately records whole response forwarding as an actual fact. The all-results auto-save wording and generic saveResult(data) contract must not silently turn every incidental response field into a task-required field. Exact demand seeds, reviewed output parts and input contracts remain unavailable to this provisional audit.

Task declarations: custom-ga4-report, search-analytics-query, result-auto-save, result-wrapper, summary-source. Flow document lines: 15, 27, 28, 29, 58, 62.

Original source: `SKILL.md:53-64`; `references/api-reference.md:31-45`; `references/api-reference.md:201-213`; `scripts/src/api/reports.ts:100-108`.

### P09 — aligned_with_pending_mapping

Flow preserves truthy range and limit behavior, the empty-bulk early return and the source default values. Task preserves caller-visible defaults and save opt-out. A future if_present input range must follow the actual constructed request, and must not erase a source truthiness guard or substitute absent-value semantics.

Task declarations: date-default, bulk-empty-lookup, result-auto-save, result-file-naming. Flow document lines: 13, 15, 27, 29, 30, 58.

Original source: `scripts/src/api/reports.ts:47-72`; `scripts/src/api/reports.ts:78-100`; `scripts/src/api/bulk-lookup.ts:149-191`; `scripts/src/core/storage.ts:72-86`.

### P10 — aligned

The flow separates low-level fail-fast notification batching from per-member catches in high-level reindexUrls/checkIndexStatus, preserves success URL spread precedence, and identifies aggregate writes after loop exit. Task requires corresponding ordered outcomes, not distinct-value URL deduplication.

Task declarations: indexing-recrawl-batch, indexing-reindex-workflow, indexing-status-workflow, combined-results. Flow document lines: 48, 52, 53, 54.

Original source: `scripts/src/api/indexing.ts:89-105`; `scripts/src/index.ts:301-345`.

### P11 — explicit_unresolved

Task retains uncertainty about the summary trigger and persistence opt-out. Flow states that saved file readers are not linked to a particular producer invocation and no supplied implementation closes the Markdown writer gap. Neither current artifact establishes a source-complete summary data path.

Task declarations: summary-source, summary-artifact. Flow document lines: 60, 62.

Original source: `SKILL.md:53-64`; `SKILL.md:129-142`; `scripts/src/core/storage.ts:103-171`.

### P12 — source_conflicts_preserved

Task keeps the standalone top-pages impressions requirement and high-level SEO clicks description scoped to their conflicting declarations, with an unresolved ranking issue. The keyword-device association also remains unresolved. Flow records the lack of explicit sort and the separate device report, avoiding invented correlations.

Task declarations: search-top-pages, search-overview, search-seo-page-performance, search-keyword-analysis. Flow document lines: 29, 43, 44.

Original source: `SKILL.md:81-85`; `references/api-reference.md:225-233`; `scripts/src/api/searchConsole.ts:127-164`; `scripts/src/index.ts:261-295`.

## Evidence and limits

The machine-readable companion, `ga4-task-flow-provisional.json`, records exact artifact hashes, source references, all finite remote/save crosswalks and pending checks. Flow references address `steps/flow/document.md`; Task declaration IDs identify entries in `task/task.json` under the fresh run:

`D:\Projects\SkillFlow\experiments\doe\runs\document-guided-ga4-input-necessity-high-20261111-173347`

The source-only baseline is `ga4-boundary-expectations.json` and `ga4-source-audit.md` in this directory. Do not rewrite that baseline based on model answers. Preserve this provisional capture if the pipeline later repairs Task or flow.

This audit does not establish source-complete CFG generation, propagation coverage, accepted semantic contracts, minimum demand, deletability, absence of excess acquisition or complete DOE. Final checks require the closed controller artifacts and its one authorized replay.
