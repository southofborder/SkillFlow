# Small-Skill interface alignment: offline verification

This is an authored engineering regression, not an online accuracy measurement. The five frozen source files for 001, 010 and 013 are copied byte-for-byte into `tests/fixtures/cfg_processing_alignment_v9/`; `provenance.json` records their original paths and SHA-256 values. Original runs and answers were not changed, resumed or replayed. No actual model request or Skill execution occurred.

## Implementation

The compact annotation interface permits `write.mode` to be omitted and supplies `replace` during program expansion. Backend `WriteOp` still requires an explicit mode. Existing input checks and explicit `append`/`delete` semantics remain. The original submitted wire object retains the omission; the expanded raw and compiled objects contain the explicit mode.

The public runtime contract is now `skillflow-abstract-runtime-v11`, with `EM18` identifying ordinary-save replace as an analysis convention rather than source-explicit overwrite. The annotation rules and endpoint-demand guidance state that unknown serialization alone does not remove a known saved-value relationship. No generic state/cache/exception mechanism was added by this work.

## Verified scenarios

| Case | Actual offline result |
|---|---|
| 001 conditional-notification | Corrected `has_member` header and separate member body compile, propagate, persist and produce DOE. Three occurrences, including two equal records, keep separate member identities and pair each recipient with that member's original summary. Known empty filtered input skips member/notification and still reaches count/save. The old Boolean-plus-member output shape is a separate rejected candidate. |
| 001 limitation | `filter_items` remains a conservative subset with its real opt-out/urgency/value predicate; this test does not execute source-language predicates. The meaning of “processed records” remains an unresolved, separate `R_COUNT` requirement. Propagation is complete; DOE is partial with that source ambiguity, not falsely complete. |
| 010 catalog-query | All four optional-argument combinations compile, propagate, persist and complete DOE. Missing arguments are absent, not null or invented presence fields. The saved value is the actual response's `total` version; returned `items` is that same response's selected original value. Default replace and explicit append are separately tested. The original source has no declared sensitivity category, so zero sensitive comparisons is allowed. |
| 013 source-fetch-with-fallback | Six controlled scenarios cover all four terminal outcomes plus both key-absent archive outcomes. Binary decisions route first success, retry success, archive success and archive failure. Error values come from distinct protected-call exception sources, not successful responses or ID computations. Archive receives only source ID. Each active terminal appends its own status before returning its own version. |
| 013 previous log | Controlled scenarios provide an explicitly unknown previous log in their authoritative initial state. A separate test with no supplied state verifies ordinary production auto-seeding of unknown existing storage and append, without an invented read. |
| 013 repair | A valid initial CFG incorrectly skips the transient/non-transient distinction. A source finding in domain `cfg` triggers graph + processing + correspondence + sensitivity + rereview, preserving Task and flow. Twelve injected responses complete the actual saved propagation and DOE. This is the existing one-round closure, with no added stage. |
| DOE positive/negative capability | A separate declared-sensitivity variant adds a diagnostic receiver with exact field requirements. An unnecessary private note is detected as supported excess; explicitly requiring that same sensitive parameter prevents that excess conclusion. This variant is not part of the original 010 source and is not an online target input. |

The explicit 013 scenario tests exposed DOE projection resolving goals for proven `not_reached` branches as if they were missing active records. Root's narrow `inactive_goal` change keeps those goals and traces, marks the diagnostic nonblocking, and avoids a fabricated derivation. After that change these 013 scenarios complete DOE. The earlier partial results remain recorded in the attempt receipts.

## Validation receipts

All **23 distinct new tests** passed across corrective runs:

- 13 non-013 cases: `small-regressions-non013.txt`.
- 2 independent sensitivity variants: `small-regressions-doe-variants-corrected.txt`.
- 8 final 013 cases, including ordinary append seeding and full guided repair: `small-regressions-013-corrected.txt`.

The five existing related modules passed **144 tests** in 11.97 seconds; see `write-default-existing-regressions-corrected.txt`. Their old current-contract v10/17-rule expectation was updated to v11/18 rules. No frozen historical contract was migrated.

`small-regressions-attempts.json` records the initial fixture errors, exposed backend issues, corrective results and exact limits. These numbers are not a claim of one all-green repository-wide execution. The production online batch remains root-owned and requires the parent's complete offline acceptance.
