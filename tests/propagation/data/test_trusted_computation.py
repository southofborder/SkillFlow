"""Focused ownership, dependency and transaction checks for backend Data reads."""

import pytest
from pydantic import ValidationError

from skillflow.propagation.data import (
    DataRegistry, DataConflictError, DataReferenceError, LiteralContent,
    OpaqueContent, Origin, SubsetViewContent,
)
from skillflow.propagation.data.registry import _Identity, _MissingPart
from skillflow.propagation.loop_domain import LoopFactRegistry
from skillflow.propagation.loop_domain import key as loop_key
from skillflow.propagation.loop_guards import guard_values


def registry(loop=False):
    value = DataRegistry("trusted-computation-test")
    if loop:
        value = LoopFactRegistry(value, {})
    return value.enable_computation()


def literal(value, key="literal", content=True):
    return value.create_result(key, content=LiteralContent(value=content), origin=Origin(at=key))


@pytest.mark.parametrize("loop", [False, True])
def test_unchanged_registration_does_not_scan_or_rehash_unrelated_records(monkeypatch, loop):
    value = registry(loop)
    for index in range(12):
        literal(value, f"unrelated-{index}", index)
    first = literal(value)
    value.take_changes()
    revision = value.revision
    hashes = []
    original = value._id

    def identity(allocation):
        hashes.append(allocation.key)
        return original(allocation)

    def forbidden(*args, **kwargs):
        pytest.fail("an unchanged computed record must not validate unrelated records")

    monkeypatch.setattr(value, "_id", identity)
    monkeypatch.setattr(value, "_validate_records", forbidden)
    if loop:
        monkeypatch.setattr(value, "_all_entries", forbidden)
    assert literal(value).id == first.id
    assert hashes == ["literal"]
    assert value.revision == revision
    assert value.take_changes() == set()


def test_public_registry_keeps_full_validation_and_computed_export_is_explicit(monkeypatch):
    value = DataRegistry("public")
    original = value._validate_records
    calls = []

    def checked(records):
        calls.append(len(records))
        return original(records)

    monkeypatch.setattr(value, "_validate_records", checked)
    literal(value)
    literal(value)
    assert calls == [1, 1]
    with pytest.raises(RuntimeError, match="computation"):
        value.snapshot_computed()
    with pytest.raises(RuntimeError, match="computation"):
        value.identity_index_computed()
    snapshot = value.to_dict()
    snapshot["records"][0]["data"]["id"] = "forged"
    with pytest.raises(DataConflictError):
        DataRegistry.from_dict(snapshot)


@pytest.mark.parametrize("different", [1, 1.0, False])
def test_computed_noop_retains_typed_literal_conflicts(different):
    value = registry()
    first = literal(value)
    value.take_changes()
    with pytest.raises(DataConflictError, match="content changed"):
        literal(value, content=different)
    assert value.get(first.id).content.value is True
    assert value.take_changes() == set()


def test_computed_constructors_still_reject_forged_local_shapes_and_missing_references():
    value = registry()
    forged = LiteralContent(value=True).model_copy(update={"value": object()})
    with pytest.raises((ValidationError, ValueError)):
        value.create_result("forged", content=forged, origin=Origin(at="forged"))
    with pytest.raises(DataReferenceError, match="unknown"):
        value.create_result("missing", content=OpaqueContent(), origin=Origin(at="missing", inputs=["absent"]))
    assert len(value) == 0
    assert value.take_changes() == set()


@pytest.mark.parametrize("loop", [False, True])
def test_closed_part_negative_lookup_and_materialization_use_direct_index(monkeypatch, loop):
    value = registry(loop)
    whole = literal(value, "whole", [True])
    value.take_changes()
    part_key = value._part_key(whole.id, [0])
    with value.observe_reads() as missing:
        with pytest.raises(_MissingPart):
            value.get_part(whole.id, [0])
    assert missing == {("data", whole.id): 1, part_key: 0}
    part = value.resolve_part(whole.id, [0])
    assert value.take_changes() == {("data", part.id), part_key}
    assert value.key_version(part_key) == 1
    monkeypatch.setattr(value, "data_ids", lambda: pytest.fail("part lookup must not enumerate Data"))
    with value.observe_reads() as found:
        assert value.get_part(whole.id, [0]).id == part.id
    assert set(found) == {("data", whole.id), part_key, ("data", part.id)}


def test_transitive_collection_and_guard_reads_include_base_but_not_unrelated_data():
    value = registry(True)
    base = literal(value, "empty", [])
    view = value.create_result("subset", content=SubsetViewContent(base=base.id, predicate="allowed"),
                               origin=Origin(at="subset", inputs=[base.id]))
    unrelated = literal(value, "unrelated", False)
    with value.observe_reads() as observed:
        assert value.resolve_iteration_entries(view.id, "scope") == ()
        assert guard_values(value, [view.id], "empty") == {True}
    assert set(observed) == {("data", view.id), ("data", base.id)}
    assert ("data", unrelated.id) not in observed


def test_new_part_refinement_reports_parent_child_and_lookup_changes():
    value = registry()
    parent = value.register_source("source", acquired_from="input")
    value.take_changes()
    part = value.register_part(parent.id, ["name"])
    assert value.take_changes() == {
        ("data", parent.id), ("data", part.id), value._part_key(parent.id, ["name"]),
    }
    value.validate()


def test_missing_data_and_parent_binding_reads_are_observed():
    value = registry(True)
    parent = value.register_source("source", acquired_from="input")
    part = value.register_part(parent.id, ["name"])
    with value.observe_reads() as observed:
        assert not value.contains_data("absent")
        assert value.bindings(part.id) == {}
        assert value.family_producer("future-family") == "future-family"
    assert set(observed) == {
        ("data", "absent"), ("data", part.id), ("data", parent.id), ("data", "future-family"),
    }


def test_family_changes_are_local_noops_are_silent_and_first_read_version_is_retained():
    value = registry(True)
    first = value.family("loop", ["op"], [], LiteralContent(value=True), Origin(at="op"), bindings={})
    assert value.take_changes() == {("data", first.id)}
    before = value.key_version(("data", first.id))
    with value.observe_reads() as observed:
        assert value.family_producer(first.id) == '["op"]'
        value.family("loop", ["op"], [], LiteralContent(value=True), Origin(at="op"), bindings={})
        assert value.take_changes() == set()
        value.family("loop", ["op"], [], LiteralContent(value=False), Origin(at="op"), bindings={})
        value.get(first.id)
    assert observed[("data", first.id)] == before
    assert value.key_version(("data", first.id)) == before + 1
    assert value.take_changes() == {("data", first.id)}
    value.validate()


def test_ordinary_data_cannot_be_replaced_by_a_loop_family():
    value = registry(True)
    allocation = "loop-family:" + loop_key(["loop", loop_key(["op"]), {}])
    ordinary = literal(value, allocation, True)
    value.take_changes()
    with pytest.raises(DataConflictError, match="cannot become"):
        value.family("loop", ["op"], [], LiteralContent(value=False), Origin(at="op"), bindings={})
    assert value.get(ordinary.id).content.value is True
    assert value.facts == {}
    assert value.take_changes() == set()


@pytest.mark.parametrize("loop", [False, True])
def test_failed_resolution_rolls_back_data_index_versions_and_notifications(monkeypatch, loop):
    value = registry(loop)
    whole = literal(value, "whole", [True, False])
    value.take_changes()
    before = value.snapshot_computed()
    original = value.resolve_part

    def resolve(identity, path):
        if path == [1]:
            raise DataReferenceError("later member failed")
        return original(identity, path)

    monkeypatch.setattr(value, "resolve_part", resolve)
    with value.observe_reads() as observed:
        with pytest.raises(DataReferenceError, match="later member"):
            value.resolve_iteration_entries(whole.id, "scope")
    assert value.snapshot_computed() == before
    assert value.take_changes() == set()
    assert value._find_part(whole.id, [0]) is None
    assert all(stamp == value.key_version(key) for key, stamp in observed.items())


def test_family_transaction_rollback_restores_counts_and_dependencies():
    value = registry(True)
    with value.observe_reads() as observed:
        with pytest.raises(ValueError, match="abort"):
            with value._transaction():
                data = value.family("loop", ["op"], [], LiteralContent(value=True), Origin(at="op"), bindings={})
                raise ValueError("abort")
    assert value.facts == {}
    assert value._fact_count == value.fact_revision == 0
    assert value.take_changes() == set()
    assert observed[("data", data.id)] == value.key_version(("data", data.id)) == 0


def test_computed_seal_and_exports_detach_without_whole_registry_validation(monkeypatch):
    value = registry(True)
    ordinary = literal(value, "ordinary", {"items": [True]})
    family = value.family("loop", ["op"], [], LiteralContent(value=True), Origin(at="op"), bindings={})

    def forbidden(*args, **kwargs):
        pytest.fail("trusted sealing/export must not revalidate the full registry")

    monkeypatch.setattr(DataRegistry, "validate", forbidden)
    monkeypatch.setattr(DataRegistry, "from_dict", forbidden)
    sealed = value.seal()
    exported = sealed.snapshot_computed()
    index = sealed.identity_index_computed()
    assert set(index["identities"]) == {ordinary.id, family.id}
    value.family("loop", ["op"], [], LiteralContent(value=False), Origin(at="op"), bindings={})
    assert len(sealed.get(family.id).content.variants) == 1
    row = next(item for item in exported["records"] if item["data"]["id"] == ordinary.id)
    row["data"]["content"]["value"]["items"].append(False)
    assert sealed.get(ordinary.id).content.value == {"items": [True]}


def test_dependency_observations_are_nested_and_preserve_initial_absence():
    value = registry()
    expected = value._id(_Identity(kind="result", key="literal"))
    with value.observe_reads() as outer:
        assert not value.contains_data(expected)
        with value.observe_reads() as inner:
            created = literal(value)
        value.get(created.id)
    assert outer[("data", expected)] == 0
    assert inner[("data", expected)] == 1
