# Interim audit of the 28 call/link cutoffs

This is a read-only source audit of the current v8 revision. It does not alter or interrupt the GA4 controller or the three-case queue. No model, Skill, compile or propagation call was added.

**Primary classification: 26 CFG/processing mismatches and 2 local capability misjudgments. None of these 28 establishes a need for a new general call-stack/exception engine.** This classification is about source expressibility, not achieved coverage.

The graph puts actual functions behind `block_029` (`function_select`), which has no incoming CFG edge. Every audited invoke has a `callee_entry_block_ref` only in metadata; its actual outgoing edges go to caller continuation/abrupt paths. The backend does not interpret that metadata as a call or bind detached callee returns. The recorded reason is therefore correct about the missing link, but often overstates it as an inability to analyze the source at all.

## Three representative distinctions

- **Fresh settings, e.g. ir_057:** the source reads `process.env` and `process.cwd()` (`settings.ts:40–48`), while the caller is an ordinary zero-input invoke. A fresh source version cannot be supplied by aliasing another settings read. Existing read and local computation can model it after the CFG source boundary is aligned. This is a generation/interface alignment defect, not an observed propagation-engine rejection.
- **Pure helper ir_135 / ir_162:** URL normalization and filter construction are local transformations of existing inputs. Existing `for_each`/yield mapping and `cases`/build suffice. No remote response or internal-call primitive is required. These two local cutoffs are capability misjudgments; their upstream parameter producers still need repair.
- **ir_270 source packet:** frozen `index.ts:355–362` contains `getAvailableFields`, calls `getPropertyMetadata()`, logs counts and returns the full metadata. The actual revision-processing SOURCE spans omit that body. The model's “not frozen here” statement must be attributed to missing delivered excerpts/qualified prior work, not called a fabricated absence of the frozen package. The call link is separately missing.

## Per-record classification

| IR | Source behavior | Primary classification |
|---|---|---|
| ir_035 | root exported-call dispatcher | cfg_processing_misalignment |
| ir_039 | documented analyze phase | cfg_processing_misalignment |
| ir_057 | validateSettings fresh settings | cfg_processing_misalignment |
| ir_080 | client validation call | cfg_processing_misalignment |
| ir_086 | client creation fresh settings | cfg_processing_misalignment |
| ir_098 | target getter fresh settings | cfg_processing_misalignment |
| ir_107 | default-date fresh settings | cfg_processing_misalignment |
| ir_129 | convenience helper API call | cfg_processing_misalignment |
| ir_135 | normalizeUrls local map | model_capability_misjudgment |
| ir_142 | selected cached client getter | cfg_processing_misalignment |
| ir_146 | selected property/site getter | cfg_processing_misalignment |
| ir_154 | date parser invocation | cfg_processing_misalignment |
| ir_162 | buildUrlFilter local constructor | model_capability_misjudgment |
| ir_219 | core API default/optional save | cfg_processing_misalignment |
| ir_227 | first orchestration API child | cfg_processing_misalignment |
| ir_232 | second orchestration API child | cfg_processing_misalignment |
| ir_237 | third orchestration API child | cfg_processing_misalignment |
| ir_242 | fourth orchestration API child | cfg_processing_misalignment |
| ir_247 | aggregate orchestration save | cfg_processing_misalignment |
| ir_256 | date comparison first report | cfg_processing_misalignment |
| ir_262 | date comparison second report | cfg_processing_misalignment |
| ir_266 | date comparison aggregate save | cfg_processing_misalignment |
| ir_270 | getAvailableFields metadata call | cfg_processing_misalignment |
| ir_299 | completed URL batch save | cfg_processing_misalignment |
| ir_323 | save-time fresh settings | cfg_processing_misalignment |
| ir_359 | list-time fresh settings | cfg_processing_misalignment |
| ir_395 | getLatestResult listResults call | cfg_processing_misalignment |
| ir_415 | getLatestResult loadResult call | cfg_processing_misalignment |

The detailed JSON includes actual inputs/outputs, predecessor/successor edges, each source excerpt, whether it appeared in the revision-processing SOURCE view, original gap text, interface citations and a conceptual minimal correction for every row.

## Correction scope, without implementing it

Align each real acquisition/save/call summary with actual CFG sources and output versions, or connect a bounded source-backed body through explicit data/control edges. Do not infer return values from adjacency, reuse stale settings, compute remote/file data from request arguments, replace local map occurrence semantics with whole-array compute, or assume a saved filename belongs to the preceding analysis. A simple supported summary is sufficient where the source supports it; an arbitrary internal invocation engine is not a prerequisite.

The 26 mismatch classification is conservative about keeping CFG semantics correct: even when a permissive processing validator could accept a new read in an ordinary invoke, that would leave the source graph falsely describing a source-free ordinary operation. The two misjudgments specifically have sufficient existing local operands.

No exact completeness/accuracy percentage follows from this audit. The controller's final propagation, DOE, source review and replay remain the evidence for the actual run.
