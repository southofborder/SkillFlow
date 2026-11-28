# Final correction-size audit

Derived offline validation/render-only measurements. No historical runner, replay, backend, model call or Skill execution occurred. All historical input hashes and measured code hashes remained unchanged during measurement.

Exact input and code hashes, complete-source identity, full logical/candidate/context equality, every conflict pair and target, and per-delivery hashes are recorded in `review-correction-size.json`.

| Candidate | Raw diagnostics | Displayed diagnostics | Conflict pairs | Delivery characters | Headroom |
| --- | ---: | ---: | ---: | ---: | ---: |
| a001 | 317 | 16 | 307 | 1014657 | 33919 |
| a002 | 311 | 10 | 307 | 1014077 | 34499 |

All recorded assertions passed. The complete original source section is identical to the historical prompt, every original logical input is preserved, and the full candidate and displayed correction diagnostics expand exactly. All 307 conflict pairs remain explicit across six groups; original diagnostic provenance and mappings remain audit material. The limit remains 1048576 characters, including the 212-character transport envelope.

Source-input errors and cross-record conflicts use the existing single full-response correction. Other local record errors retain existing-slot replacement. Full replies must have the exact review envelope; malformed replies cannot replace the prior candidate. The new display adds no calls or patch grammar and does not guarantee every future irreducible input will fit.

Measured code SHA-256:

- `src/skillflow/document_guided/fragments.py`: `f39f44b545681fa600b389c4b25091f56816f79ca12e1272e0a8815793519d8c`
- `src/skillflow/document_guided/review_correction.py`: `8823316638de92941857b2fcb0665880a552dbd7f7ce87b5aa8b2b40955bf67a`
- `src/skillflow/document_guided/review_isolation.py`: `a62172fbcdedb546258c2a36851d305ab12b2bca781470c2f56dd63efe275104`
- `src/skillflow/document_guided/review_display.py`: `f09b4b67ba191eb42a7be0741d14bfcf77c41ccf84d3d433053de943a5d07cf8`
- `src/skillflow/document_guided/source_review.py`: `659ed2f4330ff3c6c50841e5d685c5ba096f492ec6fd53308b7a55f987d72db4`
- `src/skillflow/common/structural_correction.py`: `31eece040ff7812122e434819967dade648943fa252f403a67183557a3bf8db5`
- `src/skillflow/common/validation.py`: `c61537bdd0b0b2091ca53a43dbbf8f93583d59511dad12f759c1c351eb5d3033`
- `tools/doe/document_guided_client.py`: `1252e65c52de4160c43e004434228f39f33cd13c0ca004ad82cc6d3c27b09f32`

Historical input file SHA-256:

- `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242/review/inputs.json`: `b42c390b7321cfe1537512fadf5670f340055080933f463debe0e786fbafcb26`
- `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242/review/prompt.txt`: `0b3e56a7e4fe121c40da417a23977eaa650bc83363c4d81bbcf7310deb9ef085`
- `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242/review/calls/review/a001/response.json`: `7fa702ae4bd4bad8a19ec8279e52ed60cb2b7f7bd69c87dd1ff504cd9158d77a`
- `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242/review/calls/review/a002/merged-candidate.json`: `c75245b12f6b8bee195019bf668f08002a50b570c9bc98607fe6d591c6a94a14`
