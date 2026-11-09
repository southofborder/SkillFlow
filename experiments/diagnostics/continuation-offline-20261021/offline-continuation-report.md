# Offline continuation: tools, source integrity and closed execution gates

Date: 2026-10-21. Repository: `D:/projects/SkillFlow`, revision
`2e28bcce25a24f39c54d6c06f215ff3df93b6305`.

The authorized offline implementation and material verification are complete.
The prospective reference and formal-run tools have been completed and tested.
The original 1,000-entry corpus was verified without acquisition or execution.
The selected cohort still has one unresolved current eligibility proof. A
separate source-only correction candidate is available for review and has not
been adopted. Calibration and formal target generation remain closed.

There are **zero new calibration target requests, zero formal target requests,
zero actual human reference confirmations and no comparative semantic scores**.
These engineering results establish no measured advantage for SkillFlow, direct
audit or the single-prompt full chain.

## Scope and preservation

The user's latest choice was to finish offline tools and material verification
while retaining the paused calibration. No target CLI, calibration controller,
Skill installer, Skill code or network acquisition was run. Preparation used
three assistant subtasks and the root assistant; their separately recorded
preparation usage is not zero and is not formal target usage.

[Final preservation verification](final-preservation-check.json) checked all
202 scoped tracked implementation/instruction files and all 1,054 files in the
historical local-only inventory. No inventory file is missing. The only two
inventoried files with new bytes are the interrupted untracked `formal_cli.py`
and `reference_epoch.py`; their exact original bytes are preserved under
`interrupted-code/`. The unrelated pre-existing billing-file modifications
were preserved. The 20-file source-cohort seal and 770-file preparation freeze
have zero mismatches. Historical source reviews, source bytes, preparation,
calibration records and locks were not rewritten. No commit or push was made.

The inventory is historical metadata, not a new seal or a current eligibility
certificate. The new prospective implementation, tests and documentation remain
local additions; this report does not imply they were committed or transferred.

## Original corpus and fixed long cohort

The existing read-only `acquisition.verify_corpus` checked the frozen roster,
index, result records, retained source-view and source-file hashes, and separate
archive hashes. Its [complete result](corpus-offline-verification.json) reports:

| Measure | Observed result |
|---|---:|
| Frozen roster entries | 1,000 |
| Entries with preserved acquisition attempts | 1,000 |
| Not attempted | 0 |
| `complete_verified` | 993 |
| Historical `integrity_or_format_failure` | 7 |
| Current verification errors | 0 |

The verifier took 414.36 seconds. Its
[invocation audit](corpus-offline-verification-invocation.json) records no
network, subprocess or corpus-write attempts. The seven acquisition failures
remain failures: four missing verified version pins, two missing-file failures
and one Windows path-length failure. Their original errors are retained in full.
No replacement rank, new version, repair or retry was introduced. Integrity of
these records does not make all 1,000 packages available or retroactively resolve
historical collection deviations and provenance limitations.

The [source-only cohort audit](source-only-integrity-audit.md) lists all 24
selected Skills and six reserves. The selected 24 retain 22 source clusters.
Their complete numbered source bundles measure 21,361–62,869 `o200k_base`
reference tokens, median 38,273, total 977,753. These are reference-tokenizer
measurements, not actual model-token usage. The original sources and case order
remain unchanged; the cohort was not selected using method outputs or DOE labels.

The current selector checked 65 effective reviews. It accepts 29 of the fixed
30 choices, consisting of 23 selected cases and all six reserves. It rejects
`real-022`, queue 42, `pskoett/self-improving-agent` version `4.0.3`: four named
text templates lack explicit operative-content evidence in the frozen review,
and two stored edges rely only on a recursive directory-copy instruction. The
handler has another supported route; the retained `HOOK.md` lacks one in the
unchanged review. The exact original evidence is preserved in the audit.

The source seal's selector digest differs from the maintained selector. Passing
historical byte checks therefore cannot substitute for current source proof.
There was no automatic reselection or silent transfer of the earlier pass.

The [dormant correction](case22-proposed-source-review.json) adds exact template
content and combines the own optional installer, documented hook layout, actual
hook identity/events and matching handler branches. The
[independent root review](case22-root-review.md) supports this conditional source
interpretation while preserving the unverified external loader/runtime limit.
In an isolated review copy, current mechanical validation checks all 65 reviews
with no errors and independently reproduces the exact original 24+6 IDs and
22 selected clusters. See [validation](case22-proposal-validation.json) and
[limitations](case22-proposal-review.md). This candidate is **not active** in the
original proposal and is not a new seal, human approval or semantic reference.

## Completed prospective implementation

[Reference workspace documentation](../../../tools/doe/real_comparison/README-reference-epoch.md)
describes the offline `reference_epoch.py` and shared `selection_readiness.py`:

- Copy exact fixed source packets and rules into a separate reference-only
  workspace; preserve initial drafts, every reference revision, original human
  submission and import-manifest version.
- Validate fixed source/case/bundle identities, existing reference/grading
  contracts and exact physical source quotations. Personal confirmations bind
  every reference item by group/ID and the current exact reference hash.
- Invalidate only the corrected case's active confirmations, preserve history,
  and require both people to reconfirm. Final sealing requires all 30 current
  references and 60 current personal confirmations from the two registered slots.
- Recompute current selection with `write=False`. Bind full source/review/code/
  runtime dependencies, checking them before and after validation to reject
  concurrent saves. Historical byte seals do not automatically satisfy this gate.

These tools neither create actual people nor establish semantic completeness.
No actual reference workspace, roster, revision import or human confirmation
was created in this continuation. The existing real ledgers remain partial
assistant source-fact drafts. Interrupted multi-file reference freezing fails
closed and requires explicit offline recovery preserving the partial records;
it is not a transactional operation.

[Formal CLI candidate documentation](../../../tools/doe/real_comparison/README-formal-cli.md)
describes the separate `formal_cli.py` and `formal_cli_metrics.py`. This is an
implementation candidate, not an adopted formal transport protocol. It requires
exact final materials, current source eligibility, 60 real current-version
confirmations, three complete replay-verified native calibrations, identical
production/runtime pins and a separate exact formal authorization. The existing
calibration module remains calibration-only.

The candidate retains the fixed 216 main workflows and 48 R1 reviews, fresh
native graph/pipeline execution, unchanged production core prompts, exact direct
prompts, one final answer per fresh CLI request, original-plus-review costs,
264-outcome closure, known-usage budgets and zero-model saved-evidence replay.
An accepted final response crossing a budget boundary remains consumable; the
next request is forbidden. Queued requests observing a global stop are closed
without fabricating process evidence; in-flight requests still require actual
terminal supervision. Reporting follows the active grading epoch after an
explicit reference correction, retaining original target costs and deduplicated
human history. No scoring algorithm or production semantic algorithm was changed.

## Engineering validation and retained failures

[Regression summary v2](offline-regression-summary-v2.json) deduplicates exact
JUnit class/name identities across recorded runs. **All 332 distinct tests have
a passing latest result.** Repeated tests are not added as independent checks.
The complete 41-test reference suite includes the 30-case/60-submission synthetic
seal, invalidation and history-tampering paths. The final formal suite has
55 tests; shared current-selection readiness has 22. Existing
selection, CLI-v3, usage, grading, exposure matching, human assignments, timing,
corrigenda and statistical contracts were exercised where relevant.

The recorded invocation history is deliberately retained:

| Invocation | Result | Interpretation |
|---|---|---|
| Broad initial integration | 249 passed, 2 failed | Two unchanged CLI-v3 amendment tests attempted 266–267-character temporary file paths. |
| Final formal/CLI/grading batch with short temporary root | 155 passed, 1 failed | Both earlier CLI cases passed; the blanket process guard blocked the existing local Node timer regression. |
| First exact timer wrapper | 1 failed | Windows executable-case normalization in the wrapper was too strict; no Node process started. |
| Corrected exact timer wrapper | 1 passed | Exact reviewed local DOM timer assertions ran successfully. |

The broad test guards allowed no target/worker launches and established no
outbound connection. The final timer wrapper allowed exactly one hash-checked
local Node executable and exact reviewed assertion program; it did not execute
any Skill or model client. Python socket guards are not a Node hard sandbox.
The blanket guard and first wrapper failures are diagnostic harness failures,
not removed test results. One owned synthetic test interpreter was terminated
after pytest returned because an exception had left a non-daemon fictional
worker waiting; no historical calibration process or lock was involved.

Independent review reproduced a real concurrent-save readiness race before the
fix, then reproduced rejection after the fix. Both synthetic observations are
preserved. Earlier owner development failures, interrupted invocations and
focused logs also remain. Engineering tests, simulated human records and
integrity replay are not DOE semantic outcomes or actual human confirmations.

## Paused request and cost evidence

[The paused-request audit](paused-request-audit.json) preserves the CLI-v3 first
request and its original locks. Its raw local rollout contains no final answer
or attributed per-response usage. Usage remains **unknown**. No receipt,
completion, zero-cost assertion or replacement request was manufactured. The
[read-only readiness diagnostic](formal-readiness.json) returns `ready: false`;
the missing complete reference epoch and paused calibration independently keep
formal execution closed. The current source eligibility issue is another
separate prerequisite.

[Preparation receipt capture](preparation-receipts.json) uses four exact
allowlisted assistant session IDs, six verified primary session segments and
328 distinct response IDs. Its bounded window is
2026-10-21T03:31:19.820Z through 2026-10-21T03:56:27.760426Z:

| Reported counter | Observed subtotal |
|---|---:|
| Input tokens | 42,894,684 |
| Cached input tokens, already included in input | 42,002,176 |
| Output tokens | 174,284 |
| Total tokens | 43,068,968 |

No conflicting response counters or missing attributed records were observed in
that capture. It is a preparation subtotal, not complete study cost: the live
root response, later receipts, earlier research, unregistered sessions and
unreceipted work may be absent. Cached and reasoning details are not added again
to totals. Hidden reasoning and message bodies were not exported. Formal target
cost, calibration cost and preparation cost remain separate. Historical paused
request cost remains unknown; no billing amount is estimated.

## Remaining research requirements and interpretation

Before target generation, the current source-evidence discrepancy needs an
explicit versioned resolution and current-selector validation. All real semantic
reference ledgers then need completion and both actual human source-only checks.
The paused unanswered calibration requires a separate explicit disposition that
preserves its unknown usage and failed history; the required completed calibration
and exact runtime/transport evidence do not yet exist. The prospective formal
CLI candidate has no adopted formal authorization. This report grants none.

No method comparison has been executed or scored. It remains unknown whether
SkillFlow has an accuracy, stability, total-cost or review-time advantage. The
experiment has established neither its actual advantage nor its lack of value.
Subsequent conclusions must follow the frozen shared quality criteria,
case/source-cluster analysis, symmetric practical thresholds and actual human
review records, allowing direct methods to win without changing the rules.
