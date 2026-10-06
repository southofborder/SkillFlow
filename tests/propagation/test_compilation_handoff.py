"""Real text/material compilation, scoped business handoff and zero-API replay."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
from pathlib import Path
import runpy
import socket

import pytest

from skillflow.propagation.handoff import build_doe_input
from skillflow.propagation.handoff import validate_doe_input
from skillflow.propagation.runner import load_propagation_run
from skillflow.propagation.runner import replay_propagation
from skillflow.propagation.runner import save_propagation_run
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.common.artifacts import ArtifactWriter


@pytest.fixture
def authored():
    path = project_root() / "examples/propagation/processing_demo.py"
    return runpy.run_path(str(path))["example"]()


def save(directory, authored):
    material, metadata, compilation, annotation, solved = authored
    return save_propagation_run(directory, material=material, source_metadata=metadata,
        annotation=annotation, location_evidences=compilation[1]["location_evidences"], solved=solved,
        raw_annotation=compilation[0], compilation_map=compilation[2],
        provenance={"kind": "hand_authored_specification"})


def test_raw_compiled_scoped_records_and_offline_replay_remain_distinct(tmp_path, monkeypatch, authored):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("offline attempted network"))
    monkeypatch.setattr(socket, "create_connection", lambda *a: pytest.fail("offline attempted network"))
    directory = tmp_path / "compiled"
    doe = save(directory, authored)
    raw, compiled, mapping = authored[2]
    assert all("model_observe" not in p["effects"] for p in raw["profiles"].values())
    assert any("model_observe" in p["effects"] for p in compiled["profiles"].values())
    assert mapping["events"] and any(e["kind"] == "observation" for e in mapping["events"])
    scope = doe["records"]["ir_send"]["events"][0]
    instance = scope["instances"][0]
    by_id = {data["id"]: data for data in doe["data"]}
    assert by_id[instance["collection"]]["content"]["form"] == "subset_view"
    recipient, body = [value[0] for value in instance["body"][-1]["atomic_ops"][0]["inputs"]]
    member = by_id[instance["element"]]["origin"]
    assert by_id[recipient]["origin"]["part_of"] == by_id[body]["origin"]["part_of"] == member["part_of"]
    assert by_id[recipient]["origin"]["path"] == member["path"] + ["recipient"]
    assert by_id[body]["origin"]["path"] == member["path"] + ["summary"]
    assert load_propagation_run(directory) == doe
    assert replay_propagation(directory) == doe
    assert read_json(directory / "replay/summary.json")["model_calls"] == 0
    assert not (directory / "replay/doe-input.json").exists()
    for filename in ("report.md", "report.html"):
        text = (directory / filename).read_text(encoding="utf-8")
        assert "逐元素作用域" in text and "summary" in text


@pytest.mark.parametrize("filename", ["raw-annotation", "compilation-map", "compilation"])
def test_altered_compilation_audit_is_rejected(tmp_path, authored, filename):
    directory = tmp_path / filename
    save(directory, authored)
    path = directory / "audit" / (filename + ".json")
    value = read_json(path)
    value["unexpected"] = True
    ArtifactWriter(()).json(path, value)
    with pytest.raises(ValueError):
        load_propagation_run(directory)


def test_foreign_data_cannot_masquerade_as_scope_element(authored):
    material, metadata, _, annotation, solved = authored
    doe = build_doe_input(material["source"], material["cfg"], annotation, solved,
                           source_metadata=metadata, execution_model=material["execution_model"])
    instance = doe["records"]["ir_send"]["events"][0]["instances"][0]
    instance["element"] = instance["collection"]
    with pytest.raises(ValueError):
        validate_doe_input(doe)


def test_compilation_map_cannot_be_replaced_with_other_same_shape_input(tmp_path, authored):
    values = list(authored)
    raw, compiled, mapping = deepcopy(values[2])
    mapping["raw_sha256"] = "0" * 64
    values[2] = (raw, compiled, mapping)
    with pytest.raises(ValueError, match="compilation mapping differs"):
        save(tmp_path / "bad", values)
    assert not (tmp_path / "bad/manifest.json").exists()
