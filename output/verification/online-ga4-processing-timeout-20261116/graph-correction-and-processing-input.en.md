# Accepted graph correction and initial processing input

This passive snapshot concerns the sole active GA4 run `document-guided-ga4-processing-shared-high-20261116-225414`. It reads the new saved bytes and expands presentation codecs only. It does not compile, validate, replay or execute an analysis. The model's processing response is still pending at the snapshot; no output-compression or processing-latency conclusion is available yet.

## The shared processing input retains the complete logical material

The actual processing prompt is 425,423 characters. Its structured input envelope is 190,095 characters and expands exactly to the 252,386-character logical payload: 62,291 characters, or 24.68%, less serialization for that body. The envelope uses 91 shared definitions and six record-column sets.

The logical payload contains exactly `documents`, `cfg` and `runtime_contract`; the only document is `flow`. It contains 521 distinct current CFG instruction IDs. The flow text matches the saved flow document. No Task object is supplied to processing.

All 16 readable source files, totaling 155,170 raw bytes, match their frozen digests. Their 180,825-character line-numbered source rendering appears verbatim in this processing prompt. The source was not shortened to produce the input reduction.

Two separate equivalence checks must not be conflated:

- **Codec equivalence:** expanding the actual shared input preserves the complete actual logical processing payload, with its bound logical digest `3a3d40f6f5084b49b548c28be8f737ffcaf623b9ddc6833ca84258c94d22dbcc`.
- **CFG display equivalence:** that logical payload contains the existing source-normalized CFG display, not a byte-identical copy of the raw saved CFG artifact. There are 294 `metadata.script_content` occurrences omitted from the display, each exactly present in the complete rendered source. After removing only those already-rendered code copies from the saved CFG, it equals the displayed CFG. This existing duplicate-source presentation rule is separate from shared JSON encoding; no other CFG field is omitted by this comparison.

For a same-material whole-prompt comparison, placing this exact current flow/CFG/runtime material in the previous plain `DOCUMENT`/`CFG`/`RUNTIME_CONTRACT` sections while retaining the same source and output instructions gives 486,361 characters. The actual shared prompt is 60,938 characters, or 12.53%, shorter after accounting for shared-format instruction overhead. No alternative request was sent. A simpler body-only accounting that leaves all surrounding current text untouched gives 487,714 characters; its difference is 62,291. These are character measurements of identical current logical content, not token savings, a historical prompt comparison or a speedup claim.

## What the full graph correction changed

The controller's saved a002 validation status is `valid`, and `steps/graph/result.json` selects a002. The correction retains all 237 blocks in the same order and the exact same 217-edge array. Instruction count grows from 519 to 521.

The response supplies the previously missing carry versions in two existing body blocks:

- `list_filter_body` adds `retain_filter_accumulator`, consuming `list_paths_current` and producing `list_paths_retained`. `list_filter_head` then uses `list_paths_retained` for that predecessor instead of reading its own newly produced current value.
- `latest_filter_body` similarly produces `latest_filtered_retained`, which `latest_filter_head` consumes for the reject predecessor.

Thus the observed representational repair involves four operational block records, not merely the two head records identified by the primary diagnostics. This supports the earlier warning that the 1,250-character size of the two diagnostic roots was not a sufficient repair-scope or savings estimate. Whether these pass-through operations and their predecessor pairing faithfully express the source and are supported by processing remains a semantic question for the later processing/source-review stages. A saved schema/compiler acceptance receipt does not answer it.

The full regeneration changed 110 block objects. Of those, 105 differ only inside `metadata`; one additional block, `summary_read`, also paraphrases its constraint. The remaining four are the two head/body pairs above. Metadata includes source interpretations and effect descriptions, so “metadata-only” is not a claim of semantic equivalence. Five original global constraints are rewritten and a sixth explicitly describes `call_saveResult` wrapping the supplied data under `data`, reading save-time settings, creating the directory when needed and writing JSON. That is an additional model-authored description; it does not establish that processing actually constructs the wrapper and models each occurrence's storage effect.

| Saved graph response measurement | a001 | a002 |
| --- | ---: | ---: |
| Prompt characters | 212,612 | 376,241 |
| Complete response characters | 164,162 | 164,092 |
| Compact parsed response characters | 161,209 | 159,297 |
| Native process elapsed seconds | 985.053306 | 934.197419 |

Both native processes exited successfully. The correction response was another complete graph of almost the same raw length. Elapsed values include the whole native request lifecycle and are not pure generation times. No causal performance comparison follows from these two values.

## Issues retained for semantic review

The corrected graph still supplies nine model-authored diagnostic notes. They concern invocation-to-file provenance and the unspecified summary writer; documented auto-save versus executable save conditions; Search Console date-format compatibility; conflicting top-page ranking descriptions; omitted report `filters`/`orderBy` and metadata return-wrapper differences; cached credentials and settings timing; direct-run path equality; empty-list handling and path matching in storage examples; and which progress logs were folded into surrounding actions. These are saved allegations/limitations, not independently accepted final findings. Later source review and actual propagation must determine their supported scopes.

The general follow-up proposal remains: typed causal attribution for compiler cascades, correction scope covering actual producer/predecessor dependencies, complete read-only reference context, and unchanged full post-merge validation. The observed four-block repair suggests a bounded existing-record response could express this particular structural correction; it does not prove that those four records could have been selected safely from the original two error paths alone. Preserve the whole-response fallback when a correct repair requires changed topology, new block records or an unexplained global defect. Pure local filter/map granularity guidance remains a separate future proposal.

Evidence: `presentation-audit/20261116T152936589429Z.json` records the actual processing input/source check; `graph-correction-and-processing-input-accepted.json` records exact graph differences and same-material character accounting. The earlier preliminary graph report and raw failures remain unchanged. No frozen code, prompt, controller, budget or model call was changed for this audit.
