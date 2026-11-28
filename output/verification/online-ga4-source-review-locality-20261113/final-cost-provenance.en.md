# Final passive cost and provenance audit

The sole fresh GA4 controller is closed with status **failed**. Revision-processing reached the unchanged **2,700-second native-process deadline** after public connection interruptions. The initial source review and its structural correction both reached native execution below the unchanged input limit. This audit establishes execution, available public cost, delivery sizes and provenance; it does not establish semantic analysis success.

Run: `experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902`.

The final passive snapshot is [ga4-20261113T162801663200Z.json](cost-provenance-audit/ga4-20261113T162801663200Z.json), observed at 2026-11-13 16:28:01 UTC. Its status is `verified_with_usage_limitations`, `final_observation` is true, and its issues and warnings are empty. All earlier snapshots remain preserved. Public event-type evidence is [public-surface-20261113T162801814511Z.json](cost-provenance-audit/public-surface-20261113T162801814511Z.json).

## Closure and counted requests

Main analysis started at 2026-11-13 12:39:17.144779 UTC and finished at 16:26:00.813238 UTC: **13,603.668426 seconds**. The controller finished at **16:27:01.947083 UTC**, equivalent to 2026-11-14 00:27:01.947083 China time. The one controller-owned replay matched in **60.492410 seconds**, with **zero new native markers**. Replay reproduced the saved failed outcome; it did not turn the run into a successful analysis.

There were **15 PID-confirmed native starts**, consisting of **7 normal requests, 5 structural corrections and 3 requests within one shared semantic repair round**. Outer transport retries were **0**. There were no unconfirmed launch attempts, unknown native starts or inputs rejected before native start. The three repair requests were revision Task, revision graph and revision processing; they are not three repair rounds. No revision review was launched after revision processing failed.

An independent read-only Windows process observation at 16:27:59.4524148 UTC found **none** of the recorded controller, wrapper or 15 native PIDs still present. See [operator-process-observation.json](cost-provenance-audit/operator-process-observation.json). No process-control action was performed by this passive audit.

## Available public cost

**14 requests have complete public final-response usage; 1 request has no public usage.** The known total is **2,862,874 tokens**, comprising **2,433,001 input tokens** and **429,873 output tokens**. The input counters include **555,520 cached input tokens**; output counters include **33,994 reasoning output tokens**. These subset counters must not be added to the total again. Reported cache-write input tokens are 0. No partial-usage counter was available for the failed request.

| Request category | Confirmed starts | Complete public usage receipts | Known public tokens |
| --- | ---: | ---: | ---: |
| Normal | 7 | 7 | 1,314,586 |
| Structural correction | 5 | 5 | 1,248,364 |
| Shared semantic repair | 3 | 2 | 299,924 |
| Outer retry | 0 | 0 | 0 |
| Total | 15 | 14 | 2,862,874 |

Revision-processing usage remains **unknown, not zero**. Internal provider/CLI retry activity may also have unreported usage beyond final-response receipts. Public notices do not establish HTTP-attempt counts or the complete provider bill, so monetary cost and total provider consumption remain unknown.

The requested configuration was `gpt-6.1-sol`, effort `high`, provider `openai`. No actual returned-model metadata was exposed in the saved public events. Request configuration is not evidence of an independently reported actual model.

## Native stage durations and complete public usage

All times below are UTC on 2026-11-13. Durations are the saved native-process measurements, not model-only generation time. Parallel request durations overlap and must not be summed as wall-clock analysis time. Each row is one actual native process; `a002` denotes the existing structural correction.

| Stage | Category | Start | Finish | Seconds | Input tokens | Output tokens | Total tokens |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| Flow a001 | Normal | 12:39:18.398277 | 12:42:14.457612 | 176.059 | 79,799 | 5,232 | 85,031 |
| Task a001 | Normal | 12:39:18.560503 | 12:47:45.741507 | 507.180 | 79,067 | 18,620 | 97,687 |
| Graph a001 | Normal | 12:42:15.273412 | 13:19:34.742852 | 2,239.469 | 86,392 | 49,684 | 136,076 |
| Graph a002 | Correction | 13:19:37.730571 | 13:38:08.197147 | 1,110.466 | 132,585 | 44,102 | 176,687 |
| Processing a001 | Normal | 13:38:15.291502 | 14:04:19.408509 | 1,564.117 | 161,172 | 62,249 | 223,421 |
| Processing a002 | Correction | 14:04:21.164172 | 14:32:20.167151 | 1,679.002 | 227,128 | 66,789 | 293,917 |
| Sensitivity a001 | Normal | 14:32:25.878686 | 14:42:05.580875 | 579.702 | 204,578 | 9,137 | 213,715 |
| Task-correspondence a001 | Normal | 14:32:25.878734 | 14:41:01.762858 | 515.884 | 215,674 | 20,121 | 235,795 |
| Task-correspondence a002 | Correction | 14:41:05.027535 | 14:41:41.985777 | 36.958 | 216,166 | 1,085 | 217,251 |
| Sensitivity a002 | Correction | 14:42:08.260162 | 14:42:45.683906 | 37.423 | 204,865 | 953 | 205,818 |
| Review a001 | Normal | 14:43:07.808180 | 15:02:21.078002 | 1,153.269 | 277,022 | 45,839 | 322,861 |
| Review a002 | Correction | 15:02:25.069396 | 15:19:46.449492 | 1,041.380 | 313,365 | 41,326 | 354,691 |
| Revision graph a001 | Repair | 15:19:52.653053 | 15:40:51.157809 | 1,258.504 | 148,430 | 50,022 | 198,452 |
| Revision Task a001 | Repair | 15:19:52.653624 | 15:26:08.614743 | 375.961 | 86,758 | 14,714 | 101,472 |
| Revision processing a001 | Repair | 15:41:00.352228 | 16:26:00.385522 | 2,700.032 | Unknown | Unknown | Unknown |

The first 14 rows have exit-confirmed successful native exits and complete accepted-final usage receipts. The last row has `process_status=timeout`, `returncode=1`, `exit_confirmed=true`, elapsed **2700.03195959999 seconds**, no accepted answer and unknown public usage. Native success does not imply successful structural or semantic validation of an answer.

## Internal transport events and the terminal timeout

There are **9 saved sampling-retry stderr lines** and **4 public stdout reconnect notices**. These surfaces overlap and must not be added together as independent requests. The 9 stderr lines classify as 3 connection resets, 3 request timeouts, 2 server websocket closures and 1 TLS EOF. There are no explicit connection-wait log lines and no outer retry native starts. Fourteen auxiliary model-list refresh lines are separate auxiliary activity, not additional semantic requests.

| Time UTC | Stage | Internal retry | Saved public cause |
| --- | --- | ---: | --- |
| 12:39:39.737287 | Task a001 | 1/5 | I/O error 10054; connection forcibly closed/reset |
| 12:39:39.747136 | Flow a001 | 1/5 | I/O error 10054; connection forcibly closed/reset |
| 12:39:54.979850 | Flow a001 | 2/5 | Request timed out |
| 12:39:54.980180 | Task a001 | 2/5 | Request timed out |
| 12:58:47.351506 | Graph a001 | 1/5 | Server closed websocket before response completion |
| 14:38:12.269375 | Sensitivity a001 | 1/5 | Peer closed connection without TLS close-notify; unexpected EOF |
| 16:05:29.802676 | Revision processing a001 | 1/5 | Server closed websocket before response completion |
| 16:09:39.612725 | Revision processing a001 | 2/5 | I/O error 10054; connection forcibly closed/reset |
| 16:09:54.995480 | Revision processing a001 | 3/5 | Request timed out |

Task, Flow, initial Graph and Sensitivity subsequently returned accepted native answers. Revision-processing did not: it remained within the same native attempt and reached the adapter's full **45-minute process deadline** at 16:26:00 UTC. Thus the terminal failure is a **native request/process timeout**, with preceding connection interruptions and an internal request-timeout notice. It is not accurately described as only a connection-establishment timeout. The public evidence cannot apportion the 45 minutes between generation, retries and waiting, or prove that network events alone caused the terminal deadline.

Raw public stderr/receipt hashes and bounded event classifications remain in the JSON audit. No raw session identifiers, credentials, private sessions or reasoning bodies are reproduced here.

## Complete review deliveries

Sizes were measured from the actual persisted complete deliveries, including the transport envelope. No prompt was re-rendered or sent by this audit. The adapter's metric is Unicode codepoints and its unchanged limit is **1,048,576**.

| Delivery | Core codepoints | Envelope | Complete delivery | UTF-8 bytes | Remaining codepoints |
| --- | ---: | ---: | ---: | ---: | ---: |
| Review a001 | 864,735 | 212 | 864,947 | 865,160 | 183,629 |
| Review a002 correction | 987,886 | 212 | 988,098 | 988,311 | 60,478 |

Both deliveries matched their saved request hashes, were within the limit, started one confirmed native process each, and recorded an accepted native answer. There was no input-size prestart rejection in this run. This evidence covers both actual review deliveries; it makes no claim about a revision review that was never launched.

Delivery SHA-256 values:

- Review a001: `4de9be8545c20500c820fdc819bfdb1e0c90adf7e6f6cc76b79810918595ca08`.
- Review a002: `d3699185790cbf10c446bb3d3b6ea67d9a4f2b698ad00ef9eedec3dfa6141dea`.

## Freeze and public execution surface

The final audit checked all **202 pinned implementation/protocol files** and the **16 complete source files**. Frozen changes, current changes, unpinned current files, source changes and staged-source changes are all empty. The controller and timing helpers match their prepared hashes; CLI, renderer and Python executable checks all match. No historical answers or source-donor content were read by this audit.

- Implementation SHA-256: `ae3df129739a9471521b8b19be65faa8e085f1e92efcacaac1e0c5e3d42f3cbb`.
- Source SHA-256: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
- Pinned snapshot SHA-256: `7a9f8c8ef8be88bd952fd158207190b47496e8d1f08350105e123b6806e4bfe9`.
- CLI executable SHA-256: `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f`.
- Prepared-run SHA-256: `40a27a302497b9b5b6bf996790d49f50f06563b6a8e5cb5fd5fcb5ad57ece320`.
- Passive cost auditor SHA-256: `c995082a3bf066d6ea4634a7f01c03d8b86a2e7093e8a28caf7b0589b7b54392`.
- Public-surface auditor SHA-256: `e2c5440b57b97a7d1c2631f70b1711245aef102511ab6dea72a37870981e4e6a`.

The public-surface audit inspected saved event types and completed-item type tags, without opening item bodies or private sessions. It found **no completed tool/command or other unexpected item types** (`other_completed_item_types={}`). This is evidence about the visible public event inventory, not a claim of visibility into unreported provider-internal behavior.

This final audit only read the new run's saved public artifacts, checked local provenance/process presence, and wrote verification evidence outside the run. It did not launch a model, execute a Skill, replay an analysis, run backend analysis, probe a service, modify frozen files, or alter historical evidence.
