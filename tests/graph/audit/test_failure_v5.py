"""A semantic failure is evidence checked, distinct from a normal finding."""

from copy import deepcopy

import pytest

from skillflow.graph.audit.services import validate_audit
from skillflow.graph.audit.services import audit_source_controlled
from skillflow.graph.semantic_contract import CONTRACT_VERSION
from skillflow.common.semantic_failure import SemanticFailure
from tests.graph.audit.test_services import material, FakeClient


def failure_response(response):
    finding = response["findings"][1]
    return {
        "schema_version": 5, "contract_version": CONTRACT_VERSION,
        "outcome": "cannot_assess",
        "failure": {"reason": "源文的必要范围存在互斥要求，无法确定应保留哪一个。",
                    "source_refs": deepcopy(finding["source_refs"]),
                    "controlled_refs": deepcopy(finding["controlled_refs"])},
    }


def test_evidenced_failure_is_single_call_and_not_a_normal_result(material):
    source, document, normal = material
    response = failure_response(normal)
    client = FakeClient(response)
    with pytest.raises(SemanticFailure) as caught:
        audit_source_controlled(source, document, client)
    assert len(client.prompts) == 1
    assert caught.value.reason == response["failure"]["reason"]
    assert caught.value.failure["graph_refs"] == ["/blocks/arbitrary/instructions"]
    assert "findings" not in caught.value.failure


@pytest.mark.parametrize("change", [
    lambda r: r.update(findings=[]),
    lambda r: r.update(reviewed_source_unit_ids=[]),
    lambda r: r.update(notes=[]),
    lambda r: r.update(schema_version=4),
    lambda r: r.update(contract_version="skill-ir-semantic-contract-v3"),
    lambda r: r["failure"].update(source_refs=[], controlled_refs=[]),
    lambda r: r["failure"].update(reason=" "),
    lambda r: r["failure"]["source_refs"][0].update(quote="not in source"),
    lambda r: r["failure"]["controlled_refs"][0].update(unit_id="missing"),
    lambda r: r["failure"]["controlled_refs"][0].update(quote="not in text"),
    lambda r: r["failure"].update(graph_refs=["/fabricated"]),
])
def test_bad_failure_is_protocol_error_not_semantic_failure(material, change):
    source, document, normal = material
    response = failure_response(normal)
    change(response)
    with pytest.raises(ValueError) as caught:
        validate_audit(response, source, document)
    assert not isinstance(caught.value, SemanticFailure)


@pytest.mark.parametrize("change", [
    lambda r: r.update(failure={"reason": "hidden failure"}),
    lambda r: r.update(outcome="unknown"),
    lambda r: r.pop("outcome"),
    lambda r: r["findings"][0].update(unknown_reason=None),
    lambda r: r["findings"][1].update(status="unknown"),
    lambda r: r["findings"][1].update(basis=["insufficient"]),
    lambda r: r.update(unresolved=[]),
])
def test_completed_response_refuses_failure_and_legacy_fields(material, change):
    source, document, response = material
    change(response)
    with pytest.raises(ValueError) as caught:
        validate_audit(response, source, document)
    assert not isinstance(caught.value, SemanticFailure)
