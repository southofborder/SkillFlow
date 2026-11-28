# Rejected graph a001: preliminary source mapping

This audit is explicitly unselected and preliminary.

{"blocks": 266, "instructions": 675, "edges": 250, "remote_sites_with_primary_candidate": 13, "save_sites_with_primary_candidate": 25, "source_iteration_sites_with_span_match": 11, "summary_operation_candidates": 0}

- This is a rejected raw response, not the selected CFG. Structural correction a002 remains authoritative only if it passes and is selected.
- All 13 physical remote API sites have explicit external acquisition candidates with client handle and request operands; processing must still establish actual request/response and network boundary semantics.
- All 25 saveResult sites are represented by call_saveResult instructions with source spans and write-effect descriptions. No caller storage exposure is established until processing/propagation connect these calls to actual write behavior.
- The raw runReport acquisition keeps all seven input options including filters and orderBy. Their result names report_filters and report_order have zero consumers in this candidate, preserving actual acquisition while reflecting omission from the outgoing request.
- No instruction in this raw candidate represents the Markdown summary workflow. Task requires analysis-summary, so the final mapping/review must account for this omission or retain a concrete gap.
- The two direct structural failures are self-read merge outputs in list_filter_head and latest_filter_head. The recorded endpoint failures follow from those rejected block definitions; this passive audit does not independently validate the rest of the graph.
- Loop/member calls retain opaque caller boundaries, including normal/error outcomes. Their metadata describes network effects and per-member save=false, but metadata and processed-IR counts alone do not establish actual boundary coverage.

## Recorded structural failures

- RESULT_READ_BEFORE_DEFINITION at /blocks/247: : Value error, block 'block_248' (list_filter_head), instruction 'ir_633', input[1]: RESULT 'result_344' ('list_filter_current') is read before instruction 'ir_633' defines it
- RESULT_READ_BEFORE_DEFINITION at /blocks/259: : Value error, block 'block_260' (latest_filter_head), instruction 'ir_659', input[1]: RESULT 'result_359' ('latest_filter_current') is read before instruction 'ir_659' defines it
- CFG_STRUCTURE_INVALID at : : Value error, EDGE_ENDPOINT_NOT_FOUND: edge[227] target block 'block_248' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[228] source block 'block_248' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[229] source block 'block_248' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[231] target block 'block_248' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[232] target block 'block_248' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[242] target block 'block_260' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[243] source block 'block_260' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[244] source block 'block_260' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[246] target block 'block_260' does not exist; EDGE_ENDPOINT_NOT_FOUND: edge[247] target block 'block_260' does not exist

Response file SHA256: e06b1a7e55576cadf851171ee420d77f25584928e35352285c505bc430a70a64
Validation file SHA256: cc8104e315c8af9b029e3ec586d9d40b45fb6a6e1b391486e8eac693f56c1bb9

No graph compiler, validator, propagation, demand solver, DOE or replay was invoked by this helper.
Source-span matches and metadata are preliminary traceability only, not semantic correctness, reachability or coverage proof.
