"""Sparse unified source review, real references and offline recorded decisions."""
from copy import deepcopy
import json
from threading import Event

import pytest

from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.source_review import (
    build_source_review_prompt, prepare_review_material, run_source_review,
    replay_saved_review, task_objections, validate_source_review,
)
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.propagation.contracts.task import validate_task_candidate


class Client:
    def __init__(self, *values):
        self.values, self.prompts = list(values), []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return deepcopy(self.values.pop(0))


@pytest.fixture(autouse=True)
def stable_producer_during_concurrent_workspace_edits(monkeypatch):
    files = {"tests/document_guided/test_source_review.py": "offline-fixture"}
    monkeypatch.setattr("skillflow.document_guided.source_review.implementation_provenance",
                        lambda: {"files": files, "sha256": canonical_sha256(files)})


def fixture():
    files = {"skill/SKILL.md": "Read the request and return its label.\nNever send serial.\n"}
    evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The source names the returned field."}
    task = validate_task_candidate({"purpose": {"text": "Return the requested label.", "evidences": [evidence]},
        "requirements": [{"id": "R1", "text": "Return the original label.", "evidences": [evidence]}],
        "issues": []}, source_files=files).model_dump(mode="json")
    cfg = compile_candidate({"entry_block_ref": "read", "declared_context_keys": ["request"], "blocks": [{
        "block_ref": "read", "block_name": "Read the request and return the label", "data_source_kind": "context",
        "instructions": [{"instruction_ref": "read", "opcode": "read_label", "inputs": [
            {"type": "context_key", "identifier": "request"}], "outputs": [{"type": "result", "identifier": "label"}]},
            {"instruction_ref": "return", "opcode": "return", "inputs": [{"type": "result", "identifier": "label"}]}]}]
    }).cfg
    return files, task, json.loads(cfg.to_json())


def finding(domain="cfg"):
    return {"domain": domain, "target_ids": [domain + ":"], "explanation": "The requested relationship is missing.",
            "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
            "suggestion": "Preserve the source-supported relationship."}


def test_partial_empty_findings_is_normal_without_a_fake_annotation_or_pass_ledger():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg,
        stage_failures={"annotation": {"status": "semantic_failure", "reason": "Collection output is unavailable"}})
    assert material["annotation"] is None
    assert material["availability"] == {"task": True, "cfg": True, "annotation": False}
    assert not any(target["kind"] == "annotation" for target in material["target_index"])
    assert not any(target["kind"] == "observations" for target in material["target_index"])
    result = validate_source_review({"outcome": "completed", "findings": []}, material)
    assert result["findings"] == []
    prompt = build_source_review_prompt(material)
    assert "SourceFinding" in prompt and '"suggestion"' in prompt and '"source_refs"' in prompt
    assert "COMPLETE SOURCE" in prompt and "1: Read the request" in prompt
    payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1].split("\nCOMPLETE SOURCE\n", 1)[0])
    assert "draft_instruction_id" not in json.dumps(payload["cfg"])
    assert not ({"usage", "billing", "env", "requirement_checks", "declaration_checks"} & payload.keys())


@pytest.mark.parametrize("change", ["target", "source", "domain"])
def test_actual_targets_source_ranges_and_domains_are_checked(change):
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg)
    item = finding()
    good = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert good["findings"][0]["id"] == "F001"
    if change == "target":
        item["target_ids"] = ["cfg:/invented"]
    elif change == "source":
        item["source_refs"][0]["end_line"] = 1000
    else:
        item["target_ids"] = ["task:"]
    with pytest.raises(StructuralValidationError):
        validate_source_review({"outcome": "completed", "findings": [item]}, material)


def test_task_objection_projection_contains_only_finite_source_only_data():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg)
    item = finding("task")
    item["task_objection"] = {"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}], "requirement_ids": []}
    reviewed = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert task_objections(reviewed) == [item["task_objection"]]
    for bad in ("requirement", "graph_target", "free_text"):
        changed = deepcopy(item)
        if bad == "requirement":
            changed["task_objection"]["requirement_ids"] = ["R999"]
        elif bad == "graph_target":
            changed["target_ids"].append("cfg:")
        else:
            changed["task_objection"]["reason"] = "Payloads suggest a broader purpose."
        with pytest.raises(StructuralValidationError):
            validate_source_review({"outcome": "completed", "findings": [changed]}, material)


@pytest.mark.parametrize("wire_path", [["ops", 0], "/ops/0"])
def test_compiler_observations_retain_actual_flat_wire_coordinates(wire_path):
    files, task, cfg = fixture()
    wire = {"ops": [{"ir_id": "ir_001", "op": "read"}]}
    compiled = {"locations": {"model": {"kind": "model", "name": "model"}}, "ir_semantics": {
        "ir_001": {"events": [{"effect": "model_observe", "atomic_ops": [
            {"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "model"}]}]}}}
    mapping = {"events": [{"instruction_id": "ir_001", "kind": "observation", "mode": "model",
        "compiled_path": ["ir_semantics", "ir_001", "events", 0],
        "raw_path": ["ir_semantics", "ir_001", "events", 0], "wire_path": wire_path}]}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=wire, compiled=compiled, mapping=mapping)
    assert material["observations"][0]["wire_pointer"] == "/ops/0"
    assert {"id": "annotation:/ops/0", "domain": "annotation", "kind": "annotation", "pointer": "/ops/0"} in material["target_index"]
    assert material["annotation"] == wire
    mapping["events"][0]["wire_path"] = ["ops", 9]
    with pytest.raises(ValueError):
        prepare_review_material(files=files, task=task, cfg=cfg, annotation=wire, compiled=compiled, mapping=mapping)


def test_recorded_source_review_zero_call_replay_and_accepted_resume(tmp_path):
    files, task, cfg = fixture()
    args = {"files": files, "task": task, "cfg": cfg}
    client = Client({"outcome": "completed", "findings": [finding()]})
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete" and result["diagnostic_only"]
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    def forbidden():
        raise AssertionError("Accepted response or replay must not create a client")
    assert run_source_review(tmp_path, **args, client_factory=forbidden) == result
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert replay_saved_review(tmp_path) == result
    assert len(client.prompts) == 1
    assert {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    (tmp_path / "inputs.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        run_source_review(tmp_path, **args, client_factory=forbidden)


def test_single_correction_exhaustion_is_terminal_and_not_a_semantic_finding(tmp_path):
    files, task, cfg = fixture()
    args = {"files": files, "task": task, "cfg": cfg}
    client = Client({"outcome": "completed"}, {"outcome": "completed"}, {"outcome": "completed", "findings": []})
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "structural_failure" and result["review"] is None
    assert result["counts"]["structural_corrections"] == 1 and len(client.prompts) == 2
    assert not (tmp_path / "calls/review/a003").exists()
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert run_source_review(tmp_path, **args) == result


def test_real_cannot_assess_is_preserved_without_automatic_correction(tmp_path):
    files, task, cfg = fixture()
    failure = {"reason": "No collection result can preserve these acquired per-element versions.",
        "target_ids": ["cfg:"], "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}
    material = prepare_review_material(files=files, cfg=cfg)
    with pytest.raises(SemanticFailure):
        validate_source_review({"outcome": "cannot_assess", "failure": failure}, material)
    client = Client({"outcome": "cannot_assess", "failure": failure})
    result = run_source_review(tmp_path, files=files, cfg=cfg, client=client)
    assert result["status"] == "semantic_failure" and result["failure"] == failure
    assert len(client.prompts) == 1 and not result["availability"]["task"]


def test_source_review_interruption_after_answer_replays_and_resumes_without_a_new_call(tmp_path):
    files, task, cfg = fixture()
    stopping = Event()
    class InterruptAfterAnswer(Client):
        def complete(self, prompt):
            answer = super().complete(prompt)
            stopping.set()
            return answer
    client = InterruptAfterAnswer({"outcome": "completed", "findings": []})
    args = {"files": files, "task": task, "cfg": cfg}
    interrupted = run_source_review(tmp_path, **args, client=client, stop_event=stopping)
    assert interrupted["status"] == "interrupted"
    assert interrupted["interruption"]["point"] == "after_call"
    stopping.clear()
    assert run_source_review(tmp_path, **args, replay=True) == interrupted
    assert replay_saved_review(tmp_path) == interrupted
    resumed = run_source_review(tmp_path, **args)
    assert resumed["status"] == "complete" and resumed["review"]["findings"] == []
    assert len(client.prompts) == 1


def test_source_review_monitor_unavailability_does_not_change_replayed_decisions(tmp_path, monkeypatch):
    import skillflow.document_guided.source_review as module
    files, task, cfg = fixture()
    original_counts = module.chain_counts
    monkeypatch.setattr(module, "chain_counts", lambda *a, **k: (_ for _ in ()).throw(OSError("monitor only")))
    args = {"files": files, "task": task, "cfg": cfg}
    result = run_source_review(tmp_path, **args, client=Client({"outcome": "completed", "findings": []}))
    assert result["status"] == "complete" and result["counts"] == {"status": "unavailable"}
    monkeypatch.setattr(module, "chain_counts", original_counts)
    assert run_source_review(tmp_path, **args, replay=True) == result


def test_compact_target_index_keeps_declarations_without_mechanical_reference_ids():
    files, task, cfg = fixture()
    annotation = {"ir_semantics": {"ir_001": {"segments": [{"ops": [{"op": "compute",
        "inputs": [{"kind": "alternatives", "values": [{"kind": "input", "index": 0},
            {"kind": "literal", "value": {"nested": [1, 2]}}]}],
        "demands": [{"requirement_id": "R1", "target": {"kind": "input", "index": 0},
            "path": ["label"], "expected_path": ["original", "label"]}],
        "metadata": {"explanation": {"nested": []}}}]}]}},
        "realizations": [{"requirement_id": "R1", "constraints": [{"kind": "only_if",
            "events": [{"ref": {"instruction_id": "ir_001", "operation_path": ["segments", 0, "ops", 0]}}]}]}]}
    cfg["blocks"]["block_001"]["instructions"][0]["metadata"] = {"payload": {"nested": []}}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=annotation)
    ids = {target["id"] for target in material["target_index"]}
    operation = "annotation:/ir_semantics/ir_001/segments/0/ops/0"
    for identity in ("cfg:/blocks/block_001/instructions/0", "task:/requirements/0", "annotation:",
                     operation, operation + "/demands", operation + "/demands/0",
                     "annotation:/realizations/0", "annotation:/realizations/0/constraints/0"):
        assert identity in ids
    for fragment in ("/inputs/0", "/target", "/ref", "/path", "/expected_path", "/scope_path",
                     "/operation_path", "/literal_value", "/evidences", "/metadata"):
        assert not any(identity.startswith("annotation:") and fragment in identity for identity in ids)
    assert not any("/metadata" in identity or "/evidences" in identity for identity in ids)
    assert material["annotation"] == annotation


def test_fragment_review_has_no_whole_cannot_assess_branch_and_keeps_legacy():
    files, task, cfg = fixture()
    failure = {"outcome": "cannot_assess", "failure": {
        "reason": "The unmodeled member relationship cannot be assessed.", "target_ids": ["cfg:"],
        "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}}
    material = prepare_review_material(files=files, task=task, cfg=cfg, generation="fragment-v1")
    with pytest.raises(StructuralValidationError):
        validate_source_review(failure, material)
    prompt = build_source_review_prompt(material)
    assert "FragmentSourceFinding" in prompt and '"owner"' in prompt
    assert "CannotAssessSourceReview" not in prompt
    assert "report cannot_assess only" not in prompt
    assert "never treat unknown behavior as safe" in prompt
    legacy = prepare_review_material(files=files, task=task, cfg=cfg)
    with pytest.raises(SemanticFailure):
        validate_source_review(failure, legacy)
    assert "generation" not in legacy and "processing_gaps" not in legacy


def test_fragment_review_partial_gaps_are_not_unknown_as_safe_and_replay_zero_calls(tmp_path):
    files, task, cfg = fixture()
    gap = {"instruction_id": "ir_001", "reason": "The result's internal member acquisition is not represented.",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}], "unmodeled": True}
    args = {"files": files, "task": task, "cfg": cfg, "generation": "fragment-v1", "processing_gaps": [gap]}
    client = Client({"outcome": "completed", "findings": []})
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete" and result["diagnostic_only"]
    assert result["availability"] == {"task": True, "cfg": True, "annotation": False,
        "fragments": {"processing": False, "sensitivity": False, "task-correspondence": False}}
    material = json.loads((tmp_path / "inputs.json").read_text(encoding="utf-8"))
    assert material["processing_gaps"] == [gap] and material["partial"]
    assert not any(row["domain"] == "annotation" for row in material["target_index"])
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert replay_saved_review(tmp_path) == result
    assert run_source_review(tmp_path, **args) == result
    assert len(client.prompts) == 1


def test_fragment_review_whole_failure_gets_one_shape_correction(tmp_path):
    files, task, cfg = fixture()
    client = Client({"outcome": "cannot_assess", "failure": {
        "reason": "Some processing remains unknown.", "target_ids": ["cfg:"], "source_refs": []}},
        {"outcome": "completed", "findings": []})
    args = {"files": files, "task": task, "cfg": cfg, "generation": "fragment-v1", "partial": True}
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete" and result["diagnostic_only"]
    assert result["counts"]["structural_corrections"] == 1
    assert len(client.prompts) == 2
    assert run_source_review(tmp_path, **args, replay=True) == result


@pytest.mark.parametrize("pointer,expected", [
    ("/ir_semantics/ir_001", "processing"), ("/realizations/0", "task-correspondence"),
    ("/demands/0", "task-correspondence"), ("/expressions/0", "processing"),
    ("/operation_demands/0", "task-correspondence"), ("/sensitivity/0", "sensitivity"),
    ("/declarations/0", "sensitivity"), ("", "processing"),
])
def test_fragment_review_annotation_owner_comes_from_actual_target(pointer, expected):
    files, task, cfg = fixture()
    wire = {"ir_semantics": {"ir_001": {"ops": []}}, "realizations": [{}], "demands": [{}],
            "expressions": [{}], "operation_demands": [{}], "sensitivity": [{}], "declarations": [{}]}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=wire, generation="fragment-v1")
    item = finding("annotation")
    item["target_ids"] = ["annotation:" + pointer]
    review = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert review["findings"][0]["owner"] == expected
    changed = deepcopy(item)
    changed["owner"] = "sensitivity" if expected != "sensitivity" else "processing"
    with pytest.raises(StructuralValidationError):
        validate_source_review({"outcome": "completed", "findings": [changed]}, material)


@pytest.mark.parametrize("rich_origins", [False, True])
def test_fragment_origins_override_prefix_and_full_annotation_gaps_stay_diagnostic(tmp_path, rich_origins):
    files, task, cfg = fixture()
    wire = {"ir_semantics": {"ir_001": {"demands": [{}]}}}
    pointer = "/ir_semantics/ir_001/demands/0"
    mapping = {"fragment_origins": {"/ir_semantics": "processing", pointer: "task-correspondence"},
               "processing_gaps": [{"instruction_id": "ir_001", "reason": "Unknown internal update."}]}
    if rich_origins:
        mapping["fragment_origins"] = {key: {"fragment": value, "path": "/operation_demands/0"}
                                       for key, value in mapping["fragment_origins"].items()}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=wire,
        mapping=mapping, generation="fragment-v1")
    item = finding("annotation")
    item["target_ids"] = ["annotation:" + pointer]
    checked = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert checked["findings"][0]["owner"] == "task-correspondence"
    assert material["fragment_origins"] == mapping["fragment_origins"]
    args = {"files": files, "task": task, "cfg": cfg, "annotation": wire, "mapping": mapping,
            "generation": "fragment-v1"}
    result = run_source_review(tmp_path, **args, client=Client({"outcome": "completed", "findings": []}))
    assert all(result["availability"].values()) and result["diagnostic_only"]
    assert replay_saved_review(tmp_path) == result


def test_fragment_owner_cannot_route_task_or_cfg_and_finite_objections_stay_isolated():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg, generation="fragment-v1")
    item = finding("task")
    item["task_objection"] = {"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}], "requirement_ids": []}
    review = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert task_objections(review) == [item["task_objection"]]
    assert "owner" not in review["findings"][0]
    for changed in (item, finding("cfg")):
        changed["owner"] = "processing"
        with pytest.raises(StructuralValidationError):
            validate_source_review({"outcome": "completed", "findings": [changed]}, material)


def partial_fragments():
    return {"processing": {"ir_semantics": {"ir_001": {"segments": [{"ops": [
        {"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "display"}]}]}},
        "locations": {"display": {"kind": "user", "name": "display"}}},
        "task-correspondence": {"realizations": [{"requirement_id": "R1", "bindings": []}], "demands": []}}


def test_partial_review_preserves_actual_fragments_without_fabricating_annotation():
    files, task, cfg = fixture()
    fragments = partial_fragments()
    failures = {"sensitivity": {"status": "structural_failure", "reason": "Invalid source label record"}}
    material = prepare_review_material(files=files, task=task, cfg=cfg, fragments=fragments,
        stage_failures=failures, generation="fragment-v1")
    assert material["annotation"] is None and material["observations"] == []
    assert material["fragments"] == fragments and fragments == partial_fragments()
    assert material["availability"]["annotation"] is False
    assert material["availability"]["fragments"] == {
        "processing": True, "task-correspondence": True, "sensitivity": False}
    targets = {row["id"]: row for row in material["target_index"]}
    operation = "fragment:processing:/ir_semantics/ir_001/segments/0/ops/0"
    assert targets[operation]["pointer"] == "/processing/ir_semantics/ir_001/segments/0/ops/0"
    assert targets[operation]["owner"] == "processing"
    assert "fragment:task-correspondence:/realizations/0" in targets
    assert targets["stage:sensitivity"]["requires_source"]
    assert not any(identity.startswith(("annotation:", "observations:", "fragment:sensitivity:"))
                   for identity in targets)
    assert not any("/inputs/0" in identity or "/target" in identity
                   for identity in targets if identity.startswith("fragment:"))
    prompt = build_source_review_prompt(material)
    assert '"fragments":' in prompt and '"op":"deliver"' in prompt
    assert "source-supported semantic omission or defect" in prompt
    item = finding("annotation")
    item["target_ids"] = [operation]
    checked = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert checked["findings"][0]["owner"] == "processing"
    assert task_objections(checked) == []


@pytest.mark.parametrize("owner", ["sensitivity", "task-correspondence"])
def test_partial_stage_target_routes_real_source_finding_and_rejects_bad_grounding(owner):
    files, task, cfg = fixture()
    fragments = {"processing": partial_fragments()["processing"]}
    material = prepare_review_material(files=files, task=task, cfg=cfg, fragments=fragments,
        stage_failures={owner: {"status": "structural_failure", "reason": "No validated fragment"}},
        generation="fragment-v1")
    item = finding("annotation")
    item["target_ids"] = ["stage:" + owner]
    item["explanation"] = "The original source requires a declaration missing from the available analysis."
    checked = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert checked["findings"][0]["owner"] == owner
    for change in ("no_source", "bad_source", "bad_owner", "absent_fragment"):
        changed = deepcopy(item)
        if change == "no_source":
            changed["source_refs"] = []
        elif change == "bad_source":
            changed["source_refs"][0]["end_line"] = 999
        elif change == "bad_owner":
            changed["owner"] = "processing"
        else:
            changed["target_ids"] = ["fragment:" + owner + ":"]
        with pytest.raises(StructuralValidationError):
            validate_source_review({"outcome": "completed", "findings": [changed]}, material)


@pytest.mark.parametrize("owner,pointer", [
    ("task-correspondence", "/realizations/0"), ("sensitivity", "/declarations/0")])
def test_actual_partial_owner_targets_remain_reviewable_when_another_owner_failed(owner, pointer):
    files, task, cfg = fixture()
    fragments = partial_fragments()
    fragments["sensitivity"] = {"declarations": [{"instruction_id": "ir_001",
        "value": {"kind": "input", "index": 0}, "label": "source label", "evidences": [
            {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}]}
    missing = "sensitivity" if owner == "task-correspondence" else "task-correspondence"
    fragments.pop(missing)
    material = prepare_review_material(files=files, task=task, cfg=cfg, fragments=fragments,
        stage_failures={missing: {"status": "structural_failure"}}, generation="fragment-v1")
    item = finding("annotation")
    item["target_ids"] = ["fragment:" + owner + ":" + pointer]
    checked = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert checked["findings"][0]["owner"] == owner
    assert material["annotation"] is None
    item["owner"] = missing
    with pytest.raises(StructuralValidationError):
        validate_source_review({"outcome": "completed", "findings": [item]}, material)


def test_partial_fragment_stage_finding_records_and_replays_without_new_calls(tmp_path):
    files, task, cfg = fixture()
    item = finding("annotation")
    item["target_ids"] = ["stage:sensitivity"]
    args = {"files": files, "task": task, "cfg": cfg, "generation": "fragment-v1",
        "fragments": partial_fragments(), "stage_failures": {"sensitivity": {
            "status": "structural_failure", "reason": "No valid sensitivity fragment"}}}
    client = Client({"outcome": "completed", "findings": [item]})
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete" and result["diagnostic_only"]
    assert result["review"]["findings"][0]["owner"] == "sensitivity"
    assert not result["availability"]["annotation"] and result["objections"] == []
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert replay_saved_review(tmp_path) == result
    assert len(client.prompts) == 1
    inputs = json.loads((tmp_path / "inputs.json").read_text(encoding="utf-8"))
    assert inputs["annotation"] is None and inputs["fragments"] == partial_fragments()


def test_fragment_inputs_do_not_change_finite_task_objection_projection():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg, fragments=partial_fragments(),
        generation="fragment-v1")
    item = finding("task")
    item["task_objection"] = {"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}], "requirement_ids": []}
    review = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert task_objections(review) == [item["task_objection"]]
    item["target_ids"].append("fragment:processing:")
    with pytest.raises(StructuralValidationError):
        validate_source_review({"outcome": "completed", "findings": [item]}, material)


def test_partial_fragment_inputs_are_explicit_and_legacy_default_is_unchanged():
    files, task, cfg = fixture()
    legacy = prepare_review_material(files=files, task=task, cfg=cfg,
        stage_failures={"sensitivity": {"status": "structural_failure"}})
    assert "fragments" not in legacy and "fragments" not in legacy["availability"]
    assert not any(row["id"].startswith("stage:") for row in legacy["target_index"])
    for fragments in ({"unknown": {}}, {"processing": None}, []):
        with pytest.raises(ValueError):
            prepare_review_material(files=files, task=task, cfg=cfg, fragments=fragments,
                                    generation="fragment-v1")
    with pytest.raises(ValueError):
        prepare_review_material(files=files, fragments={})
