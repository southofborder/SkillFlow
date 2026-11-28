# GA4: strict review locality, closed run

The general implementation and scoped offline acceptance are complete. This one
fresh GA4 demonstrates lossless review delivery, strict local isolation and
actual repair routing. **The overall run failed during revision-processing at
the configured 2700-second native-process deadline. Propagation and DOE did not
run.** The controller's sole zero-call replay matched; the accepted implementation
remained unchanged. No additional run or replay was started.

## Implementation and offline evidence

Accepted implementation: `ae3df129739a9471521b8b19be65faa8e085f1e92efcacaac1e0c5e3d42f3cbb`.
There are **886 distinct current scoped tests with latest passing evidence**,
zero skips and zero unresolved failures. This is not one all-green repository
execution or one all-green scoped execution: the final broad run had 885 passes
and one documentation-inventory test failure; its test-only correction was
followed by 24 targeted passes, without changing production. All failures and
corrective receipts remain in `../source-review-locality-20261113/`.

The previous three missing-field records failed sequential hidden invariants:
the first reply used an absent-argument locator for a field omission; the sole
correction then used an empty child path. Those coupled requirements were absent
from the delivered schema. Record-only correction also could not re-express an
allegation in a different review table. Filters and orderBy lack established SDK
field encodings in the frozen source; only the explicit limit field supplies a
concrete native path. The fix exposes discriminated locator alternatives and
nonempty missing-field paths, preserves strict references and coverage, and
allows the existing correction to return a complete review where necessary.

The former whole-response parser failed before independent checks could run;
receipt consumption and repair routing also required complete review status.
The new path verifies records, finite inventories and conflicts independently,
preserves the exact candidate and a reproducible isolation ledger, and blocks
only the evidenced affected operations and pairs. Native demand, all-input
assessment and deletion-impact checks share those barriers. Invalid records
remain invalid; missing coverage never defaults to acceptance. Complete source
and contracts, seven normal requests, two workers, Task v5 isolation and the
existing correction/repair/transport budgets remain unchanged.

## Actual review delivery and locality

| Actual delivery | Unicode characters including envelope | Headroom below 1,048,576 |
| --- | ---: | ---: |
| Initial source review | 864,947 | 183,629 |
| Full-candidate correction | 988,098 | 60,478 |

Both deliveries preserve all **16 source files / 155,170 bytes**, 275 physical
review obligations and 928 scopes. Independent decoding verified values,
coordinates, ordering, annotation and fragments, not just their counts. The
same initial material in compact-v1 would require 2,146,076 characters; the
generic shared presentation saves 1,281,129. This is an observed bound for this
material, not a guarantee that arbitrarily large complete inputs fit.

The first review had five invalid scope records and 27 cross-record conflicts,
displayed as seven diagnostics without dropping conflict pairs. Correction
resolved those errors but introduced one exact scope-ID spelling error at
`/input_contract_checks/64`. Both replies remain `structural_invalid`; the
review is **partial**, with no fully accepted call.

The final initial ledger retains 289 valid records and rejects one. One barrier
contains the request and response operation references of `ir_260`: **two of
275 obligations / six of 928 scopes** are quarantined. **273 usable check rows /
922 scopes** retain their own decisions: 880 accepted, 36 rejected, six unresolved.
The 274 physically retained check rows include one paired blocked row, which is
not counted as usable. No global validation barrier remains. **49 findings**
(14 ordinary and 35 contract-derived) actually entered the existing shared
repair round. This directly demonstrates that a local record error no longer
discards independent review or suppresses all repair.

The corrected initial review contains a valid `missing_field` locator for limit
at native `ir_110`, operand 0, path `["limit"]`, with an action-only impact.
Filters/orderBy remain explicit Task and mapping limitations without invented
SDK paths. The service's zero-limit output behavior remains unestablished.
Furthermore, the same call's interface scopes reject a missing receiver
relationship. Conflict checks distinguish authored ordinary findings from
contract-derived repair findings; the retained locator does not prove complete
operation faithfulness or semantic truth. See `final-review-audit.en.md` and
`initial-review-backend-boundary-audit.en.md` for this precise boundary.

## Coverage and failure boundary

The final selection remains the initial bundle: CFG **679 IR**, with initial
processing retaining 633, explicitly leaving two source-unmodeled and isolating
44 validation-failing IR. The 54 gap records are not 54 unmodeled IR: they consist
of ten model-authored records plus 44 validation gaps. All 13 physical remote
sites and 25 save callers have retained representations, but there is no
propagation/reachability evidence for them in this run. Source audits retain
concrete bulk-dimension wrapping, storage wrapper/path and helper-boundary
limitations; node presence is not source-faithful boundary completion.

The repair produced an accepted Task candidate with 58 requirements and an
accepted CFG candidate with 770 IR. The revised graph separates the dimension
maps and adds documented summary workflow coordinates. These remain repair
candidates: processing did not finish, no revised annotation/review was selected,
and no initial review was used to certify revised material.

The native revision-processing process started at 2026-11-13 15:41:00.352 UTC.
Public sampling logs record:

- 16:05:29.803 UTC: server closed the websocket before response completion.
- 16:09:39.613 UTC: connection reset, OS error 10054.
- 16:09:54.995 UTC: an internal request timed out.
- 16:26:00.386 UTC: the process exceeded its deadline after **2700.031960 s**.

The terminal error is a native-process timeout, not a demonstrated
connection-establishment timeout. The earlier network interruptions are real,
but public evidence cannot assign all elapsed time to a single cause. The outer
adapter correctly did not retry this ineligible process timeout.

There is **no final input-contract-review receipt, propagation result, input
assessment or DOE result**. No deletable original input or DOE reduction was
established. This absence is not a zero-DOE finding, a computed coverage ratio,
or a complete analysis of the revised 770-IR candidate.

## Lifecycle, cost and evidence

Run: `experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902`.
Started 2026-11-13 20:39:17 China time; controller closed 2026-11-14 00:27:01.
Analysis elapsed **13,603.668 s**. Sole replay matched in **60.492 s**, with
**zero new native starts**. Controller and wrapper exited. Source, production,
prompts, transport, controller helpers and executables remained pinned.

Actual starts: **15 = seven normal + five structural corrections + three repair
stage starts in one shared repair round**. Outer retries: **zero**. Known public
usage: **2,862,874 tokens across 14 completed requests**, plus unknown usage for
the failed revision-processing request. Internal sampling attempts and any
unreported failed-attempt costs are not fully observable; unknown usage is not
zero. Dollar billing and a returned-model identity are not established by these
receipts. No Skill execution or additional probe was performed.

Primary references are `run-summary.json`, `final-review-audit.*`, the final
source-coverage and cost/provenance audits, both delivery audits, and the run's
original `result.json`, `controller-finished.json`, `replay-check.json`,
`implementation-check.json` and transport process receipts. Initial errors and
all historical runs remain preserved. This one-run/replay authorization is
consumed; no resume, second replay or new experiment follows from this closure.
