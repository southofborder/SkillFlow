"""Read-only admission of a recorded rejected answer under a new validator."""
import json
from pathlib import Path

import pytest

from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.document_guided.accepted_upstream import load_accepted_upstream
from skillflow.document_guided.revalidated_upstream import PATH
from skillflow.document_guided.runner import prepare_from_revalidated_graph


DONOR = (Path(__file__).resolve().parents[2] / "experiments/doe/runs" /
         "document-guided-google-search-outcome-dispatch-high-20261125-205306")


def read(path):
    return json.loads(path.read_bytes())


def test_graph_readmission_rejects_conflicting_owners_before_import(tmp_path):
    (tmp_path / "manifest.json").write_text('{"accepted_upstream": {}, "revalidated_upstream": {}}')
    with pytest.raises(ValueError, match="two upstream owners"):
        load_accepted_upstream(tmp_path)


@pytest.mark.skipif(not DONOR.is_dir(), reason="requires the preserved offline 205306 CLI capture")
def test_archived_graph_acceptance_is_source_bound_and_local(tmp_path):
    child = tmp_path / "new"
    first = DONOR / "steps/graph/calls/a001"
    historical_validation = sha_file(first / "validation.json")
    prepare_from_revalidated_graph(DONOR, run_dir=child)
    values = load_accepted_upstream(child)
    receipt = read(child / PATH)
    assert receipt["origin"]["graph_attempt"]["ordinal"] == 1
    assert receipt["origin"]["graph_attempt"]["validation"]["status"] == "structural_invalid"
    assert receipt["origin"]["original_graph_status"] == "structural_failure"
    assert receipt["origin"]["selected_original_calls"] == {"task": "calls/task/a001", "flow": "calls/a001", "graph": "calls/a001"}
    assert len(receipt["origin"]["cli_calls"]["graph"]) == 2
    assert values["task"]["value"] == read(DONOR / "task/task.json")
    assert values["flow"]["path"].read_bytes() == (DONOR / "steps/flow/result.json").read_bytes()
    assert values["graph"]["origin"] == "revalidated_upstream"
    assert canonical_sha256(values["graph"]["value"]) == "4190326130a2384ef551e9d543fffb5613eda785d0bc53c953be6242e969217f"
    assert not (child / "transport").exists() and not (child / "steps/graph").exists()
    assert not (DONOR / "selection.json").exists() and sha_file(first / "validation.json") == historical_validation
    # The original rejected correction remains part of the evidence even though a001 supplied the CFG.
    path = child / "inherited/steps/graph/calls/a002/validation.json"
    before = path.read_bytes()
    path.write_bytes(b"{}")
    with pytest.raises(ValueError):
        load_accepted_upstream(child)
    path.write_bytes(before)
    native = next((child / "inherited/transport/graph").glob("*/answer.txt"))
    native.write_bytes(b"replacement")
    with pytest.raises(ValueError, match="native CLI"):
        load_accepted_upstream(child)
