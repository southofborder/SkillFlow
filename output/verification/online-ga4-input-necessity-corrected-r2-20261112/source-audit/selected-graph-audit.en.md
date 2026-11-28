# Selected initial CFG audit (downstream work pending)

The selected graph is `graph/initial.json`, derived from graph step `calls/a002`; the saved validation is `valid`. Its normalized wire identity is `ad8023ba8286c1dbc91c0f2e914478e96ea673031be289bd825ddac5fd0340aa`. The graph contains **245 blocks, 232 edges and 563 IR**. All raw-to-normalized-to-canonical instruction correspondences were inspected without rerunning compilation or analysis.

## Structural correction

The two invalid merges now consume predecessor-produced `list_filtered_unchanged` and `latest_filtered_unchanged`. Each member block adds a `carry_filter_accumulator` instruction, before its predicate dispatch, returning the current accumulator unchanged. The false edge returns that result to its header; the true keep edge still appends the accepted member. The graph's edges are unchanged. Opcode/input/output changes are confined to these four filter blocks, adding two instructions; metadata/prose also changed and remain subject to semantic review.

This removes the same-block self-reference while retaining the intended filtering skeleton. Processing must implement both carry instructions as identity bindings of the existing value, with no invented transform or observation, and preserve predecessor applicability.

## Source-boundary representation

| Finite source sites | Matching selected representation |
| --- | ---: |
| SDK API acquisitions/publications | 13/13 |
| saveResult call sites | 25/25 |
| Explicit URL loops | 3/3 |

These counts use more than overlapping citations. The API checks inspect receiver inputs, request/result bindings, operation literals and output selection: GA4 first tuple response, Search Console response.data, inspectionResult projection, and URL_UPDATED versus URL_DELETED publication. Per-site reasons and complete instructions are in the JSON audit. They establish represented call skeletons, not interface necessity or backend completeness.

All 25 save instructions carry the site's payload/category/operation/optional extra and declare no output, matching ignored filepath returns. Optional save branches remain; aggregate high-level saves remain unconditional. The shared saver still reads settings, builds path and metadata wrapper, performs a replace write with no content output and returns its filepath. Required side effects and each call's actual settings/clock/file identity remain processing/mapping obligations.

All three URL loops have has_member headers, one-member selection, child calls with save:false, append/merge relationships and real backedges. Batch rejection propagates, while reindex/status preserve success-versus-catch rows and aggregate saving. Reindex's response URL overwrite and status's indexStatus-only consumption remain explicit. Occurrence/cardinality/order and URL/result correlation still require the processing loop summary and downstream evidence.

## Preserved source facts and remaining checks

The graph retains unused filters/orderBy rather than pretending they affect runReport; empty bulk input returns before API/save; metadata dimension-only and metric-only projections remain separate from full metadata; storage retains the particular settings fields used by path and metadata. These are necessary source facts for field-level analysis, not current deletion conclusions.

Task correspondence must still reconcile empty-input persistence exceptions and avoid demands for ignored saver return values. Public callable roots and summarized call sites need per-invocation/client-state/request-response bindings. Interface input necessity requires separate semantic evidence beyond current arguments. No propagation, input assessment or DOE result was available for this audit; source review and allowed semantic repair may supersede this selected initial graph.

No production, active graph or historical artifact was edited. No model, Skill, renderer, compiler, backend or replay was run. Exact identities, canonical IR references, candidate/source evidence and pending checks are in `selected-graph-audit.json`.
