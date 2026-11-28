# Independent scoped-backend audit

The read-only audit compared `input_contracts.py` and `demand_engine.py` with the finite receipt API while the initial integrated offline run was active. Production files were not modified. One isolated synthetic reproduction and eight regression parameters were added; no real model, Skill, controller or historical replay was started.

## Confirmed defect

`InputContracts.influenced_outputs` constructs every overlap demand with `conservative=False`. This treats a nonaccepted structural input selector as a certified information upper bound. For a rejected or unresolved `cardinality(rows)` or `presence(rows.each)` scope, backward transfer correctly emits a conservative derivation without `information_bound`. A descendant `rows.each.payload` therefore overlaps that backward limitation. Forward influence nevertheless returns an empty output list for the same change, incorrectly certifying independence.

The isolated result is saved in `rejected-structural-scope-audit.json`. `structural-review-overlap-initial.xml` records eight failures: required selector / authored unresolved range × rejected / unresolved review × cardinality / presence. Each failure reaches the forward-independence assertion; backward conservatism is retained. Existing accepted structural-range tests remain unchanged and require precise descendant independence where the source reviewer actually accepted the range bound.

The parent acknowledged the defect and queued a narrow overlap correction after the initial integrated run closes, preserving the initial receipt. Forward overlap must use the same distinction as backward transfer: accepted authored explicit uncertain ranges can bound the information property; review-level nonacceptance cannot certify that bound. This is not a reason to globally widen independently accepted output/input scopes.

## Other reviewed boundaries

- Exact output property/path matching and explicit complete-output decomposition remain separate. Rejected decomposition cannot certify unlisted output independence; an independent exact whole-output rule can still supply coverage.
- Required ranges, explicit unresolved ranges and the remainder have distinct decisions. Wide claim barriers produce diagnostics without implicit retention of every actual slot; affected input scopes must be separately nonaccepted.
- Missing attachments are indexed by their stable operation obligation, avoiding collisions between null contract IDs.
- `if_present` emits unconditional presence and conditional requested information. It does not invent a known-absent value or require a redundant authored presence row.
- `information_bound` remains separate from uncertain necessity. Its origin is an accepted authored explicit uncertain range; propagation uses a finite exact-transfer whitelist, drops the flag on widening and does not grant it to generic opaque relations.
- Known source-input errors overlay only authored native action/output impacts, retain actual operands and do not introduce Task seeds or fabricated missing inputs.
- Forward and backward queries use the same sealed selected material. Source review completion/partial coverage does not globally erase accepted local scopes.

No second blocking correctness defect was established by this audit. This is a focused code review and synthetic regression result, not a proof of all transfer semantics.

## Protocol identity and documentation

The sensitivity result should advance from v7 to v8 because nested derivations and all-input location/source-finding shapes changed after the sealed measured run. Formal DOE v9 alone does not distinguish standalone sensitivity results. The parent queued this identity finalization after initial integration; the maintained English specification describes the intended final sensitivity v8 alongside demand v9, receipt v2 and source-review fragment v4. Task remains v5.

Owned Task/formal and injected lifecycle suites previously passed. The 14 current small-alignment fixture failures were corrected by the schema owner with source-backed mandatory contracts; the exact module subsequently passed 23 tests in `small-alignment-contracts-final.xml`. Original failing XML and original measured artifacts remain preserved.
