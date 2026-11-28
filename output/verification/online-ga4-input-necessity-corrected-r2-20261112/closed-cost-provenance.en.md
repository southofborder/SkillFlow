# GA4 replacement-run cost, timing and provenance

Run `document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209` closed **partial**, with diagnostic propagation/DOE and an unavailable source review. The sole zero-call replay **matched**. Independent public-record and byte-provenance audit status is **`verified`**, with no discrepancies or warnings. Audit success does not upgrade the partial semantic result or establish complete source coverage.

## Actual requests and public usage

There were **nine PID-confirmed native analysis starts**: **six normal requests and three structural corrections**. All nine have confirmed process exits, accepted public answers and complete public usage counters. There were **zero outer transport retry launches, zero semantic repair requests, zero unknown native starts and zero missing final-response usage records**. A complete public answer is not evidence that its semantic content was accepted; graph, processing and sensitivity each needed a structural correction.

Known public usage is **1,641,287 tokens = 1,368,077 input + 273,210 output**. Cached input **376,320** and reasoning output **19,029** are subsets already included in those totals. The normal requests account for 977,247 tokens; corrections account for 664,040. All reported cache-write counters are zero.

| Request | Category | PID | Process seconds | Known public tokens |
|---|---|---:|---:|---:|
| Flow | Normal | 24140 | 136.609 | 83,191 |
| Task | Normal | 20716 | 500.055 | 96,781 |
| Graph | Normal | 22604 | 2,023.705 | 126,169 |
| Graph correction | Structural | 11520 | 996.328 | 162,451 |
| Processing | Normal | 24376 | 1,646.861 | 215,784 |
| Processing correction | Structural | 10412 | 1,981.767 | 294,785 |
| Sensitivity | Normal | 5244 | 318.947 | 215,852 |
| Sensitivity correction | Structural | 20572 | 55.243 | 206,804 |
| Task correspondence | Normal | 20700 | 620.550 | 239,470 |

The seven-normal-request policy remained unchanged, but the seventh normal stage, source review, was **rejected before native launch**. Its prepared delivery had **1,079,505 Unicode code points**, exceeding the **1,048,576** limit by **30,929**. Independent inspection confirmed the delivery length and prompt hashes, and found no native-start marker in that request directory. It is one rejected logical request, **not a tenth model call or an unknown model-usage request**. Including it gives ten distinct transport-level logical requests: nine launched plus one rejected. The audit's `logical_requests=9` counter refers to the native-backed request inventory; the supplemental rejection receipt makes the broader denominator explicit.

No new metadata-only CLI invocations were made for this replacement. The three local `--help`/`--version` invocations belonged to the interrupted predecessor's prelaunch.

Public counters do not establish a complete provider bill. Internal HTTP-attempt counts, any unreported internal-attempt usage and currency billing remain unavailable even though all nine final-response usage records are present.

## Timing, transport events and replay

The actual controller PID was **10860**, started through wrapper PID **19396** at **18:32:30.258 China time on 2026-11-12**. Analysis ended at **20:41:18.273**, after **7,728.016 seconds** (2 h 8 min 48.016 s). The controller closed at **20:47:18.443**, giving a marker-to-marker interval of **8,088.185 seconds** (2 h 14 min 48.185 s), including replay and controller overhead.

Native requests span **7,440.376 seconds** from earliest start to latest recorded finish. Their process durations sum to **8,280.065 seconds**; the two workers overlap, so this sum must not be added to controller wall time. Passive component timings separately record propagation compute 7.313 s, propagation total 128.575 s, DOE compute 76.777 s and DOE total 98.943 s. These intervals are nested and must not be summed as independent work; they describe diagnostic computation, not semantic completeness.

Internal network symptoms were observed, despite all nine requests eventually producing complete answers:

- The original graph request logged one stderr sampling retry after the server closed the WebSocket before `response.completed`.
- Processing correction logged two stderr sampling retries: one remote connection reset (OS error 10054), then one request timeout.
- Its stdout also contained one `Reconnecting... 2/5 (request timed out)` notice.

Thus the final inventory contains **three stderr sampling-retry lines and one stdout reconnect notice**, with **zero connection-wait backoff lines**. The stdout notice overlaps stderr activity; do not add these layers or convert their ordinals into provider HTTP attempts or extra native starts. All outer attempts remained `attempt-001`.

There were also **99 auxiliary CLI error/warning lines**, classified separately: 64 model-list refresh errors, 17 MCP startup errors, 9 MCP startup-reconnect errors and 9 MCP shutdown-initialization errors. These do not independently establish failed analysis requests or additional model calls.

The sole replay started at **20:41:19.283**, took **359.279 seconds**, and returned `matched` with **zero new native starts**. Independent timestamp inspection found no request-start marker at or after the replay boundary. This verifies deterministic reconstruction of the recorded partial result, not successful source review or semantic equivalence.

## Frozen identity

The independent audit checked **198 pinned files** and all **16 frozen GA4 source files**. Current and archived implementation, transport and renderer bytes match, as do the staged source package, controller/timing helper hashes and native executables. The controller's own `implementation-check.json` also reports unchanged.

- Corrected implementation SHA: `796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa`.
- Source SHA: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
- Native CLI SHA: `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f`.

The CLI is the updated installation recorded before the first November 12 attempt; it differs from the November 11 native executable. The replacement used the same corrected implementation, source and CLI as its interrupted predecessor, without importing predecessor answers or generated materials.

## Separate predecessor cost

The interrupted `174538` run remains a separate user-cancelled attempt: **four native starts, 306,246 known public tokens and one unknown-usage request**, with no replay. Those values are excluded from the replacement totals above. Across the two November 12 attempts only, the arithmetic total is **13 starts and 1,947,533 known public tokens, plus the predecessor's unknown usage**. This combined accounting is not the cost or outcome of the replacement alone.

The predecessor report remains at `../online-ga4-input-necessity-corrected-20261112/aborted-cost-provenance.en.md`; neither its raw `running` result nor its cancellation was relabeled.

## Evidence

- `cost-provenance-audit/ga4-20261112T124850198832Z.json`: final independent request, public-cost, timing, replay and provenance audit, including exact reconnect/auxiliary lines and hashes.
- `cost-provenance-audit/review-input-rejection-audit.json`: independent delivery-length, prompt-binding and zero-native-start check for the rejected review.
- Run `metrics.json`, `controller-started.json`, `analysis-finished.json`, `controller-finished.json`, `component-timing.json`, `replay-started.json`, `replay-check.json` and `implementation-check.json`: original controller evidence.
- `cost-audit-tests.log`: eleven passing synthetic audit checks; this is helper validation, not another analysis run.

The audit read public records and file bytes only. It made no model calls, executed no Skill, resumed no processes, and performed no extra replay.
