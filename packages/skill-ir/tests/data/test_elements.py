"""Collection members retain source identity without pretending to know indices."""

import copy

import pytest
from pydantic import TypeAdapter, ValidationError

from skill_ir.data import (
    DataConflictError, DataPart, DataReferenceError, DataRegistry, ElementStep,
    FieldUpdatesContent, KnownPartsContent, LiteralContent, Origin, Path,
    SubsetViewContent, WholeExceptContent, export_identity_index, restore_registry,
    validate_data_records, validate_element_membership, is_definitely_empty_collection,
)


def source(registry, key="rows", content=None):
    return registry.register_source(key, acquired_from=f"source:{key}", content=content)


def data_records(registry):
    return [entry["data"] for entry in registry.to_dict()["records"]]


def test_element_path_is_typed_hashable_frozen_and_json_roundtrippable():
    step = ElementStep(scope="IR:事件0/中文")
    path = TypeAdapter(Path).validate_python([step, "0", 0])
    assert len({step, "*", "0", 0}) == 4
    encoded = TypeAdapter(Path).dump_json(path)
    assert TypeAdapter(Path).validate_json(encoded) == path
    assert TypeAdapter(Path).dump_python(path) == [
        {"kind": "element", "scope": "IR:事件0/中文"}, "0", 0,
    ]
    with pytest.raises(ValidationError):
        step.scope = "changed"


@pytest.mark.parametrize("step", [
    {"kind": "element", "scope": ""}, {"kind": "element", "scope": " "},
    {"kind": "element", "scope": 1}, {"kind": "any", "scope": "x"},
    {"kind": "element", "scope": "x", "extra": True}, True, -1, 0.0,
])
def test_invalid_path_steps_are_rejected(step):
    with pytest.raises(ValidationError):
        TypeAdapter(Path).validate_python([step], strict=True)


def test_subset_and_nested_field_share_original_symbolic_identity():
    registry = DataRegistry("elements")
    rows = source(registry)
    subset = registry.subset_view("filter", rows.id, "active is true", Origin(at="filter", inputs=[rows.id]))
    nested = registry.subset_view("filter2", subset.id, "score > 2", Origin(at="filter2", inputs=[subset.id]))
    element = registry.resolve_element(nested.id, "loop")
    owner = registry.resolve_part(element.id, ["owner"])
    address = registry.resolve_part(owner.id, ["email"])
    step = ElementStep(scope="loop")
    assert element.id == registry.resolve_element(rows.id, "loop").id
    assert address.id == registry.resolve_part(subset.id, [step, "owner", "email"]).id
    assert address.origin.part_of == rows.id
    assert address.origin.path == [step, "owner", "email"]
    assert registry.get(rows.id).content.parts_complete is False
    assert registry.get(subset.id).content.base == rows.id
    before = registry.to_dict()
    for _ in range(3):
        assert registry.resolve_elements(subset.id, "loop") == (registry.get(element.id),)
    assert registry.to_dict() == before
    assert registry.resolve_element(rows.id, "other-loop").id != element.id


@pytest.mark.parametrize("path", [[0], ["0"], ["*"], [0, "name"]])
def test_filter_does_not_preserve_fixed_offsets_or_object_fields(path):
    registry = DataRegistry("elements")
    rows = source(registry)
    subset = registry.subset_view("filter", rows.id, "condition", Origin(at="filter"))
    before = registry.to_dict()
    for lookup in (registry.resolve_part, registry.get_part, registry.register_part):
        with pytest.raises(DataReferenceError, match="not fixed indices"):
            lookup(subset.id, path)
    assert registry.to_dict() == before


def test_symbolic_paths_participate_in_exclusion_and_overlay_without_being_wildcards():
    registry = DataRegistry("elements")
    rows = source(registry)
    step = ElementStep(scope="loop")
    other_step = ElementStep(scope="other-loop")
    element = registry.resolve_element(rows.id, step.scope)
    secret = registry.resolve_part(element.id, ["secret"])
    clean = registry.create_result("remove", content=WholeExceptContent(
        base=rows.id, excluded_parts=[[step, "secret"]]), origin=Origin(at="remove", inputs=[rows.id]))
    with pytest.raises(DataReferenceError, match="excluded"):
        registry.resolve_part(clean.id, [step, "secret"])
    later = registry.resolve_part(clean.id, [step, "later"])
    assert later.origin.part_of == rows.id
    assert later.origin.path == [step, "later"]
    assert registry.resolve_part(clean.id, [other_step, "secret"]).id != secret.id
    replacement = source(registry, "replacement", LiteralContent(value="redacted"))
    updated = registry.create_result("overwrite", content=FieldUpdatesContent(
        base=clean.id, updates=[DataPart(path=[step, "secret"], data=replacement.id)]),
        origin=Origin(at="overwrite", inputs=[clean.id, replacement.id]))
    assert registry.resolve_part(updated.id, [step, "secret"]).id == replacement.id
    assert registry.resolve_part(updated.id, [step, "later"]).id == later.id
    ancestor = registry.resolve_part(updated.id, [step])
    assert ancestor.content.form == "field_updates"
    validate_element_membership(data_records(registry), updated.id, ancestor.id)
    with pytest.raises(DataReferenceError):
        validate_element_membership(data_records(registry), updated.id, element.id)
    assert registry.resolve_part(ancestor.id, ["secret"]).id == replacement.id
    assert registry.resolve_part(rows.id, [step, "secret"]).id == secret.id


def test_symbolic_part_cannot_claim_complete_membership_or_conflicting_updates():
    step = ElementStep(scope="loop")
    with pytest.raises(ValidationError, match="complete composition"):
        KnownPartsContent(parts=[DataPart(path=[step], data="element")], parts_complete=True)
    with pytest.raises(ValidationError, match="overlap"):
        FieldUpdatesContent(base="base", updates=[
            DataPart(path=[step], data="a"), DataPart(path=[step, "field"], data="b"),
        ])
    with pytest.raises(ValidationError, match="duplicate"):
        WholeExceptContent(base="base", excluded_parts=[[step], [step]])


@pytest.mark.parametrize("value", [[], [{"a": 1}, {"a": 2}], [None, True, 1.0, []]])
def test_statically_supplied_literal_list_members_are_precise_and_do_not_use_index_zero_for_all(value):
    registry = DataRegistry("elements")
    rows = source(registry, content=LiteralContent(value=value))
    members = registry.resolve_elements(rows.id, "loop")
    assert tuple(member.content.value for member in members) == tuple(value)
    assert [member.origin.path for member in members] == [[index] for index in range(len(value))]
    assert all(member.origin.part_of == rows.id for member in members)
    assert len({member.id for member in members}) == len(value)
    assert registry.get(rows.id).content == LiteralContent(value=value)
    subset = registry.subset_view("filter", rows.id, "not evaluated", Origin(at="filter"))
    assert registry.resolve_elements(subset.id, "loop") == members
    for member in members:
        validate_element_membership(data_records(registry), subset.id, member.id)


def test_literal_nested_selection_is_canonical_and_validated_against_actual_values():
    registry = DataRegistry("elements")
    rows = source(registry, content=LiteralContent(value=[{"email": "a", "n": True}]))
    element, = registry.resolve_elements(rows.id, "loop")
    field = registry.resolve_part(element.id, ["email"])
    assert registry.resolve_part(rows.id, [0, "email"]).id == field.id
    assert registry.get_part(rows.id, [0, "email"]).id == field.id
    assert field.origin.path == [0, "email"]
    mutated = data_records(registry)
    next(data for data in mutated if data["id"] == field.id)["content"]["value"] = "forged"
    with pytest.raises(DataConflictError, match="closed parent"):
        validate_data_records(mutated)
    with pytest.raises(DataReferenceError, match="direct candidate"):
        validate_element_membership(data_records(registry), rows.id, field.id)
    boolean = registry.resolve_part(element.id, ["n"])
    mutated = data_records(registry)
    next(data for data in mutated if data["id"] == boolean.id)["content"]["value"] = 1
    with pytest.raises(DataConflictError, match="closed parent"):
        validate_data_records(mutated)


def test_complete_known_list_reuses_existing_values_and_allows_nested_member_descriptions():
    registry = DataRegistry("elements")
    a, b = source(registry, "a"), source(registry, "b")
    rows = source(registry, content=KnownPartsContent(parts=[
        DataPart(path=[0], data=a.id), DataPart(path=[1], data=b.id),
    ], parts_complete=True))
    assert registry.resolve_elements(rows.id, "loop") == (a, b)
    validate_element_membership(data_records(registry), rows.id, b.id)
    nested = source(registry, "nested", KnownPartsContent(parts=[
        DataPart(path=[0, "a"], data=a.id), DataPart(path=[1, "a"], data=b.id),
    ], parts_complete=True))
    nested_members = registry.resolve_elements(nested.id, "loop")
    assert [member.origin.path for member in nested_members] == [[0], [1]]
    assert registry.resolve_part(nested_members[0].id, ["a"]).id == a.id
    validate_element_membership(data_records(registry), nested.id, nested_members[1].id)


@pytest.mark.parametrize("content", [
    LiteralContent(value={}), LiteralContent(value={"0": "a"}), LiteralContent(value=None),
    KnownPartsContent(parts=[], parts_complete=True),
])
def test_non_list_closed_contents_do_not_silently_become_collections(content):
    registry = DataRegistry("elements")
    value = source(registry, content=content)
    before = registry.to_dict()
    with pytest.raises(DataReferenceError):
        registry.resolve_elements(value.id, "loop")
    assert registry.to_dict() == before


def test_open_object_or_closed_gapped_indices_are_not_claimed_as_list_members():
    registry = DataRegistry("elements")
    value = source(registry)
    field = registry.register_part(value.id, ["field"])
    with pytest.raises(DataConflictError, match="collection"):
        registry.subset_view("filter", value.id, "condition", Origin(at="filter"))
    with pytest.raises(DataReferenceError, match="object fields"):
        registry.resolve_elements(value.id, "loop")
    gapped = source(registry, "gapped", KnownPartsContent(parts=[DataPart(path=[2], data=field.id)], parts_complete=True))
    with pytest.raises(DataReferenceError, match="contiguous"):
        registry.resolve_elements(gapped.id, "loop")


def test_membership_rejects_foreign_elements_fields_and_derived_values():
    registry = DataRegistry("elements")
    left, right = source(registry, "left"), source(registry, "right")
    member = registry.resolve_element(left.id, "loop")
    foreign = registry.resolve_element(right.id, "loop")
    field = registry.resolve_part(member.id, ["payload"])
    derived = registry.create_result("compute", content=LiteralContent(value=0), origin=Origin(at="compute", inputs=[left.id]))
    subset = registry.subset_view("filter", left.id, "condition", Origin(at="filter"))
    values = data_records(registry)
    validate_element_membership(values, subset.id, member.id)
    validate_element_membership({data["id"]: data for data in values}, left.id, member.id)
    for invalid in (foreign, field, derived, left, right):
        with pytest.raises(DataReferenceError, match="direct candidate"):
            validate_element_membership(values, subset.id, invalid.id)
    malformed = {data["id"]: data for data in values}
    malformed["wrong"] = malformed.pop(values[0]["id"])
    with pytest.raises(DataConflictError, match="mapping keys"):
        validate_element_membership(malformed, left.id, member.id)


def test_subset_snapshot_restores_scope_identity_and_refuses_old_version_and_conflicts():
    registry = DataRegistry("elements")
    rows = source(registry)
    subset = registry.subset_view("filter", rows.id, "condition", Origin(at="filter", inputs=[rows.id]))
    member = registry.resolve_element(subset.id, "loop")
    field = registry.resolve_part(member.id, ["key"])
    for restored in (DataRegistry.from_json(registry.to_json()), restore_registry(data_records(registry), export_identity_index(registry))):
        assert restored.resolve_element(subset.id, "loop").id == member.id
        assert restored.resolve_part(rows.id, [ElementStep(scope="loop"), "key"]).id == field.id
        assert restored.to_dict() == registry.to_dict()
    before = registry.to_dict()
    with pytest.raises(DataConflictError):
        registry.subset_view("filter", rows.id, "different", Origin(at="filter", inputs=[rows.id]))
    with pytest.raises(DataReferenceError):
        registry.subset_view("other", "absent", "condition", Origin(at="filter"))
    assert registry.to_dict() == before
    old = copy.deepcopy(before)
    old["schema_version"] = "skillflow-data-v3"
    with pytest.raises(ValidationError):
        DataRegistry.from_dict(old)


def test_duplicate_or_corrupt_canonical_literal_origins_cannot_hide_in_business_records():
    registry = DataRegistry("elements")
    rows = source(registry, content=LiteralContent(value=["a"]))
    member, = registry.resolve_elements(rows.id, "loop")
    values = data_records(registry)
    forged = copy.deepcopy(next(data for data in values if data["id"] == member.id))
    forged["id"] = "duplicate"
    with pytest.raises(DataConflictError, match="duplicate canonical"):
        validate_data_records([*values, forged])


@pytest.mark.parametrize("value", [{}, {"rows": []}, None, True, 1, "text"])
def test_subset_rejects_explicit_noncollection_content(value):
    registry = DataRegistry("elements")
    base = source(registry, content=LiteralContent(value=value))
    before = registry.to_dict()
    with pytest.raises(DataConflictError, match="requires a collection"):
        registry.subset_view("filter", base.id, "condition", Origin(at="filter"))
    assert registry.to_dict() == before


def test_open_collection_retains_known_member_and_an_unenumerated_remainder():
    registry = DataRegistry("elements")
    base = source(registry)
    known = registry.register_part(base.id, [0], content=LiteralContent(value={"recipient": "known", "payload": "secret"}))
    members = registry.resolve_elements(base.id, "scope")
    assert members[0] == known and len(members) == 2
    assert members[1].origin.path == [ElementStep(scope="scope")]
    assert registry.resolve_part(members[0].id, ["payload"]).content.value == "secret"
    before = registry.to_dict()
    assert registry.resolve_elements(base.id, "scope") == members
    assert registry.to_dict() == before
    for member in members:
        validate_element_membership(data_records(registry), base.id, member.id)


def test_known_list_field_overlay_resolves_actual_indices_without_symbolic_offset_guess():
    registry = DataRegistry("elements")
    base = source(registry, content=LiteralContent(value=[{"recipient": "a", "payload": "old"}]))
    replacement = source(registry, "new", LiteralContent(value="new"))
    view = registry.create_result("updated", content=FieldUpdatesContent(base=base.id, updates=[
        DataPart(path=[0, "payload"], data=replacement.id),
    ]), origin=Origin(at="update", inputs=[base.id, replacement.id]))
    member, = registry.resolve_elements(view.id, "scope")
    assert member.content.form == "field_updates"
    assert registry.resolve_part(member.id, ["recipient"]).content.value == "a"
    assert registry.resolve_part(member.id, ["payload"]).id == replacement.id
    validate_element_membership(data_records(registry), view.id, member.id)
    assert registry.resolve_part(base.id, [0, "payload"]).content.value == "old"


def test_explicit_member_exclusion_does_not_return_old_member_or_lose_remaining_values():
    registry = DataRegistry("elements")
    base = source(registry, content=LiteralContent(value=["secret", "keep"]))
    cleaned = registry.create_result("removed", content=WholeExceptContent(base=base.id, excluded_parts=[[0]]), origin=Origin(at="remove"))
    remaining, = registry.resolve_elements(cleaned.id, "scope")
    assert remaining.origin.path == [1] and remaining.content.value == "keep"
    validate_element_membership(data_records(registry), cleaned.id, remaining.id)


def test_empty_collection_check_uses_known_literal_not_predicate_or_absent_descriptions():
    registry = DataRegistry("elements")
    empty = source(registry, "empty", LiteralContent(value=[]))
    subset = registry.subset_view("filter", empty.id, "always true", Origin(at="filter"))
    opaque = source(registry)
    nonempty = source(registry, "one", LiteralContent(value=["one"]))
    filtered = registry.subset_view("false", nonempty.id, "always false", Origin(at="filter"))
    values = data_records(registry)
    assert is_definitely_empty_collection(values, empty.id)
    assert is_definitely_empty_collection(values, subset.id)
    assert not is_definitely_empty_collection(values, opaque.id)
    assert not is_definitely_empty_collection(values, filtered.id)
    with pytest.raises(DataReferenceError):
        is_definitely_empty_collection(values, "missing")


@pytest.mark.parametrize("known_parts", [False, True])
def test_all_static_members_explicitly_removed_are_purely_verifiable_empty(known_parts):
    registry = DataRegistry("closed-empty")
    if known_parts:
        members = [source(registry, str(index), LiteralContent(value={"key": index})) for index in range(2)]
        content = KnownPartsContent(parts=[DataPart(path=[index], data=member.id)
                                          for index, member in enumerate(members)], parts_complete=True)
    else:
        content = LiteralContent(value=[{"key": 0}, {"key": 1}])
    base = source(registry, "whole", content)
    replacement = source(registry, "replacement", LiteralContent(value="changed"))
    updated = registry.create_result("updated", content=FieldUpdatesContent(base=base.id, updates=[
        DataPart(path=[0, "key"], data=replacement.id)]), origin=Origin(at="update"))
    empty = registry.create_result("removed", content=WholeExceptContent(base=updated.id, excluded_parts=[[0], [1]]), origin=Origin(at="remove"))
    subset = registry.subset_view("filtered", empty.id, "not executed", Origin(at="filter"))
    before = registry.to_dict()
    for collection in (empty, subset):
        assert registry.resolve_elements(collection.id, "loop") == ()
        assert is_definitely_empty_collection(data_records(registry), collection.id)
    assert registry.to_dict() == before  # Neither verification nor empty iteration allocates.


def test_deleting_member_fields_is_not_deleting_members_and_explicit_update_restores_member():
    registry = DataRegistry("closed-empty")
    base = source(registry, content=LiteralContent(value=[{"key": "old"}]))
    fields_removed = registry.create_result("fields", content=WholeExceptContent(base=base.id, excluded_parts=[[0, "key"]]), origin=Origin(at="remove"))
    assert not is_definitely_empty_collection(data_records(registry), fields_removed.id)
    assert len(registry.resolve_elements(fields_removed.id, "loop")) == 1
    all_removed = registry.create_result("all", content=WholeExceptContent(base=base.id, excluded_parts=[[0]]), origin=Origin(at="remove"))
    replacement = source(registry, "new", LiteralContent(value="new"))
    restored = registry.create_result("restored", content=FieldUpdatesContent(base=all_removed.id, updates=[
        DataPart(path=[0, "key"], data=replacement.id)]), origin=Origin(at="restore"))
    assert not is_definitely_empty_collection(data_records(registry), restored.id)
    member, = registry.resolve_elements(restored.id, "loop")
    assert registry.resolve_part(member.id, ["key"]).id == replacement.id


def test_removing_all_known_open_members_does_not_prove_unknown_remainder_empty():
    registry = DataRegistry("open-empty")
    base = source(registry)
    registry.register_part(base.id, [0])
    removed = registry.create_result("removed", content=WholeExceptContent(base=base.id, excluded_parts=[[0]]), origin=Origin(at="remove"))
    assert not is_definitely_empty_collection(data_records(registry), removed.id)
    assert len(registry.resolve_elements(removed.id, "loop")) == 1
