"""Local contracts for the unified data model; no semantic inference."""

import pytest
from pydantic import ValidationError

from skillflow.propagation.data.models import Annotations
from skillflow.propagation.data.models import Data
from skillflow.propagation.data.models import DataPart
from skillflow.propagation.data.models import Dependency
from skillflow.propagation.data.models import FieldUpdatesContent
from skillflow.propagation.data.models import KnownPartsContent
from skillflow.propagation.data.models import LiteralContent
from skillflow.propagation.data.models import OpaqueContent
from skillflow.propagation.data.models import Origin
from skillflow.propagation.data.models import WholeExceptContent
from skillflow.propagation.data.models import path_key


@pytest.mark.parametrize(
    "content",
    [
        OpaqueContent(),
        KnownPartsContent(),
        KnownPartsContent(parts=[DataPart(path=["amount"], data="B_amount")]),
        WholeExceptContent(base="B", excluded_parts=[["api_key"]]),
        FieldUpdatesContent(base="B", updates=[DataPart(path=["owner"], data="A")]),
        LiteralContent(value=None),
        LiteralContent(value={}),
        LiteralContent(value=[]),
        LiteralContent(value={"中文": ["引号\"\\\n\u0000```", 1, 1.0, True, None]}),
    ],
)
def test_content_forms_json_round_trip(content):
    original = Data(id="D", content=content)
    restored = Data.model_validate_json(original.model_dump_json())
    assert restored == original
    assert type(restored.content) is type(content)


def test_unknown_is_distinct_from_empty_and_null():
    records = [
        Data(id="D", content=content).model_dump_json()
        for content in [OpaqueContent(), LiteralContent(value=None), LiteralContent(value={}),
                        LiteralContent(value=[]), KnownPartsContent()]
    ]
    assert len(set(records)) == 5


@pytest.mark.parametrize("value", [0, 0.0, True, False, None, "0"])
def test_literal_scalar_types_are_preserved(value):
    restored = LiteralContent.model_validate_json(LiteralContent(value=value).model_dump_json())
    assert restored.value == value
    assert type(restored.value) is type(value)


@pytest.mark.parametrize(
    "value", [(1, 2), {1: "a"}, float("nan"), float("inf"), -float("inf"),
              {"nested": [float("nan")]}, object(), {"tuple": ()}]
)
def test_python_only_and_nonfinite_literal_values_are_rejected(value):
    with pytest.raises(ValidationError):
        LiteralContent(value=value)


def test_literal_cycles_are_rejected_but_shared_subtrees_are_allowed():
    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(ValidationError, match="reference cycle"):
        LiteralContent(value=cyclic)
    shared = {"a": 1}
    assert LiteralContent(value=[shared, shared]).value == [{"a": 1}, {"a": 1}]


@pytest.mark.parametrize("value", ["", " ", "\n\t", 123, None])
def test_identity_text_must_be_nonblank_string(value):
    with pytest.raises(ValidationError):
        Data(id=value, content=OpaqueContent())


def test_paths_preserve_field_index_distinction_and_empty_field_name():
    parts = [DataPart(path=["0"], data="field"), DataPart(path=[0], data="index"),
             DataPart(path=[""], data="empty_key")]
    content = KnownPartsContent(parts=parts)
    assert len({path_key(part.path) for part in content.parts}) == 3
    assert DataPart.model_validate_json(parts[1].model_dump_json()).path == [0]


@pytest.mark.parametrize("path", [[], [True], [-1], [1.0], [None], ("a",)])
def test_paths_reject_invalid_segments_and_nonlists(path):
    with pytest.raises(ValidationError):
        DataPart(path=path, data="D")


def test_duplicate_locations_and_empty_exclusions_are_rejected():
    with pytest.raises(ValidationError, match="duplicate"):
        KnownPartsContent(parts=[DataPart(path=["a"], data="A"),
                                 DataPart(path=["a"], data="B")])
    with pytest.raises(ValidationError):
        WholeExceptContent(base="B", excluded_parts=[])
    with pytest.raises(ValidationError, match="duplicate"):
        WholeExceptContent(base="B", excluded_parts=[["a"], ["a"]])


@pytest.mark.parametrize("paths", [[], [["a"], ["a"]], [["a"], ["a", "b"]],
                                    [["a", "b"], ["a"]], [[0], [0, "x"]]])
def test_field_updates_reject_empty_duplicate_and_overlapping_paths(paths):
    with pytest.raises(ValidationError):
        FieldUpdatesContent(base="B", updates=[DataPart(path=path, data="D") for path in paths])


def test_field_updates_keep_string_keys_distinct_from_indices_and_siblings():
    content = FieldUpdatesContent(base="B", updates=[
        DataPart(path=["0"], data="string"), DataPart(path=[0], data="index"),
        DataPart(path=["a", "b"], data="first"), DataPart(path=["a", "c"], data="second"),
    ])
    assert len(content.updates) == 4


def test_complete_composition_is_an_explicit_declaration_without_evidence_fields():
    content = KnownPartsContent(parts_complete=True)
    item = Data(id="empty", content=content)
    assert item.content.parts_complete
    assert not KnownPartsContent().parts_complete
    assert set(item.origin.model_dump()) == {
        "at", "acquired_from", "part_of", "path", "inputs", "dependencies",
    }


@pytest.mark.parametrize("fields", [
    {"part_of": "B"}, {"path": ["a"]},
    {"part_of": "B", "path": ["a"], "at": "read"},
    {"part_of": "B", "path": ["a"], "acquired_from": "file"},
    {"part_of": "B", "path": ["a"], "inputs": ["X"]},
    {"part_of": "B", "path": ["a"],
     "dependencies": [{"data": "X", "relation": "possible"}]},
])
def test_origin_part_identity_cannot_be_mixed_with_operations(fields):
    with pytest.raises(ValidationError):
        Origin(**fields)


def test_inputs_keep_order_and_repetitions_and_dependencies_keep_distinction():
    origin = Origin(
        at="op", acquired_from="remote", inputs=["B", "A", "B"],
        dependencies=[Dependency(data="B", relation="derived"),
                      Dependency(data="B", relation="possible")],
    )
    assert origin.inputs == ["B", "A", "B"]
    assert [d.relation for d in origin.dependencies] == ["derived", "possible"]
    assert origin.acquired_from == "remote"


@pytest.mark.parametrize("construct", [
    lambda: Origin(dependencies=[Dependency(data="B", relation="derived"),
                                 Dependency(data="B", relation="derived")]),
    lambda: Annotations(sensitivity=["credential", "credential"]),
    lambda: Annotations(evidences=["e", "e"]),
])
def test_duplicate_labels_and_evidence_are_rejected(construct):
    with pytest.raises(ValidationError, match="duplicate"):
        construct()


@pytest.mark.parametrize("construct", [
    lambda: OpaqueContent(extra="x"),
    lambda: FieldUpdatesContent(base="B", updates=[DataPart(path=["x"], data="D")], risk="safe"),
    lambda: KnownPartsContent(parts_complete="true"),
    lambda: Data(id="D", content={"form": "source"}),
    lambda: Origin(guaranteed=True),
    lambda: Annotations(risk="high"),
    lambda: Dependency(data="B", relation="plaintext"),
    lambda: Origin(evidence_refs=[]),
    lambda: Dependency(data="B", relation="possible", evidence_refs=[]),
    lambda: Annotations(evidence_refs=[]),
    lambda: Origin(evidences=[]),
    lambda: Dependency(data="B", relation="possible", evidences=[]),
])
def test_unknown_fields_and_noncontract_values_are_rejected(construct):
    with pytest.raises(ValidationError):
        construct()


@pytest.mark.parametrize("construct", [
    lambda: Origin(inputs=("A",)),
    lambda: KnownPartsContent(parts=()),
    lambda: WholeExceptContent(base="B", excluded_parts=(["a"],)),
    lambda: FieldUpdatesContent(base="B", updates=(DataPart(path=["x"], data="D"),)),
    lambda: Annotations(sensitivity=("credential",)),
    lambda: Annotations(evidences=("e",)),
])
def test_all_contract_lists_reject_tuple_coercion(construct):
    with pytest.raises(ValidationError):
        construct()


def test_model_attributes_are_frozen_and_nested_instances_revalidated():
    item = Data(id="D", content=OpaqueContent())
    with pytest.raises(ValidationError, match="frozen"):
        item.id = "changed"
    bad_origin = Origin.model_construct(inputs=[1])
    with pytest.raises(ValidationError):
        Data(id="D", content=OpaqueContent(), origin=bad_origin)
    corrupted_content = KnownPartsContent()
    corrupted_content.parts.append(DataPart.model_construct(path=[True], data="B"))
    with pytest.raises(ValidationError):
        Data(id="D", content=corrupted_content)


def test_sensitivity_evidences_have_the_only_evidence_field_and_round_trip():
    item = Data(id="D", content=OpaqueContent(), annotations=Annotations(
        sensitivity=["credential"], evidences=["人工示例：该值是身份认证凭据"],
    ))
    restored = Data.model_validate_json(item.model_dump_json())
    assert restored == item
    assert "evidence_refs" not in item.model_dump_json()
    assert set(restored.annotations.model_dump()) == {"description", "sensitivity", "evidences"}


@pytest.mark.parametrize("value", [(), {}, [1], [""], [" \t"], ["same", "same"]])
def test_sensitivity_evidences_remain_strict_nonblank_unique_strings(value):
    with pytest.raises(ValidationError):
        Annotations(evidences=value)
