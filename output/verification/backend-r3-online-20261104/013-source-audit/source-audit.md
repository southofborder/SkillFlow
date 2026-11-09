# 013 source-fetch-with-fallback: independent source audit

The closed run produces useful request/response and credential-recipient lineage, but **does not complete propagation or produce a resolved, actionable DOE verdict**. Of 27 generated IR, 19 are processed (70.37%), four status appends are explicitly unmodeled, and their four returns are blocked. `unresolved_binding` is zero. All 13 sensitive comparisons are explicitly unresolved `no_excess_established`; all 10 constraint checks are `not_established`.

This is an assistant source/artifact audit, not human gold. No model, Skill, production import, validator, test, solver or replay was executed. Exact IDs, source pointers and hashes are in [source-audit.json](source-audit.json).

## Where the run stops

| Path | Status append | Required public post-state | Blocked return |
|---|---|---|---|
| First fast success | ir_014 | result_008 | ir_015 |
| Retry fast success | ir_018 | result_011 | ir_019 |
| Archive success | ir_022 | result_014 | ir_023 |
| Archive failure | ir_026 | result_017 | ir_027 |

Frozen SKILL.md line 16 requires appending final status before each return. The CFG additionally gives every append a public value representing the whole resulting file. **All four generated file-state results have zero CFG consumers.** Processing correctly refuses to alias the appended status as the whole file or invent a file read, but marks the entire append unmodeled because the write primitive has no local output with which to bind that public result.

That narrow limitation is real under this exact frozen CFG. It does not mean the backend cannot append. Frozen `contracts/specs.py:131-136` has write/append, `specs.py:766-769` requires each CFG result binding, and `interpreter.py:169-191,600-623` seeds append state and records before/after changes while preserving prior contents. The primary defect is **CFG/processing alignment**: unnecessary public post-state results impose a value-production obligation beyond the source's side effect. Conceptually, omit those unused public results and describe the existing append operation with its actual status input and file location. No replacement was compiled or evaluated, so this is not a claim that a modified whole candidate is verified.

The source does leave status format and append-failure handling unspecified. These remain legitimate local limitations, but do not remove the known normal append effect. No read, fake compute, replacement write, or status-as-whole-file binding is justified.

The original processing answer supplied both modeled and unmodeled coverage for these four instructions; its sole correction removed the modeled entries. The final source review returned no findings and did not challenge the avoidable CFG interface mismatch, despite its prompt explicitly requiring review of representable unmodeled behaviors (`source_review.py:412-416`). No semantic repair was used.

## Actual source boundary and value coverage

| Source-implied category | Recorded / required | Evidence |
|---|---:|---|
| Request and environment acquisition | 2/2 | ir_001, ir_003 |
| First fast, retry fast, archive requests | 3/3 | ir_005, ir_008, ir_010 |
| Corresponding responses | 3/3 | Each call's e1/a0 receive |
| Successful bodies / archive error projection | 4/4 | ir_012, ir_016, ir_020, ir_024 |
| Final-status append paths | 0/4 | Four explicit cutoffs above |
| Terminal returns | 0/4 | Four blocked successors above |

These are separate static site/path denominators, not measured execution counts. Ordinary return is not automatically a user-output sink. Saved DOE has 21 sink positions: 18 contract-default model observations and three tool deliveries; **no storage write is recorded**.

The first and retry fast.fetch requests each carry the same actual source_id and FAST_KEY versions; their receive operations create different response IDs. Archive receives only the original source_id, without the key or either fast error as an extra argument. First-fast body, retry-fast body, archive body and archive error each select from their own acquired outcome. Final status derivations likewise retain their own outcome input. These relations are useful and source-supported, but the actual four returns are not reached in saved propagation.

Credential presence is an explicit normalized `present` expression at ir_004. The transient-error classifier remains opaque because source line 10 supplies no classifier. CFG routing preserves absent-key fallback, the one retry route and terminal success branches, but global call-count and stop-after-success constraints are not established by this incomplete run. Possible credential influence on a response/status is not credential plaintext containment.

## Demand, review and DOE limits

The separate R3 correspondence defect is a failed normalized-expression reference: its corrected `only_if` condition still points to `segments/0/ops/0/expression/expression`. Both `constraint_reference` and `constraint_expression` diagnostics remain, and that record was isolated. An ir_004 presence expression exists; this is a reference/alignment failure rather than an inability to express presence.

Sensitivity resolved its one declared FAST_KEY scope. The annotation includes an archive-specific prohibition; its actual recorded request excludes the credential. However, its constraint check remains `not_established`, and the source's diagnostic-output prohibition remains a gap because no diagnostic receiver/action is supplied. Default model observations are not silently equated with diagnostic output.

All 13 data reviews say that relevant limitations leave the comparison unresolved, neither safe nor evidence of removable content. There are zero supported positive DOE claims, zero contradicted positive DOE claims, and zero actionable reductions. The absence of a token comparison at archive is not proof of global compliance; absent append/return records are not empty or safe boundaries. Source accuracy, precision and recall are not established.

The backend returned and published partial artifacts. There is no observed propagation convergence, unresolved-binding or publication exception. The remaining layers are the four CFG/processing cutoffs, one correspondence reference isolation, unresolved source/task requirements and a source review that missed the alignment opportunity. Seven original source criteria are retained as explanatory supported/unresolved observations in the JSON, without converting them into an accuracy percentage.
