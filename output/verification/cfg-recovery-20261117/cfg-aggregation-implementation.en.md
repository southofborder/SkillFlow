# CFG diagnostic aggregation and mixed causal ownership

This change addresses the general failure where a precise application error consumed the one structural correction before independent compiler errors became visible. Earlier gate order stopped at wire preflight. A full rewrite could incidentally repair an unreported defect; that was not a guarantee supplied by the previous validator. The fix makes safely available defects explicit before choosing the existing correction scope. It does not increase requests or budgets, weaken validation, or promise that a model will repair every defect in one answer.

## API and acceptance boundaries

`cfg_wire.prepare_cfg_wire(value)` returns `(canonical_candidate, preflight_diagnostics)` only after both existing wire and canonical field schemas succeed. Bookkeeping remains the existing generated instruction references, block-name defaults and context inventory. It does not infer operands, connections, producers or source roles. The returned object is diagnostic input, not an accepted CFG. `normalize_cfg_wire(value)` retains its strict rejecting API.

`online.validate_step` now passes that schema-valid candidate through the unchanged source-copy and whole-compiler path even when independent application rules failed. It prefixes every preflight diagnostic to any compiler diagnostics, preserves the compiler's original rejecting messages, rebases rejected-owner indices by the exact prefix length, and binds all rows to the exact raw wire object. A successful compiler cannot override a preflight error. Schema and source-copy failures explicitly identify their barrier; compiler inspection is not attempted across those barriers. Unknown implementation exceptions still propagate instead of becoming model-correctable findings.

The document step identity is v13. The correction scope identity is v2. Root owns the guided/fragment and policy identity updates.

## Proof for mixed global errors

Compiling a candidate whose dispatch is still missing inputs produces `DISPATCH_INPUTS_MISSING` inside the same root constructor error as missing endpoints from rejected loop heads. That root cannot use endpoint-only ownership.

`structure_issues` now includes the actual block and instruction IDs on a missing-dispatch-input issue. The compiler retains the exact original root error and adds a v2 ownership certificate only if every constituent issue is either an endpoint of a block actually rejected during this compilation or an exactly located surviving guarded dispatch with missing inputs. The constructor's actual error must equal the independently inspected issue list. Any unrelated root issue, malformed constructor field, missing entry or unexplained endpoint prevents complete ownership. Existing pure endpoint certificates remain v1 without a semantic change.

The scope selector verifies raw-candidate identity, every rejected owner and original diagnostic, all endpoint occurrences, each dispatch's exact terminator and outgoing edges, and the unique current preflight dispatch diagnostic. It independently inventories all surviving guarded dispatches, so omitting a dispatch and reducing the stated issue count cannot manufacture complete proof. Unsupported or incomplete global evidence, ambiguous identities and necessary topology edits use whole-response fallback. A known schema/source-copy barrier prevents global or causal dependency inference; it does not by itself prohibit an exact direct replacement of an existing record with unambiguous identity. Unknown barriers use whole-response fallback.

Eligible local repairs still use actual control SCCs, producers and predecessors. Existing block identities, entry and edges remain immutable in that mode. Boundary consumers/edges remain explicit readonly context. Every merged candidate undergoes the full unchanged validation path; scope is permission to edit, never acceptance.

## Offline evidence

Latest core receipt: `cfg-aggregation-core-final-02.xml`, **348 passed**, covering the new 25 aggregation tests, existing scope/strategy/peer tests, graph extraction and IR tests, and alignment/interface tests. This is scoped evidence, not a whole-repository all-green run.

The new synthetic ResponseChain regression contains simultaneous missing dispatch inputs, two self-reading loop heads and ten endpoint cascades. First-pass online validation reports all four diagnostic rows, including the root's eleven constituent issues. The existing one-correction chain receives the complete source and candidate, selects actual loop bodies and producers, accepts five corrected records, preserves every outside record and edge, and retains the rejected raw first answer. Other tests cover two preflight errors and index rebasing, pure dispatch ownership, tampered/missing proofs, all-original-error preservation at schema barriers, source-copy barriers, compiler-success/preflight-rejection, unchanged global fallback, and head-only repairs still failing for unproduced carries.

Initial `cfg-diagnostic-aggregation-01.xml` retained one test failure: an assertion expected exactly two missing-result diagnostics, while strict whole validation also reported two downstream consequences. The assertion now requires both precise missing-carry locations; no validator was relaxed. `cfg-aggregation-compatibility-01.xml` retained 110 passes and three DOE integration failures caused by the concurrently bumped source-review protocol requiring downstream identity synchronization; root was notified and owns their resolution. The new CFG tests passed in that receipt.

Only new synthetic offline artifacts were executed. No historical run/candidate was executed or replayed, no Skill or real model was called, and no protected historical artifact was modified.

## Independent review update

The read-only transport peer identified a detached-root-text editing-permission gap: the typed ownership context did not bind the exact root message. With root approval, every newly produced endpoint-only v1 and mixed v2 certificate now hashes the original root code, JSON-pointer path and complete message. The selector checks that binding; old unbound or altered proof uses whole-response fallback. Whole-graph acceptance is unchanged. The final peer receipt `cfg-aggregation-peer-final.xml` passes **352/352**, including 29 new aggregation tests and four added root-binding regressions. Earlier receipts remain preserved.

## Final-scope regression and correction

The first broad final-scope run found a real regression in both unchanged variants of `test_cfg_bad_input_record_replacement_keeps_other_blocks_and_revalidates_refs`. The newly added unconditional barrier fallback required a whole response for a single invalid operand type at an existing input record. That lost the previous safe local correction capability: inability to compile malformed input was incorrectly treated as proof that its whole existing block could not be replaced. The old test was not obsolete.

With root approval, known schema/source-copy barriers remain explicit while permitting direct existing-record editing only where every known diagnostic has a precise owner and the raw identity index is safe. No dependency closure is inferred across a barrier. A barrier combined with global/cascade or read-before-definition dependency mode, and every unknown/malformed barrier, still selects whole-response fallback. Compiler execution remains blocked until safe preparation succeeds. Full post-merge validation still rejects a corrected input referring to an undefined result.

`cfg-local-barrier-regression.xml` passes **345/345**: the original typed-record tests unchanged, the aggregation/scope/strategy/peer tests and all graph extraction/IR tests. Nine new cases cover blocked dependency proofs, unknown/malformed barriers and exact local source-copy ownership; the three existing barrier tests retain their no-compiler assertions and now verify direct records without inferred hidden-loop edits. Root preserves the initial broad-scope failures and owns subsequent affected-scope acceptance.
