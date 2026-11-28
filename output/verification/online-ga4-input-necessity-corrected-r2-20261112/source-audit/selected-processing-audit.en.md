# Selected processing audit (source review and backend pending)

Processing `calls/a002` is selected and its saved validation is `valid` with zero diagnostics. Value identity: `533595e3e761dc816c965817bcbe8497c1a8d9f5c505170bf09308b95376d8d0`. Structural acceptance is not semantic or DOE acceptance.

## Coverage and corrected records

The 563-IR graph now has **561 modeled specifications plus two exclusively unmodeled IR (`ir_419`, `ir_423`)**, with no missing or overlapping IDs. There are **13 processing gaps: two stopping unmodeled gaps and 11 other limitations**. The two stopped scopes are optional mobileUsability/richResults merges whose absent branches need JavaScript undefined without a declared operand. Source review must still decide whether these are genuine limits or repairable representation errors.

All 63 formerly rule-only local mechanism records now cite their own actual CFG instruction as a target. `ir_114` supplies the missing row reason; `ir_173` places its value-only uncertainty in a scoped range with independent remainder. The malformed nested cases at `ir_119` were replaced by a local helper tool call. `ir_179` gained processing and no longer overlaps an unmodeled gap. The original rejected response and audit remain unchanged.

Both carry IRs (`ir_103`, `ir_126`) still bind output 0 directly to input 0, adding no compute or observation.

## Contract and gap scopes

The selected wire contains **101 computes: nine inline expressions and 92 demand-transfer contracts with 92 rules**. It also has **146 tool-input contracts across call/deliver operations**, for **209 distinct IR with at least one contract**. Raw input-index accounting matches each operation. These are wire counts; no standalone compiled obligation/review inventory receipt was materialized at observation, and this audit did not invoke its builder.

Two local contract uncertainties remain: `ir_114` requires sorted-list cardinality but records the unavailable dynamic-prefix value selector; `ir_173` retains shape and isolates type-conditioned string value demand. These are specific cited claims, not generic opacity, but their adequacy remains for source review.

## Source-boundary modeling and concrete review concerns

All **13 API sites** have call/result specifications, all **25 saver sites** have delivery specifications, and all **three explicit URL loops** have header/member/merge/append and child-case specifications. These are modeling-presence counts, not backend or semantic completeness.

Two material source-binding concerns remain visible despite structural validity:

1. **Receiver identity:** at all 13 listed SDK sites, processing consumes the request but not CFG input 0's actual client handle; corresponding remote locations have no `operand_refs` tying them to that handle. For example `ir_171` calls `ga` with input 1 only, while its reason says to use the client as receiver. Prose does not materialize receiver or creation-time credential binding. No client deletion or credential irrelevance should be inferred from this omission.
2. **Persistent saver effects:** all 25 source saveResult calls now deliver arguments to a tool location named `Local saveResult`, retained for the task. They contain no per-call persistent wrapper/write events. The independent public saver body does still write serialized metadata plus data to persistent storage at `ir_077`, but that public invocation is not automatically each call site's own settings/clock/path instance. Review must establish the actual persistent effect and wrapper scope; do not count the 25 helper deliveries as 25 correctly modeled persistent writes.

The location inventory grew to 64, including 36 tools; many are local source helper summaries. A helper signature/contract and fresh return do not alone establish its internal acquisition, writes, client state or error effects. Loop child summaries retain normal/pre-request/post-request cases and explicit gaps for clock fallback or attempted-versus-completed requests. Occurrence pairing and protected logging still require review and backend evidence.

No input assessment, deletion, propagation or DOE assertion follows from this audit. Mapping, sensitivity and source review were still pending at observation. Exact selected identities, all local gaps, contract counts, per-site instructions and receiver/saver concerns are in `selected-processing-audit.json`. No model, Skill, pipeline, validator, renderer, backend or replay was run, and no production or active-run artifact was edited.
