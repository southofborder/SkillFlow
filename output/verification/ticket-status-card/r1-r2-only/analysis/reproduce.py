"""Offline task ablation on the previously selected four-instruction ticket example."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
sys.path.insert(0, str(ROOT / "src"))
from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _digest
from skillflow.document_guided.fragments import assemble_fragments
from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review, input_contract_binding
from skillflow.doe.input_contract_scopes import input_contract_review_inventory
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.runner import _calculate


def main():
    run = Path(json.loads((OUT.parents[1] / "dispatch.json").read_bytes())["run"])
    assert not OUT.is_relative_to(run)
    hashes = {}

    def read(path, expected=None):
        data = (run / path).read_bytes()
        hashes[path] = sha256(data).hexdigest()
        assert expected is None or hashes[path] == expected, path
        return json.loads(data)

    def save(path, value):
        (OUT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf8")

    selection = read("selection.json")
    selected = {key:read(x["path"], x["sha256"]) for key,x in selection.items()}
    cfg, original_task, manifest = selected["cfg"]["cfg"],selected["task"],selected["annotation"]
    assert manifest["manifest_sha256"] == canonical_sha256({k:v for k,v in manifest.items() if k!="manifest_sha256"})
    task = deepcopy(original_task)
    assert [x["id"] for x in task["requirements"]] == ["R1","R2","R3"] and not task["issues"]
    task["requirements"] = task["requirements"][:2]
    task["task_sha256"] = canonical_sha256({k:v for k,v in task.items() if k!="task_sha256"})
    frozen = read("source/inputs/snapshot.json")["files"]
    assert len(frozen)==1 and frozen[0]["path"]=="SKILL.md"
    data = (run / "source/inputs/package/SKILL.md").read_bytes()
    source_sha = sha256(data).hexdigest()
    assert source_sha == frozen[0]["raw_sha256"]
    source = {"files":[{"path":"SKILL.md","content":data.decode(),"sha256":source_sha}],
              "source_sha256":_digest([{"path":"SKILL.md","sha256":source_sha}])}
    files = {"skill/SKILL.md":data.decode()}
    processing,correspondence,sensitivity = (read("steps/"+s+"/value.json") for s in ("processing","task-correspondence","sensitivity"))
    original_material = prepare_material(source,cfg,task_baseline=original_task)
    original = assemble_fragments(processing,correspondence,sensitivity,original_material)
    for name, rebuilt in zip(("wire-annotation","raw-annotation","compiled-response","compilation-map"),original):
        name="audit/"+name+".json"
        assert read("annotation/"+name,manifest["artifacts"][name]) == rebuilt, name
    correspondence["realizations"] = [x for x in correspondence["realizations"] if x["requirement_id"]!="R3"]
    assert len(correspondence["operation_demands"])==1
    demands = correspondence["operation_demands"][0]["demands"]
    assert [x["requirement_id"] for x in demands] == ["R1","R1","R2","R3"]
    correspondence["operation_demands"][0]["demands"] = demands[:3]
    material = prepare_material(source,cfg,task_baseline=task)
    wire,raw,compiled,mapping = assemble_fragments(processing,correspondence,sensitivity,material)
    assert original[2]["ir_semantics"]==compiled["ir_semantics"]
    assert original[2]["locations"]==compiled["locations"]
    assert original[2]["input_contracts"]==compiled["input_contracts"]
    solved=_calculate(cfg,to_payload(compiled),read("propagation/audit/initial-data.json"),
                      read("propagation/audit/initial-state.json"))
    facts=materials_from_result(solved,material=material,raw_annotation=raw,compiled_annotation=compiled,mapping=mapping,
                                wire_annotation=wire)
    saved_records=read("propagation/records.json")
    def completion_version(records):
        return records["ir_003"]["events"][1]["atomic_ops"][0]["outputs"][0][0]
    completion_from, completion_to=completion_version(saved_records),completion_version(facts.records)
    assert json.loads(json.dumps(saved_records).replace(completion_from, completion_to))==facts.records
    assert facts.sinks==read("propagation/sinks.json")
    source_review=read("review/result.json")
    review_inputs=read("review/inputs.json")
    previous_receipt=read("doe/audit/input-contract-review.json")
    binding=input_contract_binding(files=files,cfg=cfg,task=task,raw_annotation=raw,compiled=compiled,mapping=mapping)
    inventory=input_contract_review_inventory(cfg=cfg,raw_annotation=raw,compiled=compiled,mapping=mapping)
    assert inventory==review_inputs["input_contract_inventory"]
    assert all(previous_receipt[k]==binding[k] for k in ("contracts_sha256","obligations_sha256","source_sha256","cfg_sha256"))
    assert previous_receipt["annotation_sha256"]!=binding["annotation_sha256"]
    # This is a controlled scenario: hold ONLY the two unchanged board-interface judgments fixed.
    # The original full source review cannot be claimed as approval of the alternative Task.
    assert len(source_review["review"]["input_contract_checks"])==2
    for name in ("findings","gap_checks","source_input_findings","input_projection_checks"):
        assert source_review["review"][name] == []
    projected_review={"status":"complete","review":source_review["review"],
                      "availability":{"task":False,"cfg":True,"annotation":False}}
    review_material={"input_contract_binding":binding,"input_contract_inventory":inventory,"annotation":wire,"partial":True}
    scope_receipt=build_input_contract_review(files=files,cfg=cfg,annotation=facts.annotation,
                            review=projected_review,review_material=review_material)
    assert not scope_receipt["source_review_complete"]
    assert scope_receipt["checks"]==previous_receipt["checks"]
    assert checked_input_contract_review(scope_receipt,files=files,cfg=cfg,annotation=facts.annotation)==scope_receipt
    result=prepare_joint_sensitivity_review(facts,facts.annotation,input_contract_review=scope_receipt)
    doe,backward=result.to_dict(),result.demand_dict()
    by_site=[]
    for sink in doe["sinks"]:
        boundary=sink["boundary"]
        rows=[]
        for row in sink["data_reviews"]:
            sig=doe["derivations"]["sensitivity"][row["derivation_id"]]
            rows.append({"path":sig["path"],"relation":sig["relation"],"data_id":sig["data_id"],
                         "conclusion":row["conclusion"],"reduction":row.get("reduction"),
                         "demand_refs":row["demand_refs"],"reason":row["reason"]})
        by_site.append({"boundary":boundary,"reviews":rows})
    summary={"scenario":"Counterfactual R1 and R2 only; actual Skill continues to send the original whole ticket.",
             "original_run":str(run),"original_selection":selection,"input_file_sha256":hashes,
             "frozen_skill_sha256":source_sha,"original_task_sha256":original_task["task_sha256"],
             "counterfactual_task_sha256":task["task_sha256"],"model_calls":0,"skill_executions":0,
             "forward_records_equal_modulo_opaque_completion_id":True,
             "opaque_completion_id_renaming":[completion_from,completion_to],
             "interface_checks":"Original two board-interface checks verified and held fixed on identical contracts and obligation inventory. No new source review of the scenario.",
             "full_scenario_source_review":False,"old_contract_binding":previous_receipt["contracts_sha256"],
             "new_contract_binding":binding["contracts_sha256"],"forward":solved.status,"backward":backward["status"],
             "doe":doe["status"],"sites":by_site}
    for path,value in (("summary.json",summary),("doe.json",doe),("backward.json",backward),("task.json",task),
                       ("input-contract-review.json",scope_receipt)):
        save(path,value)
    print([(s["boundary"]["target"],[(v["conclusion"],v["path"],v["reduction"] is not None) for v in s["reviews"]]) for s in by_site])


if __name__=="__main__":
    main()
