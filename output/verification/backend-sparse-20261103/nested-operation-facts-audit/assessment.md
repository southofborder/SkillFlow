# Nested receiver operation-facts difference

The fixed tiny nested-receiver fixture preserves the same operation alternatives and Data relationships under the frozen baseline and frozen current-r2 implementations. The raw operation-facts hash differs because **the two complete alternatives of `ir_rows` are serialized in the opposite order**. This audit found no added, removed or changed alternative, no changed pairing, and no other operation-fact difference. This is a representation-order difference in this fixture, not evidence of a semantic regression.

## Exact difference and equality scope

`diff.json` records six positional leaf differences, all under `/ir_rows/events/0/atomic_ops/0/alternatives`. The whole rows are swapped: each row's member-occurrence binding, single input identity and single output identity stay together. `normalized-diff.json` verifies that reversing **only that one list** makes the entire current operation-facts object exactly equal to baseline.

| Member occurrence | Baseline alternative index | Current alternative index | Input Data ID prefix | Output Data ID prefix |
| --- | ---: | ---: | --- | --- |
| 0 | 0 | 1 | `data_cfbf4048` | `data_1479b3ad` |
| 1 | 1 | 0 | `data_c18b186f` | `data_3329110d` |

Full identities and whole exported alternatives remain in `baseline.json`, `current-r2.json` and the JSON differences. All 23 serialized Data records are equal. All 13 IR coverage entries are equal and processed. The exact four send pairs remain `(A, a0)`, `(A, a1)`, `(B, b0)`, `(B, b1)`, with four alternatives. Every event, atomic-operation position, input/output slot position, member relation, `order` field and `precedence` field is unchanged.

| Hash scope | SHA-256 |
| --- | --- |
| Raw baseline operation facts | `97ea9a1677f33954560f39cd9869ba7cf09cad8275552ff3828a9f1071915f26` |
| Raw current-r2 operation facts | `d450a0cfefbd204e1d63d2ccdc9232f9e0e73193e4e7e57daf1ddd1a05b88071` |
| Both operation-facts objects, sorting complete alternative rows only | `98615db84dbcbbb10e24a85c5e4b89553e1bab4efbbb3b538f7689d9fe1c3bfd` |
| Both complete Data snapshots | `ed665173573e8d5783e6b3884d56e706fb91e354e6efc6e878ff441d21930ce4` |

The normalized comparison sorts each complete `alternatives` array by canonical JSON. It does not deduplicate alternatives or sort any other list, so it cannot hide changed slot order, execution/event order, missing duplicates, or broken input/output/binding association. The stronger single-list-reversal comparison does not need normalization elsewhere.

## Source cause and alternative-order meaning

The baseline frozen source is `experiments/doe/runs/document-guided-ga4-alignment-high-v9-20261102-214514/implementation-snapshot/src`; the compared current source is `output/verification/backend-sparse-20261103/implementation-current-r2/src`. Export workers verified each complete source identity against its original three-sample receipt before computing the tiny fixture.

In the baseline `skillflow/propagation/interpreter.py:743-749`, `_merge_operations` always serializes and hash-sorts its alternatives, even for a single operation variant. The current-r2 implementation at `interpreter.py:849-851` returns a single variant directly. Current `_tuples` emits candidates by sorted Data identity at `interpreter.py:313-317`; `evaluate` passes the operation through `_merge_operations` at `interpreter.py:929-930`. The old list is ordered by alternative hashes `508499fe...`, `fdb1530a...`; the new list is ordered by input IDs `data_c18b...`, `data_cfbf...`. These are the exact opposite orders recorded in the JSON audit.

The complete alternatives represent paired candidate relations, rather than an execution sequence. This follows from the existing merge behavior itself, which sorts/deduplicates alternatives by their whole-content hashes, independently of control or occurrence order. The current-r2 model at `models.py:182-197` preserves input/output slot order inside each candidate; `models.py:218-231` validates each candidate and their output union. Actual IR order and precedence are separate fields. Relevant consumers also use candidate membership rather than alternative position: `solver.py:84-94` selects compatible routes, `doe/material.py:80-89` compares request alternatives as sets of paired input/binding hashes, and `doe/sensitivity_engine.py:360-362` checks whether any candidate preserves the source/output pair. None of those relationships changes when these two whole alternatives swap.

## Determinism check and limits

Two additional **untimed** current-r2 evaluations used separate processes with `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2`. Both produced the exact same raw operation-facts object and Data snapshot as the original untimed current-r2 export, including the raw `d450a0...` hash. `hash-seed-check.json` records those comparisons and confirms that the original current timing receipt is unchanged. Each untimed export also reproduced all three original corresponding receipt hashes and recorded the original receipt file hash. This is specific evidence for this fixture and these seeds; it is not an exhaustive proof of replay determinism.

The raw baseline/current hashes should remain reported as different. Semantic equality after the stated candidate-row normalization does not make cross-version serialized artifacts identical. The unchanged current raw hashes across these processes reveal no concrete instability requiring a production change.

Only the already frozen small nested-receiver input was evaluated. No timed sample, full GA4 computation, DOE computation, historical run/replay, model call, Skill execution, or production edit was performed. The original three-sample receipts were read only. The initial baseline audit export failed after propagation because the audit compared Python tuple pairs with their JSON array representation; `initial-export-failure.json` preserves that audit-only mistake. After correcting the comparison to canonical JSON, the baseline export succeeded. Total additional tiny evaluations were two baseline attempts (one audit-export failure and one successful export) and three current-r2 attempts (initial export, seed 1, seed 2), all untimed. The initial export script did not record its inherited hash-seed setting; the two explicit-seed exports do.
