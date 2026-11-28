"""Rebuild the separate offline evaluation of the terminal selected model bundle and one archived handoff."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if not any((Path(path) / "skillflow/document_guided/local_call_transfers.py").is_file() for path in sys.path):
    sys.path.insert(0, str(ROOT / "src"))

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _digest
from skillflow.document_guided.fragments import assemble_fragments
from skillflow.document_guided.fragment_wire import expand_processing_response
from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.runner import _calculate


def summarize_boundaries(doe, backward, solved):
    signals = doe["derivations"]["sensitivity"]
    demands = backward["derivations"]
    results = {}
    for sink in doe["sinks"]:
        ir = sink["boundary"]["instruction_id"]
        row = results.setdefault(ir, {"target":sink["boundary"]["target"], "comparisons": [], "payload_operations": [],
                                     "credential_origins": [], "limitations": []})
        row["payload_operations"].extend(r["operation_id"] for r in sink["actual_payload"])
        row["limitations"] = sorted(set(row["limitations"]) | set(sink["limitations"]))
        for comparison in sink["data_reviews"]:
            sid = comparison["derivation_id"]
            row["comparisons"].append({"id": comparison["id"], "path": signals[sid]["path"],
                "operation_id": comparison["operation_id"], "input_index": comparison["input_index"],
                "conclusion": comparison["conclusion"]})
            if signals[sid]["path"] != ["params","key"]:
                continue
            pending, seen = [sid], set()
            while pending:
                parent = pending.pop()
                if parent in seen:
                    continue
                seen.add(parent)
                signal = signals[parent]
                if "explicit_declaration" in signal["rules"]:
                    root = {k:signal[k] for k in ("declaration_id", "data_id", "label")}
                    if root not in row["credential_origins"]:
                        row["credential_origins"].append(root)
                pending.extend(signal["parents"])
    for ir, acquisition in [("ir_049", "ir_034"), ("ir_076", "ir_067")]:
        sink = results[ir]
        roots = {s["data_id"] for s in sink["credential_origins"]}
        matching = {key: value for key,value in demands.items()
                    if value["node"]["instruction_id"] == acquisition
                    and roots.intersection(value["node"]["data_ids"])
                    and value["requirement_id"] == "R9" and not value["conservative"]}
        sink["precise_R9_demands_at_credential_acquisition"] = sorted(matching)
        sink["acquisition_instruction"] = acquisition
        sink["precise_R9_params_key_demands_at_GET"] = sorted(key for key, value in demands.items()
            if value["node"]["instruction_id"] == ir and value["path"] == ["params","key"]
            and value["requirement_id"] == "R9" and not value["conservative"])
    assert not ({r["data_id"] for r in results["ir_049"]["credential_origins"]} &
                {r["data_id"] for r in results["ir_076"]["credential_origins"]})
    error_stdout = results.setdefault("ir_063", {"target":"stdout","payload_operations":[],"comparisons":[],
                                                "credential_origins":[],"limitations":[]})
    error_stdout["coverage"] = solved.coverage["ir_063"]
    error_stdout["local_diagnostics"] = [r for r in doe["diagnostics"] if r.get("instruction_id") == "ir_063"]
    return results


def main(run, out, *, initial_control=False):
    inputs = {}
    def read(path, digest=None):
        path = Path(path).as_posix()
        data = (run / path).read_bytes()
        inputs[path] = sha256(data).hexdigest()
        if digest is not None and inputs[path] != digest:
            raise ValueError("Sealed input changed: " + path)
        return json.loads(data)
    def ref(path, root=run):
        return (root / path).resolve().relative_to(run).as_posix()
    def write(path, value):
        dest = out / path
        data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
        dest.write_bytes(data)
        return sha256(data).hexdigest()
    if run == out or out.is_relative_to(run) or run.is_relative_to(out):
        raise ValueError("Derived output must be separate from the recorded run.")
    out.mkdir(parents=True, exist_ok=True)
    terminal = read("result.json")
    if terminal["status"] in {"running", "prepared"}:
        raise ValueError("The controller has not published a terminal selection.")
    selection = read("selection.json")
    selected = terminal["selected_annotation"]
    assert selection["annotation"]["path"] == selected + "/manifest.json"
    basis = "annotation" if initial_control else selected
    owner = run / basis
    basis_manifest = ref("manifest.json", owner)
    if initial_control:
        manifest = read(basis_manifest)
    else:
        manifest = read(basis_manifest, selection["annotation"]["sha256"])
    assert manifest["manifest_sha256"] == canonical_sha256({k:v for k,v in manifest.items() if k != "manifest_sha256"})
    refs = read(ref("inputs/references.json",owner), manifest["files"]["inputs/references.json"])
    cfg = read(selection["cfg"]["path"], selection["cfg"]["sha256"])["cfg"]
    task = read(selection["task"]["path"], selection["task"]["sha256"])
    assert cfg == read("graph/selected.json")["cfg"]
    assert ref(refs["cfg"]["path"],owner) == selection["cfg"]["path"]
    assert refs["cfg"]["sha256"] == selection["cfg"]["sha256"]
    def fragment(name):
        link = refs["fragment_steps"][name]
        folder = (owner / link["path"]).resolve()
        assert read(ref("manifest.json",folder))["manifest_sha256"] == link["manifest_sha256"]
        result = read(ref("result.json",folder))
        value = read(ref(result["value_file"], folder))
        if result["value_sha256"] not in {inputs[ref(result["value_file"],folder)], canonical_sha256(value)}:
            raise ValueError("Fragment value differs from its saved result: " + name)
        return value
    def audit(name):
        name = "audit/" + name + ".json"
        return read(ref(name,owner), manifest["artifacts"][name])
    source = []
    package = run / "source/inputs/package"
    snapshot = read("source/inputs/snapshot.json")
    for sealed in snapshot["files"]:
        name = sealed["path"]
        path = package / name
        data = path.read_bytes()
        assert sha256(data).hexdigest() == sealed["raw_sha256"]
        inputs[path.relative_to(run).as_posix()] = sha256(data).hexdigest()
        source.append({"path": name, "content": data.decode("utf8"), "sha256": sha256(data).hexdigest()})
    material = prepare_material({"files": source, "source_sha256": _digest([
        {"path": r["path"], "sha256": r["sha256"]} for r in source])}, cfg, task_baseline=task)
    files = {"skill/" + r["path"]: r["content"] for r in source}
    target = "ir_045"
    candidate_path = "steps/processing/calls/a002/merged-candidate.json"
    archived = expand_processing_response(read(candidate_path))["ir_semantics"][target]
    assert archived["output_bindings"] == [{"output_index": i,"value":{"kind":"input","index":i+1}} for i in range(4)]
    attempts = "steps/processing/calls/"
    assert expand_processing_response(read(attempts+"a001/response.json"))["ir_semantics"][target] == archived
    read(attempts+"a002/response.json")
    validation = read(attempts+"a002/validation.json")
    assert [(e["code"],e["path"]) for e in validation["diagnostics"]] == [
        ("source_action_role", "/ir_semantics/ir_045/action_bindings")]
    read(attempts+"chain.json")
    processing, correspondence, sensitivity = map(fragment, ("processing", "task-correspondence", "sensitivity"))
    prior = audit("wire-annotation")
    prior_validation = prior.get("_validation_gaps", [])
    if target in processing["ir_semantics"]:
        raise ValueError("The selected processing already models this transfer.")
    removed = [g for g in processing["processing_gaps"] if g["instruction_id"] == target and g.get("unmodeled")]
    removed_validation = [g for g in prior_validation if g["instruction_id"] == target and g.get("unmodeled")]
    assert len(removed) + len(removed_validation) == 1
    if removed:
        assert removed[0]["outputs"] == [0,1,2,3] and not removed[0].get("locations")
    if removed_validation:
        assert any(e["code"] == "source_action_role" for e in removed_validation[0]["validation_errors"])
    processing["ir_semantics"][target] = archived
    processing["processing_gaps"] = [g for g in processing["processing_gaps"] if g not in removed]
    valid = [g for g in prior_validation if g not in removed_validation]
    wire, raw, compiled, mapping = assemble_fragments(processing, correspondence, sensitivity, material, validation_gaps=valid)
    previous = audit("compiled-response")
    for key in ("demands","realizations","locations"):
        assert wire[key] == prior[key], key
    assert {k:v for k,v in wire["ir_semantics"].items() if k != target} == prior["ir_semantics"]
    assert wire["processing_gaps"] == [g for g in prior["processing_gaps"] if g not in removed]
    assert wire.get("_validation_gaps", []) == valid
    assert len(compiled["ir_semantics"]) == len(previous["ir_semantics"]) + 1
    assert {k:v for k,v in compiled["ir_semantics"].items() if k != target} == previous["ir_semantics"]
    readmission = {"instruction_id":target,"archived_diagnostic_code":"source_action_role","source_candidate":candidate_path,
        "pointer":"/ir_semantics/" + target,"row_sha256":canonical_sha256(archived),"superseded_source_gaps":removed,
        "superseded_validation_gaps":removed_validation,"unchanged_selected_ir_records":len(prior["ir_semantics"]),
        "new_review":"unavailable","unrelated_same_ir_gaps_retained":[g for g in wire["processing_gaps"] if g["instruction_id"]==target]}
    baseline = _calculate(cfg, to_payload(previous), None, None)
    solved = _calculate(cfg, to_payload(compiled), None, None)
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled,
                                  mapping=mapping, wire_annotation=wire)
    check = build_input_contract_review(files=files, cfg=cfg, annotation=facts.annotation)
    assert checked_input_contract_review(check, files=files, cfg=cfg, annotation=facts.annotation) == check
    review = prepare_joint_sensitivity_review(facts, facts.annotation, input_contract_review=check)
    doe, backward = review.to_dict(), review.demand_dict()
    selected_review = "revision/review/result.json" if selected.startswith("revision/") else "review/result.json"
    basis_review = "review/result.json" if initial_control else selected_review
    review_provenance = {"selected_review": selected_review, "basis_review":basis_review,"official_selected_annotation":selected,
        "official_repair_review":terminal.get("repair_review"), "official_annotation_review":terminal.get("annotation_review"),
        "official_limitations":terminal.get("limitations",[]),
        "derived_review_status":"unavailable","reason":"The compiled annotation digest changed. Historical checks and findings remain attached to their original response.",
        "records": {}}
    for rel in ("review/result.json","revision/review/result.json"):
        if (run/rel).is_file():
            reviewed = read(rel)
            review_provenance["records"][rel] = {"sha256":inputs[rel], "status":reviewed["status"],
                "official_response":reviewed, "findings":(reviewed.get("review") or {}).get("findings",[])}
    from skillflow.document_guided import local_call_transfers
    import skillflow
    package = Path(skillflow.__file__).resolve().parent
    python_files = {"src/skillflow/" + p.relative_to(package).as_posix(): sha256(p.read_bytes()).hexdigest()
                    for p in package.rglob("*.py") if not p.is_relative_to(package / "_lean_sources")}
    old_impl = read("manifest.json")["implementation"]
    delta = {p:{"old":old_impl["files"].get(p),"new":h} for p,h in python_files.items() if old_impl["files"].get(p) != h}
    artifact_hashes = {name: write(name, value) for name, value in [
        ("input-contract-review.json", check), ("doe.json", doe), ("backward.json", backward),
        ("derived-wire.json", wire), ("derived-raw.json", raw), ("derived-compiled.json", compiled), ("derived-mapping.json",mapping),
        ("forward.json",{"status":solved.status,"coverage":solved.coverage,"diagnostics":solved.diagnostics}),
        ("source-review-provenance.json",review_provenance),
        ("forward-records.json", facts.records), ("forward-data.json",facts.data), ("forward-sinks.json", facts.sinks),
        ("boundary-comparisons.json", summarize_boundaries(doe, backward, solved))]}
    receipt = {"description": ("Earlier automatic assembly with the original complete a002 processing now validated. "
        "No source review certified this derivative. The handler contract assumes its prefix succeeds. Earlier failures and partial writes remain unresolved."
        if initial_control else "Offline derivative of the terminal selected bundle with a single readmission from the original processing candidate."),
        "basis":"initial_control" if initial_control else "terminal_selection",
        "basis_annotation":{"path":basis_manifest,"sha256":inputs[basis_manifest]},
        "run":run.name,"selected_annotation":selected,"selection":selection,"selected_review":selected_review,
        "basis_review":basis_review,"readmission":readmission,
        "official_implementation":old_impl["sha256"],"derived_python_tree_sha256":canonical_sha256(python_files),"changed_python_files":delta,
        "script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "new_model_calls": 0, "executed_skill": False, "seed": None, "source_sha256": material["source"]["source_sha256"],
        "task_sha256": task["task_sha256"], "inputs": inputs, "compiled_sha256": canonical_sha256(compiled),
        "modeled_IR": len(compiled["ir_semantics"]), "source_gaps": len(compiled["processing_gaps"]),
        "baseline_coverage": dict(Counter(baseline.coverage.values())), "derived_coverage": dict(Counter(solved.coverage.values())),
        "review_status": check["review_status"], "receipt_sha256": check["receipt_sha256"], "doe_status": doe["status"],
        "demand_status": backward["status"], "artifact_sha256": artifact_hashes,
        "comparisons": dict(Counter(r["conclusion"] for s in doe["sinks"] for r in s["data_reviews"])),
        "assessment_count": len(backward["input_assessments"]),
        "range_counts": dict(Counter(r["status"] for a in backward["input_assessments"] for r in a["ranges"]))}
    write("receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=ROOT / "experiments/doe/runs/document-guided-google-search-downstream-high-20261125-211940")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--initial-control", action="store_true")
    args = parser.parse_args()
    destination = args.out or (HERE / "initial-control" if args.initial_control else HERE)
    main(args.run.resolve(), destination.resolve(), initial_control=args.initial_control)
