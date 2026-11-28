"""Offline synthetic audit; never reads run responses or invokes models/Skills."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.input_assessments import deletable_reduction
from skillflow.doe.input_contract_review import build_input_contract_review, input_contract_binding
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.binding_examples import evidence, local
from skillflow.propagation.contracts.joint import joint_source_files
from skillflow.propagation.contracts.task import Task
from tests.doe.test_sink_payload_seeds import synthetic_fixture, declared_goal


SOURCE = (
    "This synthetic example preserves the original display field at the label receiver's input. "
    "The label receiver interface requires display and token when its invocation must be preserved. "
    "It ignores service_note. The payload-only candidate declares only the display information "
    "obligation; the action-and-payload candidate additionally declares the receiver invocation obligation. "
    "These explicit alternatives test action and information preservation separately."
)


def literal(value):
    return {"kind": "literal", "value": value}


def review_receipt(material, facts, *, status="accepted"):
    annotation = facts.annotation
    files = joint_source_files(annotation["material"])
    checks = [{"contract_id": entry["id"], "status": status,
        "reason": "The synthetic source explicitly defines display and token as the interface requirements and service_note as ignored.",
        "evidences": [evidence()]}
        for entry in annotation["compiled_annotation"].get("input_contracts", [])]
    review_material = {"partial": False, "input_contract_binding": input_contract_binding(
        files=files, cfg=facts.cfg, task=annotation["task"], raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])}
    review = {"status": "complete", "availability": {"task": True, "cfg": True, "annotation": True},
        "review": {"schema_version": "skillflow-document-source-review-fragment-v3", "outcome": "completed",
            "findings": [], "input_contract_checks": checks}}
    return build_input_contract_review(files=files, cfg=facts.cfg, annotation=annotation,
        review=review, review_material=review_material)


def run_case(*, contract_present, action_seed, reviewed=True):
    build = {"op": "build", "container": "object", "output": "formatted", "parts": [
        {"path": ["display"], "value": literal("CAL-7")},
        {"path": ["token"], "value": literal("synthetic-interface-token")},
        {"path": ["service_note"], "value": literal("synthetic-internal-note")}]}
    deliver = {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")],
        "demands": [declared_goal("input", index=0, path=["display"])]}
    if action_seed:
        deliver["demands"].append(declared_goal("self", preserve="action"))
    if contract_present:
        deliver["input_contract"] = {"inputs": [{"input_index": 0,
            "required": [{"property": "value", "path": [field]} for field in ("display", "token")],
            "remainder": "independent", "reason": "Only display and token are required by this synthetic interface."}],
            "reason": "The synthetic receiver requires display and token and ignores service_note.",
            "evidences": [evidence()]}
    material, raw, facts = synthetic_fixture([build, deliver], source=SOURCE,
        registry_namespace="payload-only-contract-audit")
    original_records = deepcopy(facts.records)
    original_data = deepcopy(facts.data)
    targets = build_demand_target_index(facts.cfg, raw)
    candidate = joint_demands(facts.annotation)
    task = Task.model_validate(material["task"])
    receipt = review_receipt(material, facts) if reviewed else None
    engine = DemandEngine(facts, task, facts.annotation, candidate, targets, input_contract_review=receipt)
    result = engine.solve()
    assert facts.records == original_records and facts.data == original_data
    op = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "deliver")
    assessment = next(row for row in result["input_assessments"]
        if row["node_kind"] == "op_input" and row["operation_id"] == op and row["input_index"] == 0)
    data_id = engine.ops[op]["record"]["inputs"][0][0]
    reductions = {field: deletable_reduction(result, op, 0, data_id, [field])
        for field in ("display", "token", "service_note")}
    public = {"contract_present": contract_present, "reviewed": reviewed, "action_seed": action_seed,
        "propagation_status": "complete", "demand_status": result["status"],
        "source_review_complete": receipt["source_review_complete"] if receipt else None,
        "diagnostics": result["diagnostics"], "delivery_assessment": assessment,
        "deletable_reductions": reductions, "candidate": candidate,
        "action_derivations": [row for row in result["derivations"].values() if row["node"]["kind"] == "action"],
        "actual_deliver": deliver, "actual_inputs_preserved": facts.records == original_records and facts.data == original_data}
    return public, result, receipt


def main():
    artifact = {"audit": "isolated_offline_payload_only_tool_contract", "created_at": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE, "execution": "Fresh synthetic static propagation and demand analysis only; no model, Skill, historical response or replay.",
        "frozen_batch_implementation_sha256": "09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0",
        "files_sha256": {}, "cases": {}}
    for name in ["src/skillflow/doe/demand_engine.py", "src/skillflow/doe/input_contracts.py",
                 "src/skillflow/doe/input_assessments.py", "src/skillflow/doe/input_contract_review.py",
                 "tests/doe/test_sink_payload_seeds.py", str(Path(__file__).relative_to(ROOT)).replace("\\", "/")]:
        artifact["files_sha256"][name] = sha256((ROOT / name).read_bytes()).hexdigest()
    for name, present, action, reviewed in [
        ("missing_payload_only", False, False, True),
        ("accepted_payload_only", True, False, True),
        ("unreviewed_payload_only", True, False, False),
        ("missing_action_and_payload", False, True, True),
        ("accepted_action_and_payload", True, True, True)]:
        summary, result, receipt = run_case(contract_present=present, action_seed=action, reviewed=reviewed)
        artifact["cases"][name] = {"summary": summary, "result": result, "input_contract_review": receipt}
    output = Path(__file__).with_name("payload-only-tool-contract-reproduction.json")
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(artifact, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    for name, case in artifact["cases"].items():
        summary = case["summary"]
        print(json.dumps({"case": name, "status": summary["demand_status"],
            "diagnostics": [row["code"] for row in summary["diagnostics"]],
            "action_derivations": len(summary["action_derivations"]),
            "deletable": {field: value[0] for field, value in summary["deletable_reductions"].items()}}, ensure_ascii=False))
    print(str(output))


if __name__ == "__main__":
    main()
