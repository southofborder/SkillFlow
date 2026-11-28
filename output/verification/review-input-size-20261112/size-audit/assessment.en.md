# Source-review input-size diagnosis and lossless display measurements

The rejected GA4 review delivery was **1,079,505 Unicode codepoints**, 30,929 above the unchanged 1,048,576 adapter cap. Its complete source was delivered once. The excess was not caused by duplicated full fragments or by transmitting the entire 10.87-million-character local audit material.

The current review joins a large annotation with a separate mandatory contract-review inventory. Both carry necessary information: the annotation supplies actual semantics and contracts, while the inventory identifies every actual obligation and review scope. Repeated JSON field names, descriptors and exact values can be shared without removing either representation's information.

## Exact character accounting

| Delivery component | Codepoints |
| --- | ---: |
| Transport envelope | 212 |
| Review instructions | 17,868 |
| Response-format instructions | 6,152 |
| Logical INPUT_JSON | 874,402 |
| Complete numbered source | 180,825 |
| Section delimiters | 46 |
| Total | **1,079,505** |

The source contains 16 files with 154,973 raw codepoints (155,170 UTF-8 bytes). File labels, physical-line numbering and source wrappers account for the difference to its 180,825-character rendered section. That entire section remains byte-identical in the measured new view.

| INPUT_JSON value | Codepoints, excluding its top-level key/separator |
| --- | ---: |
| Annotation | 403,839 |
| Mandatory contract inventory | 244,455 |
| Compact semantic CFG | 154,115 |
| Task | 39,090 |
| Runtime contract | 22,020 |
| Processing gaps | 10,579 |
| Availability | 123 |
| Stage failures / fragments / observations | 2 each (`{}`, `{}`, `[]`) |
| Partial flag | 4 |

The annotation contains 327,813 characters of IR semantics, 43,759 of realizations, 12,889 of demands, 12,486 of locations and 6,794 of processing gaps. Its fields and the separate richer processing-gap records must remain available.

The inventory contains **344 obligations and 1,195 scopes**: 252 interface, 513 required, 337 remainder, 92 rule and one unresolved-range scope. Scope arrays occupy 163,784 characters. Their unique IDs alone account for 48,995 value characters; field descriptors and effective optionality semantics remain necessary and are not discarded. Actual contracts remain in the annotation; the compact inventory does not duplicate their complete bodies.

## What is and is not duplicated

- Full fragments are empty in this selected request, and observations are empty. Removing them would save only a few characters and would not solve the overflow.
- `review/inputs.json` is approximately 10.87 million characters because it preserves target indexes, binding, compiled material and audit metadata. Most of that local material is already excluded from the actual model view.
- Exact repeated values include source file paths, local bindings, source/rule evidence records, whole-value selectors, optionality descriptors and repeated contract requirement lists. Shared definitions preserve a copy at every original logical occurrence after expansion.
- Repeated field names in the obligation and scope records account for substantial presentation overhead. A global column-set table retains their exact field order, values, absent-versus-null distinctions and array occurrence order.
- There are 1,161 explicit file/start_line/end_line reference objects. No delivered quote, excerpt, source_text or content field duplicates its physical source span. Remaining delivered `script_content` fields are also absent: the existing CFG compact view already removes source-contained snippets. A proposed additional source-excerpt deduplication therefore has **zero justified savings** for this request. Semantic Task `text` and evidence `reason` fields are not raw source excerpts and were not removed.

Potential repetition counts overlap when a duplicate contains smaller duplicates. They must not be added together to claim total savings. The measurements below actually encode the complete payload and expand it back.

## Reversible alternatives measured

These exploratory totals preserve the entire source section and original non-payload text. They exclude new format instructions unless explicitly stated.

| Representation | Full delivery | Savings | Remaining cap headroom |
| --- | ---: | ---: | ---: |
| Original | 1,079,505 | 0 | -30,929 |
| Separate scope tables inside each obligation | 1,053,868 | 25,637 | -5,292 |
| Shared scope column sets across the inventory | 1,018,716 | 60,789 | 29,860 |
| Exact shared-value dictionary alone | 963,659 | 115,846 | 84,917 |
| Shared scope columns plus exact shared values | 902,870 | 176,635 | 145,706 |
| Generic record-array tables plus shared values | 892,774 | 186,731 | 155,802 |
| Generic record-array/map tables plus shared values | 866,451 | 213,054 | 182,125 |

The chosen implementation limits column tables to the mechanical obligation/scope inventory rather than applying tables to all semantic objects. It combines those tables with readable exact shared values. This retains more ordinary named JSON structure in the annotation and CFG than the most aggressive generic alternative.

## Implemented display and measured result

The new `src/skillflow/document_guided/review_display.py` exposes `pack_review_payload`, `expand_review_payload` and `display_instructions`, with format identity `skillflow-review-display-v1`.

Its visible envelope contains `format`, `record_columns`, `shared_values` and `payload`. `$ref` names one exact visible shared value. `$rows` preserves an ordered record array by an explicit column-set index followed by every value. `$literal_object` escapes literal dictionaries containing marker-like keys. It uses no gzip, base64, external files, model tools or hidden semantic inference.

The measured production codec retained 591 shared definitions and nine column sets. Its displayed payload is **697,322 characters**. Including the complete source, the existing instructions and response schema, the 212-character transport envelope, and the new **1,349-character legend**, the full measured delivery is **903,775 characters**: **175,730 fewer**, with **144,801 characters of headroom**.

Expansion was compared by insertion-order-preserving compact JSON serialization, not only Python equality. It exactly reproduces the original 874,402-character logical payload, including numeric type distinctions, every one of the 344 obligation IDs, every one of the 1,195 scope IDs, their order, all annotation contracts, and every field. The complete source section SHA remains `ea5d92b44a5540b818ec0c54954c5373a0fefdd93f099565177871395964d2c4`. Packing took approximately 0.77 seconds and expansion 0.05 seconds in the local measurement; these are formatting observations, not model-latency evidence.

The codec chooses the smallest complete marked envelope among plain escaped values, optional exact sharing, inventory tables and their combination. Its constant envelope overhead is explicit. The renderer additionally selects the packed view only when the complete encoded JSON plus legend is smaller than the old logical JSON; otherwise it retains the old raw logical payload. Consequently, the integrated new view does not enlarge a formerly admissible irreducible prompt. A separate pure-render measurement of the integrated `shared-v2` builder confirms the same **903,775-character delivery and 144,801-character headroom**, exact source-section bytes, and exact serialized payload expansion. Rendering the historical `compact-v1` material with the current builder reproduces its old prompt byte for byte.

Malformed/missing/cyclic references, mixed marker objects, invalid table widths or indices, duplicate columns and duplicate literal-object keys fail with English diagnostics. Source text never enters the codec. Target IDs continue to identify the expanded original coordinates, and paired request/response obligations remain separate. The response schema and number of semantic requests are not changed by this display module.

## Evidence and limits

`request-size-breakdown.json` contains exact component accounting and nonadditive repetition examples. `shared-values-measurement.json`, `record-table-measurement.json` and `source-excerpt-duplication.json` preserve alternative measurements. `production-codec-measurement.json` binds the implemented codec and exact roundtrip/source checks. `integrated-codec-measurement.json` independently records the actual builder result, its source-file identities and historical compact-view equivalence. `new-delivery-measured.txt` and `integrated-new-delivery-measured.txt` are new local formatting artifacts, not model requests or replacements of historical prompts. The finalized codec SHA-256 is `f09b4b67ba191eb42a7be0741d14bfcf77c41ccf84d3d433053de943a5d07cf8`; this agent will make no further production changes after this measurement.

No model call, Skill execution, historical replay or full backend analysis was performed. The frozen historical requests were only read. The initial measurement helper briefly failed while counting mapping keys; correcting its `Counter.update` input changed only the new audit helper and did not affect any historical artifact or analysis result.

Byte/JSON equivalence proves preservation of supplied material, not that a model will understand it or return a semantically complete review. A later real GA4 run remains necessary, owned by root after the authorized offline acceptance. This measurement does not justify raising the adapter cap, dropping a contract, truncating source, or adding a semantic stage.
