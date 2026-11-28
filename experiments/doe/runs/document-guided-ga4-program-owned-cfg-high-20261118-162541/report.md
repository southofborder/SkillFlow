# Document-guided analysis

Status: failed; stage: sensitivity.

Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.

| Stage | Status |
|---|---|
| flow | complete |
| graph | complete |
| processing | partial |
| sensitivity | failed |
| task | complete |
| task-correspondence | aborted |

Retained limitations:

Local call counts: {'logical_calls': 6, 'structural_corrections': 1, 'json_normalizations': 0}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.

Reason: InputTooLarge: CLI input_too_large at sensitivity/calls/a001/call.json: 1107518 characters exceeds 1048576; no CLI process started
