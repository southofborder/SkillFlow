# Small Skill 001 v8: public cost and protocol audit

The closed conditional-notification run used **14 actual CLI starts**, with **343,524 known public tokens**. Its status was partial; the sole replay matched with zero new starts. This audit reads saved JSON and public event metadata only.

| Category | Starts | Input | Cached input subset | Output | Total tokens |
|---|---:|---:|---:|---:|---:|
| normal semantic | 7 | 142,687 | 86,016 | 20,456 | 163,143 |
| semantic repair | 4 | 100,698 | 49,152 | 7,098 | 107,796 |
| structural correction | 3 | 69,063 | 36,864 | 3,522 | 72,585 |

Known input usage is **312,448**, including **172,032 cached input**. Output is **31,076**, including **16,251 reasoning-output tokens**. Total is input plus output, **343,524**; cache and reasoning counters are not added again. All 14 accepted finals have complete public usage. Per-request totals match both metrics and the public turn-completed events. Original answers later corrected and repair costs are included.

There were **0 outer retries**, **0 prelaunch input rejections**, and **0 public reconnect/error events**. Public events contain 14 each of thread.started, turn.started, item.completed and turn.completed; all completed items are agent_message, with no recorded tool/delegation items. Exact provider HTTP attempts and any unreported provider work remain unknown.

The 14 CLI thread/turn-order identities are unique. Provider response IDs are not exposed. Every saved request and launch consistently requested `gpt-6.1-sol / high / openai`; this is not independent backend configuration confirmation. Saved accepted-answer hashes and delivery-input hashes all match.

| Time measure | Seconds | Readable duration |
|---|---:|---|
| Main analysis | 937.31803990 | 15 min 37.32 s |
| Sole replay | 45.74706500 | 45.75 s |
| Controller wall | 984.470494 | 16 min 24.47 s |
| Sum of native request durations | 934.57099770 | Overlapping calls; not wall time |
| First native start to last native finish | 879.63061309 | Includes gaps and overlap |

Main analysis ran from 2026-11-02 02:14:04 to 02:29:42 China time; controller closure was 02:30:29. Stage durations below include local validation, reconstruction and saving; parallel stages overlap.

| Stage | Status | Wall seconds |
|---|---|---:|
| task | complete | 59.864067 |
| flow | complete | 25.224541 |
| graph | complete | 170.521781 |
| processing | complete | 195.357234 |
| task-correspondence | complete | 180.172163 |
| sensitivity | complete | 21.056591 |
| assembly | partial | 13.161753 |
| review | complete | 93.269307 |
| revision-processing | complete | 87.621474 |
| revision-task-correspondence | complete | 38.143161 |
| revision-sensitivity | complete | 14.039534 |
| revision/assembly | partial | 9.832940 |
| revision/review | complete | 66.337268 |
| propagation | incomplete | 26.692454 |
| doe | partial | 29.087914 |

Implementation remained unchanged: `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. The frozen one-file source snapshot matches the run protocol and actual file bytes; source identity is `d7548162e5d4de62ee90bd1763b1a701bcbe731c723d675d9d2e0dd8e5c989a6`. This is the previously audited English development package, not a held-out case.

No currency amount, human review time or complete research/auditing cost is inferred. The partial result must be assessed for source coverage and DOE correctness separately.

[Structured per-request evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small001-cost.json)
