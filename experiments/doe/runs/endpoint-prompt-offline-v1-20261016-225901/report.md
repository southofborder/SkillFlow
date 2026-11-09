# Endpoint demands and review references: offline acceptance

The endpoint-demand, acquisition-scope, and review-reference update is offline only. There were zero model/API calls and no formal 001/010/013 rerun. This report separates executable-example and engine checks from unmeasured model behavior.

Broader offline regression: passed. 2,343 passed; 1 skipped; 0 failed; 0 errors.

## What changed

- Annotation: one complete independent calibration example replaces the old format example. It reads a whole packet, selects original fields, conditionally builds a request, and demands badge/offset values at deliver input 0.
- Review: one complete four-axis response finds the unsupported whole-read seed and missing receiver content seeds. Existing valid upstream, action, and shape goals remain accepted.
- Reference help: finding targets locate candidate claims; exact goal pointers check existing seeds; CFG citations support real graph facts. Source-only findings and real metadata named events remain legal.
- Diagnostics: typed evidence errors retain precise child paths, current target, schema-derived allowed forms, and one deduplicated relevant short example. The common correction protocol remains v5.
- The two candidate annotations differ only in demands. No automatic seed copying, changed read, revised Task, erased sensitivity, or added isolation makes a contrast pass.

## Executable examples and actual demand calculation

Both complete annotation candidates pass schema, reference and compilation checks. The valid candidate has 3 compiled goals; the semantic contrast has 6. A valid shape is not a semantic verdict. The complete review response routes both findings to the fixed-Task annotation repair path, followed by an isolated re-review using injected clients.

The actual compile/propagate/backward-demand regressions check that upstream value seeds plus endpoint action/shape do not create receiver value demands. Endpoint field seeds reach their own input slot with seed_goal_id; they do not flow to a second recipient. True/false/abstract controls, omitted members, model entrance needs, ordinary return, whole-value obligations, conservative opaque dependencies, and current write versus prior stored content remain distinct.

An additional explicit false-condition check caught a teaching issue: expected creates an independent original-value seed and does not inherit build.when. The final optional offset demand omits redundant expected because select_part/build already preserve its original identity. False stops before consuming offset content; true traces the original field. A nominal absent-field boundary goal is not evidence of actual exposure. The conservative behavior with an extra expected reference is retained as a regression boundary, not silently changed in the algorithm.

## Prompt size on identical frozen inputs

| Prompt | Before characters | After characters | Change | Change % |
|---|---|---|---|---|
| annotation | 67,026 | 72,832 | +5,806 | +8.66% |
| review | 58,619 | 88,705 | +30,086 | +51.32% |

These two comparison inputs are English, so character and UTF-8 byte counts coincide. Section-level byte/character counts are in prompt-sizes.json. The actual input section is identical in each before/after pair. Complete teaching contexts increase request length; internal review target bookkeeping was projected to the same compact ID-to-pointer table used in real requests. No token count, retry reduction, first-response success rate, or end-to-end cost improvement was measured.

## Preserved interfaces and historical materials

Exactly 5 of 145 production Python files changed. The other 140 are byte-identical to the pre-change snapshot. Annotation, review, and sealed Task JSON schemas match. Runtime, compiler, propagation, demand, sensitivity, Data, and common correction implementations are unchanged. All 793 historical files in the frozen integrity manifest remain byte-identical. This is the recorded history scope, not a claim to have hashed every file in the repository.

## Regression record and limits

The final regression collection includes common utilities, Task, all propagation tests, DOE, pipeline paths, CLI boundaries, and source-audit services. The final summary records exact per-group commands, results, and before/after source hashes. Focused runs overlap the broad suite and are not added to its total. Earlier groups were deliberately interrupted before source-format/projection updates and the optional-expected teaching correction; interrupted groups are not counted as passes.

Skipped tests: 1. The Windows symlink-input test cannot create a link without the required operating-system privilege; it is not counted as passed. The exact original diagnostic is retained in verification/skipped-tests.json.

Coverage, valid references, no reported review findings, and deterministic analysis completion do not prove task completeness, sensitivity completeness, minimality, indispensability, or absence of DOE. The examples are assistant-authored teaching/regression fixtures, not model outputs or an independent expert gold standard. The prior online failures are development evidence, not fresh unseen evaluation.

## Review artifacts

- [Complete annotation context](examples/annotation-context.json)
- [Valid annotation](examples/annotation-valid.json)
- [Structurally valid semantic contrast](examples/annotation-semantic-contrast.json)
- [Complete review context](examples/review-context.json)
- [Valid review response](examples/review-valid.json)
- [Rejected CFG evidence contrast](examples/review-rejected-evidence.json)
- [Rendered annotation prompt](prompts/annotation-after.txt)
- [Rendered review prompt](prompts/review-after.txt)
- [Prompt size details](prompt-sizes.json)
- [Example validation](example-validation.json)
- [Demand derivation proof](verification/endpoint-example-demand-proof.json)
- [Change and historical integrity](verification/endpoint-integrity.json)
- [Optional expected source-seed boundary](verification/endpoint-example-guard-check.md)
- [Final regression summary](verification/regression/summary.json)
