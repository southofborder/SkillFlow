# Processing-restart run: source-review failure

This audit concerns `document-guided-ga4-processing-restart-high-20261117-172228`. Its saved main result is partial. Root owns controller closure and the sole replay; this audit performs neither. All conclusions below come from saved artifacts and frozen code. The [JSON record](review-failure-final.json) contains exact hashes, scope IDs, missing positions and source references.

Review correction `a002` was rejected **before a native process started**: its 1,206,074-character core plus the 212-character adapter envelope totaled **1,206,286**, exceeding the 1,048,576 limit by **157,710**. This is an input-size failure, not a network or generation timeout. Review `a001` completed transport delivery in 1,522.221 seconds; this elapsed time is not pure generation time.

Both prompts retain the complete 16-file source and identical source suffixes. Independent display expansion confirms identical base material, the full prior answer in correction, and every expected obligation/scope ID. The current inventory has **684 contracts: 202 compute and 482 tool, covering 2,540 scopes**. No source or contract omission explains the failed request.

The first answer contains 11 findings and only **453 unique known checks**: 418 authored as accepted, 33 rejected and two unresolved. It omits **231 expected checks**—184 tool and 47 compute—with no duplicate or unknown obligation IDs. The omissions are distributed, not a cut-off suffix: they occupy 134 disjoint ranges from expected index 1 through 680, while the answer reaches the final index 683 and closes every array. Missing counts by consecutive 100-entry inventory regions are 19, 34, 42, 42, 43, 24 and 27 in the final 84-entry region. The public stream ends with `item.completed` and `turn.completed`; no finish reason or truncation/budget notice is exposed. The answer provides no explicit explanation for the omissions. **An output-budget cutoff is therefore not established.**

Saved validation records 253 raw diagnostics, grouped into 245: 11 malformed scope records, 11 finding/acceptance conflicts grouped into three diagnostics, and 231 missing-coverage diagnostics. A representative malformed group combines `rule`, `required` and `remainder` subjects while assigning the same `affected_scope_ids` to all three. The wide rule may affect input scopes; the actual-input subjects cannot inherit that wide-scope relation. Conflicts involve findings 2, 6 and 8 and respectively one, four and six checks. These are candidate claims, not accepted semantic findings.

Whole-review correction is selected both by conflicts and by missing records at `/input_contract_checks`. Existing-record replacement cannot add absent checks. Lossless sharing and column tables already ran; the correction added 213,800 core characters. The request-failure branch then leaves `review=null`; unlike structural-correction exhaustion, it does not run strict local isolation on the prior answer. Shared repair consequently records `eligible=false` because no completed or locally retained review is available. Accepted Task/CFG/annotation make missing-CFG recovery irrelevant. No accepted-check count can be inferred from the 418 authored acceptance labels.

The unchanged inherited source, Task and CFG produced a larger fresh annotation review workload:

| Saved measure | Parent 135205 | Restart 172228 |
|---|---:|---:|
| Contracts | 451 | 684 |
| Scopes | 1,738 | 2,540 |
| Base prompt core characters | 883,026 | 992,274 |
| Correction core characters | 1,055,579 | 1,206,074 |
| Final answer characters | 225,754 | 225,203 |
| Missing checks | 0 | 231 |

The largest expanded logical-section increase is inventory, from 340,314 to 514,581 characters; annotation grows from 684,852 to 720,521. Sharing across sections means these differences cannot be added as exact packed contributions. The answer remains almost the same size while required coverage grows.

Finding 9 is relevant to the task-output-input boundary: six aggregate requirements have top-level demands emphasizing shape and original date ranges. Saved source requires measurements and their grouping (`SKILL.md:70–77`, `index.ts:55–225`). The saved demands corroborate this narrow concern, but this audit does not validate the finding or determine backend preservation. A storage obligation cannot replace an independently established requirement for report content at return.

General follow-ups remain proposals only: support edits to the connected conflict records **and insertions for exactly the missing known obligation slots**, with complete merged validation; retain complete source/contracts while budgeting the final delivered prompt; give scope errors precise group/subject/target context; and consider strict isolation of a prior immutable answer after a later delivery failure, preserving all missing-coverage/conflict barriers and the failure itself. A conflict-only existing-record fix cannot repair 231 absent checks. No code, budget, prompt, runner, validator, model, Skill or replay was changed or executed here.
