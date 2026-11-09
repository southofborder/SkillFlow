# First-response screening: not passed

**Implementation and offline verification are complete. The online screening gate failed.** The revised prompts produced 3/4 valid first responses versus 2/4 for the frozen current-production baseline. Revised annotation B also misses required receiver content demands, and both negative-review responses miss the broad whole-value demand. These semantic failures remain even if invalid citations were corrected.

The experiment stopped after exactly **8 logical calls / 8 HTTP attempts**. There were **0 transport retries, 0 JSON normalizations, 0 structural corrections, 0 Task calls, 0 semantic repairs and 0 quality reruns**. No formal 001, 010 or 013 run was started. Production structural correction remains unlimited; this screen uses its separately authorized first-response-only policy.

[Assistant assessment JSON](assessment.assistant.json) · [Frozen online metrics](metrics.json) · [Zero-API replay](replay.json) · [Preregistered checks](audit/preregistration.json)

## Online results

Requested model: `deepseek-v4-flash`. Actual returned model: `deepseek-flash`. Existing official configuration, `max`, JSON Output, SSE, timeout and retry policy were retained. The baseline is the production prompt frozen immediately before this targeted change, not the older historical prompt layout. All four fixtures are independently authored English assessment materials, distinct from the teaching examples. Expected checks were not sent to the model.

| Material | Baseline first response | Revised first response | Assistant semantic assessment |
|---|---|---|---|
| Annotation A: receipt | Valid | Valid | Both preserve all four preregistered relationships. |
| Annotation B: occupancy | Invalid null-event evidence | Valid | Revised preserves filtering, Boolean computation, optional value/control and append payload; its actual delivery lacks parameter-value demands. |
| Review A: legitimate complete value | Valid, no findings | Valid, no findings | Both correctly accept explicit whole-card delivery and caption save; no added material false finding. |
| Review B: broad demand + missing save payload | Invalid CFG evidence (2 entries) | Invalid CFG evidence (1 entry) | Both miss the broad read-output value demand. Both recognize the missing save payload in unaccepted text only. |

## What still failed

1. **Delivery demand remains upstream.** Revised annotation B constructs the correct request, but its `deliver` demands contain only `self/action` and `input[0]/shape`. The values of `available_count`, `has_room`, and conditional original `zone_code` are demanded at upstream build inputs or field selection. Those seeds do not establish these content requirements at the receiver. The compiled delivery goal remains a shape demand. The append's actual value-input demand is present, so the failure is not indiscriminately assigned to every sink.
2. **Acquisition scope is still confused with required scope.** Both review B responses accept the whole read-output value demand because the implementation reads the entry or needs it for field selection. The fixed Task only requires original `tracking_code` at the sorter. Preserving source scope or possible model observation does not create a whole-value task requirement. Both reviewers miss this preregistered defect.
3. **Review evidence uses the wrong address space.** `target_ids` correctly identifies the annotation write parent, but `evidences[].target` points to CFG IR `ir_entry_save` with an `events/.../atomic_ops` path. The actual CFG instruction has no `events` field. Both reviews are rejected. These are parseable JSON responses, not syntax failures or unknown finding IDs. The program did not delete the citation or reinterpret it as an annotation reference.

Observed improvements are retained without upgrading the outcome: revised annotation B has legal null-effect evidence, uses `filter_items + shape` rather than collection-root truth, creates a real Boolean result, preserves explicit optional selection with `when`, keeps append action and payload demands, and does not invent a task gap solely because encoding is unspecified. The baseline's invalid text had endpoint value demands, but is not promoted to a valid alternative.

[Annotation assessment and exact pointers](audit/assessment-annotation.assistant.md) · [Review assessment and exact pointers](audit/assessment-review.assistant.md) · [Mechanical evidence audit](audit/assessment-structure.assistant.md)

## Actual cost and elapsed time

Reasoning and cache values are subdivisions of the provider totals, not additional tokens. All eight attempts include usage. Both failed and valid responses remain in the totals. Token use is not a currency invoice.

| Metric | Baseline (4 calls) | Revised (4 calls) |
|---|---:|---:|
| Input tokens | 55,079 | 61,935 |
| Output tokens (including reasoning) | 226,885 | 223,742 |
| Total tokens | 281,964 | 285,677 |
| Reasoning tokens (already included) | 215,242 | 215,772 |
| Recorded call seconds | 1234.726 | 1185.735 |

The revised arm used **3,713 more tokens (+1.32%)**. There is no measured first-response token saving. Total online wall time was **2440.324 seconds (40 minutes 40.3 seconds)**, excluding preparation and replay. The small time difference is descriptive, not evidence of a reliable speedup. No complete correction chain was run, so its cost and correction-count reduction were not measured.

## Eight recorded requests

The following order is the actual interleaved schedule. Each link points to a real saved `a001`; invalid responses have not been hidden or replaced.

| Order | Case / arm | Status | Input | Output | Total | Seconds | Request and validation |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | annotation_a_receipt / baseline | valid | 12,764 | 66,118 | 78,882 | 360.053 | [prompt](cases/annotation_a_receipt/baseline/calls/annotation/a001/prompt.txt), [raw response](cases/annotation_a_receipt/baseline/calls/annotation/a001/response.json), [validation](cases/annotation_a_receipt/baseline/calls/annotation/a001/validation.json), [call](cases/annotation_a_receipt/baseline/calls/annotation/a001/call.json) |
| 2 | annotation_a_receipt / revised | valid | 15,353 | 63,787 | 79,140 | 339.570 | [prompt](cases/annotation_a_receipt/revised/calls/annotation/a001/prompt.txt), [raw response](cases/annotation_a_receipt/revised/calls/annotation/a001/response.json), [validation](cases/annotation_a_receipt/revised/calls/annotation/a001/validation.json), [call](cases/annotation_a_receipt/revised/calls/annotation/a001/call.json) |
| 3 | review_a_display / revised | valid | 15,278 | 45,816 | 61,094 | 252.579 | [prompt](cases/review_a_display/revised/calls/review/a001/prompt.txt), [raw response](cases/review_a_display/revised/calls/review/a001/response.json), [validation](cases/review_a_display/revised/calls/review/a001/validation.json), [call](cases/review_a_display/revised/calls/review/a001/call.json) |
| 4 | review_a_display / baseline | valid | 14,439 | 41,047 | 55,486 | 239.824 | [prompt](cases/review_a_display/baseline/calls/review/a001/prompt.txt), [raw response](cases/review_a_display/baseline/calls/review/a001/response.json), [validation](cases/review_a_display/baseline/calls/review/a001/validation.json), [call](cases/review_a_display/baseline/calls/review/a001/call.json) |
| 5 | annotation_b_occupancy / baseline | structural_invalid | 12,984 | 69,231 | 82,215 | 349.021 | [prompt](cases/annotation_b_occupancy/baseline/calls/annotation/a001/prompt.txt), [raw response](cases/annotation_b_occupancy/baseline/calls/annotation/a001/response.json), [validation](cases/annotation_b_occupancy/baseline/calls/annotation/a001/validation.json), [call](cases/annotation_b_occupancy/baseline/calls/annotation/a001/call.json) |
| 6 | annotation_b_occupancy / revised | valid | 15,573 | 45,273 | 60,846 | 211.251 | [prompt](cases/annotation_b_occupancy/revised/calls/annotation/a001/prompt.txt), [raw response](cases/annotation_b_occupancy/revised/calls/annotation/a001/response.json), [validation](cases/annotation_b_occupancy/revised/calls/annotation/a001/validation.json), [call](cases/annotation_b_occupancy/revised/calls/annotation/a001/call.json) |
| 7 | review_b_dispatch / revised | structural_invalid | 15,731 | 68,866 | 84,597 | 382.334 | [prompt](cases/review_b_dispatch/revised/calls/review/a001/prompt.txt), [raw response](cases/review_b_dispatch/revised/calls/review/a001/response.json), [validation](cases/review_b_dispatch/revised/calls/review/a001/validation.json), [call](cases/review_b_dispatch/revised/calls/review/a001/call.json) |
| 8 | review_b_dispatch / baseline | structural_invalid | 14,892 | 50,489 | 65,381 | 285.827 | [prompt](cases/review_b_dispatch/baseline/calls/review/a001/prompt.txt), [raw response](cases/review_b_dispatch/baseline/calls/review/a001/response.json), [validation](cases/review_b_dispatch/baseline/calls/review/a001/validation.json), [call](cases/review_b_dispatch/baseline/calls/review/a001/call.json) |

## Final prompt and offline verification

The seven sections retain their original order. Required reasons and evidence are no longer recursively removed from shown examples. The complete sample has a real frozen synthetic Task context; final rendered examples are parsed, reference-checked and compiled without inserting hidden internal fields. Review lessons demonstrate review output rather than duplicate annotation snippets. Shared rules distinguish filter truth, expected-original relations, actual field selection, and optional control values.

Structural-correction protocol v5 preserves raw diagnostics plus a deterministic model-visible projection. The nested target example collapses 16 union-branch diagnostics to one actual target object while preserving all mappings. No missing paths, evidence moves or demands are generated by that projection. Independent errors are collected only when their prerequisites are valid.

- Broad related regression: **1,690 passed, 1 skipped** before the final three targeted fixes. The skip is a Windows symbolic-link creation privilege limitation. This was not every repository test.
- Final affected regression after those fixes: **285 passed** (125 rendered-prompt/semantic/language, 138 diagnostic/recovery, 22 screen checks). These overlap the broad suite; the totals are not added.
- Strict Task/annotation/review Schema hashes match the baseline. Runtime, compiler, propagation, Data and DOE analysis identities are unchanged.
- **522 historical files and 25 protected analysis files are unchanged.** The current production/tools identity still matches the frozen online implementation.
- Compileall and the CRLF-aware Git whitespace check passed. Input and request identities, accepted-response recovery and zero-API replay checks passed.
- Actual screen replay: **matched, 0 API calls**, including rejected responses. Replay did not overwrite call timing or usage.

[Change comparison](changes.md) · [Offline validation report](offline-verification.md) · [Detailed verification receipt](audit/offline-verification.json) · [Protected-file checks](audit/offline-protection.json) · [Prompt-size measurements](audit/prompt-sizes.json)

### Rendered prompt size

Character and UTF-8 byte counts below measure the actual sent text. Section counts are available in the linked JSON. Longer complete examples were permitted; length is not the primary success criterion and these counts are not estimated tokens.

| Case | Arm | Characters | UTF-8 bytes |
|---|---|---:|---:|
| annotation_a_receipt | baseline | 56,806 | 56,806 |
| annotation_a_receipt | revised | 66,988 | 66,988 |
| review_a_display | revised | 63,097 | 63,097 |
| review_a_display | baseline | 59,793 | 59,793 |
| annotation_b_occupancy | baseline | 57,808 | 57,808 |
| annotation_b_occupancy | revised | 67,990 | 67,990 |
| review_b_dispatch | revised | 64,466 | 64,466 |
| review_b_dispatch | baseline | 61,162 | 61,162 |

## Assessment status and stopping decision

The revised arm fails both the structural threshold (3/4 rather than 4/4) and the preregistered semantic threshold. The positive review control passed; the negative control did not. The outcome remains **not passed**. No extra requests or formal-case reruns follow this result.

The machine-generated `metrics.json` and `summary.json` were frozen before assistant assessment and intentionally retain their pending/not-assessed markers. This report and `assessment.assistant.json` record the later external assessment without rewriting those frozen records. The assessments are assistant-authored, not independent human expert gold labels. This screen does not establish general accuracy, semantic completeness, task minimality, executability, sensitivity completeness, absence of DOE, or overall correction-chain improvement.

The remaining work is evidenced here, not silently implemented after the evaluation: distinguish CFG evidence from annotation finding targets; keep acquisition defaults separate from task-demand scope; and teach receiver input-value demands through a complete construct-to-deliver example. Any new evaluation or formal-case run requires a separate decision.
