# Paused arrangement and environment audit

This is a read-only source and saved-evidence audit for the user-paused GA4 v9 run. No target, replay, test suite, model call, Skill, or process-control operation was executed by this auditor. Only this note was written. The continuation state was read first. Statements below separate saved point-in-time observations from deductions from source. They do not grade source semantics or establish final coverage, convergence, or remaining duration.

The principal conclusion is that **partial-order permutation enumeration does not explain this paused execution**. The selected revised annotation contains 345 modeled IR semantics, all `order: fixed`, and zero `partial` semantics. Saved locals identify the current instruction as `ir_238`, `capture_reindex_try_completion`, in `block_119`, with `uncertain=False`. The recursion seen in the original stack is the ordinary fixed-order operation walk. The stronger evidence instead shows 1,486 incoming relation environments being processed separately, while a repeated literal registration triggers reconstruction and validation of a 959-entry registry view.

## Saved observations

Evidence files are `paused-stack.json`, `paused-backend-locals.json`, and `paused-container-counts.json` in this directory. The root agent obtained the latter two; this auditor read their saved contents and did not inspect or attach to the paused process.

- The stack enters `solver.py:504` -> `interpreter.py:794` -> `_arrangements`/six active `visit` frames -> `execute:412` -> `_build_candidates:344` -> literal registration -> `LoopFactRegistry._commit:147` -> `_validate_records:766` -> identity serialization. This locates one sampled operation, not its proportion of total runtime.
- Saved locals identify `ir_238`, `block_119`, event 5, operation 0, `BuildOp`, and literal `True` at member path `normal`. `_register.old` is an existing `_Entry`, so this sampled literal identity already exists. The record contents were not fully extracted here; exact equality of the old and proposed entries is inferred from the deterministic literal site and source, not directly measured.
- The active `propagate.environments` list has length **1,486**; `split=True`; the current predecessor is `block_118`. Static CFG inspection confirms that `block_118` is the only predecessor of `block_119`, so the 1,486 entries arise from alternatives on that one incoming edge, not 1,486 different CFG predecessors.
- `_validate_records.records` has **959** entries and `_commit.updates` has **1**. This is the validation view including loop-family entries, not a measured count of ordinary immutable records alone.
- Other saved lengths are: `evaluated=169`, `block_records=169`, `block_out=126`, `edge_out=196`, `queued=1`, `instructions=347`, and `unmodeled=2`. These are container sizes at pause. They do not count completed propagation passes, processed IR, pending total work, or final semantic coverage.
- `evaluate.outcomes=[]` is expected while `_arrangements` is still executing. It does not mean previous environments have failed: `propagate.candidates` already contains records for both instructions in the block, and `failed={}` in the saved locals.

## Selected material and exact static structure

The JSON contents of `graph/selected.json` and `graph/revision.json` are equal. The inspected annotation is `revision/annotation/audit/compiled-response.json`.

- `graph/revision.json:7534` starts `block_119`; `ir_238` starts at line 7539 and `ir_239` at 7582. Their annotations start at `compiled-response.json:38765` and 40028.
- `ir_238` contains 17 events with one primitive each. Four labeled return cases are walked in one fixed operation order: normal (6 primitives), before-request error (2), request failure (4), and after-response error (5). The sampled sixth primitive constructs `{normal: true, accumulator: <normal-case accumulator>}`. The output binding retains alternatives from all four cases. This is a finite case summary; this observation does not assert that its source semantics are correct.
- `ir_239` has two fixed primitives: select the `normal` part, then branch to `block_120` or `block_121`.
- A bounded pure graph reachability calculation gives the SCC containing `block_119` as `block_115` through `block_125`, inclusive: 11 blocks and 24 IR instructions. No propagation code was imported or called for this calculation.
- The header merge `ir_230` is at graph line 7314 and annotation line 38225. It takes the initial accumulator from predecessor `block_114` or the carried accumulator from `block_125`. The body obtains a member in `block_116`; branch alternatives select batch, reindex, or status paths. The merge `ir_252` at graph line 7911 / annotation line 42848 receives accumulator alternatives from `block_117`, `block_120`, `block_121`, `block_123`, and `block_124`. The edge at graph lines 11292-11294 returns from `block_125` to `block_115`.

The source supports an origin mechanism for multiple environments: guard alternatives produce distinct filtered states, merge/member bindings retain correlation, and the loop carries those states back. The static graph and saved lengths do **not** reveal which precise historical guard combination created each of the 1,486 states, whether every difference is relevant downstream, or how many earlier rounds occurred.

## Why the fixed walk repeats so much work

`solver.py:403-407` assigns loop scopes to every instruction in an SCC. Lines 467-470 form the joined predecessor states and the separate per-edge relation environments. Lines 473-477 preserve every environment for a block if any instruction is in a loop scope or has a merge. Consequently all 11 blocks in this SCC use separate environments, including `block_119`, whose own operations contain no merge.

Lines 487-504 evaluate every IR in the block for each environment. Lines 505-506 retain each result and carry its state forward; records are joined only after this work at lines 523-524. At lines 67-118, `_guarded_outgoing` can create a route for each compatible branch alternative. It filters result identities by member/predecessor bindings and deduplicates only exact full-state keys at lines 113-115. Per-edge state lists are deduplicated by every location and every Data ID at lines 540-545. Thus distinct irrelevant retained state can prevent collapse, but dropping it without a proven liveness/equivalence argument could alter required correlations.

If `registry.revision` changes during a block evaluation, `solver.py:554-555` adds **all previously evaluated blocks** to the next-work set. `LoopFactRegistry.revision` includes `fact_revision` (`loop_domain.py:48-50`), and every genuinely new family variant increments it (lines 169-176). The saved `before_revision=495` and `evaluated` length 169 establish the state of these variables, not how often the global invalidation branch has been taken. Source nevertheless shows that a new loop relation can trigger broad repeated work.

For this fixed `ir_238`, absent unresolved references, one environment executes 17 primitives and enters `visit` 18 times. For all 1,486 incoming environments to complete in this pass, that implies 25,262 `ir_238` primitive executions and 26,748 `visit` calls; the following two-primitive `ir_239` adds 2,972 primitive executions and 4,458 visits. These are conditional arithmetic from the code and input-list length, **not measured execution counters**. Candidate products inside individual operations and registry validation are additional costs.

The literal path (`interpreter.py:168-178`) calls `create_result` whenever it resolves a literal. `_register` (`data/registry.py:257-273`) strictly validates the proposed entry and checks existing identity/origin, merges it, and calls `_commit` even when the merged entry is unchanged. `LoopFactRegistry._commit` at `loop_domain.py:144-151` rebuilds the complete view through `_all_entries` (lines 138-139), then validates the complete view. `_validate_records` recomputes every ID at `data/registry.py:763-776`, then invokes further data/reference validation at line 777. Hence an existing `True` literal can repeatedly pay whole-registry work across environment evaluations and subsequent block revisits. The sampled 959-entry validation with one proposed update is direct evidence of that disproportionate validation scope; wall-time attribution remains unmeasured.

The default `max_variants=100000` is visible in the saved solver locals and at `solver.py:376`. It bounds individual relation lists/products/facts, not aggregate work. `_attempts` resets for each `evaluate` (`interpreter.py:782`) and caps recursive calls inside that one IR evaluation (lines 687-690). A fixed 17-primitive walk is far below that cap, and 1,486 incoming states are also far below the per-edge cap. These limits do not prevent expensive repeated whole-registry validation.

## What `partial` means, independently of this run

This section is algorithmic background, not a diagnosis of the selected annotation.

`evaluate` sets `uncertain` exactly when `typed_spec.order == "partial"` (`interpreter.py:791`). Scheduling atoms are primitive operations, except a `for_each` is one outer atom; empty events get a placeholder (`671-677`). Dependencies combine explicit precedence, same-event operation order, required local producers, request/receive pairing, and collection-scope constraints (`contracts/specs.py:998-1042`, 1087-1107). Processing-event boundaries alone do not serialize all their primitives. Fixed order adds the full sequential chain at lines 1040-1042.

For partial order, `visit` tries every currently enabled atom and recursively explores each prefix (`interpreter.py:694-733`). It has no equivalent-frontier memoization. All complete arrangements are materialized before downstream merging (`691-693`, `740-741`, `794-801`). For n fully independent, successful atoms this is n! leaves and sum(k=0..n) n!/(n-k)! visit calls: n=5 gives 120 leaves/326 visits; n=7 gives 5,040/13,700; n=8 would give 40,320/109,601 and would exceed the default visit budget. Dependencies and failures can sharply reduce these counts. Nested member scopes share `_attempts` within the current evaluation. `partial` also makes ordinary writes weak (`interpreter.py:513-517`), so changing the order flag is not a harmless performance switch.

A future partial-order optimization would need a proved commutativity/equivalence criterion retaining local values, branch/case states, operation alternatives, receiver/payload pairing, diagnostics, and registry effects. Blindly choosing one schedule or merging frontiers by only the done-set is unsound. That work is not needed to explain the present all-fixed annotation and is not the first repair suggested by this evidence.

## Smallest source-supported repair candidate

The first candidate is an **unchanged-entry short circuit**, after strict incoming validation, identity/origin conflict checks, and content/annotation merging have succeeded. If the proposed resulting entry is equal to the existing immutable entry, return the existing detached Data without rebuilding and validating the complete registry. This is reuse of already verified material, not a new persistent cache or a change to Data identity. It directly addresses the sampled repeated literal. A careful implementation must preserve the existing failure behavior for forged models, identity collisions, changed origins, conflicting/refining content, annotations, and changed references; genuinely new or modified entries still need the required validation, and mutable loop facts need their own sound validation/publication boundary.

This is a recommendation only, not an implemented or accepted fix, and no speedup or eventual convergence is promised. It should be verified offline against identical re-registration and conflict/refinement cases before any approved run resumes. If disproportionate work remains after that repair, the next inquiry is a bounded measurement of total block evaluations, environments per block, genuinely new relation facts, and validation calls. Whole-environment collapse or dependency-based requeue changes need separate correlation-preserving reasoning; they should not be casually bundled into the smallest repair.

## Source identity

Each live source file below was SHA-256 compared with the corresponding file under this run's `implementation-snapshot/`; every pair matched exactly. The implementation aggregate recorded by the continuation state is `e5c8d5ffce9f94b02f103b284a2b366c32d9bd386727bfad8b78d6df79842154`.

| Source file | Equal live/frozen SHA-256 |
|---|---|
| `src/skillflow/propagation/interpreter.py` | `0764fdbdedcdab75b0e193ed63d7104a2bd59e5f327b85f6ec0f314f128f90f6` |
| `src/skillflow/propagation/solver.py` | `ee8ea4c7ea0eb429ff45b67da90f8303df69bcdd82eb19eda88c7869fe8364ea` |
| `src/skillflow/propagation/contracts/specs.py` | `a0d32eb5123b2737a689fe8b38fab7c22168d94c3cb402f0d563c34991f500ef` |
| `src/skillflow/propagation/data/registry.py` | `602bde3cae58e3e65ab8d8a9fd17c26dcff2868e24e0c4344bb7513d43e80f4f` |
| `src/skillflow/propagation/loop_domain.py` | `f732bdbc243118e8f926ee8e61edaff99d869782064aed004713ae5306fe654f` |
