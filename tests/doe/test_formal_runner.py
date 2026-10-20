"""Formal accepted-response handoff, one demand solve and durable zero-API DOE."""
from copy import deepcopy
import json
import socket

import pytest

from skillflow.common.recording import canonical_sha256, read_json, sha_file
from skillflow.doe import formal_runner as runner
from skillflow.doe.demand_engine import DemandEngine
from skillflow.propagation.annotation.runner import run_annotation
from tests.propagation.annotation.helpers import authored_prepare_run as prepare_run
from skillflow.propagation.annotation.inputs import load_prepared_material
from skillflow.propagation.runner import run_propagation, load_propagation_materials
from tests.propagation.annotation.helpers import FakeClient, graph, valid_raw_response


@pytest.fixture(autouse=True)
def stable_test_implementation(monkeypatch):
    # Parallel implementation work must not race the live source hash between
    # fixture stages. Production identity checks remain intact and are tested
    # separately below by changing this injected identity after preparation.
    from skillflow.propagation.annotation import runner as annotation_runner
    from skillflow.propagation import runner as propagation_runner
    identity = runner.implementation_provenance()
    for module in (annotation_runner, propagation_runner, runner):
        monkeypatch.setattr(module, "implementation_provenance", lambda: deepcopy(identity))


@pytest.fixture
def propagation_run(tmp_path, monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_kw: pytest.fail("Formal DOE used network"))
    monkeypatch.setattr(socket, "create_connection", lambda *_a, **_kw: pytest.fail("Formal DOE used network"))
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_text("---\nname: source\n---\nRead config.json; preserve its title. The token is a credential.\n", encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    directory = tmp_path / "annotation"
    prepare_run(package, analysis, run_dir=directory,
        user_request="Preserve the stated result and restrictions.")
    material = load_prepared_material(directory)
    raw = valid_raw_response(material)
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    segment["mode"] = "default"
    segment.pop("returns")
    raw["ir_semantics"]["ir_read"]["sensitivity"] = [{
        "value": {"kind": "local", "name": "stage_0"}, "path": ["token"],
        "property": "value", "label": "credential", "evidences": [{
            "file": "skill/SKILL.md", "start_line": 4, "end_line": 4,
            "reason": "The source identifies this field as a credential."}]}]
    raw["realizations"][0].update(status="expressed", gaps=[], constraints=[{
        "kind": "at_most", "scope": {"kind": "task"},
        "events": [{"instruction_id": "ir_read", "path": []}],
        "limit": 1, "unit": "attempt"}])
    raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [{
        "requirement_id": "R001", "target": {"kind": "output"},
        "preserve": "value", "path": [], "reason": "Retain the actual computed result in this test."}]
    client = FakeClient(raw)
    result = run_annotation(directory, client=client)
    assert result["status"] == "complete", result["reason"]
    assert len(client.prompts) == 1
    path = tmp_path / "propagation"
    run_propagation(directory, run_dir=path)
    return path


def test_one_solve_and_one_result_with_joint_projection(propagation_run, tmp_path, monkeypatch):
    original = DemandEngine.solve
    calls = []
    def solve(self, *args, **kwargs):
        calls.append(1)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(DemandEngine, "solve", solve)
    directory = tmp_path / "doe"
    loaded = runner.run_doe(propagation_run, run_dir=directory)
    assert calls == [1]
    assert loaded["manifest"]["identity"] == "skillflow-doe-run-v5"
    assert loaded["manifest"]["policy"]["candidate_origin"] == "model_annotation"
    assert loaded["annotation"]["task"]["basis"] == "user_request"
    assert loaded["result"]["coverage"]["declarations"] == 1
    assert len(loaded["result"]["constraints"]["checks"]) == 1
    assert all(row["status"] == "satisfied" for row in loaded["result"]["constraints"]["checks"].values())
    assert set(loaded["result"]["derivations"]["demand"]).isdisjoint(loaded["support"]["extra_derivations"])
    assert not any((directory / path).exists() for path in ("audit/demand", "task.json", "demand-result.json", "sensitivity-review.json"))
    assert 'href="doe-result.json"' in (directory / "report.html").read_text(encoding="utf-8")
    before = (directory / "doe-result.json").read_bytes()
    runner.load_doe_run(directory)
    runner.run_doe(propagation_run, run_dir=directory)
    assert calls == [1]
    assert runner.replay_doe(directory)["status"] == "matched"
    assert calls == [1, 1]
    assert (directory / "doe-result.json").read_bytes() == before
    assert len(list(directory.rglob("doe-result.json"))) == 1


def test_public_propagation_bundle_is_checked_and_isolated(propagation_run):
    bundle = load_propagation_materials(propagation_run)
    bundle.annotation["task"].clear()
    assert load_propagation_materials(propagation_run).annotation["task"]
    call = propagation_run.parent / "annotation/calls/annotation/a001/call.json"
    value = read_json(call)
    value["tampered"] = True
    call.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        load_propagation_materials(propagation_run)


@pytest.mark.parametrize("name", sorted(runner._ARTIFACTS))
def test_tampered_artifacts_are_rejected(propagation_run, tmp_path, name):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    path = directory / name
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="digest mismatch"):
        runner.load_doe_run(directory)


def test_read_no_solve_replay_strict_implementation(propagation_run, tmp_path, monkeypatch):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    monkeypatch.setattr(runner, "prepare_joint_sensitivity_review", lambda *_a, **_kw: pytest.fail("Loading solved again"))
    monkeypatch.setattr(runner, "implementation_provenance", lambda: {"changed": True})
    assert runner.load_doe_run(directory)["manifest"]["policy"]["model_calls"] == 0
    with pytest.raises(ValueError, match="implementation identity changed"):
        runner.replay_doe(directory)


@pytest.mark.parametrize("name", ["doe-result.json", "report.html", "manifest.json"])
def test_interrupted_save_is_not_committed_and_can_resume(propagation_run, tmp_path, monkeypatch, name):
    directory = tmp_path / "doe"
    original = runner.atomic_write_text
    def write(path, text):
        if path.name == name:
            raise KeyboardInterrupt()
        return original(path, text)
    monkeypatch.setattr(runner, "atomic_write_text", write)
    with pytest.raises(KeyboardInterrupt):
        runner.run_doe(propagation_run, run_dir=directory)
    assert not (directory / "manifest.json").exists()
    monkeypatch.setattr(runner, "atomic_write_text", original)
    assert runner.run_doe(propagation_run, run_dir=directory)["manifest"]["status"] in {"complete", "partial"}


def test_upstream_change_and_output_overlap_rejected(propagation_run, tmp_path):
    with pytest.raises(ValueError, match="overlap"):
        runner.run_doe(propagation_run, run_dir=propagation_run / "doe")
    assert not (propagation_run / "doe").exists()
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    path = propagation_run.parent / "annotation/audit/raw-annotation.json"
    raw = read_json(path)
    raw["task_revision_id"] = "changed"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="Saved annotation compilation material differs: raw-annotation"):
        runner.load_doe_run(directory)


def test_reject_authored_origin_before_writing(propagation_run, tmp_path, monkeypatch):
    loaded = load_propagation_materials(propagation_run)
    loaded._provenance["kind"] = "hand_authored_specification"
    monkeypatch.setattr(runner, "load_propagation_materials", lambda *_a: deepcopy(loaded))
    target = tmp_path / "doe"
    with pytest.raises(ValueError, match="accepted model"):
        runner.run_doe(propagation_run, run_dir=target)
    assert not target.exists()


def test_resealed_index_does_not_relabel_declaration(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    path = directory / "audit/index.json"
    index = read_json(path)
    # Declarations are owned by the selected annotation. The DOE index stores
    # only their coordinates; resealing it must not redirect a declaration to
    # another operation.
    next(iter(index["declarations"].values()))["instruction_id"] = "ir_filter"
    path.write_text(json.dumps(index), encoding="utf-8")
    manifest = read_json(directory / "manifest.json")
    manifest["artifacts"]["audit/index.json"] = sha_file(path)
    manifest["index_sha256"] = canonical_sha256(index)
    manifest["manifest_sha256"] = canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="declaration index differs"):
        runner.load_doe_run(directory)


def test_cli_explicit_identity_dispatch(propagation_run, tmp_path, capsys):
    from skillflow.doe.__main__ import main
    directory = tmp_path / "doe"
    assert main(["run", "--propagation-run", str(propagation_run), "--run-dir", str(directory)]) in {0, 1}
    assert main(["replay", "--run-dir", str(directory)]) == 0
    assert "matched" in capsys.readouterr().out
    manifest = read_json(directory / "manifest.json")
    manifest["identity"] = "unknown"
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        main(["replay", "--run-dir", str(directory)])
    assert error.value.code == 2
