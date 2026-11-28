# Accepted review merge and shared repair routing

Snapshot of the sole `document-guided-ga4-runtime-locality-high-20261117-205158` run after its initial review correction, while shared repair is in progress. This is a passive saved-byte audit; no stages, validators, backend, tests, replay, models or Skills were executed, and no frozen/run files were edited.

The saved a002 validation is **valid**, and its response chain selects a002. It returned **21 complete existing-check replacements and zero insertions**, within the 25 permitted record slots. Applying only those replacements to the saved a001 object exactly reproduces `merged-candidate.json` and its validation hash. The 507 other checks are unchanged; all 19 original findings are unchanged, including the four that the correction was permitted to edit. Obligation order and identities are preserved. This is a successful targeted merge, not an unverified whole-answer reconstruction.

The merged initial review contains **528 checks / 1735 scopes**:

- Checks: 503 accepted, 25 rejected, zero unresolved. Two previously accepted checks became rejected; the 23 prior rejected summaries remain rejected.
- Scopes: 1625 accepted and 110 rejected. Compared with a001's authored decisions, 80 accepted scopes became rejected and 2 rejected scopes became accepted; 1623 accepted and 30 rejected scopes stayed in their prior states.
- The saved review status is `complete`, with `diagnostic_only: true`. Strict schema, reference, scope coverage and conflict acceptance does not independently prove that every source interpretation is correct. It also does not mean the original CFG/annotation passed semantic review.

The review result has **44 routed findings**: the 19 unchanged model-authored findings plus one program-generated processing finding for each of the 25 rejected contract checks. These are not 25 extra findings invented by the correction response. Routing is Task 3, CFG 6, processing 32, task-correspondence 2 and sensitivity 1. There are no authored acquisition-projection checks or typed source-input findings; this does not establish absence of source input errors.

`audit/shared-repair-decision.json` is bound to this complete review and the source hash. It admits the existing **one shared repair round**, mode `reviewed_bundle`, for `annotation`, `cfg` and `task`, with no admission barriers. The initial Task/489-IR CFG/annotation remain selected at this snapshot. No revised artifact is claimed selected or correct yet.

The actual prepared Task revision contains only the exact previous Task and three source-based objections; it receives no CFG or annotation in that request object. The graph revision feedback contains exactly the six CFG findings and the previous 489-IR graph. Existing flow is reused. Frozen runner dependencies require Task and graph repair, then processing against the revised graph; task-correspondence requires revised Task and processing, and sensitivity requires processing. Assembly and a newly bound source re-review follow. The initial review's accepted scopes cannot be transferred to changed contracts without that new review. Current Task/graph execution is only the beginning of this closure.

a002 returned 34,563 model-text characters, stored in a 36,859-byte JSON container. Its public call timestamps span 394.804739 seconds; this is an observable call interval, not pure generation or proof that this approach is generally faster. Full-source/contract preservation and the 926,055-character correction core input were established separately by `source-review-a001-correction-audit.json`; this merge audit confirms the actual selected response and retained records.

Evidence: `source-review-merge-repair-audit.json`, SHA256 `49d9c097d71b6e6d19fc59e0579d6f9e95d9ecceeeb1c22a91b45e041e6f69db`. All 18 passive identity/comparison checks passed. These checks compare saved JSON and hashes; they do not rerun semantic validation. Further correctness, source-boundary coverage and deletion conclusions await the completed revision/re-review/backend outputs.
