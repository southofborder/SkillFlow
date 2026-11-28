# GA4 interrupted-run cost and provenance

Run `document-guided-ga4-input-necessity-corrected-high-20261112-174538` was **aborted by the user after a reported network outage**, with the controller tree confirmed stopped at **18:31:00.391 China time on 2026-11-12**. This is not a recorded 45-minute native timeout or a normally completed failed analysis. The original `result.json` remains `running`, with Task and flow complete and graph generation unfinished; it was not rewritten. No replay was started because the user cancelled this run.

The actual controller was PID **10492**, launched through Python wrapper PID **15096**. The interrupted native request was PID **16232**. The stop receipt records zero remaining recorded processes; an independent read-only process inventory at **18:32:06.104 China time** also found none of these three PIDs. The two Python PIDs represent wrapper and child, not duplicate analysis controllers.

## Public cost

There were **four PID-confirmed native analysis starts**: three normal requests and one graph structural-correction request. All used `attempt-001`; there were **zero outer transport retry launches** and no shared semantic repair requests. Three requests returned complete public answers and usage counters. A completed answer does not establish that its semantic or structural content was accepted; the original graph response required correction.

Known public usage totals **306,246 tokens**, comprising **241,686 input + 64,560 output**. Cached input **32,512** and reasoning output **13,997** are subsets already included in those totals. The interrupted correction reported neither a complete answer nor public usage. Its token consumption remains **unknown, not zero**. Provider-internal HTTP attempts, unreported internal-attempt usage and currency billing are unavailable.

| Request | Category | PID | Recorded process seconds | Known public tokens |
|---|---|---:|---:|---:|
| Flow | Normal | 1224 | 137.955 | 83,355 |
| Task | Normal | 8084 | 485.397 | 96,256 |
| Graph | Normal | 10876 | 1,065.768 | 126,635 |
| Graph correction | Structural correction | 16232 | Unknown; no process-exit receipt | Unknown |

Three local metadata-only CLI invocations preceded the run: root ran `exec --help`, and the independent prelaunch auditor ran `--version` and `exec --help`. These made zero model calls and are separate from the four analysis starts.

## Timing and network observations

The controller started at **17:46:35.778**. The observed interval to confirmed operator stop is **2,664.614 seconds** (44 min 24.614 s). The graph correction started at **18:06:43.382**; its observed interval to confirmed stop is **1,457.009 seconds** (24 min 17.009 s). This interval is not a fabricated native process-duration receipt, and it is below the unchanged 2,700-second per-request limit. No final controller analysis-duration receipt was published. The three available process durations sum to 1,689.119 seconds; overlapping workers mean that sum is not controller wall time.

The interrupted correction contains:

- **Five stderr sampling-retry lines**, reporting stream disconnection and OS error 10054.
- **Seven stderr connection-wait lines**, with 5/10/20/40/60-second backoff settings, including repeated 60-second waits.
- **Eleven stdout reconnect notices**: four ordinal sampling-reconnect notices and seven waiting-for-network notices.

These stdout and stderr layers overlap. They must not be added together or interpreted as additional native starts, an exact provider HTTP-attempt count, or additional known token usage. Both exact inventories and line positions are preserved in the audit JSON.

Separately, stderr contains **41 auxiliary CLI error/warning lines**: 26 available-model refresh errors, 8 MCP startup errors, 4 MCP startup-reconnect errors and 3 MCP shutdown-initialization errors. Such auxiliary timeouts occurred even in requests that completed. They do not independently establish a failed model request or an extra model invocation.

## Frozen provenance and evidence limits

The audit checked **198 pinned files** covering implementation, transport and renderer; current and archived bytes match. The 16 frozen GA4 source files and newly staged source files also match. Controller and timing helper hashes, renderer and native CLI hashes match their prepared protocol.

- Corrected implementation SHA: `796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa`.
- Source SHA: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
- Native CLI SHA: `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f`.

The installed CLI had updated since the November 11 run; the original and current identities remain explicit in `run-protocol.json`. This interruption establishes neither successful propagation/DOE nor semantic adequacy of the corrected implementation. Its cost must remain separate from any newly authorized replacement run.

The final independent audit status is **`verified_with_usage_limitations`**, with no audit discrepancies. Expected limitations are the missing process-exit/usage receipt for the interrupted request and absence of final metrics after cancellation. No normal controller-finished receipt or zero-call replay is claimed.

Evidence:

- `cost-provenance-audit/ga4-20261112T103306940146Z.json`: final public-cost, source and byte-provenance audit.
- `cost-provenance-audit/operator-process-observation.json`: independent zero-process observation.
- Run `operator-stop-confirmed.json`: operator cancellation, recorded PIDs and stop time.
- `cost-audit-aborted-run-tests.log`: eleven passing synthetic checks, extended to require explicit cancellation plus independent process closure, preserve raw `running` status and keep incomplete usage unknown.

All raw source, prompts, responses, failures, request logs and unfinished run records remain preserved. The audit did not call models, execute the Skill, resume a process or replay this run.
