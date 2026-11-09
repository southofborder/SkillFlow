# Endpoint prompt validation: assistant assessment

**The latest prompt improved the tested semantic relationships, but the first-response and retry objective was not met.** Baseline: 4/4 legal initial responses and zero corrections. Latest: 3/4 legal initial responses and one correction. No schema relaxation, candidate field deletion, or quality rerun was used.

## Structure and real cost

| Measurement | Baseline | Latest, including correction |
|---|---:|---:|
| Logical requests | 4 | 5 |
| HTTP attempts | 4 | 5 |
| Structural corrections | 0 | 1 |
| JSON normalizations | 0 | 0 |
| HTTP retries | 0 | 0 |
| Input tokens | 64,776 | 104,034 |
| Output tokens (reasoning included) | 177,782 | 113,103 |
| Total tokens | 242,558 | 217,137 |
| Reasoning-token breakdown (already included) | 170,490 | 101,785 |
| Sum of request seconds | 826.239 | 538.051 |

All nine HTTP attempts supplied usage. Total usage was **459,695 tokens**. Actual online wall time was **1,384.703 seconds (23 minutes 4.7 seconds)**, excluding preparation and replay. The requested alias was deepseek-v4-flash with reasoning_effort=max; all responses reported deepseek-flash. There were no HTTP retries, truncations, JSON normalizations, semantic repairs, or quality reruns.

Latest initial requests alone used 193,318 tokens. Its one correction added 23,819 tokens and 21.711 request seconds. Including that correction, observed total tokens were 10.48% below baseline and summed request time was 34.88% lower. These are observations from one small interleaved sample, not a stable cost guarantee. Output tokens include reasoning; cache and reasoning breakdowns are not added again.

## Semantic assessment

| Case | Baseline | Latest |
|---|---|---|
| Ceramic dispatch annotation | Actual request correct, but receiver has only action/shape; field-value seeds remain upstream | Separate glaze/batches value seeds on actual delivery input, confirmed by backward demand |
| Folio annotation control | Legitimate entire-object deposit and opaque dependency preserved | Same legitimate control preserved; real return input explicitly seeded |
| Custody review control | No substantive findings | No substantive findings |
| Voucher review defects | Missing receiver content found; excessive read-output value seed accepted | Both controlled defects found; exact existing goal and missing-seed parent located |

Whole acquisition and model observation were preserved in both annotation arms. Narrow delivery requirements did not shrink the earlier read. Latest delivery seeds had receiver-specific derivations and distinct seed_goal_id values. Both ceramic arms produced the same four sensitive-note exclusion computations, so DOE result counts alone would conceal the baseline demand defect.

Latest voucher evidence uses real CFG read-output and send-input operands, and explicitly separates those graph facts from the candidate demand declarations. Baseline uses a syntactically legal IR target but its reason claims that the CFG proves an annotation demand-list fact; the candidate target should support that claim instead.

The latest voucher review also reports a missing Task exclusion for private_case_note and a missing sensitivity declaration. Both have source support. They reveal incompleteness in the assistant-authored external expectation, not automatically reviewer false positives. No reference answer was changed after seeing model output. Its missing-demand repair wording still needs a distinction: preserve the actual request/build operations, but do not retain redundant upstream seeds merely because the operation remains.

## First invalid response and correction

The latest voucher a001 invented requirement_checks[0].requirement_id_note. Strict schema validation rejected the extra field. The a002 correction removed it and made a minor wording change; findings and goal checks were unchanged. Both controlled findings were already present in the invalid response, but only a002 is the accepted review. First-response failure is not overwritten by final success.

[Original response](cases/review_voucher_delivery/latest/calls/review/a001/response.json) · [Mechanical diagnostic](cases/review_voucher_delivery/latest/calls/review/a001/validation.json) · [Accepted review](cases/review_voucher_delivery/latest/review.json)

## Prompt size and interpretation

| Static section (characters / UTF-8 bytes; English ASCII) | Baseline | Latest |
|---|---:|---:|
| Annotation | 49,706 | 55,512 |
| Review | 26,488 | 56,574 |

The latest prompt is longer. The observed total-token reduction mainly reflects lower generated reasoning in this sample, despite larger inputs and an extra call. The same model settings and validators were used, but stochastic generation, cache state, and execution order limit causal conclusions. The registered all-first-responses-legal gate failed; this run must not be presented as successful retry reduction.

## Verification and evidence

Zero-API replay matched all eight saved decisions after timing, usage, and call-file identities were frozen. Independent read-only recomputation matched canonical compilation and completed forward propagation, backward demand, and sensitivity comparisons for all four annotations without diagnostics. This validates reproducibility of the declared relationships, not their universal semantic correctness.

The new durable-validation tests passed 19/19; the fixture and analysis checks passed 5/5. Their scopes are separate from the real-model outcomes.

[Annotation assessment](assessment-annotations.assistant.md) · [Review assessment](assessment-reviews.assistant.md) · [Frozen metrics](metrics.json) · [Replay receipt](replay.json) · [Runner tests](verification/runner-tests/summary.json) · [External assessment bindings](assessment.assistant.json)

The cases and assessment are assistant-authored development materials, not an independent expert gold standard. No formal 001/010/013 run was started. This experiment does not establish generalized accuracy, semantic completeness, global minimality, or absence of DOE.
