# Formal joint pipeline: three-case pilot

A completed pipeline is conditional on its front-end declarations and supported rules. Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion.

Fixed source packages and CFGs; one new joint annotation per case, one initial review, and at most one semantic repair plus independent rereview. Every response stage uses unlimited structural corrections; actual calls and transport attempts are recorded. No graph extraction, assistant-authored semantic candidates, or final DOE model call.

| Case | Pipeline | Review | Selected annotation | Propagation | DOE | Logical calls | Materials |
|---|---|---|---|---|---|---:|---|
| 001 | complete | review_passed | annotation | complete | complete | 2 | [Pipeline](cases/001/report.html), [Original annotation](cases/001/annotation/audit/raw-annotation.json), [Review and repair](cases/001/refinement/report.html), [Propagation](cases/001/propagation/report.html), [Facts](cases/001/propagation/data.json), [DOE review](cases/001/doe/report.html), [DOE result](cases/001/doe/doe-result.json), [Assistant review](cases/001/assistant-review.md) |
| 010 | complete | review_passed | annotation | complete | complete | 2 | [Pipeline](cases/010/report.html), [Original annotation](cases/010/annotation/audit/raw-annotation.json), [Review and repair](cases/010/refinement/report.html), [Propagation](cases/010/propagation/report.html), [Facts](cases/010/propagation/data.json), [DOE review](cases/010/doe/report.html), [DOE result](cases/010/doe/doe-result.json), [Assistant review](cases/010/assistant-review.md) |
| 013 | complete | review_passed | annotation | complete | complete | 2 | [Pipeline](cases/013/report.html), [Original annotation](cases/013/annotation/audit/raw-annotation.json), [Review and repair](cases/013/refinement/report.html), [Propagation](cases/013/propagation/report.html), [Facts](cases/013/propagation/data.json), [DOE review](cases/013/doe/report.html), [DOE result](cases/013/doe/doe-result.json), [Assistant review](cases/013/assistant-review.md) |

**001:** All stages completed; the bounded review reported no material issue.

**010:** All stages completed; the bounded review reported no material issue.

**013:** All stages completed; the bounded review reported no material issue.

Review failure or repair_limit permits only explicitly diagnostic downstream analysis. Failed annotation never falls back to a historical successful response. Candidate and range counts are not counts of measured leaks.

## Measured execution and substantive review

All three formal runs and zero-API replay completed. Reviewer findings were empty; assistant review found material demand-binding gaps. Completion does not establish semantic correctness.

- [Substantive assistant review](assistant-review.md)
- [Actual call, token and latency measurements](metrics.md)
- [Replay and unchanged-call verification](replay-verification.json)
