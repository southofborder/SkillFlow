# GA4 provisional initial processing audit

Status: **PROVISIONAL; source review is pending.** Captured 2026-11-11T18:35:37.609614+08:00.

Initial processing SHA-256: `bc438b2cad3fd2f9572f05db74f9ae48d91b4cab4433edd544cf88120f22529c`.

The fragment models 531 of 535 CFG instructions and records 12 processing gaps, including four explicit unmodeled instructions. It contains 67 compute operations: 22 expressions and 45 demand transfers. All transfers have one rule, and none declares output_parts. Its 109 call operations include 13 remote calls and 96 local-tool/helper calls; 67 calls have actual data inputs. No call carries an input_contract.

These counts describe initial annotation contents. They do not establish processed propagation, accepted semantic contracts, precise demand, deletability or final DOE status. The scheduled source-review stage may repair them.

## Provisional source comparisons

### C01 — initial_missing_tool_contracts

All 13 directly represented remote calls have actual request payload construction and response selections, but none carries input_contract. The whole fragment has zero input_contract attachments across 109 call operations. The 45 compute contracts cannot substitute for trusted interface-required fields of these calls. This is an initial completeness limitation, not a final accepted finding; source review is pending.

Processing: `/ir_semantics/ir_101`, `/ir_semantics/ir_163`, `/ir_semantics/ir_177`, `/ir_semantics/ir_208`, `/ir_semantics/ir_218`, `/ir_semantics/ir_228`, `/ir_semantics/ir_238`, `/ir_semantics/ir_248`, `/ir_semantics/ir_260`, `/ir_semantics/ir_272`, `/ir_semantics/ir_282`, `/ir_semantics/ir_299`, `/ir_semantics/ir_317`.

Source: `scripts/src/api/reports.ts:88-100`; `scripts/src/api/searchConsole.ts:102-111`; `scripts/src/api/indexing.ts:149-157`.

### C02 — initial_gap_scope_requires_review

The ir_101 processing gap names missing complete upstream required/optional/admissible wire-field schemas and SDK internals. It is a specific limitation, but is not an independently accepted per-input contract and does not account for all 13 remote calls or 54 nonempty local-tool calls. Source review must distinguish source-supported query inputs from genuinely missing interface semantics; the audit does not supply invented upstream schema fields.

Processing: `/processing_gaps/1`.

Source: `scripts/src/api/reports.ts:20-28`; `references/api-reference.md:31-45`.

### C03 — source_aligned_for_authored_selector

The full Settings rule requires only five named optional environment values plus cwd; validation requires only truth of propertyId/clientEmail/privateKey; property formatting selects propertyId; directory construction selects resultsDir. These are useful field/property distinctions for their authored selectors. Every opaque compute has either a demand transfer or an expression, but these have not yet been independently accepted.

Processing: `/ir_semantics/ir_017`, `/ir_semantics/ir_020`, `/ir_semantics/ir_023`, `/ir_semantics/ir_483`, `/ir_semantics/ir_512`.

Source: `scripts/src/config/settings.ts:40-74`; `scripts/src/core/client.ts:50-53`; `scripts/src/core/storage.ts:64-65`; `scripts/src/core/storage.ts:123-125`.

### C04 — precision_limit_exact_output_selectors

All 45 transfers have exactly one rule: 38 whole-value outputs, four truth outputs and three message-field outputs. None declares output_parts. Full Settings, validation, calendar ranges and inspection base/mobile/rich values therefore have no authored exact child-output rule or reviewed closed decomposition. A narrower requested output must remain unresolved at an unmatched selector; the audit does not treat the whole-output row as a narrow-output necessity proof.

Processing: `/ir_semantics/ir_017`, `/ir_semantics/ir_020`, `/ir_semantics/ir_083`, `/ir_semantics/ir_087`, `/ir_semantics/ir_319`, `/ir_semantics/ir_321`, `/ir_semantics/ir_325`.

Source: `scripts/src/config/settings.ts:40-74`; `scripts/src/api/searchConsole.ts:64-83`; `scripts/src/api/indexing.ts:161-185`.

### C05 — represented_with_remaining_helper_boundary

The earlier graph-only settings-read concern is now explicitly represented by a call to in-process getSettings in ir_047/ir_057, followed by clientEmail/privateKey selection and construction of credential/scopes options. However, this is still a zero-input tool call, not an expanded settings-read body. Source provenance and necessity across that helper boundary remain unverified. Remote call ir_101 also intentionally omits its client receiver from the data payload; this omission alone does not prove that client initialization is unnecessary.

Processing: `/ir_semantics/ir_038`, `/ir_semantics/ir_047`, `/ir_semantics/ir_057`, `/ir_semantics/ir_101`.

Source: `scripts/src/core/client.ts:33-42`; `scripts/src/core/client.ts:67-79`; `scripts/src/api/reports.ts:88-100`.

### C06 — represented_with_local_unmodeled_cutoffs

Metadata dimensions and metrics use explicit select_part and build with the source fallback, so they keep their distinct branches. checkIndexStatus explicitly selects value.indexStatus and derives indexed by an expression over verdict. The direct inspection base/mobile/rich transfers name source fields, but absent-section merges ir_323/ir_327 are explicitly unmodeled because undefined is unavailable in their CFG operands. This prevents claiming that the complete inspection path is solved.

Processing: `/ir_semantics/ir_250`, `/ir_semantics/ir_262`, `/ir_semantics/ir_319`, `/ir_semantics/ir_321`, `/ir_semantics/ir_325`, `/ir_semantics/ir_380`.

Source: `scripts/src/api/metadata.ts:46-76`; `scripts/src/api/indexing.ts:161-185`; `scripts/src/index.ts:331-336`.

### C07 — initial_semantic_overstatement_watchpoint

ir_521 marks the whole path-array value as required while its own reason says values outside slice(0, limit) do not affect the output. The remainder is marked unresolved with a specific unsupported symbolic-slice selector gap. Whole-value required plus that gap is not evidence that every original member is semantically necessary. For a valid positive limit smaller than the list, the unused suffix is a concrete counterexample to such a necessity claim. This remains an initial review item.

Processing: `/ir_semantics/ir_521/segments/0/ops/0/demand_transfer`.

Source: `scripts/src/core/storage.ts:141-143`.

### C08 — initial_conditional_overstatement_watchpoint

The original-date label transfers in ir_103 and ir_179 request shape plus the whole input value whenever present. Source returns undefined for every non-string input; changing fields of a present date-range object does not change this label. if_present tests absence, not the source string-type condition. These rows therefore need source-review qualification before their present non-string field values can be called necessary.

Processing: `/ir_semantics/ir_103/segments/0/ops/1/demand_transfer`, `/ir_semantics/ir_179/segments/0/ops/1/demand_transfer`.

Source: `scripts/src/api/reports.ts:104-104`; `scripts/src/api/searchConsole.ts:117-117`.

### C09 — represented_without_minimality_certificate

All 25 internal save sites use deliver to the in-process save helper with no returned value. The direct save entry separates filepath construction from wrapper data/propertyId and serialization. JSON.stringify requests the complete wrapper value, and source forwarding remains intact. This representation does not settle whether each saved field has an independent task purpose or whether a whole serialized payload is the minimal requested result.

Processing: `/ir_semantics/ir_104`, `/ir_semantics/ir_491`, `/ir_semantics/ir_495`, `/ir_semantics/ir_496`.

Source: `scripts/src/core/storage.ts:58-95`; `scripts/src/api/reports.ts:102-108`.

### C10 — source_aligned_cardinality_scope

The available-fields logging transfers use dimensions/metrics cardinality if present, explicitly excluding member contents. This is a concrete information-property distinction in the initial contracts; no claim is made that the independent full metadata return has the same reduced requirement.

Processing: `/ir_semantics/ir_478/segments/0/ops/0/demand_transfer`, `/ir_semantics/ir_478/segments/0/ops/2/demand_transfer`.

Source: `scripts/src/index.ts:355-361`.

### C11 — explicit_unmodeled_and_incomplete_outcomes

Four CFG instructions have no modeled semantics: ir_323, ir_327, ir_342 and ir_345. The last two concern distinguishing normal low-level batch completion from an uncaught rejection and forwarding the thrown value. The high-level try summaries preserve pre-request versus post-request alternatives but retain stated limits about cache effects and whether a normal reply preceded an exception. The fragment has 12 processing gaps total, of which four are unmodeled; these counts must not be conflated.

Processing: `/processing_gaps/2`, `/processing_gaps/3`, `/processing_gaps/4`, `/processing_gaps/5`, `/ir_semantics/ir_359`, `/ir_semantics/ir_378`.

Source: `scripts/src/api/indexing.ts:89-105`; `scripts/src/index.ts:305-341`.

### C12 — specific_summary_limit_preserved

The source summary gap explicitly distinguishes possible whole observation from whole-field necessity and does not invent a Markdown writer or user delivery from an ordinary reader return. This remains a useful source boundary, not a complete summary path.

Processing: `/processing_gaps/11`.

Source: `SKILL.md:53-64`; `SKILL.md:129-142`; `scripts/src/core/storage.ts:123-171`.

## Contract granularity

The 45 authored output selectors comprise 38 whole-value rules, four truth rules and three error-message rules. Their 64 input rows contain 83 required selectors, including 24 if_present selectors. Sixty-three remainders are independent and one is unresolved; no input row has an empty required list. The initial contracts therefore demonstrate field exclusions and information-property distinctions, but do not yet demonstrate an entirely irrelevant declared compute input.

Specific initial review items are the whole-array requirement on a variable slice and whole present-value requirements on string-only labels. Missing exact child rules also limit field-level demand through composite blackboxes. These observations are recorded without feeding the running pipeline.

## Evidence and continuation

`ga4-processing-provisional.json` preserves all 45 compute contracts with exact pointers, all 109 call sites, the 13 remote/25 save source crosswalks, gap details and artifact hashes. Original source files remain byte-identical. Source-reference range checks are recorded separately from semantic review.

If later repairs change processing or CFG, preserve this initial capture and compute a final reviewed comparison after closure. Do not relabel the initial omissions as final findings or count structurally modeled IR as processed IR.
