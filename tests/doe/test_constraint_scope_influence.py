"""Empty recorded member sets do not prove that an upstream change is isolated."""
from copy import deepcopy

import pytest

from skillflow.doe.constraint_preservation import ConstraintAnalysis, ForwardInfluence
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, inp, instruction, literal, local,
    segment, semantics,
)
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from tests.doe.test_sink_payload_seeds import solve_fixture


def empty_members_case(constraint_kind):
    source = (
        "Inspect the supplied envelope and process its members using the model. "
        "The member actions obey the stated finite event restriction."
    )
    pick = segment([{"op": "select_part", "input": inp(), "path": ["members"], "output": "members"}])
    pick["mode"] = "model"
    body = segment([{"op": "deliver", "target": "display", "inputs": [local("member")]}], "user_output")
    event = {"kind": "for_each", "collection": local("members"), "item": "member",
             "evidences": [evidence()], "body": [body]}
    spec = semantics([pick, event])
    spec["operator"] = ["llm"]
    spec["operator_evidences"] = [{"value": "llm", **evidence()}]
    example = _fixture("empty member scope", "A valid empty collection retains its operation template.", source,
        [instruction("ir_members", "process_members", [literal({"members": []})]),
         instruction("ir_end", "return", [])],
        {"ir_members": spec, "ir_end": semantics()})
    material = example_material(example)
    raw = example["annotation"]
    raw["task_revision_id"] = material["task"]["task_sha256"]
    raw["locations"]["display"] = {"kind": "user", "name": "display", "operand_refs": [],
                                      "access_scope": "recipient", "retention": None}
    raw["location_evidences"]["display"] = [evidence()]
    target = {"instruction_id": "ir_members", "operation_path":
              ["events", 1, "body", 0, "events", 0, "atomic_ops", 0], "slot": {"kind": "self"}}
    if constraint_kind == "at_most":
        constraint = {"kind": "at_most", "scope": {"kind": "task"},
                      "events": [target], "limit": 0, "unit": "attempt"}
    else:
        constraint = {"kind": "forbid_information", "scope": {"kind": "task"},
            "source": {"instruction_id": "ir_members", "scope_path": [], "value": inp()},
            "path": ["members", {"kind": "each"}],
            "receivers": {"kind": "locations", "ids": ["display"]}, "events": [target]}
    raw["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [],
                            "gaps": [], "constraints": [constraint]}]
    checked, compiled, mapping = compile_response(raw, material)
    propagated = propagate(material["cfg"], to_payload(compiled))
    assert propagated.status == "complete", propagated.diagnostics
    facts = materials_from_result(propagated, material=material, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping)
    return material, checked, facts


@pytest.mark.parametrize("constraint_kind", ["at_most", "forbid_information"])
def test_empty_member_scope_is_not_an_absence_of_affected_event_templates(constraint_kind):
    case = empty_members_case(constraint_kind)
    engine, demands = solve_fixture(case)
    before = deepcopy((case[2].data, case[2].records, case[2].sinks, demands))
    assert not any(info["scope"] is not None for info in engine.ops.values())
    observer = next(key for key, info in engine.ops.items()
                    if info["generated"] and info["position"]["instruction_id"] == "ir_members"
                    and engine.slots(key).get(0, ({},))[0] == inp())
    analysis = ConstraintAnalysis(engine)
    check = next(iter(analysis.checks.values()))
    assert check["status"] == "satisfied"
    assert not check["structural"]
    changed = ForwardInfluence(engine).run(observer, 0, ["members"])
    assert "ir_members" in changed["instructions"]
    refs, preserved = analysis.evaluate(observer, 0,
        engine.ops[observer]["record"]["inputs"][0][0], ["members"])
    assert refs and not preserved
    assert all(analysis.preservation[ref]["rule"] == "not_established" for ref in refs)
    assert (case[2].data, case[2].records, case[2].sinks, demands) == before
