# Prompt restructuring and validation

The first experiment is complete and did not demonstrate reduced correction cost. The follow-up is [targeted prompt rework and first-response screening](prompt-first-response.md). It retains the seven sections below and repairs the exact teaching content rather than replacing the architecture. The historical comparison and three-case procedure described later on this page records the preceding experiment; it is not authorization to run those cases again.

This revision compresses post-CFG model requests while preserving source-only Task extraction, fixed-Task annotation, four-axis review, two controlled repair routes, and per-seed provenance. It does not change business fields, runtime rules, or deterministic analysis algorithms.

## Language

As confirmed on 2026-10-16, maintained prompts, synthetic examples, model-authored interpretations and reasons, program diagnostics, and new reports use English. The new three-case experiment follows this policy. Genuine source documents and user input retain their original language in general production services; evidence is never silently translated. Historical frozen artifacts are unchanged.

The fixed pilot explicitly derives an English source and CFG text version for 001 and records every change. Its graph topology, IR IDs, operand structure, paths, and business literals remain unchanged; no graph is re-extracted. The already-English 010/013 input bytes are preserved. This is an assistant translation, not a semantic-equivalence proof. Discussion with the user may remain in Chinese.

## Calls and isolation

Normal execution uses three semantic calls: Task extraction, joint annotation, and initial review. Annotation-only problems add one full annotation repair and independent review, for five calls. Task problems add isolated Task revision, full reannotation, and independent review, for six. Both repair routes share one semantic budget. Structural corrections remain unlimited and separately counted, as are HTTP retries.

Task extraction sees only complete source and the independent user request. Task revision additionally sees the old Task and restricted issue categories, source spans, and requirement IDs. Reviews exclude propagation facts, DOE conclusions, assistant opinions, and evaluation answers. Independent rereview excludes initial findings and repair instructions.

## Joint annotation prompt

```text
Authority and responsibility
  Realize the fixed Task; interpret the implementation; do not decide DOE
Actual input
  Complete source, user request, sealed Task, CFG, runtime contract
Compact output format
  Response branches, required relations, evidence, references, scope
Construction order
  Locations -> processing -> sensitivity -> demands/expressions -> realizations
Semantic decisions
  Properties, payload positions, repeated calls, open descriptions and gaps
Independent synthetic contrasts
  A short complete example and focused local relationships
Final checks
  Coverage, references, seed/status consistency, one complete JSON object
```

This construction order adds no response fields or execution order.

## Semantic review prompt

```text
Authority and limits
  Check source -> Task -> realization -> demand -> operation
Actual input
  Original material, current candidate, generated targets, goals, observations
Compact output format
  source_checks / requirement_checks / goal_checks / reviewed_ir_ids / findings
Four axes
  Source obligations, every requirement, every seed, every IR
Routing and legitimate exceptions
  Isolated Task revision or fixed-Task annotation repair; conservative relations
Independent synthetic contrasts
  Material differences, valid targets, and similar but valid representations
Final checks
  Missing/overbroad demands, separate calls and terminals, evidence and suggestions
```

Valid references establish location, not semantic support. Complete checks, structural validity, and empty findings do not prove semantic completeness.

## Required demand distinctions

- `filter_items` produces a collection; its expression defines member selection. Membership/shape does not automatically require every member's complete value. Collection-root `truth` cannot substitute for a predicate.
- Shape, cardinality, field values, and actual Boolean results remain distinct. Required downstream fields, counts, conditions, and same-element relations propagate backward.
- Genuine whole-value requirements and conservative retention from opaque processing remain legitimate, with different grounds.
- Each applicable delivery, retry, and terminal save is checked at its own input. Equal data does not transfer one receiver's demand to another.
- Unspecified encoding does not erase the supported abstract result-to-current-write relation. Retain remaining gaps without inventing an encoding or whole-value obligation.
- Upstream seeds, action-only seeds, and conservative request retention from `receive` do not replace explicit parameter requirements. Do not automatically add whole-value seeds to all sinks.

## Format and structural correction

The program keeps the full strict Schema. The compact model reference is generated from it, defining shared types once. Unsupported Schema features fail explicitly.

Correction retains authority, actual input, format, workflow, rules, and necessary semantic-repair context. Only precisely marked generic examples and self-checks are removed. Parseable candidates are compact objects; invalid JSON and duplicate keys remain raw. This display does not overwrite the accepted response or repair business relations.

Independent mechanical errors are batched at actual candidate paths. Failed prerequisites prevent dependent checks. The model returns a complete replacement, not a patch. Names and opcodes do not generate missing semantics. Valid cannot_assess, transport/truncation, identity, and implementation failures stop rather than becoming unlimited corrections.

The original experiment used correction protocol v4. The targeted follow-up uses v5, retaining raw diagnostics while deriving a mapped, compact display and error-specific teaching examples. Recovery reuses accepted responses; replay reconstructs the same request, diagnostics, and stopping decision with zero API calls. Historical chains are not migrated.

## Validation and comparison

Validate contracts, examples, demand relations, four-axis review, repair routes, recovery, and replay first. Three held-out synthetic inputs each receive old/new prompts, for six initial chains with identical inputs, configuration, validator, and diagnostics.

The historical old template remains frozen. Its sent version has a recorded English projection of the teaching reasons and output-language instruction. This compares language-aligned old/new organization, not byte-identical historical requests. The old template is experimental data, not a second production service.

Then run fresh Task extraction and the formal 001/010/013 chains using the audited English inputs and existing CFG structure. Keep reasoning settings unchanged. Save all new artifacts separately and verify historical hashes.

Measure static characters/UTF-8 bytes, first-response validity, corrections, repeated errors, actual API usage, elapsed time, and semantic preservation separately. Reasoning/cache counters are components, not extra tokens; missing usage stays unknown. Freeze online timing before replay.

This small experiment does not establish general accuracy. Check source obligations, Tasks, realizations, raw seeds, derivations, and corresponding sink inputs. DOE count changes are insufficient. Unformalized limitations continue to block unsupported reductions under existing conservative rules.
