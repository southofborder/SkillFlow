# Independent delivery observation — provisional

This observation belongs only to `document-guided-ga4-lossless-delivery-high-20261122-211742`, implementation `6126c7ba84984aec0d20ead0693df291ea3978a4072056dbd6428321bdfd627b`. It does not close the run or replace root's final request audit. At 2026-11-22 14:16:49 UTC, eight fresh requests had PID and complete public-usage receipts, while no controller-finished receipt existed. Final cost and replay conclusions remain pending controller closure.

All eight saved preflight records match the actual delivery character count, UTF-8 byte count, SHA-256, section-size sums and logical core prompt digest. Every delivery contains all 16 frozen source files with exact original numbered lines. The source bytes match the run protocol. Every observed delivery is below the unchanged 1,048,576-code-point limit.

| Actual request | Delivered code points | Shape |
|---|---:|---|
| Processing normal | 431,150 | Complete shared processing input |
| Processing correction | 461,502 | Shared original input plus correction material |
| Sensitivity normal | 476,237 | Shared fragment input |
| Task correspondence normal | 516,118 | Shared fragment input with sealed Task |
| Source review normal | 909,828 | Complete review delivery |
| Source review correction | 918,793 | Complete corrected review delivery |
| Scoped graph revision | 194,148 | Shared `cfg` scope |
| Scoped processing revision | 308,564 | Shared processing scope and runtime contract |

The complete numbered-source section is 180,842 characters in each fragment delivery, with one exact full-source body retained. Review deliveries also retain every source file. Shared scope encoding preserves the supplied finite scope; this audit does not assert that a model's chosen semantic scope or its answer is correct.

For a controlled encoding-only comparison, the inspector expands each saved JSON display body and substitutes its compact expanded JSON while holding every other delivered character fixed. This is a size reference, not a new submitted prompt or a reconstruction of a historical renderer:

| Normal fragment | Actual shared delivery | Same-payload expanded reference | Characters saved by JSON encoding |
|---|---:|---:|---:|
| Sensitivity | 476,237 | 1,030,256 | 554,019 |
| Task correspondence | 516,118 | 1,078,676 | 562,558 |

Both expanded payloads were separately compared against their bound saved inputs. Sensitivity expands exactly to the original processing document and displayed selected CFG, without Task. Task correspondence expands exactly to the same processing/CFG plus the sealed Task and complete expression-reference view. These equality checks establish lossless input delivery; they do not establish semantic accuracy of generated annotations. The correspondence expanded reference exceeds the adapter limit, while its actual shared delivery fits.

The accepted offline saved-input evidence uses a different preserved processing answer and reports sensitivity normal/full-revision sizes 495,187/495,675 and task-correspondence normal/full-revision sizes 540,921/541,392. Its round-trip and complete-source checks passed. These offline values are retained as coverage of those rendering paths. Their difference from the current normal sizes is descriptive because the processing answers differ; it is not an encoding-effect, token-cost or latency estimate. No live sensitivity or task-correspondence correction/revision delivery was present in this observation, so their actual online behavior is not claimed here.

The three inherited initial stages and their 303,082 known public tokens are excluded from fresh counts. Root owns the sole replay. The inspector reads public records and invokes only a pure decoder; it starts no model, API, Skill, runner or replay and does not change frozen code or artifacts.

Evidence:

- `independent-delivery-audit-20261122T141649Z.json`: exact actual delivery/preflight/source/encoding and provisional request observations.
- `independent-normal-fragment-input-equality.json`: normal-input equality against original bound processing, CFG and Task.
- `../lossless-delivery-20261119/saved-inputs-accepted.json`: accepted offline same-material round-trip evidence for normal/full-revision paths.

Original network notices and partial/failed semantic stages remain in the run. The later final audit must reconcile all reached requests, prestart rejections, native exits, counters, controller timing and the sole replay without converting internal connection messages into extra outer launches or provider HTTP totals.
