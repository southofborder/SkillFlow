# Rejected processing a001: preliminary source audit

This raw candidate is unaccepted. No backend coverage is inferred.

{"cfg_instructions": 679, "modeled": 630, "explicit_unmodeled": 48, "processing_gap_records": 54, "missing": ["ir_111"], "unmodeled_high_level_child_acquisitions": 25, "other_unmodeled": 23, "remote_physical_sites_with_remote_call_ops": 13, "save_physical_sites_with_storage_write_ops": 25}

- ir111-dispatch-omission: ir_111 is the empty dispatch immediately after the runReport acquisition. A non-unmodeled processing_gap note exists, but no modeled specification or explicit unmodeled coverage exists, so the instruction coverage check correctly rejects a001.
- unmodeled-upstream-and-child-acquisitions: 48 explicit unmodeled IR comprise 25 high-level child acquisitions and 23 setup/helper/default/undefined cases. Several missing property/client/parser/default operations precede direct remote requests in their CFG blocks. Direct boundary operations being present does not establish those paths will be processed or their results usable. Many reasons describe required work the model did not represent, rather than a semantic relation missing from the supplied source.
- all-save-wrappers-and-path-identities-unrepresented: Every raw saveResult summary writes only input[0] directly to a category-level symbolic storage location. The source instead constructs a wrapper containing data and save-time metadata, derives the path from category/operation/extraInfo/current settings/time, and writes serialized wrapper content. The prose at ir_115 claims wrapping, but its operations contain no wrapper construction, metadata acquisition or dynamic path binding. This is stronger boundary representation than a local-tool placeholder, but not the complete source save behavior.
- bulk-dimension-double-wrapping: CFG input[2] already contains [{name:pagePath},{name:pageTitle}]. Raw processing iterates those objects and builds {name:item}, producing nested name objects rather than the source's existing name strings. Metrics input[3] is a string array and is correctly the one that requires name-object mapping. The raw deterministic construction must not be treated as source-equivalent merely because its schema validates.
- loop-helper-tool-substitution: The batch update and both protected high-level URL calls use in-process updateHelper/inspectHelper tool locations. Their raw normal/error operations do not contain the actual remote publish/inspect or per-URL console event. Error-split gaps acknowledge uncertainty but do not establish the normal-path remote action. Separate standalone remote definitions do not prove the same member invocation's boundary coverage.
- receiver-and-interface-evidence-check: The direct remote calls pass the constructed request but omit the CFG's separate receiver-handle operand from the call inputs and use generic named remote locations without operand_refs. Check whether caller/receiver/authentication identities are preserved elsewhere in the final compilation. Contract evidence often cites constructed arguments themselves; those alone do not establish a tool interface's sufficient-and-necessary field requirements.
- summary-gap-is-recorded-not-implemented: The non-unmodeled gap at ir_678 explicitly notes no Markdown processing/write coordinate, the lack of invocation-to-saved-file binding, and conditional/empty paths without a saved file. This preserves a limitation; it is not an implementation or fulfillment of Task analysis-summary.

## Explicit unmodeled instructions

- ir_021 / setup_install / npm_install: The setup invokes npm install in the successfully changed directory. The fragment leaves the npm process exit status and dependency installation effects unmodeled. Lockfile registry URLs identify possible package origins, while runtime cache and per-package fetch outcomes are unavailable.
- ir_103 / report_request_base / call_parseDateRange: The call-site parser summary needs the original range plus a conditional settings acquisition on falsy input. The standalone parser's result is scoped to its invocation.
- ir_114 / report_save / report_save_labels: The save labels derive from joined dimensions with custom fallback and an original string range when supplied. The extra output requires the JavaScript undefined alternative.
- ir_171 / bulk_request / call_getPropertyId: The bulk property getter needs a fresh settings read and properties/ formatting at this invocation.
- ir_172 / bulk_request / call_bulk_parseDateRange: The bulk parser needs call-site representation of its conditional default lookup and object or relative-range return.
- ir_187 / active_request / call_getPropertyId: The active-user request has a fresh property target read independently of the GA4 client cache.
- ir_201 / rt_events_request / call_getPropertyId: The event request has its own current formatted property target.
- ir_215 / rt_pages_request / call_getPropertyId: The pages request has its own current formatted property target.
- ir_229 / rt_sources_request / call_getPropertyId: The sources request has its own current formatted property target.
- ir_242 / md_dims_request / call_getClient: The dimensions metadata request needs the handle from this cache-hit or validated creation path.
- ir_243 / md_dims_request / call_getPropertyId: The dimensions metadata request formats the current property ID separately from handle creation.
- ir_244 / md_dims_request / build_metadata_request: The request name is the current formatted property with /metadata appended.
- ir_256 / md_metrics_request / call_getClient: The metrics metadata request needs the handle from this cache-hit or validated creation path.
- ir_257 / md_metrics_request / call_getPropertyId: The metrics metadata request separately formats the current property ID.
- ir_258 / md_metrics_request / build_metadata_request: The metrics request name is the current formatted property with /metadata appended.
- ir_270 / md_full_request / call_getClient: The full metadata request needs the handle from this cache-hit or validated creation path.
- ir_271 / md_full_request / call_getPropertyId: The full metadata request separately formats the current property ID.
- ir_272 / md_full_request / build_metadata_request: The full request name is the current formatted property with /metadata appended.
- ir_306 / sc_query_request / apply_search_defaults: The four independently defaulted options require separately selected undefined alternatives. Their defaults are query grouping, row limit 1000, offset 0 and saving enabled.
- ir_309 / sc_query_request / call_parseSearchConsoleDateRange: The query needs its own parser invocation with conditional settings and two distinct clock reads on string paths, while object input passes through.
- ir_316 / sc_query_save / search_save_labels: The labels combine effective dimensions with a query fallback and retain the original range only for strings. The absent extra requires undefined.
- ir_395 / inspect_mobile_absent / undefined_value: Absent mobile usability is JavaScript undefined. The literal format admits JSON values only, and null would change the serialized representation.
- ir_402 / inspect_rich_absent / undefined_value: Absent rich results is JavaScript undefined, distinct from a JSON null value or a populated object.
- ir_428 / overview_analysis / call_getPageViews: The site-overview pageViews field requires this specific report call using the original dateRange and its default child save.
- ir_430 / overview_analysis / call_getTrafficSources: The site-overview trafficSources field requires this original-range report acquisition and its default child save.
- ir_432 / overview_analysis / call_getUserDemographics: The demographics field needs this original-range demographics response and child save.
- ir_434 / overview_analysis / call_getEventCounts: The events field needs this original-range event report response and child save.
- ir_443 / traffic_analysis_calls / call_getTrafficSources: The sources field needs the traffic-sources report from this call and its default save.
- ir_445 / traffic_analysis_calls / call_runReport: The sessions field needs this source-medium report with its four metrics, original range and default save.
- ir_447 / traffic_analysis_calls / call_runReport: The newVsReturning field needs the report acquired with this dimension, original range and specified metrics, with default save.
- ir_456 / content_calls / call_getPageViews: The content pages field needs this page-view report call and default save.
- ir_458 / content_calls / call_runReport: The landingPages field requires this original-range report and default child save.
- ir_460 / content_calls / call_runReport: The exitPages field requires this pagePath report using exits and screenPageViews and default child save.
- ir_469 / behavior_calls / call_getUserDemographics: The user-behavior demographics field needs its own original-range acquisition and child save.
- ir_471 / behavior_calls / call_getEventCounts: The user-behavior events field needs its own original-range acquisition and child save.
- ir_473 / behavior_calls / call_runReport: The engagement field needs this date-grouped acquisition and default child save.
- ir_493 / liveSnapshot / call_getActiveUsers: The snapshot's activeUsers value is acquired through this zero-argument child, with its own realtime response and active_users save.
- ir_495 / liveSnapshot / call_getRealtimePages: The snapshot's currentPages value is acquired through this zero-argument child with default pages save.
- ir_497 / liveSnapshot / call_getRealtimeEvents: The snapshot's currentEvents value is acquired through this zero-argument child with default events save.
- ir_505 / sc_overview_calls / call_getTopQueries: The overview topQueries field needs this independent query-grouped Search Console response and default child save.
- ir_507 / sc_overview_calls / call_getSearchConsoleTopPages: The overview topPages field needs this page-grouped Search Console response and default child save.
- ir_509 / sc_overview_calls / call_getDevicePerformance: The overview devicePerformance field needs its device-only acquisition and child save.
- ir_511 / sc_overview_calls / call_getCountryPerformance: The overview countryPerformance field needs its country-only acquisition and child save.
- ir_520 / keyword_calls / call_getTopQueries: The keyword analysis queries field needs its own query-grouped acquisition and child save.
- ir_522 / keyword_calls / call_getDevicePerformance: The deviceBreakdown field needs this independent device-only acquisition and child save. The source supplies no query-device joint grouping.
- ir_531 / seo_calls / call_getSearchConsoleTopPages: The SEO topPages field needs this independent page-grouped acquisition and child save. Ranking language in the log cannot supply a request sort field.
- ir_533 / seo_calls / call_getCountryPerformance: The countryBreakdown field needs this independent country-only acquisition and child save.
- ir_578 / getAvailableFields / call_getPropertyMetadata: The zero-argument call acquires the full first metadata response and uses the default metadata/full save before logging counts and returning that response. The reference's descriptions of the separate metadata methods as arrays conflict with their object returns.

This is not selected processing, successful compilation or propagation coverage. Recheck the accepted correction and any semantic repair separately.
The helper reads saved JSON only; it invokes no compiler, validator, model, Skill, backend or replay.
