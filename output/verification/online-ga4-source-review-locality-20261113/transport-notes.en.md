# Provisional public transport observations

These observations concern only the single fresh source-review-locality GA4 run. They read saved public CLI stderr and stdout event types; no private session, model probe, new analysis request or process-control action was used. Counts remain provisional while the controller runs.

| Stage | UTC timestamp | Public observation |
| --- | --- | --- |
| task | 2026-11-13 12:39:39.737287 | Internal sampling retry 1/5: stream disconnected with IO error 10054 (connection reset). |
| flow | 2026-11-13 12:39:39.747136 | Internal sampling retry 1/5: stream disconnected with IO error 10054. |
| flow | 2026-11-13 12:39:54.979850 | Internal sampling retry 2/5: request timed out. |
| task | 2026-11-13 12:39:54.980180 | Internal sampling retry 2/5: request timed out. |
| graph | 2026-11-13 12:58:47.351506 | Internal sampling retry 1/5: websocket closed by server before response.completed; reported backoff 211 ms. |

Task and flow later completed. Their public usage totals are 97687 and 85031 tokens respectively; these counters do not establish additional unreported provider-internal retry usage. At 13:01:31 UTC, graph had been running for approximately 1155.98 seconds since its native start at 12:42:15.273412. It had no process completion or final-usage receipt. Its public stdout contained only thread.started and turn.started event types (101 bytes), so the public records cannot prove continuous generation or identify where internal computation was spent.

The graph server-close notice occurred approximately 16 minutes 32 seconds after its native start. It is concrete evidence of an interrupted response stream during the long stage, not evidence that the entire duration was network waiting. It is distinct from a connection-establishment timeout and from the adapter's 2700-second native-process timeout. The initial two request-timeout notices are also CLI-internal notices, not native-process timeout receipts.

At the referenced snapshot there are three confirmed native starts, zero outer retry starts, zero structural corrections and zero semantic repair starts. Internal retry notices, stdout reconnect notices and stderr lines overlap; they must not be added as distinct HTTP requests or token costs. Underlying HTTP-attempt counts and unreported usage remain unknown.

Evidence: `cost-provenance-audit/ga4-20261113T130121623221Z.json` and `cost-provenance-audit/public-surface-20261113T130121726210Z.json`. Both preserve file hashes and public line coordinates while omitting raw session identifiers. This note is a provisional observation, not a final run assessment.
