"""The new preparation contract and local timing preserve seven-call computation."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import json

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import ANNOTATION_IDENTITY, STEP_IDENTITY, read
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


def timing_class():
    path = Path(__file__).resolve().parents[2] / "output/verification/cfg-processing-alignment-v9-20261102/local_timing.py"
    spec = spec_from_file_location("alignment_local_timing", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LocalTiming


def test_new_policy_is_explicit_and_observation_keeps_seven_calls_and_replay(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = Harness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    manifest = read(harness.directory / "manifest.json")
    assert manifest["identity"] == "skillflow-document-guided-run-v9"
    assert STEP_IDENTITY == "skillflow-document-step-v8"
    assert ANNOTATION_IDENTITY == "skillflow-document-annotation-v8"
    assert manifest["policy"]["semantic_source_view"] == "complete_frozen_source"
    assert manifest["policy"]["ordinary_write_default"] == "replace"
    assert manifest["policy"]["dispatch_successors"] == "binary"
    observer = timing_class()().install()
    def unavailable_progress(*args):
        raise OSError("optional progress output unavailable")
    try:
        result = runner.run(harness.directory, client_factory=harness.factory, progress=unavailable_progress)
        assert result["status"] == "complete", result
        observer.phase = "replay"
        assert runner.replay(harness.directory) == result
    finally:
        observer.restore()
    assert len(harness.calls) == 7
    assert result["counts"]["structural_corrections"] == 0
    observed = observer.snapshot()
    analysis = {row["component"] for row in observed["records"] if row["phase"] == "analysis"}
    assert analysis == {"propagation_compute", "propagation_save", "propagation_total",
                        "doe_load", "doe_compute", "doe_total"}
    assert all(row["elapsed_seconds"] >= 0 for row in observed["records"])
    assert len(observed["doe_post_compute_publication"]) == 1
    assert observed["doe_post_compute_publication"][0]["phase"] == "analysis"


def test_local_timing_preserves_failure_identity_and_does_not_capture_data():
    observer = timing_class()()
    failure = ValueError("unchanged failure")
    def fail(value):
        assert value == "unrecorded argument"
        raise failure
    with pytest.raises(ValueError) as caught:
        observer._observe(fail, "offline_failure")("unrecorded argument")
    assert caught.value is failure
    snapshot = observer.snapshot()
    assert snapshot["records"][0]["returned"] is False
    assert "unrecorded argument" not in str(snapshot)


def test_controller_uses_existing_runner_observer_error_boundary(tmp_path):
    path = Path(__file__).resolve().parents[2] / "output/verification/cfg-processing-alignment-v9-20261102/controller-template.py"
    parsed = ast.parse(path.read_text(encoding="utf-8"))
    function = next(node for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef) and node.name == "progress")
    def closed_output(*args, **kwargs):
        raise OSError("observational stdout is unavailable")
    scope = {"RUN": tmp_path, "json": json, "stamp": lambda: "test", "print": closed_output}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), scope)
    state = {"stage": "propagation", "stages": {"propagation": {"status": "running"}}}
    # The caller's existing observer boundary is exercised by the first test.
    # The callback itself does not introduce a redundant error mechanism.
    with pytest.raises(OSError):
        scope["progress"](state)
    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt("user stopped")
    scope["print"] = interrupt
    with pytest.raises(KeyboardInterrupt):
        scope["progress"](state)
