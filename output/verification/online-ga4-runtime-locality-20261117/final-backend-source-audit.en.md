# Terminal analysis: backend and source-boundary audit

This report covers the saved terminal analysis of `document-guided-ga4-runtime-locality-high-20261117-205158`. It was produced solely by reading this run's JSON, complete source, and frozen code. It does not invoke validation, propagation, DOE, models, Skills, tests, or replay. The sole replay and process closure remain controller-owned and are reported separately by root.

The analysis is **partial**. The failed graph repair returned no complete answer, so revision processing, mapping, sensitivity and re-review were skipped. The selected bundle remains the original **49-requirement Task, inherited 489-IR CFG, original annotation and its bound initial review**. The completed 60-requirement Task revision is unselected. All 44 initial review findings remain unresolved by repair; none is silently treated as fixed.

## Observed propagation and boundary records

Propagation is `incomplete`: **470 processed, 4 unmodeled and 15 blocked IR**, with 470 committed IR records and 1033 Data records. The encountered unmodeled IR are `ir_001`, `ir_289`, `ir_295`, `ir_436`; blocked coverage is `ir_002`–`ir_013`, `ir_290`, `ir_296`, `ir_437`. The separately declared unmodeled `ir_011` is within the blocked entry continuation and was not encountered as an executed unmodeled instruction.

There are **zero typed `operation_execution_error` diagnostics** in this run. The new failure-isolation mechanism therefore has offline evidence but no triggering online instance here. `ir_148` and `ir_151` are both processed. This is not an isolated causal comparison to the previous run: the generated annotation changed, and `ir_151` now represents `normalizeUrls` through an opaque tool request/response rather than exercising the previous internal collection-operation shape.

All 16 frozen source files match their snapshot hashes. Physical source sites map one-to-one to inherited CFG instructions and now have committed boundary records:

| Source site family | Physical sites | Sites with corresponding processed boundary record |
|---|---:|---:|
| Remote SDK calls | 13 | 13 |
| Calls to `saveResult` | 25 | 25 |
| Filesystem calls in storage utility | 7 | 7 |

These are **abstract record-reach counts**, not Skill execution, verified recipient correctness, complete source behavior, or task necessity. For six remote sites, an explicit CFG client operand exists but its entry-state Data IDs do not appear directly in the remote inputs; the authored calls use only the request. The other seven realtime/metadata sites acquire local `ga` through `getClient`, but the entire IR contains no value reference to that local output. Thus service endpoint presence still does not establish the actual receiver/authentication dependency. Twenty-five logical storage writes do not prove correct caller operation/extra/address relationships; seven filesystem records include the still-disputed directory path-as-payload representation. All nineteen newly wrong report-return bindings identified by F010 are themselves `processed`, illustrating why coverage cannot stand in for source faithfulness.

## Two local `missing_part` diagnostics

Both diagnostics have produced IR records and `processed` coverage:

- `ir_457`, compiled event 0 / op 0, selects `['value']` from the read outcome `result_242`.
- `ir_459`, event 0 / op 0, selects `['value']` from the parse outcome `result_243`.

The diagnostic bases are complete **failure wrappers** with `fulfilled: false` and `exception`; the success wrappers contain `fulfilled: true` and `value`. Frozen source `skill/scripts/src/core/storage.ts:103–114` reads and parses inside `try`, returning null on the caught failure. CFG `ir_456` and `ir_458` select `fulfilled` and branch before the success-body selections. Saved branch alternatives correctly distinguish literal true from false, but both original wrappers remain in the success consumer's entry state. The selector succeeds on the success wrapper and reports the absent field on the unrefined failure alternative.

This is not unknown-address aliasing, an absent field in the valid success wrapper, or a demonstrated erroneous source field name. The saved state and frozen `solver.py:69–116` show a discriminator/container correlation limitation: a local branch input is associated with a state location only when it is also that IR's public output binding; these dispatch instructions have no outputs, and the branch alternatives' binding maps are empty. The original wrapper version is not narrowed by its selected discriminant. `interpreter.py:677–691` correctly records the missing part for the candidate actually supplied.

Each diagnostic becomes one IR-local `upstream_diagnostic` in demand. The ten assessments at these two IR contain ten unresolved ranges. They do not cause the 15 blocked-IR count or a whole propagation abort. A future fix should preserve sound correlation between supported discriminator selections and the original wrapper version, testing true/false and independent state; it must not infer inverse behavior for opaque computation or relax the missing-field guard. No such fix was made during this frozen run.

## Bound review, demand and DOE

The demand result receives exactly the selected review receipt, SHA256 `9cd2b0d3b6f34b71f59b2f0eb99d2233872a3dc5d41b19c0829333635956d8b9`. Its review status is `complete`, with **503 accepted / 25 rejected checks** and **1625 accepted / 110 rejected scopes** over 528 obligations / 1735 scopes. There are no structural validation barriers in this receipt. However, `source_review_complete` is **false** because the review's input material is partial (`core.partial=true`); the original review is diagnostic-only and retains 44 findings. Complete receipt coverage is not a clean semantic verdict or authorization to reuse it for different contracts.

Demand is partial. It contains **2004 input assessments**: 1091 operation inputs, 590 CFG inputs, and 323 acquisition outputs. Their coverage is 1989 processed / 13 blocked / 2 unmodeled. Actual range entries are:

| Range status | Count |
|---|---:|
| Required | 497 |
| Unresolved | 3078 |
| Deletable | **0** |

There are **zero non-null modification recipes**. Counts are repeated range entries across uses, goals and information properties, not unique fields. The 497 required entries remain conditional on the selected representation and its unresolved source findings.

There are **250 blocking diagnostics: 70 global and 180 IR-scoped**. The global group comprises 40 `requirement_expression_gap`, 27 `unbound_requirement`, and 3 `task_source_issue`. Selected realizations are 27 retained-only, 13 partial and 9 expressed. The scoped group comprises 108 rejected-contract diagnostics, 22 output-contract selector gaps, 20 processing gaps, 19 upstream-coverage diagnostics, 6 upstream diagnostics, and 5 expected-relation mismatches. The latter yield five `wrong_input` findings at `ir_145`, `ir_153`, `ir_160`, `ir_258` and `ir_270`; they are not five proven excessive fields.

The **22 exact output-selector gaps affect 13 IR**. They include 11 value demands, 10 truth demands and one shape demand; 12 have nonempty paths. Examples are `ir_167.rowLimit/startRow/save/dimensions`, `ir_034.clientEmail/privateKey`, `ir_440.resultsDir`, `ir_150` member-value/shape and `ir_030.valid` truth. This is observed use of the conservative whole-output rule boundary, not merely an anticipated limitation. Source-authored per-output contracts or existing deterministic constructors are needed where the output structure supports them; a whole-value contract cannot certify every child/property.

DOE is partial with **123 sinks, all with recorded payload, and 295 comparisons, all `no_excess_established`**. Both declared constraint checks remain `not_established`; no preservation/reduction recipes were generated. This does not prove there is no excess acquisition.

The earlier static hypothesis about upstream deletion when a required action lacks records was neither reproduced nor refuted by this run. No deletion was published, and 70 global blockers prevent this result from isolating that hypothesis. It remains a proposed offline regression, not an observed false deletion or a claim that the risk has been eliminated.

Evidence: `final-backend-source-audit.json`, SHA256 **`d3dd1b37fe8574e7672033ccbb29fedae56bb229d830d0e6249a95e4297d3eb0`**. It binds selected artifacts and code, preserves exact source-site/operation/Data coordinates and both missing-part cases, and contains every terminal range/finding count. No automatic rewrite or extra experiment was performed.
