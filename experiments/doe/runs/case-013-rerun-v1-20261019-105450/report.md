# Case 013: fresh full-pipeline rerun

The new annotation and initial review completed successfully. All three logical requests were structurally valid on their first candidate; no structural correction or semantic repair was needed. One initial annotation connection timed out, then the existing transport policy completed that same logical request. The previous run remains unchanged.

The four terminal status writes now carry their own payload-value demands, and these demands reach the corresponding sink inputs in deterministic analysis. This is an improvement in this accepted candidate, not proof of general model reliability. The production implementation, frozen source/CFG and configuration were unchanged; the Task and annotation were freshly sampled.

## Results that matter

| Check | Previous selected 013 candidate | This rerun |
|---|---|---|
| Review execution | Final rereview failed with IncompleteRead after semantic repair | Initial review completed without findings; no repair/rereview needed |
| Terminal status saves | Four action-only seeds; missing actual content demands | Four action seeds and four receiver-input value seeds; confirmed in sink derivations |
| First and retry call parameters | Separate source_id and FAST_KEY value demands | Preserved at both actual call boundaries |
| Archive parameters | source_id only | Preserved; no key input added |
| Credential sensitivity | Repair added a second declaration for the same source range | One environment FAST_KEY declaration, with exact field selection retained |
| Exposure rows | 20 rows: 8 direct and 12 possible, with duplicate declaration paths | 10 rows: 4 direct and 6 possible; 16 sinks retained |
| Final DOE state | Partial; diagnostic pipeline | Partial; diagnostic pipeline |

See the [independent assistant audit](cases/013/assistant-review.md) for source-to-demand-to-sink evidence and remaining limitations. No accepted model artifact was edited by the assistant.

## Analysis limits

The review covers 11 source spans, 16 requirements, 30 demand goals and all 26 IRs. Coverage and review acceptance do not prove semantic completeness.

Six retained restrictions produce six expression-gap and six unbound-requirement diagnostics; two source ambiguities concern transient-error classification and the final status description. All 14 diagnostics remain global blockers under the current contract. They are not 14 independently demonstrated implementation defects. Splitting the archive-key and diagnostic-key prohibitions into separate requirements also changes the diagnostic count relative to the previous Task.

All ten sensitive-range comparisons are `no_excess_established`. With partial demand analysis and global blockers, this means no supported excess conclusion was established; it does not mean every field is necessary, every prohibition was verified, or no DOE exists. Possible credential influence is not credential plaintext.

## Actual calls and cost

- Logical requests: **3** (Task, joint annotation, initial review).
- Structural corrections: **0**; JSON normalizations: **0**.
- Semantic repairs: **0**; Task revisions: **0**.
- HTTP attempts: **4**, including **1** transport retry.
- Requested model: `deepseek-v4-flash`, reasoning effort `max`; returned model: `deepseek-flash`.
- Online workflow: **767.7 s**; summed request wall time: **612.1 s**. These nested clocks are not added together.
- API-reported token subtotal: **217,414** (85,767 input + 131,647 output). One failed connection reported no usage, so the complete total is unknown.

| Request | HTTP attempts | Input tokens | Output tokens | Reasoning tokens (included in output) | Reported total | Request time |
|---|---:|---:|---:|---:|---:|---:|
| [task_extraction](cases/013/task/calls/task/a001/prompt.txt) | 1 | 1,699 | 12,655 | 10,716 | 14,354 | 54.9 s |
| [annotation](cases/013/annotation/calls/annotation/a001/prompt.txt) | 2 | 21,565 | 52,700 | 42,610 | 74,265 | 266.7 s |
| [initial_review](cases/013/refinement/initial-review/calls/review/a001/prompt.txt) | 1 | 62,503 | 66,292 | 63,024 | 128,795 | 290.6 s |

The successful response usage is measured, not estimated from characters. Cache and reasoning details are subdivisions, not additional tokens. The annotation connection failure is not a structural correction. This single rerun uses a different semantic path from the previous five-request run; it does not establish a general cost reduction.

## Replay and preservation

Zero-API replay returned the same stage selection and deterministic results. Network calls were blocked during replay; attempted network calls: **0**. **28** frozen call/result files were unchanged. The previous run and pinned source materials retain their hashes. Replay time: **98.9 s**, separate from online timing.

## Review files

- [Pipeline report](cases/013/report.html)
- [Accepted Task](cases/013/task/task.json)
- [Accepted annotation](cases/013/annotation/audit/raw-annotation.json)
- [Review / repair decision](cases/013/refinement/report.html)
- [Propagation report](cases/013/propagation/report.html)
- [DOE report](cases/013/doe/report.html) and [DOE result JSON](cases/013/doe/doe-result.json)
- [Assistant semantic audit](cases/013/assistant-review.md)
- [Full measurements](metrics.md) and [machine-readable measurements](metrics.json)
- [Replay verification](verification/replay-check.json)
- [Previous run](../latest-prompts-pipeline-v1-20261018-124304/index.html)
