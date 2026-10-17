from skillflow.propagation.contracts.references import cfg_instructions
"""Sidecar review calls are bounded, recoverable and isolated from upstream facts."""
from copy import deepcopy
import io
import json
from pathlib import Path
from threading import Event
import urllib.error

import pytest

from skillflow.propagation.review import runner
from skillflow.propagation.review.report import display_model
from skillflow.propagation.review.report import render_html
from skillflow.propagation.review.report import render_markdown
from skillflow.common.llm import LlmClient
from skillflow.common.llm import LlmConfig
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.propagation.annotation import runner as annotation_runner
from tests.propagation.annotation.helpers import FakeClient, graph
from tests.propagation.annotation.test_security_runner import setup_run


DELIMITER = "\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n"


def forbidden(*args, **kwargs):
    raise AssertionError("No online call or factory is allowed")


def material_from_prompt(prompt):
    from skillflow.common.structural_correction import CORRECTION_MARKER
    from tests.propagation.annotation.helpers import material_from_model_payload
    from skillflow.propagation.review.material import prepare_review_material
    value = json.JSONDecoder().raw_decode(prompt.split(CORRECTION_MARKER, 1)[0].split(DELIMITER, 1)[1])[0]
    return prepare_review_material(material_from_model_payload(value), value['raw_annotation'])


def response_for(material, *, finding=False):
    from tests.propagation.review.test_core import empty_response
    response = empty_response(material)
    if finding:
        target = next(t for t in material["target_index"] if t["pointer"] == "/ir_semantics/ir_read")
        response["findings"] = [{
            "domain": "annotation",
            "target_ids": [target["id"]],
            "explanation": "范围说明可能遗漏读取内容与回传值的区分，影响观察范围。",
            "evidences": [{"target": {"instruction_id": "ir_read", "path": []}, "reason": "The operation locates the read."}],
            "suggestion": "依据源文机制分别描述读取与回传范围。",
        }]
    return response


class ReviewClient:
    def __init__(self, transform=None):
        self.prompts = []
        self.transform = transform

    def complete(self, prompt):
        self.prompts.append(prompt)
        material = material_from_prompt(prompt)
        response = response_for(material)
        return self.transform(response, material) if self.transform else response


def prepared(tmp_path, *, config=None, raw_edit=None, metadata=None):
    upstream, _, _ = setup_run(tmp_path)
    assert annotation_runner.run_annotation(upstream, client=FakeClient())["status"] == "complete"
    raw = read_json(upstream / "audit/raw-annotation.json")
    candidate = raw_edit(raw) if raw_edit else None
    directory = tmp_path / "review"
    manifest = runner.prepare_run(upstream, run_dir=directory, config=config,
                                  raw_annotation=candidate, authored_metadata=metadata)
    return directory, upstream, manifest


def file_bytes(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


def test_single_call_resume_and_zero_api_replay_preserve_upstream(tmp_path, monkeypatch):
    directory, upstream, manifest = prepared(tmp_path)
    before = file_bytes(upstream)
    client = ReviewClient()
    result = runner.run_review(directory, client=client)
    assert result["status"] == "complete"
    assert result["summary"] == "no_material_issue"
    assert result["review"]["findings"] == []
    assert result["counts"]["logical_calls"] == len(client.prompts) == 1
    assert result["request_validation"]["transport"] == "injected"
    assert result["request_validation"]["observed"] is False
    assert manifest["config"]["response_format"] == "json_object"
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.run_review(directory, client_factory=forbidden) == result
    assert runner.replay_run(directory) == result
    assert before == file_bytes(upstream)
    assert (directory / "replay/report.html").is_file()


@pytest.mark.parametrize("kind", ["bad_json", "duplicate_key", "extra_brace", "quote", "coverage", "target"])
def test_invalid_response_is_corrected_and_replays_without_resending(tmp_path, monkeypatch, kind):
    directory, _, _ = prepared(tmp_path)
    attempts = 0
    def invalid(response, material):
        nonlocal attempts
        attempts += 1
        if attempts > 1:
            return response
        if kind == "bad_json":
            return "{invalid"
        if kind == "duplicate_key":
            return '{"outcome": "completed", "reviewed_ir_ids":[],"findings":[],"findings":[]}'
        if kind == "extra_brace":
            return json.dumps(response) + "}"
        if kind == "coverage":
            response["reviewed_ir_ids"].pop()
            return response
        response = response_for(material, finding=True)
        if kind == "quote":
            response["findings"][0]["evidences"][0]["quote"] = "NOT_IN_THE_GRAPH"
        else:
            response["findings"][0]["target_ids"] = ["ann_nonexistent"]
        return response
    client = ReviewClient(invalid)
    result = runner.run_review(directory, client=client)
    assert result["status"] == "complete", result
    assert result["summary"] == "no_material_issue"
    assert result["validation"]["status"] == "passed"
    assert result["counts"]["structural_corrections"] == (0 if kind == "extra_brace" else 1)
    assert result["counts"]["json_normalizations"] == int(kind == "extra_brace")
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.run_review(directory, client_factory=forbidden) == result
    assert runner.replay_run(directory) == result
    expected_calls = 1 if kind == "extra_brace" else 2
    assert len(client.prompts) == expected_calls
    assert result["response_chain"]["accepted_call"] == f"calls/review/a{expected_calls:03d}"


@pytest.mark.parametrize("stop_point", ["before", "after_acceptance", "progress"])
def test_interruption_recovery_never_resends_accepted_calls(tmp_path, monkeypatch, stop_point):
    directory, _, _ = prepared(tmp_path)
    stop = Event()
    if stop_point == "before":
        stop.set()
    class StopAfter(ReviewClient):
        def complete(self, prompt):
            value = super().complete(prompt)
            if stop_point == "after_acceptance":
                stop.set()
            return value
    client = StopAfter()
    progress = (lambda _: stop.set()) if stop_point == "progress" else None
    result = runner.run_review(directory, client=client, stop_event=stop, progress=progress)
    assert result["status"] == "interrupted"
    expected_calls = 1 if stop_point == "after_acceptance" else 0
    assert result["counts"]["logical_calls"] == len(client.prompts) == expected_calls
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.replay_run(directory) == result
    if expected_calls:
        monkeypatch.setattr(runner, "RecordingClient", forbidden)
        resumed = runner.run_review(directory, client_factory=forbidden)
        assert resumed["status"] == "complete"
        assert resumed["counts"]["logical_calls"] == 1
        assert runner.replay_run(directory) == resumed


@pytest.mark.parametrize("kind", ["error", "interrupt", "incomplete"])
def test_uncertain_request_never_falls_through_to_online_factory(tmp_path, monkeypatch, kind):
    directory, _, _ = prepared(tmp_path)
    class Failed:
        def complete(self, prompt):
            if kind == "interrupt":
                raise KeyboardInterrupt("用户中断")
            raise RuntimeError("Incomplete SSE response: missing termination" if kind == "incomplete" else "transport failure")
    result = runner.run_review(directory, client=Failed())
    assert result["status"] == ("interrupted" if kind == "interrupt" else "execution_error")
    assert result["summary"] is None
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.run_review(directory, client_factory=forbidden) == result
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("target", ["candidate", "material", "prompt", "upstream", "config", "implementation", "result"])
def test_changed_identity_refuses_without_network_or_result_overwrite(tmp_path, monkeypatch, target):
    directory, upstream, _ = prepared(tmp_path)
    result = runner.run_review(directory, client=ReviewClient())
    kwargs = {}
    if target == "candidate":
        (directory / "inputs/candidate.json").write_text("{}", encoding="utf-8")
    elif target == "material":
        path = directory / "inputs/observations.json"
        path.write_text("[]", encoding="utf-8")
    elif target == "prompt":
        (directory / "inputs/prompt.txt").write_text("changed", encoding="utf-8")
    elif target == "upstream":
        (upstream / "audit/raw-annotation.json").write_text("{}", encoding="utf-8")
    elif target == "config":
        kwargs["config"] = {"model": "changed-model"}
    elif target == "implementation":
        monkeypatch.setattr(runner, "implementation_provenance", lambda: {})
    elif target == "result":
        changed = deepcopy(result)
        changed["summary"] = "issues_found"
        (directory / "result.json").write_text(json.dumps(runner._seal(runner.result_snapshot(changed))), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    with pytest.raises(runner.RunIdentityError):
        runner.run_review(directory, client_factory=forbidden, **kwargs)
    assert (directory / "result.json").read_bytes() == before


def test_referenced_upstream_requires_unchanged_original_run(tmp_path, monkeypatch):
    directory, upstream, _ = prepared(tmp_path)
    (upstream / "result.json").write_text("changed after freeze", encoding="utf-8")
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    with pytest.raises(ValueError):
        runner.run_review(directory, client_factory=forbidden)
    assert not (directory / "inputs/upstream").exists()


def test_freezing_preserves_skill_files_named_like_generated_reports(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# 配置处理\n读取配置后在本地筛选字段。", encoding="utf-8")
    (source / "report.md").write_text("SOURCE_REPORT_CANARY", encoding="utf-8")
    (source / "replay").mkdir()
    (source / "replay/details.txt").write_text("SOURCE_REPLAY_CANARY", encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    upstream = tmp_path / "annotation"
    from tests.propagation.annotation.helpers import authored_prepare_run
    assert authored_prepare_run(source, analysis, run_dir=upstream)["preparation_status"] == "ready"
    assert annotation_runner.run_annotation(upstream, client=FakeClient())["status"] == "complete"
    directory = tmp_path / "review"
    runner.prepare_run(upstream, run_dir=directory)
    client = ReviewClient()
    assert runner.run_review(directory, client=client)["status"] == "complete"
    assert "SOURCE_REPORT_CANARY" in client.prompts[0]
    assert "SOURCE_REPLAY_CANARY" in client.prompts[0]


def test_authored_metadata_and_upstream_opinions_never_enter_prompt(tmp_path):
    def edit(raw):
        raw["ir_semantics"]["ir_read"]["operator_evidences"][0]["reason"] = "根据当前获取动作描述进行判断。"
        return raw
    directory, upstream, manifest = prepared(
        tmp_path, raw_edit=edit,
        metadata={"mutation": "EXTERNAL_COUNTEREXAMPLE_CANARY", "expected": "EXTERNAL_ANSWER_CANARY"})
    client = ReviewClient()
    result = runner.run_review(directory, client=client)
    prompt = client.prompts[0]
    assert result["status"] == "complete"
    assert "EXTERNAL_COUNTEREXAMPLE_CANARY" not in prompt and "EXTERNAL_ANSWER_CANARY" not in prompt
    assert "OLD_CANDIDATE_CANARY" not in prompt and "OLD_REVIEW_CANARY" not in prompt
    assert manifest["candidate_origin"] == "authored_candidate"
    accepted = read_json(upstream / "audit/raw-annotation.json")
    candidate = read_json(directory / "inputs/candidate.json")
    assert accepted != candidate
    assert not (directory / "inputs/upstream").exists()
    assert read_json(upstream / "audit/raw-annotation.json") == accepted
    assert material_from_prompt(prompt)["raw_annotation"] == candidate


def test_prompt_credential_overlap_is_local_error_and_replays_without_api(tmp_path, monkeypatch):
    directory, _, _ = prepared(tmp_path)
    result = runner.run_review(directory, client_factory=forbidden, secrets=("配置处理",))
    assert result["status"] == "input_error"
    assert result["counts"]["logical_calls"] == 0
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.replay_run(directory) == result


def test_response_secret_is_rejected_redacted_and_not_resent(tmp_path, monkeypatch):
    directory, _, _ = prepared(tmp_path)
    secret = "test-review-response-secret-1234567"
    def overlap(response, material):
        response = response_for(material, finding=True)
        response["findings"][0]["explanation"] = secret
        return response
    client = ReviewClient(overlap)
    result = runner.run_review(directory, client=client, secrets=(secret,))
    assert result["status"] == "execution_error"
    assert all(secret.encode() not in raw for raw in file_bytes(directory).values())
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.run_review(directory, client_factory=forbidden, secrets=(secret,)) == result
    assert runner.replay_run(directory) == result
    assert len(client.prompts) == 1


def run_http(tmp_path, monkeypatch, kind="valid"):
    config = {"model": "offline-review-model", "reasoning_effort": "high"}
    directory, _, _ = prepared(tmp_path, config=config)
    sent = []
    class Response:
        status = 200
        headers = {}
        def __init__(self, payload):
            self.payload = json.dumps(payload).encode()
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return self.payload
    def request(req, timeout):
        payload = json.loads(req.data)
        sent.append(payload)
        if kind == "unsupported":
            raise urllib.error.HTTPError(req.full_url, 400, "unsupported", {}, io.BytesIO(b"response_format unsupported"))
        response = response_for(material_from_prompt(payload["messages"][0]["content"]))
        content = json.dumps(response) + ("}" if kind == "extra_brace" and len(sent) == 1 else "")
        return Response({"model": "offline-review-returned", "choices": [{
            "finish_reason": "length" if kind == "truncated" else "stop", "message": {"content": content}}]})
    monkeypatch.setattr("urllib.request.urlopen", request)
    factory = lambda writer, checkpoint: LlmClient(
        LlmConfig(api_key="offline-secret", **runner._config(config)), record_calls=True, on_record=checkpoint)
    result = runner.run_review(directory, client_factory=factory, config=config)
    return directory, result, sent


@pytest.mark.parametrize("kind,status,error_kind", [
    ("valid", "complete", None), ("extra_brace", "complete", None),
    ("truncated", "execution_error", "output_truncated"), ("unsupported", "execution_error", "execution"),
])
def test_json_output_actual_request_and_failure_replay(tmp_path, monkeypatch, kind, status, error_kind):
    directory, result, sent = run_http(tmp_path, monkeypatch, kind)
    assert result["status"] == status, result["reason"]
    assert result["error_kind"] == error_kind
    expected_calls = 1
    assert result["counts"]["json_normalizations"] == int(kind == "extra_brace")
    assert len(sent) == expected_calls
    assert sent[0]["response_format"] == {"type": "json_object"}
    assert result["request_validation"]["observed"] is True
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    assert runner.replay_run(directory) == result
    assert len(sent) == expected_calls


@pytest.mark.parametrize("change", ["missing_parameter", "altered_hash", "saved_validation"])
def test_http_request_identity_cannot_be_resealed_to_bypass_replay(tmp_path, monkeypatch, change):
    directory, result, _ = run_http(tmp_path, monkeypatch)
    if change == "saved_validation":
        result["request_validation"]["observed"] = False
        (directory / "result.json").write_text(json.dumps(runner._seal(runner.result_snapshot(result))), encoding="utf-8")
    else:
        path = directory / runner.CALL_PATH / "transport.json"
        trace = read_json(path)
        attempt = trace[0]["http_attempts"][0]
        if change == "missing_parameter":
            attempt["request_parameters"].pop("response_format")
        else:
            attempt["request_body_sha256"] = "0" * 64
        trace[0].pop("record_sha256")
        trace[0]["record_sha256"] = canonical_sha256(trace[0])
        path.write_text(json.dumps(trace), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    with pytest.raises(runner.RunIdentityError):
        runner.replay_run(directory)
    assert before == (directory / "result.json").read_bytes()


def test_report_escapes_html_and_preserves_finding_order(tmp_path):
    directory, _, _ = prepared(tmp_path)
    def findings(response, material):
        first = response_for(material, finding=True)["findings"][0]
        first["explanation"] = '<script>alert("x")</script> & 原始值'
        second = deepcopy(first)
        second.update(suggestion="保留已知顺序。", explanation="已知顺序被颠倒。")
        return {**response, "findings": [first, second]}
    result = runner.run_review(directory, client=ReviewClient(findings))
    assert result["status"] == "complete"
    material = runner.load_prepared_review_material(directory)
    model = display_model(result, material)
    html, markdown = render_html(model), render_markdown(model)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert html.index("F001") < html.index("F002")
    assert markdown.index("F001") < markdown.index("F002")
    assert "<b>Material issues found</b>" in html


def test_offline_replay_rejects_client_injection(tmp_path):
    directory, _, _ = prepared(tmp_path)
    with pytest.raises(ValueError, match="Offline"):
        runner.run_review(directory, replay=True, client=ReviewClient())
