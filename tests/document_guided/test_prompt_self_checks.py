"""Pre-submit checks reuse existing requests and preserve stage isolation."""
import pytest

from skillflow.document_guided.prompts import (
    build_compact_graph_prompt, build_flow_prompt, build_fragment_prompt,
)
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.task.material import prepare_task_material
from skillflow.task.prompts import PRE_SUBMIT_CHECK, build_task_prompt
from skillflow.task.runner import prepare_task_run, run_task, verify_task_prepared
from tests.document_guided.test_boundary_prompt_alignment import material_inputs
from tests.task.test_protocol import Client, source, seal


def _fragment(step, *, repair=False, self_check=False):
    material, fragments, files = material_inputs()
    extra = {"task": material["task"]} if step == "task-correspondence" else {"runtime_contract": runtime_contract()} if step == "processing" else {}
    if repair:
        extra["repair_context"] = {"previous_fragment": fragments[step], "source_rechecks": []}
    documents = {"flow": "Inspect skill/SKILL.md:1-1."} if step == "processing" else {"processing": fragments["processing"]}
    return build_fragment_prompt(step, files=files, documents=documents, cfg=material["cfg"],
        global_requirements="Preserve actual sources, versions and receiving boundaries.", self_check=self_check, **extra)


def test_flow_and_cfg_checks_are_optional_and_reuse_existing_response():
    files = {"skill/SKILL.md": "Read the selected input and return it unchanged.\n"}
    flow_args = {"files": files, "global_requirements": "Preserve actual source behavior."}
    assert build_flow_prompt(**flow_args) == build_flow_prompt(**flow_args, self_check=False)
    flow = build_flow_prompt(**flow_args, self_check=True)
    assert flow.count(PRE_SUBMIT_CHECK) == 1
    assert "independent capabilities" in flow.split("PRE-SUBMIT CHECK\n")[1]
    graph_args = {**flow_args, "documents": {"flow": "Read then return. skill/SKILL.md:1-1"}}
    old = build_compact_graph_prompt(**graph_args)
    assert old == build_compact_graph_prompt(**graph_args, self_check=False)
    assert PRE_SUBMIT_CHECK not in old
    for feedback in (None, {"findings": []}):
        graph = build_compact_graph_prompt(**graph_args, feedback=feedback, self_check=True)
        assert graph.count(PRE_SUBMIT_CHECK) == 1
        assert "Check all explicit connections, operands, unique references and actual entry\nbefore returning" not in graph
        assert "unique producers" in graph.split("PRE-SUBMIT CHECK\n")[1]
    assert "supplied source" in PRE_SUBMIT_CHECK
    assert "pass tables" in PRE_SUBMIT_CHECK and "hidden reasoning" in PRE_SUBMIT_CHECK


@pytest.mark.parametrize("step,owner_rule", [
    ("processing", "current-IR coverage"),
    ("task-correspondence", "Separate action necessity from payload necessity"),
    ("sensitivity", "Distinguish plaintext inclusion from possible or derived influence"),
])
@pytest.mark.parametrize("repair", [False, True])
def test_fragment_checks_apply_to_initial_and_rebuild_without_cross_owner_input(step, owner_rule, repair):
    old = _fragment(step, repair=repair)
    prompt = _fragment(step, repair=repair, self_check=True)
    assert PRE_SUBMIT_CHECK not in old
    assert prompt.count(PRE_SUBMIT_CHECK) == 1
    assert owner_rule in prompt.split("PRE-SUBMIT CHECK\n")[1]
    assert ("SEALED_TASK\n" in prompt) == (step == "task-correspondence")
    assert ("RUNTIME_CONTRACT\n" in prompt) == (step == "processing")
    assert ("SOURCE REVIEW REPAIR\n" in prompt) is repair


def _task_candidate():
    evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "The source states the required behavior."}
    return {"purpose": {"text": "Return the original label.", "evidences": [evidence]},
        "requirements": [{"id": "R1", "text": "Return the label unchanged.", "evidences": [evidence]}], "issues": []}


def test_task_reuses_one_existing_self_check_in_initial_and_isolated_revision():
    src = source({"SKILL.md": "Return the label unchanged.\n"})
    material = prepare_task_material(src)
    prior = seal(_task_candidate(), src).model_dump(mode="json")
    revision = {"previous_task": prior, "objections": [{"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}], "requirement_ids": []}]}
    for revised in (None, revision):
        legacy = build_task_prompt(material, revised, allow_cannot_assess=False)
        assert legacy == build_task_prompt(material, revised, allow_cannot_assess=False, self_check=False)
        assert PRE_SUBMIT_CHECK not in legacy
        prompt = build_task_prompt(material, revised, allow_cannot_assess=False, self_check=True)
        assert prompt.count("7. SELF-CHECK") == 1
        assert prompt.count(PRE_SUBMIT_CHECK) == 1
        assert "SEALED_TASK\n" not in prompt and "RUNTIME_CONTRACT\n" not in prompt
        assert "outcome=cannot_assess" not in prompt


@pytest.mark.parametrize("enabled", [False, True])
def test_task_saves_check_policy_and_replays_with_zero_new_calls(tmp_path, enabled):
    run = tmp_path / "task"
    src = source({"SKILL.md": "Return the label unchanged.\n"})
    manifest = prepare_task_run(run, src, allow_cannot_assess=False, self_check=enabled, max_corrections=1)
    assert manifest["policy"].get("self_check", False) is enabled
    assert ("self_check" in manifest["policy"]) is enabled
    prompt = (run / "inputs/prompt.txt").read_text(encoding="utf-8")
    assert (PRE_SUBMIT_CHECK in prompt) is enabled
    assert verify_task_prepared(run)["policy"] == manifest["policy"]
    fake = Client(_task_candidate())
    first = run_task(run, client=fake, max_corrections=1)
    assert first["status"] == "complete" and len(fake.prompts) == 1
    replay = run_task(run, replay=True, max_corrections=1)
    assert replay["status"] == "complete" and len(fake.prompts) == 1
    assert (run / "inputs/prompt.txt").read_text(encoding="utf-8") == prompt
