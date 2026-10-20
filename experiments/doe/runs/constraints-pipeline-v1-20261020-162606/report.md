# Formal joint pipeline: three-case pilot

A completed pipeline is conditional on its front-end declarations and supported rules. Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion.

[Actual calls, tokens and time](metrics.md) · [Measurement records](metrics.json) · [Assistant semantic review](assistant-review.md) · [Offline validation](validation.md) · [Zero-API replay](replay-summary.json) · [001 English input projection](audit/english-inputs/001/projection.json) · [010 English input projection](audit/english-inputs/010/projection.json) · [013 English input projection](audit/english-inputs/013/projection.json)

Verified historical sources and CFGs are retained. The pilot freezes an explicitly audited English projection without graph extraction; each Task is newly extracted from the English source only, then sealed for annotation and review. The normal path has 3 semantic calls; fixed-Task annotation repair has 5, while isolated Task revision and full reannotation has 6. The two repair paths share one semantic repair budget and end with independent rereview. Every response stage uses unlimited structural corrections; actual calls and transport attempts are recorded. No graph extraction, assistant-authored semantic candidates, or final DOE model call.

Case 001 uses an explicitly translated source/CFG projection; comparison with historical Chinese runs also changes input language, so changes cannot be attributed entirely to prompting.

| Case | Pipeline | Task | Review | Repair route | Selected Task | Selected annotation | Propagation | DOE | Logical calls | Materials |
|---|---|---|---|---|---|---|---|---|---:|---|
| 001 | failed | complete | not run | None | none | none | not run | not run | 5 | [Pipeline](cases/001/report.html), [Initial Task](cases/001/task/task.json), [Assistant review](cases/001/assistant-review.md) |
| 010 | diagnostic | complete | review_passed | None | Initial Task | annotation | complete | partial | 4 | [Pipeline](cases/010/report.html), [Initial Task](cases/010/task/task.json), [Original annotation](cases/010/annotation/audit/raw-annotation.json), [Initial four-axis review](cases/010/refinement/initial-review/report.html), [Review and repair](cases/010/refinement/report.html), [Propagation](cases/010/propagation/report.html), [Facts](cases/010/propagation/data.json), [DOE review](cases/010/doe/report.html), [DOE result](cases/010/doe/doe-result.json), [Assistant review](cases/010/assistant-review.md) |
| 013 | diagnostic | complete | repair_limit | Fixed-Task annotation repair | Initial Task | refinement/repair | complete | complete | 8 | [Pipeline](cases/013/report.html), [Initial Task](cases/013/task/task.json), [Original annotation](cases/013/annotation/audit/raw-annotation.json), [Initial four-axis review](cases/013/refinement/initial-review/report.html), [Review and repair](cases/013/refinement/report.html), [Repaired annotation](cases/013/refinement/repair/audit/raw-annotation.json), [Independent re-review](cases/013/refinement/final-review/report.html), [Propagation](cases/013/propagation/report.html), [Facts](cases/013/propagation/data.json), [DOE review](cases/013/doe/report.html), [DOE result](cases/013/doe/doe-result.json), [Assistant review](cases/013/assistant-review.md) |

**001:** Joint annotation failed: IncompleteRead(0 bytes read)

**010:** Analysis is available with review findings, a review failure, or analysis limitations.

**013:** Analysis is available with review findings, a review failure, or analysis limitations.

Review failure or repair_limit permits only explicitly diagnostic downstream analysis. Failed annotation never falls back to a historical successful response. Candidate and range counts are not counts of measured leaks.

Source-only Task reports: [001](cases/001/task/report.md) · [010](cases/010/task/report.md) · [013](cases/013/task/report.md)
