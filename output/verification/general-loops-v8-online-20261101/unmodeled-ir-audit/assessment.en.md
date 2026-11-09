# Interim diagnosis of all 48 unmodeled GA4 v8 IR

This is a read-only audit of the revised candidate selected for propagation in the ongoing fresh GA4 run. It is not the final propagation or DOE assessment. No production code, prompts, run inputs, controller, queue or selected output was changed; no audit findings were sent to a target. Three independent assistant reviewers checked bindings, calls and interfaces, with the parent checking five special IR and reconciling all 48 records. These are assistant engineering judgments, not human gold labels.

## Result

| Primary local diagnosis | IR count | Meaning |
|---|---:|---|
| CFG/processing abstraction and data-link mismatch | 43 | 15 empty-input binders, 26 internal-call links, and 2 exception/completion merges. The current graph often cannot be annotated faithfully as written; its missing value relationships must not be fabricated. |
| Overbroad unsupported judgment despite existing local operations | 4 | normalizeUrls (ir_135), buildUrlFilter (ir_162), and real undefined expressions (ir_205/211). The latter remain opaque and do not establish exact JS serialization behavior. |
| Mixed boundary-summary underuse and genuine source precision uncertainty | 1 | dotenv initialization (ir_019). A possible state summary can preserve known effects; missing library internals cannot be invented. |

These are mutually exclusive primary diagnoses for accounting, not exclusive root causes. Source-view omissions and narrower precision limits overlap them. The audit found no IR for which the evidence establishes that a new general loop or call-stack engine is the only way to analyze the underlying GA4 behavior. This does **not** mean the current interface supports arbitrary invocation, exceptions, language values or library semantics.

The selected annotation has 372 modeled IR and 48 source-declared unmodeled IR out of 420 (88.57% / 11.43%), plus 14 other source processing gaps. None of these 48 is a program validation-isolation record. This ratio is annotation coverage only. A cutoff at an early binder/call can block many later modeled IR, so it must not be presented as actual propagated coverage or source accuracy.

## What is actually wrong

**The generated graph chose a modular interprocedural notation that the processing interpreter does not execute.** All 28 audited invoke instructions identify a callee in metadata while their actual outgoing edges lead to caller normal/exceptional continuations, not the callee. The function_select block has no predecessor. The solver nevertheless seeds predecessor-free blocks as independent roots, so the accurate description is absent caller linkage, not unreachable code. A callee name, prose argument_binding or generic completion name cannot provide a call frame or return identity.

All 15 parameter binders have inputs=[]. Processing is locally correct to reject invented input(0). For example, ir_322 must bind the actual API response or constructed comparison passed to saveResult; rereading root invocation arguments would substitute a request for the response. Similarly, the bulk URL binder ir_275 loses the array before the loop starts. These facts do not diagnose a failure of finite loop convergence.

The existing abstraction contract already says not to require an internal call stack and to preserve source-supported boundary summaries. The main correction would be aligning actual CFG operands/control/boundary summaries with that contract. Simply telling processing to fill every record would encourage invented data relations. A generic internal call stack is indeed absent, but the chosen graph need not have required one.

**Four whole-IR cutoffs overstate a local capability limit.** normalizeUrls (bulk-lookup.ts64–75) maps its real input URLs using trim and a conditional leading slash. Existing for_each/member-local computation and yield/output preserve order and duplicate occurrences. buildUrlFilter (bulk-lookup.ts84–99) returns null for an empty array or builds a filter containing the actual URLs; existing cases/build/binding can express that. Neither needs a remote response or a general invoke primitive. This does not repair their separate upstream binder gaps.

ir_205/211 correspond to real undefined expressions in indexing.ts174–185. JSON null is not a substitute. However a zero-input local compute is accepted and creates an opaque value for a real expression; exact undefined/property-presence/serialization behavior can remain unresolved without declaring that no output is representable. Small independent in-memory type checks confirmed this structural capability. No replacement candidate was executed.

**The exception merges need real error sources.** ir_293 asks for an exception raised during projection/append while its corresponding input is the successful API value. ir_419 combines 48 completion inputs but lacks some actual local error identities. A predecessor-aware merge selects supplied values; it cannot turn a success response into an exception or infer a dynamic caller from prose. Existing bounded source-backed catch summaries can preserve actual known effects, but generic exception execution and completion unwrapping are not supplied. The source distinction between per-item catch-and-continue and failure escaping the batch must remain.

**dotenv remains mixed, not a forced all-or-nothing verdict.** settings.ts5–9 supports a config() call and .env loading. Existing cases/read/opaque state computation/task-local may replacement can preserve prior and possible post-state. The return of config must not be relabeled as process.env, nor may the analysis assert unconditional update. Exact precedence, errors, affected keys and return-to-state relationships are not established by the frozen dependency call site alone.

## Independent source-delivery problem

The full frozen 16-file package is not the same as the actual SOURCE text delivered to every downstream model stage. All four normal/repair graph and processing prompts have the same relevant omissions:

- index.ts SOURCE spans end at 346 and resume at 364, omitting getAvailableFields at 355–362. The real function calls getPropertyMetadata and returns the full metadata. ir_270's claim that the body is not frozen is false, while absence from that stage's direct source view is real.
- indexing.ts SOURCE spans are only 57–80 and 89–105. The real inspectUrl response construction and optional undefined expressions at 146–190 are absent.

Prior working material contains some summaries/references, which is different from supplying the implementation verbatim. The source selector uses referenced ranges and always retains the main Skill instructions; it does not establish full transitive callee coverage. This is a cross-stage material-delivery gap, not evidence that the underlying frozen source is missing. It contributes to, rather than replaces, the separate CFG data-link defects. The audit did not modify this selection during the live run.

## Runtime and scope

At the saved observation, GA4's initial and revised reviews had returned and deterministic propagation was running. There was no final DOE artifact yet. The original controller and the single small-Skill queue supervisor remained active; 001, 010 and 013 were still waiting for GA4 plus its controller-owned replay. No extra launch, restart or replay was introduced.

All 18 target requests had returned substantive answers: 7 normal, 6 shared-repair-related and 5 structural corrections. Public complete-response usage was 2,309,177 tokens: 1,981,141 input and 328,036 output. Cached input 928,512 and reasoning output 62,953 are subsets, not additional tokens. Outer retry count was zero. Earlier internal CLI reconnect errors remain in the record; exact provider HTTP attempts and their unreported usage are unknown. The token total is for the measured target run, not this assistant audit's unmeasured overhead. Running elapsed time is not final analysis/replay time.

## Evidence and validation

The JSON summary contains all 48 unique IR exactly matching the selected candidate's unmodeled set; 99 source ranges were checked for valid file/line bounds. The six candidate snapshot hashes remained unchanged. Detailed evidence includes original gap reasons, actual CFG inputs/edges, exact source excerpts, interface references and minimal conceptual corrections. These are diagnosis and local feasibility arguments, not tested fixes or claims of improved DOE accuracy.

- [Machine-readable combined summary](audit-summary.json)
- [15 binding records](binding-audit.json) and [binding brief](binding-audit.md)
- [28 call records](call-audit.json) and [call brief](call-audit.md)
- [Five special records](special-audit.json)
- [Independent interface audit](interface-audit.md)
- [Original candidate snapshot](candidate-snapshot.json)

## Per-IR primary classification

| IR | Primary diagnosis | Detail artifact |
|---|---|---|
| ir_019 | Boundary summary plus source precision | [special-audit.json](special-audit.json) |
| ir_035 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_039 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_053 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_057 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_075 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_080 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_086 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_097 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_098 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_105 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_107 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_127 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_129 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_133 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_135 | Overbroad unsupported judgment | [call-audit.json](call-audit.json) |
| ir_142 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_146 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_154 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_162 | Overbroad unsupported judgment | [call-audit.json](call-audit.json) |
| ir_205 | Overbroad unsupported judgment | [special-audit.json](special-audit.json) |
| ir_211 | Overbroad unsupported judgment | [special-audit.json](special-audit.json) |
| ir_219 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_222 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_227 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_232 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_237 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_242 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_247 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_251 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_256 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_262 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_266 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_270 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_275 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_293 | CFG/processing mismatch | [special-audit.json](special-audit.json) |
| ir_299 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_303 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_317 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_322 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_323 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_346 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_358 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_359 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_394 | CFG/processing mismatch | [binding-audit.json](binding-audit.json) |
| ir_395 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_415 | CFG/processing mismatch | [call-audit.json](call-audit.json) |
| ir_419 | CFG/processing mismatch | [special-audit.json](special-audit.json) |
