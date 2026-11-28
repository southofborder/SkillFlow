# Document-guided analysis

Status: failed; stage: doe.

The Task and flow are inherited. The first graph answer was revalidated offline. Four normal downstream requests and bounded downstream repairs may use the two workers.

| Stage | Status |
|---|---|
| assembly | partial |
| doe | failed |
| flow | complete |
| graph | complete |
| processing | partial |
| propagation | incomplete |
| review | complete |
| revision-processing | complete |
| revision-sensitivity | complete |
| revision-task-correspondence | complete |
| revision/assembly | partial |
| revision/review | complete |
| sensitivity | complete |
| task | complete |
| task-correspondence | complete |

Retained limitations:
- Fixed upstream cfg finding F001 in review/result.json remains open at cfg:/blocks/block_028/instructions/0
- Fixed upstream cfg finding F001 in revision/review/result.json remains open at cfg:/blocks/block_028/instructions/0
- Fixed upstream cfg finding F002 in revision/review/result.json remains open at cfg:/blocks/block_038/instructions/0
- Unified source review is partial or retains material issues.
- Propagation is incomplete: incomplete

Local call counts: {'logical_calls': 9, 'structural_corrections': 1, 'json_normalizations': 0, 'scope': 'fresh_downstream_requests', 'inherited_history': {'logical_calls': 4, 'structural_corrections': 1, 'json_normalizations': 0}}
Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE.

Reason: ValueError: Outcome diagnostic must identify a declared protected outcome
