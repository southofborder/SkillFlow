# Reporting and input-integrity audit

Audit snapshot: **2026-10-20 08:45:42–08:45:58 UTC**. The online run was still active. This is an independent assistant audit of saved records and reporting behavior, not a final execution summary or semantic verdict. No model/API call, source edit, metrics rewrite, or index rewrite was performed. Only this note was added.

The authoritative implementations are [the pilot scheduler](../../../../../tools/doe/run_joint_pipeline_pilot.py) and [the metrics collector](../../../../../tools/doe/summarize_pipeline_run.py). Verification used their read-only `verify_baseline`, `_load` and `collect` functions, plus `verify_analysis_prepared` from the public pipeline. It did not invoke `run_pilot`, replay, or a report-writing function.

## Input and implementation identity

| Check | Observed result |
|---|---|
| Pinned pre-upgrade receipts for 001, 010 and 013 | Passed the hard-coded receipt SHA-256 checks. |
| Historical annotation files, source packages and selected CFGs | All **74** recorded files matched; the freshly verified inventory exactly matched [audit/history-sha256.json](../audit/history-sha256.json). Source/CFG correspondence and package membership also passed the scheduler's checks. |
| Pilot manifest and frozen projection | [manifest.json](../manifest.json) passed its canonical digest check and all **12** frozen-file checks, including **11** English-projection files. Its case records equal the freshly verified baseline records. |
| Prepared case inputs | All three cases passed `verify_analysis_prepared(..., config=manifest['config'])`: 001/010/013 each remained `ready`, with 5/7/5 frozen files respectively. This checks preparation identity; it does not mean annotation or analysis succeeded. |
| Recorded production implementation | All **164** files recorded in each case's implementation inventory matched the files on disk. This is the inventory actually sealed by the pipeline, not a claim about every workspace file. |

The verified pilot manifest identity was `dc601b74b6ce43699ce87ce5dfdab83df5245b2cece0bd9b51d626301897fd85`. No mismatch was found in this snapshot. Repeat these checks after the online process finishes; an interim pass is not evidence about later edits.

Case 001 uses the explicit [English source/CFG projection](../audit/english-inputs/001/projection.json). Cases 010 and 013 retain the verified English inputs. Historical material is not rewritten. Comparisons with the historical Chinese 001 run therefore change input language as well as the current pipeline; they cannot isolate a prompt or constraint effect.

## Interim status and report navigation

| Case | Evidence at this audit snapshot | Reporting interpretation |
|---|---|---|
| 001 | [Terminal pipeline result](../cases/001/result.json): failed at annotation. Task extraction completed; annotation requests a001–a003 were structurally invalid, and a004 ended in `IncompleteRead`. | Five logical calls, three structural-correction requests, five recorded HTTP attempts, zero retries; these counts match the terminal pipeline result. No accepted annotation, review, propagation, or DOE result exists. |
| 010 | The Task request completed and annotation a001 was running. | No terminal pipeline result or final case count was available. |
| 013 | No recorded request had started. | Prepared inputs do not count as a completed analysis or a zero-cost final case. |

The [saved metrics](../metrics.json) were measured at **08:41:02.362789 UTC**, with `final: false`; their byte SHA-256 was `f4f6f5992b80c55fbf3e42c940d8d5cc14012ce0dda3da8ae71b1f6ab8087369`. They still showed the earlier 010 Task request in progress. A fresh read-only collection saw its completed Task and running annotation. This is snapshot lag, not evidence of an unrecorded request. The saved totals exactly equal aggregation of that snapshot's own saved call rows.

The [pilot index](../index.html), [pilot report](../report.md) and [summary](../summary.json) are written after a case returns. While 010 runs, they can still say `prepared`/`not_started` for it and display only the completed 001 result. They are not live request-progress views. At final reporting, reconcile them with terminal case results and refreshed metrics.

All local links present in the four checked pages resolved: index.html (10 links), report.md (8), metrics.md (12), and validation.md (1). One navigation omission remains: `_write_reports` looks for `task/report.html` and `refinement/task-revision/report.html`, while the Task runner writes `report.md`. The available detailed reports are [001 Task report](../cases/001/task/report.md) and [010 Task report](../cases/010/task/report.md); task.json is separately linked by the index when present. This audit leaves the active source and index unchanged. The verification notes in this directory are also not automatically indexed by that helper.

## What the metrics measure

- Logical requests are actual durable `call.json` records in the six supported stage directories. A structural correction is another request, not an HTTP retry or a semantic repair. The normal/annotation-repair/Task-revision routes have 3/5/6 semantic calls before additional structural corrections and transport retries.
- Usage is summed once per HTTP attempt. Repeated top-level transport usage is excluded. Reasoning and cache fields are components of reported usage, not additional token costs. Missing usage remains unknown. No tokenizer estimate, price, or prompt-length conversion is substituted.
- Prompt size uses the actual `prompt.txt` once per logical request, with separate character, UTF-8 byte and content-hash-deduplicated figures. These are material sizes, not token measurements. HTTP retries do not create additional logical prompts.
- Call-wall, transport-call and HTTP times are nested clocks. Per-case time starts at its earliest recorded call and ends at the initially observed terminal result mtime. Overall time uses the explicit [online clock](../online-clock.json), **08:26:50.474354 UTC**, through the initial completed pilot-summary mtime. Preparation is excluded; nested durations must not be added together.
- The collector verified all transport-record hashes observed during this audit without an integrity error. Active requests remain incomplete snapshots. Final collection additionally requires terminal results for every case, no observed/pipeline count disagreement, and no transport integrity errors; it freezes the call-file inventory and rejects later changes.

For terminal case 001, the observed case interval is **819.285621 seconds**. Its API-reported total-token subtotal is **192,354 across four attempts**, with one attempt missing usage; therefore its complete token total is **unknown**. Annotation a004 was the third structural-correction request, but its terminal failure was a transport/execution failure: HTTP 200, `IncompleteRead`, `remote_outcome_unknown`, zero recorded content characters, and no usage. HTTP 200 does not establish a complete response, successful processing, or zero provider consumption. No final run totals are claimed here.

## Final validation still required

1. Wait for the online process and all three cases to reach recorded terminal states. Preserve the initial `summary.json`, case results, statuses, selected Task/annotation identities, and failure reasons. Review rejection or repair limits must remain diagnostic where applicable; failed annotation must not acquire historical fallback output.
2. Recheck pinned historical bytes, English projection, case preparation, and sealed implementation identities. Record any difference explicitly. The checks above cover this audit snapshot only.
3. **Before any replay, finalize metrics with the original explicit start clock.** Confirm per-case observed counts match pipeline counts, transport hashes pass, terminal timing/result identities are recorded, and `frozen_call_files` is populated. Preserve missing usage as unknown even when every case is terminal.
4. Run the public pilot **zero-API replay only after that timing freeze**. Check `api_calls == 0`, `history_unchanged == true`, no replay interruption or unstarted case, and correspondence with the initial case statuses/results. Replaying the failed 001 case must not resend its request or manufacture a successful annotation/DOE result.
5. Recollect metrics after replay and require `call_files_unchanged == true`, unchanged frozen call/transport/prompt files, and unchanged initial online timing. Compare the stored terminal result/summary hashes as well as statuses; timing preservation is keyed by those identities, so mtime changes alone must not redefine the online experiment.
6. Refresh final report navigation through the existing reporting helper after final metrics, replay summary and assistant assessments exist, then recheck local links and initial/final Task, annotation and review selections. Include the available Markdown Task reports or explicitly retain the navigation omission. This separate note does not modify the current index.
7. Report execution failures, structural corrections, review outcomes, declared constraints, baseline checker results and candidate-preservation results separately. Completion/cost records do not establish extraction completeness, natural-language equivalence, actual leaks, or the absence of DOE. Constraint fidelity and the justification for each supported reduction still require the separate semantic assessment.

Zero-API replay had **not** been performed at this snapshot. No final online total, final semantic outcome, or full-run integrity verdict is asserted.
