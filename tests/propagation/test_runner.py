"""Offline run/replay identities, immutable inputs and review rendering."""
from copy import deepcopy
import json
import socket

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.propagation.models import FlowState
from skillflow.propagation.runner import load_propagation_materials
from skillflow.propagation.runner import replay_propagation
from skillflow.propagation.runner import run_propagation
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json, sha_file
from types import SimpleNamespace
from skillflow.propagation.annotation import load_prepared_material
from tests.propagation.annotation.helpers import authored_prepare_run as prepare_run
from skillflow.propagation.annotation.runner import run_annotation
from tests.propagation.annotation.helpers import FakeClient, graph


def components(value):
    return {name: getattr(value, name) for name in ("data", "records", "sinks", "status", "coverage", "diagnostics", "runtime_contract")}


def reseal(directory, manifest):
    manifest["manifest_sha256"] = canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    ArtifactWriter(()).json(directory / "manifest.json", manifest)


@pytest.fixture
def annotation_run(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline tests must not use networking")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_text("---\nname: fixture\n---\n读取文件，在本地处理后返回。\n", encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    directory = tmp_path / "annotation"
    prepare_run(package, analysis, run_dir=directory)
    client = FakeClient()
    result = run_annotation(directory, client=client)
    assert result["status"] == "complete" and len(client.prompts) == 1
    return directory


def test_run_and_replay_are_offline_and_bind_real_seed(annotation_run, tmp_path, monkeypatch):
    import skillflow.common.recording as recording
    monkeypatch.setattr(recording, "streaming_factory", lambda *_args, **_kwargs: pytest.fail("network factory created"))
    directory = tmp_path / "propagation"
    result = run_propagation(annotation_run, run_dir=directory)
    assert result.status == "complete"
    assert set(result.records) == {"ir_read", "ir_filter", "ir_return"}
    assert read_json(directory / "audit/requested-state.json") is None
    assert read_json(directory / "audit/requested-data.json") is None
    assert read_json(directory / "audit/initial-state.json")["bindings"]
    assert read_json(directory / "audit/initial-data.json")["records"]
    assert components(replay_propagation(directory)) == components(result)
    assert read_json(directory / "replay/summary.json")["status"] == "matched"
    assert all((directory / name).is_file() for name in ("data.json", "records.json", "sinks.json"))
    assert not any((directory / name).exists() for name in ("result.json", "doe-input.json", "resolved-seed.json"))
    assert not (directory / "replay/doe-input.json").exists()
    assert (directory / "report.html").is_file()
    assert (directory / "replay/report.md").is_file()
    assert 'href="../data.json"' in (directory / "replay/report.html").read_text(encoding="utf-8")
    assert result.runtime_contract == load_prepared_material(annotation_run)["runtime_contract"]
    assert "runtime_contract" not in read_json(directory / "manifest.json")
    assert not (directory / "audit/material.json").exists()



def test_annotation_result_cannot_substitute_its_contract_binding(annotation_run, tmp_path):
    path = annotation_run / "result.json"
    result = read_json(path)
    result["runtime_contract"]["sha256"] = "0" * 64
    ArtifactWriter(()).json(path, result)
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        run_propagation(annotation_run, run_dir=tmp_path / "propagation")


def test_full_run_checks_contract_binding_even_after_manifest_reseal(annotation_run, tmp_path):
    directory = tmp_path / "propagation"
    run_propagation(annotation_run, run_dir=directory)
    path = directory / "manifest.json"
    manifest = read_json(path)
    manifest["accepted_response_sha256"] = "0" * 64
    reseal(directory, manifest)
    with pytest.raises(ValueError, match="accepted annotation identity"):
        load_propagation_materials(directory)


def test_full_run_rejects_changed_upstream_contract_rules(annotation_run, tmp_path):
    directory = tmp_path / "propagation"
    run_propagation(annotation_run, run_dir=directory)
    path = annotation_run / "inputs/runtime-contract.json"
    contract = read_json(path)
    contract["rules"][0]["text"] += " altered rule"
    ArtifactWriter(()).json(path, contract)
    with pytest.raises(ValueError):
        load_propagation_materials(directory)


def test_explicit_empty_state_is_not_replaced_by_default_seed(annotation_run, tmp_path):
    directory = tmp_path / "empty-state"
    result = run_propagation(annotation_run, run_dir=directory, initial_state=FlowState())
    assert read_json(directory / "audit/requested-state.json") == {"bindings": []}
    assert read_json(directory / "audit/initial-state.json") == {"bindings": []}
    assert result.status != "complete"
    assert components(replay_propagation(directory)) == components(result)


def test_new_propagation_keeps_strict_producer_identity(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.annotation.runner as annotation_runner
    from skillflow.propagation.annotation.loading import load_annotation_run

    monkeypatch.setattr(annotation_runner, "implementation_provenance", lambda: {"changed_source": True})
    assert load_annotation_run(annotation_run)["result"]["status"] == "complete"
    target = tmp_path / "different-producer"
    with pytest.raises(ValueError, match="Implementation identity changed"):
        run_propagation(annotation_run, run_dir=target)
    assert not target.exists()


def test_existing_run_and_input_overlap_rejected(annotation_run, tmp_path):
    with pytest.raises(ValueError, match="overlap"):
        run_propagation(annotation_run, run_dir=annotation_run / "child")
    directory = tmp_path / "existing"
    directory.mkdir()
    keep = directory / "keep.txt"
    keep.write_text("unchanged")
    with pytest.raises(ValueError, match="new directory"):
        run_propagation(annotation_run, run_dir=directory)
    assert keep.read_text() == "unchanged"


@pytest.mark.parametrize("name", ["requested-data", "requested-state", "initial-data", "initial-state", "stats"])
def test_replay_refuses_changed_input_snapshot(annotation_run, tmp_path, name):
    directory = tmp_path / "changed"
    run_propagation(annotation_run, run_dir=directory)
    ArtifactWriter(()).json(directory / "audit" / (name + ".json"), {"tampered": True})
    with pytest.raises(ValueError, match="digest mismatch"):
        replay_propagation(directory)


@pytest.mark.parametrize("field,value", [("schema_version", 0), ("schema_version", 3), ("schema_version", 4), ("profile_schema_version", "security-profile-v5"), ("identity", "skill-ir-propagation-v3"), ("identity", "skill-ir-propagation-v4")])
def test_replay_refuses_prior_record_version(annotation_run, tmp_path, field, value):
    directory = tmp_path / "old"
    run_propagation(annotation_run, run_dir=directory)
    manifest = read_json(directory / "manifest.json")
    manifest[field] = value
    ArtifactWriter(()).json(directory / "manifest.json", manifest)
    with pytest.raises(ValueError, match="Unsupported propagation run version"):
        replay_propagation(directory)


def test_replay_refuses_changed_result_or_implementation(annotation_run, tmp_path):
    directory = tmp_path / "changed-result"
    run_propagation(annotation_run, run_dir=directory)
    path = directory / "data.json"
    original = path.read_bytes()
    result = read_json(path)
    result[0]["annotations"]["description"] = "changed business data"
    ArtifactWriter(()).json(path, result)
    with pytest.raises(ValueError, match="digest mismatch"):
        replay_propagation(directory)
    path.write_bytes(original)
    manifest = read_json(directory / "manifest.json")
    manifest["implementation"] = {}
    reseal(directory, manifest)
    with pytest.raises(ValueError, match="producer identity"):
        replay_propagation(directory)


def test_relative_upstream_tree_can_move_but_missing_annotation_is_rejected(annotation_run, tmp_path):
    import shutil
    tree = tmp_path / "tree"
    tree.mkdir()
    moved_annotation = tree / "annotation"
    # The independent Task owner is part of the exact upstream dependency tree.
    shutil.move(str(annotation_run.with_name(annotation_run.name + "-task")), tree / "annotation-task")
    shutil.move(str(annotation_run), moved_annotation)
    directory = tree / "propagation"
    result = run_propagation(moved_annotation, run_dir=directory)
    target = tmp_path / "relocated"
    tree.rename(target)
    assert components(replay_propagation(target / "propagation")) == components(result)
    (target / "annotation").rename(tmp_path / "missing-upstream")
    with pytest.raises((ValueError, FileNotFoundError)):
        load_propagation_materials(target / "propagation")


def test_cli_dispatches_only_offline_runner(monkeypatch, tmp_path):
    from skillflow.propagation import __main__ as cli
    calls = []
    monkeypatch.setattr(cli, "run_propagation", lambda *args, **kwargs: calls.append((args, kwargs)) or SimpleNamespace(status="complete"))
    monkeypatch.setattr(cli, "replay_propagation", lambda path: calls.append(path) or SimpleNamespace(status="incomplete"))
    assert cli.main(["run", "--annotation-run", str(tmp_path / "a"), "--run-dir", str(tmp_path / "b"),
                     "--seed-data", str(tmp_path / "data.json"), "--seed-state", str(tmp_path / "state.json")]) == 0
    assert cli.main(["replay", "--run-dir", str(tmp_path / "b")]) == 1
    assert len(calls) == 2
    assert calls[0][1]["initial_state"] == tmp_path / "state.json"
    assert calls[0][1]["seed_data"] == tmp_path / "data.json"


def test_state_file_is_frozen_and_empty_state_stays_explicit(annotation_run, tmp_path):
    state_path = tmp_path / "seed-state.json"
    state_path.write_text('{"bindings":[]}', encoding="utf-8")
    directory = tmp_path / "state-file"
    result = run_propagation(annotation_run, run_dir=directory, initial_state=state_path)
    assert state_path.read_text(encoding="utf-8") == '{"bindings":[]}'
    assert read_json(directory / "audit/requested-state.json") == {"bindings": []}
    assert read_json(directory / "audit/initial-state.json") == {"bindings": []}
    state_path.write_text("changed after freezing", encoding="utf-8")
    assert components(replay_propagation(directory)) == components(result)


def test_valid_but_replaced_result_is_not_the_accepted_response(annotation_run, tmp_path):
    saved = read_json(annotation_run / "audit/compiled-response.json")
    saved["ir_semantics"]["ir_filter"]["events"][0]["atomic_ops"][0]["dependencies"] = ["possible"]
    ArtifactWriter(()).json(annotation_run / "audit/compiled-response.json", saved)
    with pytest.raises(ValueError, match="compiled response|payload|compilation"):
        run_propagation(annotation_run, run_dir=tmp_path / "replaced")
    assert not (tmp_path / "replaced").exists()


@pytest.mark.parametrize("field,value", [("identity", "skill-ir-security-profile-v3"), ("schema_version", 3)])
def test_accepted_result_must_have_current_run_identity(annotation_run, tmp_path, field, value):
    saved = read_json(annotation_run / "result.json")
    saved[field] = value
    ArtifactWriter(()).json(annotation_run / "result.json", saved)
    with pytest.raises(ValueError, match="payload or location evidence differs from the accepted response"):
        run_propagation(annotation_run, run_dir=tmp_path / "old-result")


@pytest.mark.parametrize("relative", ["result.json", "audit/location-evidences.json", "audit/compiled-response.json",
                                      "audit/raw-annotation.json", "validation.json", "calls/annotation/a001/response.json"])
def test_annotation_changes_during_freezing_rejected_even_if_json_equal(annotation_run, tmp_path, monkeypatch, relative):
    original = ArtifactWriter.json
    modified = False
    def write_then_change(self, path, value):
        nonlocal modified
        answer = original(self, path, value)
        if not modified and path.name == "data.json":
            modified = True
            source = annotation_run / relative
            source.write_bytes(source.read_bytes() + b" ")
        return answer
    monkeypatch.setattr(ArtifactWriter, "json", write_then_change)
    directory = tmp_path / "raced"
    with pytest.raises(ValueError, match="changed|digest|differs"):
        run_propagation(annotation_run, run_dir=directory)
    assert modified and not (directory / "manifest.json").exists()


def test_changed_upstream_payload_cannot_replace_accepted_response(annotation_run, tmp_path):
    directory = tmp_path / "resealed"
    run_propagation(annotation_run, run_dir=directory)
    path = annotation_run / "audit/compiled-response.json"
    annotation = read_json(path)
    annotation["ir_semantics"]["ir_filter"]["events"][0]["atomic_ops"][0]["dependencies"] = ["possible"]
    ArtifactWriter(()).json(path, annotation)
    with pytest.raises(ValueError, match="accepted response|differs|identity"):
        replay_propagation(directory)


def test_replay_checks_upstream_call_and_transport(annotation_run, tmp_path):
    directory = tmp_path / "call-integrity"
    run_propagation(annotation_run, run_dir=directory)
    ArtifactWriter(()).json(annotation_run / "calls/annotation/a001/transport.json", [])
    with pytest.raises(ValueError, match="digest|request|identity"):
        replay_propagation(directory)


def test_location_audit_is_upstream_only_and_reported(annotation_run, tmp_path):
    directory = tmp_path / "separate-audit"
    result = run_propagation(annotation_run, run_dir=directory)
    table = read_json(annotation_run / "audit/location-evidences.json")
    payload = result.compiled_annotation
    assert set(table) == set(payload["locations"])
    assert not (directory / "audit/location-evidences.json").exists()
    assert not (directory / "audit/annotation.json").exists()
    for declaration in payload["locations"].values():
        assert set(declaration) == {"kind", "name", "operand_refs", "access_scope", "retention"}
    html = (directory / "report.html").read_text(encoding="utf-8")
    assert 'location-evidence' in html
    for data in result.data:
        assert "evidence_refs" not in json.dumps(data)
        assert data["annotations"]["evidences"] == []
        assert data["annotations"]["sensitivity"] == []


@pytest.mark.parametrize("mutation", ["missing", "digest", "quote", "resealed"])
def test_location_audit_changes_rejected_before_propagation(annotation_run, tmp_path, mutation):
    audit = annotation_run / "audit/location-evidences.json"
    if mutation == "missing":
        audit.unlink()
    else:
        table = read_json(audit)
        evidence = next(iter(table.values()))[0]
        evidence["quote" if mutation == "quote" else "reason"] = "不存在的证据内容"
        ArtifactWriter(()).json(audit, table)
        if mutation in {"quote", "resealed"}:
            saved = read_json(annotation_run / "result.json")
            saved["location_evidences_sha256"] = canonical_sha256(table)
            ArtifactWriter(()).json(annotation_run / "result.json", saved)
    with pytest.raises((ValueError, FileNotFoundError)):
        run_propagation(annotation_run, run_dir=tmp_path / "invalid-audit")
    assert not (tmp_path / "invalid-audit").exists()


def test_upstream_location_sidecar_cannot_replace_accepted_response(annotation_run, tmp_path):
    directory = tmp_path / "resealed-audit"
    run_propagation(annotation_run, run_dir=directory)
    path = annotation_run / "audit/location-evidences.json"
    table = read_json(path)
    next(iter(table.values()))[0]["reason"] = "Modified interpretation"
    ArtifactWriter(()).json(path, table)
    with pytest.raises(ValueError):
        replay_propagation(directory)


def test_readonly_loading_and_recomputation_have_different_identity_boundaries(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    directory = tmp_path / "read-only"
    result = run_propagation(annotation_run, run_dir=directory)
    assert components(load_propagation_materials(directory)) == components(result)
    monkeypatch.setattr(runner, "implementation_provenance", lambda: {"different_source": True})
    assert components(load_propagation_materials(directory)) == components(result)
    with pytest.raises(ValueError, match="implementation identity"):
        replay_propagation(directory)


@pytest.mark.parametrize("name", ["data-identities", "initial-data", "initial-state", "requested-data", "requested-state", "stats"])
def test_full_loader_checks_seed_and_registry_identity_index(annotation_run, tmp_path, name):
    directory = tmp_path / "identity-check"
    run_propagation(annotation_run, run_dir=directory)
    ArtifactWriter(()).json(directory / "audit" / (name + ".json"), {"tampered": True})
    with pytest.raises(ValueError, match="digest mismatch"):
        load_propagation_materials(directory)


def test_final_data_and_records_only_saved_once(annotation_run, tmp_path):
    directory = tmp_path / "no-copies"
    result = run_propagation(annotation_run, run_dir=directory)
    identity = read_json(directory / "audit/data-identities.json")
    assert set(identity) == {"schema_version", "namespace", "identities"}
    assert set(identity["identities"]) == {data["id"] for data in result.data}
    assert read_json(directory / "data.json") == result.data
    assert read_json(directory / "records.json") == result.records
    assert read_json(directory / "sinks.json") == result.sinks
    assert not (directory / "audit/record-materials.json").exists()
    for record in result.records.values():
        for event in record["events"]:
            assert set(event) == {"effect", "atomic_ops"}
            for op in event["atomic_ops"]:
                assert set(op) == {"op", "inputs", "outputs", "endpoints", "changes"}
                assert all(isinstance(candidates, list) for candidates in op["inputs"] + op["outputs"])


@pytest.fixture
def sink_annotation_run(tmp_path, monkeypatch):
    from tests.propagation.annotation.helpers import valid_raw_response
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_kw: pytest.fail("offline sink fixture"))
    package = tmp_path / "sink-package"
    package.mkdir()
    (package / "SKILL.md").write_text("---\nname: default-source\n---\n读取文件供 Agent 处理，未规定本地隔离机制。\n", encoding="utf-8")
    analysis = tmp_path / "sink-analysis.json"
    analysis.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    directory = tmp_path / "sink-annotation"
    prepare_run(package, analysis, run_dir=directory)
    raw = valid_raw_response(load_prepared_material(directory))
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    segment["mode"] = "default"
    segment.pop("returns", None)
    client = FakeClient(raw)
    result = run_annotation(directory, client=client)
    assert result["status"] == "complete", result["reason"]
    assert len(client.prompts) == 1
    return directory


def test_sink_list_and_boundary_table_use_actual_records_not_role_filter(sink_annotation_run, tmp_path):
    from skillflow.propagation.report import render_html
    from skillflow.propagation.report import render_markdown
    directory = tmp_path / "sink-view"
    result = run_propagation(sink_annotation_run, run_dir=directory)
    payload = result.compiled_annotation
    assert result.sinks
    for sink in result.sinks:
        assert sink in payload["sink_boundaries"]
        event = result.records[sink["instruction_id"]]["events"][sink["event_index"]]
        operation = event["atomic_ops"][sink["op_index"]]
        target = result.locations[sink["target"]]
        assert operation["endpoints"] == [{"kind": target["kind"], "name": target["name"]}]
        assert set(sink) == {"instruction_id", "event_index", "op_index", "body_event_index", "scope", "target", "sink_type", "exposure_level"}
    md, html = render_markdown(result), render_html(result)
    assert "Receiving and storage boundaries" in md and 'class="boundaries"' in html
    assert "not sensitivity" in html
    for sink in result.sinks:
        assert sink["sink_type"] in md and sink["sink_type"] in html
    assert components(replay_propagation(directory)) == components(result)


def test_resealed_sink_edit_cannot_change_fixed_classification(sink_annotation_run, tmp_path):
    directory = tmp_path / "sink-tamper"
    run_propagation(sink_annotation_run, run_dir=directory)
    sinks = read_json(directory / "sinks.json")
    sinks[0]["exposure_level"] = 3
    ArtifactWriter(()).json(directory / "sinks.json", sinks)
    manifest = read_json(directory / "manifest.json")
    manifest["artifacts"]["sinks.json"] = sha_file(directory / "sinks.json")
    reseal(directory, manifest)
    with pytest.raises(ValueError, match="sink inventory differs"):
        load_propagation_materials(directory)


def test_interrupted_save_has_no_commit_marker(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    directory = tmp_path / "interrupted"
    monkeypatch.setattr(runner, "write_reports", lambda *_a, **_kw: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        run_propagation(annotation_run, run_dir=directory)
    assert (directory / "data.json").is_file()
    assert not (directory / "manifest.json").exists()
    with pytest.raises(FileNotFoundError):
        load_propagation_materials(directory)


def test_replay_detects_resealed_requested_seed_change(annotation_run, tmp_path):
    directory = tmp_path / "changed-seed"
    run_propagation(annotation_run, run_dir=directory)
    state = {"bindings": []}
    ArtifactWriter(()).json(directory / "audit/requested-state.json", state)
    manifest = read_json(directory / "manifest.json")
    manifest["artifacts"]["audit/requested-state.json"] = sha_file(directory / "audit/requested-state.json")
    manifest["manifest_sha256"] = canonical_sha256({k:v for k,v in manifest.items() if k != "manifest_sha256"})
    ArtifactWriter(()).json(directory / "manifest.json", manifest)
    with pytest.raises(ValueError, match="differs from saved result"):
        replay_propagation(directory)
    assert read_json(directory / "replay/summary.json")["status"] == "mismatch"
    assert not (directory / "replay/doe-input.json").exists()




def test_save_checks_upstream_call_at_commit(annotation_run, tmp_path, monkeypatch):
    original = ArtifactWriter.json
    def mutate(self, path, value):
        answer = original(self, path, value)
        if path.name == "data.json":
            original(self, annotation_run / "calls/annotation/a001/transport.json", [])
        return answer
    monkeypatch.setattr(ArtifactWriter, "json", mutate)
    directory = tmp_path / "commit-call"
    with pytest.raises(ValueError, match="changed|digest|identity"):
        run_propagation(annotation_run, run_dir=directory)
    assert not (directory / "manifest.json").exists()


def test_save_checks_solved_seed_against_record_seed(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    calculate = runner._calculate
    def altered(*args):
        solved = calculate(*args)
        solved.initial_state = {"bindings": []}
        return solved
    monkeypatch.setattr(runner, "_calculate", altered)
    directory = tmp_path / "commit-seed"
    with pytest.raises(ValueError, match="seed|initial"):
        run_propagation(annotation_run, run_dir=directory)
    assert not (directory / "manifest.json").exists()


def test_non_network_tool_acquisition_survives_annotation_save_and_zero_api_replay(tmp_path, monkeypatch):
    from tests.propagation.annotation.helpers import valid_raw_response
    from skillflow.propagation.annotation.runner import replay_run as replay_annotation
    import skillflow.common.recording as recording

    def forbidden(*args, **kwargs):
        raise AssertionError("online operation forbidden")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(recording, "streaming_factory", forbidden)
    cfg = graph()
    acquisition = cfg["blocks"]["entry"]["instructions"][0]
    acquisition["opcode"] = "catalog.lookup"
    acquisition["inputs"][0]["identifier"] = "catalog"
    package = tmp_path / "skill"
    package.mkdir()
    text = "---\nname: catalog-result\n---\n从目录工具取得条目，工具返回内容交给模型后进行本地筛选。\n"
    (package / "SKILL.md").write_text(text, encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": cfg}), encoding="utf-8")
    directory = tmp_path / "annotation"
    prepare_run(package, analysis, run_dir=directory)
    material = load_prepared_material(directory)
    response = valid_raw_response(material)
    response["ir_semantics"]["ir_read"]["operator"] = ["tool", "llm"]
    response["ir_semantics"]["ir_read"]["operator_evidences"] = [
        {"target": {"instruction_id": "ir_read", "path": []}, "reason": "Authored tool fixture.", "value": value}
        for value in ["tool", "llm"]]
    response["ir_semantics"]["ir_read"]["empty_effect_evidences"] = [{
        "target": {"instruction_id": "ir_read", "path": []}, "reason": "Tool acquisition uses an unlabelled event."}]
    evidence = {"target": {"instruction_id": "ir_read", "path": []}, "reason": "离线构造的工具获取与观察，用于验证保存重放。"}
    response["locations"]["ir_read_boundary_0"]["kind"] = "tool"
    response["locations"]["ir_read_boundary_0"]["access_scope"] = "recipient"
    response["locations"]["ir_read_boundary_0"]["retention"] = None
    response["ir_semantics"]["ir_read"]["events"] = [
        {"kind": "processing", "mode": "default", "evidences": [deepcopy(evidence)], "events": [
            {"effect": None, "atomic_ops": [{"op": "receive", "location": "ir_read_boundary_0", "inputs": [], "output": "stage_0", "evidences": [deepcopy(evidence)]}]},
        ]},
    ]
    client = FakeClient(response)
    annotated = run_annotation(directory, client=client)
    assert annotated["status"] == "complete", annotated["reason"]
    assert len(client.prompts) == 1
    target = tmp_path / "propagation"
    actual = run_propagation(directory, run_dir=target)
    assert actual.status == "complete"
    tool_data = [d for d in actual.data if (d["origin"]["acquired_from"] or "").startswith("tool:")]
    assert len(tool_data) == 1
    assert actual.records["ir_read"]["events"][1]["atomic_ops"][0]["inputs"] == [[tool_data[0]["id"]]]
    assert components(load_propagation_materials(target)) == components(actual)
    assert replay_annotation(directory) == annotated
    assert components(replay_propagation(target)) == components(actual)
    assert len(client.prompts) == 1
    assert "Unlabeled data operation" in (target / "report.html").read_text(encoding="utf-8")
