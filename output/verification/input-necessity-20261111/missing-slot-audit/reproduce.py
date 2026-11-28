"""Offline, source-explicit missing-argument audit; no Skill/model execution."""
from copy import deepcopy
import json
from pathlib import Path

from skillflow.common.recording import canonical_sha256
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.input_contract_review import (
    SOURCE_REVIEW_VERSION, build_input_contract_review, input_contract_binding,
)
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.binding_examples import evidence, inp
from skillflow.propagation.contracts.input_requirements import check_input_coverage
from skillflow.propagation.contracts.joint import joint_source_files
from skillflow.propagation.contracts.task import Task
from tests.doe.test_sink_payload_seeds import synthetic_fixture


SOURCE = (
    "The documented Service.fetch interface requires both a and b as arguments. "
    "The actual workflow calls Service.fetch(a) with only a, omitting b, and returns its response."
)
requirement = {"input_index": 0, "required": [{"property": "value", "path": []}],
    "remainder": "independent", "reason": "The actual first input supplies required argument a."}
contract = {"inputs": [requirement],
    "reason": "The actual input list contains a only; the source establishes that required argument b is missing.",
    "evidences": [evidence()]}
material, raw, facts = synthetic_fixture([
    {"op": "deliver", "target": "label_receiver", "inputs": [inp()], "input_contract": contract},
    {"op": "receive", "location": "label_receiver", "inputs": [inp()], "output": "receipt",
     "input_contract": contract}], output="receipt", return_demand=True, source=SOURCE)
annotation = facts.annotation
files = joint_source_files(annotation["material"])
binding = input_contract_binding(files=files, cfg=facts.cfg, task=annotation["task"],
    raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"],
    mapping=annotation["mapping"])
checks = [{"contract_id": entry["id"], "status": "rejected",
    "reason": "The source explicitly requires argument b, but the actual call has only argument a; b is absent.",
    "evidences": [evidence()]} for entry in annotation["compiled_annotation"]["input_contracts"]]
receipt = build_input_contract_review(files=files, cfg=facts.cfg, annotation=annotation,
    review={"status": "complete", "availability": {"task": True, "cfg": True, "annotation": True},
        "review": {"schema_version": SOURCE_REVIEW_VERSION, "outcome": "completed",
                   "findings": [], "input_contract_checks": checks}},
    review_material={"input_contract_binding": binding, "partial": False})
before = canonical_sha256(facts.records)
engine = DemandEngine(facts, Task.model_validate(material["task"]), annotation, joint_demands(annotation),
    build_demand_target_index(facts.cfg, raw), input_contract_review=receipt)
result = engine.solve()
extended = [requirement, {**deepcopy(requirement), "input_index": 1}]
try:
    check_input_coverage(extended, 1)
except ValueError as error:
    extension = {"accepted": False, "error": str(error)}
else:
    extension = {"accepted": True}
report = {
    "schema_version": "skillflow-missing-slot-offline-audit-v1",
    "source": SOURCE,
    "scope": "One constructed offline source-explicit example; no real source/model/Skill execution.",
    "attempt_to_add_missing_slot_to_actual_input_contract": extension,
    "review_checks": checks,
    "demand_status": result["status"],
    "diagnostic_codes": sorted({row["code"] for row in result["diagnostics"]}),
    "known_missing_or_wrong_input_findings": [row for row in result["input_findings"]
        if row["kind"] in {"missing_input", "wrong_input"}],
    "actual_input_counts": {key: len(info["record"]["inputs"]) for key, info in engine.ops.items()
        if info["spec"]["op"] in {"deliver", "receive"}},
    "forward_records_unchanged": before == canonical_sha256(facts.records),
    "input_assessments": result["input_assessments"],
}
assert not extension["accepted"]
assert "input_contract_rejected" in report["diagnostic_codes"]
assert not report["known_missing_or_wrong_input_findings"]
assert report["forward_records_unchanged"]
Path(__file__).with_name("result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in report.items()
    if key not in {"input_assessments", "review_checks"}}, ensure_ascii=False))
