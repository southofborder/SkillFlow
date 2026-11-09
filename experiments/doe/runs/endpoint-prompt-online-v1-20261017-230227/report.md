# Endpoint prompt paired validation

**Outcome: semantic improvements observed; the first-response/retry gate was not met.** Baseline 4/4 first legal, zero corrections; latest 3/4 first legal, one correction.

**Actual usage:** 9 logical calls / 9 HTTP attempts; 459,695 total tokens; 23 minutes 4.7 seconds online wall time. Zero-API replay matched. Latest total tokens were 10.48% lower, while its input was larger and its structural result was worse.

[Read the semantic and cost assessment](assessment.assistant.html) · [Assessment Markdown](assessment.assistant.md)

Paired development validation; authored fixtures and assistant assessment are not independent expert ground truth.

Both arms use identical inputs, strict validators, current v5 correction, and transport configuration. Eight initial chains are scheduled; structural corrections are separately counted and unlimited. There are no Task-extraction, semantic-repair, or quality-rerun calls.

| Case | Arm | Status | First legal | Calls | Corrections | HTTP attempts | Known total tokens | Call seconds |
|---|---|---|---|---:|---:|---:|---:|---:|
| annotation_ceramic_dispatch | baseline | complete | True | 1 | 0 | 1 | 70362 | 250.69 |
| annotation_ceramic_dispatch | latest | complete | True | 1 | 0 | 1 | 42531 | 118.64 |
| review_custody_release | latest | complete | True | 1 | 0 | 1 | 37645 | 66.89 |
| review_custody_release | baseline | complete | True | 1 | 0 | 1 | 60312 | 213.71 |
| annotation_folio_return | baseline | complete | True | 1 | 0 | 1 | 49614 | 159.91 |
| annotation_folio_return | latest | complete | True | 1 | 0 | 1 | 51408 | 156.29 |
| review_voucher_delivery | latest | complete | False | 2 | 1 | 2 | 85553 | 196.23 |
| review_voucher_delivery | baseline | complete | True | 1 | 0 | 1 | 62270 | 201.92 |

Reasoning and cache tokens are usage breakdowns, never added to total tokens. Missing usage remains unknown. A valid cannot_assess is a legal protocol response and a stopped semantic failure, not successful analysis. JSON normalization is separately recorded. First legal response and semantic correctness are different outcomes.

## Evidence

[Frozen expectations](audit/preregistration.json) · [Live decisions](summary.json)

[Frozen online timing and usage](metrics.json)

[Assistant semantic assessment](assessment.assistant.md)

- [annotation_ceramic_dispatch: input](cases/annotation_ceramic_dispatch/material.json) · [external fixture and expectations](audit/fixtures/annotation_ceramic_dispatch.json)
  - [baseline initial prompt](cases/annotation_ceramic_dispatch/baseline/prompt.txt) · [record](cases/annotation_ceramic_dispatch/baseline/result.json)
  - [latest initial prompt](cases/annotation_ceramic_dispatch/latest/prompt.txt) · [record](cases/annotation_ceramic_dispatch/latest/result.json)
- [annotation_folio_return: input](cases/annotation_folio_return/material.json) · [external fixture and expectations](audit/fixtures/annotation_folio_return.json)
  - [baseline initial prompt](cases/annotation_folio_return/baseline/prompt.txt) · [record](cases/annotation_folio_return/baseline/result.json)
  - [latest initial prompt](cases/annotation_folio_return/latest/prompt.txt) · [record](cases/annotation_folio_return/latest/result.json)
- [review_custody_release: input](cases/review_custody_release/material.json) · [external fixture and expectations](audit/fixtures/review_custody_release.json)
  - [baseline initial prompt](cases/review_custody_release/baseline/prompt.txt) · [record](cases/review_custody_release/baseline/result.json)
  - [latest initial prompt](cases/review_custody_release/latest/prompt.txt) · [record](cases/review_custody_release/latest/result.json)
- [review_voucher_delivery: input](cases/review_voucher_delivery/material.json) · [external fixture and expectations](audit/fixtures/review_voucher_delivery.json)
  - [baseline initial prompt](cases/review_voucher_delivery/baseline/prompt.txt) · [record](cases/review_voucher_delivery/baseline/result.json)
  - [latest initial prompt](cases/review_voucher_delivery/latest/prompt.txt) · [record](cases/review_voucher_delivery/latest/result.json)
