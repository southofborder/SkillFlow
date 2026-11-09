from copy import deepcopy
import json

import pytest

from skillflow.document_guided.audit import BatchJournal, record_injected_request, replay_request


class Client:
    def __init__(self, response):
        self.response, self.calls = response, 0

    def complete(self, prompt):
        self.calls += 1
        return deepcopy(self.response)


def test_saved_request_recovery_and_replay_never_resend(tmp_path):
    client = Client("# Flow\nReturn the acquired value.")
    bindings = {"source": "frozen-source-identity", "ranges": [{"file": "s", "start_line": 1, "end_line": 1}]}
    first = record_injected_request(tmp_path, "prompt", bindings, client=client)
    assert client.calls == 1
    assert record_injected_request(tmp_path, "prompt", bindings, client=client) == first
    assert replay_request(tmp_path, "prompt", bindings) == first
    assert client.calls == 1
    with pytest.raises(ValueError):
        record_injected_request(tmp_path, "changed", bindings, client=client)
    assert client.calls == 1
    # Simulate interruption after durable transport acceptance but before the
    # outer call's final completion checkpoint. Recovery uses the saved response.
    call_path = tmp_path / "call" / "call.json"
    call = json.loads(call_path.read_text(encoding="utf-8"))
    call["status"] = "running"
    call.pop("response")
    call.pop("response_sha256")
    call_path.write_text(json.dumps(call), encoding="utf-8")
    assert record_injected_request(tmp_path, "prompt", bindings, client=client) == first
    assert client.calls == 1


def test_response_tamper_and_wrong_upstream_refused(tmp_path):
    client = Client({"text": "source-bound conclusion"})
    record_injected_request(tmp_path, "p", {"source": "one"}, client=client)
    with pytest.raises(ValueError):
        replay_request(tmp_path, "p", {"source": "two"})
    path = tmp_path / "call" / "call.json"
    call = json.loads(path.read_text(encoding="utf-8"))
    call["response"] = {"text": "changed"}
    path.write_text(json.dumps(call), encoding="utf-8")
    with pytest.raises(ValueError):
        replay_request(tmp_path, "p", {"source": "one"})


def test_local_batch_replacement_retains_other_revisions_and_rejects_stale_dependents(tmp_path):
    journal = BatchJournal(tmp_path, {"source": "one"})
    first = journal.accept("part_one", "graph", {"blocks": [], "edges": []})
    journal.accept("part_two", "graph", {"blocks": [], "edges": []})
    independent = journal.revisions()["part_two"]
    journal.accept("header", "graph_globals", {"entry_block_ref": "start"}, depends_on={"part_one": first})
    before = (tmp_path / "revisions" / (first + ".json")).read_bytes()
    replacement = {"blocks": [{"block_ref": "start", "block_name": "Start", "instructions": []}], "edges": []}
    new = journal.accept("part_one", "graph", replacement)
    assert journal.revisions()["part_two"] == independent
    assert (tmp_path / "revisions" / (first + ".json")).read_bytes() == before
    with pytest.raises(ValueError, match="replaced upstream"):
        journal.current()
    journal.accept("header", "graph_globals", {"entry_block_ref": "start"}, depends_on={"part_one": new})
    assert journal.current()["part_one"]["blocks"][0]["block_ref"] == "start"
    assert BatchJournal(tmp_path, {"source": "one"}).current() == journal.current()
    with pytest.raises(ValueError):
        BatchJournal(tmp_path, {"source": "another"})
    with pytest.raises(ValueError):
        journal.accept("../escape", "graph", replacement)


def test_invalid_batch_does_not_replace_accepted_selection(tmp_path):
    journal = BatchJournal(tmp_path, {})
    journal.accept("shared", "locations", {"locations": {}, "location_evidences": {}})
    before = journal.revisions()
    with pytest.raises(ValueError):
        journal.accept("shared", "locations", {"locations": {}, "location_evidences": {}, "extra": True})
    assert journal.revisions() == before


def test_saved_batches_recompose_same_final_cfg_without_api(tmp_path):
    from skillflow.document_guided.batches import combine_graph
    from tests.document_guided.test_batches import graph_batches
    header, batches = graph_batches()
    journal = BatchJournal(tmp_path, {"fixture": "independent source"})
    first = journal.accept("acquire", "graph", batches[0])
    second = journal.accept("return", "graph", batches[1])
    journal.accept("globals", "graph_globals", header, depends_on={"acquire": first, "return": second})
    stored = journal.current()
    candidate, compiled = combine_graph(stored["globals"], [stored["acquire"], stored["return"]])
    assert compiled.ok
    replay = BatchJournal(tmp_path, {"fixture": "independent source"}).current()
    again, recompiled = combine_graph(replay["globals"], [replay["acquire"], replay["return"]])
    assert again == candidate
    assert recompiled.model_dump(mode="json") == compiled.model_dump(mode="json")


def test_revision_from_different_frozen_inputs_is_rejected(tmp_path):
    import shutil
    first = BatchJournal(tmp_path / "first", {"source": "source-a"})
    second = BatchJournal(tmp_path / "second", {"source": "source-b"})
    first.accept("locations", "locations", {"locations": {}, "location_evidences": {}})
    # Even a valid response/revision must remain bound to its original inputs.
    shutil.copytree(tmp_path / "first/revisions", tmp_path / "second/revisions")
    shutil.copyfile(tmp_path / "first/selection.json", tmp_path / "second/selection.json")
    with pytest.raises(ValueError, match="different frozen inputs"):
        second.current()
    assert first.current()["locations"]["locations"] == {}
