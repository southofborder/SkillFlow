# Paused GA4 v9 propagation diagnosis

The user requested a pause and investigation on 2026-11-03. The sole queue supervisor (PID 11184) and GA4 controller (PID 30428) were suspended, in that order, at 01:23:09 UTC / 09:23:09 China time. Both remain suspended, with unchanged CPU counters across subsequent checks. They were not terminated. The heartbeat automation was also set to PAUSED. There is no automatic resume authorization.

The selected GA4 analysis has not completed propagation and has not published a DOE result. The three small Skills have not launched. This document is a forensic diagnostic, not a terminal validation report or a replacement for the outstanding four-case results.

## Direct evidence

The coarse propagation stage began at 2026-11-02 15:25:26 UTC / 23:25:26 China time. At suspension it had occupied approximately 9 hours 57 minutes 44 seconds. Controller CPU was 35,695.828125 seconds cumulatively since process creation, and private memory was 2,518,409,216 bytes. CPU includes earlier controller work and must not be assigned entirely to this stage.

The paused Python stack contains `_calculate -> propagate -> evaluate -> _arrangements -> execute -> _build_candidates -> literal -> create_result -> _register -> LoopFactRegistry._commit -> _validate_records -> _id -> model_dump`. Thus the process was still inside propagation computation, not its final save/validation phase. This differs from the previously sampled v8 publication bottleneck.

Saved backend frame locals identify `block_119`, `ir_238`, opcode `capture_reindex_try_completion`. This represents the try/catch inside `reindexUrls`: acquire a per-URL indexing response, append a success or failure record, and preserve the accumulator. The frozen source is `source/inputs/package/scripts/src/index.ts:301-318` in the run directory. The currently executing operation constructs the `normal: true` completion field at event 5, operation 0.

| Observation | Paused value | Interpretation |
|---|---:|---|
| Selected generated IR | 347 | Graph size, not completion coverage |
| Selected modeled IR | 345, all fixed order | No selected IR requests partial-order schedule enumeration |
| Active block incoming environments | 1,486 | Alternative analysis states, not actual URLs or measured source iterations |
| Registry entries in active full validation | 959 | All are revisited for the sampled ordinary commit |
| Entries proposed by that commit | 1 | Existing, unchanged literal descriptor |
| Already evaluated blocks in solver set | 169 | Point-in-time bookkeeping, not final source coverage |
| Queued blocks at suspension | 1 | Does not imply imminent completion; revisions can requeue work |

Container sizes were read from the suspended process using read-only `ReadProcessMemory`, with built-in object types checked and CPython 3.12 64-bit container layouts confirmed against the installed headers. No code was injected into the process. Stack inspection used the already available py-spy binary in nonblocking mode. No model request, Skill execution, replay, or production change was performed.

## Confirmed unnecessary work and amplification

1. **Unchanged registration still performs a complete registry validation.** The current literal is `True`, its old record exists, and identity, origin, and canonical content checks have already succeeded. Empty incoming annotations preserve the old descriptor. Nevertheless, `_register` invokes `_commit`. `LoopFactRegistry._commit` rebuilds all loop-family entries and calls `_validate_records` over the whole 959-entry view. That includes rehashing identities, reference checks and graph checks. The later change check only controls the revision counter; it does not avoid the scan. See `registry-audit.md` for the exact proof and line references.
2. **The block is evaluated separately for many incoming alternatives.** The selected loop SCC contains blocks 115 through 125. Solver code preserves separate environments for SCC/member/merge handling. At this pause, block 119 has 1,486 environments from predecessor block 118. This can repeat stable literal registration and operation construction many times. The alternatives cannot safely be equated with source loop iterations or collapsed indiscriminately, because member/receiver/predecessor correspondence matters.
3. **A registry revision triggers a broad revisit.** `solver.py:554-555` adds all previously evaluated blocks to the next work set when the registry revision changes. New loop-family variants advance that revision. Consequently a local fact change can cause much wider repeated computation. This is a confirmed source rule; the pause does not measure its cumulative firing count or time share.

The evidence supports a multiplication of repeated environment evaluation, broad revisits, and full-registry checks. It does not quantify each component's share of the nearly ten hours. It also does not prove an infinite loop or eventual convergence.

The recursion in `_arrangements` must not be presented as factorial schedule explosion in this case. Both active `uncertain` values are false, the active IR has 17 fixed-order events, and all 345 selected modeled IR use fixed order. The recursive function also implements ordinary sequential execution. A preliminary stack-only hypothesis was corrected after inspecting these locals and the selected annotation.

The relevant registry/interpreter/loop-domain code is byte-identical between current source and the frozen v8/v9 snapshots. This is an inherited propagation scaling problem exposed by the current workload, not evidence that v9 introduced a new registry change. Prior material-reuse changes addressed material loading and publication, while these checks occur during computation.

## Smallest next repair to evaluate

First avoid committing an identical ordinary record after strict incoming validation and identity/origin/content/annotation conflict checks have succeeded. Reuse the already validated record. Retain typed equality and necessary validation at deliberate loop/publication boundaries. This directly removes the observed pointless whole-table work without adding a model stage, cache service, or new execution mechanism.

Measure that focused change on a separate offline regression derived from this exact repeated-literal scenario before deciding whether environment handling or revisit scope also needs changes. Do not initially merge all environments, cap results silently, alter the source-supported loop into a black box, or claim that eliminating one hotspot guarantees full completion. No repair has been implemented in this diagnostic turn.

## Preserved evidence and next state

- `suspend-receipt.json` and `pause-verification.json`: process suspension and unchanged CPU counters.
- `paused-stack.json`: the paused main-thread call path.
- `paused-backend-locals.json`: selected propagation frame values, excluding transport/controller frame exports.
- `paused-container-counts.json`: bounded, read-only container-size observations.
- `registry-audit.md`: independent source audit of the no-change commit and validation cost.
- `arrangements-audit.md`: independent source audit of fixed order, incoming alternatives and revisit scheduling.
- `automation-before-pause.json`: prior automation settings; the current automation is paused.

The frozen implementation, prompts, selected artifacts, original answers and historical runs remain unchanged. The current process retains its memory for investigation and will not be resumed without a new user instruction. Final coverage, useful DOE and complete analysis/replay timing remain unavailable.
