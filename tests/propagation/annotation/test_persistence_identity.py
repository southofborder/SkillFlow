"""Saved projections preserve JSON types and check caller paths before resolution."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skillflow.common.recording import read_json
from skillflow.propagation.annotation import runner, loading
from tests.propagation.annotation.helpers import FakeClient
from tests.propagation.annotation.test_security_runner import setup_run, forbidden


@pytest.mark.parametrize("entry", ["verify_prepared", "run_annotation", "replay_run"])
def test_run_entry_checks_the_original_path_before_resolution(tmp_path, monkeypatch, entry):
    directory, _, _ = setup_run(tmp_path)
    original = directory.parent / "unresolved-parent" / ".." / directory.name
    seen = []
    def deny(value):
        seen.append(value)
        raise ValueError("Run references cannot follow links or reparse points")
    monkeypatch.setattr(runner, "checked_run_path", deny)
    with pytest.raises(ValueError, match="links"):
        getattr(runner, entry)(original)
    assert seen == [original]


@pytest.mark.parametrize("replacement", [0.0, False])
def test_compiled_operand_index_type_tampering_is_not_python_equality(tmp_path, monkeypatch, replacement):
    directory, _, _ = setup_run(tmp_path)
    client = FakeClient()
    assert runner.run_annotation(directory, client=client)["status"] == "complete"
    path = directory / "audit/compiled-response.json"
    compiled = read_json(path)
    reference = compiled["ir_semantics"]["ir_filter"]["events"][0]["atomic_ops"][0]["inputs"][0]
    assert reference == {"kind": "input", "index": 0}
    reference["index"] = replacement
    path.write_text(json.dumps(compiled), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    for operation in (lambda: runner.run_annotation(directory, client_factory=forbidden),
                      lambda: runner.replay_run(directory),
                      lambda: loading.load_annotation_run(directory)):
        with pytest.raises(ValueError, match="compilation material"):
            operation()
    assert before == (directory / "result.json").read_bytes()
    assert len(client.prompts) == 1
