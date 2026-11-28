# Saved transport retry evidence

This note inspects only the two saved stderr sampling-retry events identified by the passive snapshot `cost-provenance-audit/ga4-20261112T144459676938Z.json`. It does not start an audit loop, process, model request, probe, analysis or replay. Public identifiers and the explanatory URL are redacted below.

The initial graph request experienced a transport interruption and an internal CLI sampling retry. The saved cause is a server-closed WebSocket before the response-completed event, not a recorded connection timeout. The task request separately experienced a peer closing its TLS connection without a close-notify message. These events establish interrupted streams and internal retries; they do not establish the root network cause or quantify how much of the elapsed time they added.

| Stage / request | Event time UTC | China time | Saved event | Advertised retry delay |
| --- | --- | --- | --- | --- |
| Graph, normal `a001`, native `attempt-001` | 2026-11-12 14:28:15.879658 | 22:28:15.879658 | `websocket closed by server before response.completed` | 180 ms |
| Task, normal `a001`, native `attempt-001` | 2026-11-12 14:21:54.176516 | 22:21:54.176516 | `peer closed connection without sending TLS close_notify` | 186 ms |

Both lines say `stream disconnected - retrying sampling request (1/5 ...)`, with `retries=1` and `max_retries=5`. These are CLI-internal labels within the existing native process. The ordinals are not an independently measured HTTP-attempt count, and the advertised delays are not total reconnection or recomputation durations.

The graph process ran from 14:16:03.979453 to 14:43:28.565341 UTC, with a recorded duration of 1,644.585311 seconds (27 minutes 24.6 seconds). Its interruption was logged about 12 minutes 11.9 seconds after native start; the saved finish followed about 15 minutes 12.7 seconds after the warning. Thus a transport retry was part of this long graph request. The public records cannot separate model generation time, connection handling and any repeated generation, so attributing the full 27 minutes to the network would be unsupported.

The task process ran from 14:13:22.552555 to 14:27:17.510319 UTC, with a recorded duration of 834.957263 seconds (13 minutes 55.0 seconds). Its interruption was logged about 8 minutes 31.6 seconds after start; the saved finish followed about 5 minutes 23.3 seconds later.

At the cited snapshot there were three normal native starts and one graph structural-correction start. There were zero recorded outer network-retry attempts, zero stderr connection-wait lines, and zero stdout reconnect/error notices classified by the passive auditor. The graph structural correction began at 14:43:30.496119 UTC (22:43:30.496119 China time); it is a separate deterministic representation-correction request, not the outer network retry for the earlier stream closure. Neither cited warning reports a timeout, and neither completed normal request hit the 2,700-second native timeout.

Exact saved excerpts, with identifiers redacted:

```text
2026-11-12T14:28:15.879658Z WARN codex_core::responses_retry: stream disconnected - retrying sampling request (1/5 in 180ms)... turn_id=[IDENTIFIER REDACTED] retries=1 max_retries=5 sampling_error=stream disconnected before completion: websocket closed by server before response.completed
2026-11-12T14:21:54.176516Z WARN codex_core::responses_retry: stream disconnected - retrying sampling request (1/5 in 186ms)... turn_id=[IDENTIFIER REDACTED] retries=1 max_retries=5 sampling_error=stream disconnected before completion: IO error: peer closed connection without sending TLS close_notify: [URL REDACTED]
```

Evidence locations relative to the sole new run `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242`:

- Graph: `transport/graph/38bb1c0deb7a6ebcc944c7d167e0f4bd77ec9a250f41c7558a1ea98e7143c8ed/attempt-001/stderr.txt`, line 5. Saved message digest: `5b1b4cae39cfd78ca053c1eb29879413a7995aeaac6e12d830b9f5bde95642b3`.
- Task: `transport/task/4c6b14bdf05ecb74c07a06dba88cff06305e4c635da036af413d593f6b8acd1a/attempt-001/stderr.txt`, line 4. Saved message digest: `3e450ab883b325333a3efa5ae398138d00e3ff30a9dece2e3d02ee4f1b91daea`.

Public final counters and missing counters remain as reported in the snapshot. Additional usage potentially incurred by unreported internal attempts, provider billing and underlying HTTP-attempt counts remain unknown. These two events do not establish that the user's local network disconnected, that the server alone caused the interruption, or that future requests will fail.
