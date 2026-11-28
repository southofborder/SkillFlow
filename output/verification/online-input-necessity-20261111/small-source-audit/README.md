# Small-Skill source-only expectations

Finite source-only expectations for later comparison with the newly authorized batch; not a gold benchmark, model-performance label set, or actual execution trace.

Only the offline continuation-state source pins and complete source files inside the three pinned package directories were read. No historical Task, CFG, annotation, model answer or result was consulted.

| Case | Expectations | Local ambiguities | Inventory |
|---|---:|---:|---|
| 001 | 7 | 1 | [001](001.md) |
| 010 | 9 | 0 | [010](010.md) |
| 013 | 10 | 2 | [013](013.md) |

001 leaves the count scope unspecified. 010 explicitly defines optional omission and unchanged returned items. 013 leaves final-status representation and concrete outcome field encoding unspecified, while its bounded action cases remain explicit.

Every expectation has source file/line evidence in its JSON. No source was modified or executed, no real model request was made, and no historical model result was used.
