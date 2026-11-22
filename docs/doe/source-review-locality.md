# Strict source-review record isolation

This revision distinguishes an authored review record, a strictly validated
record, and a decision that is usable for the selected operation. It preserves
seven normal semantic requests, two workers, one structural correction per
stage, the existing shared semantic repair round, transport budgets and Task
v5 isolation. It does not rewrite or execute the analyzed Skill.

## Failure mechanism

The three rejected GA4 records claimed `missing_field`. The original response
used `absent_argument`; its correction selected the real request operand but
used `path=[]`. Both representations are invalid. Previously the delivered
schema exposed an independent kind enum and actual-range union. The coupling
and nonempty-path requirements were hidden in sequential model validators, so
the first error concealed the second.

Two allegations named logical roles without establishing their concrete SDK
field encoding. A source role is not a field path. A known `limit` omission can
use its source-supported concrete locator; unknown SDK keys cannot be invented.
Native output paths must refer to the operation's actual output, including a
tuple prefix when that is the represented result.

The former whole-response validator stopped before checking independent
contracts. Several downstream `complete` gates then discarded all tables and
prevented the existing repair round from consuming valid findings. There were
also separate contradictory candidate claims: a broad CFG-parent finding
overlapped many accepted contracts, and a source-defect allegation coexisted
with a finding that its actual call was mistranscribed. Fixing the three field
locators alone would not validate those acceptances.

## Validation and correction

The source-input grammar now has discriminated variants. `missing_argument`
requires `absent_argument`; `missing_field` requires an existing input slot and
a nonempty concrete path; `wrong_field` permits a whole-operand path only for
that kind. The constraints are present in both the delivered schema and English
guidance. No malformed field is filled, reclassified or accepted by the program.

Fragment review uses the same record validators for strict success and local
isolation. All records are inspected against the complete selected inventory;
missing and duplicate identities remain failures. Conflicts sharing one finding
use an explicit list of every affected check, with the individual diagnostics
retained in audit provenance. This reduces repetition without hiding conflicts.

The existing correction may replace the full review when a defect requires
moving an unexpressible allegation between tables. Full replacement must retain
the complete mandatory inventories. Malformed replacement envelopes are
recorded as merge failures; they cannot erase the last retained candidate's
independently valid records. Review correction presentation shares exact values
and homogeneous tables across original context and correction context, while
preserving complete source once. Presentation is roundtrip checked and never
truncates source, contracts, records or conflict relationships.

## Local isolation and evidence

After correction exhaustion the terminal retained candidate is not accepted.
A separate deterministic ledger preserves:

- The exact candidate, its digest and selected source/CFG/annotation binding.
- Every expected obligation and finite scope, including missing or duplicate rows.
- Each raw record location, raw digest, validation status and diagnostics.
- Strictly validated records, cross-record conflicts and effective blocked IDs.
- Validation barriers with exact operation references, reason and resolution.

An invalid source allegation with a verified operation locator blocks that
operation and any proven request/response pair. It does not establish a source
semantic error. Without a validated narrower relation the barrier covers the
operation, including deterministic operations without an input contract.
An unlocatable allegation or missing source-finding section has an explicitly
broader barrier. Projection failures block acquisition capability, independently
of input necessity. A broad actual CFG-parent objection still blocks all
overlapping contract acceptances; prefix consistency checks were not relaxed.

Independent valid records yield review status `partial`. With zero surviving
records, status remains `structural_failure`, while its validation evidence and
barriers remain available. Neither status means complete source review.
Only validated findings can route the existing semantic repair. Repaired
material must receive a newly bound review; a partial rereview does not confirm
that prior objections were resolved.

## Backend and immutable loading

Contract and projection consumers use finite coverage and blocked IDs rather
than a global success flag. Native action/output demands, all-input assessments
and forward deletion-impact analysis consume the same barriers. An affected
input with no positive demand cannot become deletable by losing its diagnostic.
Unrelated actual uses remain independently assessable; original propagation,
reads, observations and receiver/occurrence identities are unchanged.

Receipt loading reconstructs the ledger from the exact candidate and selected
material. Optional fragment aliases must be projections of that selected
annotation. The loader rejects changed inventories, stale bindings, fabricated
context, omitted barriers and altered effective coverage. Demand-result loading
also checks the required unresolved ranges and exact barrier diagnostics.
Hashes establish identity and reproducibility, not semantic correctness.

The current identities are guided run v13, source review fragment v5, input
contract review v3, demand result v10 and DOE run v10. Shared-v2 review display
and Task v5 remain. Historical artifacts retain their original identities and
are not migrated or replayed by this change.

See [Chinese design and validation boundaries](source-review-locality.zh.md)
and `output/verification/source-review-locality-20261113/` for the preserved
diagnosis, initial failures, corrective regressions and final acceptance receipt.

## Closed online validation

The sole fresh GA4 closed on 2026-11-14. Its initial partial review retained
273 usable checks / 922 scopes and quarantined two paired obligations / six
scopes at one operation, then routed 49 validated findings through the existing
repair. Both complete review deliveries fit the unchanged cap. Revision-processing
later exceeded its 2700-second native deadline; there is no final contract receipt,
propagation or DOE result. The sole replay matched with zero new native starts.
See [the English assessment](../../output/verification/online-ga4-source-review-locality-20261113/assessment.en.md)
for actual evidence, source-semantic limits, cost and the distinction between
successful local isolation and failed overall analysis. No additional run is
authorized by this completed experiment.
