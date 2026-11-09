# Final saved-receipt cross-check

Status: **passed; no numerical discrepancy or concrete 010 reporting overclaim found**.

Scope: the four exact `document-guided-{ga4,001,010,013}-backend-r3-high-20261104-132226` runs. This audit reads saved JSON/text and hashes files. It imports no production code, invokes no transport metrics collector, and performs no replay, model call, Skill execution, or process inspection. Original artifacts remain unchanged. Detailed request identities, raw-event hashes, usage, group totals, and checks are in `receipt.json`; the independent standard-library script is `verify_saved_receipts.py`.

| Case | Native starts / unique public identities | Normal / correction / repair requests | Input | Cached input | Output | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GA4 | 5 / 5 | 4 / 1 / 0 | 459,522 | 61,440 | 102,863 | 562,385 |
| 001 | 14 / 14 | 7 / 2 / 5 | 338,323 | 172,032 | 36,431 | 374,754 |
| 010 | 9 / 9 | 7 / 2 / 0 | 197,845 | 110,592 | 19,287 | 217,132 |
| 013 | 9 / 9 | 7 / 2 / 0 | 226,576 | 106,368 | 28,752 | 255,328 |
| Batch | **37 / 37** | **25 / 7 / 5** | **1,222,266** | **450,432** | **187,333** | **1,409,599** |

Each native request directory has matching start and PID evidence plus an exited process receipt. Each raw public stream has one thread start, one turn start, one substantive final, and one turn completion; the final matches the saved last message. All 37 thread/turn-or-order identities are globally unique. Public turn IDs are absent, so these identities use the exposed thread ID and turn order 0. Raw completion usage agrees with sidecars, per-request metrics, aggregate metrics, and all four published summaries/group tables. Cached input is a subset of input; reasoning output totals 39,910 and is a subset of output. Neither is added again to the total.

All saved public final-turn usage is complete: zero partial/unknown final-usage requests, zero unknown native starts, and zero outer retries. This does not imply no internal retries. Raw streams contain nine CLI reconnect notices: three for GA4 flow and six for 001 (Task one, sensitivity three, correspondence two). Notice counts do not determine provider HTTP attempt counts or extra billed usage. Provider attempts and any usage not exposed by public counters remain unknown.

Each sole replay receipt says `matched` with zero new native-start markers, agrees with its controller closure receipt, and the currently saved native starts all precede analysis closure. This audit did not rerun replay. All 189 pinned files per run match both the frozen snapshot and current workspace; the 186-file implementation manifest agrees with the snapshot subset. Archived controller/timing hashes also agree. The implementation SHA remains `9ae31392bf97b0ae8c5ae75c48d1994e8b303b68cda6d532eb4b96f508c56703`.

001's cost table names the five-request repair group `semantic_repair`, while logical categories call it `semantic_repair_generation`. These are label aliases with identical numerical counters, not a discrepancy.

The separate 010 prose/summary review found no concrete overclaim. Its report distinguishes 21/21 generated IR from source coverage, scopes the four inspected source relationships and unresolved return recipient, retains correspondence/DOE limitations, and does not interpret zero sensitive comparisons as safety. Its historical cost comparison is explicitly a sample comparison with different generated work, not an equal-work backend speedup or broad accuracy claim.
