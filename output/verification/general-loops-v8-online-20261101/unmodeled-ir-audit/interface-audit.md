# Independent interface audit of the v8 GA4 unmodeled IRs

This is a read-only engineering audit of the revision candidate in `experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322`. It does not alter the running controller, queue, implementation, prompts or frozen source, and sends no findings to a target context. It is not a source accuracy score or a propagation run. The candidate graph is `graph/revision.json`; the corresponding model fragment is `steps/revision-processing/value.json`. The parent audit accounts for all 48 IRs and their exact categories.

## Principal conclusion

The interface genuinely lacks a generic, context-sensitive internal call/return stack and an implicit active-invocation parameter binding. However, the current modeling contract explicitly does **not** require such a stack. It permits source-backed boundary summaries and ordinary operands. Consequently, “there is no invocation primitive” can correctly explain why the **selected factored graph** cannot be annotated as written, but cannot establish that these GA4 functions require a new backend mechanism.

The current candidate mixes two abstractions: a modular interprocedural graph with named callee definitions, completion values and parameter-binding nodes, versus processing operations whose inputs must be real CFG operands and whose `call` means a paired boundary request/response. Natural-language metadata does not bridge that mismatch. A faithful annotation cannot invent the missing invocation identity or parameter operands. At the same time, treating every such conflict as an unavoidable source capability gap overstates what is missing.

The current v8 interface already supports opaque local computation, zero-argument calls, zero-input computation, source-backed case alternatives, task-local may-state replacement, predecessor-aware merge, and ordinary return operands. None of these grants arbitrary exception extraction, exact JavaScript value semantics or missing source provenance.

## Evidence in the actual contract and implementation

All implementation paths below are relative to `D:/projects/SkillFlow`.

| Capability | Actual contract and limit | Evidence |
|---|---|---|
| Pure local computation | Unknown inputs or internal details alone are not unrepresentable. Preserve actual inputs and possible dependencies. Do not replace an external acquisition with parameter computation. | `src/skillflow/common/abstraction.py:4–7`; `src/skillflow/document_guided/annotation_wire.py:48–49` |
| Granularity | No line-by-line expansion or internal call stack is required. Actual boundaries, alternatives and named state effects may be summarized. | `src/skillflow/common/abstraction.py:16–26` |
| Value references | Only enclosing-IR input, lexical local, JSON literal and alternatives are available. There is no callee-argument/global-result reference variant. | `src/skillflow/propagation/contracts/values.py:13–42` |
| Input meaning | `input(index)` must exist in this IR. `external_resource` denotes a boundary, not payload. A lexical local must already be defined. | `src/skillflow/propagation/contracts/specs.py:623–642`; `src/skillflow/propagation/interpreter.py:185–207` |
| `call` | `location`, ordered `inputs`, `output`; expands to exact paired `deliver` and `receive`. It does not dispatch a named CFG function body or bind its parameters. Empty argument lists are legal. | `src/skillflow/document_guided/annotation_wire.py:45,87–96,421–426` |
| Atomic semantics | The union includes read, receive, deliver, write, select/exclude/update/build/compute/filter, merge/member/branch/append. It contains no generic internal invoke, dynamic caller return, catch binding or completion-value extraction. | `src/skillflow/propagation/contracts/specs.py:272–285` |
| Local observation | `mode=local, returns=[]` permits local processing without inventing a model observation. Output binding and case yield are not themselves model observations. | `src/skillflow/document_guided/annotation_wire.py:38,43` |
| Cases and exceptions | Cases preserve normal/pre-request/post-request/local-error alternatives and boundary operations. Throwing cases cannot yield normal output. At least one return candidate is required for a summary; always-throw paths belong in the CFG. Cases are not a general exception interpreter. | `src/skillflow/document_guided/annotation_wire.py:40,122–151` |
| May state | Inside an explicit case, `write(mode=replace, may=true)` is allowed only on a task-local `runtime_context`. It does not specify an arbitrary library's state transformer. | `src/skillflow/propagation/contracts/specs.py:871–878` |
| Zero-input compute | `inputs=[]` and `dependencies=[]` satisfy arity. Interpreter emits one opaque result because the empty operand product has one tuple. Exact JS value identity is not inferred. | `src/skillflow/propagation/contracts/specs.py:212–222`; `src/skillflow/propagation/interpreter.py:232–254,562–564` |

These rules were also present in the actual revision-processing request. `steps/revision-processing/prompt.txt:1545–1570` contains the shared granularity text, including the no-internal-stack sentence at line 1558; line 1633 contains the zero-argument `call` rule. This is not a proposal to add a previously absent abstract permission to the prompt.

## Concrete diagnosis and counterexamples

### Internal calls and parameter binders

A real pure local helper that transforms a provided `dateRange` can be summarized with that argument as a CFG input and an opaque local result, retaining a possible dependency. A helper that reads credentials, performs an API request and saves a result needs those actual boundaries and their conditions retained; one input-to-output compute would be false. Neither example inherently requires a general call stack.

By contrast, a zero-input `bind_parameters` node cannot legally use `input(0)`, and the word “active invocation” in graph constraints does not give it an input. The interpreter's `resolve` method handles only concrete operands and scoped locals. Similarly, a callee name in metadata cannot make an opaque receive inherit the body’s API/credential/save provenance. A repair would need to align the graph's real values and boundaries with the existing semantics; merely changing processing prose cannot repair the current missing edges.

The selected graph's top-level constraints explicitly call it a “factored interprocedural CFG” and assert dynamic caller-specific completion routing. Those are model assertions, not additional executable primitives. A named callee reference without actual program semantics does not provide call/return matching.

### `ir_205` and `ir_211`: undefined is a precision limit, not proof that no output is possible

Both selected instructions are `make_undefined`, have no inputs, and expose one result. The actual frozen source has real conditional expressions ending in `undefined` at `source/inputs/package/scripts/src/api/indexing.ts:174–185` (the two specific expressions are at lines 179 and 185). Their recorded gap citations to `index.ts:331–336` and `SKILL.md:89–92` do not directly locate those expressions.

There is no JSON literal for JavaScript `undefined`; using JSON null would change semantics. That part of the gap diagnosis is correct. But the broader claim that an input-free output cannot be represented is false: a source-supported local evaluation can use `compute` with no inputs and produce an opaque, distinct local value. This represents the real expression without inventing external acquisition or adding model observation. The result is **not** an exact representation of `undefined`: optional-property existence, JSON serialization omission and equality to null remain precision questions. Such downstream judgments must not be claimed resolved by the opaque result.

An alternative future graph may express actual omission via a source-backed conditional construction when that is truly the consumed semantics. It must not silently change an in-memory `undefined` property into absent/null everywhere merely to satisfy schema. No such modification was made during this audit.

### `ir_019`: dotenv environment initialization

The source imports `config` and calls it at `scripts/src/config/settings.ts:5–9`, with a comment that it loads `.env` from the current working directory. The selected IR has three resource operands (the imported interface, `.env`, process environment), and one `dotenv_completion` output. Those resources cannot directly be treated as data payload inputs.

The interface does have the components for a bounded source-backed state summary: read actual prior state, preserve source-supported acquisition, produce a distinct possible post-state, and use a case-local may replacement on a task-local environment snapshot. Unknown library precedence or return details alone do not justify asserting that no state summary capability exists.

This is not a complete executable dotenv specification. The frozen source does not include the dependency implementation, so exact parsing, file-error behavior, precedence, affected-key conditions and result-to-environment relationships cannot be invented. A tool receive cannot be relabeled as the environment state if that is not the library's actual return. The selected IR also does not itself carry a defined data operand for a pre/post environment version. Thus this gap combines missing/uncertain source relations with the selected graph's versioning granularity, rather than proving that every initialization effect is unsupported. Whether a conservative summary suffices for a downstream claim must be checked at that claim.

### `ir_293`: catch value is missing from the selected graph

The instruction's three operands are a log completion, a call completion and a successful member value. The `url_loop_success` incoming metadata asks for “exception raised while projecting or appending this received value,” while the operand is still the successful API value. A predecessor merge cannot turn that success value into its unrepresented exception. An unguarded alternatives union would also lose predecessor correspondence.

Cases can retain a source-backed exception acquisition and caught error record where the protected boundary and catch source are real. They cannot fabricate the exception of arbitrary local projection from URL or API data. The exact current node therefore has a real graph/processing mismatch. It does not prove that ordinary source-level per-item catch is generally unsupported. The unsupported precision is extracting a thrown value from a completion that has no explicit typed representation or source value.

### `ir_419`: global abrupt completion

The global abrupt merge combines 48 completion/value operands and metadata about their originating predecessor. Actual `merge` can select an already available value by predecessor. It cannot reconstruct a missing local exception, identify the dynamic caller, or unwrap an arbitrary completion from a prose opcode. If the CFG already exposed each thrown value and its predecessor, the ordinary merge relation would apply. The current graph additionally asks for generic completion/caller semantics that the interface does not implement.

This is an interface boundary for the **chosen representation**, and a source-boundary/graph-design mismatch at the overall workflow level. It should not be counted as evidence that explicit-loop propagation cannot converge: these are different mechanisms.

## Source delivery is a separate cause

The repair prompt does not deliver all frozen source bodies verbatim. It includes `RELATED SOURCE` spans. In `steps/revision-processing/prompt.txt`, the only direct indexing source spans are `indexing.ts:57–80` at line 446 and `indexing.ts:89–105` at line 473. The optional undefined construction at lines 162–185 is absent from that source view. Its existence in the frozen package does not mean the processing model was given those exact lines.

Likewise, direct `index.ts` spans stop at 346 (prompt line 1449) and resume at 364 (line 1498), excluding `getAvailableFields` at source lines 355–362. The `PREVIOUS WORK` text at prompt line 62 actually summarizes that function and cites its real body. Therefore “not in the frozen source” is false; “not in the direct source spans supplied to this stage” is true. A missing source-view segment should not be attributed entirely to model reluctance or entirely to backend inability.

A further read-only check confirmed that all four actual prompts (`steps/graph/prompt.txt`, `steps/processing/prompt.txt`, `steps/revision-graph/prompt.txt`, and `steps/revision-processing/prompt.txt`) carry the same indexing and index source spans listed above. The omission is therefore cross-stage, including initial generation; it is not specific to repair. This audit does not infer which source-selection algorithm caused it.

## Minimal in-memory checks and limits

No solver, replay, target call or Skill execution was performed. Small schema checks confirmed:

1. `FlatProcessing(mode=local, ops=[compute(inputs=[], output=...)], returns=[])` is accepted; default dependencies become `[]`.
2. `FlatCall(location=..., inputs=[], output=...)` is accepted.
3. A low-level `ComputeOp` with empty inputs/dependencies and real source evidence is accepted.
4. Python's empty operand product is `[()]`, consistent with the inspected interpreter path producing one opaque result.

The preliminary low-level checks without evidence, with an empty evidence list and without an evidence reason were rejected as required; those attempts did not reveal an operand-arity limit. The corrected final low-level object included source file, line range and reason. These are schema/implementation checks only, not proof that a full replacement candidate compiles, that propagation is complete, or that the final DOE is accurate.

## Implication for the parent audit

Classify at least three distinct questions for every gap: (1) can this **current graph** be annotated without inventing facts; (2) can the **source behavior** be expressed by the current boundary/operand abstraction; (3) what **exact source relation or language precision** remains unresolved. Those answers can differ. The evidence supports graph/processing abstraction mismatch and incomplete source delivery as major causes, with narrower genuine precision limits around dynamic invocation/completion identity, exact undefined behavior and dependency-internal effects. It does not support describing all 48 as a failure of the loop backend or as proven necessary new language features.
