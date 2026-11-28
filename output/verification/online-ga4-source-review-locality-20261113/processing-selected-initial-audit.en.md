# Initial selected partial processing: source coverage audit

Snapshot before source review; not propagation coverage or final selected evidence.

Selected file: `D:\Projects\SkillFlow\experiments\doe\runs\document-guided-ga4-source-review-locality-high-20261113-203902\steps\processing\value.json`; SHA-256 `0d781ad2a740cc7264c1e3e9a103db71310b3c63ff29e46f6152b51266aa7f0a`.
Initial CFG SHA-256: `24befff7f6e705d0fe53a02f5552ab82bd0644ed7a05ce9cbad6fc0cde557fc3`.

- 679 CFG IR = 633 retained modeled + 2 source-unmodeled + 44 validation-isolated; no missing or overlapping IDs.
- 54 combined gap records = 10 model records (2 unmodeled + 8 ordinary limitations) + 44 validation-origin records.
- 77 a002 diagnostics cover 44 isolated IR; a002 remains structurally invalid and has no accepted_call.
- All 13 direct remote sites and 25 physical saveResult sites have retained boundary operations; backend reachability is not yet established.

- **partial-selection-is-not-accepted-a002**: The a002 response is structurally invalid and accepted_call is null. The selected step value is a program-isolated partial fragment retaining 633 modeled IR. Its 10 model gap records contain two unmodeled IR and eight ordinary limitations; the 44 validation-origin gaps in result.json produce 54 combined gap records. Those numbers describe different sets and must not be interchanged.
- **source-unmodeled-only-undefined-values**: The two source-declared unmodeled IR are absent mobile and rich-results sections yielding JavaScript undefined. The supplied reasons distinguish undefined from null and explain serialization consequences. They are separate from the 44 program-isolated records.
- **ir111-coverage-corrected**: The missing report-RPC dispatch now has a source-evidenced empty specification and is retained. The correction also represents 46 of the former 48 source-unmodeled IR. Passing record coverage does not establish their source semantics.
- **all-save-wrappers-and-path-identities-still-unrepresented**: All 25 physical saveResult sites remain modeled as a direct write of input[0] to category-level symbolic storage. Actual saveResult creates a wrapper containing data and metadata, incorporates current settings/propertyId, time, category and labels, derives a concrete path, and serializes that wrapper. The selected summaries do not construct this wrapper or bind the dynamic path. The prose at ir_115 claims metadata wrapping while its operations still write input[0] only. The separate saveResult function body does not by itself connect those summaries to their physical call occurrences.
- **bulk-dimension-double-wrapping-persists**: CFG input[2] is already [{name:pagePath},{name:pageTitle}], but the retained processing for_each builds {name:item} for each existing object, producing nested names. The source passes the object array directly; only the metric-name strings require mapping. This is a source mismatch despite retention by structural validation.
- **loop-boundaries-improved-but-normal-helper-substitution-remains**: The correction introduces separate pre-request and post-request error cases for the two high-level loops; post-request cases explicitly deliver publish/inspect requests. Normal branches and the low-level batch still invoke local tool locations update/inspection, rather than explicit remote events, and omit the per-URL console event inside the protected body. Separate standalone remote IR do not establish member-specific normal-path remote coverage. The ordinary gaps accurately retain uncertainty about response acquisition before a later exception.
- **former-child-gaps-now-local-tools-plus-storage**: All 25 formerly unmodeled high-level child acquisitions are now retained as local tool calls and separate category-storage writes. This recovers modeled records and explicit default-save effects, but does not by itself model the child invocation's actual network request/response, helper defaults, save wrapper, dynamic path or receiver identity. Do not equate the higher modeled count with those external boundaries being covered.
- **receiver-and-interface-evidence-limit**: The 13 direct calls retain remote request/response operations. Their generic locations do not bind the CFG method receiver. The model now records this explicitly at ir_110, including the unknown SDK token-exchange relation. Several interface contracts cite actual request construction and say those fields select an operation; current supplied fields alone do not establish the interface's sufficient-and-necessary field requirements. This snapshot does not establish verified minimal contracts.
- **summary-still-an-explicit-gap**: The ordinary gap still records absent summary reader binding, Markdown transform and Markdown write coordinates, plus the lack of invocation-to-file binding. Task analysis-summary remains a documented obligation, not a fulfilled source boundary.
- **validation-isolation-extends-beyond-boundary-nodes**: Isolation includes resource handles, client-cache writes, save defaults, response projections, clock reads, save filename/metadata clocks and load dispatch/projections. Although all direct remote and physical save-site IR survive, surrounding and upstream records do not. Only saved propagation records can later establish which concrete sites were actually processed.

## Validation-isolated instructions

- ir_001: index_import_dotenv / acquire_interface; validate_ref.
- ir_009: index_runtime_identity / acquire_runtime_identity; validate_ref.
- ir_016: setup_script / acquire_shell_script_path; validate_ref.
- ir_054: ga_client_create / write_module_state; mechanism_evidence_reference.
- ir_065: sc_client_create / write_module_state; mechanism_evidence_reference.
- ir_076: indexing_client_create / write_module_state; mechanism_evidence_reference.
- ir_100: report_request_base / default_if_undefined; mechanism_evidence_reference.
- ir_112: report_response / select_first_response; mechanism_evidence_reference.
- ir_164: bulk_normalize / default_if_undefined; mechanism_evidence_reference.
- ir_165: bulk_normalize / default_if_undefined; mechanism_evidence_reference.
- ir_179: bulk_save / original_string_or_custom; mechanism_evidence_reference.
- ir_185: active_request / default_if_undefined; mechanism_evidence_reference.
- ir_199: rt_events_request / default_if_undefined; mechanism_evidence_reference.
- ir_213: rt_pages_request / default_if_undefined; mechanism_evidence_reference.
- ir_227: rt_sources_request / default_if_undefined; mechanism_evidence_reference.
- ir_241: md_dims_request / default_if_undefined; mechanism_evidence_reference.
- ir_255: md_metrics_request / default_if_undefined; mechanism_evidence_reference.
- ir_269: md_full_request / default_if_undefined; mechanism_evidence_reference.
- ir_292: sc_range_shorthand_end_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_294: sc_range_shorthand_start_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_298: sc_range_fallback_end_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_300: sc_range_fallback_start_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_314: sc_query_response / select_response_data; mechanism_evidence_reference.
- ir_342: update_request / default_if_undefined; mechanism_evidence_reference.
- ir_350: update_fallback_clock / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_362: delete_request / default_if_undefined; mechanism_evidence_reference.
- ir_370: delete_fallback_clock / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_382: inspect_request / default_if_undefined; mechanism_evidence_reference.
- ir_412: batch_init / default_if_undefined; mechanism_evidence_reference.
- ir_436: overview_analysis / original_string_or_custom; mechanism_evidence_reference.
- ir_449: traffic_analysis_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_462: content_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_475: behavior_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_481: compare_calls / default_if_undefined; mechanism_evidence_reference.
- ir_482: compare_calls / default_if_undefined; mechanism_evidence_reference.
- ir_513: sc_overview_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_524: keyword_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_535: seo_calls / original_string_or_custom; mechanism_evidence_reference.
- ir_591: save_filename_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_603: save_metadata_time / acquire_time; validate_event_operations, validate_operation_boundary.
- ir_614: load_read / dispatch; mechanism_evidence_reference.
- ir_615: load_parse / select_read_contents; mechanism_evidence_reference.
- ir_617: load_parse / dispatch; mechanism_evidence_reference.
- ir_619: load_return / select_parsed_contents; mechanism_evidence_reference.

This is the initial selected partial fragment before source review and any semantic repair; final selected identities require a separate audit.
Retained or modeled is not processed, reached, source-equivalent, contract-verified or task-complete.
This helper reads saved JSON only and invokes no validator, compiler, backend, model, Skill, replay or tests.
