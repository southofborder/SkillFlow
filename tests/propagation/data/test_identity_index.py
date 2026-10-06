"""One business Data copy plus a separately validated allocation index."""
from copy import deepcopy

import pytest

from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import Dependency
from skillflow.propagation.data import Origin
from skillflow.propagation.data import WholeExceptContent
from skillflow.propagation.data import export_identity_index
from skillflow.propagation.data import restore_registry
from skillflow.propagation.data import validate_data_records


def sample():
    registry = DataRegistry("identity-split")
    source = registry.register_source("read", acquired_from="document")
    registry.register_part(source.id, ["key"])
    registry.create_result("clean", content=WholeExceptContent(base=source.id, excluded_parts=[["key"]]),
                           origin=Origin(at="clean", inputs=[source.id],
                                         dependencies=[Dependency(data=source.id, relation="derived")]))
    return registry


def test_identity_export_and_restore_keep_all_ids_without_copying_data():
    registry = sample()
    data = [item["data"] for item in registry.to_dict()["records"]]
    index = export_identity_index(registry)
    assert set(index) == {"schema_version", "namespace", "identities"}
    assert all("data" not in identity and "content" not in identity for identity in index["identities"].values())
    assert restore_registry(data, index).to_dict() == registry.to_dict()
    index["namespace"] = "tampered"
    with pytest.raises(ValueError, match="identity"):
        restore_registry(data, index)
    assert registry.namespace == "identity-split"


@pytest.mark.parametrize("mutation", ["missing", "extra", "version", "key", "wrapper"])
def test_invalid_identity_indexes_are_rejected(mutation):
    registry = sample()
    data = [item["data"] for item in registry.to_dict()["records"]]
    index = export_identity_index(registry)
    first = next(iter(index["identities"]))
    if mutation == "missing": del index["identities"][first]
    if mutation == "extra": index["identities"]["extra"] = deepcopy(index["identities"][first])
    if mutation == "version": index["schema_version"] = "skillflow-data-v2"
    if mutation == "key": index["identities"][first]["key"] = "other"
    if mutation == "wrapper": index["records"] = []
    with pytest.raises(ValueError): restore_registry(data, index)


def test_standalone_validation_needs_no_allocation_keys_and_keeps_relationships():
    data = [{"id": "B", "content": {"form": "opaque"}},
            {"id": "clean", "content": {"form": "whole_except", "base": "B", "excluded_parts": [["key"]]},
             "origin": {"inputs": ["B", "B"], "dependencies": [{"data": "B", "relation": "possible"}]}}]
    checked = validate_data_records(data)
    assert checked[1]["origin"]["inputs"] == ["B", "B"]
    assert checked[1]["origin"]["dependencies"][0]["relation"] == "possible"
    assert data[0] == {"id": "B", "content": {"form": "opaque"}}


@pytest.mark.parametrize("data", [
    [{"id": "B", "content": {"form": "opaque"}}, {"id": "B", "content": {"form": "opaque"}}],
    [{"id": "B", "content": {"form": "whole_except", "base": "missing", "excluded_parts": [["key"]]}}],
    [{"id": "B", "content": {"form": "whole_except", "base": "B", "excluded_parts": [["key"]]}}],
    [{"id": "B", "content": {"form": "opaque"}},
     {"id": "P", "content": {"form": "opaque"}, "origin": {"part_of": "B", "path": ["key"]}}],
])
def test_standalone_validation_reuses_reference_and_composition_checks(data):
    with pytest.raises(ValueError): validate_data_records(data)


def test_dependency_cycles_are_not_confused_with_containment_cycles():
    data = [{"id": "A", "content": {"form": "opaque"}, "origin": {"dependencies": [{"data": "B", "relation": "possible"}]}},
            {"id": "B", "content": {"form": "opaque"}, "origin": {"dependencies": [{"data": "A", "relation": "derived"}]}}]
    assert len(validate_data_records(data)) == 2
