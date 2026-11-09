# Interim audit: fifteen unmodeled parameter-binding IR

Run: `document-guided-ga4-general-loops-high-v8-20261101-214322`. This report audits the revised candidate only; it is not a final propagation/DOE result.

**Finding: all 15 are primarily CFG/processing misalignment.** Every assigned binder has `inputs: []`; actual caller identity/arguments live only in metadata or textual edge conditions. Existing source behavior can be expressed through actual CFG operands and source-backed call-boundary summaries. A new generic binding engine is not established as necessary by these examples.

The processing refusal to invent `input(0)` is locally justified. It would be misleading to call these fifteen solely model laziness or solely unsupported source behavior. The faulty contract spans graph generation and processing. Unknown contents of an actual parameter do not make its source identity unavailable.

`block_029/function_select` has no predecessors, but it is NOT unreachable by solver definition: all predecessor-free components are roots (`solver.py:165`). It receives seed state, not a caller frame. Natural-language incoming-edge labels on the other fourteen blocks cannot transfer actual call arguments.

| IR | Source behavior | Primary classification | Smallest conceptual repair |
|---|---|---|---|
| ir_053 | Selected function and invocation arguments | CFG/processing misalignment | Connect the real invocation operand/version to the selected entry, or use separate source-backed entry contexts plus caller-site summaries. Keep internal callee arguments distinct from top-level invocation arguments. |
| ir_075 | Client getter selection | CFG/processing misalignment | Keep getter-specific source branches, or pass the true selected getter identity as an explicit operand into the combined summary. Do not fabricate credentials, requests or cache state to initialize the kind. |
| ir_097 | Target getter identity | CFG/processing misalignment | Preserve the selected getter in CFG control/operands or keep separate getter summaries; then use the true settings result for the appropriate projection. |
| ir_105 | Date parser identity and actual date argument | CFG/processing misalignment | Pass the actual date argument and any true parser selection as operands. Keep missing-date/default-settings acquisition as its existing source condition and version, rather than guessing a date. |
| ir_127 | Convenience helper arguments | CFG/processing misalignment | Make the helper selection and actual optional date available through caller operands; use source literals/build for dimensions and metrics and preserve the forwarded date. |
| ir_133 | API function arguments/options/defaults | CFG/processing misalignment | Expose each actual API options/url input and real function identity in CFG or summarize each caller boundary with its real operands. Preserve option defaults and falsy save values; do not promote request arguments into response contents. |
| ir_222 | Orchestration identity and arguments | CFG/processing misalignment | Keep real orchestration branches or pass their actual selection and date. Represent fixed call lists and literal labels with existing supported constructs and preserve each call result; do not introduce a fictional loop or source read. |
| ir_251 | Date comparison arguments | CFG/processing misalignment | Pass the true two date operands and actual/defaulted dimension/metric values, preserving which date belongs to each report call. |
| ir_275 | URL list, selected batch operation and save option | CFG/processing misalignment | Supply the actual collection and operation/save selection to the loop entry. Retain duplicate occurrences and the different catch/save strategies of these source functions. |
| ir_303 | normalizeUrls collection argument | CFG/processing misalignment | Add the actual caller array operand to the function boundary or summarize at its callsite, then retain map occurrence/order/duplicates using supported member and collection semantics. |
| ir_317 | buildUrlFilter collection argument | CFG/processing misalignment | Pass the actual URL array and preserve empty/nonempty control; build the true filter object using the same array, not an invented external read or unrelated literal list. |
| ir_322 | Save payload and filename labels | CFG/processing misalignment | Pass each actual save-site payload/version and labels as typed CFG operands or summarize saving at that site. Keep different callers/versions separate. Do not replace acquired response data by its request parameters. |
| ir_346 | Load filepath | CFG/processing misalignment | Bind the actual path operand at the call boundary, then retain the existence check and file read as separate real actions. Preserve an unresolved producer-to-file identity when source does not establish it. |
| ir_358 | List category and optional limit | CFG/processing misalignment | Expose true caller category/limit values and apply the existing file acquisition, selection and conditional limit semantics; do not invent a category literal when it is runtime supplied. |
| ir_394 | Latest-result category and operation | CFG/processing misalignment | Pass category/operation into the summary and preserve the real list/filter/first-file/load lineage. Do not infer that this file is from a particular prior analysis without source evidence. |

## Concrete source examples

- `ir_075`: the three client getters are zero-argument source functions (`core/client.ts:23`, `:87`, `:109`). The generator combines them and then cannot bind its invented selection value. This is not a source parameter feature. Preserve function selection in actual control/operands or keep getter summaries separate.
- `ir_303` / `ir_317`: `normalizeUrls(urls)` maps a real array (`bulk-lookup.ts:64-76`); `buildUrlFilter(urls)` returns null or constructs an object containing that array (`:84-98`). Existing member, computation and build operations cannot conjure the removed array, but no new acquisition/binding primitive is necessary once its operand is connected.
- `ir_322`: `saveResult(data, category, operation, extraInfo)` (`core/storage.ts:58-63`) is called with a real API response (`api/reports.ts:105`) or a later comparison (`index.ts:200`). Passing/re-reading original request arguments instead would corrupt the saved-data provenance. This needs true producer-to-save operands, not a fabricated compute or input.
- `ir_275`: the missing `urls` parameter precedes the loops. It does not establish a defect in member occurrence or finite loop propagation. Distinct per-item catch behavior and batch failure behavior must remain separate.

## Exact contract evidence

- [CFG input/control rules](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/document_guided/cfg_wire.py:12): real inputs/context acquisition are supported, and edge text does not replace condition operands.
- [Input-reference check](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/contracts/specs.py:623): indexes must exist on the enclosing IR; an undefined local is rejected.
- [Value variants](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/contracts/values.py:13): input/local/literal/alternatives, not an implicit caller frame.
- [Processing contract](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/document_guided/annotation_wire.py:42): output bindings alias real available values; locations and computations cannot invent external acquisition.
- [Opcode contract](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/graph/ir/instruction.py:16): opcode is an open string; `bind_parameters` passing graph syntax validation does not confer executable binding semantics.
- [Independent-root behavior](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:165): missing predecessors do not mean unreachable.

The eight inspected live implementation files were byte-identical to the archived implementation snapshot at audit time. Exact per-IR source excerpts, CFG JSON pointers, reported gap text, interface line ranges and artifact hashes are in [binding-audit.json](binding-audit.json).

No production/prompt/source changes, model requests, solver execution, controller intervention or queue changes were made. These are static conceptual repairs, not validated patches; this subset does not classify the remaining 33 gaps or prove complete DOE feasibility.
