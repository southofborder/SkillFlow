# Final GA4 source and coverage assessment

Run: `document-guided-ga4-processing-shared-high-20261116-225414`. Frozen implementation: `8ed018204232f0fc5ed2a26ae9c86d0d3055b900aee3583b5c8b17723d9316ed`.

The run **failed in the structural correction of initial processing**. It did not reach revision-processing, source review, propagation or DOE. There is **no selected annotation or selected CFG bundle**. The completed initial graph contains **521 IR in 237 blocks with 217 edges**; this is generated representation, not processed coverage.

## Terminal evidence

- Initial processing a001 was rejected at the JSON boundary: `duplicate JSON member: shared_values`. No processing semantic validation or accepted coverage was established from that answer. Its raw records remain preserved; duplicate keys were not normalized away.
- Processing correction a002 reached the 2,700-second native total deadline (`2700.039036` seconds), with confirmed process exit and no complete response. The controller's analysis elapsed time was `6287.714050` seconds.
- Actual starts: **6 = 4 normal stage requests + 2 structural corrections**. Seven normal requests and two workers remained configured; only Task, flow, graph and processing were reached. Shared semantic repair was never used.
- The sole controller replay **matched in 7.030900 seconds with 0 new native starts**. This reproduces the recorded failed frontier; it does not establish semantic or DOE correctness.
- All six native attempt exits are confirmed by the saved exit receipts. The controller closed at `2026-11-16T16:39:48.628006+00:00` and records unchanged frozen implementation/helpers/executables.
- The fatal-frontier receipt binds 49 existing artifact references; this passive audit found their hashes matching. All 16 frozen source files still match the initial inventory and protocol.

## Available material and unavailable results

| Item | Evidence |
|---|---|
| Task | Source-only extraction completed: 54 requirements, 13 issues. No whole-chain source review followed. |
| Flow | Completed working document. |
| Initial graph | a002 accepted after one graph correction; 237 blocks / 521 IR / 217 edges. |
| Processing | a001 malformed; a002 incomplete; accepted_call is null and no processing value/result artifact exists. |
| Selected bundle, annotation, revised material | Absent. |
| Task correspondence, sensitivity, source review | Not run. |
| Bound contract-review receipt | Absent. |
| Propagation, demand preparation, input assessments | Not run. Counts are unavailable/null. |
| DOE comparisons, reductions or deletable ranges | Not run. Counts are unavailable/null. |

Unavailable is **not zero coverage, zero deletable inputs, or no_excess_established**. No final required/deletable/unresolved range classifications were computed. No actual Skill execution occurred.

## What the generated graph does and does not establish

The independent source inventory has 13 remote call sites, 25 saveResult caller sites and 11 loop/map/filter/sort sites. All have source-matched generated representations in the accepted initial graph, and all 294 copied source spans match exactly. This establishes source-location representation only.

Six remote IR carry explicit receiver results and request/body operands. Four realtime and three metadata operations instead describe getClient/getPropertyId inside composite effect text. Whether processing establishes the internal authentication, cached receiver and property routing dependencies is unknown because there is no accepted processing result.

All 25 saveResult call summaries and the independent filesystem writer ir_453 are present. Their presence does not prove caller-to-filesystem payload/receiver transfer. That eventual coverage count remains null.

The two initial graph filter-head errors were corrected by separate retained-accumulator values (ir_482 and ir_501), keeping the rejection and acceptance branches. This is a source-consistent generated state-flow correction; no backend loop completion or member-pairing result followed.

## Concrete source risks still awaiting analysis

1. **Actual unused reads:** `reports.ts:78-86` destructures filters/orderBy; the outgoing request omits both. ir_089 lists them only as unused_destructured_fields metadata, without distinct produced values. Actual read/observation retention and the documented filtering/sorting mismatch remain unverified. This is not a deletion verdict.
2. **Composite remote inputs:** the seven realtime/metadata boundaries need explicit processing evidence for receiver, credentials and routing. Physical source coverage cannot establish that evidence.
3. **Storage transfer and metadata:** each caller's data/category/operation/extraInfo must be connected to `storage.ts:79-92`, including conditional metadata, path identity and directory creation. No such propagation result exists.
4. **Summary provenance:** ir_517/519/520 represent the required saved-JSON read and Markdown summary/write. The graph explicitly leaves invocation-to-file provenance and concrete writer/filename unspecified. No mapping/review resolved those specific relationships.
5. **Loops and conditions:** filtering, sorting, optional limits, sequential URL/result pairing and caught-error alternatives remain requirements for subsequent processing and review. Their generated presence is not evidence of successful preservation checks.

The new result supports prioritizing strict shared-JSON output construction and completion within the existing correction budget. It does not support weakening duplicate-key validation or claiming the intended field-necessity improvement. The original-bundle retention fallback was inapplicable because this run never formed an initial bundle. Further proposals should keep these delivery failures separate from the untested source-semantic risks above.

This audit read saved public artifacts only. It did not invoke a validator, renderer, model, Skill, backend or replay. The sole authorized run and its controller replay are closed.
