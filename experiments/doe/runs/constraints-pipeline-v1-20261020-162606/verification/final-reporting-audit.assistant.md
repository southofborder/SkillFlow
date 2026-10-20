# Final online reporting and input-integrity audit

Audit snapshot: **2026-10-20 09:45 UTC**. The online run is terminal and its metrics were finalized before replay. Replay is in progress; a replay-summary file can contain intermediate results and is not treated here as a completion receipt. This note verifies saved records, arithmetic, identities, stage selections and report links. It does not assess the completeness or semantic correctness of the model's declarations.

No API, pipeline execution, or replay was invoked by this audit. No source, metrics or index was changed. Only this note was written. Authoritative references are [run_joint_pipeline_pilot.py](../../../../../tools/doe/run_joint_pipeline_pilot.py) and [summarize_pipeline_run.py](../../../../../tools/doe/summarize_pipeline_run.py).

## Frozen measurements

The inspected [metrics.json](../metrics.json) had `final: true`, measurement time **09:43:18.682393 UTC**, and byte SHA-256 `0df7992b7f3de04d708f5ccb4d566ff20b92c8780b89b3feb57296598eadf0f8`. A fresh read-only `collect` matched its calls, case results, totals, frozen inventory, timing and terminal-summary identity exactly. Independent calculations from request files, prompt bytes and individual HTTP-attempt usage also matched.

| Case | Logical calls / structural corrections | HTTP attempts / retries | Reported input tokens | Reported output tokens | Reported total tokens | Frozen case seconds |
|---|---:|---:|---:|---:|---:|---:|
| 001 | 5 / 3 | 5 / 0 | 62,074 subtotal | 130,280 subtotal | **Unknown; 192,354 subtotal** | 819.285621 |
| 010 | 4 / 1 | 4 / 0 | 88,793 | 154,436 | 243,229 | 971.497258 |
| 013 | 8 / 3 | 8 / 0 | 307,544 | 322,471 | 630,015 | 2,754.999892 |
| Run | **17 / 7** | **17 / 0** | **458,411 subtotal** | **607,187 subtotal** | **Unknown; 1,065,598 subtotal** | **4,550.989651 overall wall time** |

The run contains 10 stage-initial requests, one fixed-Task semantic repair request, no Task-revision request, and no JSON normalization. The seven structural corrections are additional requests, not seven semantic repairs. All per-case counts agree with their terminal pipeline results.

Exactly one HTTP attempt lacks usage: 001 annotation a004, the third structural-correction request. It ended with HTTP 200 followed by `IncompleteRead`, `remote_outcome_unknown`, and no complete accepted response. No provider token usage or zero-consumption claim can be inferred for that attempt. The other 16 attempts supply the reported subtotals. Missing usage keeps the 001 and overall complete token totals unknown even though online execution is terminal.

The configured request model is **`deepseek-v4-flash`**, with `max` reasoning. The model name actually present in response records is **`deepseek-flash`**. Both strings should be retained in the experiment report; this audit does not infer provider alias equivalence from their names.

All 17 saved prompts were independently checked against their recorded character counts, UTF-8 byte counts and SHA-256 values: **1,875,888 characters / 1,875,888 bytes**, with 17 distinct contents. These are actual request-material sizes, not token estimates. Reasoning (507,117 reported tokens) and cache-hit/miss figures are components of reported usage and must not be added to the token subtotal again.

The explicit [online clock](../online-clock.json) starts at **08:26:50.474354 UTC**; the frozen terminal-summary time is **09:42:41.464005 UTC**, yielding **4,550.989651 seconds**. All per-case and overall timestamp subtractions match the recorded durations. Per-case clocks begin at the earliest recorded request and exclude the small preceding preparation/verification interval. Call wall time (3,030.279416 seconds), transport-call time and HTTP time are nested measures; they are not added to the overall wall time. Replay time must remain excluded.

## Terminal stages and selection identity

| Case | Actual request stages | Selected result and reason |
|---|---|---|
| 001 | Task ×1; annotation ×4 | [Pipeline failed at annotation](../cases/001/result.json): `IncompleteRead(0 bytes read)`. Task completed, but there is no accepted/selected annotation, review, propagation or DOE result. |
| 010 | Task ×1; annotation ×2; initial review ×1 | [Pipeline is diagnostic](../cases/010/result.json). Initial review reported `review_passed`, selected the original `annotation`, and invoked no semantic repair. Propagation completed with 12 sinks; DOE is `partial`. The pipeline's diagnostic status remains visible despite review acceptance. |
| 013 | Task ×1; annotation ×3; initial review ×1; annotation repair ×2; final review ×1 | [Pipeline is diagnostic](../cases/013/result.json). Fixed-Task repair selected `refinement/repair`; final refinement status is `repair_limit`: issues remain after the single semantic repair. Propagation completed with 16 sinks and DOE computation is `complete`; neither changes the unresolved semantic-review outcome. |

Each terminal case result passed its seal check and equals the corresponding [online summary](../summary.json) case record after removing the result's own seal. The selected 010/013 annotation manifest IDs and canonical raw-annotation hashes match the actual selected artifacts. Both selected annotations' `task_revision_id` matches that case's original sealed Task; no Task revision was selected. Review result `status: complete` records successful review-response validation and must not be confused with an issue-free semantic review.

## Input, source and record integrity

- All **74** pinned historical files passed `verify_baseline`, including hard-coded receipt digests, annotation-file hashes, selected CFGs, source correspondence and complete package membership. Its freshly verified inventory equals [history-sha256.json](../audit/history-sha256.json), and its case records equal the pilot manifest's records.
- The pilot manifest and all **12** frozen pilot files passed `_load`, including **11** English-projection files. Case 001's explicit translation remains a comparison caveat; historical Chinese source was not rewritten.
- Each case's pipeline manifest seal and public configuration match. All **5/7/5** case frozen-input files for 001/010/013 match their recorded bytes.
- All **164** implementation files recorded by each case still match the current workspace, including the recorded production source and formal assets. This statement is about the sealed inventory, not every unrelated workspace file.
- All **17** transport records passed their canonical record-digest check. All **100 frozen call files** still match `metrics.frozen_call_files`. The terminal case-result and online-summary byte hashes still match the frozen timing identities.

No arithmetic, selected-artifact, frozen-input, implementation, transport-record or call-file mismatch was found in this audit snapshot.

## Links and remaining reporting work

All existing local links in **24 currently present report pages** resolved. The check covered the top-level index, report, metrics and validation pages, all currently present case `report.html` files (including partial replay reports), and the three Task Markdown reports. It does not certify report pages that replay has not yet generated.

The earlier navigation omission remains: the pilot helper checks for `task/report.html`, while Task output is Markdown. Available details are [001 Task](../cases/001/task/report.md), [010 Task](../cases/010/task/report.md) and [013 Task](../cases/013/task/report.md). The same helper pattern would omit a Task-revision Markdown report, though no Task revision occurred here. The index also needs its ordinary final refresh after replay and assistant assessments so newly available links appear; no source or index change was made during this audit.

**Replay completion remains pending in this note.** The frozen metrics contain `zero_api_replay: null`. After replay terminates, attach its completion receipt and verify zero API calls, unchanged historical inputs, no unstarted/interrupted case, unchanged frozen call files, equality with the original stage decisions, and unchanged initial online timing. Then recollect metrics and verify `call_files_unchanged: true`, refresh the final report links through the existing helper, and check those links again. An intermediate replay-summary file or a subset of successful replay pages is insufficient evidence of completion.

This audit found a navigation omission, but no integrity or arithmetic discrepancy. The experiment still contains an annotation transport failure (001), partial DOE (010), and unresolved post-repair review issues (013). These outcomes must remain explicit in the final interpretation; successful deterministic computation does not establish semantic completeness or absence of DOE.
