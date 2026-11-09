# 010 independent source and DOE audit

Run: `D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-backend-r3-high-20261104-132226`.

This audit independently reads the three frozen source files, selected CFG, Task, processing and correspondence declarations, propagated Data/records, review, and DOE outputs. It uses source consistency, field identity, path correlation, receiving boundaries, and explicit limitations as criteria. It is not human gold, a dynamic Skill execution, or a proof of natural-language equivalence. The accompanying `extract_evidence.py` uses only Python standard-library JSON/file operations on saved artifacts; it imports no production code and reruns no analysis. `evidence.json` contains exact Data IDs, relevant records, and input SHA-256 values. No production or original run artifact was changed.

The finite source relationships inspected here are preserved: the request term feeds the query unchanged; each optional field is inserted only on its presence branch; the four argument combinations remain correlated with their responses; `response.total` is saved; and the same response's complete `items` value reaches the return operand. All 21 generated IR are processed, but DOE remains partial. A concrete correspondence-reference error, unexpressed prohibition/return-boundary limits, and the absence of any sensitivity declarations prevent a complete DOE conclusion.

## Source boundaries and actual recorded relationships

The source package includes `SKILL.md`, `query.yaml`, and `references/workflow.md`. Its source SHA is `66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c`. `SKILL.md:8` incorporates the workflow. The Task separately preserves ten requirements, including both optional-field omissions and the delete prohibition.

| Frozen source requirement | Selected IR and saved evidence | Scope of the finding |
| --- | --- | --- |
| Read user-supplied `request.json` (`workflow.md:5`) | `ir_001` acquires the request from storage; later projections retain `part_of` links to that request. | The actual file contents are not supplied. Its open `known_parts` descriptor is not a claim that optional fields are always present. |
| Call `index.search` exactly once, with unchanged term as query (`workflow.md:7`) | One acyclic call template at `ir_016`; its delivery has four argument alternatives. Each argument's `query` is the original request's `term` Data. | Four static alternatives are not four executed calls. The positive action demand and satisfied `at_most(1)` constraint support the modeled requirement; no real call was executed by this audit. |
| Save `response.total` to local `count.txt` (`workflow.md:21`) | `ir_018` selects `total`; `ir_019` writes precisely those selected Data to local storage. Each alternative preserves the response and branch bindings. | No request field or complete response is substituted for the saved payload. The saved record has a strong storage update under the public replace default. |
| Return `response.items` unchanged (`workflow.md:23`) | `ir_020` selects complete `items`; `ir_021` entry operand contains exactly the four corresponding items Data. | The source does not identify a receiving party/mechanism. No user/network sink is invented; the relationship is established through the return operand, not through an externally identified output boundary. |

The 21/21 figure measures completion of generated IR. It is not a 21-site source coverage score. The sink inventory is 14 `model_observe`, one `external_tool`, and one `storage_write`. Contract-derived observations are static possibilities, not extra source actions or measured model observations during Skill execution. Reading storage is an acquisition; the unspecified return does not become a user-output sink. The empty projected exit state of `ir_021` is not evidence that the returned value was erased.

## Optional fields, missing values, and response pairing

`workflow.md:10-13` and `query.yaml:1-3` require independent presence-based insertion/omission for `from_date` and `limit`. The saved object descriptors resolve to exactly these field sets:

| `from_date` present | `limit` present | Delivered argument fields |
| --- | --- | --- |
| No | No | `query` |
| No | Yes | `query`, `limit` |
| Yes | No | `query`, `from_date` |
| Yes | Yes | `query`, `from_date`, `limit` |

The evidence extractor follows only explicit, single-variant `selection`, `known_parts`, and `field_updates` descriptors. It checks each delivered field's original request `part_of` and path; matches delivery and receive by their two predecessor bindings; and confirms that the saved `total` and returned `items` select the same paired response. All four rows satisfy these checks. No absent optional field is replaced with literal null or a fabricated default.

Presence tests at `ir_005` and `ir_010` use `present(field(request, name))`, not truthiness of the optional value. The frozen expression interpreter distinguishes its `MISSING` sentinel from ordinary values, including null/false (`implementation-snapshot/src/skillflow/doe/constraint_control.py:365-397`); the frozen prompt explicitly describes that distinction. Thus the declared branch semantics preserve missing versus present-null. These are static declarations and saved candidates, not four executed concrete requests, and this audit does not claim all candidates are dynamically feasible. The accepted date format is a call requirement; `workflow.md:19` explicitly gives no pre-call validation or normalization instruction. The graph adds neither validation nor fuzzy expansion from the capability note at line 3.

The source merely says to write `count.txt`; it does not explicitly specify overwrite or append. Processing records `mode: replace`, consistent with runtime contract EM18 (`implementation-snapshot/src/skillflow/propagation/contracts/runtime_contract.py:41`). The declaration also identifies replacement as a runtime default. Explicit append would take priority if present, but this source has no append instruction. The write record's empty `before` list does not establish that an actual existing file is empty.

## Why correspondence and DOE remain partial

There is a concrete interface failure, distinct from the correctly retained optional-field dataflow. The first task-correspondence response declares R8 `retained_only` with no gap, violating the realization schema. Its one structural correction fixes that row. Validation of the corrected candidate then rejects R4 and R6 `only_if` conditions at `/realizations/3/constraints/0/condition` and `/realizations/5/constraints/0/condition`.

Those references select the compute **output** slot at compact operation paths `ir_005/segments/0/ops/0` and `ir_010/segments/0/ops/0`. The actual normalized presence expressions are attached to the compute operation's **self** slot, as saved in `annotation/audit/compiled-response.json`. The validator requires an exact expression target (`implementation-snapshot/src/skillflow/propagation/contracts/constraints.py:197-205`). This is not evidence that presence expressions were missing: the slot identities differ. With the correction allowance already used, the two realization records become explicit validation gaps. Their separately valid operation-level presence/value demands survive. No corrected run or modified declaration is substituted in this audit.

Final requirement expression status is six `expressed` (R1/R2/R3/R5/R7/R9), three `partial` (R4/R6/R10), and one `retained_only` (R8). R4's complete date-related requirement is therefore not established, including any separately required format property. R8 has no applicable demand goal or encoded prohibition constraint because no deletion event is available to select; independently, the selected graph contains no `index.delete` call. R10 retains its value/action demands but has an unresolved return-recipient boundary. The processing declaration also retains a limitation about unspecified tool deployment, transport, and failure handling; it represents the normal request/response path without inventing error continuations or network transport. These limitations must not be reported as proven source violations.

The source review completed with `findings: []` and `objections: []`; its saved availability includes Task, CFG, and assembled annotation. `diagnostic_only` remains true, and no semantic repair was used. Empty model findings do not discharge the deterministic correspondence gaps or independently certify semantic completeness.

## DOE utility and residual limits

DOE did compute useful demand support. Thirteen applicable seed goals across nine requirements have nonempty derivation references. At the tool boundary, saved demands include the search action, `query` value, and optional `from_date`/`limit` presence and values. At the write boundary, R9 has both an action demand and an exact value demand for the actual total payload; its support has no unestablished range. R10's items demand traces back to the acquisition while the recipient limitation remains. There are also conservative possible dependencies through the opaque tool response; they do not prove that request plaintext is contained in response fields. The R2 `at_most` and R9 `requires_prior` checks both report satisfied within the declared static model. These results provide auditable payload/requirement relationships despite partial global demand status.

Sensitivity declarations are empty, and every sink's `data_reviews` is empty: **zero sensitive-data comparisons were performed**. The frozen source gives no concrete request values or affirmative sensitive-data declaration that this audit can say was omitted; user-supplied/opaque data is nevertheless not certified nonsensitive. The run therefore supplies no supported DOE finding, possible-excess comparison, or no-excess comparison for a declared sensitive range. It cannot establish absence of over-exposure or sensitivity completeness.

The residual layers should remain distinct: generated propagation completed; inspected source field/response relationships are supported; two correspondence references failed; prohibition and recipient/transport limits remain; and sensitivity-based DOE comparison has an empty declared basis. This single case supports the finite structural/dataflow claims above, without a precision/recall score, a broad correctness claim, or a complete DOE claim.
