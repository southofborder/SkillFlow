# Accepted initial CFG: source audit

The accepted a002 graph contains 268 blocks, 679 IR and 252 edges. Processing is not yet audited in this snapshot.

Bound graph/initial.json SHA256: 24befff7f6e705d0fe53a02f5552ab82bd0644ed7a05ce9cbad6fc0cde557fc3

- This snapshot is the accepted initial CFG from graph a002. It is not yet the final selected CFG after whole-chain source review or semantic repair.
- Structural correction changes the initial count from 266 blocks/675 IR/250 edges to 268 blocks/679 IR/252 edges. Two filter skip blocks carry the previous accumulator into distinct result versions, replacing the self-read merge operands. All a001 artifacts and its preliminary audit remain preserved.
- The whole-response correction also rewrites metadata/source spans beyond the two failed merges: 107 spans are removed and 27 altered among shared instructions; 372 accepted spans remain, all within the frozen source and matching their compiled script_content. The client-cache initializer additionally gains three explicit external cache-slot operands. These changes require auditing the accepted material itself; they do not mean source files were removed from the complete prompt.
- Every physical remote API site has one explicit external acquisition IR with endpoint identity, receiver handle and request operands. This is CFG representation, not proof that processing modeled or propagation reached the network boundary.
- Every physical saveResult call has one call_saveResult IR. These carry payload/category/operation/optional extra operands and write-effect prose. They still require actual storage effects at the calling occurrence; a standalone saveResult body or local-tool operation does not establish caller exposure.
- Seven explicit iteration heads cover URL normalization, the three URL loops and storage filter/map/filter. The two report name mappings, bulk metric mapping and storage sort remain within broader build/sort IR. Exact member/field and ordering demand depend on later processing contracts.
- The accepted graph preserves source acquisition of filters and orderBy as separate outputs, with zero downstream consumers. It also preserves the truthy limit branch. The documented filter/order obligations remain unfulfilled source behavior; SDK zero-limit semantics remain unproved.
- The graph constraints/diagnostics acknowledge the Markdown summary workflow and its absent runtime writer, but there is no summary operation IR. Task analysis-summary remains distinct from implemented TypeScript coverage and needs an explicit realization/gap in the later mapping.
- Normal and error outcomes for high-level URL loops describe member pairing and external attempts. Their actual request, response and log/storage events must be inspected in the accepted processing and recorded outcomes before claiming boundary coverage.

## Remote site mapping

- skill/scripts/src/api/bulk-lookup.ts:183 → ir_175
- skill/scripts/src/api/indexing.ts:62 → ir_346
- skill/scripts/src/api/indexing.ts:119 → ir_366
- skill/scripts/src/api/indexing.ts:152 → ir_387
- skill/scripts/src/api/metadata.ts:42 → ir_246
- skill/scripts/src/api/metadata.ts:64 → ir_260
- skill/scripts/src/api/metadata.ts:86 → ir_274
- skill/scripts/src/api/realtime.ts:28 → ir_190
- skill/scripts/src/api/realtime.ts:48 → ir_204
- skill/scripts/src/api/realtime.ts:68 → ir_218
- skill/scripts/src/api/realtime.ts:88 → ir_232
- skill/scripts/src/api/reports.ts:100 → ir_110
- skill/scripts/src/api/searchConsole.ts:102 → ir_312

## Save site mapping

- skill/scripts/src/api/bulk-lookup.ts:188 → ir_180
- skill/scripts/src/api/indexing.ts:76 → ir_357
- skill/scripts/src/api/indexing.ts:101 → ir_422
- skill/scripts/src/api/indexing.ts:133 → ir_377
- skill/scripts/src/api/indexing.ts:189 → ir_407
- skill/scripts/src/api/metadata.ts:51 → ir_250
- skill/scripts/src/api/metadata.ts:73 → ir_264
- skill/scripts/src/api/metadata.ts:91 → ir_278
- skill/scripts/src/api/realtime.ts:35 → ir_194
- skill/scripts/src/api/realtime.ts:55 → ir_208
- skill/scripts/src/api/realtime.ts:75 → ir_222
- skill/scripts/src/api/realtime.ts:95 → ir_236
- skill/scripts/src/api/reports.ts:105 → ir_115
- skill/scripts/src/api/searchConsole.ts:118 → ir_317
- skill/scripts/src/index.ts:73 → ir_437
- skill/scripts/src/index.ts:104 → ir_450
- skill/scripts/src/index.ts:135 → ir_463
- skill/scripts/src/index.ts:162 → ir_476
- skill/scripts/src/index.ts:200 → ir_489
- skill/scripts/src/index.ts:222 → ir_499
- skill/scripts/src/index.ts:252 → ir_514
- skill/scripts/src/index.ts:272 → ir_525
- skill/scripts/src/index.ts:292 → ir_536
- skill/scripts/src/index.ts:316 → ir_555
- skill/scripts/src/index.ts:343 → ir_574

Source-span checks: {"source_span_checks": 372, "invalid_source_span_ranges": 0, "compiled_script_source_mismatches": 0}

No compiler, validator, solver, propagation, DOE, model or replay was invoked by this passive audit.
Valid source spans and accepted CFG structure do not prove correct source semantics, dynamic reachability or actual network/storage effects.
Rebind and compare the final selected CFG and annotation after whole-chain review; do not silently replace this initial snapshot.
