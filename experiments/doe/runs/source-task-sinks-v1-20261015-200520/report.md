# Formal joint pipeline: three-case pilot

A completed pipeline is conditional on its front-end declarations and supported rules. Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion.

[Actual calls, tokens and time](metrics.md) · [Measurement records](metrics.json) · [Assistant semantic review](assistant-review.md) · [Zero-API replay](replay-summary.json)

Fixed source packages and CFGs; each Task is newly extracted from source only, then sealed for annotation and review. The normal path has 3 semantic calls; fixed-Task annotation repair has 5, while isolated Task revision and full reannotation has 6. The two repair paths share one semantic repair budget and end with independent rereview. Every response stage uses unlimited structural corrections; actual calls and transport attempts are recorded. No graph extraction, assistant-authored semantic candidates, or final DOE model call.

| Case | Pipeline | Task | Review | Repair route | Selected Task | Selected annotation | Propagation | DOE | Logical calls | Materials |
|---|---|---|---|---|---|---|---|---|---:|---|
| 001 | diagnostic | complete | review_passed | None | Initial Task | annotation | complete | partial | 8 | [Pipeline](cases/001/report.html), [Initial Task](cases/001/task/task.json), [Original annotation](cases/001/annotation/audit/raw-annotation.json), [Initial four-axis review](cases/001/refinement/initial-review/report.html), [Review and repair](cases/001/refinement/report.html), [Propagation](cases/001/propagation/report.html), [Facts](cases/001/propagation/data.json), [DOE review](cases/001/doe/report.html), [DOE result](cases/001/doe/doe-result.json), [Assistant review](cases/001/assistant-review.md) |
| 010 | diagnostic | complete | review_passed | None | Initial Task | annotation | complete | partial | 5 | [Pipeline](cases/010/report.html), [Initial Task](cases/010/task/task.json), [Original annotation](cases/010/annotation/audit/raw-annotation.json), [Initial four-axis review](cases/010/refinement/initial-review/report.html), [Review and repair](cases/010/refinement/report.html), [Propagation](cases/010/propagation/report.html), [Facts](cases/010/propagation/data.json), [DOE review](cases/010/doe/report.html), [DOE result](cases/010/doe/doe-result.json), [Assistant review](cases/010/assistant-review.md) |
| 013 | diagnostic | complete | execution_error | None | Initial Task | annotation | complete | partial | 5 | [Pipeline](cases/013/report.html), [Initial Task](cases/013/task/task.json), [Original annotation](cases/013/annotation/audit/raw-annotation.json), [Initial four-axis review](cases/013/refinement/initial-review/report.html), [Review and repair](cases/013/refinement/report.html), [Propagation](cases/013/propagation/report.html), [Facts](cases/013/propagation/data.json), [DOE review](cases/013/doe/report.html), [DOE result](cases/013/doe/doe-result.json), [Assistant review](cases/013/assistant-review.md) |

**001:** Analysis is available with review findings, a review failure, or analysis limitations.

**010:** Analysis is available with review findings, a review failure, or analysis limitations.

**013:** Analysis is available with review findings, a review failure, or analysis limitations.

Review failure or repair_limit permits only explicitly diagnostic downstream analysis. Failed annotation never falls back to a historical successful response. Candidate and range counts are not counts of measured leaks.

## 本轮实质复核（助手）

001、010 的规定载荷需求已实际到达接收／保存输入；013 的四个状态追加和重试参数需求仍未补齐。

001 上游整值需求被初审漏检；013 初审发生 IncompleteRead，没有合法审查结果。三例 DOE 均为 partial，不能据此声称无 DOE。

实际 18 次逻辑请求、18 次 HTTP 尝试、9 次结构纠正、0 次语义修复；17 条 usage 的已知小计为 1,244,104 tokens，完整总量未知。整轮在线 85 分 0.86 秒。

三例已完成零 API 重放：pipeline 相等、传播／DOE matched，调用文件及在线时钟保持不变。

[助手总复核](assistant-review.md) · [工程验证与命令](validation.md) · [成本与时间](metrics.md) · [完整性核验](audit/verification.log)
