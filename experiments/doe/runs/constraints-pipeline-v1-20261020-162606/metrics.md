# Online execution metrics

Run: `constraints-pipeline-v1-20261020-162606`

These measurements describe actual requests. They do not establish semantic correctness.

| Case | Logical calls | Structural corrections | JSON normalizations | Annotation repair / reannotation | HTTP attempts / retries | Reported input | Reported output | Reported total | Online seconds |
|---|---:|---:|---:|---:|---:|---|---|---|---:|
| 001 | 5 | 3 | 0 | 0 | 5 / 0 | unknown (reported subtotal: 62,074; 1 missing) | unknown (reported subtotal: 130,280; 1 missing) | unknown (reported subtotal: 192,354; 1 missing) | 819.29 |
| 010 | 4 | 1 | 0 | 0 | 4 / 0 | 88,793 | 154,436 | 243,229 | 971.50 |
| 013 | 8 | 3 | 0 | 1 | 8 / 0 | 307,544 | 322,471 | 630,015 | 2,755.00 |

Normal / fixed-Task annotation repair / isolated Task revision and reannotation use 3 / 5 / 6 semantic calls. Structural corrections and HTTP retries are additional; these are not total-request limits.

| Case | Actual repair route | Task revision requests | Semantic-stage initial requests | Counts match pipeline |
|---|---|---:|---:|---|
| 001 | none | 0 | 2 | True |
| 010 | none | 0 | 3 | True |
| 013 | fixed_task_annotation_repair | 0 | 5 | True |

Overall online wall time: **4,550.99 seconds**.
Logical requests: **17**. HTTP attempts: **17**. API-reported total tokens: **unknown (reported subtotal: 1,065,598; 1 missing)**.

## Per-request detail

| Case / stage / call | Outcome | Correction | JSON repair | HTTP attempts | Call seconds | HTTP seconds | Reported total tokens |
|---|---|---|---|---:|---:|---:|---|
| [001 / task_extraction / a001](cases/001/task/calls/task/a001/call.json) | complete / valid | False | False | 1 | 54.82 | 54.54 | 11,912 |
| [001 / annotation / a001](cases/001/annotation/calls/annotation/a001/call.json) | complete / structural_invalid | False | False | 1 | 322.11 | 320.11 | 81,207 |
| [001 / annotation / a002](cases/001/annotation/calls/annotation/a002/call.json) | complete / structural_invalid | True | False | 1 | 196.37 | 195.03 | 55,350 |
| [001 / annotation / a003](cases/001/annotation/calls/annotation/a003/call.json) | complete / structural_invalid | True | False | 1 | 124.97 | 124.15 | 43,885 |
| [001 / annotation / a004](cases/001/annotation/calls/annotation/a004/call.json) | error / None | True | False | 1 | 112.65 | 112.33 | unknown (reported subtotal: unknown; 1 missing) |
| [010 / task_extraction / a001](cases/010/task/calls/task/a001/call.json) | complete / valid | False | False | 1 | 100.80 | 100.04 | 21,823 |
| [010 / annotation / a001](cases/010/annotation/calls/annotation/a001/call.json) | complete / structural_invalid | False | False | 1 | 359.67 | 357.91 | 87,546 |
| [010 / annotation / a002](cases/010/annotation/calls/annotation/a002/call.json) | complete / valid | True | False | 1 | 117.41 | 116.58 | 43,906 |
| [010 / initial_review / a001](cases/010/refinement/initial-review/calls/review/a001/call.json) | complete / valid | False | False | 1 | 260.36 | 258.83 | 89,954 |
| [013 / task_extraction / a001](cases/013/task/calls/task/a001/call.json) | complete / valid | False | False | 1 | 48.41 | 48.10 | 12,008 |
| [013 / annotation / a001](cases/013/annotation/calls/annotation/a001/call.json) | complete / structural_invalid | False | False | 1 | 303.15 | 300.60 | 96,728 |
| [013 / annotation / a002](cases/013/annotation/calls/annotation/a002/call.json) | complete / structural_invalid | True | False | 1 | 103.74 | 103.07 | 55,365 |
| [013 / annotation / a003](cases/013/annotation/calls/annotation/a003/call.json) | complete / valid | True | False | 1 | 155.75 | 154.59 | 64,951 |
| [013 / initial_review / a001](cases/013/refinement/initial-review/calls/review/a001/call.json) | complete / valid | False | False | 1 | 330.32 | 328.02 | 142,885 |
| [013 / fixed_task_semantic_repair / a001](cases/013/refinement/repair/calls/annotation/a001/call.json) | complete / structural_invalid | False | False | 1 | 82.12 | 81.09 | 61,360 |
| [013 / fixed_task_semantic_repair / a002](cases/013/refinement/repair/calls/annotation/a002/call.json) | complete / valid | True | False | 1 | 62.45 | 61.61 | 63,872 |
| [013 / final_review / a001](cases/013/refinement/final-review/calls/review/a001/call.json) | complete / valid | False | False | 1 | 295.18 | 292.80 | 132,846 |

## API-reported reasoning and cache breakdown

These fields are parts of the reported token totals, not additional tokens. Missing fields stay unknown.

| Case / stage / call | Input | Output | Reasoning within output | Cache-hit input | Cache-miss input |
|---|---:|---:|---:|---:|---:|
| 001 / task_extraction / a001 | 1,681 | 10,231 | 8,677 | 1,536 | 145 |
| 001 / annotation / a001 | 20,541 | 60,666 | 55,951 | 0 | 20,541 |
| 001 / annotation / a002 | 19,927 | 35,423 | 30,710 | 14,720 | 5,207 |
| 001 / annotation / a003 | 19,925 | 23,960 | 19,048 | 15,488 | 4,437 |
| 001 / annotation / a004 | unknown (reported subtotal: unknown; 1 missing) | unknown (reported subtotal: unknown; 1 missing) | unknown | unknown | unknown |
| 010 / task_extraction / a001 | 1,792 | 20,031 | 17,950 | 1,536 | 256 |
| 010 / annotation / a001 | 21,429 | 66,117 | 60,733 | 128 | 21,301 |
| 010 / annotation / a002 | 21,639 | 22,267 | 16,746 | 15,616 | 6,023 |
| 010 / initial_review / a001 | 43,933 | 46,021 | 43,352 | 0 | 43,933 |
| 013 / task_extraction / a001 | 1,699 | 10,309 | 8,561 | 1,536 | 163 |
| 013 / annotation / a001 | 22,895 | 73,833 | 62,479 | 128 | 22,767 |
| 013 / annotation / a002 | 29,774 | 25,591 | 14,289 | 17,152 | 12,622 |
| 013 / annotation / a003 | 28,931 | 36,020 | 24,620 | 22,400 | 6,531 |
| 013 / initial_review / a001 | 69,159 | 73,726 | 69,743 | 128 | 69,031 |
| 013 / fixed_task_semantic_repair / a001 | 39,416 | 21,944 | 9,960 | 22,656 | 16,760 |
| 013 / fixed_task_semantic_repair / a002 | 46,066 | 17,806 | 5,706 | 17,152 | 28,914 |
| 013 / final_review / a001 | 69,604 | 63,242 | 58,592 | 8,960 | 60,644 |

## Actual prompt input size

These are character and UTF-8 byte counts, not token estimates. Each logical request is counted once; HTTP retries of the same request are not additional prompts.

| Case / stage / call | Characters | UTF-8 bytes |
|---|---:|---:|
| [001 / task_extraction / a001](cases/001/task/calls/task/a001/prompt.txt) | 7,207 | 7,207 |
| [001 / annotation / a001](cases/001/annotation/calls/annotation/a001/prompt.txt) | 89,198 | 89,198 |
| [001 / annotation / a002](cases/001/annotation/calls/annotation/a002/prompt.txt) | 86,293 | 86,293 |
| [001 / annotation / a003](cases/001/annotation/calls/annotation/a003/prompt.txt) | 86,280 | 86,280 |
| [001 / annotation / a004](cases/001/annotation/calls/annotation/a004/prompt.txt) | 87,025 | 87,025 |
| [010 / task_extraction / a001](cases/010/task/calls/task/a001/prompt.txt) | 7,574 | 7,574 |
| [010 / annotation / a001](cases/010/annotation/calls/annotation/a001/prompt.txt) | 92,789 | 92,789 |
| [010 / annotation / a002](cases/010/annotation/calls/annotation/a002/prompt.txt) | 93,573 | 93,573 |
| [010 / initial_review / a001](cases/010/refinement/initial-review/calls/review/a001/prompt.txt) | 162,319 | 162,319 |
| [013 / task_extraction / a001](cases/013/task/calls/task/a001/prompt.txt) | 7,206 | 7,206 |
| [013 / annotation / a001](cases/013/annotation/calls/annotation/a001/prompt.txt) | 97,811 | 97,811 |
| [013 / annotation / a002](cases/013/annotation/calls/annotation/a002/prompt.txt) | 120,965 | 120,965 |
| [013 / annotation / a003](cases/013/annotation/calls/annotation/a003/prompt.txt) | 118,161 | 118,161 |
| [013 / initial_review / a001](cases/013/refinement/initial-review/calls/review/a001/prompt.txt) | 238,828 | 238,828 |
| [013 / fixed_task_semantic_repair / a001](cases/013/refinement/repair/calls/annotation/a001/prompt.txt) | 158,980 | 158,980 |
| [013 / fixed_task_semantic_repair / a002](cases/013/refinement/repair/calls/annotation/a002/prompt.txt) | 181,351 | 181,351 |
| [013 / final_review / a001](cases/013/refinement/final-review/calls/review/a001/prompt.txt) | 240,328 | 240,328 |

Across 17 logical requests: **1,875,888 characters / 1,875,888 UTF-8 bytes**. Distinct prompt contents: **17**, totaling 1,875,888 characters / 1,875,888 UTF-8 bytes.

## Consumption explanation

For currently API-reported subtotals; pending or unreported attempts are excluded, reasoning accounts for **507,117 tokens**, **83.52% of completion tokens** and **47.59% of total tokens**. Reasoning is already included in completion and total tokens; adding it again would double-count consumption.

A long request can spend substantial time and output-token budget in reasoning before any final JSON text appears. Stream-event counts and bytes are not token measurements. This run uses the frozen configured reasoning effort; the report records consumption without changing generation settings.

Per-request call wall times measure each model operation plus its local call wrapper. Per-case wall times additionally include stage validation, compilation, propagation, and DOE work. Overall process wall time includes sequential case orchestration. These are nested clocks and are not added together.

## Measurement boundaries

- Only the six durable request directories of cases in this pilot: Task extraction, annotation, initial review, isolated Task revision, annotation repair/reannotation, and final review. Connectivity diagnostics are excluded.
- One on-disk call.json per actual request. Corrections are distinct calls; accepted-response replay is not a call.
- Sum HTTP attempt usage exactly once; top-level transport usage repeats the last attempt and is excluded. Missing usage is unknown, never zero.
- API-reported cache-hit/miss/reasoning/detail fields are breakdowns, not extra tokens; never add them to total_tokens.
- Character and UTF-8 byte counts use each actual prompt.txt once per logical request, with a content-hash deduplication subtotal. HTTP retries do not create prompts. These are sizes, not token estimates.
- Call wall, transport call, and HTTP elapsed are nested measures and must not be added together. Per-case clocks include local stage work. Initial terminal times are frozen before replay.
- An explicit process start can be supplied once; otherwise use the earliest recorded call. Preparation is excluded. Never infer a process clock from measurement time.
- Usage and completion metrics do not validate sensitivity, demand, or DOE conclusions.
- Per-case timing starts at the first recorded call and ends at the initial terminal pipeline result write. It excludes the small validation interval before that call.
- Running requests have incomplete time/usage. Failed HTTP attempts without usage prevent a claim of complete token totals; known subtotals remain available.
- API usage, including cache details, is preserved per HTTP attempt in metrics.json. No tokenizer-based estimate or price assumption is substituted.

## Provider and transport failures

- 001 / annotation / a004, HTTP attempt 1: The HTTP response stream ended with IncompleteRead before a complete candidate was accepted; this is a transport/execution failure, not structural correction or semantic-review failure. No result is inferred from HTTP status 200 alone. Recorded content characters: 0.
