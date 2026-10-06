"""Real compiler and Lean conversion; synthetic audits test orchestration only."""
from copy import deepcopy
import hashlib
import json
from threading import Event

import pytest

from skillflow.graph.feedback import runner
from skillflow.graph.extraction.pipeline import analyze_skill
from skillflow.common.inputs.skill_package import load_skill_package
from skillflow.graph.semantic_contract import CONTRACT_VERSION
from skillflow.graph.semantic_contract import contract_binding


def candidate(value="ok"):
    return {"entry_block_ref": "finish", "blocks": [{"block_ref": "finish", "block_name": "结束",
            "instructions": [{"instruction_ref": "return_value", "opcode": "return",
                              "inputs": [{"type": "literal", "literal_value": value}]}]}], "edges": []}


def answer(prompt, status="represented", *, kind="semantic", marker="current-difference"):
    data = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
    files = {f["path"]: f["content"].splitlines() for f in data["source_files"]}
    refs = [{"unit_id": u["id"], "file": u["file"], "start_line": u["start_line"], "end_line": u["end_line"],
             "quote": "\n".join(files[u["file"]][u["start_line"]-1:u["end_line"]])} for u in data["source_units"]]
    controlled = data["required_coverage"]["reviewed_controlled_unit_ids"]
    finding = {"id": marker, "kind": kind, "status": status, "source_requirement": "返回 ok。",
               "actual_representation": "工程协议测试记录，不是语义答案。", "reason": marker,
               "source_refs": refs, "controlled_refs": [{"unit_id": key} for key in controlled],
               "basis": ["explicit_graph"], "suggestions": []}
    if status in {"omitted", "mistranslated", "unsupported_addition", "internal_conflict"}:
        finding["suggestions"] = [{"target_ids": [controlled[-1]], "change": marker, "reason": "依源文修正"}]
    if status == "cannot_assess":
        return {"schema_version": 5, "contract_version": CONTRACT_VERSION, "outcome": "cannot_assess",
                "failure": {"reason": "源文在必要返回要求上相互冲突。", "source_refs": refs,
                            "controlled_refs": [{"unit_id": key} for key in controlled]}}
    return {"schema_version": 5, "outcome": "completed", "contract_version": CONTRACT_VERSION,
            "findings": [finding], **data["required_coverage"], "notes": []}


class Client:
    def __init__(self, responses):
        self.responses, self.prompts = iter(responses), []

    def complete(self, prompt):
        self.prompts.append(prompt)
        result = next(self.responses)
        if isinstance(result, BaseException):
            raise result
        return result(prompt) if callable(result) else deepcopy(result)


@pytest.fixture
def material(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_bytes("# 样例\n\n返回 ok。\n".encode())
    cfg = analyze_skill(source, candidate=candidate()).cfg
    seed = tmp_path / "analysis.json"
    seed.write_text(json.dumps({"cfg": cfg.model_dump(mode="json"), "raw_candidate": "DO-NOT-USE-STALE"}), encoding="utf-8")
    return source, seed, tmp_path / "run"


def execute(material, statuses, extractions=(), **kwargs):
    source, seed, directory = material
    audits = Client([lambda p, s=s: answer(p, s) for s in statuses])
    extraction = Client(extractions)
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 audit_client=audits, extraction_client=extraction, **kwargs)
    return result, audits, extraction


def test_initial_pass_and_offline_replay_with_no_api(material, monkeypatch):
    result, audits, extraction = execute(material, ["represented"])
    assert result["status"] == "audit_passed", result["reason"]
    assert result["counts"]["semantic_revisions"] == 0
    assert len(audits.prompts) == 1 and not extraction.prompts
    assert result["passed_cfg"] == result["last_valid_cfg"]
    assert result["representation_summary"] == {"represented_ids": ["current-difference"], "conservative_ids": []}
    assert result["schema_version"] == 5 and result["identity"] == "skill-ir-semantic-feedback-v5"
    def no_api(*args, **kwargs):
        pytest.fail("replay creates no online client")
    monkeypatch.setattr(runner, "RecordingClient", no_api)
    monkeypatch.setattr(runner, "injected_factory", no_api)
    assert runner.replay_run(material[2]) == result


def test_valid_conservative_audit_passes_zero_revision_and_is_reported(material):
    from skillflow.graph.audit.controlled import render_controlled
    from skillflow.graph.audit.evidence import normalize_cfg
    from skillflow.graph.extraction.prompt import _EXAMPLES
    source, seed, directory = material
    # Use the production contract's real branch/merge example. The two
    # candidates are distinct branch-produced results, never literal inputs.
    raw = deepcopy(_EXAMPLES[1][1])
    (source / "SKILL.md").write_text(
        "# 合成分支样例\n\n读取消息；紧急时发送提醒并取得回执，否则生成无需提醒的说明。"
        "最后根据实际执行分支的结果组织并返回消息。\n", encoding="utf-8")
    cfg = analyze_skill(source, candidate=raw).cfg
    assert cfg is not None
    seed.write_text(json.dumps({"cfg": normalize_cfg(cfg)}), encoding="utf-8")
    document = render_controlled(cfg)
    merge_block, position, merge = next(
        (block_id, position, instruction)
        for block_id, block in cfg.blocks.items()
        for position, instruction in enumerate(block.instructions)
        if instruction.opcode == "format_alert_outcome")
    assert all(operand.type.value == "result" for operand in merge.inputs[1:])
    assert len({operand.identifier for operand in merge.inputs[1:]}) == 2
    locations = {f"/blocks/{merge_block}/instructions/{position}/inputs/{index}" for index in (1, 2)}
    ids = [unit["id"] for unit in document["units"]
           if len(unit["graph_refs"]) == 1 and unit["graph_refs"][0] in locations
           and not unit["id"].endswith(":link")]
    assert len(ids) == 2

    def conservative(prompt):
        value = answer(prompt)
        value["findings"][0].update(conservative={
            "rule_id": "DEP-MERGE", "candidate_fact_ids": ids,
            "lost_distinctions": ["合成样例用于验证记录传播，不主张业务语义正确。"],
            "reason": "工程协议测试"})
        return value

    extraction, audits = Client([]), Client([conservative])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 extraction_client=extraction, audit_client=audits)
    assert result["status"] == "audit_passed", result["reason"]
    assert not extraction.prompts and len(audits.prompts) == 1
    assert result["representation_summary"] == {"represented_ids": ["current-difference"], "conservative_ids": ["current-difference"]}
    assert result["contract_sha256"] == contract_binding()["contract_sha256"]
    assert "保守规则" in (directory / "report.md").read_text(encoding="utf-8")
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("missing", ["contract_version", "status", "source_refs"])
def test_missing_essential_audit_contract_is_execution_error_without_retry(material, missing):
    def invalid(prompt):
        response = answer(prompt)
        if missing == "contract_version":
            response.pop(missing)
        else:
            response["findings"][0].pop(missing)
        return response
    source, seed, directory = material
    client = Client([invalid])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=client)
    assert result["status"] == "audit_error" and result["passed_cfg"] is None
    assert len(client.prompts) == 1
    assert result["representation_summary"] == {"represented_ids": [], "conservative_ids": []}


@pytest.mark.parametrize("version", [1, 2, 3])
def test_old_feedback_records_are_not_reinterpreted(material, version):
    directory = material[2]
    directory.mkdir()
    (directory / "manifest.json").write_text(
        json.dumps({"schema_version": version, "identity": f"skill-ir-semantic-feedback-v{version}"}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        runner.replay_run(directory)


def test_one_revision_is_full_candidate_reextraction_and_isolated(material):
    result, audits, extraction = execute(material, ["mistranslated", "represented"], [candidate()])
    assert result["status"] == "audit_passed", result["reason"]
    assert result["counts"]["semantic_revisions"] == 1
    assert len(extraction.prompts) == 1 and len(audits.prompts) == 2
    assert '"previous_cfg"' in extraction.prompts[0]
    assert "DO-NOT-USE-STALE" not in extraction.prompts[0]
    sources = []
    for prompt in audits.prompts:
        assert "current-difference" not in prompt and '"previous_cfg"' not in prompt
        data = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
        assert set(data) == {"source_files", "source_line_index", "source_units", "controlled_text", "controlled_units", "required_coverage"}
        sources.append(data["source_files"])
    assert sources[0] == sources[1]
    assert runner.replay_run(material[2]) == result


def test_three_revisions_and_structural_repairs_count_separately(material):
    attempts = [value for _ in range(3) for value in ("bad", "bad", "bad", candidate())]
    result, audits, extraction = execute(material, ["omitted"] * 4, attempts)
    assert result["status"] == "revision_limit", result["reason"]
    assert result["counts"]["extraction_logical_calls"] == len(extraction.prompts) == 12
    assert result["counts"]["audit_logical_calls"] == len(audits.prompts) == 4
    assert result["counts"]["structural_repairs"] == 9
    assert result["counts"]["semantic_revisions"] == 3
    assert result["counts"]["http_attempts"] == 0
    assert result["counts"]["http_attempts_observed"] is False
    assert result["passed_cfg"] is None


@pytest.mark.parametrize("status,expected", [("cannot_assess", "semantic_failure"), ("omitted", "revision_limit")])
def test_unknown_and_budget_zero_stop(material, status, expected):
    result, _, extraction = execute(material, [status], max_semantic_revisions=0)
    assert result["status"] == expected and not extraction.prompts


def test_all_background_is_not_semantic_pass(material):
    source, seed, directory = material
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 audit_client=Client([lambda p: answer(p, kind="context")]))
    assert result["status"] == "semantic_failure" and result["passed_cfg"] is None


@pytest.mark.parametrize("failure", ["json", "quote", "coverage", "unknown_id"])
def test_invalid_audit_is_execution_error_not_revision_or_pass(material, failure):
    def invalid(prompt):
        value = answer(prompt)
        if failure == "json": return "broken JSON"
        if failure == "quote": value["findings"][0]["source_refs"][0]["quote"] = "nonexistent"
        if failure == "coverage": value["reviewed_source_unit_ids"] = []
        if failure == "unknown_id": value["findings"][0]["controlled_refs"][0]["unit_id"] = "NO-SUCH-ID"
        return value
    source, seed, directory = material
    audit = Client([invalid])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=audit)
    assert result["status"] == "audit_error" and result["passed_cfg"] is None
    assert result["counts"]["total_logical_calls"] == 1


def test_fidelity_failure_before_any_audit(material):
    result, audits, _ = execute(material, ["represented"], renderer=material[2].parent / "missing.exe")
    assert result["status"] == "fidelity_error" and not audits.prompts


def test_extraction_exhaustion_preserves_last_valid_graph(material):
    result, audits, extraction = execute(material, ["omitted"], ["bad"] * 4)
    assert result["status"] == "extraction_error", result["reason"]
    assert len(extraction.prompts) == 4 and len(audits.prompts) == 1
    assert result["last_valid_cfg"] is not None and result["passed_cfg"] is None


def test_source_start_default_prompt_has_extra_initial_generation(material):
    source, _, directory = material
    result = runner.refine_skill(source, run_dir=directory, extraction_client=Client([candidate()]),
                                 audit_client=Client([answer]))
    assert result["status"] == "audit_passed", result["reason"]
    assert result["limits"]["logical_call_bounds"] == {"extraction": 16, "audit": 4, "total": 20}
    assert result["counts"]["extraction_logical_calls"] == 1


def test_new_error_after_fix_gets_full_second_feedback_and_only_latest(material):
    source, seed, directory = material
    audits = Client([lambda p: answer(p, "omitted", marker="old-error-marker"),
                     lambda p: answer(p, "unsupported_addition", marker="new-error-marker"), answer])
    extraction = Client([candidate("first-fix"), candidate()])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 extraction_client=extraction, audit_client=audits)
    assert result["status"] == "audit_passed", result["reason"]
    assert result["counts"]["semantic_revisions"] == 2
    assert "new-error-marker" in extraction.prompts[1]
    assert "old-error-marker" not in extraction.prompts[1]
    for prompt in audits.prompts:
        assert "old-error-marker" not in prompt and "new-error-marker" not in prompt


def test_explicit_difference_then_semantic_failure_stops_without_more_repair(material):
    source, seed, directory = material
    extraction = Client([candidate()])
    audit = Client([lambda p: answer(p, "omitted"), lambda p: answer(p, "cannot_assess")])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 extraction_client=extraction, audit_client=audit)
    assert result["status"] == "semantic_failure", result["reason"]
    assert result["passed_cfg"] is None and len(extraction.prompts) == 1 and len(audit.prompts) == 2
    assert '"unknown_reminders"' not in extraction.prompts[0]
    assert (directory / "rounds/r001/semantic-failure.json").is_file()
    assert runner.replay_run(directory) == result


def test_accepted_response_then_interrupt_recovery_never_resends(material):
    source, seed, directory = material
    calls = []
    def factory(writer, checkpoint):
        class Accepted:
            def complete(self, prompt):
                calls.append(prompt)
                checkpoint([{"status": "complete", "prompt": prompt, "response": answer(prompt), "http_attempts": [{"http_status": 200}]}])
                raise KeyboardInterrupt("after accepted response persisted")
        return Accepted()
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert result["status"] == "interrupted" and len(calls) == 1
    restored = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert restored["status"] == "audit_passed" and len(calls) == 1
    assert runner.replay_run(directory) == restored


def test_uncertain_failure_never_resent(material):
    source, seed, directory = material
    audit = Client([RuntimeError("accepted but incomplete")])
    first = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=audit)
    second = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=audit)
    assert first == second and first["status"] == "audit_error"
    assert len(audit.prompts) == 1
    assert runner.replay_run(directory) == first


@pytest.mark.parametrize("changed", ["source", "snapshot", "config", "code", "initial", "contract"])
def test_resume_refuses_identity_changes(material, monkeypatch, changed):
    execute(material, ["represented"])
    source, seed, directory = material
    options = {}
    if changed == "source": (source / "SKILL.md").write_text("changed", encoding="utf-8")
    if changed == "snapshot": (directory / "inputs/package/SKILL.md").write_text("changed", encoding="utf-8")
    if changed == "initial": seed.write_text("{}", encoding="utf-8")
    if changed == "config": options["config"] = {"model": "other"}
    if changed == "code": monkeypatch.setattr(runner, "implementation_provenance", lambda: {})
    if changed == "contract": monkeypatch.setattr(runner, "contract_binding", lambda: {
        **contract_binding(), "contract_sha256": "changed-contract"})
    with pytest.raises(ValueError, match="changed|identity"):
        runner.refine_skill(source, run_dir=directory, initial_analysis=seed, **options)


def test_controlled_text_tamper_prevents_audit_even_with_saved_response(material):
    execute(material, ["represented"])
    path = material[2] / "rounds/r000/controlled.txt"
    path.write_bytes(path.read_bytes() + b"changed")
    replay = runner.replay_run(material[2])
    assert replay["status"] == "fidelity_error" and replay["passed_cfg"] is None
    assert replay["counts"]["audit_logical_calls"] == 0


def test_interrupted_before_start_and_old_run_rejected(material):
    source, seed, directory = material
    stopped = Event(); stopped.set()
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, stop_event=stopped)
    assert result["status"] == "interrupted" and result["counts"]["total_logical_calls"] == 0
    other = directory.parent / "old"; other.mkdir()
    (other / "manifest.json").write_text('{"schema_version":2,"identity":"skill-ir-controlled-source-audit-v2"}')
    with pytest.raises(ValueError, match="Unsupported"):
        runner.replay_run(other)


def test_explicit_json_audit_records_request_identity_without_changing_extraction(material, monkeypatch):
    config = {"extraction": {}, "audit": {"response_format": "json_object"}}
    result, audits, extraction = execute(material, ["represented"], config=config,
                                          max_semantic_revisions=0)
    assert result["status"] == "audit_passed", result["reason"]
    assert len(audits.prompts) == 1 and not extraction.prompts
    manifest = runner.read_json(material[2] / "manifest.json")
    assert manifest["config"] == config
    path = material[2] / "calls/r000/audit/a001/request-validation.json"
    check = runner.read_json(path)
    assert check["transport"] == "injected" and check["observed"] is False
    assert runner.replay_run(material[2]) == result
    check["prompt_sha256"] = "0" * 64
    path.write_text(json.dumps(check), encoding="utf-8")
    replay = runner.replay_run(material[2])
    assert replay["status"] == "audit_error"
    assert "changed" in replay["reason"] or "differs" in replay["reason"]


def test_json_request_format_is_opt_in_and_rejects_unknown_formats():
    assert runner._config(None) == {"extraction": {}, "audit": {}}
    assert runner._config({"extraction": {}, "audit": {"response_format": "json_object"}})["extraction"] == {}
    with pytest.raises(ValueError, match="response_format"):
        runner._config({"response_format": "json_schema"})
