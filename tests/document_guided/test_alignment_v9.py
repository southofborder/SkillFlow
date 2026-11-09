"""Full-source contracts and executable connected CFG/processing examples."""
from copy import deepcopy
import json

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.cfg_wire import normalize_cfg_wire
from skillflow.document_guided.fragments import assemble_fragments
from skillflow.document_guided.interface_examples import alignment_examples
from skillflow.document_guided.prompts import build_compact_graph_prompt, build_fragment_prompt
from skillflow.document_guided.source import render_source, source_packet
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.propagation.annotation.binding_examples import _fixture, example_material
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate


def compile_example(example):
    result = compile_candidate(normalize_cfg_wire(example["cfg"]))
    assert result.ok, result.diagnostics
    fixture = _fixture("alignment", "Connected boundary example", example["source"], [], {})
    fixture["cfg"] = json.loads(result.cfg.to_json())
    material = example_material(fixture)
    mapping = {"realizations": [{"requirement_id": "R1"}], "demands": [
        {"requirement_id": "R1", "target": {"instruction_id": instruction["id"], "side": "input", "index": 0},
         "preserve": "value", "reason": "Keep the actual source-specified result at this return."}
        for block in material["cfg"]["blocks"].values() for instruction in block["instructions"]
        if instruction["opcode"] == "return" and instruction["inputs"]]}
    assembled = assemble_fragments(example["processing"], mapping, {"declarations": []}, material)
    return material, assembled


@pytest.mark.parametrize("name", list(alignment_examples()))
def test_published_connected_pairs_compile_propagate_and_load_for_doe(name):
    from skillflow.propagation.loading import materials_from_result
    from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
    material, (saved, raw, compiled, mapping) = compile_example(alignment_examples()[name])
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=json.loads(json.dumps(compiled)), mapping=mapping, wire_annotation=saved)
    facts.record_store.validate(require_complete=True)
    assert prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()["goals"]
    if name == "caller_boundary":
        operation = result.records.get("ir_003").events[0].atomic_ops[0]
        assert operation.inputs[0] == result.records.get("ir_001").events[0].atomic_ops[0].outputs[0]
    elif name == "guard_then_member":
        operation = result.records.get("ir_005").events[0].atomic_ops[0]
        assert len(operation.alternatives) == 2
        assert len({tuple(candidate.bindings.items()) for candidate in operation.alternatives}) == 2


@pytest.mark.parametrize("ready,retry,reached", [(True, False, "ir_003"), (False, True, "ir_004"), (False, False, "ir_005")])
def test_binary_decisions_preserve_three_outcomes_without_three_way_dispatch(ready, retry, reached):
    example = alignment_examples()["binary_outcome_routing"]
    example["cfg"]["blocks"][0]["instructions"][0]["inputs"][0]["literal_value"] = ready
    example["cfg"]["blocks"][1]["instructions"][0]["inputs"][0]["literal_value"] = retry
    material, (_, _, compiled, _) = compile_example(example)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    assert result.coverage[reached] == "processed"
    assert all(result.coverage[other] == "not_reached" for other in {"ir_003", "ir_004", "ir_005"} - {reached})


def test_empty_traversal_has_no_member_call_or_response():
    example = alignment_examples()["guard_then_member"]
    example["cfg"]["blocks"][0]["instructions"][0]["inputs"][0]["literal_value"] = []
    material, (_, _, compiled, _) = compile_example(example)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    assert result.coverage["ir_004"] == result.coverage["ir_005"] == "not_reached"
    assert result.coverage["ir_007"] == "processed"


def test_zero_argument_call_remains_valid_and_has_no_invented_payload():
    example = alignment_examples()["caller_boundary"]
    example["cfg"]["blocks"][1]["instructions"][0]["inputs"] = []
    example["processing"]["ir_semantics"]["ir_003"]["segments"][0]["ops"][0]["inputs"] = []
    example["source"] = "Acquire request; call helper() without arguments. It returns Service()'s actual response."
    material, (_, _, compiled, _) = compile_example(example)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    assert result.records.get("ir_003").events[0].atomic_ops[0].inputs == []


def test_three_distinct_successors_get_early_precise_error_without_rewriting():
    value = alignment_examples()["binary_outcome_routing"]["cfg"]
    value["edges"].append({"source_block_ref": "ready_check", "target_block_ref": "stop"})
    original = deepcopy(value)
    with pytest.raises(StructuralValidationError) as caught:
        normalize_cfg_wire(value)
    diagnostic = next(row for row in caught.value.diagnostics if row["code"] == "binary_dispatch")
    assert diagnostic["path"] == "/blocks/0/instructions/0"
    assert diagnostic["context"]["successors"] == ["ready", "retry_check", "stop"]
    assert diagnostic["context"]["edge_indices"] == [0, 1, 4]
    assert diagnostic["context"]["current_value"] == value["blocks"][0]["instructions"][0]
    assert value == original


def test_duplicate_edge_does_not_become_a_third_distinct_successor():
    value = alignment_examples()["binary_outcome_routing"]["cfg"]
    value["edges"].append(deepcopy(value["edges"][0]))
    normalize_cfg_wire(value)


@pytest.mark.parametrize("repair", [False, True])
def test_current_graph_and_all_fragments_receive_complete_source_not_prior_citation_slices(repair):
    from tests.document_guided.test_fragments import fixture
    material, _, fragments = fixture()
    files = {"skill/SKILL.md": "Keep source roles.\r\n", "skill/entry.py": "call_helper()\r\n",
             "skill/unmentioned.py": "# 真正源码\r\nreturn distinct_result\r\n",
             "skill/other.md": "Independent documented capability.\n"}
    cfg = deepcopy(material["cfg"])
    first = next(iter(cfg["blocks"].values()))["instructions"][0]
    first["metadata"]["script_content"] = files["skill/unmentioned.py"]
    args = {"files": files, "documents": {"flow": "Only skill/entry.py:1-1 was previously mentioned."},
            "global_requirements": "Keep actual source boundaries."}
    graph = build_compact_graph_prompt(**args, spans=[{"file": "skill/entry.py", "start_line": 1, "end_line": 1}],
        feedback={"cfg": cfg} if repair else None)
    prompts = [graph]
    for step in ("processing", "task-correspondence", "sensitivity"):
        kwargs = {"runtime_contract": {"rules": []}} if step == "processing" else {}
        if step == "task-correspondence":
            kwargs["task"] = material["task"]
        prompts.append(build_fragment_prompt(step, files=files, cfg=cfg,
            documents=args["documents"] if step == "processing" else {"processing": fragments["processing"]},
            global_requirements=args["global_requirements"], repair_context={"source_rechecks": []} if repair else None, **kwargs))
    for prompt in prompts:
        actual_source = prompt.split("RELATED SOURCE\n", 1)[1].split("\n\nOUTPUT REQUIREMENTS\n", 1)[0]
        assert actual_source == render_source(source_packet(files))
        assert '"script_content"' not in prompt
    assert "SEALED_TASK\n" not in prompts[1] and "SEALED_TASK\n" not in prompts[3]
    assert "SEALED_TASK\n" in prompts[2]
    assert first["metadata"]["script_content"] == files["skill/unmentioned.py"]
