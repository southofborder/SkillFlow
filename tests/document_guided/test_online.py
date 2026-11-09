from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input, read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.online import (
    prepare_step, run_step, load_step, save_annotation, load_annotation, seal, CONFIG,
)


class Client:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), 0

    def complete(self, prompt):
        self.calls += 1
        return deepcopy(self.responses.pop(0))


def test_stage_corrects_only_its_batch_and_replays_without_dispatch(tmp_path):
    directory = tmp_path / "step"
    prepare_step(directory, "Return only locations and their evidence.", kind="locations")
    good = {"locations": {}, "location_evidences": {}}
    client = Client({**good, "ir_semantics": {}}, good)
    assert run_step(directory, client=client) == good
    assert client.calls == 2
    assert run_step(directory, client=client) == good
    assert client.calls == 2
    assert run_step(directory, replay=True) == load_step(directory) == good
    result = json.loads((directory / "result.json").read_text())
    assert result["counts"]["structural_corrections"] == 1


def test_document_and_dependencies_are_sealed(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("Original source")
    directory = tmp_path / "step"
    prepare_step(directory, "Source-only understanding", kind="document", dependencies=[source])
    assert run_step(directory, client=Client("# Flow\nPreserve source relationships."))
    assert load_step(directory).startswith("# Flow")
    source.write_text("Changed source")
    with pytest.raises(ValueError, match="changed"):
        load_step(directory)


def test_composition_load_propagate_doe_replay_and_tamper(tmp_path):
    from tests.document_guided.test_batches import annotation_batches
    from skillflow.task.runner import prepare_task_run, run_task
    from skillflow.propagation.runner import run_propagation, replay_propagation
    from skillflow.doe.formal_runner import run_doe, replay_doe
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.propagation.review.runner import prepare_run as prepare_review
    locations, irs, global_fields, material = annotation_batches()
    package = tmp_path / "package"
    package.mkdir()
    for row in material["source"]["files"]:
        path = package / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(row["content"].encode())
    writer = ArtifactWriter(())
    owner = tmp_path / "source"
    freeze_input(package, owner, writer)
    writer.json(owner / "manifest.json", seal({"identity": "test-source", "implementation": implementation_provenance()}))
    source = read_snapshot(owner)[1]
    task_dir = tmp_path / "task"
    prepare_task_run(task_dir, source_owner=owner, config=CONFIG)
    candidate = {key: material["task"][key] for key in ("purpose", "requirements", "issues")}
    result = run_task(task_dir, client=Client(candidate), config=CONFIG)
    assert result["status"] == "complete", result
    from skillflow.task.runner import load_task_run
    task = load_task_run(task_dir)["task"]
    global_fields["task_revision_id"] = task["task_sha256"]
    cfg_path = tmp_path / "cfg.json"
    writer.json(cfg_path, material["cfg"])
    steps = []
    for i, (kind, value) in enumerate([("locations", locations), *[("ir", v) for v in irs], ("globals", global_fields)]):
        step = tmp_path / f"step{i}"
        prepare_step(step, "Frozen synthetic batch request " + str(i), kind=kind)
        run_step(step, client=Client(value))
        steps.append(step)
    annotation = tmp_path / "annotation"
    saved = save_annotation(annotation, source_owner=owner, cfg_path=cfg_path, task_run=task_dir,
        location_step=steps[0], ir_steps=steps[1:-1], global_step=steps[-1])
    assert load_annotation_run(annotation)["raw_annotation"] == saved["raw_annotation"]
    assert saved["manifest"]["candidate_origin"] == "explicit_model_batch_composition"
    prepare_review(annotation, run_dir=tmp_path / "review", config=CONFIG)
    propagation = tmp_path / "propagation"
    run_propagation(annotation, run_dir=propagation)
    run_doe(propagation, run_dir=tmp_path / "doe")
    replay_propagation(propagation)
    replay_doe(tmp_path / "doe")
    raw = annotation / "audit/raw-annotation.json"
    raw.write_bytes(b"{}")
    with pytest.raises(ValueError, match="changed"):
        load_annotation(annotation)
