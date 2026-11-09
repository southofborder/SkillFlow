# Document-guided analysis

Status: failed; stage: doe.

Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.

| Stage | Status |
|---|---|
| assembly | partial |
| doe | failed |
| flow | complete |
| graph | complete |
| processing | complete |
| propagation | unsupported_feedback |
| review | complete |
| revision-graph | complete |
| revision-processing | partial |
| revision-sensitivity | partial |
| revision-task-correspondence | complete |
| revision/assembly | partial |
| revision/review | complete |
| sensitivity | complete |
| task | complete |
| task-correspondence | partial |

Retained limitations:
- processing: Invalid records retained as explicit local validation gaps
- sensitivity: Invalid records retained as explicit local validation gaps
- Unified source review is partial or retains material issues.
- Propagation is incomplete: unsupported_feedback

Local call counts: {'logical_calls': 17, 'structural_corrections': 5, 'json_normalizations': 0}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.

Reason: ValueError: Demand collection output has no recorded member scope
