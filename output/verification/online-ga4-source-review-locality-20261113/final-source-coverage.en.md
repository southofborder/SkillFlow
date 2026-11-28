# GA4 source coverage at closure

The run failed in revision-processing before propagation or DOE. There is no measured backend source-boundary coverage or minimization result.

Run: `document-guided-ga4-source-review-locality-high-20261113-203902`. Controller closed at `2026-11-13T16:27:01.947083+00:00`.
Native revision-processing status: `timeout`, elapsed 2700.031960 seconds. Sole replay: `matched`, 0 new native markers.

| Material | Final selected | Unselected repair candidate |
|---|---|---|
| Task requirements | 46 | 58 |
| CFG | 268 blocks / 679 IR | 302 blocks / 770 IR |
| Processing | 633 modeled + 2 source-unmodeled + 44 validation-isolated | No completed answer |
| Propagation / demand / DOE | Not run; no result records | Not run |

Selected CFG file SHA-256: `24befff7f6e705d0fe53a02f5552ab82bd0644ed7a05ce9cbad6fc0cde557fc3`.
Unselected revised CFG file SHA-256: `f5b9be024271521f251d94fbacf366f3f49736a430138e0831a239418a601a41`.
Selected compiled annotation file SHA-256: `a9053bed0a18f8d6e913da8e320a54fa34034621fbaea10cb7fcc33330b85be0`.

All 16 frozen source files remain byte-identical. All 13 physical remote calls and 25 physical saveResult sites have generated selected representations. Their processed/reached counts are unavailable; this is not a measured 0/13 or 0/25 result.

- **failed-before-backend**: The controller terminated at revision-processing after its native CLI exceeded the 2700-second process limit without a complete final answer. No revision processing value, revised annotation, rereview, propagation or DOE result was produced. The recorded failure is a process deadline, not an established connection timeout; this audit does not infer the provider-side reason for the unfinished answer.
- **final-selection-is-initial-material**: selection.json retains the initial Task, initial 679-IR CFG and initial partial annotation. graph/selected.json is byte-identical to graph/initial.json. The accepted 58-requirement revised Task and accepted 770-IR revised CFG remain unselected repair candidates; their improved structures must not be reported as the final analyzed material.
- **selected-fragment-counts**: The final selected annotation contains 633 modeled IR, two source-unmodeled IR (ir_395, ir_402) and 44 validation-isolated IR, covering all 679 CFG identities. Its 54 gap records comprise ten source-origin records (two unmodeled and eight ordinary limitations) plus 44 validation records. These are representation counts, not instructions processed by propagation.
- **physical-source-coverage-is-not-record-coverage**: The selected CFG/partial annotation represents all 13 physical remote API sites and all 25 physical saveResult sites. There are no recorded propagation outcomes for them because the run stopped earlier. Recorded coverage is unmeasured, not a measured zero-of-13 or zero-of-25 result; no source boundary is certified as reached, safe or unnecessary.
- **source-mismatches-survive-in-final-selection**: The selected initial processing still double-wraps bulk dimension objects at ir_173; all 25 physical save summaries write the raw result without the actual metadata wrapper/dynamic save address. Normal URL helper calls and higher child acquisitions use local tool summaries without establishing the child's occurrence-specific normal network effect. Direct remote calls omit the authenticated receiver relation, and summary operations are absent from the selected CFG. The source review identified several of these problems, but the incomplete repair supplies no selected fix.
- **task-improvements-not-final-selected**: The revised candidate fixes standalone realtime scope, full-property metadata preservation and the empty-bulk save conflict, but the final selected Task remains the original 46-requirement interpretation. Both versions retain documented filters/orderBy duties despite their actual omission in the Skill request, and retain the row-limit obligation without claiming unknown SDK zero semantics.
- **revision-graph-improvements-have-no-processing-evidence**: The accepted revision candidate adds separate report/bulk map coordinates, documentation-level summary read/compose/write, and distinct module dependency routes with explicit cache/state obligations. No completed revised processing answer exists, so these changes have no new executable annotation, verified field demand or propagation result. In particular the earlier bulk double-wrap and save-wrapper problems cannot be declared repaired.
- **review-and-replay-do-not-establish-doe**: The initial source review retained independently valid records and routed the existing shared repair after structural correction exhaustion. Its partial status is not a completed whole-chain contract approval. The controller's sole replay matched with zero new native markers, reproducing the failed lifecycle; replay agreement is not source-semantic correctness or successful minimization.
- **no-deletion-or-necessity-results**: No demand preparation, input assessment, deletion-impact result or DOE comparison was emitted. This run establishes no deletable input, no non-excess result, and no absence of DOE. Missing output artifacts must not be converted into zero findings or safe conclusions.

## Physical source mappings

The revision IDs below belong to an unselected candidate; every row has no propagation record.

| Physical site | Final selected IR | Unselected revision IR |
|---|---|---|
| skill/scripts/src/api/bulk-lookup.ts:183 | ir_175 | ir_230 |
| skill/scripts/src/api/indexing.ts:62 | ir_346 | ir_403 |
| skill/scripts/src/api/indexing.ts:119 | ir_366 | ir_424 |
| skill/scripts/src/api/indexing.ts:152 | ir_387 | ir_446 |
| skill/scripts/src/api/metadata.ts:42 | ir_246 | ir_301 |
| skill/scripts/src/api/metadata.ts:64 | ir_260 | ir_315 |
| skill/scripts/src/api/metadata.ts:86 | ir_274 | ir_329 |
| skill/scripts/src/api/realtime.ts:28 | ir_190 | ir_245 |
| skill/scripts/src/api/realtime.ts:48 | ir_204 | ir_259 |
| skill/scripts/src/api/realtime.ts:68 | ir_218 | ir_273 |
| skill/scripts/src/api/realtime.ts:88 | ir_232 | ir_287 |
| skill/scripts/src/api/reports.ts:100 | ir_110 | ir_146 |
| skill/scripts/src/api/searchConsole.ts:102 | ir_312 | ir_368 |
| skill/scripts/src/api/bulk-lookup.ts:188 | ir_180 | ir_235 |
| skill/scripts/src/api/indexing.ts:76 | ir_357 | ir_414 |
| skill/scripts/src/api/indexing.ts:101 | ir_422 | ir_481 |
| skill/scripts/src/api/indexing.ts:133 | ir_377 | ir_435 |
| skill/scripts/src/api/indexing.ts:189 | ir_407 | ir_466 |
| skill/scripts/src/api/metadata.ts:51 | ir_250 | ir_305 |
| skill/scripts/src/api/metadata.ts:73 | ir_264 | ir_319 |
| skill/scripts/src/api/metadata.ts:91 | ir_278 | ir_333 |
| skill/scripts/src/api/realtime.ts:35 | ir_194 | ir_249 |
| skill/scripts/src/api/realtime.ts:55 | ir_208 | ir_263 |
| skill/scripts/src/api/realtime.ts:75 | ir_222 | ir_277 |
| skill/scripts/src/api/realtime.ts:95 | ir_236 | ir_291 |
| skill/scripts/src/api/reports.ts:105 | ir_115 | ir_151 |
| skill/scripts/src/api/searchConsole.ts:118 | ir_317 | ir_373 |
| skill/scripts/src/index.ts:73 | ir_437 | ir_497 |
| skill/scripts/src/index.ts:104 | ir_450 | ir_511 |
| skill/scripts/src/index.ts:135 | ir_463 | ir_525 |
| skill/scripts/src/index.ts:162 | ir_476 | ir_539 |
| skill/scripts/src/index.ts:200 | ir_489 | ir_552 |
| skill/scripts/src/index.ts:222 | ir_499 | ir_563 |
| skill/scripts/src/index.ts:252 | ir_514 | ir_579 |
| skill/scripts/src/index.ts:272 | ir_525 | ir_591 |
| skill/scripts/src/index.ts:292 | ir_536 | ir_603 |
| skill/scripts/src/index.ts:316 | ir_555 | ir_626 |
| skill/scripts/src/index.ts:343 | ir_574 | ir_649 |

This is a source/representation and artifact-closure audit, not a fresh execution or propagation/DOE analysis.
No compiler, validator, model, Skill, tests, backend or replay was invoked by this helper. The sole replay result is read from the controller's saved receipt.
Initial and revised artifacts remain preserved; no failed result is rewritten or promoted to accepted semantic evidence.
