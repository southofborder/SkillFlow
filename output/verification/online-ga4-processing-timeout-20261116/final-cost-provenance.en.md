# Final public cost, network, timing and frozen provenance

The sole fresh GA4 run closed with failure in **initial processing's structural correction**, before any semantic repair. Processing a002 reached the unchanged 2,700-second native process deadline without a completed answer. This is an observed total process timeout; the public evidence does not establish how much of the delay was generation, network waiting or reconnect work.

The native timeout receipt records `status="timeout"`, `error="CLI process exceeded its timeout"`, `elapsed_seconds=2700.039036100032`, `exited=true` and return code 1, ending at **2026-11-16 16:39:40.596233 UTC / 2026-11-17 00:39:40.596233 China**. The guided reason is `ModelRequestFailure: CLI produced no complete answer; this is not an eligible transient network retry`. No outer retry was started. There is no selected annotation, and `repair_used` is false.

The controller closed at 16:39:48.628006 UTC after its sole zero-call replay **matched in 7.0309 seconds with zero new native start markers**. Recorded analysis time is 6,287.71405 seconds. All six native attempts have confirmed exits. Root's independent observation at 16:40:51.8603396 UTC confirms that all eight recorded wrapper, controller and native process IDs are absent. This audit did not start or trigger replay or perform process control.

## Actual starts and public usage

The policy remains seven normal requests and two workers. The early failure meant **four normal requests actually started**, plus **two structural corrections**, totaling **six native starts**. No semantic repair request or outer retry started. The observed native execution intervals overlap at most twice, consistent with the two-worker policy.

Five completed native deliveries have complete, final-associated public usage receipts. These are **not five accepted semantic stages**. The auditor fields `accepted_answer_present` / `accepted_answer_recorded`, and this summary's `native_answer_available`, refer only to transport delivery acceptance. In particular, processing a001 returned a complete native answer but failed strict JSON validation for `duplicate JSON member: shared_values`. Neither processing answer was structurally or semantically accepted.

| Native request | Elapsed seconds | Public input tokens | Public output tokens | Known total |
|---|---:|---:|---:|---:|
| Flow a001 | 122.099 | 79,797 | 4,528 | 84,325 |
| Task a001 | 521.146 | 79,065 | 20,376 | 99,441 |
| Graph a001 | 985.053 | 86,035 | 38,816 | 124,851 |
| Graph a002 structural correction | 934.197 | 122,282 | 36,961 | 159,243 |
| Processing a001, structurally rejected | 1,535.208 | 141,467 | 60,888 | 202,355 |
| Processing a002 structural correction, native timeout | 2,700.039 | Unknown | Unknown | Unknown |
| **Known public total** | — | **508,646** | **161,569** | **670,215** |

Cached input tokens (39,936) and reasoning output tokens (15,588) are subsets, not additional totals. The timed-out correction has no partial or final public usage receipt. Its provider usage, any internal retry usage, complete provider HTTP-attempt count and provider bill remain unknown. Request durations overlap and must not be added to the controller wall time.

## Public network evidence

All three sampling-retry stderr lines belong to the same processing a002 native attempt:

| UTC timestamp on 2026-11-16 | CLI ordinal | Recorded cause | Seconds since native start | Gap from prior sampling notice | Backoff |
|---|---|---|---:|---:|---:|
| 16:09:40.309444 | 1/5 | Connection reset, OS error 10054 | 899.753114 | — | 196 ms |
| 16:09:55.533043 | 2/5 | Request timed out | 914.976713 | 15.223599 s | 377 ms |
| 16:25:12.304769 | 3/5 | Server closed WebSocket before `response.completed` | 1,831.748439 | 916.771726 s | 802 ms |

The two stdout reconnect notices report ordinals 2/5 and 3/5. They overlap the corresponding stderr records and are not two extra retries or launches. No connection-wait retry lines were recorded. Twelve auxiliary model-list refresh timeout lines are separately inventoried; they are not sampling requests or additional analysis invocations. No other completed public tool/command item type was observed. These statements describe only the visible public inventory.

The approximately 900-second intervals are numerical gaps between recorded events. They do not establish a 900-second idle timeout, a server timeout setting, continuous generation, or network-only causation. The early `request timed out` notice is distinct from the later observed total native process timeout. The record proves that disruptions occurred and that the total budget subsequently expired; it cannot quantify each cause's contribution.

## Input, output and host observations

| Processing request | Complete delivery characters | Complete delivery UTF-8 bytes | Completed final characters | Completed final UTF-8 bytes |
|---|---:|---:|---:|---:|
| a001 | 425,635 | 426,062 | 212,300 | 212,302 |
| a002 structural correction | 675,505 | 675,934 | Not observed | Not observed |

There was no prestart input-size rejection. Processing a001's final message was observed within **15:54:34.524652–15:54:39.376724 UTC**. The a002 stdout errors were observed within **16:09:40.794849–16:10:10.806635 UTC** and **16:25:11.002436–16:25:41.016930 UTC**. Its sidecar contains 91 samples and ends terminal at 2,700.038872 seconds, with 313 stdout bytes, 1,501 stderr bytes and no completed final message.

These are conservative host file-observation intervals. The public interface exposed completed messages and errors, not a demonstrated stream of generated tokens. Time to first token, provider prefill time, actual generation duration and network-wait duration remain unknown. No visible final message is not proof that the provider generated no output.

## Frozen provenance and scope

All **206 pinned implementation files**, **16 complete source files**, controller, timing helper and CLI/Python/renderer executable pins match their frozen identities. There are no changed or unpinned implementation files, source changes, protocol discrepancies or audit warnings in the final v14 snapshot.

- Implementation: `8ed018204232f0fc5ed2a26ae9c86d0d3055b900aee3583b5c8b17723d9316ed`.
- Source: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`; 16 files, 155,170 UTF-8 bytes.
- Requested runtime: `gpt-6.1-sol`, `high`, `openai`; seven normal requests, two workers, one structural correction per stage, one shared semantic repair budget, 2,700-second native timeout and at most two eligible outer transient retries remain unchanged.

The returned model identity is not present in public response metadata and remains unknown; requested configuration is not returned-model evidence. The copied passive auditor's stale v13 assertion was reconciled by creating a new utility with only the expected guided identity changed to v14. The observer pin remains required. The original utility and initial discrepancy snapshot remain intact; no runtime or controller changed.

This audit covered only the sole fresh run and read no private sessions or reasoning bodies. It started no model, Skill, probe, backend computation, historical replay or current replay. The failure/replay receipts do not establish processing semantics, input minimization or DOE findings.

## Evidence

- `final-cost-provenance.json`: complete cost/provenance summary and per-attempt public timing, size and network evidence.
- `final-cost-provenance-closeout.json`: final summary digest, independent process-exit evidence, actual concurrency and transport-versus-semantic acceptance clarification.
- `cost-provenance-audit/ga4-20261116T164009627109Z.json`: final passive audit, `verified_with_usage_limitations`, no issues or warnings.
- `cost-provenance-audit/public-surface-20261116T164008563096Z.json`: final public event and cause inventory.
- `root-process-exit-check.json`: root's independent observation of all eight recorded process IDs absent.
- `passive-audit-v14-reconciliation.json`: exact audit-only identity correction and both utility digests.
- Run-local `controller-finished.json`, `replay-check.json`, `analysis-finished.json`, processing attempt `process.json`, public stdout/stderr and `public-observations.jsonl`: original terminal and timing records.
