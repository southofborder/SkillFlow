# Can a strong model directly replace SkillFlow?

**Experiment state: complete.** 120 of 120 planned target trials are imported. 120 have paired semantic assessments.

Two deliverables are tested: direct source-only DOE audit and full source-only semantic-chain reconstruction. Historical SkillFlow outputs are not gold. No same-model SkillFlow run was performed, so this experiment does not establish a causal advantage or disadvantage of the architecture.

One uniform development revision was used and frozen. Both pilot versions remain: 12 original and 12 revised target answers. Preparations of the superseded held-out prompt were never target calls and are not failures or extra samples. The held-out cohort contains 72 first answers (12 cases × 2 deliverables × 3 independent repeats) and 24 preselected independent reviews of repeat 1.

## Semantic observations

References and two separate assessments are assistant-authored exploratory evidence. Agreement is not independent human validation. Source-based disputes remain explicit. Trial names, repeats and execution order are hidden. Requested content is provided for fair scoring and reveals artifact kind; answer structure or correction notes may reveal review status. This is identity masking, not complete condition blinding.

A source-grounded answer can satisfy the reference while explicitly leaving a DOE question unresolved because the source lacks sensitivity or recipient evidence. That is correct uncertainty handling, not a claim of safety. An indeterminate trial score instead means the assessors or references cannot resolve the answer's adequacy.

| Stage / deliverable / response | Satisfies reference | Substantive error | Indeterminate/disagreement | Unassessed |
|---|---:|---:|---:|---:|
| heldout/audit/initial | 36 | 0 | 0 | 0 |
| heldout/audit/review | 12 | 0 | 0 | 0 |
| heldout/chain/initial | 36 | 0 | 0 | 0 |
| heldout/chain/review | 12 | 0 | 0 | 0 |
| pilot/audit/initial | 2 | 1 | 0 | 0 |
| pilot/audit/review | 3 | 0 | 0 | 0 |
| pilot/chain/initial | 3 | 0 | 0 | 0 |
| pilot/chain/review | 3 | 0 | 0 | 0 |
| pilot_revision/audit/initial | 2 | 1 | 0 | 0 |
| pilot_revision/audit/review | 3 | 0 | 0 | 0 |
| pilot_revision/chain/initial | 3 | 0 | 0 | 0 |
| pilot_revision/chain/review | 3 | 0 | 0 | 0 |

Capability counts require observed protocol conformity and membership in the frozen effective schedule. Excluded for violated, unverified or unplanned execution: 0. Raw assessments remain preserved separately.

## Repetition and one independent review

Held-out first answers are sampled three times; only the preselected first repeat is independently reviewed. Reviews do not replace or erase first-answer scores.

- audit: 12/12 fully assessed, protocol-eligible case groups have all three answers satisfy the paired reference assessments.
- chain: 12/12 fully assessed, protocol-eligible case groups have all three answers satisfy the paired reference assessments.
- Per-reviewer mandatory-check profiles and exposure counts are preserved in results.json. Identical check outcomes do not imply identical reasoning, proposals, or wording.

| Stage | Deliverable | First-answer judgment | Reviewed judgment | Pairs |
|---|---|---|---|---:|
| heldout | audit | satisfies_reference | satisfies_reference | 12 |
| heldout | chain | satisfies_reference | satisfies_reference | 12 |
| pilot | audit | satisfies_reference | satisfies_reference | 2 |
| pilot | audit | substantive_error | satisfies_reference | 1 |
| pilot | chain | satisfies_reference | satisfies_reference | 3 |
| pilot_revision | audit | satisfies_reference | satisfies_reference | 2 |
| pilot_revision | audit | substantive_error | satisfies_reference | 1 |
| pilot_revision | chain | satisfies_reference | satisfies_reference | 3 |

## Measured target usage

Usage includes the target subagent's base instructions and complete prompt. Reference authoring, scoring and root orchestration are excluded from target totals. Per-response records are deduplicated; reasoning/cache fields are not added again. Missing usage remains unknown. No currency amount is inferred.

| Stage / deliverable / response | Calls | Reported total tokens | Complete token total | Sum of individual trial seconds |
|---|---:|---:|---:|---:|
| heldout/audit/initial | 36 | 1,267,919 | 1267919 | 4148.1 |
| heldout/audit/review | 12 | 451,017 | 451017 | 1471.6 |
| heldout/chain/initial | 36 | 1,388,234 | 1388234 | 8002.6 |
| heldout/chain/review | 12 | 518,082 | 518082 | 2636.9 |
| pilot/audit/initial | 3 | 106,277 | 106277 | 589.9 |
| pilot/audit/review | 3 | 112,066 | 112066 | 560.9 |
| pilot/chain/initial | 3 | 116,194 | 116194 | 1380.7 |
| pilot/chain/review | 3 | 127,354 | 127354 | 420.0 |
| pilot_revision/audit/initial | 3 | 106,775 | 106775 | 723.9 |
| pilot_revision/audit/review | 3 | 114,381 | 114381 | 348.8 |
| pilot_revision/chain/initial | 3 | 117,462 | 117462 | 768.6 |
| pilot_revision/chain/review | 3 | 134,365 | 134365 | 1405.9 |

The following cost groups include both the preselected original answer and its one independent review, rather than quoting only the review's incremental usage.

| Stage / deliverable | Two-call workflows | Original + review total tokens |
|---|---:|---:|
| heldout/audit | 12 | 873062 |
| heldout/chain | 12 | 981090 |
| pilot/audit | 3 | 218343 |
| pilot/chain | 3 | 243548 |
| pilot_revision/audit | 3 | 221156 |
| pilot_revision/chain | 3 | 251827 |

Individual times overlap during concurrent execution and must not be presented as workflow wall time or added to nested orchestration clocks.

Across all imported targets, median individual duration is 149.5825 seconds. The earliest-start to latest-completion execution window is 18825 seconds and includes orchestration gaps. This is distinct from summed trial durations.

## Scope and limitations

- The three familiar pilots are development observations, not held-out accuracy. The existing historical semantic corpus is not reclassified as an unseen DOE gold standard.
- Target, reference authors and assessors use separate contexts of the same configured model. Correlated interpretation errors can survive agreement; there is no independent human gold standard.
- The twelve new assistant-authored synthetic cases form four controlled triplets. Their explicit controller, data and interface contracts reduce ambiguity relative to many real Skills. They are not twelve independent real-world domains.
- Target runtime configuration is checked per trial. Tools are forbidden by protocol, not disabled by a hard sandbox; base runtime instructions remain present.
- Collaboration task payloads are encrypted in local receipts. Exact delivery equality cannot be independently verified there; saved prompts and dispatcher records are retained without claiming that proof.
- Zero-call replay verifies preserved artifacts and deterministic aggregation; it does not re-prove natural-language judgments or reproduce the model generation.
- Competitive direct answers would leave SkillFlow's empirical advantage unestablished here. A same-model end-to-end method comparison is required before attributing differences to architecture.

## Review material

- [Execution schedule](schedule-revision1.json)
- [Preregistration](preregistration.json)
- [Measurements and completion state](results.json)
- [Paired semantic assessment](assessment-report.md)
- [Qualitative historical context](historical-context.md)
- [Reusable direct-audit prompt](prompts/direct-audit-final.txt)
- [Reusable full-chain prompt](prompts/full-chain-final.txt)
- [Original references](references/)
- [All original target trials](trials/)
