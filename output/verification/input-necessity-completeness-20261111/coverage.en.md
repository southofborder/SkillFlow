# Corrective offline acceptance coverage

These are injected semantic fixtures and deterministic regressions, not new real-model runs or a semantic accuracy benchmark. Earlier failures remain archived. The original real batch is preserved under its measured identity.

| Obligation | Primary regression modules |
| --- | --- |
| `a.a`, `b.b`, `c.c`: remove unused c, retain actual reads/observations | `tests/doe/test_reviewed_input_necessity.py`, `test_input_contract_preservation.py` |
| Field complement, whole input, nonsensitive input; concrete distinct edit types | `test_reviewed_input_necessity.py`, `test_input_locations.py`, `test_input_necessity_additional_acceptance.py` |
| Exact output selectors, union, no whole-output-to-subfield substitution | `test_reviewed_input_necessity.py`, `test_input_necessity_scoped_backend.py` |
| Conditions, cardinality, presence, member/receiver pairing and other consumers | `test_reviewed_input_necessity.py`, `test_input_necessity_additional_acceptance.py`, `test_case_member_integration.py`, existing demand/endpoint tests |
| Required interface fields, optional presence, extra fields, whole values, no automatic action seed | `test_input_contract_preservation.py`, `test_input_necessity_review_regressions.py`, `tests/document_guided/test_input_requirement_contracts.py` |
| Whole missing attachments, zero-input boundaries and exact expression exemption | `tests/document_guided/test_input_contract_completeness.py`, `tests/doe/test_input_contract_scopes.py` |
| Independently accepted required/uncertain/remainder ranges; finite exhaustive review partition | `test_input_contract_scopes.py`, `test_input_necessity_scoped_backend.py` |
| Rejected structural claim cannot certify forward independence; accepted uncertainty keeps its information bound | `test_input_necessity_scoped_backend.py`, `test_demand_results.py` |
| A local gap does not block independent same-sink sensitive information | `test_input_necessity_scoped_sensitivity.py` |
| Concrete gap missing/resolution/evidence; generic gap rejection and stale receipt rejection | `test_input_contract_review.py`, `test_input_contract_scopes.py`, `tests/document_guided/test_input_requirement_contracts.py` |
| Source wrong/missing field and absent whole argument; no invented values or seeds | `test_source_input_findings.py`, `test_input_locations.py` |
| Raw/wire/CFG/source edit locations, generated observations, conditional input offsets, literal/resource metadata use | `test_input_locations.py` |
| Exact paired acquisition capability and independent review, no arbitrary union or descendant inference | `test_input_contract_scopes.py`, `test_input_locations.py` |
| Deletion constraint preservation shares the same contract | `test_input_contract_preservation.py`, `test_input_necessity_scoped_backend.py`, existing constraint tests |
| FIFO/LIFO, receipt identity, seven injected responses, shared repair, saved and zero-call fixture replay | `test_reviewed_input_necessity.py`, `test_input_necessity_scoped_backend.py`, `tests/document_guided/test_input_contract_review_flow.py`, `tests/document_guided/test_parallel_runner.py`, existing guided/formal lifecycle tests |
| Reuse the detached CFG for receipt checks and edit locations; preserve public copy isolation | `test_component_snapshot_reuse.py` |

All listed `test_*.py` names without another prefix are under `tests/doe/`. Tests using saved synthetic responses do not replay a historical real experiment. They do not execute the analyzed Skills. A concrete source audit remains necessary to assess real model-produced contracts; the original four-case audit found one failed and three partial results.

The [main example](main-example.json) preserves all three actual modeled input slots,
requires only slots 0 and 1, and reports slot 2 removable with its concrete
location. Forward-record hashes before and after demand analysis are identical.
These are static records and injected semantic judgments, not runtime measurements.
