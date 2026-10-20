"""One independent, compilable restriction lesson; no positive seed for a ban."""
from __future__ import annotations

from copy import deepcopy

from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, goal, inp, instruction, literal, local,
    segment, semantics,
)


def constraint_example():
    source = (
        "Submit the calibration envelope's label unchanged to the device interface. "
        "Never deliver its diagnostic_note field to that interface."
    )
    pick = {"op": "select_part", "input": inp(), "path": ["label"], "output": "label"}
    send = {"op": "deliver", "target": "interface", "inputs": [local("label")],
            "demands": [goal({"kind": "self"}, "action"),
                        goal({"kind": "input", "index": 0}, expected=inp(), expected_path=["label"])]}
    example = _fixture("envelope_restriction", "Expression is not enforcement or a positive demand.", source,
        [instruction("ir_envelope", "submit_label", [literal({"label": "calibration", "diagnostic_note": "maintenance"})]),
         instruction("ir_end", "return", [])],
        {"ir_envelope": semantics([segment([pick]), segment([send], None)]), "ir_end": semantics()})
    # A null interaction event carries evidence on its operation and segment.
    example["annotation"]["ir_semantics"]["ir_envelope"]["events"][1]["events"][0]["evidences"] = []
    task = example["task_candidate"]
    task["requirements"][0]["text"] = "Submit the unchanged label to the device interface."
    task["requirements"].append({"id": "R2", "text": "Do not deliver diagnostic_note to the device interface.",
                                 "evidences": [evidence()]})
    task["source_accounting"][0]["requirement_ids"] = ["R1", "R2"]
    raw = example["annotation"]
    raw["locations"] = {"interface": {"kind": "tool", "name": "device interface", "operand_refs": [],
                                     "access_scope": "recipient", "retention": None}}
    raw["location_evidences"] = {"interface": [evidence()]}
    raw["realizations"] = [
        {"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []},
        {"requirement_id": "R2", "status": "expressed", "bindings": [], "gaps": [], "constraints": [{
            "kind": "forbid_information", "scope": {"kind": "task"},
            "source": {"instruction_id": "ir_envelope", "scope_path": [], "value": inp()},
            "path": ["diagnostic_note"], "receivers": {"kind": "locations", "ids": ["interface"]},
        }]},
    ]
    raw["task_revision_id"] = example_material(example)["task"]["task_sha256"]
    return example


def constraint_lesson():
    """Public context makes the complete realization fragment directly checkable."""
    example = constraint_example()
    return {
        "case": example["name"], "source": example["source"],
        "context": {"file": "skill/SKILL.md", "line": 1,
            "requirement": deepcopy(example["task_candidate"]["requirements"][1]),
            "instruction": deepcopy(example["cfg"]["blocks"]["sample"]["instructions"][0]),
            "location": deepcopy(example["annotation"]["locations"]["interface"]), "location_id": "interface"},
        "realization": deepcopy(example["annotation"]["realizations"][1]),
        "rule": "R2 has no positive demand. This complete realization states the restriction, not that it is satisfied. "
                "The actual label selection and delivery remain separate processing facts. A whole-envelope delivery "
                "would remain whole for forward checking; the restriction cannot silently delete diagnostic_note.",
    }
