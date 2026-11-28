# Initial processing candidate audit (provisional)

The first processing response was rejected with **69 diagnostics: five schema, one instruction coverage and 63 mechanism-evidence references**. Response identity: `c7e575530a7399cb264a15d9581786968bfc34a82e4914c40d5fe828d8f48465`. The following describes this rejected candidate only.

## Local diagnostic causes

| Location | Cause | Interpretation |
| --- | --- | --- |
| `ir_114`, slice input requirement | Missing mandatory row-level `reason`; a separate dynamic-slice gap exists. | One contract schema error, not proof of missing source semantics. |
| `ir_119`, listed case's second segment | A nested `cases` object sits in a list of ordinary processing segments; `kind`, `output`, `cases` are rejected. | Three diagnostics for one segment-shape error. |
| `ir_173`, save-label input requirement | `remainder=unresolved` lacks its required row-level gap; only a scoped value gap is supplied. | One inconsistent gap-scope record. The supplied type-conditioned rationale is concrete but still needs semantic review. |
| `ir_179` coverage | Both an evidence-only modeled placeholder and explicit unmodeled gap. | Exact-one coverage fails; no CFG IR is wholly absent from the saved modeled/unmodeled union. |

All 63 mechanism-reference errors cite only runtime rules: **40 EM17, 22 EM16 and one EM14**. A local mechanism additionally needs a source-file or CFG-target reference. The affected CFG opcodes are **26 dispatch, 21 merge, ten member and six append**. These are traceability failures; they do not by themselves establish 63 wrong semantic operations.

## Coverage and contract inventory

The raw response has **561 IR specifications and 13 processing gaps** for the 563-IR graph. Three gaps explicitly mark `ir_179`, `ir_419`, `ir_423` unmodeled. Only `ir_419`/`ir_423` lack raw specification rows; `ir_179` is duplicated across modeled/unmodeled coverage. Validation also isolates the three malformed records `ir_114`, `ir_119`, `ir_173`, yielding 558 modeled IDs and six unmodeled IDs with the same one-ID overlap. Do not report either count as successful backend coverage.

Raw syntax contains **124 compute operations: nine inline expressions and 115 demand-transfer attachments containing 117 rules**. It also contains **26 tool-input contract attachments**, for **123 distinct IR with any contract attachment**. Every raw compute has an attachment or inline expression, and every raw call/deliver has an attachment. The JSON receipt reports input-index enumeration checks. These counts do not establish valid or complete semantic contracts: the official obligation inventory is gated behind the current validation errors and has not completed.

The explicitly unmodeled claims concern a fresh helper-call expansion at `ir_179`, and absent JavaScript undefined values on optional inspection-result branches at `ir_419`/`ir_423`. They contain specific output/input representational reasons, rather than generic opacity; review must still distinguish genuine supported limits from repairable representation errors.

## Carry instructions

The actual added carry IRs are **`ir_103` and `ir_126`**. Both bind output 0 directly to input 0, with no compute or observation operation, satisfying the identity-binding concern from the selected-graph audit at the submitted syntax level. `ir_100`/`ir_123` are the header merges; `ir_114` is slice, `ir_122` dispatch, and `ir_136` an input-range acquisition. No outcome is inferred from stale pre-correction instruction numbers.

The structural correction is still allowed to supersede this response. This audit used only saved JSON and implementation/source text, without calling validation/analysis functions, a model, Skill, renderer, backend or replay. It changed no production or active-run file. Exact diagnostics, local evidence, hashes and counts are in `initial-processing-audit.json`.
