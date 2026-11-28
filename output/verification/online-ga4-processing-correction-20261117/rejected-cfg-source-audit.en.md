# Fresh GA4: rejected CFG and source relationships

Run: `document-guided-ga4-processing-correction-high-20261117-110830`.
This report uses only its saved raw responses, prompts, validation receipts, merged candidate, terminal result and complete frozen source. It does not execute the Skill, any validator/compiler, propagation, DOE, model call or replay. The companion `rejected-cfg-source-audit.json` binds the inspected artifacts by SHA-256 and retains the precise candidate records and saved diagnostics. `audit_rejected_cfg.py` performs only JSON/text/hash inventory.

The run ended without an accepted CFG or annotation. Graph exhausted its one structural correction; processing, task-correspondence and sensitivity were skipped. The terminal root result records review as partial, shared repair unused and no executable annotation. This is an initial graph/review failure, not a new processing or revision-processing timeout. Source-review routing and delivery evidence are audited separately by the protocol agent; replay and cost are owned by the root report.

## What the graph correction actually did

The first response authored 258 blocks, 619 instructions and 246 edges. Its saved validation reported only `dispatch_inputs` at `/blocks/183/instructions/3/inputs`: a guarded/backedge dispatch had no explicit condition dependency. The first response was 176,427 characters; its saved stage prompt was 213,256 characters.

The one correction used `skillflow-cfg-correction-scope-v1` with `scope_policy: direct_records`, one allowed record `/blocks/183`, no dependency expansion and no readonly boundary records. Its context contained the exact complete initial candidate. The model returned one complete block replacement, 2,039 characters. Its saved stage prompt was 389,196 characters, including the original prompt and complete correction context. These are stage-text character counts, not native delivery totals, generation times or an estimated latency saving.

The replacement added `batch_next` as the dispatch input, with a constraint that the backedge follows normal completion and append. The corresponding source is `scripts/src/api/indexing.ts:95–98`: sequentially await the URL notification, then append before the next iteration. The first three block instructions were unchanged. Exact saved-object comparison shows that only block 183 changed; all other blocks, all 246 edges, entry, top-level constraints and diagnostic notes were unchanged. The merged candidate remained 258 blocks and 619 authored instructions. Passing this early dispatch check does not itself establish source correctness.

The final saved validation reported two `RESULT_READ_BEFORE_DEFINITION` errors and one root `CFG_STRUCTURE_INVALID` error. The latter contains ten missing-endpoint observations caused by the two rejected blocks, five for each. Its complete typed cascade context names the rejected owners and binds the current merged candidate. Therefore the new causal evidence mechanism emitted the intended information, but **the new dependency-closure correction mode was not exercised**: those diagnostics became visible only after the sole correction had already been consumed.

## Why the remaining loop defects were hidden

Both bad heads and their bodies were already present, unchanged, in the first candidate:

| Rejected head | Incorrect merge | Actual source |
| --- | --- | --- |
| `/blocks/222`, `list_filter_head`, canonical `ir_501` | Reads `list_json_names` as its own input while defining that same result | `storage.ts:131–132`, directory entries filtered by `.endsWith('.json')` |
| `/blocks/234`, `latest_filter_head`, canonical `ir_526` | Reads `latest_filtered` as its own input while defining that same result | `storage.ts:161–164`, optional operation filter using `.includes('__' + sanitized)` |

For the first loop, the merge operands are the initial array, the head's own `list_json_names`, and the keep branch's `list_filter_added`. The false branch goes directly from `list_filter_member` to the head. The member body does not produce a distinct retained accumulator for that branch. The second loop has the same pattern with `latest_filtered`, `latest_filter_added` and `latest_filter_member`. A sound source-faithful repair must account for both keep and skip paths; replacing just the two head records is not demonstrated sufficient. The needed scope includes actual carry producers/consumers and branch relationships, with whole-candidate fallback when existing-record permissions cannot express the repair.

Static read-only inspection explains the sequence. `cfg_wire.py:80–117` performs early wire/schema checks and raises collected diagnostics before returning normalization. `online.py:237–243` calls `_full_graph` only after normalization succeeds. Consequently the initial `dispatch_inputs` error prevented compiler inspection that would expose the pre-existing merge self-reads. Fixing the dispatch revealed them; it did not introduce them. This is a diagnostic aggregation gap across validation gates, not evidence that the causal dependency scope failed to include already-visible loop errors.

## Source-site presence in the rejected candidate

The complete frozen inventory has 16 files, 155,170 bytes, source SHA `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. Source-site matching and direct inspection of candidate arguments establish the following limited facts:

| Source boundary | Authored candidate presence | Qualification |
| --- | --- | --- |
| 13 direct remote API call sites | 13 unique external boundary records | Each has an explicit client receiver, request value and response result. This does not establish complete request-field semantics or interface necessity. |
| 25 internal `saveResult` callers | 25 unique `save_result` instructions | Payload/category/operation/optional extra are present; no filepath output is introduced where the caller discards it. These are opaque call summaries, not verified caller-to-writer transfers. |
| 7 filesystem operations | 7 corresponding records | Three existence checks, directory creation, write, read and directory listing are present. Downstream filter loops are invalid. |

These are **unaccepted authored-record counts**, not accepted CFG coverage, source-reviewed correctness, propagation reach, or DOE coverage. There is no accepted instruction count to use as a propagation denominator. No processing contract, final input assessment or deletion conclusion was produced.

The independent `saveResult` body does represent the source's settings read, category path, conditional recursive mkdir, filename timestamp, operation/extra sanitization, a separate fresh ISO metadata time, `{metadata,data}` serialization, ordinary replacing write, and public filepath return (`storage.ts:58–95`). That independent body does not prove that every opaque caller summary preserves all those dependencies; processing and source review would still have to establish that relationship for each demanded call.

The documented summary is represented as its own obligation: read saved JSON, compose Markdown with tables/trends/recommendations, and write below `results/summaries/`. The candidate explicitly leaves the selected file/invocation relationship and exact filename unresolved, consistent with the missing source mapping. It does not invent an edge from an ignored internal save path or a latest-result example to that summary read.

For `reports.ts:78–98`, the candidate explicitly notes that `filters` and `orderBy` are destructured but absent from the request and saved payload, and still takes the whole options object as the operation input. The real source behavior must remain visible; documentation promising filtering/sorting must be reported as a semantic mismatch. There is no processing or observation record here from which to infer field-level necessity or deletability, and this audit does not do so.

## Result-based follow-up proposal

1. Aggregate independently checkable compiler defects with early application diagnostics on schema-valid, safely normalizable candidates. Preserve rejection, exact raw/canonical ownership and all existing checks; produce no accepted graph from a partial compile. Then the existing single correction can receive the current dispatch and loop defects together. Retain whole-response fallback for schema/global/topology failures whose safe owner scope cannot be proved. Offline regression should reproduce this exact mixed-gate shape and prove both diagnostics arrive before the one correction is chosen.
2. Test the resulting correction scope on real skip/keep loops: heads, carry-producing bodies and relevant consumers/predecessors must be included, with immutable boundary context. Verify exact identity/permissions and full post-merge validation. Do not claim that the two head records or their byte size alone define a sufficient repair or a time saving.
3. Correct source-review target guidance and fixtures for the no-accepted-graph failure path, as detailed in the separate protocol audit. The current source review twice used invalid target `stage:graph`; the existing target allowlist should remain strict. No reviewed processing contracts exist in this run.

All three are proposals from the closed run, not frozen-code modifications. The processing shared-output grammar and supplemental pair-tree diagnostics were not exercised online because processing never started. This run provides no measured processing output compression or processing latency result. It also does not establish that networking or native timeouts have improved.
