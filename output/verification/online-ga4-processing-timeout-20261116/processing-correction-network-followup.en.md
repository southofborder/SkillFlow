# Processing correction: third internal retry observation

Provisional snapshot, 2026-11-16 16:26:15–16:26:57 UTC (2026-11-17 00:26:15–00:26:57 China). The same initial processing structural-correction process remains active. There is still no native exit/timeout receipt or completed public final message.

At 16:25:12.304769 UTC, native stderr reports sampling retry **3/5**, with an 802 ms backoff. The recorded cause is a server-closed WebSocket before `response.completed`. This occurs 1,831.748439 seconds after the native start marker and 916.771726 seconds after retry 2's public timestamp. The complete notice sequence is:

| Retry | Recorded cause | Seconds after start | Gap from previous retry notice |
|---|---|---:|---:|
| 1/5 | Connection reset, OS error 10054 | 899.753114 | — |
| 2/5 | Request timed out | 914.976713 | 15.223599 seconds |
| 3/5 | Server closed WebSocket before response completion | 1,831.748439 | 916.771726 seconds |

The second stdout reconnect notice reports ordinal 3/5. Its host observation interval is 16:25:11.002436–16:25:41.016930 UTC, containing retry 3's native stderr timestamp. The earlier stdout notice reports ordinal 2/5. These two notices overlap the three stderr retry records; they are not two additional retries or launches.

The roughly 900-second intervals above are measured gaps between particular public events. They do **not** establish a 900-second idle timeout, uninterrupted generation duration, a server timeout configuration, or network-only attribution of the elapsed time. The evidence establishes the reported reset, request timeout and server-closed stream, without apportioning the intervals among generation, waiting and reconnect work.

The total native budget remains 2,700 seconds. Adding that budget to the public start marker gives 16:39:40.556330 UTC as an arithmetic deadline reference, not an observed timeout. The latest sidecar sample is nonterminal at 1,920.475668 elapsed seconds and contains no completed final message. Final duration and usage for this active correction remain unknown.

One additional auxiliary model-list refresh timeout is recorded at 16:12:54.426485 UTC. There are now ten auxiliary refresh lines across the run, separate from the three sampling retries. The public surface classifier labels retry 3 generically as `other_public_responses_retry`; the more specific WebSocket-close classification here comes directly from its raw public stderr line, recorded with a digest in the follow-up JSON. The classifier utility was not changed.

Counts remain six native starts (four normal requests and two structural corrections), zero outer retries and five complete public usage receipts. Known usage remains 670,215 tokens (508,646 input plus 161,569 output); the active correction remains unknown. All 206 implementation pins, 16 source files, controller/timing helper and three executable pins remain unchanged, with no cost/provenance audit issue.

Evidence:

- `cost-provenance-audit/ga4-20261116T162615325928Z.json`
- `cost-provenance-audit/public-surface-20261116T162613335316Z.json`
- `cost-provenance-audit/public-network-followup-20261116T162657431584Z.json`

This update used only passive local public-log and artifact reads. No process control, model call, Skill, probe, replay or frozen-file change was performed. Further reads stop pending a terminal notification.
