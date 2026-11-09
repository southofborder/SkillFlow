# GA4 v8 online verification: read-only protocol review

Reviewed on 2026-11-01 (Asia/Shanghai). This review did not dispatch a model, probe, Skill, replay or controller and did not change production code, prompts or historical artifacts. Root remains the sole generation owner.

## Implementation identity

The current implementation identity is `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. Relative to the completed offline acceptance identity `fa02488dc9d01435b747284e0fa8f27ef9f1bea834e07cb6ade83230fc325a5b`, the only changed provenance file is `src/skillflow/graph/audit/prompts.py`.

That change supplies a nonempty suggestion example and explicit requirements in the standalone source/controlled-text audit contract. The current guided runner builds its CFG with `build_compact_graph_prompt` and reviews source with `document_guided.source_review.build_source_review_prompt`. The guided normal and repair routes do not call the changed standalone prompt. The graph controlled-text renderer is still used for deterministic certificates; rendering is not a separate model audit request.

This difference does not present a launch blocker found in this review. Record the current identity; do not relabel the offline acceptance identity or claim that the new full-source run was already covered by injected-answer tests.

## Current transport and workflow

- `analysis_config` retains the exact model `gpt-6.1-sol` and permits the saved `high` effort. `Client.command` sends that saved effort and the `openai` provider. Request configuration is evidence of the requested runtime, not independent proof of the provider's actual backend model.
- The complete-input guard checks `ENVELOPE + prompt` against 1,048,576 Unicode codepoints before process launch. This is a CLI input limit, not a measured model context window.
- Each attempt has its own empty working directory. User configuration/rules are ignored, project document bytes are zero, and the envelope forbids tools and delegation. The sandbox is read-only; the envelope is not equivalent to proof that tool invocations were impossible. After closure, inspect public event types for actual tool activity without reading hidden reasoning.
- Completed substantive answers are retained and reused. A differing completed last-message or second substantive final is rejected as ambiguous rather than sampled again. Missing usage does not reject an answer.
- A replacement attempt is permitted only after the previous CLI exit is confirmed, no complete answer exists, and public errors identify an eligible transient failure. At most two extra attempts are available. A forcibly timed-out process is retained as a timeout; it is not silently restarted by the current client.
- The guided runner retains seven normal semantic requests, two workers, one structural correction per stage and one shared semantic repair round. Its independent source-review path can inspect partial material. The program assembles annotation.
- Guided `replay` calls the same runner with `replay=True` and no client factory. The source-review replay rejects live clients. Current DOE failure replay recomputes the original failure without publishing a successful manifest.

## Controller-template review

The closed v7 controller is suitable as a small observation/replay template, not as a controller to resume. It records analysis elapsed time separately, calls passive `transport_metrics`, performs one offline replay and compares native-start marker counts. An exclusive-create `controller-started.json` prevents a second invocation from dispatching under the same controller file.

The template catches a controller-level exception and may leave `outcome=None`, in which case it skips replay. Most current guided stage failures are already returned as a durable failed result. If a controller exception does occur, inspect the saved result and error before deciding whether an offline replay is meaningful; do not automatically rerun or resume targets.

Archive and hash the transport/metrics/controller files separately. `implementation_provenance()` covers maintained Python under `src/skillflow` and formal source/configuration, not `tools/doe` or the per-run controller. A final unchanged check should cover both sets.

## Accounting and report limits

Use passive `transport_metrics` after closure and verify against actual public artifacts. It distinguishes attempted launches from confirmed native starts, correlates public completion usage with an accepted substantive final, deduplicates strong response IDs globally and local IDs by thread, and keeps partial/unknown usage separate. Cached input and reasoning output are subsets, not extra totals. HTTP attempts and monetary cost remain unknown unless independently supplied.

No accuracy result is established by this prelaunch protocol review. Full-source coverage, source correctness, remaining findings, DOE usefulness and actual costs must be assessed from the new closed run. A successful replay establishes repeatability of the saved deterministic decisions, not natural-language correctness.
