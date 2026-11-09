# Focused review-output validation

**Outcome: first-response structure improved in this paired sample; repair advice remains only partially satisfactory.** Baseline 1/2 first legal and one correction; latest 2/2 and zero corrections. Whole-chain tokens fell 12.16%, but latest initial requests used 2.91% more tokens.

[Read the semantic and cost assessment](assessment.assistant.html) · [Change notes](changes.md)


Paired development validation; authored fixtures and assistant assessment are not independent expert ground truth.

Both arms use identical inputs, strict validators, current v5 correction, and transport configuration. 4 initial chains are scheduled; structural corrections are separately counted and unlimited. There are no Task-extraction, semantic-repair, or quality-rerun calls.

| Case | Arm | Status | First legal | Calls | Corrections | HTTP attempts | Known total tokens | Call seconds |
|---|---|---|---|---:|---:|---:|---:|---:|
| review_custody_release | baseline | complete | True | 1 | 0 | 1 | 53251 | 147.10 |
| review_custody_release | latest | complete | True | 1 | 0 | 1 | 66126 | 187.77 |
| review_voucher_delivery | latest | complete | True | 1 | 0 | 1 | 58974 | 164.87 |
| review_voucher_delivery | baseline | complete | False | 2 | 1 | 2 | 89169 | 211.92 |

Reasoning and cache tokens are usage breakdowns, never added to total tokens. Missing usage remains unknown. A valid cannot_assess is a legal protocol response and a stopped semantic failure, not successful analysis. JSON normalization is separately recorded. First legal response and semantic correctness are different outcomes.

## Evidence

[Frozen expectations](audit/preregistration.json) · [Live decisions](summary.json)

[Frozen online timing and usage](metrics.json)

[Assistant semantic assessment](assessment.assistant.md)

- [review_custody_release: input](cases/review_custody_release/material.json) · [external fixture and expectations](audit/fixtures/review_custody_release.json)
  - [baseline initial prompt](cases/review_custody_release/baseline/prompt.txt) · [record](cases/review_custody_release/baseline/result.json)
  - [latest initial prompt](cases/review_custody_release/latest/prompt.txt) · [record](cases/review_custody_release/latest/result.json)
- [review_voucher_delivery: input](cases/review_voucher_delivery/material.json) · [external fixture and expectations](audit/fixtures/review_voucher_delivery.json)
  - [baseline initial prompt](cases/review_voucher_delivery/baseline/prompt.txt) · [record](cases/review_voucher_delivery/baseline/result.json)
  - [latest initial prompt](cases/review_voucher_delivery/latest/prompt.txt) · [record](cases/review_voucher_delivery/latest/result.json)
