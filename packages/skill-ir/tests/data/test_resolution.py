"""Deterministic structural selection and overlay views; no operation execution."""

import copy
import json

import pytest
from pydantic import ValidationError

from skill_ir.data import (
    Annotations, DataConflictError, DataPart, DataReferenceError, DataRegistry,
    FieldUpdatesContent, KnownPartsContent, LiteralContent, OpaqueContent,
    Origin, WholeExceptContent,
)


def source(registry, key="B", content=None):
    return registry.register_source(key, acquired_from=key, at="ir_read", content=content)


def result(registry, key, content, inputs):
    return registry.create_result(key, content=content, origin=Origin(
        at="ir_" + key, inputs=inputs,
    ))


def test_unknown_resolution_refines_original_base_and_keeps_whole_open():
    registry = DataRegistry("resolve")
    base = source(registry)
    filtered = result(registry, "exclude", WholeExceptContent(
        base=base.id, excluded_parts=[["secret"]],
    ), [base.id])
    before_origin = registry.get(filtered.id).origin
    address = registry.resolve_part(filtered.id, ["address"])
    assert address.id == registry.resolve_part(base.id, ["address"]).id
    assert address.origin.part_of == base.id
    assert registry.get(base.id).content.parts_complete is False
    assert registry.get(filtered.id).origin == before_origin
    for path in [["secret"], ["secret", "child"]]:
        before = registry.to_dict()
        with pytest.raises(DataReferenceError):
            registry.resolve_part(filtered.id, path)
        assert registry.to_dict() == before


def test_partial_exclusion_produces_filtered_ancestor_not_original():
    registry = DataRegistry("resolve")
    base = source(registry)
    original = registry.resolve_part(base.id, ["group"])
    secret = registry.resolve_part(base.id, ["group", "secret"])
    filtered = result(registry, "exclude", WholeExceptContent(
        base=base.id, excluded_parts=[["group", "secret"]],
    ), [base.id])
    view = registry.resolve_part(filtered.id, ["group"])
    assert view.id != original.id
    assert view.content == WholeExceptContent(base=original.id, excluded_parts=[["secret"]])
    assert view.origin.inputs == [filtered.id]
    before = registry.to_dict()
    assert registry.resolve_part(filtered.id, ["group"]).id == view.id
    assert registry.to_dict() == before
    with pytest.raises(DataReferenceError):
        registry.resolve_part(view.id, ["secret"])
    public = registry.resolve_part(view.id, ["public"])
    assert public.id == registry.resolve_part(base.id, ["group", "public"]).id
    assert registry.resolve_part(base.id, ["group", "secret"]).id == secret.id


def test_field_update_overrides_old_value_and_preserves_unknown_remainder():
    registry = DataRegistry("resolve")
    base, replacement = source(registry), source(registry, "replacement")
    old = registry.resolve_part(base.id, ["owner"])
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["owner"], data=replacement.id)],
    ), [base.id, replacement.id])
    assert registry.get_part(changed.id, ["owner"]).id == replacement.id
    assert registry.resolve_part(changed.id, ["owner"]).id == replacement.id
    assert registry.resolve_part(base.id, ["owner"]).id == old.id
    address = registry.resolve_part(changed.id, ["address"])
    assert address.id == registry.resolve_part(base.id, ["address"]).id
    assert registry.get(base.id).content.parts_complete is False
    assert isinstance(registry.get(changed.id).content, FieldUpdatesContent)


def test_updated_parent_hides_all_old_descendants():
    registry = DataRegistry("resolve")
    base = source(registry)
    old_secret = registry.resolve_part(base.id, ["group", "secret"])
    replacement = source(registry, "replacement", LiteralContent(value={"public": "ok"}))
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["group"], data=replacement.id)],
    ), [base.id, replacement.id])
    assert registry.resolve_part(changed.id, ["group", "public"]).content.value == "ok"
    with pytest.raises(DataReferenceError):
        registry.resolve_part(changed.id, ["group", "secret"])
    assert registry.resolve_part(base.id, ["group", "secret"]).id == old_secret.id


def test_partial_field_update_returns_overlay_ancestor_and_keeps_base_late_parts():
    registry = DataRegistry("resolve")
    base, replacement = source(registry), source(registry, "replacement")
    group = registry.resolve_part(base.id, ["group"])
    old_secret = registry.resolve_part(base.id, ["group", "secret"])
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["group", "secret"], data=replacement.id)],
    ), [base.id, replacement.id])
    view = registry.resolve_part(changed.id, ["group"])
    assert view.content == FieldUpdatesContent(
        base=group.id, updates=[DataPart(path=["secret"], data=replacement.id)],
    )
    assert registry.resolve_part(view.id, ["secret"]).id == replacement.id
    late = registry.resolve_part(base.id, ["group", "late"])
    assert registry.resolve_part(view.id, ["late"]).id == late.id
    assert registry.resolve_part(changed.id, ["group"]).id == view.id
    assert registry.resolve_part(group.id, ["secret"]).id == old_secret.id


def test_explicit_update_can_introduce_new_value_without_reviving_excluded_base():
    registry = DataRegistry("resolve")
    base, replacement = source(registry), source(registry, "replacement")
    registry.resolve_part(base.id, ["group", "old_secret"])
    filtered = result(registry, "exclude", WholeExceptContent(
        base=base.id, excluded_parts=[["group"]],
    ), [base.id])
    changed = result(registry, "update", FieldUpdatesContent(
        base=filtered.id, updates=[DataPart(path=["group", "public"], data=replacement.id)],
    ), [filtered.id, replacement.id])
    view = registry.resolve_part(changed.id, ["group"])
    assert isinstance(view.content, KnownPartsContent) and view.content.parts_complete
    assert registry.resolve_part(view.id, ["public"]).id == replacement.id
    with pytest.raises(DataReferenceError):
        registry.resolve_part(view.id, ["old_secret"])


def test_exclusion_after_update_wins_without_deleting_original_records():
    registry = DataRegistry("resolve")
    base, replacement = source(registry), source(registry, "replacement")
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["group", "secret"], data=replacement.id)],
    ), [base.id, replacement.id])
    filtered = result(registry, "exclude", WholeExceptContent(
        base=changed.id, excluded_parts=[["group", "secret"]],
    ), [changed.id])
    view = registry.resolve_part(filtered.id, ["group"])
    with pytest.raises(DataReferenceError):
        registry.resolve_part(view.id, ["secret"])
    assert registry.get(replacement.id).id == replacement.id


@pytest.mark.parametrize("value,path,expected", [
    ({"0": None}, ["0"], None), ([True, {"x": []}], [1, "x"], []),
    ({"nested": {"value": {}}}, ["nested", "value"], {}),
    ({"中文": ["line\n\\\"", 1.0]}, ["中文", 1], 1.0),
])
def test_literal_selection_preserves_json_types_and_is_stable(value, path, expected):
    registry = DataRegistry("resolve")
    base = source(registry, content=LiteralContent(value=value))
    chosen = registry.resolve_part(base.id, path)
    assert chosen.content.value == expected
    assert type(chosen.content.value) is type(expected)
    assert chosen.origin.inputs == []
    assert chosen.origin.part_of == base.id
    assert chosen.origin.path == path
    before = registry.to_dict()
    assert registry.resolve_part(base.id, path).id == chosen.id
    assert registry.to_dict() == before
    assert registry.get(base.id).content.value == value


@pytest.mark.parametrize("content,path", [
    (LiteralContent(value={"0": "field"}), [0]),
    (LiteralContent(value=["index"]), ["0"]),
    (LiteralContent(value=[]), [0]),
    (LiteralContent(value=None), ["field"]),
    (LiteralContent(value={}), ["missing"]),
    (KnownPartsContent(parts=[], parts_complete=True), ["missing"]),
])
def test_explicitly_absent_selection_does_not_create_opaque(content, path):
    registry = DataRegistry("resolve")
    base = registry.register_source("base", acquired_from="base", content=content)
    before, revision = registry.to_dict(), registry.revision
    with pytest.raises(DataReferenceError):
        registry.resolve_part(base.id, path)
    assert registry.to_dict() == before
    assert registry.revision == revision


def test_complete_flat_path_composition_resolves_ancestor_without_unknown_remainder():
    registry = DataRegistry("resolve")
    value = source(registry, "value")
    base = result(registry, "build", KnownPartsContent(
        parts=[DataPart(path=["group", "leaf"], data=value.id)], parts_complete=True,
    ), [value.id])
    view = registry.resolve_part(base.id, ["group"])
    assert view.content.parts_complete is True
    assert registry.resolve_part(view.id, ["leaf"]).id == value.id
    with pytest.raises(DataReferenceError):
        registry.resolve_part(view.id, ["unlisted"])


def test_revision_tracks_existing_description_changes_not_new_results():
    registry = DataRegistry("revision")
    assert registry.revision == 0
    base = source(registry)
    result(registry, "opaque", OpaqueContent(), [base.id])
    assert registry.revision == 0
    registry.resolve_part(base.id, ["field"])
    revision = registry.revision
    assert revision > 0
    registry.resolve_part(base.id, ["field"])
    assert registry.revision == revision
    registry.refine(base.id, annotations=Annotations(sensitivity=["credential"]))
    assert registry.revision > revision
    revision = registry.revision
    registry.refine(base.id, annotations=Annotations(sensitivity=["credential"]))
    assert registry.revision == revision
    with pytest.raises((ValidationError, AttributeError)):
        registry.revision = 999
    restored = DataRegistry.from_dict(registry.to_dict())
    assert restored.revision == 0
    assert restored.to_dict() == registry.to_dict()


def test_field_update_snapshot_isolated_roundtrip_and_origin_cannot_be_overwritten():
    registry = DataRegistry("resolve")
    base, replacement, other = source(registry), source(registry, "replacement"), source(registry, "other")
    content = FieldUpdatesContent(base=base.id, updates=[DataPart(path=["x"], data=replacement.id)])
    changed = result(registry, "update", content, [base.id, replacement.id])
    snapshot = registry.to_dict()
    restored = DataRegistry.from_json(registry.to_json())
    assert restored.to_dict() == snapshot
    assert restored.resolve_part(changed.id, ["x"]).id == replacement.id
    content.updates.clear()
    changed.content.updates.clear()
    assert registry.get(changed.id).content.updates[0].data == replacement.id
    with pytest.raises(DataConflictError):
        result(registry, "update", FieldUpdatesContent(
            base=base.id, updates=[DataPart(path=["x"], data=other.id)],
        ), [base.id, other.id])
    assert registry.to_dict() == snapshot


@pytest.mark.parametrize("reference", ["base", "updated_part"])
def test_field_update_rejects_dangling_references_atomically(reference):
    registry = DataRegistry("resolve")
    base = source(registry)
    before = registry.to_dict()
    content = FieldUpdatesContent(
        base="absent" if reference == "base" else base.id,
        updates=[DataPart(path=["x"], data="absent" if reference == "updated_part" else base.id)],
    )
    with pytest.raises(DataReferenceError):
        result(registry, "bad", content, [base.id])
    assert registry.to_dict() == before


@pytest.mark.parametrize("cyclic_edge", ["base", "updated_part"])
def test_field_update_rejects_containment_cycles_on_import(cyclic_edge):
    registry = DataRegistry("resolve")
    base, value = source(registry), source(registry, "value")
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["x"], data=value.id)],
    ), [base.id, value.id])
    payload = copy.deepcopy(registry.to_dict())
    entry = next(item for item in payload["records"] if item["data"]["id"] == changed.id)
    if cyclic_edge == "base":
        entry["data"]["content"]["base"] = changed.id
    else:
        entry["data"]["content"]["updates"][0]["data"] = changed.id
    with pytest.raises(DataConflictError, match="cycle"):
        DataRegistry.from_dict(payload)


def test_get_part_remains_read_only_and_does_not_reveal_old_partial_ancestor():
    registry = DataRegistry("resolve")
    base, value = source(registry), source(registry, "value")
    registry.resolve_part(base.id, ["group"])
    changed = result(registry, "update", FieldUpdatesContent(
        base=base.id, updates=[DataPart(path=["group", "x"], data=value.id)],
    ), [base.id, value.id])
    before = registry.to_dict()
    with pytest.raises(DataReferenceError):
        registry.get_part(changed.id, ["group"])
    with pytest.raises(DataReferenceError):
        registry.get_part(base.id, ["unknown"])
    assert registry.to_dict() == before


def test_failed_view_resolution_rolls_back_intermediate_base_refinement():
    registry = DataRegistry("resolve")
    base = source(registry)
    filtered = result(registry, "exclude", WholeExceptContent(
        base=base.id, excluded_parts=[["group", "secret"]],
    ), [base.id])
    reserved_key = "data-resolved-part:" + json.dumps(
        [filtered.id, ["group"]], ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    )
    registry.create_result(reserved_key, content=OpaqueContent(), origin=Origin(at="conflict"))
    before, revision = registry.to_dict(), registry.revision
    with pytest.raises(DataConflictError):
        registry.resolve_part(filtered.id, ["group"])
    assert registry.to_dict() == before
    assert registry.revision == revision
    assert isinstance(registry.get(base.id).content, OpaqueContent)
