# Complete source-review delivery

The default source-review presentation is `shared-v2` in guided run v12. This
is a general program transformation of review material, independent of Skill
names, paths, graph size or domain. It changes neither the seven normal semantic
requests nor the two-worker schedule, Task v5 isolation, correction/repair
budgets, transport limit, review response schema or backend semantics.

## Why the previous request exceeded the limit

The closed GA4 replacement run on 2026-11-12 delivered 1,079,505 Unicode
codepoints, exceeding the adapter's 1,048,576-character input limit by 30,929.
This was a local pre-start rejection, not a connection timeout, provider token
limit or Windows command-line limit. The adapter sends the request through stdin.

| Component | Characters |
| --- | ---: |
| Logical `INPUT_JSON` | 874,402 |
| Complete numbered source | 180,825 |
| Review instructions | 17,868 |
| Response format | 6,152 |
| Transport envelope and delimiters | 258 |
| Total | 1,079,505 |

Within the logical JSON, annotation occupied 403,839 characters, mandatory
contract inventory 244,455, CFG 154,115, Task 39,090, runtime contract 22,020
and processing gaps 10,579, plus field names and punctuation. Contract inventory
and annotation necessarily contain related evidence, descriptors and selectors;
the old representation repeated those values and record field names. The
review's local saved material was about 10.87 million characters, but local
indexes and audit metadata were already excluded from model delivery. It was
not a second copy of all fragments: delivered fragments and observations were
empty in this complete-annotation case. Complete source is not the main source
of growth and must remain intact.

## Generic lossless representation

`src/skillflow/document_guided/review_display.py` implements the explicitly marked
`skillflow-review-display-v1` JSON presentation. It offers plain escaped JSON,
exact shared values, inventory record columns, and their combination, choosing
the shortest complete envelope. Sharing uses exact serialized JSON values and
preserves object order, array order and every occurrence. Numeric types, absent
fields versus null, conditions, versions, receiver/member identities and source
evidence remain distinct.

`shared_values` holds repeated values. A sole `$ref` object refers to one value;
it does not merge identities or review decisions. `record_columns` gives the
ordered field names for rows of inventory obligations and scopes. These are
protocol paths for every Skill, not paths inside a particular Skill. Different
row shapes preserve optional fields. Literal marker-like objects are explicitly
escaped. A validated deterministic decoder reconstructs the exact logical JSON
and rejects missing references, cycles, malformed rows and ambiguous markers.

The renderer compares the packed JSON **plus its complete English explanation**
with the original JSON. It emits the packed form only when strictly shorter;
otherwise it emits the original JSON without the explanation. Thus small or
irreducible material cannot become larger because of presentation overhead.
The complete source section follows separately, byte-identical and unencoded.
No model fetch, decompression tool, extra semantic stage or per-IR call is needed.

Every contract occurrence and scope remains present. Review findings and repair
coordinates refer to original logical targets, never to display definitions or
row positions. Correction and re-review retain the selected presentation and
existing ownership and coverage validation. Empty findings still cannot replace
mandatory contract checks. Partial material, unavailable stages and local gaps
remain explicit; no missing fragment is fabricated.

## Identity and acceptance boundaries

New runs use `skillflow-document-guided-run-v12` and policy `review_protocol:
shared-v2`. Explicit legacy `compact-v1` and absent-view material retain their
original rendering behavior. The review response and semantic contracts do not
change schema. Historical artifacts are neither migrated nor relabeled.

The frozen rejected GA4 request is a read-only rendering regression, not a
historical analysis replay. Its new complete delivery is **903,775 characters**:
175,730 fewer (16.28%), with 144,801 characters below the unchanged cap. Exact
serialized expansion matches all logical documents; all 16 source files, 344
obligations and 1,195 scope descriptors and identities are retained. Twelve
tracked historical artifacts remain byte-identical. See
[the measured receipt](../../output/verification/review-input-size-20261112/integrated-delivery-measurement.json)
and [independent review](../../output/verification/review-input-size-20261112/review-notes.en.md).

Final offline acceptance passed **511 scoped tests, zero skips and failures** in
one integrated execution (408.07 seconds); it is not a whole-repository run. See
[the acceptance receipt](../../output/verification/review-input-size-20261112/offline-acceptance.json).
Offline regressions cover generic sizes and names, repetition and near-duplicates,
literal collisions, partial material, original targets, inventory coverage,
transport boundaries, seven injected semantic requests, worker/isolation
barriers, correction and zero-call replay. Earlier focused receipts remain
preserved and are not added as duplicate passes.

This transformation cannot make arbitrarily large irreducible information fit
one fixed-cap request. Over-limit complete material still produces the existing
explicit pre-start error; source or contracts are never truncated. Exact
reconstruction establishes preservation, not model comprehension or semantic
correctness. The authorized fresh GA4 run is separate online evidence.

That one fresh GA4 and its sole zero-call replay closed on 2026-11-13. Both
actual review deliveries retained all material and fit the unchanged cap
(861,152 and 867,125 characters). The final analysis remains partial because
three source-input findings still had invalid field locations after correction;
there are zero accepted contract checks and zero deletable ranges. See the
[online assessment](../../output/verification/online-ga4-review-shared-v2-20261112/assessment.en.md).
Its 12 native starts comprise seven normal requests and five structural
corrections, with no semantic repair or outer retry. No further launch or replay
is authorized by this completed follow-up.
