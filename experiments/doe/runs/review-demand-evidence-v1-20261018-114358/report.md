# Outcome: partial semantic acceptance; no observed cost reduction

Latest and baseline: 2/2 first completed legal responses, zero structural corrections. Exact redundant-demand relocation and the missing Task prohibition are identified. One CFG-evidence attribution overstatement remains. Latest uses 124,880 tokens versus baseline 114,071 (+9.48%); structural-retry reduction is not demonstrated.

[Read the full relationship assessment](assessment.assistant.html) · [Independent review](assessment-reviews.assistant.md) · [Offline 300-test receipts](verification/regression/summary.json) · [Preregistered checks](assessment-plan.json)

# Endpoint prompt paired validation

Paired development validation; authored fixtures and assistant assessment are not independent expert ground truth.

Both arms use identical inputs, strict validators, current v5 correction, and transport configuration. 4 initial chains are scheduled; structural corrections are separately counted and unlimited. There are no Task-extraction, semantic-repair, or quality-rerun calls.

| Case | Arm | Status | First legal | Calls | Corrections | HTTP attempts | Known total tokens | Call seconds |
|---|---|---|---|---:|---:|---:|---:|---:|
| review_custody_release | baseline | complete | True | 1 | 0 | 1 | 55365 | 147.63 |
| review_custody_release | latest | complete | True | 1 | 0 | 1 | 65195 | 191.27 |
| review_voucher_delivery | latest | complete | True | 1 | 0 | 1 | 59685 | 157.39 |
| review_voucher_delivery | baseline | complete | True | 1 | 0 | 1 | 58706 | 157.13 |

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
