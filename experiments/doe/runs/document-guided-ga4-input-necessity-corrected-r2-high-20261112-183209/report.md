# Document-guided analysis

Status: partial; stage: doe.

Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.

| Stage | Status |
|---|---|
| assembly | partial |
| doe | partial |
| flow | complete |
| graph | complete |
| processing | complete |
| propagation | incomplete |
| review | request_failure |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

Retained limitations:
- Unified source review did not complete (InputTooLarge): CLI input_too_large at review/calls/review/a001/call.json: 1079505 characters exceeds 1048576; no CLI process started; the selected candidate remains unreviewed.
- Propagation is incomplete: incomplete
- DOE retains analysis limitations: partial

Local call counts: {'logical_calls': 10, 'structural_corrections': 3, 'json_normalizations': 0}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.
