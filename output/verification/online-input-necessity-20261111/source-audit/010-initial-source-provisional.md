# 010 initial source and contract audit

Status: **PROVISIONAL; initial processing is available, source review is not assessed.** Captured 2026-11-11T20:25:10.648354+08:00.

The Task has 10 requirements and no issues. The CFG has 20 instructions, 8 blocks and 9 edges. Processing models all 20 IR with no processing gaps. There is one search call carrying one input contract; two computes use exact presence expressions, with no opaque compute requiring a demand_transfer.

All three source files match the prewritten inventory. The nine finite expectations are represented: one search, unchanged term, presence-based optional values, no fuzzy/validation/delete operation, a total-only local write and an unchanged whole items return. Static enumeration finds four normal graph paths, each with one search, one write and one return. This is representation, not actual execution or propagation.

## Interface contract

The call contract accounts for its one actual payload input: query value is required; from_date and limit values are required only if present; the remainder is independently unnecessary under the supplied interface. The parameter presence tests precede value selection and merging, so absence is not replaced by a default or null. The contract cites the workflow and query.yaml.

The call input index is 0 in the processing operation and corresponds to CFG ir_015 input 1, the named-argument object. The tool itself is the CFG input 0 boundary. The captured contract has not yet been independently accepted or exercised by deterministic demand.

## Source comparison

- **010-source-closure**: All three source documents are incorporated; query.yaml controls omission of optional arguments on the same call.
- **010-search-action**: The term field is selected unchanged into query and all optional branches merge before the single search.
- **010-from-date**: The expression checks field presence, not truthiness. A present value is selected unchanged; absence retains the unaugmented argument object. The tool contract uses value/from_date with if_present=true.
- **010-limit**: The expression checks field presence, with unchanged supplied value and omission when absent. The tool contract uses value/limit with if_present=true.
- **010-no-expansion**: No fuzzy expansion, normalization, date parsing, limit clamping or pre-call validation operation appears.
- **010-delete-ban**: The prohibition remains a Task requirement and graph constraint; no actual delete operation is introduced.
- **010-total-output**: The file write receives only response.total and has no fabricated returned file value.
- **010-items-output**: The complete items field is selected unchanged; no item-member narrowing or replacement summary appears.
- **010-input-union**: Actual whole request/response acquisition remains distinct from the selected fields. The shared request needs term plus optional presence/values; the response output union is total and whole items. Task mapping, review and deterministic demand must still verify the actual union.

## Remaining limits

Task-correspondence, sensitivity, source review and backend records are outside this provisional capture. Exact seeds must require total for the file and the complete items value for return; optional inputs must preserve presence and supplied value. No individual item fields can be dropped from an unchanged items requirement. Unknown request/response sibling names must not be invented.

The source supplies no actual request.json values and no retrieval field-selection interface. No concrete missing-input error or server projection capability follows from this audit. No mismatch was found within the finite captured comparison, but this is not an accuracy, complete semantic, propagation, minimality or DOE claim.

The JSON companion preserves source identities, exact instruction and expression pointers, all four normal graph paths, the full initial tool contract and artifact hashes. Initial audits remain immutable if selection later changes. No observation was fed back to the running pipeline.
