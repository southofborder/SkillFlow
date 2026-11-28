# Initial CFG candidate audit (provisional)

The replacement run's first graph response contains **245 blocks, 232 edges and 561 instruction occurrences**. Saved structural validation rejected it. This is a generated-candidate audit, not accepted CFG or propagation coverage.

## Two primary errors

| Saved IR | Exact candidate input | Generated self-reference | Source filter |
| --- | --- | --- | --- |
| `ir_100` | `/blocks/47/instructions/0/inputs/2` | `list_filtered` is both this merge's input and its new output. | `scripts/src/core/storage.ts:132` |
| `ir_122` | `/blocks/58/instructions/0/inputs/2` | `latest_filtered` is both this merge's input and its new output. | `scripts/src/core/storage.ts:163` |

Both merges try to retain an unchanged accumulator when a filter predicate rejects a member. The initial path uses `[]`; the keep path uses the append result; the reject path incorrectly names the merge's own output. The predecessor table does not exempt this same-block read from the immutable result rule. Source `Array.filter` uses ordinary callbacks and contains no corresponding read-before-definition defect. These are generated representation errors.

The saved diagnostics are actionable: they name the block, canonical instruction, result and input index. The table adds exact draft paths. Any correction must preserve member filtering and unchanged state on rejection using supported predecessor versions. This audit does not modify or manually repair the graph.

## Secondary endpoint diagnostics

All raw candidate edge endpoints exist. The compiler separately constructs and validates BasicBlocks; the two invalid filter headers are omitted from the canonical block map, while their edges remain for subsequent graph validation. That produces ten missing-endpoint messages referring to the same two headers. They are consequences of the two primary self-references, not evidence of ten independent absent source blocks.

## Finite candidate coverage

Source-span and opcode inspection found candidate representations for **13/13 API sites, 25/25 saveResult sites and 3/3 explicit URL loops** from the previously frozen source-only inventory. API sites have acquisition/publish opcodes, save sites have `save_result`, and URL-loop sites have header/member relationships. Exact per-site candidate ordinals and references are in the JSON receipt.

These are provisional representation counts. The graph failed validation; no accepted CFG, processing, propagation, demand or DOE coverage follows. Broad source correspondence also cannot establish request/response identity, condition precision, field necessity, review correctness or preservation. The sole structural correction is a later candidate and requires separate verification.

The response identity is `83929cd7a865ec20b67b983debc49074abd891404b387fc123ad31132c41b806`. Exact raw-file and source hashes, instructions, saved diagnostics and source quotes are preserved in `initial-graph-audit.json`. No production, active run or historical artifact was changed, and no model, Skill, compiler, propagation or replay was executed.
