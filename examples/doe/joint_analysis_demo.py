"""Offline synthetic example: direct references through deterministic DOE.

Run: python -m examples.doe.joint_analysis_demo [--show annotation|result|sizes]
The declaration is authored example data, not an accepted model response.
No evaluated Skill, historical result or test-only reconstruction is imported.
"""
from __future__ import annotations

import argparse
import json

from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.binding_examples import binding_examples, example_material, evidence, segment
from skillflow.propagation.annotation.services import compile_response, to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate


def build_example():
    example = next(item for item in binding_examples() if item["name"] == "return_input")
    example["source"] = ("The agent runtime reads the calibration record from calibration.json "
                         "and returns its original label internally. The record also contains "
                         "a confidential maintenance serial.\n")
    example["cfg"]["blocks"]["sample"]["instructions"][0]["inputs"][0] = {
        "type": "external_resource", "identifier": "calibration.json"}
    semantics = example["annotation"]["ir_semantics"]["ir_sample_pick"]
    semantics["events"][0]["events"][0]["atomic_ops"][0]["input"] = {"kind": "local", "name": "record"}
    semantics["events"].insert(0, segment([{"op": "read", "location": "calibration_file", "output": "record"}], "fs_read"))
    example["annotation"]["locations"] = {"calibration_file": {
        "kind": "storage", "name": "calibration.json", "access_scope": "task", "retention": "persistent",
        "operand_refs": [{"instruction_id": "ir_sample_pick", "side": "input", "index": 0}]}}
    example["annotation"]["location_evidences"] = {"calibration_file": [evidence()]}
    example["annotation"]["ir_semantics"]["ir_sample_pick"]["sensitivity"] = [{
        "value": {"kind": "local", "name": "record"}, "path": ["serial"],
        "property": "value", "label": "confidential_identifier",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                       "reason": "The source explicitly describes the maintenance serial as confidential."}]}]
    material = example_material(example)
    example["annotation"]["task_revision_id"] = material["task"]["task_sha256"]
    raw, compiled, mapping = compile_response(example["annotation"], material)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
                                  compiled_annotation=compiled, mapping=mapping)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    return material, raw, facts, review.to_dict()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", choices=("annotation", "result", "sizes"), default="annotation")
    args = parser.parse_args(argv)
    material, raw, facts, result = build_example()
    if args.show == "sizes":
        output = {}
        for name, value in (("annotation_material", material), ("raw_annotation", raw),
                            ("data", facts.data), ("records", facts.records),
                            ("sinks", facts.sinks), ("doe_result", result)):
            text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            output[name] = {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}
    else:
        output = raw if args.show == "annotation" else result
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
