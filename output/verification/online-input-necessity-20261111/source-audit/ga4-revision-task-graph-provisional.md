# GA4 revised Task and CFG provisional audit

Status: **PROVISIONAL; revision processing and rereview are not assessed.** Captured 2026-11-11T19:22:44.875466+08:00.

The revised Task has 68 requirements and 15 issues (4 unresolved). The revised wire CFG has 658 instructions, 279 blocks and 259 edges. All 13 explicit remote call sites, 25 saveResult sites and 3 URL loops still map to the original-source inventory. Every mapped call line matches its source excerpt; all 25 internal save calls still have no returned path output.

Initial source review contained 39 findings and checked the 45 supplied compute contracts: 31 accepted, 5 rejected and 9 unresolved. Those counts apply only to the initial submitted inventory and do not certify omitted tool contracts.

## Repair correspondence

### RT01 — represented

Direct help is now a separate conditional Task declaration and a guarded graph path. It does not promise analysis on every direct invocation.

Initial review: F001.

### RT02 — represented_with_scope_watchpoint

Task adds separately callable settings, validation, client initialization/reset and parser contracts. These have export/type/comment/implementation evidence. Their whole return requirements must stay scoped to the relevant utility invocation; the public Settings accessor does not justify whole Settings demand for a property-only internal consumer. Shared validation remains a current utility contract, not an independent non-GA4 resource purpose.

Initial review: F002.

### RT03 — explicitly_resolved_or_unresolved

Task resolves metadata collection wording to an object with the selected array, preserving the named member fields; it explicitly leaves per-path bulk row coverage, duplicate handling and alignment unresolved. Whole response belongs to the separate full-metadata operation.

Initial review: F003.

### RG01 — represented

Revision introduces separate module dependency/interface entries for settings, client, storage, each API and index. Constraints distinguish ESM evaluation reuse, type-only imports and independent exported entries, replacing the single settings-to-client-to-index route. Runtime linking/processing correctness is still pending.

Initial review: F004.

### RG02 — represented

shell_cd now returns setup_cwd and npm_install consumes that same result, with success gating retained.

Initial review: F005.

### RG03 — represented

Explicit member/accumulator loops now represent standard-report dimension and metric maps, bulk metric map, result-list suffix filter and path map, and latest-result path filter. The original three URL loops remain separate. Source-site counts are unchanged; finite traversal representation is not proof of backend completion or all occurrence correlations.

Initial review: F006.

### RG04 — represented_in_cfg_pending_processing

Each missing optional inspection section now has an explicit materialize_undefined result for the corresponding merge predecessor. This is the JavaScript source value, not null; whether current processing can represent it remains pending.

Initial review: F007.

### RG05 — represented_in_summary_pending_processing

Both protected-update summaries now take the current accumulator, include construction and push inside the protected operation, and return either the updated accumulator or abrupt accumulator state plus actual exception. Success successors select rather than perform the protected append. This addresses the earlier missing accumulator dependency; exact post-failure effects remain a processing concern.

Initial review: F008.

### RG06 — documentary_obligation_only

Four workflow blocks add ordered analysis, persistence, saved JSON read and Markdown creation/write obligations. They explicitly retain unknown file/write-version selection and unspecified writer implementation. These nodes must not be counted as newly implemented remote/storage source sites or as a completed summary. The 13 remote/25 saveResult denominator excludes documentary obligations.

Initial review: F009.

### RG07 — processing_still_pending

Revision improves graph context and summary operands, including a separate GoogleAuth constructor with settings input. The revision-processing stage, its source review, compiled input contracts and source provenance are not inspected in this Task/CFG audit. Initial helper/receiver/cache and output-transfer issues cannot be called fixed from graph prose alone.

Initial review: F010, F011, F012, F013, F015, F016.

## Source limits remain

The actual Skill source remains unchanged. Advertised custom filters/orderBy are still absent from the request, newest-operation selection still uses a filename substring, and Search Console calendar restrictions are not enforced on passed objects. Ranking, query/device correlation, per-URL row coverage and summary invocation/file ownership retain explicit limitations. Documentary Markdown obligations do not provide an implemented writer or identify a concrete saved version.

Task utility declarations have source support but must remain conditional on the relevant invocation. A direct whole Settings accessor contract cannot establish whole-object necessity for every internal settings consumer; a saved-wrapper field does not turn the GA4 property into a non-GA4 resource selector.

## Evidence and continuation

`ga4-revision-task-graph-provisional.json` records all 38 exact callsite mappings, loop edge pointers, source references, initial-review correspondence and artifact hashes. The graph pointers address the revised wire graph, not the initial compiled graph. Initial audit pointers are superseded for this revision and remain preserved as initial evidence.

Revision graph SHA-256: `b842bdf072e789a9cb0f521e16e1e6fbfba8be9a5e6e94ec48d2b377ea76296c`.

Revised Task SHA-256: `7a35cff8041e48ff354b06294f633edfe45e311eb41a585d31f6b7cc62538e47`.

Final selected processing, reviewed contracts, source-supported demand and actual propagation remain pending. No changes or audit feedback were sent to the running pipeline.
