# Document-guided analysis

Status: partial; stage: doe.

Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.

| Stage | Status |
|---|---|
| assembly | partial |
| doe | partial |
| flow | complete |
| graph | complete |
| processing | partial |
| propagation | incomplete |
| review | partial |
| revision-graph | partial |
| revision-processing | structural_failure |
| revision-task-correspondence | skipped |
| revision/review | skipped |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

Retained limitations:
- The shared repair did not produce a consistent revised annotation. The original Task, CFG, annotation and their bound review remain selected together; all original findings remain unresolved by this repair.
- The shared repair was not confirmed by a completed source re-review; prior findings remain recorded in review/result.json and are not marked resolved.
- The shared repair did not form a consistent new annotation; retaining the original candidate.
- graph: Graph updates quarantined: /updates/0 A region value is a nonempty array of blocks; /updates/1 A region value is a nonempty array of blocks
- processing: Structural correction limit reached (0); the stage has no accepted response.
- Unified source review did not complete (partial): Structural correction limit reached (1); the stage has no accepted response.; independently validated records are retained with explicit local validation barriers.
- Propagation is incomplete: incomplete
- DOE retains analysis limitations: partial

Local call counts: {'logical_calls': 11, 'structural_corrections': 2, 'json_normalizations': 0}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.

The semantic repair remains unconfirmed; original review findings remain in review/result.json.
