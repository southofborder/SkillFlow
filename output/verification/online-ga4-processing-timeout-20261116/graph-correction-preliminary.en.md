# Initial CFG correction: passive preliminary diagnosis

This report concerns only the active `document-guided-ga4-processing-shared-high-20261116-225414` run. It reads saved responses, prompts, validation receipts and frozen source/code. No candidate was modified, compiled, validated or replayed for this audit. The frozen implementation remains unchanged.

## The local failures triggered complete regeneration

The initial graph response contains 237 blocks, 519 instructions and 217 edges. The saved validator reports two `RESULT_READ_BEFORE_DEFINITION` errors at `/blocks/218` and `/blocks/227`:

- `list_filter_head` reads `list_paths_current` as its merge's second input and produces that same result in the same instruction.
- `latest_filter_head` analogously reads and produces `latest_filtered_current` in the same merge.

The third saved diagnostic is root-scoped `CFG_STRUCTURE_INVALID`, containing ten missing-endpoint observations. Raw JSON enumeration shows every edge endpoint is declared in the original candidate and all block references are unique. Those ten observations point exactly to the same two rejected blocks.

The compiler constructs each `BasicBlock` independently. A block that fails its intra-block ordering check is absent from `canonical_blocks`; its originally declared reference remains in the reference table used to construct edges. `ControlFlowGraph` consequently sees edges to missing canonical blocks and emits the root diagnostic. This is a downstream consequence of rejected local construction, not evidence that the model omitted ten independent edge endpoints. See `src/skillflow/graph/extraction/compiler.py`, BasicBlock construction and final CFG construction.

`FragmentCorrectionStrategy` initially identifies the two block record slots, but a diagnostic at the empty root path belongs to no existing record. The strategy therefore clears its local selection and falls back to the existing complete-response correction. The actual a002 prompt explicitly requests one complete replacement response and does not contain the mechanical existing-record replacement instructions. This is observed routing, not a prediction.

| Measurement | Graph a001 | Graph a002 |
| --- | ---: | ---: |
| Prompt characters | 212,612 | 376,241 |
| Prompt UTF-8 bytes | 213,007 | 376,736 |
| Saved complete response characters | 164,162 | Not yet published at 15:16:58 UTC |
| Compact parsed response characters | 161,209 | Not yet available |

The correction prompt grows by 163,629 characters. The initial native process receipt records 985.053306 seconds elapsed and a successful exit. That is process elapsed time, not isolated model generation time. Public network/cost interpretation belongs to the separate transport audit; this report does not infer a reconnect or token count from these character measurements.

## Two diagnostic roots do not prove a two-record repair is sufficient

The two implicated raw block records total 1,250 compact JSON characters. This is only their serialized size; it is neither a sufficient correction scope nor a promised output, token or time saving.

The nearby raw producer/edge inventory matters:

| Loop | Init predecessor | Reject predecessor | Keep predecessor | Head output |
| --- | --- | --- | --- | --- |
| Filename filter/map | `list_paths_initial` | `list_filter_body` produces only `list_filename` | `list_paths_updated` | `list_paths_current` |
| Latest-operation filter | `latest_filtered_initial` | `latest_filter_body` produces only `latest_candidate` | `latest_filtered_updated` | `latest_filtered_current` |

Both reject edges return directly to their loop head. Neither reject predecessor declares a distinct accumulator carry version. Each current-accumulator name has exactly the offending head as its only producer. There is therefore no already-authored correct carry input that this audit can simply substitute in a head-only repair.

The source requires rejected members to leave previously accepted members intact: `storage.ts:131-133` filters directory names and maps accepted names to paths; `storage.ts:161-164` conditionally filters paths by the operation substring. Deleting the self input or replacing it with the initial array or a possibly unavailable updated value would not, by itself, establish that preservation relationship. No such manual fix was attempted.

## General follow-up proposal, after this frozen run

1. Preserve the complete strict diagnostics while adding typed dependency attribution. The compiler can record which declared block failed construction and which canonical endpoint observations arise only from that rejection. Carry the original candidate identity, exact block/edge coordinates and direct cause relationships. Do not infer this by parsing human-readable messages or relabel every root failure as local.
2. Use those proved relationships to choose the smallest sufficient existing-record correction scope. Here it must consider the actual head/body/predecessor producer closure, not only the two error roots. Keep the complete prior candidate or a complete exact reference context visible as read-only material: a correction request that exposes only two heads would omit the predecessor output names needed to reason about them.
3. Re-run the unchanged full schema/compiler/integrity checks after any mechanically merged correction. A downstream diagnostic being attributed to a local cause does not make it accepted or ignored. Genuine missing endpoints, duplicate references, unexplained global errors, required new blocks or topology changes must keep the complete-response fallback within the same existing correction budget. Do not synthesize placeholder valid blocks, invent carry producers or delete real branches merely to pass validation.
4. Improve general source-action granularity guidance separately. These particular loops expand pure `.filter`/`.map` operations around a distinct `readdirSync` acquisition. Existing opaque local computation can represent the complete pure transformation without constructing unnecessary accumulator-management CFG nodes. Retain the real acquisition, output version, filtering/order/limit semantics and any genuine per-member effects; do not make all loops opaque or collapse observable interactions. This is a future source-faithfulness and size proposal, not a change to the running experiment.

The observed correction response and later processing result are still needed to assess the actual cost and whether regeneration changed unaffected graph records. No additional model request, retry or experiment is proposed by this preliminary report.

Evidence: `graph-correction-preliminary.json` includes exact input/output sizes and the saved diagnostics; `graph-correction-dependency-context.json` records the relevant original blocks, producer coordinates and edges. Both are passive audit artifacts in this directory.
