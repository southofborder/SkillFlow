"""A saved step boundary resumes without another model completion."""
from copy import deepcopy

from skillflow.document_guided import runner
from tests.document_guided.test_parallel_recovery import cfg_wire


class Client:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def complete(self, prompt):
        self.calls += 1
        return deepcopy(self.value)


def test_accepted_document_boundary_recovers_and_replays_without_dispatch(tmp_path, monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_bytes(b"Return the original input value.\r\n")
    span = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "The source explicitly requires the original value."}
    task = {"purpose": {"text": "Return the original value.", "evidences": [span]},
            "requirements": [{"id": "R1", "text": "Return the original value.", "evidences": [span]}],
            "issues": []}
    clients = {"task": Client(task),
               "flow": Client("# Flow\nRead the input and return it unchanged. See skill/SKILL.md:1-1.\n"),
               "graph": Client(cfg_wire())}
    run = tmp_path / "run"
    runner.prepare(package, run_dir=run)

    def stop_after(name):
        def progress(result):
            if result["stage"] == name and result["stages"][name]["status"] == "complete":
                raise KeyboardInterrupt("Stopped after accepted " + name)
        return progress

    factory = lambda name, owner: clients[name]
    first = runner.run(run, client_factory=factory, progress=stop_after("flow"))
    assert first["status"] == "interrupted", first
    assert first["stage"] == "flow"
    assert clients["task"].calls == clients["flow"].calls == 1
    saved = {path: path.read_bytes() for path in run.rglob("response.json")}
    assert runner.replay(run) == first
    assert all(path.read_bytes() == value for path, value in saved.items())
    assert clients["task"].calls == clients["flow"].calls == 1
    second = runner.run(run, client_factory=factory, progress=stop_after("graph"))
    assert second["status"] == "interrupted", second
    assert second["stage"] == "graph"
    assert {name: client.calls for name, client in clients.items()} == {"task": 1, "flow": 1, "graph": 1}
    assert second["counts"]["logical_calls"] == 3
    assert "annotation" not in second["stages"]
    assert not (run / "annotation/manifest.json").exists()
    assert runner.replay(run) == second
    assert all(path.read_bytes() == value for path, value in saved.items())
