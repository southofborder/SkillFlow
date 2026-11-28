# Final public cost and provenance audit

The sole fresh shared-v2 GA4 controller closed **partial**. Its source review remained a structural failure after one structural correction; no semantic repair ran. The passive cost/provenance audit is **verified**, with no discrepancies or warnings. This accounting result does not mean source review or semantic analysis succeeded.

The final machine-readable audit is [`cost-provenance-audit/ga4-20261112T163447543820Z.json`](cost-provenance-audit/ga4-20261112T163447543820Z.json), observed at 2026-11-12T16:34:47.542508+00:00. Earlier snapshots and transport notes remain unchanged. This audit performed no model call, Skill execution, backend analysis, test run or replay.

## Actual calls and available cost

There were **12 PID-confirmed native starts: seven normal requests and five structural corrections**. Corrections occurred in graph, processing, task-correspondence, sensitivity and review. Semantic-repair starts, outer network retries, launch errors, unconfirmed starts and pre-start input rejections were all zero. The configured schedule remained seven normal requests and two workers.

All 12 requests have complete public final usage associated with accepted transport answers. There are zero partial or missing final-usage requests and no partial token totals.

| Public counter | Tokens |
| --- | ---: |
| Input | 2,054,895 |
| Cached input, included in input | 924,416 |
| Cache-write input reported | 0 |
| Output | 241,840 |
| Reasoning output, included in output | 8,916 |
| **Total input plus output** | **2,296,735** |

The seven normal requests account for 1,289,624 public tokens; the five structural corrections account for 1,007,111. Cache and reasoning subsets are not added again. These are the full available public counters, not a provider bill: additional unreported internal-attempt usage, underlying HTTP-attempt counts and monetary charges remain unknown. All requests asked for `gpt-6.1-sol`, high effort, OpenAI; public completion metadata did not disclose an actual returned model name, so that identity remains unobserved.

## Actual durations

Main analysis took **8,255.173 seconds** (2 hours 17 minutes 35.2 seconds). The sole replay matched in **174.913 seconds** (2 minutes 54.9 seconds), with **zero new native starts**. Native-request durations sum to 9,820.393 seconds because two workers overlap; the interval from first native start to final native finish was 8,136.397 seconds. Neither sum is an additional controller wall duration.

| Stage | Normal request seconds | Structural-correction seconds | Stage start-to-finish seconds | Public tokens |
| --- | ---: | ---: | ---: | ---: |
| task | 834.957 | 0.000 | 834.958 | 99,528 |
| flow | 160.899 | 0.000 | 160.899 | 85,689 |
| graph | 1,644.585 | 893.528 | 2,540.045 | 282,811 |
| processing | 1,675.962 | 187.367 | 1,865.214 | 381,675 |
| task-correspondence | 1,165.505 | 44.269 | 1,212.604 | 444,413 |
| sensitivity | 859.839 | 27.774 | 890.253 | 403,367 |
| review | 2,291.115 | 34.592 | 2,326.592 | 599,252 |

Stage spans include the small local gaps between a normal request and its correction. Concurrent stage spans must not be summed. Saved backend timing separately records propagation total 49.856 seconds (compute 2.517; save 46.223) and DOE total 65.138 seconds (load 3.557; compute 55.770; measured post-compute publication 3.034). These nested components are not added to their parent totals. Backend return does not establish complete semantic coverage.

## Complete review deliveries

Both source-review requests reached native start. The normal review delivered **861,152 Unicode codepoints**, leaving **187,424** below the 1,048,576 cap. Its structural correction delivered **867,125**, leaving **181,451**. Each total includes the 212-character transport envelope. The frozen delivered hashes match request records. The recorded UTF-8 byte sizes are 861,369 and 867,342 respectively; this adapter limit is measured in codepoints, not bytes or tokens. There was no input-size rejection.

The delivery-size fix therefore allowed both complete review requests to be sent. It did not prevent the separate structural response failure after correction.

## Internal transport errors and timeouts

Saved stderr contains **10 internal CLI sampling-retry lines**: three TLS peer-close errors without `close_notify`, three OS error 10054 events, one server-closed WebSocket before response completion, and **three internal `request timed out` events**. Public stdout contains five reconnect error notices. These observations overlap and are not 15 independent attempts. There are no stderr connection-wait lines or other responses-retry lines, and no outer network retries.

| Stage | UTC event time | Saved error class | Advertised retry delay, ms |
| --- | --- | --- | ---: |
| task | 2026-11-12T14:21:54.176516Z | tls_peer_closed_without_close_notify | 186 |
| graph | 2026-11-12T14:28:15.879658Z | websocket_closed_before_response_completed | 180 |
| sensitivity | 2026-11-12T15:35:02.723124Z | tls_peer_closed_without_close_notify | 199 |
| task-correspondence | 2026-11-12T15:35:09.856694Z | tls_peer_closed_without_close_notify | 196 |
| task-correspondence | 2026-11-12T15:39:39.499188Z | os_error_10054 | 366 |
| sensitivity | 2026-11-12T15:39:39.515191Z | os_error_10054 | 364 |
| task-correspondence | 2026-11-12T15:39:54.910641Z | internal_request_timeout | 791 |
| sensitivity | 2026-11-12T15:39:54.943427Z | internal_request_timeout | 794 |
| review | 2026-11-12T16:09:40.007398Z | os_error_10054 | 189 |
| review | 2026-11-12T16:09:55.258331Z | internal_request_timeout | 395 |

The three internal timeout warnings occurred in sensitivity and task-correspondence at approximately 15:39:54 UTC (23:39:54 China time), and in normal review at 16:09:55 UTC (00:09:55 China time on November 13). All 12 native processes ultimately exited with return code zero. **None reached the 2,700-second native-process timeout.** The longest was normal review at 2,291.115 seconds. The logs establish internal request timeouts and closed streams, but do not distinguish connection establishment, waiting for data or another provider-internal timeout phase. They also do not establish a user-local outage or quantify added latency and repeated generation.

The 22 auxiliary model-list-refresh log lines are recorded separately; they are not additional analysis calls. Detailed event coordinates and hashes are in [`cost-provenance-audit/final-transport-events.json`](cost-provenance-audit/final-transport-events.json). Earlier `transport-notes.en.md` describes the first two stream closures as of its earlier snapshot; later timeout events do not rewrite that observation.

## Frozen materials, replay and process closure

The current and frozen **199 pinned files** match, with no changed, missing or unpinned implementation files. Controller/timing helper and CLI/renderer/Python executable hashes match. All **16 source files** match their frozen snapshot and staged package.

- Implementation SHA-256: `b3eba2da9823ac8a38620d7a5a728d7b8c66b4f3a5fe14fd7980997923330387`.
- Source SHA-256: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
- Implementation snapshot SHA-256: `4c420a118ba814ecbd0422fff3b0465d05315a0539dd60a7d97fb20982511ba2`.

The saved sole-replay receipt matches controller closure, declares the maximum of one replay and zero new native markers, and an independent scan finds no native start at or after the recorded replay boundary. No second replay was performed by this audit.

A passive OS observation at 16:35:30 UTC confirms controller PID 22344 and wrapper PID 6636 are absent. All native process receipts confirm exit. Numeric PID 22492 currently belongs to `svchost`, while its original processing-correction receipt records exit with code zero at 15:29:34 UTC; its current process start time was unavailable. Accordingly, current reuse of a numeric PID is not treated as evidence of a surviving analysis process, and this report does not claim every old numeric PID is absent. See [`cost-provenance-audit/final-process-exit-observation.json`](cost-provenance-audit/final-process-exit-observation.json).

## Public tool-execution observation

Only public stdout event/item **type labels** and file hashes were inventoried. There are 12 `agent_message` items and no other item types: no command-execution, tool-call, MCP, web-search or other unexpected tool item is present. The event inventory contains 12 each of thread-started, turn-started, item-completed and turn-completed, plus five error notices; there are no malformed lines. This establishes no tool execution visible in these public events, not visibility into unreported provider-internal activity. No private session or reasoning text was read for this inspection. Evidence: [`cost-provenance-audit/final-public-event-types.json`](cost-provenance-audit/final-public-event-types.json).
