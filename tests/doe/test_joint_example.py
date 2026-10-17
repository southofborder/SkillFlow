"""The public example is independent, executable and transparently authored."""
import socket

from examples.doe.joint_analysis_demo import build_example


def test_synthetic_example_preserves_original_field_demand(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline example must not contact a model")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    material, raw, facts, result = build_example()
    assert material["user_request"] is None
    assert raw["demands"][0]["target"] == {
        "instruction_id": "ir_sample_return", "side": "input", "index": 0}
    assert raw["demands"][0]["preserve"] == "value"
    assert result["status"] == "complete"
    assert len(result["sinks"]) == len(facts.sinks)
    assert all(review["conclusion"] == "excess_supported"
               for sink in result["sinks"] for review in sink["data_reviews"])
    assert {value["label"] for value in result["derivations"]["sensitivity"].values()} == {"confidential_identifier"}
