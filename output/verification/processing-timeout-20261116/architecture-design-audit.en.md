# Processing revision timeout: architecture and general design audit

This is a read-only design audit of the closed run `document-guided-ga4-source-review-locality-high-20261113-203902` and baseline implementation `ae3df129739a9471521b8b19be65faa8e085f1e92efcacaac1e0c5e3d42f3cbb`. It does not replay the run, execute a Skill, validate historical candidates, run a backend, or call a model. Network/timing attribution belongs to the separate transport evidence audit. No duration in this report is represented as measured generation-only time.

## Findings

The current revision path deliberately rebuilds the dependency closure. A CFG finding invalidates graph, processing, task correspondence and sensitivity; a processing change invalidates correspondence and sensitivity. Processing sees source, the current CFG, the flow document and the runtime contract. It receives neither Task nor sensitivity. In a semantic repair it additionally receives the complete prior processing fragment and source-review objections, then must submit a complete replacement for the current CFG. These are appropriate semantic boundaries. See `src/skillflow/document_guided/runner.py`, `phase`, and `src/skillflow/document_guided/prompts.py`, `build_fragment_prompt`.

The previous run changed the CFG from 679 to 770 IR. Instruction identifiers are generated coordinates, not durable semantic identities; even the initial structural graph correction rewrote many records. Therefore retaining processing by matching `ir_N`, labels, nearby source spans or equal arguments would be unsound. A revision must still account explicitly for every current instruction. A source span alone does not bind operand versions, control conditions, member scope, request/response pairing, resource locations or evidence inheritance. Adding a new cross-version semantic matcher would be a larger, riskier mechanism than the present timeout requires.

The failed revision prompt grew because it included a larger current CFG and the prior fragment plus repair findings, not because source text grew. Read-only string and JSON parsing produced:

| Material | Initial processing a001 | Revision processing a001 | Difference |
| --- | ---: | ---: | ---: |
| Complete prompt characters | 539,754 | 810,707 | +270,953 |
| Previous-work section | 305,571 | 575,705 | +270,134 |
| Related-source section | 180,842 | 180,842 | 0 |
| Output format/guidance section | 52,644 | 53,463 | +819 |
| CFG JSON within previous work | 268,284 | 298,744 | +30,460 |
| Repair-context JSON | absent | 239,277 | +239,277 |

The source sections have identical SHA-256 `dab07c12957c05f40a49142fa474d780cf087e4a7fd2e8d05a32038461ba872f`. The extra output-format characters are principally the longer explicit required-IR list. A complete repair context is useful: it keeps the earlier interpretation and every objection available. Truncation is unnecessary and would lose evidence.

The existing source-review display already demonstrates a strict exact-JSON-sharing mechanism, but `build_fragment_prompt` presently concatenates plain CFG/runtime/prior-fragment JSON and `ProcessingFragment` output has no equivalent shared-value envelope. The response already permits omitted defaults and evidence inheritance; merely asking for shorter prose is less reliable and risks reducing necessary justification.

Completed processing responses contain substantial exact repetition. The a002 complete response contains 263 identical output-binding arrays, 372 identical input-zero references, 203 identical EM16-only IR records and 13 identical full optional-save IR records. These counts overlap and cannot be added as separate savings.

An independent stdlib-only illustrative exact-subtree encoder, including definitions and an explicit envelope, establishes the following net character opportunity. It verifies exact serialized roundtrip, including dictionary order, before reporting a number:

| Logical material | Plain JSON characters | Exact shared encoding characters | Reduction |
| --- | ---: | ---: | ---: |
| Initial previous-material JSON | 305,620 | 275,593 | 9.825% |
| Revision previous-material JSON | 575,375 | 483,066 | 16.043% |
| Processing a001 full response, 630 modeled IR | 222,118 | 170,688 | 23.154% |
| Processing a002 full response, 677 modeled IR | 243,712 | 176,029 | 27.772% |
| Selected processing, 633 modeled IR | 228,473 | 170,150 | 25.527% |

These are retrospective character-size measurements on saved content, not a model experiment, token count, speed forecast or proof that the model will author the smallest encoding. There is no revision-processing response to measure. Unique source-specific reasoning, contracts and evidence still require generation; compression cannot guarantee completion during a network interruption.

## Recommended implementation boundary

1. Generalize lossless shared structured-input presentation for semantic fragments and their corrections. Share exact JSON values across the permitted upstream material, including repair context. Keep full source separately unchanged, every CFG instruction, every actual input, every contract and every objection. Expansion must reproduce the same logical material; no optional/unknown field may disappear. Preserve Task ownership: the processing payload must not gain Task, correspondence or sensitivity fields. Measure the full delivered prompt, including format instructions and adapter envelope.

2. Offer a self-contained model-authored exact-value response envelope for processing, with plain full responses remaining valid. Each explicit current IR still appears in the logical `ir_semantics` mapping and expands to a complete record. Shared values are literal serialization reuse, never shared data identity, semantic inference, automatic copying of old processing, or an implicit merge against a previous revision. Do not add parameter substitution, default templates inferred from CFG, pointer references to old artifacts, expressions evaluated during expansion or omitted-record inheritance. Every claim is still authored for its actual current occurrence.

3. Expand the envelope before the existing schema, coverage, reference, evidence, input-contract and operation validators. Save the raw provider response unchanged and bind the expanded logical candidate separately. Diagnostic JSON pointers, structural record replacement, `chain.last_candidate`, salvage and final annotation mappings must all address the expanded logical tree. Preserve all existing semantic rejection and local-isolation behavior. In particular a malformed envelope must be structural failure, not a source-supported unmodeled claim. Correction must use the existing one-correction budget, and a replacement response must not be silently treated as a full semantic revision.

4. Validate representation integrity: exact envelope keys/version, defined references, no cycles, valid marker escaping, no duplicate object keys, no conflicting keys, no invalid unused definitions, and bounded expansion/depth. Keep number/string/null distinctions, omission versus explicit null, order, and every occurrence. Definition reuse must copy values so a later mutation cannot alias independent operations. Resource-limit rejection is an explicit representational failure; it cannot drop a subtree. New prompt/wire/selection identities should distinguish future products without migrating old artifacts.

5. Add narrow shared-repair request-failure containment. It is a separate availability improvement, not a latency claim. A confirmed-ended `ModelRequestFailure` during the repair may retain an already assembled original bundle and its exact bound original source review, while reporting the repair as unconfirmed and preserving every original objection. A new Task or CFG from the failed repair must never replace one member of that original bundle. There is no usable revised annotation to review or select. The original candidate remains diagnostic/partial according to its actual evidence. No failed revision claim is accepted.

The existing source-review request-failure handling gives the relevant narrow type boundary: `ModelRequestFailure`, or the corresponding saved-call wrapper during a zero-call replay, and only when recording integrity is intact. Do not catch arbitrary exceptions, integrity errors, unknown process states or user interruption. Initial processing failure still fails because no original complete annotation exists. The generic phase error path currently sets the shared stopping event and rethrows, bypassing the existing inconsistent-revision fallback and all backend analysis. A repair-only contained failure must not accidentally leave that cancellation set for otherwise authorized retained-original analysis; a genuine user stop must continue to stop all work.

Normal semantic requests remain seven; the scheduler remains two workers. Keep current timeouts, native/outer retries, one structural correction per stage and one shared repair round. Do not split processing into hidden model requests, lengthen its deadline, add an automatic second repair, reconnect by launching another controller, or discard the complete source/contract inventory.

## Focused offline acceptance requirements

- Plain and shared complete responses must produce identical logical values, compiled records, demand contracts and evidence coordinates. Cover source strings and literal marker-like objects, ordering, omitted fields versus null, numeric types and repeated independent occurrences.
- Reject undefined/cyclic references, malformed/extra envelope fields, invalid unused definitions, duplicate keys and expansion-limit excess. No such rejection may bypass correction limits or become a semantic fact.
- Exercise current logical-IR coverage after a CFG change. An old IR with the same label but changed inputs must still be checked as current; no implicit prior record may fill a missing current record.
- Exercise invalid shared-response records through existing record correction and salvage. Diagnostics and replacement targets must remain logical coordinates; raw records and logical candidates must both be reproducibly bound.
- Preserve full source and repair context by exact expansion comparison, and assert processing/Task isolation. Measure both raw and delivered input sizes rather than merely the packed body.
- Inject an initial request failure and a repair-only confirmed request failure separately. The first must fail; the second can continue only with the complete original selected bundle, its original bound review, unchanged findings, explicit failed-stage provenance and no synthetic revision value. Integrity failure, unknown process state and user stop must remain fatal/interrupted.
- Validate the same decisions in a fresh offline injected seven-request integration and the permitted failure/replay path. Existing semantic review locality and all-input assessment regressions remain required; no historical run is recomputed for acceptance.

## Scope of the fresh online conclusion

The next authorized run should report actual raw/encoded/expanded sizes, complete and failed request durations, visible reconnect evidence, available usage, corrected/selected artifact identities and backend coverage. If the revised processing still times out, distinguish whether it emitted a complete usable response, and whether original-bundle continuation produced only partial findings. Retrospective compression ratios must not be reported as realized token savings or eliminated network cost. A later modification plan should respond to those observations; this audit alone does not justify another budget increase or model call.

Supporting artifacts: `design-size-evidence.json` and `design_size_audit.py` in this directory. The script imports only Python standard-library modules, reads the closed run, writes this new audit directory, and performs no production calls.
