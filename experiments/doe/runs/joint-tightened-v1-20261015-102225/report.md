# Formal joint pipeline: three-case pilot

A completed pipeline is conditional on its front-end declarations and supported rules. Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion.

Fixed source packages and CFGs; one new joint annotation per case, one initial review, and at most one semantic repair plus independent rereview. Every response stage uses unlimited structural corrections; actual calls and transport attempts are recorded. No graph extraction, assistant-authored semantic candidates, or final DOE model call.

| Case | Pipeline | Review | Selected annotation | Propagation | DOE | Logical calls | Materials |
|---|---|---|---|---|---|---:|---|
| 001 | failed | not run | none | not run | not run | 1 | [Pipeline](cases/001/report.html), [Assistant review](cases/001/assistant-review.md) |
| 010 | failed | not run | none | not run | not run | 1 | [Pipeline](cases/010/report.html), [Assistant review](cases/010/assistant-review.md) |
| 013 | failed | not run | none | not run | not run | 1 | [Pipeline](cases/013/report.html), [Assistant review](cases/013/assistant-review.md) |

**001:** Joint annotation failed: SSE provider error: {"error": {"message": "We were unable to start processing your request within the 900-second timeout limit. Please try again later."}}

**010:** Joint annotation failed: IncompleteRead(0 bytes read)

**013:** Joint annotation failed: SSE provider error: {"error": {"message": "We were unable to start processing your request within the 900-second timeout limit. Please try again later."}}

Review failure or repair_limit permits only explicitly diagnostic downstream analysis. Failed annotation never falls back to a historical successful response. Candidate and range counts are not counts of measured leaks.

## Execution measurements and assistant review

All three calls failed before model content. No new sensitivity, backward-demand or DOE result exists.

- [Assistant review](assistant-review.md)
- [Actual call, token and time metrics](metrics.md)
- [Zero-API replay verification](replay-verification.json)
- [Separate tiny connection probe](../../../diagnostics/deepseek-connectivity-20261015-1051/report.md)
