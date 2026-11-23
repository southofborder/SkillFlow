"""A donor's immutable proof and a receiving installation's independent proof."""
from copy import deepcopy
import hashlib
import json

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.graph.audit import controlled
from skillflow.graph.audit.evidence import canonical_graph_sha256
from tests.graph.audit.test_evidence import example_cfg


@pytest.fixture
def proofs(monkeypatch):
    # Isolate receipt validation from native execution. test_controlled.py
    # separately exercises the real Lean round trip for two producer identities.
    sources = {"formal/ControlledMain.lean": "a" * 64}
    original = {"schema_version": 2, "method": "controlled", "text": "example",
                "graph_sha256": "c" * 64, "units": [], "derived_links": [],
                "certificate": {"checks": {"actual_text_parsed": True},
                                "source_files": sources, "source_sha256": canonical_graph_sha256(sources),
                                "binary_sha256": "b" * 64}}
    local = deepcopy(original)
    new_sources = {"formal/ControlledMain.lean": "d" * 64}
    local["certificate"].update(binary_sha256="e" * 64, source_files=new_sources,
                                source_sha256=canonical_graph_sha256(new_sources))
    monkeypatch.setattr(controlled, "render_controlled", lambda cfg, executable: local)
    return original, local


def encode(value):
    raw = json.dumps(value).encode("utf-8")
    return raw, hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("field,value", [
    ("text", "altered"), ("units", ["altered"]), ("derived_links", ["altered"]),
    ("graph_sha256", "1" * 64), ("certificate.checks", {"actual_text_parsed": 1}),
    ("certificate.source_sha256", "0" * 64), ("certificate.binary_sha256", "invalid"),
])
def test_recertification_rejects_divergence_even_with_matching_donor_digest(proofs, field, value):
    old, _ = proofs
    if field.startswith("certificate."):
        old["certificate"][field.split(".")[1]] = value
    else:
        old[field] = value
    raw, digest = encode(old)
    with pytest.raises(controlled.ControlledVerificationError):
        controlled.recertify_inherited(raw, expected_sha256=digest, cfg=example_cfg())


def test_inherited_receipt_binds_both_producers_and_never_repairs_on_replay(tmp_path, proofs):
    old, local = proofs
    raw, digest = encode(old)
    target = tmp_path / "graph/initial/controlled.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(raw)
    receipt = target.with_name("local-verification.json")
    origin = {"path": "inherited/graph/revision/controlled.json", "sha256": digest}
    graph = json.loads(example_cfg().to_json())
    with pytest.raises(ValueError, match="Missing local graph verification"):
        runner._certificate(tmp_path, "initial", graph, True, None, origin)
    runner._certificate(tmp_path, "initial", graph, False, None, origin)
    accepted = read(receipt)
    assert accepted["inherited_document"] == origin
    assert accepted["local_certificate"] == local["certificate"]
    runner._certificate(tmp_path, "initial", graph, True, None, origin)
    assert target.read_bytes() == raw
    accepted["local_certificate"]["checks"]["actual_text_parsed"] = 1
    runner.WRITER.json(receipt, accepted)
    with pytest.raises(ValueError, match="receipt differs"):
        runner._certificate(tmp_path, "initial", graph, True, None, origin)
    with pytest.raises(ValueError, match="bound upstream bytes"):
        runner._certificate(tmp_path, "initial", graph, False, None, {**origin, "sha256": "0" * 64})


def test_fatal_processing_replay_requires_real_local_proof(tmp_path, monkeypatch):
    from tests.document_guided.test_accepted_upstream import Downstream, parent_run
    from tests.document_guided.test_parallel_runner import freeze_producer

    freeze_producer(monkeypatch)
    donor = parent_run(tmp_path)
    child = Downstream(tmp_path / "child", fail_processing=True)
    runner.prepare_from_accepted_cfg(donor.directory, run_dir=child.directory)
    result = runner.run(child.directory, client_factory=child.factory)
    assert result["status"] == "failed" and result["stage"] == "processing"
    assert result["fatal_frontier"] and runner.replay(child.directory) == result
    receipt = child.directory / "graph/initial/local-verification.json"
    value = read(receipt)
    value["local_certificate"]["binary_sha256"] = "0" * 64
    runner.WRITER.json(receipt, value)
    with pytest.raises(ValueError, match="receipt differs"):
        runner.replay(child.directory)
    receipt.unlink()
    with pytest.raises(ValueError, match="Missing local graph verification"):
        runner.run(child.directory, client_factory=child.factory)
    assert not receipt.exists() and child.calls == ["processing"]
    assert read(child.directory / "result.json") == result
