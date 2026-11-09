# Small 013 v8: cost and protocol audit

The closed `source-fetch-with-fallback` run used **13 actual CLI starts and 375,925 known public tokens**, including all structural corrections and the shared repair. Its sole replay matched with zero new starts. This report audits cost and provenance only; the separate source audit evaluates the partial result.

| Category | Native starts | Public tokens |
|---|---:|---:|
| normal semantic | 7 | 180,153 |
| semantic repair | 4 | 128,768 |
| structural correction | 2 | 67,004 |
| **Total** | **13** | **375,925** |

Input usage is **335,585 tokens**, including **159,744 cached-input tokens**; output is **40,340 tokens**, including **12,242 reasoning-output tokens**. Cache and reasoning values are subsets, not additional totals. All 13 accepted finals report complete usage. Totals reconcile exactly between public turn-completed events, per-request records and metrics.json.

Main analysis took **940.2633461 seconds (15 min 40.26 s)**. The sole replay took **111.3602313 seconds (1 min 51.36 s)**. Controller wall time was **1053.142802 seconds (17 min 33.14 s)**. The native request-duration sum was 811.873898 seconds; the first-to-last native span was 793.142806 seconds. Sums, overlapping spans and full analysis wall time are different measures.

| Stage | Status | Wall seconds |
|---|---|---:|
| task | complete | 49.771105 |
| flow | complete | 27.576794 |
| graph | complete | 92.250019 |
| processing | complete | 148.267403 |
| task-correspondence | complete | 173.838485 |
| sensitivity | complete | 17.844859 |
| assembly | partial | 20.735014 |
| review | complete | 75.919132 |
| revision-processing | complete | 108.421370 |
| revision-task-correspondence | complete | 81.501401 |
| revision-sensitivity | complete | 14.944859 |
| revision/assembly | partial | 20.902781 |
| revision/review | complete | 43.245190 |
| propagation | incomplete | 53.712383 |
| doe | partial | 92.062570 |

Stage durations include local reconstruction, validation and saving, and parallel stages overlap. They are not solver-only measurements.

All request records and launch flags consistently requested **gpt-6.1-sol / high / openai**. Public logs expose 13 unique CLI thread/turn identities, but no provider response IDs or independent backend configuration attestation. Each accepted answer matches its recorded hash, public final message and saved last message. Each submitted prompt hash matches the request delivery hash and launch stdin hash.

Public events comprise 13 thread starts, 13 turn starts, 13 completed agent messages and 13 completed turns. **No public reconnect/error events, tool/delegation items, outer retries or prelaunch input rejections were observed.** Exact provider HTTP attempts and any additional unreported internal work remain unknown; they are not inferred as zero. No currency amount or human review time is estimated. Independent post-run assistant auditing is outside this target-generation usage total.

The one frozen source file matches its snapshot hash. Source identity is `fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da`. The saved implementation check is unchanged, SHA `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`, with no changed files. The accepted source snapshots, answers, failures, stage results and replay were not rewritten. This audit read saved JSON, public logs and source bytes; it invoked no model target, Skill, loader, compiler, solver or replay.

[Machine-readable cost and evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small013-cost.json) · [Original metrics](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/metrics.json) · [Replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/replay-check.json)
