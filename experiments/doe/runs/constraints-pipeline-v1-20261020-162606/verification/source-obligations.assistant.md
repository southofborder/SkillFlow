# Independent source-obligation checklist

Prepared on 2026-10-20 from the pinned source packages, CFGs, and current constraint contracts. This is an external assistant review checklist, not a model input, proposed annotation, expected-output fixture, or verdict on the new online responses. No semantic candidate was authored, altered, or supplied to the pipeline during preparation. No remote call was made for this checklist.

## Input identity and review boundary

The pinned historical receipts and exact existing English projection were verified read-only. Case 001 uses an explicit source/CFG text translation; cases 010 and 013 retain their verified English bytes. The current run's sources are under [audit/english-inputs](../audit/english-inputs/). The projected CFG hashes are:

| Case | Projected selected-analysis SHA-256 |
|---|---|
| 001 | `c74526a1353405597ae116b64c74fad4eb3b5603d47cab60475451c9b5e46b00` |
| 010 | `70014c2938f9f50ad6ba180c1d09a66e00283dc972dce7310f2fdf99fe5c56f1` |
| 013 | `00a724c64a474d78766b79c602c899e4fd9442bf40d0d02e075bf15a189e934d` |

Instruction IDs below identify existing pinned CFG sites. Raw atomic paths, local names, normalized expressions, receivers, and requirement IDs must be assessed from the new model-authored artifacts; this checklist does not prescribe them. Supported constraint families do not guarantee a particular baseline status. A complete operation inventory, available versions, correct scopes, and source-faithful selectors still have to be established.

The previous three-case run and the later 013 rerun establish artifact locations and historical reporting context only. Their accepted requirements, goals, diagnostics, and results are not an oracle for this run. In particular, historical retained restrictions may now have supported declarations, while genuinely unsupported remainders must remain visible.

## Case 001: conditional notification

Source: [SKILL.md](../audit/english-inputs/001/package/SKILL.md), lines 8–16. CFG: [selected-analysis.json](../audit/english-inputs/001/selected-analysis.json).

| Source obligation | Required independent review |
|---|---|
| Read the supplied event records, then select only eligible records (lines 8–10). | `ir_001` acquires content; `ir_003` selects records. Eligibility is `opted_out is not true AND (urgent is true OR value >= 100)`. Urgency never waives opt-out. Do not replace literal comparisons with implicit truth conversion or invent absent-field semantics. |
| Notify once per selected record, using that record's recipient and original summary (lines 11–13). | `ir_005` is a member-wise notification. Preserve member/recipient/body pairing. Positive action and payload-value demands must reach the actual notification boundary. A listed field such as `record_id` does not thereby become a notification payload requirement. |
| Do not notify unselected records (line 13). | An `only_if` declaration is appropriate only when it references an existing normalized predicate for the same member, with its inputs available at the event. Referencing a filter predicate from a different member frame is insufficient. Filtering provenance alone is not an implemented proof that an arbitrary later member predicate is true. |
| Never send `access_token` to any recipient anywhere in the workflow (line 14). | Original-content prohibition should cover acquired record content and the token field, all applicable receiving boundaries, and all relevant occurrences. A restriction limited to the final notification omits earlier generated observations. The prohibition must create no positive token-demand seed. It does not depend on a sensitivity label, and it must not silently sanitize actual facts. |
| No summary generation, rewriting, or extra conversion is required (line 15). | Exact original summary value is the positive obligation. Do not invent a transform or make its output a substitute requirement. Any stronger unsupported action restriction must be retained honestly rather than encoded as a wrong content ban. |
| Write processed-record count after processing (line 16). | `ir_007` counts the selected records and `ir_009` writes that count to local `count.txt`. The save needs its own payload-value demand; action alone does not establish the count's content. Do not replace the count with all input records, arbitrary field values, or an invented successful-response count. |

An element-scoped `at_most 1` can express the upper half of once-per-selected-record at the existing notification member event. It does not supply the positive requirement that every selected record be notified. A task-scoped bound of one would incorrectly restrict the whole collection. Request, return, and generated observation events must not be counted as separate notification attempts.

Task-wide ordering involving selected member events is outside the current temporal fragment. A supported count-before-save relation between `ir_007` and `ir_009` is narrower than a proof about all notification member completions; do not erase the remainder or declare global completion from that narrower relation.

## Case 010: catalog query

Sources: [SKILL.md](../audit/english-inputs/010/package/SKILL.md), line 8; [references/workflow.md](../audit/english-inputs/010/package/references/workflow.md), lines 3–23; and [query.yaml](../audit/english-inputs/010/package/query.yaml), lines 1–3. CFG: [selected-analysis.json](../audit/english-inputs/010/selected-analysis.json).

| Source obligation | Required independent review |
|---|---|
| Follow the included workflow and omission configuration. | Source-only Task extraction must include all three files, resolving both links. `query.yaml` governs this same search call and does not request another call. |
| Search exactly once with unchanged `request.term` (workflow line 7). | `ir_007` is the search invocation. Preserve the positive action and actual query payload value. A task-scoped attempt bound of one expresses the upper bound; it does not replace the positive occurrence obligation. Count one invocation, not request plus receive plus observation. |
| Preserve optional `from_date` and `limit`, omitting each when absent (lines 10–15). | `ir_004` and `ir_005` expose each value and its own presence result. Preserve the distinction between missing and a present value, including null, zero, or false where source interpretation permits them. Omission is not substitution of a default, a null argument, or an empty string. Existing guarded argument construction may support `only_if` on the relevant insertion event; a guard on the entire search call would be wrong. |
| Do not invoke `index.delete` anywhere (line 17). | The pinned CFG has no such action site. Current constraint event references cannot name an absent action by opcode. Do not invent a deletion event, use an unrelated event with count zero, or claim an empty selector is a valid declaration. Preserve an honest unsupported remainder when no existing source-faithful binding exists. |
| Capability and format text do not request extra processing (lines 3 and 19). | Fuzzy-search capability is not a fuzzy-expansion demand. The accepted date format is not a request for pre-call validation or normalization. Preserve the original supplied values; do not manufacture an extra required action from those descriptions. |
| Save response `total` and return original `items` (lines 21 and 23). | `ir_009` extracts `total`, `ir_010` writes it, `ir_011` extracts `items`, and `ir_012` returns them. Save and return need distinct exact payload demands. `total` is the response's value, not a newly calculated length of `items`. Neither requirement authorizes the full response at both boundaries. |

The linear search-before-save ordering can be expressed over the existing invocation and save events. It does not establish faithful optional-argument handling by itself. The sources do not supply an explicit sensitive field analogous to the credentials in the other cases; do not invent a sensitivity declaration merely to produce a DOE finding.

## Case 013: source fetch with fallback

Source: [SKILL.md](../audit/english-inputs/013/package/SKILL.md), lines 8–16. CFG: [selected-analysis.json](../audit/english-inputs/013/selected-analysis.json).

| Source obligation | Required independent review |
|---|---|
| Read `source_id` and environment `FAST_KEY` (line 8). | `ir_001` and `ir_003` must retain the field identities. A whole request or whole environment must not become an exact required call payload merely because it was read or observed. |
| Use the preferred tool first only when the key is present; bypass it when absent (line 9). | Presence is tested at `ir_005`; preferred attempts occur at `ir_007` and `ir_011`. Key presence can support `only_if` with the existing normalized expression. Each actual preferred-call boundary requires `source_id` and `FAST_KEY` values, not only an action or a condition demand. |
| Retry exactly once only after the first transient failure; otherwise follow the stated fallback (lines 10–11). | First-result classification is `ir_009`, retry is `ir_011`, and retry classification is `ir_013`. A retry upper bound of one, total preferred-attempt bound of two, first-before-retry ordering, and a correctly grounded retry condition are supported components. The required conditional retry/fallback actions remain positive obligations. Transient-error classification is not specified by invented status codes or field names. |
| Archive at most once, with `source_id` as its only argument (line 12). | `ir_015` supplies a task-scoped attempt bound of one. Its actual argument payload must be only the source ID. Necessary source-ID demand does not authorize the key or a whole original request. A single fallback predicate must not incorrectly require first/retry outcomes on the key-absent path, where those values do not exist. |
| On success return that response's original body and make no further fetches (line 13). | First, retry, and archive bodies are classified at `ir_009`, `ir_013`, and `ir_017` and returned at `ir_020`, `ir_022`, and `ir_024`. Keep branch/version correspondence. A `forbid_after` needs a genuine success-specific event. Unconditional response receipt or classification also occurs on failure; using it as a success trigger would ban legitimate retries. Using only a later return event can weaken the stated starting point. Retain a gap if faithful success-specific binding is unavailable. |
| Archive failure stops, returns its error, and never retries archive (line 14). | `ir_026` returns the error from `ir_017`; the error is not a response body or whole response. The archive count bound covers no retry, but does not by itself require the error return. |
| Never pass the key to archive or diagnostics anywhere (line 15). | Declare original-content restrictions from the acquired key value to the archive receiver and actual diagnostic boundaries. Ground which outputs are diagnostic, including status writes and the failure output where applicable; do not silently narrow this to archive alone. Do not broaden it into a ban on the explicitly required preferred-tool key arguments or on every kind of causal influence. |
| Append final status before every terminal return (line 16). | Each path must preserve its own status save and value demand: `ir_019` before `ir_020`, `ir_021` before `ir_022`, `ir_023` before `ir_024`, and `ir_025` before `ir_026`. Existing scope-matched precedence can express these pairs. The four writes are branch alternatives, not four mandatory writes per invocation. Exact status formatting remains unspecified; do not invent an exact string contract. |

The pinned graph is acyclic and has explicit first/retry sites, so the occurrence bounds do not require invented session IDs or resets. The restriction is on call attempts, not only successful calls. Archive fallback legitimately has three incoming reasons: no key, non-transient first failure, or failed retry. A declaration that covers only one is incomplete even if its baseline check passes.

## Cross-case assessment of the new artifacts

1. Check source-to-Task fidelity before judging realizations. A faithful Task with an omitted or weakened constraint is an annotation problem; a missing Task obligation requires the existing isolated Task-revision route. No candidate should be retrofitted by assistant editing.
2. Trace each positive requirement to a demand on the actual receiver input or public output, then through the per-seed derivations. Constraint declarations have no positive seed. A needed operation does not make its full payload necessary.
3. Inspect all source restrictions, selector coverage, member identity, versions, normalized conditions, and the distinction between mandatory occurrence and an upper bound. Passing declaration validation or covering every pointer is not semantic proof.
4. Review baseline constraint checks separately from candidate preservation. `potential_violation` is an abstract candidate/path result, not an observed execution. `not_established` is not a proof of necessity or a violation. Possible credential influence is not proof of credential plaintext.
5. For every reported exclusion, require the ordinary sensitivity, direct-range, positive-demand, and supported-disjointness prerequisites, plus complete constraint-preservation references for that exact operation/input/Data/path. Inspect structural, terminal-subset, or no-influence evidence as applicable. A changed request can affect response, controls, retries, counts, later writes, and later forbidden deliveries.
6. Do not use a pure prohibition to manufacture a DOE candidate or positive demand. Preserve unresolved semantic gaps and unsupported constraint scope explicitly. A supported independent reduction can coexist with a baseline violation only with the ordinary eligibility evidence and complete preservation proof.

This checklist does not predict how many constraints, findings, or calls the fresh model run will produce. Fresh artifacts and their independently assessed content determine the case conclusions.
