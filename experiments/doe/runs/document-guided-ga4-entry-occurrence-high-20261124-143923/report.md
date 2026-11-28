# Document-guided analysis

Status: failed; stage: doe.

Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.

| Stage | Status |
|---|---|
| assembly | partial |
| doe | failed |
| flow | complete |
| graph | complete |
| processing | partial |
| propagation | incomplete |
| review | complete |
| revision-graph | partial |
| revision-processing | structural_failure |
| revision-sensitivity | skipped |
| revision-task-correspondence | skipped |
| revision/review | skipped |
| revision/task | complete |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

Retained limitations:
- The shared repair did not produce a consistent revised annotation. The original Task, CFG, annotation and their bound review remain selected together; all original findings remain unresolved by this repair.
- The shared repair was not confirmed by a completed source re-review; prior findings remain recorded in review/result.json and are not marked resolved.
- The shared repair did not form a consistent new annotation; retaining the original candidate.
- graph: Graph updates quarantined: /updates/8 Preserve the reviewed action's declared constraints; /updates/9 Preserve the reviewed action's declared constraints; /updates/10 An unaffected action changed in the action region; /updates/11 Preserve the reviewed action's declared constraints; /updates/12 Preserve the reviewed action's declared constraints; /updates/13 Preserve the reviewed action's declared constraints; /updates/14 Preserve the reviewed action's declared constraints; /updates/15 Preserve the reviewed action's declared constraints; Graph findings without a finite slot: F001
- processing: Structural correction limit reached (0); the stage has no accepted response.
- Unified source review is partial or retains material issues.
- Propagation is incomplete: incomplete

Local call counts: {'logical_calls': 13, 'structural_corrections': 3, 'json_normalizations': 0}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.

Reason: ValueError: Accepted input-contract scope input_obligation_00f959727b16f1ce877a conflicts with a finding at its operation or CFG location: annotation:/ir_semantics/ir_093

The semantic repair remains unconfirmed; original review findings remain in review/result.json.
