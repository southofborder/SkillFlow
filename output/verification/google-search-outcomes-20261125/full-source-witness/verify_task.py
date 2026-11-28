"""Verify task and boundary evidence in the authored google-search witness offline."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CLOSED = ROOT / "experiments/doe/runs/document-guided-google-search-full-high-20261125-172053"
sys.path.insert(0, str(ROOT / "src"))

from skillflow.common.recording import canonical_sha256
from skillflow.doe.sensitivity_material import build_sensitivity_index
from skillflow.propagation.contracts.sensitivity import extract_sensitivity_candidate
from skillflow.propagation.contracts.task import checked_task, task_source_files
from skillflow.propagation.data import DataReferenceError, DataRegistry
from skillflow.propagation.data.summary import content_options


API = "https://www.googleapis.com/customsearch/v1"
SCRIPT = "skill/scripts/search.py"
REQUEST_KEY_PATH = ["params", "key"]
REQUIREMENT_SITES = {
    "R9": {"cli": ["ir_034", "ir_036"], "public": ["ir_054", "ir_056"]},
    "R10": {"cli": ["ir_038", "ir_040"], "public": ["ir_059", "ir_062", "ir_065"]},
    "R11": {"cli": ["ir_042", "ir_044"]},
    "R12": {"cli": ["ir_047", "ir_048", "ir_050", "ir_051"]},
}
KEY_SOURCES = {
    "cli": "runtime_context:process environment: GOOGLE_API_KEY",
    "public": "runtime_context:google_search.invocation.api_key",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def graph(value):
    return value.get("cfg", value)


def instruction_order(value):
    return {block: [op["id"] for op in row["instructions"]] for block, row in value["blocks"].items()}


def compatible_cfg(left, right):
    """A source span can move to the action owner while preserving graph and operands."""
    def instructions_without_metadata(value):
        return {block: [{k: v for k, v in op.items() if k != "metadata"} for op in row["instructions"]]
                for block, row in value["blocks"].items()}
    return (instructions_without_metadata(left) == instructions_without_metadata(right)
            and left["entry_block_id"] == right["entry_block_id"] and left["edges"] == right["edges"]
            and left.get("constraints") == right.get("constraints")
            and left.get("declared_context_keys") == right.get("declared_context_keys"))


def verify_material(folder, closed):
    source = load(folder / "source-bundle.json")
    files = {row["path"]: row for row in source["files"]}
    assert set(files) == {"SKILL.md", "scripts/search.py"}, "offline witness must retain both complete source files"
    for relative, row in files.items():
        original = (closed / "source/inputs/package" / relative).read_bytes()
        assert original == row["content"].encode("utf-8"), ("source bytes changed", relative)
        assert hashlib.sha256(original).hexdigest() == row["sha256"]
    task = load(folder / "task-extracted-unchanged.json")
    assert task == load(closed / "task/task.json"), "Task or its source evidence changed"
    checked_task(task, source_files=task_source_files(source), source_sha256=source["source_sha256"])
    reqs = {row["id"]: row for row in task["requirements"]}
    assert len(reqs) == 12
    for required, phrases in {"R9": (API, "API key as key"), "R10": ("before parsing",),
                              "R11": ("as JSON",), "R12": ("exception's string representation", "exit with status 1")}.items():
        assert all(phrase in reqs[required]["text"] for phrase in phrases), ("unexpected Task contents", required)
        assert any(row["file"] == SCRIPT for row in reqs[required]["evidences"])

    script = files["scripts/search.py"]["content"].splitlines()
    for number, phrase in {6: "def google_search(", 7: API, 10: "'key': api_key",
                           14: "requests.get(url, params=params)", 15: "raise_for_status()",
                           16: "return response.json()", 27: 'os.getenv("GOOGLE_API_KEY")',
                           35: "google_search(query, api_key, cse_id, num_results)",
                           36: "json.dumps(results, indent=2)", 38: 'print(f"Error: {str(e)}")',
                           39: "sys.exit(1)"}.items():
        assert phrase in script[number - 1], ("unexpected script evidence", number)

    authored = graph(load(folder / "authored-cfg.json"))
    original = graph(load(closed / "graph/selected.json"))
    order = instruction_order(authored)
    assert order == instruction_order(original) and sum(map(len, order.values())) == 65
    return {
        "source_sha256": source["source_sha256"], "task_sha256": task["task_sha256"],
        "task_requirement_count": len(reqs), "ir_count": 65,
        "same_graph_including_metadata": authored == original,
        "same_control_flow_and_operands": compatible_cfg(authored, original),
        "requirements": {req: {"text": reqs[req]["text"], "source_evidence": reqs[req]["evidences"],
                              "instruction_sites": sites} for req, sites in REQUIREMENT_SITES.items()},
        "source_evidence": {
            "cli_request_key": [27, 35, 10, 14], "public_request_key": [6, 10, 14],
            "cli_success_output": [35, 36], "cli_error_output": [37, 38, 39],
            "public_exceptions_escape": [6, 14, 15, 16],
        },
    }


def exact_required_ranges(demand, operation_id, index, data_id, requirement, path):
    """The reviewed data version and task-seeded requirement must occur at the same slot."""
    rows = []
    for assessment in demand["input_assessments"]:
        if (assessment["node_kind"] != "op_input" or assessment["operation_id"] != operation_id
                or assessment["input_index"] != index or data_id not in assessment["data_ids"]):
            continue
        for item in assessment["ranges"]:
            if not (item["status"] == "required" and item["property"] == "value" and item["path"] == path):
                continue
            for ref in item["demand_refs"]:
                row = demand["derivations"][ref]
                node = row["node"]
                if (row["requirement_id"] == requirement and not row["conservative"]
                        and node["kind"] == "op_input" and node["operation_id"] == operation_id
                        and node["slot"] == index and data_id in (row.get("outcome_data_ids") or node["data_ids"])):
                    rows.append(ref)
    return sorted(set(rows))


def sensitized_slots(sink, doe, key_declarations):
    for comparison in sink["data_reviews"]:
        item = doe["derivations"]["sensitivity"][comparison["derivation_id"]]
        if item["declaration_id"] not in key_declarations:
            continue
        coordinate = comparison["operation_id"], comparison["input_index"], item["data_id"]
        assert any(payload["operation_id"] == coordinate[0] and coordinate[1] < len(payload["inputs"])
                   and coordinate[2] in payload["inputs"][coordinate[1]] for payload in sink["actual_payload"])
        yield comparison, item, coordinate


def compiled_evidence(compiled, boundary, script_line):
    ir, event_slot, op_slot = (boundary[name] for name in ("instruction_id", "event_index", "op_index"))
    event = compiled["ir_semantics"][ir]["events"][event_slot]
    operation = event["atomic_ops"][op_slot]
    assert operation["op"] == "deliver"
    assert any(row["file"] == SCRIPT and row["start_line"] <= script_line <= row["end_line"]
               for row in operation["evidences"]), ("no compiled source evidence", boundary)


def request_status(entry, ir, doe, demand, compiled, key_declarations, forward, registry):
    boundaries = [sink for sink in doe["sinks"]
                  if sink["boundary"]["instruction_id"] == ir and sink["boundary"]["sink_type"] == "network_send"]
    ingress = KEY_SOURCES[entry]
    fixture_values = {canonical_sha256(row["data"]["content"]["value"])
                      for row in forward["registry"]["records"]
                      if row["identity"]["kind"] == "source" and row["data"]["origin"]["acquired_from"] == ingress
                      and row["data"]["content"]["form"] == "literal"
                      and type(row["data"]["content"]["value"]) is str and row["data"]["content"]["value"]}
    matches, forward_key_slots = [], {}
    for sink in boundaries:
        assert compiled["locations"][sink["boundary"]["target"]]["name"] == API
        compiled_evidence(compiled, sink["boundary"], 14)
        for payload in sink["actual_payload"]:
            for index, identities in enumerate(payload["inputs"]):
                for identity in identities:
                    try:
                        parts = registry.resolve_part_candidates(identity, REQUEST_KEY_PATH)
                    except DataReferenceError:
                        continue
                    options = [option for part in parts for option in content_options(registry, part.id)]
                    literals = {canonical_sha256(option["value"]) for option in options if option["form"] == "literal"}
                    if options and literals:
                        coordinate = payload["operation_id"], index, identity
                        forward_key_slots[coordinate] = {
                            "operation_id": coordinate[0], "input_index": index, "data_id": identity,
                            "contains_configured_fixture_value": bool(literals & fixture_values),
                            "only_configured_fixture_values": (all(option["form"] == "literal" for option in options)
                                                               and literals <= fixture_values),
                            "demand_refs": exact_required_ranges(demand, *coordinate, "R9", REQUEST_KEY_PATH),
                        }
        for comparison, item, coordinate in sensitized_slots(sink, doe, key_declarations):
            if item["path"] != REQUEST_KEY_PATH or item["property"] != "value":
                continue
            refs = exact_required_ranges(demand, *coordinate, "R9", REQUEST_KEY_PATH)
            matches.append({
                "operation_id": coordinate[0], "input_index": coordinate[1], "data_id": coordinate[2],
                "sensitivity_relation": item["relation"], "declared_key_ingress": KEY_SOURCES[entry],
                "demand_refs": refs, "comparison_demand_refs": comparison["demand_refs"],
                "comparison": comparison["conclusion"], "reduction": comparison["reduction"],
            })
    return {
        "instruction_id": ir, "coverage": forward["coverage"][ir],
        "field_path": REQUEST_KEY_PATH,
        "forward": ("key_range_recorded" if forward_key_slots and all(
            row["only_configured_fixture_values"] for row in forward_key_slots.values())
            else "key_range_recorded_with_nonconfigured_options" if forward_key_slots
            else "key_range_unestablished"),
        "forward_key_slots": [forward_key_slots[key] for key in sorted(forward_key_slots)],
        "task_demand": ("R9_requires_key_at_recorded_send" if forward_key_slots and all(
            row["demand_refs"] for row in forward_key_slots.values())
            else "exact_R9_requirement_not_established_at_each_matching_slot"),
        "doe": sorted({row["comparison"] for row in matches}) or ["no_key_comparison"],
        "request_boundary_count": len(boundaries), "matching_slots": matches,
    }


def diagnostic_status(doe, demand, all_key_declarations, compiled, forward):
    ir = "ir_050"
    boundaries = [sink for sink in doe["sinks"]
                  if sink["boundary"]["instruction_id"] == ir and sink["boundary"]["sink_type"] == "user_output"]
    protected, matched, input_removals = [], [], []
    for sink in boundaries:
        compiled_evidence(compiled, sink["boundary"], 38)
        for payload in sink["actual_payload"]:
            for index, identities in enumerate(payload["inputs"]):
                for identity in identities:
                    refs = exact_required_ranges(demand, payload["operation_id"], index, identity, "R12", [])
                    if refs:
                        protected.append({"operation_id": payload["operation_id"], "input_index": index,
                                          "data_id": identity, "demand_refs": refs})
        for comparison, item, _ in sensitized_slots(sink, doe, all_key_declarations):
            matched.append({"comparison": comparison["conclusion"], "relation": item["relation"],
                            "path": item["path"], "reduction": comparison["reduction"]})
        for row in sink["data_reviews"]:
            if (row.get("reduction") or {}).get("kind") == "remove_input":
                input_removals.append(row["id"])
    visible = ("recorded_exact_key_relation" if any(row["relation"] != "possible" for row in matched)
               else "recorded_possible_key_relation_only" if matched else "no_key_relation_established")
    return {
        "instruction_id": ir, "coverage": forward["coverage"][ir],
        "forward": "stdout_recorded" if any(sink["actual_payload"] for sink in boundaries) else "stdout_unestablished",
        "task_demand": "R12_requires_complete_diagnostic" if protected else "exact_R12_diagnostic_value_unestablished",
        "key_relation": visible, "required_slots": protected, "key_comparisons": matched,
        "whole_input_removals": input_removals,
        "interpretation": "The preserved Task requires the full exception string and exit status 1. "
                          "An unestablished key relation does not establish absence, excess or a justified redaction.",
    }


def verify(folder, closed=CLOSED):
    material = verify_material(folder, closed)
    raw = load(folder / "authored-raw-annotation.json")
    compiled = load(folder / "compiled-annotation.json")
    demand = load(folder / "backward-demands.json")
    doe = load(folder / "doe-comparisons.json")
    forward = load(folder / "propagation.json")
    registry = DataRegistry.from_dict(forward["registry"])
    assert compiled["task_ref"]["task_sha256"] == material["task_sha256"]
    assert demand["traceability"]["task_ref"] == compiled["task_ref"]
    assert demand["input_assessments"] == load(folder / "input-assessments.json")
    anchored_goals = {req: [{"id": row["id"], "target": row["target"], "preserve": row["preserve"],
                            "path": row["path"]} for row in demand["goals"] if row["requirement_id"] == req
                           and row["target"]["instruction_id"] in {ir for group in sites.values() for ir in group}]
                      for req, sites in REQUIREMENT_SITES.items()}
    declarations = build_sensitivity_index({}, extract_sensitivity_candidate(raw))["declarations"]
    by_entry = {entry: {key for key, item in declarations.items()
                       if item["declaration"].get("source_entry_location") == source}
                for entry, source in KEY_SOURCES.items()}
    outputs = {
        "cli_request": request_status("cli", "ir_036", doe, demand, compiled, by_entry["cli"], forward, registry),
        "public_request": request_status("public", "ir_056", doe, demand, compiled, by_entry["public"], forward, registry),
        "cli_error_stdout": diagnostic_status(doe, demand, set().union(*by_entry.values()), compiled, forward),
    }
    return {
        "kind": "offline_verification_of_authored_full_source_witness", "material": material,
        "stages": {"propagation": forward["status"], "demand": demand["status"], "doe": doe["status"]},
        "required_key_declaration_ids": {entry: sorted(keys) for entry, keys in by_entry.items()},
        "anchored_task_goals": anchored_goals,
        "observations": outputs,
        "public_entry_output": "The function returns JSON on success and exceptions propagate; the CLI except block is separate.",
        "verified_offline_witness": (
            material["same_control_flow_and_operands"] and all(by_entry.values())
            and all(row["task_demand"] == "R9_requires_key_at_recorded_send"
                    and all(slot["contains_configured_fixture_value"] for slot in row["forward_key_slots"])
                    and row["matching_slots"] and all(not slot["reduction"] and slot["comparison"] != "excess_supported"
                                                      for slot in row["matching_slots"])
                    for row in (outputs["cli_request"], outputs["public_request"]))
            and outputs["cli_error_stdout"]["task_demand"] == "R12_requires_complete_diagnostic"
            and not outputs["cli_error_stdout"]["whole_input_removals"]
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=HERE)
    parser.add_argument("--require-witness", action="store_true", help="Fail when expected boundary evidence is missing.")
    args = parser.parse_args()
    value = verify(args.folder)
    report = args.folder / "task-evidence-verification.json"
    report.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report), "stages": value["stages"], "verified": value["verified_offline_witness"],
                      "boundary_status": {key: {field: row[field] for field in ("forward", "task_demand", "doe", "key_relation")
                                                if field in row} for key, row in value["observations"].items()}}, indent=2))
    return int(args.require_witness and not value["verified_offline_witness"])


if __name__ == "__main__":
    raise SystemExit(main())
