# GA4 r2 selected assembly and failed review audit

The selected assembly is structurally assembled but unreviewed. Assembly `partial` is triggered by the existing 13 processing gaps; it is not a new assembly validation rejection (`runner.py:424`). It retains 561 modeled IR and two explicit unmodeled IR, `ir_419` and `ir_423`, with zero validation-origin gaps. Processing operators and contract bodies are unchanged from selected processing; assembly adds sensitivity and 40 operation-demand attachments across 38 IR. The compiled material contains 616 events, 191 demands, 9 expressions and 3 constraints.

The actual inventory has 344 obligations linked one-to-one by ID to 344 compiled contracts over 209 IR: 92 compute, 146 delivery and 106 receipt obligations. The 106 wire calls expand to request/response pairs. Review scope rows comprise 252 interface, 513 required, 337 remainder, 92 rule and one unresolved-range scope. These are structural counts, not accepted semantic relationships.

Unified review failed before a CLI process started: the input was 1,079,505 characters, above the 1,048,576-character limit by 30,929. The immutable receipt binds source, CFG, annotation, contracts, obligations and failed review, and explicitly records `source_review_complete:false`, `review_status:request_failure` and zero checks. None of the 344 contracts is source-reviewed. This is an input-size failure, not a connection timeout.

The selected-processing source concerns remain open: all 13 API call summaries omit the actual client handle from processing operands/receiver bindings, all 25 saveResult sites use a task-retained local-tool delivery without their per-call persistent write effect, and helper summaries do not by themselves reproduce source internal reads/writes. The failed review supplied no acceptance or correction for them. See `selected-processing-audit.en.md`; no automatic repair was made.

Exact bindings, identities, gaps and per-IR obligations are in `assembly-review-audit.json`. This audit reads saved artifacts only and makes no completed DOE claim.
