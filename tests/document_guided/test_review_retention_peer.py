"""Independent regressions for source-review delivery-retention boundaries."""
import json

from skillflow.common.llm.request_errors import InputTooLarge
from skillflow.common.recording import read_json, sha_file
from skillflow.document_guided.source_review import replay_saved_review
from tests.document_guided.test_review_delivery_retention import (
    Client, partial_fixture, producer, run,
)


def test_normalized_complete_prior_response_remains_retainable(tmp_path):
    values, material, initial, missing = partial_fixture()

    class ExtraCloserClient(Client):
        def complete(self, prompt):
            response = super().complete(prompt)
            return response + "}"

    client = ExtraCloserClient(initial, InputTooLarge("The complete correction was rejected before delivery."))
    result = run(tmp_path, values, material, client)
    assert result["status"] == "partial"
    assert result["request_failure"]["error_type"] == "InputTooLarge"
    assert result["validation"]["candidate"] == initial
    assert result["review"]["input_contract_checks"] == initial["input_contract_checks"]
    assert any(row["obligation_id"] == missing["obligation_id"] and row["status"] != "accepted"
               for row in result["validation"]["contract_coverage"])
    assert read_json(tmp_path / "calls/review/a001/response.json") == json.dumps(initial) + "}"
    normalization = "calls/review/a001/normalization.json"
    assert result["delivery_retention"]["artifacts"][normalization] == sha_file(tmp_path / normalization)
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert replay_saved_review(tmp_path) == result
    assert before == {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert len(client.prompts) == 2
