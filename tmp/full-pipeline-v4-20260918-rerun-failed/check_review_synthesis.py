import importlib.util
import json
from collections import Counter
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
tools = repo / "packages/skill-ir/experiments/security_profile/tools"
spec = importlib.util.spec_from_file_location("synthesis_exporter", tools / "export_full_pipeline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
run = repo / "packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed"
temporary = Path(__file__).resolve().parent
manifest = module.read_json(run / "manifest.json")
origins = module.execution_origins(run, manifest["cases"])
rows = []
for case in manifest["cases"][:24]:
    result = module.read_json(run / case["run_dir"] / "result.json")
    selected = result["selection"]
    row = {"selected_revision": selected["revision"], "graph_sha256": selected["graph_sha256"],
           "cfg": result["feedback"]["last_valid_cfg"]}
    review = module._assistant_review(temporary / "assistant-reviews", run, case, result, row)
    assert sum(record["matches_selected_graph"] for record in review["reviews"]) == 1
    assert module.canonical_sha256(row["cfg"]) == selected["graph_sha256"]
    rows.append({"case_id": case["case_id"], "sample_id": case["sample_id"], **selected,
                 "annotation_status": result["annotation"]["status"],
                 "profile_count": len(result["annotation"].get("profiles", {})),
                 "unresolved_count": len(result["annotation"].get("unresolved", [])),
                 "source_run_id": origins[case["case_id"]]["source_run_id"],
                 "execution_kind": origins[case["case_id"]]["kind"],
                 "review_file": review["source_file"], "review_sha256": review["source_sha256"]})
evidence = {"run_id": run.name, "scope": "001-024 only", "reviewer": "assistant", "human_confirmed": False,
            "formal_thirty_case_acceptance": False, "cases": rows,
            "feedback_statuses": dict(Counter(row["feedback_status"] for row in rows)),
            "annotation_statuses": dict(Counter(row["annotation_status"] for row in rows)),
            "profile_count": sum(row["profile_count"] for row in rows),
            "unresolved_count": sum(row["unresolved_count"] for row in rows)}
module.write_json(temporary / "review-synthesis-001-024-evidence.json", evidence)
print(json.dumps({key: value for key, value in evidence.items() if key != "cases"}, ensure_ascii=False))
for identifier in ("009", "015", "018"):
    case = next(case for case in manifest["cases"] if case["case_id"] == identifier)
    result = module.read_json(run / case["run_dir"] / "result.json")
    row = module.load_case(run, case, result, repo / "dataset/skills", renderer=manifest["renderer"]["path"])
    print("TARGET_SOURCE", identifier, json.dumps(row["source"]["files"], ensure_ascii=False))
    if identifier == "009":
        print("TARGET_GRAPH", identifier, json.dumps(row["cfg"]["blocks"]["block_001"], ensure_ascii=False))
        print("TARGET_FINDING", identifier, json.dumps(next(finding for finding in row["audit"]["findings"] if finding["id"] == "finding_3"), ensure_ascii=False))
    elif identifier == "015":
        print("TARGET_APPENDS", identifier, json.dumps([{"block_id": block["block_id"], "block_constraints": block["constraints"], "instruction": ir} for block in row["cfg"]["blocks"].values() for ir in block["instructions"] if "append" in ir["opcode"]], ensure_ascii=False))
        print("TARGET_FINDING", identifier, json.dumps(next(finding for finding in row["audit"]["findings"] if finding["id"] == "finding_10"), ensure_ascii=False))
    else:
        print("TARGET_ENVIRONMENT", identifier, json.dumps(row["cfg"]["blocks"]["block_002"], ensure_ascii=False))
