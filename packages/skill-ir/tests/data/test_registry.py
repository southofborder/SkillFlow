"""Identity, refinement and import contracts without any propagation engine."""

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from skill_ir.data.models import (
    Annotations,
    DataPart,
    Dependency,
    FieldUpdatesContent,
    KnownPartsContent,
    LiteralContent,
    OpaqueContent,
    Origin,
    WholeExceptContent,
)
from skill_ir.data.registry import (
    DataConflictError,
    DataReferenceError,
    DataRegistry,
    DataRegistryError,
)


def source(registry, key="read-B", **kwargs):
    return registry.register_source(
        key, acquired_from="expense_document", at="ir_read", **kwargs
    )


def snapshot_record(snapshot, data_id):
    return next(record for record in snapshot["records"] if record["data"]["id"] == data_id)


def test_source_ids_are_stable_and_independent_of_registration_order():
    first, second = DataRegistry("demo"), DataRegistry("demo")
    a1, b1 = source(first, "A"), source(first, "B")
    b2, a2 = source(second, "B"), source(second, "A")
    assert (a1.id, b1.id) == (a2.id, b2.id)
    assert a1.id != b1.id
    assert source(DataRegistry("other"), "A").id != a1.id


def test_same_resource_different_acquisition_keys_remain_distinct():
    registry = DataRegistry("demo")
    first, retry = source(registry, "first_attempt"), source(registry, "retry_attempt")
    assert first.origin.acquired_from == retry.origin.acquired_from
    assert first.id != retry.id


def test_repeated_source_and_static_result_are_idempotent():
    registry = DataRegistry("demo")
    b = source(registry)
    assert source(registry).id == b.id
    origin = Origin(at="ir_sum", inputs=[b.id], dependencies=[
        Dependency(data=b.id, relation="derived")
    ])
    first = registry.create_result("sum-result", content=OpaqueContent(), origin=origin)
    second = registry.create_result("sum-result", content=OpaqueContent(), origin=origin)
    assert first.id == second.id
    assert len(registry) == 2


def test_reregistered_results_keep_exact_origins_inputs_and_relations():
    registry = DataRegistry("demo")
    b, other = source(registry), source(registry, "other")

    def register():
        return registry.create_result("sum", content=OpaqueContent(), origin=Origin(
            at="sum", inputs=[b.id], dependencies=[Dependency(
                data=b.id, relation="derived",
            )],
        ))

    first = register()
    second = register()
    third = register()
    assert first.id == second.id == third.id
    assert third.origin == first.origin
    before = registry.to_dict()
    for inputs, dependency in [
        ([b.id, other.id], Dependency(data=b.id, relation="derived")),
        ([b.id], Dependency(data=other.id, relation="derived")),
        ([b.id], Dependency(data=b.id, relation="possible")),
    ]:
        with pytest.raises(DataConflictError):
            registry.create_result("sum", content=OpaqueContent(), origin=Origin(
                at="sum", inputs=inputs, dependencies=[dependency],
            ))
        assert registry.to_dict() == before


@pytest.mark.parametrize("change", ["at", "acquired_from", "input_order", "input_repeat", "dependency_order"])
def test_reregistered_result_cannot_change_origin_order_or_repeat(change):
    registry = DataRegistry("origin-order")
    a, b = source(registry, "A"), source(registry, "B")
    original = Origin(at="op", inputs=[a.id, b.id, a.id], dependencies=[
        Dependency(data=a.id, relation="derived"), Dependency(data=b.id, relation="possible"),
    ])
    item = registry.create_result("result", content=OpaqueContent(), origin=original)
    changed = original.model_dump()
    if change == "at":
        changed["at"] = "different-op"
    elif change == "acquired_from":
        changed["acquired_from"] = "new-external-source"
    elif change == "input_order":
        changed["inputs"] = [a.id, a.id, b.id]
    elif change == "input_repeat":
        changed["inputs"] = [a.id, b.id]
    else:
        changed["dependencies"].reverse()
    before, revision = registry.to_dict(), registry.revision
    with pytest.raises(DataConflictError):
        registry.create_result("result", content=OpaqueContent(), origin=Origin.model_validate(changed))
    assert registry.to_dict() == before
    assert registry.revision == revision
    assert registry.get(item.id).origin == original


def test_source_and_result_keys_have_separate_identity_kinds():
    registry = DataRegistry("demo")
    b = source(registry, "same-key")
    result = registry.create_result("same-key", content=OpaqueContent(), origin=Origin(at="op"))
    assert b.id != result.id


def test_conflicting_source_origin_is_rejected_without_overwrite():
    registry = DataRegistry("demo")
    b = source(registry)
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        registry.register_source("read-B", acquired_from="different-resource", at="ir_read")
    assert registry.to_dict() == before
    assert registry.get(b.id).origin.acquired_from == "expense_document"


def test_part_registration_refines_parent_without_changing_its_identity():
    registry = DataRegistry("demo")
    b = source(registry)
    key = registry.register_part(b.id, ["api_key"])
    assert registry.get(b.id).id == b.id
    assert isinstance(registry.get(b.id).content, KnownPartsContent)
    assert registry.get(b.id).content.parts == [DataPart(path=["api_key"], data=key.id)]
    assert not registry.get(b.id).content.parts_complete
    assert key.origin.part_of == b.id
    assert key.origin.path == ["api_key"]


def test_repeated_part_registration_reuses_identity_and_deduplicates_sensitivity_evidences():
    registry = DataRegistry("demo")
    b = source(registry)
    first = registry.register_part(b.id, ["amount"], annotations=Annotations(
        sensitivity=["financial"], evidences=["私人费用金额"],
    ))
    second = registry.register_part(b.id, ["amount"], annotations=Annotations(evidences=["个人消费记录"]))
    third = registry.register_part(b.id, ["amount"], annotations=Annotations(evidences=["个人消费记录"]))
    assert first.id == second.id == third.id
    assert len(registry) == 2
    assert third.annotations.evidences == ["私人费用金额", "个人消费记录"]
    assert third.origin == first.origin


def test_string_field_and_integer_index_get_distinct_parts():
    registry = DataRegistry("demo")
    b = source(registry)
    field = registry.register_part(b.id, ["0"])
    index = registry.register_part(b.id, [0])
    assert field.id != index.id
    assert registry.get_part(b.id, ["0"]).id == field.id
    assert registry.get_part(b.id, [0]).id == index.id


def test_nested_part_identity_is_independent_of_parent_discovery_order():
    first, second = DataRegistry("demo"), DataRegistry("demo")
    b1, b2 = source(first), source(second)
    child_first = first.register_part(b1.id, ["group", "key"])
    group_later = first.register_part(b1.id, ["group"])
    group_first = second.register_part(b2.id, ["group"])
    child_later = second.register_part(group_first.id, ["key"])
    assert group_first.id == group_later.id
    assert child_first.id == child_later.id
    assert first.register_part(group_later.id, ["key"]).id == child_first.id
    assert second.get_part(b2.id, ["group", "key"]).id == child_first.id
    first.validate()
    second.validate()


def test_refinement_unions_possible_parts_without_claiming_completeness():
    registry = DataRegistry("demo")
    b = source(registry)
    first, second = source(registry, "known-first"), source(registry, "known-second")
    registry.refine(b.id, parts=[DataPart(path=["debug"], data=first.id)])
    registry.refine(b.id, parts=[DataPart(path=["normal"], data=second.id)])
    result = registry.get(b.id)
    assert result.id == b.id
    assert {tuple(part.path) for part in result.content.parts} == {("debug",), ("normal",)}
    assert result.content.parts_complete is False


def test_refinement_adds_annotations_and_evidence_idempotently():
    registry = DataRegistry("demo")
    b = source(registry)
    annotations = Annotations(description="费用文档", sensitivity=["financial"],
                              evidences=["包含个人费用明细"])
    registry.refine(b.id, annotations=annotations)
    first = registry.to_dict()
    registry.refine(b.id, annotations=annotations)
    assert registry.to_dict() == first
    assert registry.get(b.id).annotations.sensitivity == ["financial"]


def test_conflicting_description_and_part_binding_fail_atomically():
    registry = DataRegistry("demo")
    b = source(registry, annotations=Annotations(description="原描述"))
    child = registry.register_part(b.id, ["amount"])
    other = source(registry, "other")
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        registry.refine(b.id, annotations=Annotations(description="替换描述"))
    with pytest.raises(DataConflictError):
        registry.refine(b.id, parts=[DataPart(path=["amount"], data=other.id)])
    assert registry.to_dict() == before
    assert registry.get_part(b.id, ["amount"]).id == child.id


def test_explicit_complete_composition_cannot_be_silently_changed():
    registry = DataRegistry("demo")
    b = source(registry)
    registry.register_part(b.id, ["amount"])
    assert not registry.get(b.id).content.parts_complete
    registry.refine(b.id, parts_complete=True)
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        registry.refine(b.id, parts_complete=False)
    with pytest.raises(DataConflictError):
        registry.register_part(b.id, ["unlisted"])
    assert registry.to_dict() == before
    assert registry.get(b.id).content.parts_complete
    assert len(registry) == 2


def test_explicit_complete_reregistration_cannot_omit_existing_parts():
    registry = DataRegistry("demo")
    b = source(registry)
    amount = registry.register_part(b.id, ["amount"])
    registry.register_part(b.id, ["api_key"])
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        source(registry, content=KnownPartsContent(
            parts=[DataPart(path=["amount"], data=amount.id)], parts_complete=True,
        ))
    assert registry.to_dict() == before
    complete = registry.refine(b.id, parts_complete=True)
    assert complete.content.parts_complete
    assert len(complete.content.parts) == 2
    assert source(registry).id == b.id
    assert registry.get(b.id).content.parts_complete


def test_processing_creates_new_result_and_keeps_original_content():
    registry = DataRegistry("demo")
    b = source(registry)
    registry.register_part(b.id, ["api_key"])
    before = registry.get(b.id).model_dump()
    output = registry.create_result(
        "filtered", content=WholeExceptContent(base=b.id, excluded_parts=[["api_key"]]),
        origin=Origin(at="remove", inputs=[b.id]),
    )
    assert output.id != b.id
    assert output.origin.acquired_from is None
    assert registry.get(b.id).model_dump() == before


def test_exclusion_preserves_unknown_remainder_and_later_known_parts():
    registry = DataRegistry("demo")
    b = source(registry)
    output = registry.create_result(
        "filtered", content=WholeExceptContent(base=b.id, excluded_parts=[["api_key"]]),
        origin=Origin(at="remove", inputs=[b.id]),
    )
    address = registry.register_part(b.id, ["address"])
    key = registry.register_part(b.id, ["api_key"])
    registry.register_part(key.id, ["secret"])
    assert registry.get_part(output.id, ["address"]).id == address.id
    assert isinstance(registry.get(output.id).content, WholeExceptContent)
    with pytest.raises(DataReferenceError):
        registry.get_part(output.id, ["api_key"])
    with pytest.raises(DataReferenceError):
        registry.get_part(output.id, ["api_key", "secret"])


def test_partially_excluded_parent_cannot_be_returned_as_unfiltered_whole():
    registry = DataRegistry("demo")
    b = source(registry)
    group = registry.register_part(b.id, ["group"])
    registry.register_part(group.id, ["secret"])
    public = registry.register_part(group.id, ["public"])
    output = registry.create_result(
        "filtered", content=WholeExceptContent(base=b.id, excluded_parts=[["group", "secret"]]),
        origin=Origin(at="remove", inputs=[b.id]),
    )
    with pytest.raises(DataReferenceError):
        registry.get_part(output.id, ["group"])
    assert registry.get_part(output.id, ["group", "public"]).id == public.id


def test_refinement_cannot_rewrite_exclusion_as_known_parts():
    registry = DataRegistry("demo")
    b = source(registry)
    output = registry.create_result(
        "filtered", content=WholeExceptContent(base=b.id, excluded_parts=[["api_key"]]),
        origin=Origin(at="remove", inputs=[b.id]),
    )
    before = registry.to_dict()
    with pytest.raises(DataReferenceError):
        registry.register_part(output.id, ["x"])
    with pytest.raises(DataConflictError):
        registry.refine(output.id, parts=[DataPart(path=["x"], data=b.id)])
    assert registry.to_dict() == before


def test_direct_content_derived_value_and_possible_dependency_stay_distinct():
    registry = DataRegistry("demo")
    b = source(registry)
    total = registry.create_result("total", content=OpaqueContent(), origin=Origin(
        at="sum", inputs=[b.id], dependencies=[Dependency(data=b.id, relation="derived")]
    ))
    unknown = registry.create_result("unknown", content=OpaqueContent(), origin=Origin(
        at="f", inputs=[b.id], dependencies=[Dependency(data=b.id, relation="possible")]
    ))
    composite = registry.create_result("composite", content=KnownPartsContent(
        parts=[DataPart(path=["debug"], data=b.id), DataPart(path=["total"], data=total.id)],
        parts_complete=True,
    ), origin=Origin(at="build", inputs=[b.id, total.id]))
    assert registry.get_part(composite.id, ["debug"]).id == b.id
    assert total.origin.dependencies[0].relation == "derived"
    assert unknown.origin.dependencies[0].relation == "possible"
    assert isinstance(unknown.content, OpaqueContent)


def test_missing_references_and_unknown_lookup_fail_without_inserting_data():
    registry = DataRegistry("demo")
    b = source(registry)
    before = registry.to_dict()
    with pytest.raises(DataReferenceError):
        registry.get("absent")
    with pytest.raises(DataReferenceError):
        registry.get_part(b.id, ["unrecognized"])
    with pytest.raises(DataReferenceError):
        registry.refine(b.id, parts=[DataPart(path=["x"], data="absent")])
    with pytest.raises(DataReferenceError):
        registry.create_result("bad", content=OpaqueContent(), origin=Origin(at="op", inputs=["absent"]))
    assert registry.to_dict() == before


def test_contradictory_containment_prefix_overlap_is_rejected():
    registry = DataRegistry("demo")
    b = source(registry)
    x, y = source(registry, "x"), source(registry, "y")
    registry.register_part(x.id, ["b"])
    with pytest.raises(DataConflictError):
        registry.refine(b.id, parts=[DataPart(path=["a"], data=x.id),
                                     DataPart(path=["a", "b"], data=y.id)])
    assert isinstance(registry.get(b.id).content, OpaqueContent)


@pytest.mark.parametrize("content_kind", ["excluded", "literal", "complete"])
@pytest.mark.parametrize("intermediate_path", [["b"], ["b", "c"]])
def test_nested_overlap_cannot_bypass_filtered_literal_or_complete_content(
    content_kind, intermediate_path,
):
    registry = DataRegistry("demo")
    b = source(registry)
    secret = registry.register_part(b.id, ["secret"])
    claimed_field = "secret" if content_kind == "excluded" else "impossible"
    if content_kind == "excluded":
        restricted_content = WholeExceptContent(base=b.id, excluded_parts=[["secret"]])
    elif content_kind == "literal":
        restricted_content = LiteralContent(value={})
    else:
        restricted_content = KnownPartsContent(parts=[], parts_complete=True)
    filtered = registry.create_result(
        "restricted", content=restricted_content,
        origin=Origin(at="restrict", inputs=[b.id]),
    )
    # The longer form deliberately has no separately registered part at "b".
    intermediate = registry.create_result(
        "intermediate", content=KnownPartsContent(parts=[
            DataPart(path=intermediate_path, data=filtered.id),
        ]), origin=Origin(at="wrap", inputs=[filtered.id]),
    )
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        registry.create_result(
            "invalid-overlap", content=KnownPartsContent(parts=[
                DataPart(path=["a"], data=intermediate.id),
                DataPart(path=["a", *intermediate_path, claimed_field], data=secret.id),
            ]), origin=Origin(at="outer", inputs=[intermediate.id, secret.id]),
        )
    assert registry.to_dict() == before


def test_returned_models_input_models_and_export_dicts_are_isolated():
    registry = DataRegistry("demo")
    original_annotations = Annotations(sensitivity=["financial"])
    b = source(registry, annotations=original_annotations)
    original_annotations.sensitivity.append("tampered")
    b.annotations.sensitivity.append("tampered")
    registry.get(b.id).annotations.evidences.append("tampered")
    exported = registry.to_dict()
    snapshot_record(exported, b.id)["data"]["annotations"]["sensitivity"].append("tampered")
    assert registry.get(b.id).annotations.sensitivity == ["financial"]
    assert registry.get(b.id).annotations.evidences == []
    input_content = LiteralContent(value={"x": []})
    result = registry.create_result("literal", content=input_content,
                                    origin=Origin(at="constant"))
    input_content.value["x"].append("input-tampered")
    result.content.value["x"].append("tampered")
    assert registry.get(result.id).content.value == {"x": []}


@pytest.mark.parametrize("old_value", [[], ["spec:old"], (), {}])
def test_removed_evidence_arguments_are_rejected_instead_of_migrated(old_value):
    registry = DataRegistry("demo")
    with pytest.raises(TypeError, match="evidence_refs"):
        source(registry, evidence_refs=old_value)
    assert len(registry) == 0
    b = source(registry)
    before = registry.to_dict()
    with pytest.raises(TypeError, match="evidence_refs"):
        registry.register_part(b.id, ["key"], evidence_refs=old_value)
    with pytest.raises(TypeError, match="evidence_refs"):
        registry.refine(b.id, evidence_refs=old_value)
    assert registry.to_dict() == before


def test_forged_model_instances_cannot_bypass_validation():
    registry = DataRegistry("demo")
    invalid = Origin.model_construct(inputs=[123])
    with pytest.raises((DataRegistryError, ValidationError)):
        registry.create_result("bad", content=OpaqueContent(), origin=invalid)
    assert len(registry) == 0


def test_snapshot_round_trip_restores_identity_refinement_and_reuse():
    registry = DataRegistry("demo")
    b = source(registry)
    part = registry.register_part(b.id, ["amount"])
    document = registry.to_dict()
    assert document["schema_version"] == "skillflow-data-v4"
    for restored in [DataRegistry.from_dict(document), DataRegistry.from_json(registry.to_json())]:
        restored.validate()
        assert restored.to_dict() == document
        assert source(restored).id == b.id
        assert restored.register_part(b.id, ["amount"]).id == part.id
        assert len(restored) == 2


def test_data_v4_identity_is_version_bound_and_old_hash_is_not_reinterpreted():
    registry = DataRegistry("versioned")
    b = source(registry)
    document = registry.to_dict()
    entry = snapshot_record(document, b.id)
    old_encoded = json.dumps(
        ["skillflow-data-v3", document["namespace"], entry["identity"]],
        ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    old_id = "data_" + hashlib.sha256(old_encoded).hexdigest()
    assert old_id != b.id
    entry["data"]["id"] = old_id
    with pytest.raises(DataConflictError, match="identity key"):
        DataRegistry.from_dict(document)


@pytest.mark.parametrize("target", ["origin", "dependency", "annotations"])
def test_snapshot_rejects_old_evidence_fields_instead_of_moving_them(target):
    registry = DataRegistry("strict-v3")
    b = source(registry)
    result = registry.create_result("result", content=OpaqueContent(), origin=Origin(
        at="op", inputs=[b.id], dependencies=[Dependency(data=b.id, relation="possible")],
    ))
    document = registry.to_dict()
    data = snapshot_record(document, result.id)["data"]
    container = data["origin"]["dependencies"][0] if target == "dependency" else data[target]
    container["evidence_refs"] = ["spec:old"]
    with pytest.raises(ValidationError):
        DataRegistry.from_dict(document)
    assert registry.get(result.id).annotations.evidences == []


def test_snapshot_record_order_is_not_identity():
    registry = DataRegistry("demo")
    b = source(registry)
    child = registry.register_part(b.id, ["amount"])
    document = registry.to_dict()
    document["records"].reverse()
    restored = DataRegistry.from_dict(document)
    assert restored.get_part(b.id, ["amount"]).id == child.id
    assert restored.register_part(b.id, ["amount"]).id == child.id


def test_snapshot_part_identity_must_use_canonical_root_even_with_valid_hash():
    registry = DataRegistry("demo")
    b = source(registry)
    group = registry.register_part(b.id, ["group"])
    child = registry.register_part(group.id, ["key"])
    document = registry.to_dict()
    child_record = snapshot_record(document, child.id)
    child_record["identity"].update(parent_id=group.id, path=["key"])
    # Recompute the public identity hash so this tests canonical-root checking,
    # rather than merely failing an unrelated digest mismatch.
    encoded = json.dumps(
        [document["schema_version"], document["namespace"], child_record["identity"]],
        ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    forged_id = "data_" + hashlib.sha256(encoded).hexdigest()
    child_record["data"]["id"] = forged_id
    child_record["data"]["origin"].update(part_of=group.id, path=["key"])
    snapshot_record(document, group.id)["data"]["content"]["parts"][0]["data"] = forged_id
    with pytest.raises(DataConflictError, match="canonical root"):
        DataRegistry.from_dict(document)


@pytest.mark.parametrize("mutation", [
    lambda d: d.pop("schema_version"),
    lambda d: d.update(schema_version="skillflow-data-v0"),
    lambda d: d.update(schema_version="skillflow-data-v1"),
    lambda d: d.update(schema_version="skillflow-data-v2"),
    lambda d: d.update(schema_version="skillflow-data-v3"),
    lambda d: d.update(extra="not allowed"),
    lambda d: d["records"].append(copy.deepcopy(d["records"][0])),
    lambda d: d["records"][0]["identity"].update(key="forged-key"),
    lambda d: d["records"][0]["data"].update(id="forged-id"),
    lambda d: d["records"][0]["data"]["origin"].update(inputs=["absent"]),
])
def test_incompatible_corrupted_and_unbound_snapshots_are_rejected(mutation):
    registry = DataRegistry("demo")
    source(registry)
    document = registry.to_dict()
    mutation(document)
    with pytest.raises((DataRegistryError, ValidationError)):
        DataRegistry.from_dict(document)


def test_snapshot_import_rejects_composition_cycle():
    registry = DataRegistry("demo")
    a, b = source(registry, "A"), source(registry, "B")
    document = registry.to_dict()
    for item, other in [(a, b), (b, a)]:
        snapshot_record(document, item.id)["data"]["content"] = {
            "form": "known_parts", "parts_complete": False,
            "parts": [{"path": ["child"], "data": other.id}],
        }
    with pytest.raises(DataConflictError):
        DataRegistry.from_dict(document)


@pytest.mark.parametrize("payload", [
    '{"schema_version":"skillflow-data-v4","schema_version":"skillflow-data-v4",'
    '"namespace":"demo","records":[]}',
    '{"schema_version":"skillflow-data-v4","namespace":"demo","records":NaN}',
    '[]',
])
def test_non_strict_json_snapshots_are_rejected(payload):
    with pytest.raises(DataRegistryError):
        DataRegistry.from_json(payload)


def test_snapshot_import_allows_dependency_cycle_without_content_cycle():
    registry = DataRegistry("demo")
    a = registry.create_result("A", content=OpaqueContent(), origin=Origin(at="op_A"))
    b = registry.create_result("B", content=OpaqueContent(), origin=Origin(at="op_B"))
    document = registry.to_dict()
    for item, other in [(a, b), (b, a)]:
        origin = snapshot_record(document, item.id)["data"]["origin"]
        origin["inputs"] = [other.id]
        origin["dependencies"] = [{"data": other.id, "relation": "possible"}]
    restored = DataRegistry.from_dict(document)
    restored.validate()
    assert restored.get(a.id).origin.dependencies[0].data == b.id
    assert restored.get(b.id).origin.dependencies[0].data == a.id


def test_model_module_has_no_inference_or_propagation_dependencies():
    module_dir = Path(__file__).resolve().parents[2] / "src" / "skill_ir" / "data"
    forbidden = {"llm", "security_profile", "feedback", "backtrace", "propagation"}
    for module_path in module_dir.glob("*.py"):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module or "")
        assert not any(forbidden.intersection(name.split(".")) for name in modules)
