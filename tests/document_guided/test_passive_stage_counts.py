"""Observer availability must not decide acceptance of a genuine stage answer."""
from skillflow.document_guided import online


def test_missing_stage_counts_do_not_block_acceptance_loading_or_replay(tmp_path, monkeypatch):
    owner = tmp_path / "document"
    online.prepare_step(owner, "Return a short working document.", kind="document", max_corrections=1)
    original = online.chain_counts

    def unavailable(*args, **kwargs):
        raise OSError("Injected passive observer failure")

    class Client:
        calls = 0
        def complete(self, prompt):
            self.calls += 1
            return "# Document\nThe original source remains authoritative."

    client = Client()
    monkeypatch.setattr(online, "chain_counts", unavailable)
    accepted = online.run_step(owner, client=client)
    assert online.read(owner / "result.json")["counts"] == {"status": "unavailable"}
    monkeypatch.setattr(online, "chain_counts", original)
    assert online.load_step(owner) == accepted
    assert online.run_step(owner, replay=True) == accepted
    assert client.calls == 1
