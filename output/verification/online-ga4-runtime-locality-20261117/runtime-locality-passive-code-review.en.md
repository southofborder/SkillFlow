# Passive runtime locality review — proposal only

Run: `document-guided-ga4-runtime-locality-high-20261117-205158`. Frozen producer: `3ebfb40a0053f0e3dc84aa4c7877b116445749b478b912910b8a9d192d787af6`.

This is a bounded read-only code and saved-evidence review while source review is running. No project imports, tests, validators, compiler, propagation, DOE, replay, model request, or Skill execution was performed. No frozen file was changed. The findings below are not claims about terminal results of this live run.

## 1. Required action with no successful operation record: upstream deletion hypothesis

**Classification: actionable code-review hypothesis, not an executed reproduction or an observed GA4 false deletion.** The exact combination needs a new offline regression after authorization; it must not be repaired during this frozen run.

Conditions: (a) a Task requirement is fully expressed as a required action; (b) its IR has no successful committed record because a typed operation-domain failure occurs in it, or its action is blocked by an earlier failure; (c) a successfully processed upstream producer supplies a value used by that declared action; (d) there is no separate demand on that upstream value, global requirement/review gap, or applicable preservation constraint. The action must not be proved infeasible.

The static path is:

1. `src/skillflow/doe/material.py:136`–156 indexes operations only from committed `records`. A rolled-back IR's completed prefix is preserved as diagnostic `observed_operations`, not promoted to a committed operation. This preservation is appropriate; it is relevant because the missing action has no operation key.
2. `src/skillflow/doe/demand_engine.py:552`–556 finds only those recorded operation keys. `seed()` at 626–628 still creates a required IR action and marks the requirement bound when no matching operation exists. `step()` at 840–854 has no input transfer for this `op_key=None` action.
3. `src/skillflow/propagation/solver.py:782`–786 correctly preserves the failure on the failed IR and its actual forward-dependent instructions. It does not mark already processed upstream producers failed. `diagnostic_applies()` at `src/skillflow/propagation/contracts/limitations.py:110`–117 applies that explicit scope exactly.
4. `src/skillflow/doe/input_assessments.py:344`–378 checks the assessed IR's coverage and applicable diagnostics. For the upstream processed use, the missing action's downstream-local fault may not apply. With no constraints, `preservation()` at 302–304 returns true. Line 400 then emits a final `deletable` range, rather than just proposing a candidate.
5. `src/skillflow/doe/input_locations.py:106`–137 translates that range to a modification recipe; it does not recheck an unrecorded consumer. An acquisition result can receive `omit_result_range_at_use` at 123–126; an ordinary whole input use can receive `remove_input` at 131–135. A generated context-only location can prevent a concrete edit at 111–113, but does not remove the `deletable` classification.

Thus the currently read code has no universal final guard for this particular missing-action path. Whether the condition is reachable under the complete public setup is not established by this read-only review. No terminal DOE comparison is asserted to be wrong. Constraints or other demands can block this path; the hypothesis deliberately excludes them. A successful alternative path with actual operation records is a different case: the affected IR still has a scoped failure diagnostic, and ordinary recorded transfers also exist.

**Proposed minimum offline test:** an accepted source-backed fixture has a processed read/build producing `x`; a required `deliver(x)` belongs to an IR whose earlier collection operation rejects a known object; an independent branch produces unrelated `y`. Preserve the original failure and detached prefix observations. The failed action and the actual upstream use of `x` must remain unresolved/nondeletable, while unrelated `y` retains its independent decision. Cover no-prefix and successful-prefix variants, blocked required action, and FIFO/LIFO. Do not count detached prefix evidence as successful execution. If the test confirms the hypothesis, introduce a conservative backward uncertainty relation only for the source-declared operands needed by the missing required action; do not globally taint every predecessor or fabricate accepted records.

For the current run, audit every terminal deletion against failed/blocked required actions before describing it as supported. No live change or rerun is proposed.

## 2. Whole-output contracts do not establish arbitrary field necessity

This boundary is implemented conservatively. `src/skillflow/doe/input_contracts.py:91`–110 selects an exact output/property rule, or a reviewed exhaustive decomposition for a whole value. A whole-value rule is not reused for a nonempty child selector. At 133–138 an uncovered selector produces `input_contract_output_gap`; `src/skillflow/doe/demand_engine.py:282`–294 conservatively retains the affected inputs. `tests/doe/test_reviewed_input_necessity.py:121`–127 explicitly specifies no deletion in this case.

The saved current processing snapshot contains **89 compute contracts, all with a single whole-value output rule and no child output rule**. Saved mapping contains nonempty selectors (11 IR demand rows and 25 operation demand rows). These are separate inventories: this does not prove that all, or any specific number, of those selectors reaches a particular compute at runtime. Source review has not yet accepted these contracts at this snapshot.

**Remaining precision limitation:** if such a child demand reaches one of those whole-only computations, the implementation will retain a concrete selector gap instead of making the requested field-level distinction. The appropriate proposal is source-backed per-output rules or deterministic `build`/`select_part`/`update_fields` where the source actually defines those constructors, with review checking the Task-selected child selectors. Processing must remain Task-isolated; whole-output acceptance must not become blanket child-output acceptance.

Snapshot evidence: `processing-a002-retention-audit.json` and `source-review-input-v12-audit.json` in this directory. Their counts concern authored/retained material, not accepted review or final demand coverage.

## 3. Address separation and execution locality: bounded positive findings and limits

`src/skillflow/propagation/contracts/locations.py:47`–66 uses explicit address policy; unknown content in an identified source does not imply aliasing. Truly unidentified addresses still may alias every declared location of the same kind. `src/skillflow/propagation/interpreter.py:102`–113 includes implicit caller context slots, and 153–167 uses the same policy for reads. No name-based universal alias or weakening of unknown-address writes was found in this bounded review.

For mixed successful/failed paths, `src/skillflow/propagation/solver.py:780`–786 can retain successful records as `processed`, but it also retains the exact failure diagnostic and affected IR scope. `input_assessments.py:344`–378 consults that diagnostic before deletion; `deletable_reduction()` at 478–489 also requires processed coverage and an explicit deletion assessment. No direct false-deletion bypass was found for the failed/affected IR itself.

Isolation currently has an **IR transaction boundary**: `failure_scope.py:60`–99 collects declared IR outputs/state writes; solver 697–706 marks that write set unavailable after a local operation error. Independent outputs or prefix writes inside the same failing IR may therefore remain unavailable, while prefix observations survive in the failure evidence. This is a conservative precision limit, not evidence that unrelated addresses alias. Any finer operation-level continuation would need explicit transaction/effect semantics and separate offline evidence.

Existing offline evidence was read, not rerun: `output/verification/runtime-locality-20261117/locality-focused.xml` records 172 tests, zero failures/errors/skips. Its tests include independent continuation, prefix rollback/evidence, strong overwrite, verified branch reconvergence, explicit unknown address versus unknown payload, and unknown internal-identity errors remaining fatal. Root's final acceptance records the larger scoped union separately. Earlier failing receipts remain historical evidence and are not represented as passing.

The finite runtime inventory covers the supported vocabulary and its machine contracts. It cannot prove arbitrary source behavior is faithfully represented, nor replace source review. This audit found no new address-policy defect; item 1 and the measured field-contract precision limitation are the actionable follow-up items.
