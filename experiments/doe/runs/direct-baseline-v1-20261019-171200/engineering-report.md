# Direct experiment engineering integrity

Status: **passed_with_evidence_limitations**. This audit made **0 model calls** and found **0 errors**. It contains no semantic grades.

All **120/120** fixed planned targets have exact child receipts and saved decisions: **120/120** canonical identities, **120/120** single attributed turns, **120/120** verified `gpt-6.1-sol` / `ultra`, **120/120** observed protocol conformity, and **120/120** with no observed tools. All have one observed incoming agent message. The 192 preparations comprise 120 executed targets and 72 superseded unexecuted preparations; no unplanned target decision was found.

Actual dispatcher `spawn_agent` invocation metadata, independently extracted without inspecting message values, contains **120/120** explicit `fork_turns=none` arguments. Its task IDs and call IDs match all 120 saved delivery records, and the actual call order equals the frozen effective schedule. Child source metadata names the same dispatcher parent, root session, canonical path and depth for every target. Target start timestamps are nondecreasing in that order.

The exact child `session_meta` **omits** `forked_from_id` in **120** receipts; **0** explicitly contain null and **0** have a non-null value. Absence is not proof of fresh history and is not an observed violation. The original six-trial partial audit was preserved byte-for-byte as `isolation-audit.initial.json` (SHA-256 `d5139c9613e1fc68ee25b974a0c4a1a2644f1eeae95c44571bea7a0b5189b6c4`). The replacement records field presence explicitly for all targets.

The final existing-helper replay passed: **15 cases, 192 registrations, 4 reference byte hashes, 120 exact receipt replays, 0 errors, 0 model calls**. It checked source bytes, rendered source bundles, requests, manifests, template/shared/original-answer inputs, rendered prompts, final output hashes, all 36 review-parent links and saved receipt decisions. Original catalog sources and all three pilot source packages match frozen input hashes. Original and revised prompt seals, the revised schedule's original-schedule seal, final reusable templates, and the evaluator/common-assignment seal also match.

The new corpus offline verifier (`python -m tools.doe.direct_corpus verify`, exit 0) verified **12 cases and 51 files**, with catalog SHA-256 `ab2e2d17843cd118e1081a6bf6dccb130d10bab9ddbe1ef2456436d517789b9d`. Saved dispatcher completion/checkpoint/replay records agree with the independent audit. The final corpus and replay checks use no model calls.

There are **120 distinct response IDs**, one per target, no cross-trial reuse, no conflicts, and no missing core usage. Core usage is **3,984,744 input + 575,382 output = 4,560,126 total tokens**. Cached input is 3,403,264, cache-write input is 0, and reasoning output is 224,406; these subsets are not added again. Target totals exclude orchestration, references, scoring, and engineering review. No currency amount is inferred.

Assessment protocol bytes match their final seal: evaluator SHA-256 `bef642a2f45b7b2d34ef3bc6955b5326ba1bce2007d90fec58c038a40397e584`; common assignment SHA-256 `6c82d432acb4bf6cda1094603b4d4dfcd5a92e692345f5677dac18f21bf3d19d`. Only bytes were hashed; no assessment or reference contents were reviewed.

Execution commands and their exact results, every hash comparison, tooling hashes, all checks and errors are preserved in `execution-integrity.json`. Python is 3.12.3. The first audit invocation returned exit 1 because it incorrectly compared reusable prompt exports with uninlined arm templates. The export manifest identifies shared rules as inlined; corrected checks validate manifest hashes and exact deterministic substitution. No frozen artifact changed. The final invocation used `--reuse-final-replay` to retain the already-passed final 120-receipt replay without repeating it. Focused unit tests were not repeated: the parent retains the existing 26-test exit-0 result, and no implementation change was made.

Evidence limits:

- Tools were forbidden by protocol and no target tool use was observed; no hard sandbox disabled tools or access to project/runtime instructions.
- forked_from_id field absence is not explicit null and does not prove that no history could have been inherited. Actual dispatcher spawn calls explicitly requested fork_turns=none; canonical child identity and one attributed target turn are verified separately.
- Each target has exactly one observed incoming agent message, but collaboration payloads are encrypted in receipt evidence. Exact plaintext prompt delivery equality and the absence of extra material inside that payload cannot be independently proven.
- Saved prompt/source/reference/review-parent hashes and zero-model replay verify preserved bytes and deterministic bookkeeping; they are not semantic proof or model-generation reproducibility.
- Target usage excludes root orchestration, reference authoring, scoring, and this engineering audit. Cached and reasoning fields are subsets, not extra token charges. No monetary amount is inferred.
- No semantic assessments or reference contents were read for this audit; target answers were processed only internally by the existing deterministic verifier and compared by hashes, without inspection or export.

Artifacts: [machine-readable integrity](execution-integrity.json), [all120 allowlisted metadata](isolation-audit.json), [preserved initial audit](isolation-audit.initial.json), [audit script](execution-integrity-audit.py).
