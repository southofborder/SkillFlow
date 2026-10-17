# Structural correction and semantic review

Program validation checks JSON, types, references, evidence locations, and compilation constraints. A complete response that violates these mechanical contracts can trigger a new full-response correction request. Production structural correction is unlimited; semantic repair has one shared budget. Their counts and conclusions remain separate.

## Execution and binding boundaries

Task extraction, annotation, review, and their supported revision paths use the same response-processing mechanism. The normal semantic paths remain 3, 5, or 6 calls. Structural correction does not consume the semantic repair budget and has no hidden repetition, stagnation, or cumulative-time limit. Transport retry and per-request timeout policies remain unchanged.

User interruption stops subsequent requests. Valid `cannot_assess`, incomplete transport, output truncation, identity mismatch, damaged material, disk errors, and implementation faults are stopping conditions, not invitations to correct indefinitely. Only explicit mechanical diagnostics authorize a correction call; arbitrary Python exceptions do not.

A sealed Task receives no CFG. Annotation realizations can refer generally to graph, block, IR, constraints, or metadata. Executable demands must target actual supported values or actions. IR and block anchors require `path: []`; operand references use `instruction_id`, `side`, and `index`. A name string is not the operand it names.

`ValueRef.input[index]` addresses an input of the enclosing IR. An operation demand's `input/index` addresses that atomic operation's consumption slot. Ordinary return uses the real CFG input without inventing an output or external receiver. Control expressions use the source block dispatch inputs; locals cannot cross IR boundaries.

These checks establish valid representation and references. Task fidelity, sensitivity completeness, appropriate information ranges, and evidence sufficiency remain semantic questions. Missing demand seeds remain visible diagnostics rather than being invented for validation.

## Restricted JSON normalization

`common/json_normalization.py` defines `skillflow-json-normalization-v1`. It accepts one unambiguous wrapper edit: a complete strict top-level JSON object followed, apart from JSON whitespace, by exactly one extra `}`. A decoder locates the object boundary; only that character is removed before full validation. Already valid responses are unchanged.

Duplicate keys, non-finite numbers, multiple objects, explanatory text, Markdown fences, multiple surplus brackets, missing brackets, and truncation are not repaired. Business validators remain strict when called directly. Normalization runs only after call completion and verification of response and request identity; incomplete transport and `finish_reason=length` cannot become successful candidates.

Original `call.json`, `transport.json`, and `response.json` are preserved. An applicable edit produces `normalization.json`, recording policy version, text-string digests, deleted character, and Unicode character offset without copying the full response. `validation.json` binds the response, candidate, and receipt; the receipt digest is null when no edit applies. A normalized candidate can still fail business validation.

Recovery and replay reconstruct the edit and compare receipts, digests, validation, and final selection. Missing, altered, inapplicable, or duplicate-key receipts are rejected. Normalization is counted separately from logical calls, model corrections, semantic repair, and HTTP attempts.

## Mechanical diagnostics and correction protocol v5

The original validator diagnostics remain in the audit record. The model-facing projection groups alternative schema-branch failures for one CFG target at its real candidate path. It displays the current object and allowed complete reference forms, with a mapping back to the original rows. Many alternative-type rows are not counted as independent candidate mistakes.

After prerequisite structure is valid, independent evidence-layer, target-capability, and realization-consistency problems can be reported together. Invalid prerequisite references suppress dependent cascades. The program does not add `path`, move evidence, or synthesize demands. Violations in program-generated compilation material after candidate validation are implementation failures.

The v5 correction builder preserves the stage's authority, frozen input, format, semantic rules, and applicable repair context. It removes marked generic teaching and repeated self-check sections, then adds only the current candidate, mechanical diagnostics, and relevant short examples. Strictly parseable candidates appear as compact JSON objects; invalid JSON or duplicate keys remain raw text. Presentation does not rewrite the accepted response or modify its semantics.

The shared mechanism lives in `common` and has no reverse dependency on annotation, review, or DOE. Injected services, persistent runners, loaders, and replay use the same deterministic builder. Old request chains are not migrated or interpreted under the new protocol.

## Durable request chains and identity

Each stage saves ordered `calls/<stage>/aNNN/` entries and `chain.json`. Every request binds its prompt, response, predecessor, and diagnostic identity; the chain identifies the final valid call. A new correction is a new request, not a resend of an accepted response.

`call_sha256` binds all original call-file bytes, including fields not consumed by business parsing. Failed transport receipts are bound too; a request that has not started can have no receipt digest. Resume validates and consumes accepted responses before deciding on another request. Zero-API replay reconstructs diagnostics, subsequent requests, and final selection. Propagation validates its explicit upstream annotation chain, not a hard-coded `a001` or only the final response.

Artifact comparisons use canonical JSON identity with primitive types preserved: integer `0`, floating-point `0.0`, and Boolean `false` are distinct. Entry points validate caller paths before resolution so links and junctions cannot be hidden. Repair context is reconstructed from its explicit refinement owner and fixed initial review, rather than a duplicated feedback bundle. Review findings are stored once; resolved target values are an in-memory and report view.

## Teaching and evaluation boundaries

Independent synthetic examples are tested in the actual rendered prompts. Displayed objects retain all required internal fields even when an explicitly described outer context is omitted. Source text, field combinations, and answers from 001, 010, and 013 are not teaching material. Their historical failures can be offline development regressions.

The separate [first-response screening](../doe/prompt-first-response.md) makes eight initial requests and deliberately does not correct invalid responses. That experimental stop policy does not impose a production limit. It cannot establish full correction-chain savings. Historic prompts, responses, reports, and digests remain unchanged.

Business versions and field responsibilities are documented in [field tightening](field-tightening.md). Reports distinguish structural corrections, semantic review, selected candidate, propagation, and DOE status. Successful validation, an empty review finding list, and completed computation do not prove semantic correctness, complete sensitivity annotation, or absence of DOE.
