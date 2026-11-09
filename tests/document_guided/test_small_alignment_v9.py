"""Concrete v8 failure regressions through current compilation and saved DOE.

All answers are explicitly authored test candidates. These tests measure
representation and deterministic behavior, not online model correctness.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response, FlatAnnotationResponse
from skillflow.propagation import propagate, FlowLocation, FlowState
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.specs import WriteOp
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.data.summary import content_options
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.runner import save_propagation_run, load_propagation_materials
from skillflow.doe.formal_runner import run_doe
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from tests.propagation.component_helpers import accepted_annotation
from tests.document_guided.small_alignment_cases import (
    ROOT, UNKNOWN, catalog_fixture, catalog_sensitive_variant, notification_fixture, fallback_fixture, lit, local, inp,
)


@pytest.fixture(autouse=True)
def fixed_test_producer(monkeypatch):
    # Parallel implementation work must not masquerade as a changed producer
    # inside one freshly authored offline test. Real runs never use this seam.
    from tests.document_guided.test_parallel_runner import freeze_producer
    from skillflow.common.recording import implementation_provenance
    frozen = implementation_provenance()
    freeze_producer(monkeypatch)
    monkeypatch.setattr("skillflow.propagation.annotation.runner.implementation_provenance", lambda: deepcopy(frozen))


def solve(candidate):
    material, wire, seeds = candidate
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    registry = DataRegistry("source-derived-small-v9")
    bindings = {}
    for (kind, name), value in seeds.items():
        data = registry.register_source(kind + ":" + name, acquired_from=kind + ":" + name,
                                        **({} if value is UNKNOWN else {"content": LiteralContent(value=value)}))
        bindings[FlowLocation(kind=kind, name=name)] = frozenset([data.id])
    state = FlowState.from_mapping(bindings)
    solved = propagate(material["cfg"], to_payload(compiled), initial_registry=registry, initial_state=state)
    assert solved.status == "complete", solved.diagnostics
    return material, saved, raw, compiled, mapping, solved


def persist_doe(tmp_path, values, *, expected_status="complete"):
    material, wire, raw, compiled, mapping, solved = values
    origin = accepted_annotation(tmp_path / "annotation", material, raw)
    facts = save_propagation_run(tmp_path / "propagation", annotation_run=origin, solved=solved,
        requested_data=solved.initial_data, requested_state=solved.initial_state)
    assert facts.records == load_propagation_materials(tmp_path / "propagation").records
    result = run_doe(tmp_path / "propagation", run_dir=tmp_path / "doe")
    actual = json.loads((tmp_path / "doe/doe-result.json").read_text(encoding="utf-8"))
    assert actual["status"] == expected_status, actual.get("diagnostics")
    assert (tmp_path / "propagation/report.md").is_file()
    assert (tmp_path / "doe/report.md").is_file()
    return facts, actual


def operations(solved, identity, kind):
    return [op for event in solved.records.get(identity).events for op in event.atomic_ops if op.op == kind]


def literals(solved, identities):
    return [option["value"] for identity in identities for option in content_options(solved.registry, identity)
            if option["form"] == "literal"]


def test_frozen_small_source_copies_retain_original_bytes():
    import hashlib
    provenance = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
    assert len(provenance["files"]) == 5
    for row in provenance["files"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]


def test_optional_write_mode_is_only_wire_default_and_raw_mode_is_explicit():
    material, wire, _ = catalog_fixture()
    original = deepcopy(wire)
    saved, raw, compiled, _ = compile_flat_response(wire, material)
    assert saved == original == wire
    assert "mode" not in saved["ir_semantics"]["ir_save"]["segments"][0]["ops"][0]
    write = raw["ir_semantics"]["ir_save"]["events"][0]["events"][0]["atomic_ops"][0]
    assert write["mode"] == "replace"
    assert compiled["ir_semantics"]["ir_save"]["events"][0]["atomic_ops"][0]["mode"] == "replace"
    assert WriteOp.model_fields["mode"].is_required()
    schema = FlatAnnotationResponse.model_json_schema()
    flat_write = next(value for value in schema["$defs"].values() if value.get("properties", {}).get("op", {}).get("const") == "write")
    assert flat_write["properties"]["mode"]["default"] == "replace"
    assert "mode" not in flat_write["required"]


@pytest.mark.parametrize("mode", [None, "append", "delete"])
def test_write_defaults_preserve_input_validation_and_explicit_updates(mode):
    material, wire, _ = catalog_fixture(save_mode=mode)
    write = wire["ir_semantics"]["ir_save"]["segments"][0]["ops"][0]
    if mode == "delete":
        with pytest.raises(StructuralValidationError, match="delete"):
            compile_flat_response(wire, material)
        write.pop("input")
        write.pop("demands")
        _, raw, _, _ = compile_flat_response(wire, material)
        assert raw["ir_semantics"]["ir_save"]["events"][0]["events"][0]["atomic_ops"][0]["mode"] == "delete"
    else:
        write.pop("input")
        with pytest.raises(StructuralValidationError, match="input"):
            compile_flat_response(wire, material)


@pytest.mark.parametrize("from_date,limit", [(False, False), (True, False), (False, True), (True, True)])
def test_010_all_optional_combinations_real_response_save_and_return(tmp_path, from_date, limit):
    values = solve(catalog_fixture(from_date, limit))
    *_, solved = values
    call = operations(solved, "ir_search", "deliver")[0]
    request = solved.registry.get(next(iter(call.inputs[0]))).content
    names = {tuple(part.path) for part in request.parts}
    assert names == {("query",)} | ({("from_date",)} if from_date else set()) | ({("limit",)} if limit else set())
    assert not names & {("has_limit",), ("has_from_date",)}
    saved = operations(solved, "ir_save", "write")[0]
    selected = operations(solved, "ir_select", "select_part")
    assert saved.inputs[0] == selected[0].outputs[0]
    returned = solved.records.get("ir_return").entry_state.get(FlowLocation(kind="result", name="items"))
    assert returned == selected[1].outputs[0]
    assert not saved.inputs[0] & call.inputs[0]
    facts, doe = persist_doe(tmp_path, values)
    assert all(status == "processed" for status in facts.coverage.values())
    assert doe["coverage"]["declarations"] == 0  # Source supplies no sensitivity category.


def test_010_explicit_append_keeps_previous_storage_and_appends_actual_total(tmp_path):
    candidate = catalog_fixture(save_mode="append")
    candidate[2][("storage", "count.txt")] = ["old-count"]
    values = solve(candidate)
    *_, solved = values
    write = operations(solved, "ir_save", "write")[0]
    assert write.inputs[0] == operations(solved, "ir_select", "select_part")[0].outputs[0]
    facts, _ = persist_doe(tmp_path, values)
    mode = values[3]["ir_semantics"]["ir_save"]["events"][0]["atomic_ops"][0]["mode"]
    assert mode == "append"


@pytest.mark.parametrize("required", [False, True])
def test_separate_sensitive_variant_detects_extra_field_but_preserves_required_sensitive_use(tmp_path, required):
    values = solve(catalog_sensitive_variant(required=required))
    facts, doe = persist_doe(tmp_path, values)
    reviews = [item for sink in doe["sinks"] for item in sink["data_reviews"]]
    assert reviews
    assert any(item["conclusion"] == "excess_supported" for item in reviews) is (not required)
    assert any(row["path"] == "offline-variant.md" for row in values[0]["source"]["files"])
    original = catalog_fixture()[0]["source"]
    assert all(row["path"] != "offline-variant.md" for row in original["files"])


def test_001_guard_member_duplicate_pairing_and_count_ambiguity_survive_saved_doe(tmp_path):
    values = solve(notification_fixture())
    material, wire, _, _, _, solved = values
    members = operations(solved, "ir_member", "member")[0]
    assert len(members.outputs[0]) == 3
    assert len(members.alternatives) == 3
    sent = operations(solved, "ir_notify", "deliver")[0]
    assert len(sent.alternatives) == 3
    pairs = []
    for alternative in sent.alternatives:
        for identity in alternative.inputs[0]:
            content = content_options(solved.registry, identity)
            for row in content:
                if row["form"] == "known_parts":
                    parts = {tuple(part["path"]): part["data"] for part in row["parts"]}
                    recipient = solved.registry.get(parts[("recipient",)]).content.variants[0].content
                    body = solved.registry.get(parts[("body",)]).content.variants[0].content
                    assert recipient.path == ["recipient"] and body.path == ["summary"]
                    assert recipient.base == body.base
                    pairs.append(recipient.base)
    assert len(pairs) == len(set(pairs)) == 3
    assert material["task"]["issues"][0]["resolution"] == "unresolved"
    assert "Processed records" in wire["realizations"][1]["gaps"][0]["reason"]
    facts, doe = persist_doe(tmp_path, values, expected_status="partial")
    assert facts.coverage["ir_save"] == facts.coverage["ir_return"] == "processed"
    assert "Processed records" in json.dumps(doe)


def test_001_known_empty_filtered_collection_has_no_notification(tmp_path):
    values = solve(notification_fixture([]))
    *_, solved = values
    assert solved.coverage["ir_member"] == solved.coverage["ir_notify"] == "not_reached"
    assert solved.coverage["ir_save"] == "processed"
    _, doe = persist_doe(tmp_path, values, expected_status="partial")
    assert any(item["code"] == "task_source_issue" for item in doe["diagnostics"])


def test_001_old_boolean_plus_member_shape_cannot_invent_a_boolean_output():
    material, wire, _ = notification_fixture()
    # The original v8 fault is preserved as an independent invalid candidate.
    ir = material["cfg"]["blocks"]["body"]["instructions"][0]
    ir["outputs"].append({"type": "result", "identifier": "has_record", "semantic_name": "has_record"})
    wire["ir_semantics"]["ir_member"]["output_bindings"].append({"output_index": 1, "value": local("has_record")})
    with pytest.raises((StructuralValidationError, ValueError), match="has_record|local|binding"):
        compile_flat_response(wire, material)


def test_013_default_initial_state_keeps_unknown_previous_log_without_invented_read():
    material, wire, _ = fallback_fixture()
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    write = operations(solved, "ir_first_done_status", "write")[0]
    assert not operations(solved, "ir_first_done_status", "read")
    assert write.changes[0].before
    for identity in write.changes[0].before:
        before = solved.registry.get(identity)
        assert before.origin.acquired_from == "storage:status.txt"
        assert before.content.form == "opaque"


@pytest.mark.parametrize("options,terminal,called", [
    ({"first": True}, "first_done", ["fast"]),
    ({"first": False, "transient": True, "retry": True}, "retry_done", ["fast", "retry"]),
    ({"first": False, "transient": False, "archive": True}, "archive_done", ["fast", "archive"]),
    ({"first": False, "transient": True, "retry": False, "archive": False}, "archive_failed", ["fast", "retry", "archive"]),
    ({"key": False, "archive": True}, "archive_done", ["archive"]),
    ({"key": False, "archive": False}, "archive_failed", ["archive"]),
])
def test_013_binary_decisions_real_exception_sources_and_final_status(tmp_path, options, terminal, called):
    values = solve(fallback_fixture(**options))
    *_, solved = values
    for name in ("fast", "retry", "archive"):
        assert solved.coverage["ir_" + name] == ("processed" if name in called else "not_reached")
    for name in ("first_done", "retry_done", "archive_done", "archive_failed"):
        assert solved.coverage["ir_" + name + "_status"] == ("processed" if name == terminal else "not_reached")
        assert solved.coverage["ir_" + name + "_return"] == ("processed" if name == terminal else "not_reached")
    actual_key = set(operations(solved, "ir_context", "read")[1].outputs[0])
    for name in called:
        delivery = operations(solved, "ir_" + name, "deliver")[0]
        assert len(delivery.inputs) == (1 if name == "archive" else 2)
        assert (not actual_key.intersection(set().union(*delivery.inputs))) if name == "archive" else delivery.inputs[1] == actual_key
    status = operations(solved, "ir_" + terminal + "_status", "write")[0]
    returned = solved.records.get("ir_" + terminal + "_return")
    status_record = solved.records.get("ir_" + terminal + "_status")
    return_ir = values[0]["cfg"]["blocks"][terminal]["instructions"][-1]
    return_location = FlowLocation(kind="result", name=return_ir["inputs"][0]["identifier"])
    returned_ids = returned.entry_state.get(return_location)
    # Record v16 projects each instruction's snapshot separately. The return
    # retains its actual payload version, not the preceding write's dead file
    # binding; the write's own published state-change evidence must survive.
    assert {binding.location for binding in returned.entry_state.bindings} == {return_location}
    assert returned_ids and returned_ids == status_record.exit_state.get(return_location)
    for binding in returned.entry_state.bindings:
        assert binding.data_ids == status_record.exit_state.get(binding.location)
    assert len(status.changes) == 1
    change = status.changes[0]
    assert change.location == FlowLocation(kind="storage", name="status.txt")
    assert change.before and change.after and change.before.isdisjoint(change.after)
    assert status_record.entry_state.get(change.location) == change.before
    assert status_record.exit_state.get(change.location) == change.after
    assert returned.entry_state.get(change.location) is None
    if terminal != "archive_failed":
        producer = {"first_done": "fast", "retry_done": "retry", "archive_done": "archive"}[terminal]
        response = operations(solved, "ir_" + producer, "receive")[0]
        selected = operations(solved, "ir_" + producer, "select_part")[0]
        assert selected.inputs[0] == response.outputs[0]
        assert returned_ids == selected.outputs[0]
    assert status.inputs and literals(solved, status.inputs[0])
    if terminal == "archive_failed":
        errors = [op for op in operations(solved, "ir_archive", "receive")]
        returned_ids = returned.entry_state.get(FlowLocation(kind="result", name="archive_error"))
        assert len(errors) == 1 and returned_ids == errors[0].outputs[0]
        assert all(solved.registry.get(identity).origin.acquired_from == "tool:archive protected-call exception" for identity in returned_ids)
    facts, doe = persist_doe(tmp_path, values)
    assert facts.status == "complete"
    assert doe["coverage"]["declarations"] == 1
    inactive = [item for item in doe["diagnostics"] if item["code"] == "inactive_goal"]
    assert inactive and all(item.get("id") and not item["blocking"] for item in inactive)
    assert all(solved.coverage[item["instruction_id"]] == "not_reached" for item in inactive)
    assert not any(item["code"] in {"unbound_goal", "missing_local_record"} for item in doe["diagnostics"])


def _guided_fixture(material, wire):
    """Program-ID adaptation for an authored test, never historical migration."""
    from skillflow.document_guided.cfg_wire import normalize_cfg_wire
    from skillflow.graph.extraction.compiler import compile_candidate
    blocks = material["cfg"]["blocks"]
    candidate = {"entry_block_ref": material["cfg"]["entry_block_id"], "blocks": [], "edges": [
        {"source_block_ref": edge["source_block_id"], "target_block_ref": edge["target_block_id"]}
        for edge in material["cfg"]["edges"]]}
    for name, block in blocks.items():
        candidate["blocks"].append({"block_ref": name, "block_name": name,
            "data_source_kind": block.get("data_source_kind"), "instructions": [
                {"opcode": row["opcode"], "inputs": [
                    {key: value for key, value in operand.items() if key in {"type", "identifier", "literal_value"} and value is not None}
                    for operand in row["inputs"]], "outputs": [
                    {"type": "result", "identifier": operand["identifier"]} for operand in row["outputs"]]}
                for row in block["instructions"]]})
    compiled = compile_candidate(normalize_cfg_wire(candidate))
    assert compiled.ok, compiled
    block_names = {old: new for old, new in zip(blocks, compiled.cfg.blocks)}
    ids = {old["id"]: new.id for old_block, new_block in zip(blocks.values(), compiled.cfg.blocks.values())
           for old, new in zip(old_block["instructions"], new_block.instructions)}
    def rename(value):
        if isinstance(value, list):
            return [rename(item) for item in value]
        if isinstance(value, dict):
            return {ids.get(key, key): (ids.get(item, item) if key == "instruction_id" else
                block_names.get(item, item) if key in {"true_target", "false_target", "predecessor"} else rename(item))
                for key, item in value.items()}
        return value
    return candidate, rename(wire)


def test_013_source_cfg_finding_rebuilds_its_real_dependency_closure_and_finishes_doe(tmp_path, monkeypatch):
    from skillflow.document_guided import runner
    from skillflow.document_guided.fragments import split_fragments
    from tests.document_guided.test_parallel_runner import Harness
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    material, corrected, _ = fallback_fixture(first=False, transient=False, archive=True)
    before_material, before_wire = deepcopy(material), deepcopy(corrected)
    # A valid binary graph can still omit the separate transient-error test.
    # This is a CFG omission: processing cannot add the absent control block.
    before_material["cfg"]["blocks"].pop("failure")
    before_material["cfg"]["edges"] = [edge for edge in before_material["cfg"]["edges"] if edge["source_block_id"] != "failure"]
    for edge in before_material["cfg"]["edges"]:
        if edge["target_block_id"] == "failure":
            edge["target_block_id"] = "retry"
    before_wire["ir_semantics"].pop("ir_transient_guard")
    before_wire["ir_semantics"]["ir_first_guard"]["segments"][0]["ops"][0]["false_target"] = "retry"
    initial_graph, initial_wire = _guided_fixture(before_material, before_wire)
    corrected_graph, corrected_wire = _guided_fixture(material, corrected)

    class FallbackHarness(Harness):
        def __init__(self, directory):
            super().__init__(directory)
            self.example = {"source": (ROOT / "013/SKILL.md").read_text(encoding="utf-8"),
                "task_candidate": {key: deepcopy(material["task"][key]) for key in ("purpose", "requirements", "issues")}}
            self.graph = initial_graph
            self.fragments = split_fragments(initial_wire)

        def prepare(self, package):
            package.mkdir()
            (package / "SKILL.md").write_bytes((ROOT / "013/SKILL.md").read_bytes())
            runner.prepare(package, run_dir=self.directory)

        def complete(self, stage, prompt):
            if stage.startswith("revision-"):
                self.graph = corrected_graph
                self.fragments = split_fragments(corrected_wire)
            answer = super().complete(stage, prompt)
            if stage == "review":
                return {"outcome": "completed", "findings": [{"domain": "cfg", "target_ids": ["cfg:"],
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 10, "end_line": 11}],
                    "explanation": "The first failure directly reaches retry. The source retries only transient errors, requiring a separate conditional block consuming the first error classification.",
                    "suggestion": "Keep the success/failure decision and add a second binary transient/non-transient decision; route non-transient failure to archive."}]}
            return answer

    harness = FallbackHarness(tmp_path / "guided")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["repair_used"] and result["selected_annotation"] == "revision/annotation"
    assert len(harness.calls) == 12
    assert harness.calls.count("task") == harness.calls.count("flow") == 1
    assert {name for name in harness.calls if name.startswith("revision")} == {
        "revision-graph", "revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}
    facts = load_propagation_materials(harness.directory / "propagation")
    assert facts.status == "complete"
    doe = json.loads((harness.directory / "doe/doe-result.json").read_text(encoding="utf-8"))
    assert doe["status"] == "complete"
    assert any(item["code"] == "inactive_goal" for item in doe["diagnostics"])
    assert "first error classification" not in harness.prompts["task"]
