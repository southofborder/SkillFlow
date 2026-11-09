# Reusing validated analysis material

This offline change follows the completed GA4 and 001/010/013 v8 validation.
Its purpose is to reduce repeated local reconstruction and validation. It does
not change the seven semantic requests, model formats, runtime semantics or
the source-based incompleteness recorded in those runs.

## Ownership and normal reads

An accepted guided step already stores its normalized value, terminal selection,
request-chain identity and byte hashes. `load_step` now reads that value while
checking its saved identity, dependencies, terminal state and request artifacts.
It does not rerun semantic validators over every original and corrected answer.
An explicitly partial step may have an empty `validation_gaps` list: a mapping
gap can instead live in its requirement realization. Partial status is preserved.

`load_annotation` uses the saved raw annotation, compiled annotation and
compilation map. Their manifest, source/CFG/Task bindings and artifact hashes
remain checked. Normal reading does not assemble the three fragments again.
Explicit `recompute=True` retains response reconstruction and compilation, with
the original implementation requirement. The existing standalone legacy loader
keeps its stronger reconstruction path.

These are short-lived values owned by a read or calculation. There is no global
cache, disk cache index, invalidation service, new protocol or additional model
request. A new call reads its current referenced artifacts rather than silently
returning a value cached by a previous call.

## Publication reuses the checked input

Guided propagation loads its accepted annotation once and carries it through
calculation and saving. The saved-artifact path can reuse the existing compiled
annotation; public factories receiving raw fixture material still compile and
validate it. Registry, record, CFG, seed, receiver and binding checks remain.
The final manifest is attached to the checked facts without reconstructing all
facts a second time. Before commit, lightweight identity and artifact checks
detect changed inputs.

DOE publication similarly retains one checked propagation bundle and the freshly
computed review. It solves demand once and writes that review, index and support
instead of repeatedly reloading propagation and reconstructing the same review.
Normal external DOE reads still validate the saved result and references.
Downstream demand material must match its verified propagation owner exactly;
canonical identity keeps distinctions such as `false` and `0`. It no longer
recompiles an annotation already owned by that checked bundle.

## Reuse within assembly and indexing

One processing expansion supplies the case aliases and member-scope coordinates
used by all sensitivity declarations during validation. Assembly shares that
checked expansion across the three fragment owners. Final combined compilation
and correspondence checks remain. This removes a whole-fragment expansion per
case-related declaration while retaining candidate identities, occurrence
pairing, source evidence, local returns and diagnostic paths.

The CFG target index walks known positions directly. It checks duplicate IR
identities once and constructs the same independent entries without scanning all
IR again for every generated target. External target resolution retains its
canonical-address and path checks. Sensitivity-result validation also shares one
demand target index across its declaration and reference checks.

## What this does not establish

The source/CFG/processing mismatches in the four online runs are unchanged. Faster
reads do not repair those semantic gaps or make their propagation complete.
Frozen runs, answers and failures are not migrated, overwritten or replayed by
this implementation work. Measured improvements are offline component results,
not a new GA4 latency, token-cost or accuracy result.

See the [offline acceptance report](material-reuse-offline.zh.md) and the
[four-run online assessment](../../output/verification/general-loops-v8-online-20261101/assessment.en.md).
