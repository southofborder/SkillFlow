# Paused GA4 registry validation audit

Date: 2026-11-03. Scope: read-only diagnosis of the already paused v9 GA4 controller, using the existing captured stack/locals and source files. No controller interaction, resume, target execution, replay, benchmark, production edit, or prompt edit was performed by this audit. The only file written is this note.

The sampled operation is a repeated, unchanged literal registration that nevertheless reconstructs and validates the entire working registry. This is a concrete scaling hotspot. It does not establish how much of the accumulated elapsed time belongs to this path, nor prove that it is the sole cause of the delay. The relevant code is byte-identical to the frozen v8 GA4 implementation, so it is not evidence of a newly introduced v9 registry regression.

## Evidence and identity

The authorization state was read first from `output/verification/cfg-processing-alignment-v9-20261102/continuation-state.json`: phase `paused_by_user_for_diagnosis`; implementation and prompts remain frozen.

Evidence files in this directory:

- `paused-stack.json`: the sampled main-thread path runs from `propagate` through `evaluate`, `_arrangements`, `execute`, `_build_candidates`, `resolve`, `literal`, `create_result`, `_register`, `LoopFactRegistry._commit`, `_validate_records`, `_id`, and Pydantic `model_dump`. It is an in-computation registration/validation path, not the final save path.
- `paused-backend-locals.json`: the literal is `True` at `[["ir_238", 5, 0], "member", 0, "value"]`. The build member is `normal` in `capture_reindex_try_completion`. `_register.old` is an existing `_Entry`; `create_result.annotations` is `None`. The update is for `data_e2e0db24933a4d51f1340bea137fa9e16a31eea6f716e2522db989478c374d48`. The currently rehashed record is the different ID `data_54423cc9acd1a830daf22bbf30a17db53fc24875550ba866c405d17d9c083baa`. Both `evaluate.uncertain` and `execute.uncertain` are `False` in this sample.
- `paused-container-counts.json`, supplied by the root audit: `_validate_records.records` contains 959 entries, while `_commit.updates` contains one entry. The source loop therefore intends to recheck all 959 identities for this one unchanged update. The same receipt reports 1,486 solver environments in the current block evaluation; that is a multiplicative workload dimension, not a measured count of completed registrations or proof that every environment reaches this operation.

All code references below are workspace-relative and refer to the frozen-v9-equivalent source. SHA-256 checks found exact byte equality between the workspace, `experiments/doe/runs/document-guided-ga4-alignment-high-v9-20261102-214514/implementation-snapshot/`, and `experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/` for these files:

| File | SHA-256 in all three locations |
|---|---|
| `src/skillflow/propagation/loop_domain.py` | `f732bdbc243118e8f926ee8e61edaff99d869782064aed004713ae5306fe654f` |
| `src/skillflow/propagation/data/registry.py` | `602bde3cae58e3e65ab8d8a9fd17c26dcff2868e24e0c4344bb7513d43e80f4f` |
| `src/skillflow/propagation/interpreter.py` | `0764fdbdedcdab75b0e193ed63d7104a2bd59e5f327b85f6ec0f314f128f90f6` |

These are per-file identity checks, not a new whole-implementation verification or historical replay.

## Why this sampled update is unchanged

`interpreter.py:168-172` registers a literal with a stable position-based result key and an origin containing that position. `resolve` calls it at lines 177-178; `_build_candidates` resolves an included member value at line 344. `DataRegistry.create_result` at `registry.py:286-294` supplies empty default annotations when the caller passes `None`.

The sampled stack has already reached `_register` line 272, after the following checks and merge at lines 257-271:

1. The incoming entry passes strict model validation at line 259, including forged `model_copy` protection.
2. Because `old` exists, identity collision and exact origin/input-relation checks at lines 263-267 have passed.
3. A literal is neither `OpaqueContent` nor `KnownPartsContent`. Consequently `_content_merge` at lines 184-196 can reach line 272 only by finding canonical content equality at lines 194-195 and returning the old content. A different literal would have raised first.
4. The merged record preserves `old.data.origin` at line 270. Empty incoming annotations preserve the old annotations through `_annotations_merge` at lines 154-161; annotation lists are unique under `data/models.py:277-292`.

Under the registry's existing validity invariants, the resulting descriptor is therefore unchanged. This is stronger than merely observing an existing ID. Nonetheless `_register:272` unconditionally calls `_commit`. `LoopFactRegistry._commit:148-150` checks for descriptor change only after full validation at line 147, and uses that check only to advance the revision counter. It does not avoid validation for a no-change update.

Existing tests at `tests/propagation/data/test_registry.py:55-65` verify stable IDs and record count for repeated registrations; they do not check that repeated registrations avoid a global scan. Semantic idempotence is currently present, computational idempotence is not.

## Work performed by one ordinary commit

`LoopFactRegistry._commit` at `loop_domain.py:144-151` first checks that ordinary updates do not mutate a loop-family identity, then calls `_validate_records({**self._all_entries(), **updates})` at line 147.

- `_all_entries`, lines 138-139, reconstructs an `_Entry` for every loop family and copies the ordinary-record/family mappings. `_entry`, lines 122-136, sorts every family's variant IDs, gathers inputs and dependencies, and constructs fresh `LoopSummaryContent`, `Origin`, `Data`, and `_Entry` objects. This cost exists even when the one ordinary literal update does not change anything. The data models have `revalidate_instances="always"` at `data/models.py:37-40`.
- `_validate_records`, `registry.py:763-777`, iterates every resulting entry. At line 766 it recomputes each identity-derived ID. `_id`, lines 229-231, performs identity `model_dump`, canonical JSON serialization, UTF-8 encoding, and SHA-256. It hashes identity payloads, not every complete data descriptor; the latter would overstate the specific hashing work.
- The second validation phase at lines 780-832 traverses all records and all relevant references, including every loop-summary variant at lines 809-825, builds containment/parent graphs, and runs two whole-graph acyclicity checks.
- Further whole-registry checks at lines 847-890 inspect mapped membership, part origins, and nested composition. The nested known-parts check at lines 885-890 compares every ordered pair of parts, so its local cost can be quadratic in a record's part count. Mapped/base and part-location traversals can add further costs.
- `_records.update(updates)` at `loop_domain.py:151` then replaces the ordinary entry even when its descriptor is equal. The ordinary `DataRegistry._commit` also performs full-registry validation for every update at `registry.py:244-255`, but the loop subclass additionally reconstructs all working family entries.

For `M` repeated ordinary registrations against approximately `N` registry entries, identity validation alone performs approximately `M * N` rehashes, plus reconstruction, reference checks, and graph checks. For `N` successive new ordinary records built from an empty registry, the same structure yields `N * (N + 1) / 2` identity checks before other work. These are source-derived scaling formulas, not timing measurements of this run. The captured 959-versus-one sizes directly demonstrate that validation breadth is disproportionate to the sampled no-change update.

The qualifier “ordinary registration” matters. It is incorrect to say that every candidate necessarily triggers a full registry rehash. `_result` at `interpreter.py:296-314` routes suitable loop/correlated results to `family`; `LoopFactRegistry.family` at `loop_domain.py:153-177` deduplicates variants and does not call `_commit`. It hashes the candidate variant, increments `fact_revision` only for a new variant, and returns that family's current description. Literals bypass this family route and always use `create_result`, including inside loops. Resolved locals and existing references also need not register a record.

`solver.py:487-504` evaluates instructions separately for each incoming environment, explaining how stable literals can be registered repeatedly without any new literal identity. The sample's `uncertain=False` does not support attributing this instance to factorial ordering of partially ordered events.

## Minimal repair options for later authorization

The smallest useful change to evaluate later is a no-change registration/commit exit after strict incoming validation and all identity, origin, content, and annotation conflict checks have succeeded, but before `_all_entries` and `_validate_records`. It should compare canonical typed record content, preserve the detached return value, and avoid descriptor/revision mutation for exact repetition. Use the established typed equality semantics at `registry.py:120-122`; ordinary Python/model equality can collapse `True`, `1`, and `1.0` and is not a suitable substitute. This requires no persistent cache, protocol change, model stage, or weakened immutable identity.

There is one important ownership issue: loop `family` mutations occur separately from ordinary `_commit`. Today an ordinary commit incidentally validates the current complete family set. Skipping a no-change ordinary update must not accidentally become the only change that removes validation of newly added family facts. Make the intended family-validation boundary explicit and retain complete validation at publication: `LoopFactRegistry.seal` at lines 246-248 imports through `DataRegistry.from_dict`, whose lines 949-956 invoke `validate`. `LoopFactRegistry.validate` at lines 237-238 is also an explicit existing full check. Whether invalid intermediate family references must fail immediately or at a defined boundary needs to be preserved deliberately, not assumed from ordinary-record equality.

A broader second option is incremental validation of genuinely added or refined records, retaining necessary reverse-reference/affected-composition checks and complete import/publication validation. This is more invasive: ordinary updates can alter parent layouts and invalidate existing mapped membership or nested paths. Merely validating the supplied one-record update would be unsound. It should not be bundled into the first no-change shortcut without separate evidence and offline acceptance.

Future offline checks should demonstrate that repeating an identical validated literal does not enumerate/reconstruct all unrelated records, while malformed or changed identities/origins/literal types still fail; genuine part refinements still advance revision and receive cross-record checks; family changes remain validated at the defined boundary; and published records retain ordinary immutable identities. These are proposed checks only. No tests, benchmarks, or implementation changes were run for this audit.

The prior material-reuse work addressed publication and repeated material loading; `docs/doe/material-reuse.md:29-35` explicitly retains registry/record checks. Byte identity of these three hot-path files across v8 and v9 is consistent with that scope. Faster publication/material reuse does not eliminate repeated whole-registry work during propagation itself.

## Limits

One paused sample establishes the active call path and, with its saved locals, a concrete unnecessary whole-registry validation on a no-change literal. It cannot establish a wall-time percentage, sustained sampling frequency, eventual convergence, full source coverage, or the number of completed registrations. The current counts are not final results. Other amplification paths, including environment growth, require their own evidence. The frozen run remains paused and unchanged.
