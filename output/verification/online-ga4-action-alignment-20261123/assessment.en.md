# GA4 action alignment and fresh graph verification

The run started from all 16 source files, with newly generated Task, flow and CFG stages. Task and flow completed. Graph construction failed after correction and shared revision. The run ended before processing, field demand, sensitivity or DOE. No online field deletion or coverage percentage can be established. [Run summary](run-summary.json)

## Implementation and offline verification

A single IR can carry multiple ordered source actions on the same control path. Processing binds each action to its operations, including the real boundaries of a call. An unknown value can be projected or passed forward. A placeholder for uncertain behavior carries possible inputs and bounded resource effects. Known sibling actions retain their observed versions, and demand uncertainty follows the affected fields. The offline Search Console example checks query response projection, default saving, the overview's `topQueries` member and final save. The three-input regression retains the actual observation of `c.c` and identifies it as deletable when only the other two inputs are required. The ingress regression exercises retention of 73 gaps across revision. [Design and acceptance](../../../docs/doe/cfg-processing-actions.zh.md)

All tests under `tests/` were run on one frozen implementation in four disjoint groups. There were 6,291 passes, four skips and zero failures. Two skips require Windows symlink privileges and two require optional historical materials. Lean used a local build from the repository source. GitHub and local trees matched before dispatch. [Offline receipt](offline-acceptance.json) · [Verified commit](https://github.com/southofborder/SkillFlow/commit/f48b39c951ed2069830d0b24c839c9f478da160d)

## Why the graph failed

The initial candidate contained 117 blocks with 223 ordinary operations and 117 exits. Of these operations, 33 explicitly listed multiple source actions. The reply tagged 50 blocks as context acquisitions. Only one contained the required single operation before its exit. Twenty-five contained no ordinary operation, and 24 contained several. The first request listed the three allowed values of `source_kind` without the compiler's acquisition cardinality rule. Validation reported all 49 block-shape errors and one ordinary use of a raw context key. [Submitted blocks and diagnostics](cfg-repair-evidence.json)

| Step | Available edits | Result |
|---|---|---|
| Initial generation | Entire candidate | 50 structural errors |
| Correction | 49 operation arrays and one nested input. No block-kind or region edit | 25 updates submitted. Two overlapping edits were rejected. The merge changed 23 blocks and retained all 50 errors |
| Shared revision | The same 50 fields. Two source-review CFG findings had no writable location | 24 updates submitted. The raw key use was fixed. All 49 block-shape errors remained |

The empty `select_site` block branches on an existing `selected_entry`. Its cited source line declares `siteOverview`. Inserting a new acquisition would invent a read. The `document_workflow` candidate combined five operations for the documented analysis, storage and summarization sequence. Revision introduced an actual input acquisition and connected subsequent uses to its outputs, but all six operations were still in one acquisition block. Its ordinary correction had targeted both an operation array and one of its inputs. The merger rejected both edits. When no CFG compiled, the validation entry point emitted the remaining graph diagnostics and omitted the overlap diagnostic. [Repair paths and source examples](cfg-repair-evidence.json) · [Validation entry point](../../../src/skillflow/document_guided/graph_steps.py)

Initial source review identified two CFG issues. One concerned loop-carried arrays missing from saved results. The other concerned the missing conditional delivery on direct module execution. Both were recorded as unaddressable against the failed candidate. The revised Task passed local validation. Both reviews inspected diagnostic materials with CFG and annotation explicitly unavailable. Zero findings in the last diagnostic review did not certify any input contract. [Stage audit](result-audit.json)

## Reach and cost

The original and revised processing, sensitivity and Task correspondence stages were skipped. Propagation and DOE were never scheduled. The source contains 13 SDK call sites. No selected graph was available to check recipients, responses, field projections or default saves. Sensitive sources, feasible branch counts, field assessments, candidate counts and DOE report bytes are unavailable. The previous run used an inherited 489-IR graph and recorded 133 processed, 54 reached and unmodeled, and 302 blocked. Its 285 required, 997 unresolved and zero deletable ranges have no measured counterparts in this fresh run. [Prior assessment](../online-ga4-entry-review-20261122/assessment.en.md)

Two workers used the existing budgets. The seven-stage normal policy issued four normal requests. One CFG correction, three shared revision stage requests and one revised Task correction brought total native starts to nine. All exited. Public tokens totaled 1,019,177, including 888,579 input and 130,598 output. The transport recorded zero outer retries or pre-submit rejections. Each of the three graph requests returned an answer. They took 966.6, 692.6 and 475.3 seconds. Analysis took 2,459.87 seconds. The controller's sole replay matched in 4.37 seconds with zero new native starts. [Transport and replay](run-summary.json)

## Next change

Publish the compiler's block-kind contract in the normal graph request. Assemble an ordinary control block when the source actions and operands uniquely show a pure exit on existing values. Where a real acquisition and subsequent behavior are mixed, offer one bounded edit that can split the block, preserve producer identities and reconnect its edges. Group dependent operand edits inside that update. Return patch diagnostics with residual compiler errors. Bind source-review findings to the failed candidate by source span and action even when no certified CFG exists. The new offline acceptance fixture should cover the 25 empty blocks, 24 mixed blocks, overlapping update and both missing review targets before spending tokens on another online comparison.
