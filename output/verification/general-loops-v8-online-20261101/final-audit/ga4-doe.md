# GA4 v8: independent final DOE audit

The run did **not** produce complete propagation or a useful substantive DOE conclusion. It saved a **partial diagnostic result**: 29 of 420 generated IRs were processed (6.90%), five reached explicit unmodeled cutoffs, and 386 were blocked. Both saved propagation sinks and DOE sinks are empty. The result is useful for locating modeling failures; it does not tell the user which actual sensitive payloads are unnecessary.

This assistant audit read saved JSON and the current run's frozen source after closure. It made no target call, compiler/solver call, replay, or production change. The 24 source-derived correctness criteria are assistant criteria, not human gold.

## Actual result and denominators

| Measure | Observed result |
|---|---:|
| Generated IR processed / all generated IR | 29 / 420 (6.90%) |
| Reached unmodeled / downstream blocked IR | 5 / 386 |
| Emitted substantive sink DOE judgments | 0 |
| Source-supported / contradicted emitted DOE conclusions | 0 / 0, denominator **0** |
| Unresolved declared boundary coordinates | 14: 9 network, 3 model observations, 2 storage |
| Resolved sensitivity declarations | 0 / 57, across 23 declared scopes |
| Sensitivity / demand derivations | 0 / 0 |
| Constraint checks / preservation / influence results | 0 / 0 / 0 |
| Task realization records | 45 partial, 1 unmapped |
| Diagnostics | 787; overlapping causes and dependent sites |

Evidence: [DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/doe/doe-result.json), [propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/propagation/manifest.json), and [saved sinks](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/propagation/sinks.json).

The unresolved boundary coordinates and zero emitted conclusions are **different denominators**. `expected_sinks: 0` reflects the generated propagation inventory, not the source program: actual Google requests and persistence appear in the frozen source. No-exposure, no-DOE, precision, recall, or an accuracy percentage can be inferred from this empty sink result. The 24 source relations have no end-to-end DOE score here. Generated-IR coverage also must not be substituted for source API/save-site coverage.

The five cutoffs are `ir_019`, `ir_035`, `ir_039`, `ir_053`, and `ir_419`. Their saved diagnostic is `unmodeled_processing`: the affected block stops before evaluation and OUT publication. The subsequent empty DOE is a consequence of incomplete propagation. It is not evidence that a solver successfully analyzed the business loop bodies and found nothing excessive.

## Remaining review findings checked against source

The final independent source review itself completed and retained ten findings. Their core source-defect statements are corroborated below. This is a check of ten retained objections, **not** ten successful DOE conclusions or a 100% accuracy claim. One review target is misplaced; suggested implementation repairs were not executed by this audit.

| ID | Remaining defect and concrete evidence |
|---|---|
| F001 | **CFG ordering.** Bulk filtering precedes client acquisition in source, but block_071 client acquisition precedes block_081 filtering. Failure-side settings/client effects are therefore overapproximated in the wrong order. Source: `scripts/src/api/bulk-lookup.ts:155-172`. |
| F002 | **Request payload structure.** The selected processing builds top-level inspectionUrl/siteUrl, while the source passes requestBody.inspectionUrl/siteUrl. Source: `scripts/src/api/indexing.ts:152-157`. |
| F003 | **Boundary summary / processing cutoff.** The frozen source explicitly invokes zero-argument dotenv.config(), while ir_019 marks the complete call/environment post-state unmodeled and cuts off dependent propagation. Source: `scripts/src/config/settings.ts:5-9`. |
| F004 | **Call-boundary representation.** The settings implementation visibly reads five named environment entries, obtains cwd and builds the settings result. Selected call sites remain unmodeled because internal invocation linkage is unavailable. Source: `scripts/src/config/settings.ts:40-48; scripts/src/core/client.ts:28-38; scripts/src/core/storage.ts:64-65,123-125`. |
| F005 | **State-version linkage.** ir_077 reads caches, while initializers/constructors/reset update the separate ga4_cache, search_cache and indexing_cache locations. The annotation has no declared relation linking that aggregate read to those updates. Source: `scripts/src/core/client.ts:12-25,58-61,87-120`. |
| F006 | **Occurrence summary omissions.** ir_287 notification_normal mentions client acquisition only in its condition, then builds/publishes a request and computes notification from response plus URL. It has neither cache/creation effects nor the clock input used by the source fallback. Source: `scripts/src/api/indexing.ts:57-79; scripts/src/core/client.ts:67-122; scripts/src/index.ts:305-312`. |
| F007 | **Known source projection treated as unavailable.** ir_200/201/214 leave inspection field extraction opaque despite the frozen implementation providing paths/defaults; ir_214 additionally uses api_spec as a possible dependency although source result construction uses response fields. Source: `scripts/src/api/indexing.ts:159-192`. |
| F008 | **Missing field-level necessity.** Selected realizations state that row-value paths are unavailable. The frozen ReportResponse and RealtimeResponse interfaces explicitly provide rows[].dimensionValues[].value and rows[].metricValues[].value. Existing shape/outbound demands do not replace returned-measurement demands. Source: `scripts/src/api/reports.ts:33-42; scripts/src/api/realtime.ts:11-19; scripts/src/index.ts:195-203`. |
| F009 | **Overbroad necessity.** Dimension/metric discovery demands whole acquired collections by value although their documented entries require apiName, uiName and description. The separate full-property-metadata contract explicitly requires its full response. Source: `references/api-reference.md:165-193; scripts/src/api/metadata.ts:11-24,46-54`. |
| F010 | **Missing order requirement.** Task indexing_batch requires input-order notification results; source loops in input order and appends each result. The selected annotation has cardinality/member demands but zero order demands. Source: `references/api-reference.md:282-291; scripts/src/api/indexing.ts:92-104`. |

For F002, the submitted review target `cfg:/blocks/block_084/instructions/1` points to `ir_170` (dispatch); construction is `instructions/0`, `ir_169`. The actual top-level-field error is confirmed in the selected processing's `inspection` case. This correction is recorded in this audit only; the original review is preserved.

F003/F004 identify visible boundaries and a source-grounded summary direction; they do not establish unknown dotenv internals, exact environment precedence, cache-hit counts, or the correctness of a future implementation. F008's interfaces provide field paths but do not prove runtime response validation. F009 identifies overbroad necessity, not an observed extra runtime field: full-property metadata and complete saved results retain their separate legitimate whole-object requirements.

See the [retained review](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/revision/review/result.json), [selected annotation](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/revision/annotation/audit/compiled-response.json), [Task](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/revision/task/task.json), and [selected CFG](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/graph/revision.json). The accompanying [audit JSON](ga4-doe.json) records per-finding artifact locations, source ranges, caveats, evidence hashes and the exact unresolved boundary list.

## What this run establishes

The backend now produces and preserves a partial DOE artifact for this run. It does **not** yet establish full GA4 analysis or useful payload/condition/receiver-specific minimization. Immediate coverage loss comes from unmodeled processing and CFG/processing boundary mismatches; remaining annotation and demand defects would matter even after those cutoffs were removed. The saved evidence does not justify attributing this failure to a currently running loop fixed point, nor does it prove the business loops were successfully evaluated.

The completed review is valuable diagnosis, including concrete request nesting, cache-location, known projection and necessity defects. Repairing those artifacts is separate future work. No historical result, answer, implementation, or failure record was modified by this audit.
