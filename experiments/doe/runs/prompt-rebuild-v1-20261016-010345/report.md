# Formal joint pipeline: three-case pilot

A completed pipeline is conditional on its front-end declarations and supported rules. Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion.

[001 English input projection](audit/english-inputs/001/projection.json) · [010 English input projection](audit/english-inputs/010/projection.json) · [013 English input projection](audit/english-inputs/013/projection.json)

Verified historical sources and CFGs are retained. The pilot freezes an explicitly audited English projection without graph extraction; each Task is newly extracted from the English source only, then sealed for annotation and review. The normal path has 3 semantic calls; fixed-Task annotation repair has 5, while isolated Task revision and full reannotation has 6. The two repair paths share one semantic repair budget and end with independent rereview. Every response stage uses unlimited structural corrections; actual calls and transport attempts are recorded. No graph extraction, assistant-authored semantic candidates, or final DOE model call.

Case 001 uses an explicitly translated source/CFG projection; comparison with historical Chinese runs also changes input language, so changes cannot be attributed entirely to prompting.

| Case | Pipeline | Task | Review | Repair route | Selected Task | Selected annotation | Propagation | DOE | Logical calls | Materials |
|---|---|---|---|---|---|---|---|---|---:|---|
| 001 | prepared | not run | not run | None | none | none | not run | not run | 0 |  |
| 010 | prepared | not run | not run | None | none | none | not run | not run | 0 |  |
| 013 | prepared | not run | not run | None | none | none | not run | not run | 0 |  |

**001:** Awaiting execution

**010:** Awaiting execution

**013:** Awaiting execution

Review failure or repair_limit permits only explicitly diagnostic downstream analysis. Failed annotation never falls back to a historical successful response. Candidate and range counts are not counts of measured leaks.
