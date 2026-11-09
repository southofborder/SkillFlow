# GA4 and three small Skills: v8 online validation

All four authorized controllers and their sole zero-model replays have closed. **None completed full propagation or established a complete, useful substantive DOE result.** The runs still provide different amounts of useful evidence: 010 preserves request/response provenance, and 013 preserves the first fast call and the direct archive route. GA4 and 001 chiefly provide diagnostic prefixes. No run is classified as a complete success merely because it saved output or replayed consistently.

The requested configuration was `gpt-6.1-sol / high / openai`, two workers, seven normal semantic requests, one structural correction per stage and one shared semantic-repair round. Requests were fresh; no historical Task, CFG or answer was imported. The single queue supervisor launched 001, 010 and 013 sequentially after GA4 closed. Production code and prompts remained unchanged for all four runs and replays.

## Actual coverage and usefulness

| Case | Generated IR actually processed | Source-related coverage and result |
|---|---:|---|
| GA4 | **29 / 420 (6.90%)**; 5 cutoffs, 386 blocked | **0 / 13** remote API sites, **0 / 25** saveResult sites and **0 / 3** explicit source loops propagated. No sink-level DOE judgment; 14 declared boundary coordinates unresolved; sensitivity 0 / 57 resolved. |
| 001 conditional-notification | **2 / 13 (15.38%)**; 1 cutoff, 10 blocked | File acquisition 1 / 1; notification 0 / 1; count save 0 / 1. One sensitive comparison remains explicitly unresolved. |
| 010 catalog-query | **19 / 23 (82.61%)**; 1 cutoff, 3 blocked | Request acquisition and search call/response each 1 / 1; count save and items return each 0 / 1. Four optional-argument alternatives preserve request/response identity. No source-grounded sensitivity category, hence no sensitive-data comparisons. |
| 013 source-fetch-with-fallback | **15 / 26 (57.69%)**; 1 cutoff, 10 blocked | First fast call and direct key-absent archive route propagate. Retry and fast-success terminals are blocked. Archive success/error return and status-append paths cover **2 / 4** required terminal outcomes. Four sensitive comparisons remain explicitly unresolved. |

These denominators describe different things. Generated IR coverage is not source-boundary coverage, and a resolved sink position is not a DOE judgment. 013's two terminal outcomes are branch coverage, not two physical source statements. The partial archive route does not establish the failed-fast entries into that route.

The useful partial results are specific. In 010, optional `from_date` and `limit` alternatives retain the actual field values and request/response pairing without leaking presence markers into the payload. In 013, the fast request carries the correct `source_id` and `FAST_KEY` versions; the archive request carries the source ID without the key. Archive body and error retain their selection paths and matching response, with status appends before the two reached returns. Possible influence on responses is not treated as plaintext credential inclusion.

## Blocking layers and correctness

| Case | Main remaining blocker |
|---|---|
| GA4 | Selected CFG/processing alignment and broad unmodeled-boundary choices stop internal-call results, parameter bindings, environment handling and an exception merge. Known function bodies are also absent from some downstream SOURCE views despite a complete frozen package. |
| 001 | CFG expects a member operation to produce both a Boolean and a current member; the processing interface yields a member, while `has_member` is a collection branch predicate. A processing-only repair cannot fix that CFG shape. |
| 010 | The required write is unmodeled because update mode and serialization are unspecified. The interface genuinely requires replace/append/delete; serialization uncertainty alone is an overbroad stopping reason under its own prompt. No update mode was invented during this audit. |
| 013 | A three-successor CFG dispatch conflicts with binary BranchOp's exact-successor contract. The retained review recommends two binary decisions but assigns processing ownership, although CFG blocks/edges must change. |

The selected candidates compiled and the backends returned explicit partial results. These failures are not the same as rejected schemas or evidence of continuing loop nonconvergence. GA4's inventoried source loops were never reached. The absence of findings in the last 001 and 010 reviews did not remove their remaining cutoffs. GA4 retained ten source-review findings, with ten core defect statements independently corroborated and one target-location caveat; 013 retained its dispatch finding.

There are five sensitive comparisons across 001 and 013, all explicitly unresolved `no_excess_established`. They are neither safety verdicts nor confirmed excess. GA4 has no emitted sink comparison. 010 has no source-grounded sensitivity class, which is not itself an annotation error and does not prove arbitrary runtime data harmless. There is no valid denominator for a claimed end-to-end DOE accuracy, precision or recall. The source audits provide concrete supported local relations and defects, using assistant criteria rather than human gold.

## Full available target cost

| Case | Normal / repair / correction starts | Total starts | Public tokens | Main analysis | Sole replay |
|---|---:|---:|---:|---:|---:|
| GA4 | 7 / 6 / 5 | 18 | 2,309,177 | 3 h 34 m 44.53 s | 54 m 10.07 s |
| 001 | 7 / 4 / 3 | 14 | 343,524 | 15 m 37.32 s | 45.75 s |
| 010 | 7 / 5 / 1 | 13 | 334,706 | 15 m 14.98 s | 1 m 30.83 s |
| 013 | 7 / 4 / 2 | 13 | 375,925 | 15 m 40.26 s | 1 m 51.36 s |
| **Total** | **28 / 19 / 11** | **58** | **3,363,332** | **4 h 21 m 17.09 s** | **58 m 18.01 s** |

The sequence from first controller start to last closure lasted **5 h 20 m 11.13 s**, from 2026-11-01 21:44:56 to 2026-11-02 03:05:07 China time. That interval includes local work, replays and controller gaps; subsequent source audits/reporting are outside it. GA4's propagation and DOE stages alone took 38 m 51.87 s and 43 m 39.58 s, including validation, reconstruction and saving rather than only solving.

Known public tokens comprise **2,932,462 input + 430,870 output**. Cached input **1,415,808** and reasoning-output **104,238** are already included subsets. Normal requests used 1,292,867 tokens; semantic repair and dependent rebuilding used 1,264,132; structural correction used 806,333. Corrected and replaced answers remain counted.

Independent cross-checking found **58 unique CLI thread/turn identities**, no cross-run duplicate identities, and matching public usage and saved-answer/delivery hashes. All 58 accepted finals have complete public usage. Outer retries and input rejections were zero. Six internal reconnect events occurred in GA4's two reviews; exact provider HTTP attempts and any additional unreported failed-attempt usage remain unknown. Provider response IDs and independent backend configuration attestations are not exposed. Historical experiments, post-run assistant auditing/report work, currency cost and human review time are not silently included or treated as zero.

All four sole replays matched with **zero new model starts**, and all four implementation checks recorded unchanged SHA `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. This verifies saved-material reproducibility, not semantic correctness or repeated-generation stability.

## Historical context and next authorized work

Compared with GA4 v7, v8 used 5.70% more public tokens and 63.05% more main-analysis time. Compared with v5, increases were 31.36% and 174.83%. v5 processed 8 / 126 IR with unresolved comparisons; v7 solved none of its 262 IR and failed before publishing DOE; v8 saved partial diagnostic DOE with 29 / 420 IR. The generated representations and achieved scopes differ. The new matched replay and diagnostic output improve failure handling, but no acceleration, general accuracy or advantage over direct GPT is established by these runs.

The next authorized phase is offline simplification: reuse validated materials, compiled results and locating indexes; remove redundant whole reconstruction/verification during ordinary reads/saves and per-declaration projection; retain proportionate version/reference checks. It begins after this four-run result delivery. No additional real run is authorized. That work addresses local overhead; the semantic interface mismatches above remain visible and are not reclassified as complete results.

## Reports and evidence

- [ga4 assessment](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/assessment.en.md)
- [001 assessment](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/assessment.en.md)
- [010 assessment](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/assessment.en.md)
- [013 assessment](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/assessment.en.md)
- [Structured four-run summary](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/four-run-summary.json)
- [Independent complete cost cross-check](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/four-run-cost-crosscheck.md)
- [Per-request accounting and identity ledger](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/four-run-cost-crosscheck.json)

Original frozen source, prompts, answers, corrections, retained findings, failure records and replay receipts remain unchanged. The final audits read saved artifacts and source without new compilation, solving, replay, target calls or Skill execution.
