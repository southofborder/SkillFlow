"""Read frozen 010 JSON only; no SkillFlow imports or analysis execution."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "experiments/doe/runs/document-guided-010-backend-r3-high-20261104-132226"
OUT = Path(__file__).resolve().parent
hashes = {}


def read(relative):
    payload = (RUN / relative).read_bytes()
    hashes[relative] = hashlib.sha256(payload).hexdigest()
    return json.loads(payload)


data = {row["id"]: row for row in read("propagation/data.json")}
records = read("propagation/records.json")
support = read("doe/audit/demand-support.json")
doe = read("doe/doe-result.json")
processing = read("steps/processing/value.json")
compiled = read("annotation/audit/compiled-response.json")
candidate = read("steps/task-correspondence/calls/a002/merged-candidate.json")
review = read("review/result.json")
sinks = read("propagation/sinks.json")
read("task/task.json")
read("graph/selected.json")
read("steps/sensitivity/value.json")
read("steps/task-correspondence/value.json")
for path in sorted((RUN / "source/inputs/package").rglob("*")):
    if path.is_file():
        hashes[path.relative_to(RUN).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()


def content(data_id):
    value = data[data_id]["content"]
    if value["form"] == "loop_summary":
        assert len(value["variants"]) == 1
        return value["variants"][0]["content"]
    return value


def object_fields(data_id):
    """Follow only saved object descriptors; never infer unknown contents."""
    value = content(data_id)
    if value["form"] == "selection" and value["path"] == []:
        return object_fields(value["base"])
    if value["form"] == "known_parts":
        assert value["parts_complete"] is True
        assert all(len(part["path"]) == 1 for part in value["parts"])
        return {part["path"][0]: part["data"] for part in value["parts"]}
    if value["form"] == "field_updates":
        fields = object_fields(value["base"])
        assert all(len(part["path"]) == 1 for part in value["updates"])
        fields.update({part["path"][0]: part["data"] for part in value["updates"]})
        return fields
    raise ValueError(f"Unsupported saved object descriptor: {value['form']}")


def operation(ir, event):
    return records[ir]["events"][event]["atomic_ops"][0]


def key(bindings):
    return tuple(sorted(bindings.items()))


deliver = operation("ir_016", 0)
receive = operation("ir_016", 1)
write = operation("ir_019", 0)
receive_by_path = {key(x["bindings"]): x for x in receive["alternatives"]}
write_by_path = {key(x["bindings"]): x for x in write["alternatives"]}
returned = records["ir_021"]["entry_state"]["bindings"][0]["data_ids"]
items_by_path = {key(data[x]["content"]["bindings"]): x for x in returned}
request = next(x for x in data.values() if x["origin"].get("acquired_from") == "storage:user-supplied request.json")
rows = []
for alternative in deliver["alternatives"]:
    binding_key = key(alternative["bindings"])
    argument = alternative["inputs"][0][0]
    fields = object_fields(argument)
    origins = {name: data[part]["origin"] for name, part in fields.items()}
    assert all(value["part_of"] == request["id"] for value in origins.values())
    assert all(value["path"] == (["term"] if name == "query" else [name]) for name, value in origins.items())
    paired_receive = receive_by_path[binding_key]
    assert paired_receive["inputs"] == alternative["inputs"]
    response = paired_receive["outputs"][0][0]
    total = write_by_path[binding_key]["inputs"][0][0]
    items = items_by_path[binding_key]
    assert content(total) == {"form": "selection", "base": response, "path": ["total"]}
    assert content(items) == {"form": "selection", "base": response, "path": ["items"]}
    rows.append({"from_date_present": "from_date" in fields, "limit_present": "limit" in fields,
                 "argument_id": argument, "argument_fields": fields, "field_origins": origins,
                 "bindings": alternative["bindings"], "response_id": response,
                 "saved_total_id": total, "returned_items_id": items})
rows.sort(key=lambda row: (row["from_date_present"], row["limit_present"]))
assert {(row["from_date_present"], row["limit_present"]) for row in rows} == {(False, False), (False, True), (True, False), (True, True)}
assert len(rows) == 4

definitions = {**doe["derivations"], **support["extra_derivations"]}
boundary_support = []
for sink in doe["sinks"]:
    if sink["boundary"]["sink_type"] == "model_observe":
        continue
    details = next(row for row in support["sinks"] if row["id"] == sink["id"])
    boundary_support.append({"boundary": sink["boundary"], "support": details,
                             "demand_records": {i: definitions[i] for i in details["demanded_information"] + details["conservative_retention"]}})

evidence = {
    "audit_kind": "independent static source and frozen JSON audit; not human gold or execution",
    "run": str(RUN),
    "source_claim_scope": "Finite named source relationships; no natural-language equivalence or complete sensitivity claim",
    "request": request,
    "optional_argument_combinations": rows,
    "presence_expressions": [row for row in compiled["expressions"] if row["target"]["instruction_id"] in ["ir_005", "ir_010"]],
    "write_annotation": processing["ir_semantics"]["ir_019"],
    "write_changes": write["changes"],
    "return_record": records["ir_021"],
    "mapping_attempts": [read(f"steps/task-correspondence/calls/a00{i}/validation.json") for i in [1, 2]],
    "rejected_conditions": {row["requirement_id"]: row["constraints"] for row in candidate["realizations"] if row["requirement_id"] in ["R4", "R6"]},
    "requirement_coverage": support["coverage"]["requirements"],
    "seed_derivation_counts": {row["requirement_id"]: {"seeds": len(row["seeds"]), "derivation_references": sum(len(seed["derivation_ids"]) for seed in row["seeds"])} for row in support["traceability"]["requirements"]},
    "sink_counts": dict(Counter(row["sink_type"] for row in sinks)),
    "boundary_demand_support": boundary_support,
    "demand_diagnostics": support["diagnostics"],
    "constraint_checks": doe["constraints"],
    "doe_coverage": doe["coverage"],
    "data_reviews": sum(len(row["data_reviews"]) for row in doe["sinks"]),
    "review": review,
    "input_sha256": hashes,
}
(OUT / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUT / "evidence.json"), "four_correlated_rows_verified": len(rows), "sink_counts": evidence["sink_counts"], "data_reviews": evidence["data_reviews"]}))
