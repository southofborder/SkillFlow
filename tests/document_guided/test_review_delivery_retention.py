"""Known-ended correction failures retain only bound, revalidated review records."""
from copy import deepcopy
import json

import pytest

from skillflow.common.llm.request_errors import InputTooLarge, ModelRequestFailure
from skillflow.common.recording import canonical_sha256, read_json, sha_file
from skillflow.document_guided.source_review import replay_saved_review, run_source_review
from tests.document_guided.test_source_review_locality import two_operations
from tests.doe.input_review_helpers import source_review_response


@pytest.fixture(autouse=True)
def producer(monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)


class Client:
    def __init__(self, initial, error):
        self.initial, self.error, self.prompts = initial, error, []

    def complete(self, prompt):
        self.prompts.append(prompt)
        if len(self.prompts) == 1:
            return json.dumps(self.initial)
        raise self.error


def run(directory, values, material, client):
    return run_source_review(directory, files=material["files"], task=values[1], cfg=values[0].cfg,
        annotation=values[2]["raw_annotation"], raw_annotation=values[2]["raw_annotation"],
        compiled=values[2]["compiled_annotation"], mapping=values[2]["mapping"],
        generation="fragment-v1", client=client)


def partial_fixture():
    values, material, _ = two_operations()
    candidate = source_review_response(material, [])
    missing = candidate["input_contract_checks"].pop()
    return values, material, candidate, missing


@pytest.mark.parametrize("error_type", [InputTooLarge, ModelRequestFailure])
def test_ended_correction_failure_retains_complete_prior_local_records_and_replays(tmp_path, error_type):
    values, material, initial, missing = partial_fixture()
    client = Client(initial, error_type("The complete correction request was rejected before a native start."))
    result = run(tmp_path, values, material, client)
    assert result["status"] == "partial" and result["diagnostic_only"]
    assert result["request_failure"]["error_type"] == error_type.__name__
    assert result["request_failure"]["failure_call"] == {"point": "call", "call": "calls/review/a002"}
    assert result["validation"]["candidate"] == initial
    assert result["review"]["input_contract_checks"] == initial["input_contract_checks"]
    assert any(row["obligation_id"] == missing["obligation_id"] and row["status"] != "accepted"
               for row in result["validation"]["contract_coverage"])
    assert result["counts"]["structural_corrections"] == 1 and len(client.prompts) == 2
    assert not (tmp_path / "calls/review/a002/response.json").exists()
    assert read_json(tmp_path / "calls/review/a001/response.json") == json.dumps(initial)
    assert read_json(tmp_path / "calls/review/a002/call.json")["status"] == "error"
    proof = result["delivery_retention"]
    assert proof["candidate_sha256"] == canonical_sha256(initial)
    assert proof["material_sha256"] == canonical_sha256(read_json(tmp_path / "inputs.json"))
    assert all(sha_file(tmp_path / name) == digest for name, digest in proof["artifacts"].items())
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert replay_saved_review(tmp_path) == result
    assert len(client.prompts) == 2
    assert before == {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


@pytest.mark.parametrize("defect", ["table_missing", "outcome", "array_type", "all_records_invalid"])
def test_incomplete_or_wholly_invalid_answer_is_not_retained(tmp_path, defect):
    values, material, candidate, _ = partial_fixture()
    if defect == "table_missing":
        candidate.pop("input_projection_checks")
    elif defect == "outcome":
        candidate["outcome"] = "unfinished"
    elif defect == "array_type":
        candidate["findings"] = None
    else:
        for check in candidate["input_contract_checks"]:
            check["evidences"][0]["file"] = "absent-source.md"
        candidate["input_projection_checks"] = []
    result = run(tmp_path, values, material, Client(candidate, InputTooLarge("Complete delivery exceeds the limit.")))
    assert result["status"] == "request_failure" and result["review"] is None
    assert "delivery_retention" not in result


@pytest.mark.parametrize("error", [RuntimeError("Unknown process state"), ValueError("Integrity mismatch")])
def test_unknown_state_or_integrity_error_never_becomes_local_retention(tmp_path, error):
    values, material, candidate, _ = partial_fixture()
    with pytest.raises(type(error), match=str(error)):
        run(tmp_path, values, material, Client(candidate, error))
    assert not (tmp_path / "result.json").exists()


def test_interruption_preserves_interrupted_state_without_retention(tmp_path):
    values, material, candidate, _ = partial_fixture()
    result = run(tmp_path, values, material, Client(candidate, KeyboardInterrupt()))
    assert result["status"] == "interrupted" and "delivery_retention" not in result


def test_correction_recording_failure_cannot_be_downgraded_to_local_retention(tmp_path):
    values, material, candidate, _ = partial_fixture()
    error = ModelRequestFailure("Request ended but its audit persistence failed.")
    error.recording_failed = True
    with pytest.raises(ModelRequestFailure):
        run(tmp_path, values, material, Client(candidate, error))
    assert not (tmp_path / "result.json").exists()


@pytest.mark.parametrize("artifact", ["calls/review/a001/response.json", "calls/review/a001/validation.json",
    "calls/review/a002/request.json", "calls/review/a002/transport.json", "inputs.json", "result.json"])
def test_retention_replay_rejects_tampered_binding_or_artifact(tmp_path, artifact):
    values, material, candidate, _ = partial_fixture()
    result = run(tmp_path, values, material, Client(candidate, InputTooLarge("Complete correction exceeds limit.")))
    assert result["status"] == "partial"
    path = tmp_path / artifact
    value = read_json(path)
    if isinstance(value, dict):
        value["tampered"] = True
    elif isinstance(value, list):
        value.append({"tampered": True})
    else:
        value += " Changed."
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises((ValueError, RuntimeError)):
        replay_saved_review(tmp_path)


def test_finite_correction_complete_merge_runs_whole_validator_and_zero_call_replay(tmp_path):
    values, material, initial, missing = partial_fixture()
    from tests.document_guided.test_typed_record_correction import TextClient
    client = TextClient(initial, {"replacements": [], "insertions": [missing]})
    result = run(tmp_path, values, material, client)
    assert result["status"] == "complete" and "delivery_retention" not in result
    assert len(result["review"]["input_contract_checks"]) == len(material["input_contract_inventory"]["obligations"])
    assert len(client.prompts) == 2 and result["counts"]["structural_corrections"] == 1
    assert replay_saved_review(tmp_path) == result


def test_incomplete_insertion_keeps_missing_scope_blocked_after_single_correction(tmp_path):
    values, material, initial, missing = partial_fixture()
    from tests.document_guided.test_typed_record_correction import TextClient
    client = TextClient(initial, {"replacements": [], "insertions": []})
    result = run(tmp_path, values, material, client)
    assert result["status"] == "partial"
    assert "delivery_retention" not in result
    assert any(row["code"] == "review_coverage" for row in result["validation"]["diagnostics"])
    assert result["review"]["input_contract_checks"] == initial["input_contract_checks"]
    assert len(client.prompts) == 2 and not (tmp_path / "calls/review/a003").exists()
    assert replay_saved_review(tmp_path) == result


def test_retained_delivery_review_seals_only_independent_doe_contract_scopes(tmp_path):
    from skillflow.doe.input_contract_review import (
        build_input_contract_review, checked_input_contract_review, reviewed_contract_scopes,
    )
    values, material, initial, missing = partial_fixture()
    client = Client(initial, InputTooLarge("The complete correction delivery was rejected."))
    result = run(tmp_path, values, material, client)
    saved_material = read_json(tmp_path / "inputs.json")
    receipt = build_input_contract_review(files=material["files"], cfg=values[0].cfg, annotation=values[2],
        review=result, review_material=saved_material)
    assert receipt["review_status"] == "partial" and not receipt["source_review_complete"]
    assert reviewed_contract_scopes(receipt, initial["input_contract_checks"][0]["contract_id"])["available"]
    assert not reviewed_contract_scopes(receipt, missing["contract_id"])["available"]
    assert checked_input_contract_review(receipt, files=material["files"], cfg=values[0].cfg, annotation=values[2]) == receipt
    assert result["request_failure"]["failure_call"]["call"] == "calls/review/a002"
    assert replay_saved_review(tmp_path) == result and len(client.prompts) == 2


@pytest.mark.parametrize("tamper_normalization", [False, True])
def test_auditable_prior_json_normalization_is_bound_and_replayed(tmp_path, tamper_normalization):
    values, material, initial, _ = partial_fixture()

    class NormalizedClient(Client):
        def complete(self, prompt):
            result = super().complete(prompt)
            return result + "}"

    client = NormalizedClient(initial, InputTooLarge("Complete correction delivery exceeds limit."))
    result = run(tmp_path, values, material, client)
    assert result["status"] == "partial" and result["validation"]["candidate"] == initial
    assert result["counts"]["json_normalizations"] == 1
    name = "calls/review/a001/normalization.json"
    assert result["delivery_retention"]["artifacts"][name] == sha_file(tmp_path / name)
    assert read_json(tmp_path / "calls/review/a001/response.json") == json.dumps(initial) + "}"
    if tamper_normalization:
        receipt = read_json(tmp_path / name)
        receipt["tampered"] = True
        (tmp_path / name).write_text(json.dumps(receipt), encoding="utf-8")
        with pytest.raises((ValueError, RuntimeError)):
            replay_saved_review(tmp_path)
    else:
        before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
        assert replay_saved_review(tmp_path) == result and len(client.prompts) == 2
        assert before == {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
