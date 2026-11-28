"""Read-only forensics from small saved artifacts; no analysis/model execution."""
import collections
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
PARENT = ROOT / "experiments/doe/runs/document-guided-ga4-runtime-locality-high-20261117-205158"
OUT = Path(__file__).resolve().parent / "independent-candidate-scale-forensics.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


records = read(RUN / "propagation/records.json")
data = {row["id"]: row for row in read(RUN / "propagation/data.json")}
annotation = read(RUN / "annotation/audit/compiled-response.json")
processing = read(RUN / "steps/processing/value.json")
current_declarations = read(RUN / "steps/sensitivity/value.json")["declarations"]
parent_declarations = read(PARENT / "steps/sensitivity/value.json")["declarations"]
creation = [row for row in current_declarations if "at this handle" in row["label"]]
seed_records = []
for ir, sem in annotation["ir_semantics"].items():
    for declaration in sem.get("sensitivity", []):
        if "at this handle" not in declaration["label"]:
            continue
        for ei, event in enumerate(sem.get("events", [])):
            for oi, op in enumerate(event.get("atomic_ops", [])):
                if op.get("output") != declaration["value"].get("name"):
                    continue
                saved_events = records.get(ir, {}).get("events", [])
                saved_ops = saved_events[ei].get("atomic_ops", []) if len(saved_events) > ei else []
                ids = saved_ops[oi]["outputs"][0] if len(saved_ops) > oi else []
                seed_records.append({"instruction_id": ir, "event_index": ei, "op_index": oi,
                                     "declaration": declaration, "data_ids": ids})

components = []
output_branch = {}
for ir in ["ir_411", "ir_412", "ir_413", "ir_414"]:
    events = records[ir]["events"]
    original = events[12]["atomic_ops"][0]["inputs"][0][0]
    branches = {original: "object"}
    for ei in [12, 17]:
        branch = events[ei]["case"]["name"]
        for identity in events[ei]["atomic_ops"][0]["outputs"][0]:
            branches[identity] = branch
    final_compute = events[19]["atomic_ops"][0]
    for alt in final_compute["alternatives"]:
        for identity in alt["outputs"][0]:
            output_branch[identity] = branches[alt["inputs"][1][0]]
    components.append({"instruction_id": ir, "original_range_data_id": original,
                       "range_cases": branches, "input_cardinalities": list(map(len, final_compute["inputs"])),
                       "output_cardinalities": list(map(len, final_compute["outputs"])),
                       "alternatives": final_compute["alternatives"],
                       "compiled_compute": annotation["ir_semantics"][ir]["events"][19],
                       "per_case_alternative_bindings": {
                           str(ei): [a["bindings"] for a in events[ei]["atomic_ops"][0]["alternatives"]]
                           for ei in [12, 17]}})

build = records["ir_415"]["events"][0]["atomic_ops"][0]
combinations = []
for alt in build["alternatives"]:
    combinations.append({"branches": [output_branch[ids[0]] for ids in alt["inputs"]],
                         "data_id": alt["outputs"][0][0], "bindings": alt["bindings"]})
mixed = [row for row in combinations if len(set(row["branches"])) > 1]
witness = next(row for row in mixed if "object" in row["branches"] and "default" in row["branches"])
shared_counts = collections.Counter(identity for row in seed_records for identity in row["data_ids"])
code_comparison = {}
for name in ["doe/sensitivity_engine.py", "doe/sensitivity_report.py", "doe/sensitivity_material.py",
             "propagation/interpreter.py", "propagation/data/registry.py", "propagation/annotation/compiler.py"]:
    relative = Path("src/skillflow") / name
    current = ROOT / relative
    prior = PARENT / "implementation-snapshot" / relative
    code_comparison[str(relative)] = {"current_sha256": digest(current), "parent_sha256": digest(prior),
                                      "byte_identical": current.read_bytes() == prior.read_bytes()}

input_paths = [RUN / path for path in ["propagation/records.json", "propagation/data.json",
              "annotation/audit/compiled-response.json", "steps/processing/value.json", "steps/sensitivity/value.json"]]
input_paths += [PARENT / "steps/sensitivity/value.json"]
report = {
    "audit_kind": "small_saved_artifact_forensics_no_engine_or_model_execution",
    "run": str(RUN), "parent": str(PARENT), "huge_doe_result_loaded": False,
    "inputs": [{"path": str(p), "bytes": p.stat().st_size, "sha256": digest(p)} for p in input_paths],
    "current_declaration_count": len(current_declarations), "parent_declaration_count": len(parent_declarations),
    "creation_declaration_count": len(creation), "creation_ir_count": len({d['instruction_id'] for d in creation}),
    "creation_local_names": dict(collections.Counter(d["value"]["name"] for d in creation)),
    "creation_seed_records": seed_records,
    "creation_resolved_data_fanout": dict(shared_counts),
    "creation_shared_data": {identity: data[identity] for identity in shared_counts},
    "component_variants": components,
    "build": {"instruction_id": "ir_415", "input_cardinalities": list(map(len, build["inputs"])),
              "output_cardinalities": list(map(len, build["outputs"])),
              "alternative_count": len(build["alternatives"]),
              "branch_combinations": combinations, "mixed_category_combination_count": len(mixed),
              "mixed_object_default_witness": {**witness, "data": data[witness["data_id"]]}},
    "storage_payload_cardinality": len(records["ir_416"]["events"][0]["atomic_ops"][0]["inputs"][0]),
    "site_and_default_computes": {
        str(ei): {"compiled": annotation["ir_semantics"]["ir_411"]["events"][ei],
                  "record": records["ir_411"]["events"][ei]} for ei in [8, 14]},
    "site_contract": processing["ir_semantics"]["ir_411"]["segments"][1]["ops"][1]["demand_transfer"],
    "default_contract": processing["ir_semantics"]["ir_411"]["segments"][2]["cases"][2]["segments"][0]["ops"][1]["demand_transfer"],
    "code_comparison": code_comparison,
    "interpretation_limits": [
        "Repeated declaration identities preserve source sites; they are not 100 different credential values.",
        "Possible influence is not evidence that plaintext credentials occur in the real response or storage payload.",
        "Source type/truthiness conditions correlate across the shared argument, but runtime prose is not executable; no shared typed discriminator was present in these saved alternatives.",
        "Three uniform branch categories do not imply exactly three concrete source executions; clock/environment observations and remote responses can differ.",
        "The backend agent independently counted 83442 unique review candidates; this helper does not load or recount the large DOE result."
    ]
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"report": str(OUT), "creation_seed_data": dict(shared_counts),
                  "build_inputs": report["build"]["input_cardinalities"],
                  "build_outputs": report["build"]["output_cardinalities"],
                  "mixed_branch_categories": len(mixed)}))
