"""Focused recording checks for whole-object document-guided requests."""
from copy import deepcopy

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.recording import implementation_provenance
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.document_guided.online import (
    CONFIG, load_annotation, load_step, prepare_step, read, run_step,
    save_whole_annotation, seal,
)
from tests.document_guided.test_online import Client
from tests.document_guided.test_batches import graph_example


def source_owner(tmp_path, files):
    package = tmp_path / "package"
    package.mkdir()
    for name, content in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
    owner = tmp_path / "source"
    writer = ArtifactWriter(())
    freeze_input(package, owner, writer)
    writer.json(owner / "manifest.json", seal({"identity": "test-source",
        "implementation": implementation_provenance()}))
    return owner


def test_whole_graph_corrects_compilation_and_copies_exact_code_then_recovers(tmp_path):
    owner = source_owner(tmp_path, {"SKILL.md": "Return the acquired value.\n", "code.py": "value = 1\r\nprint(value)\r\n"})
    candidate = graph_example()
    candidate["blocks"][0]["instructions"][0]["metadata"] = {
        "_source_span": {"file": "skill/code.py", "start_line": 1, "end_line": 2}}
    invalid = deepcopy(candidate)
    invalid["blocks"][1]["instructions"][0]["inputs"][0]["identifier"] = "missing"
    directory = tmp_path / "graph"
    prepare_step(directory, "Complete existing graph.", kind="full_graph", context={"source_owner": owner})
    client = Client(invalid, candidate)
    value = run_step(directory, client=client)
    assert client.calls == 2
    assert value["blocks"][0]["instructions"][0]["metadata"] == {"script_content": "value = 1\r\nprint(value)\r\n"}
    assert candidate["blocks"][0]["instructions"][0]["metadata"].get("_source_span")
    assert run_step(directory, client=client) == load_step(directory) == value
    assert client.calls == 2
    assert run_step(directory, replay=True) == value
    assert read(directory / "result.json")["counts"]["structural_corrections"] == 1


def test_graph_cannot_assess_is_terminal_not_a_structural_correction(tmp_path):
    owner = source_owner(tmp_path, {"SKILL.md": "The response format is unspecified.\n"})
    directory = tmp_path / "graph"
    prepare_step(directory, "Complete existing graph.", kind="full_graph", context={"source_owner": owner})
    failure = {"outcome": "cannot_assess", "failure": {"reason": "An entry relationship is unavailable.",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                       "reason": "No executable entry is identified."}]}}
    client = Client(failure)
    for kwargs in ({"client": client}, {"client": client}, {"replay": True}):
        with pytest.raises(SemanticFailure):
            run_step(directory, **kwargs)
    assert client.calls == 1
    assert read(directory / "result.json")["counts"]["structural_corrections"] == 0


def test_single_annotation_publication_loads_for_existing_backend(tmp_path):
    from skillflow.propagation.annotation.binding_examples import example_material, sink_demand_examples
    from skillflow.task.runner import prepare_task_run, run_task, load_task_run
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.propagation.runner import run_propagation, replay_propagation
    from skillflow.doe.formal_runner import run_doe, replay_doe
    example = sink_demand_examples()[0]
    material = example_material(example)
    owner = source_owner(tmp_path, {row["path"]: row["content"] for row in material["source"]["files"]})
    task = tmp_path / "task"
    prepare_task_run(task, source_owner=owner, config=CONFIG)
    task_candidate = {key: material["task"][key] for key in ("purpose", "requirements", "issues")}
    assert run_task(task, client=Client(task_candidate), config=CONFIG)["status"] == "complete"
    value = deepcopy(example["annotation"])
    value["task_revision_id"] = load_task_run(task)["task"]["task_sha256"]
    cfg = tmp_path / "cfg.json"
    ArtifactWriter(()).json(cfg, material["cfg"])
    step = tmp_path / "annotation-step"
    context = {"source_owner": owner, "cfg_path": cfg, "task_run": task}
    prepare_step(step, "Fill the complete annotation.", kind="full_annotation", context=context)
    client = Client(value)
    actual = run_step(step, client=client)
    annotation = tmp_path / "annotation"
    saved = save_whole_annotation(annotation, step=step, **context)
    assert saved["raw_annotation"] == actual
    assert saved["manifest"]["candidate_origin"] == "single_complete_model_response"
    assert "batch_steps" not in saved["upstream_identity"]
    assert load_annotation_run(annotation)["raw_annotation"] == actual
    assert save_whole_annotation(annotation, step=step, **context)["raw_annotation"] == actual
    run_propagation(annotation, run_dir=tmp_path / "propagation")
    run_doe(tmp_path / "propagation", run_dir=tmp_path / "doe")
    replay_propagation(tmp_path / "propagation")
    replay_doe(tmp_path / "doe")
    run_step(step, replay=True)
    assert client.calls == 1
    (annotation / "audit/raw-annotation.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        load_annotation(annotation)
