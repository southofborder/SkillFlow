# GA4 branch, ingress and field coverage

The selected run established **285 required field or property ranges and no deletable range**. Propagation completed 133 of the 489 retained instructions. Eight modeled receiver boundaries remained unresolved, so DOE had no recorded receiver on which to compare a sensitive field with a task demand. The selected annotation uses revised processing, task correspondence and sensitivity. [Selected fragments and outcome](run-summary.json) · [Field assessments](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/doe/audit/demand-support.json)

| Measure | Closed baseline 211742 | Current run 150337 |
| --- | ---: | ---: |
| IR processed / unmodeled / blocked | 451 / 6 / 32 | 133 / 54 / 302 |
| Alternatives at the four-field build in `ir_415` | 81 | No execution record |
| DOE comparison candidates | 83,442 | 0 |
| Required / unresolved / deletable ranges | 2,942 / 5,077 / 0 | 285 / 997 / 0 |
| DOE result JSON, bytes | 266,059,954 | 288,517 |
| HTML, bytes | 3,938,066,348 | 5,633,811 |
| Markdown, bytes | 3,697,695,105 | 5,633,334 |

Range counts sum assessment rows and can include repeated uses of a field. File sizes are the published byte lengths. [Baseline outcome and bytes](../online-ga4-lossless-delivery-20261119/assessment.en.md) · [Baseline candidate count](../online-ga4-lossless-delivery-20261119/independent-candidate-scale-forensics.en.md) · [Current backend audit](final-backend-audit.json) · [Current artifact bytes](run-summary.json)

## What the branch records show

The baseline build combined three alternatives from each of four inputs. Its largest receiver comparison had 81 payload versions and 428 sensitivity signals, giving 34,668 candidates. In this run the first producer, `ir_411`, was explicitly unmodeled. Instructions `ir_412` through `ir_416` were blocked, including the build and the save. Across the recorded portion of the graph, 100 operation records contained 106 alternatives. Fourteen operations in ten instructions carried a selector binding. These counts show where typed selectors were used. Testing whether they remove infeasible combinations at the former hotspot still requires the missing producer and consumer records. [Baseline branch evidence](../online-ga4-lossless-delivery-20261119/independent-candidate-scale-forensics.en.md) · [Current IR coverage](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/propagation/manifest.json) · [Recorded alternatives and bindings](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/propagation/records.json)

## Which sensitive inputs were observed

The selected answer contains 35 distinct field classifications across 27 ingress entries and 27 modeled access sites. Of the 35 declarations, 18 label Skill arguments, 11 label tool responses and six label environment data. DOE resolved 24 declarations. Matching the declared accesses to recorded reads, consumed input slots and their source versions independently witnessed 11 sites and 11 data versions. Two sites read environment data and nine consumed Skill arguments. Sixteen classified sites lacked a matching observation, including all classified tool-response sites. DOE recorded zero alias groups. The prior run had 209 use-site declarations, of which 100 credential declarations resolved to one environment version. Testing the grouping of those repeated uses still relies on offline regressions. [Selected classifications](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/steps/revision-sensitivity/value.json) · [Observed sites and versions](run-summary.json) · [Baseline ingress evidence](../online-ga4-lossless-delivery-20261119/independent-candidate-scale-forensics.en.md)

## Field decisions and report size

Of 700 input assessments, 222 occur at processed positions, 405 at blocked positions and 73 at unmodeled positions. The required ranges include the values of `rows[*].clicks` and `rows[*].impressions` at `ir_179`. All eight unresolved receiver boundaries were blocked. Six are network sends, one invokes `mkdir` and one writes `saved_file`. Receiver coverage limits both candidate counts and the report-size comparison. The separate offline publication benchmark measures the indexed report with controlled candidate shapes and shared evidence. [Input locations and ranges](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/doe/audit/demand-support.json) · [Unresolved boundaries](../../../experiments/doe/runs/document-guided-ga4-entry-review-high-20261123-150337/doe/doe-result.json) · [Offline publication measurements](../entry-review-20261122/report-publication.json)
