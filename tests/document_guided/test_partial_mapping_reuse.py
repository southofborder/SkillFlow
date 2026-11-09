"""A salvaged mapping can store requirement gaps without processing gaps."""
from copy import deepcopy

from skillflow.common.artifacts import ArtifactWriter
from skillflow.document_guided import online
from skillflow.task.runner import prepare_task_run, run_task
from tests.document_guided.test_fragment_diagnostic_aggregation import case_inputs
from tests.document_guided.test_online import Client
from tests.document_guided.test_parallel_runner import freeze_producer
from tests.document_guided.test_whole_steps import source_owner


def test_saved_partial_mapping_with_empty_validation_gap_list_is_readable(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    material, parts = case_inputs()
    owner = source_owner(tmp_path, {row["path"]: row["content"] for row in material["source"]["files"]})
    cfg = tmp_path / "cfg.json"
    ArtifactWriter(()).json(cfg, material["cfg"])
    task = tmp_path / "task"
    prepare_task_run(task, source_owner=owner, config=online.CONFIG)
    task_candidate = {key: material["task"][key] for key in ("purpose", "requirements", "issues")}
    assert run_task(task, client=Client(task_candidate), config=online.CONFIG)["status"] == "complete"
    processing = tmp_path / "processing"
    online.prepare_step(processing, "Return the processing facts.", kind="processing_fragment",
        context={"source_owner": owner, "cfg_path": cfg})
    online.run_step(processing, client=Client(parts["processing"]))
    invalid = deepcopy(parts["task-correspondence"])
    invalid["operation_demands"][0]["operation_path"] = ["segments", 99, "ops", 0]
    stage = tmp_path / "mapping"
    online.prepare_step(stage, "Return source-supported requirement correspondence.",
        kind="task-correspondence_fragment", max_corrections=0,
        context={"source_owner": owner, "cfg_path": cfg, "task_run": task, "processing_step": processing})
    client = Client(invalid)
    value = online.run_step(stage, client=client)
    result = online.read(stage / "result.json")
    assert result["status"] == "partial"
    assert result["validation_gaps"] == []
    assert value["realizations"][0]["gaps"]
    assert online.load_step(stage) == value
    assert online.load_step(stage, recompute=True) == value
    assert client.calls == 1
