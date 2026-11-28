"""Passive saved-JSON/source inventory; no SkillFlow imports or execution."""
import hashlib
import json
from pathlib import Path

RUN = Path("experiments/doe/runs/document-guided-ga4-processing-correction-high-20261117-110830")
OUT = Path("output/verification/online-ga4-processing-correction-20261117")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def raw_response(call):
    raw = read(RUN / f"steps/graph/calls/{call}/response.json")
    assert isinstance(raw, str)
    return raw, json.loads(raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw1, initial = raw_response("a001")
    raw2, replacement = raw_response("a002")
    merged = read(RUN / "steps/graph/calls/a002/merged-candidate.json")
    inventory = read(OUT / "source-boundary-inventory.json")
    context = json.loads((RUN / "steps/graph/calls/a002/prompt.txt").read_text(encoding="utf-8").splitlines()[-1])
    records = []
    for bi, block in enumerate(merged["blocks"]):
        for ii, instruction in enumerate(block["instructions"]):
            records.append({"path": f"/blocks/{bi}/instructions/{ii}", "block_ref": block["block_ref"],
                            "data_source_kind": block.get("data_source_kind"), **instruction})

    def matching(site, predicate):
        line = site.get("line", site.get("start_line"))
        return [row for row in records if predicate(row)
                and (s := row.get("metadata", {}).get("_source_span", {})).get("file") == site["file"]
                and s.get("start_line", 0) <= line <= s.get("end_line", 0)]

    remote = [{"source": site, "candidate_records": matching(site, lambda r:
               r["data_source_kind"] == "external" and any(x["type"] == "external_resource" for x in r.get("inputs", [])))}
              for site in inventory["remote_sites"]]
    saves = [{"source": site, "candidate_records": matching(site, lambda r: r["opcode"] == "save_result")}
             for site in inventory["save_callers"]]
    fs_op = {"existsSync": "file_system_exists", "mkdirSync": "create_directory", "writeFileSync": "write_file_sync",
             "readFileSync": "read_utf8_file_try", "readdirSync": "read_directory_entries"}
    filesystem = [{"source": site, "candidate_records": matching(site, lambda r: r["opcode"] == fs_op[site["method"]])}
                  for site in inventory["filesystem_sites"]]
    for rows in (remote, saves, filesystem):
        assert all(len(row["candidate_records"]) == 1 for row in rows)
    changed = [i for i, (a, b) in enumerate(zip(initial["blocks"], merged["blocks"])) if a != b]
    paths = ["steps/graph/calls/a001/response.json", "steps/graph/calls/a002/response.json",
             "steps/graph/calls/a001/prompt.txt", "steps/graph/calls/a002/prompt.txt",
             "steps/graph/calls/a001/validation.json", "steps/graph/calls/a002/validation.json",
             "steps/graph/calls/a002/merged-candidate.json", "steps/graph/result.json", "result.json"]
    report = {
        "run": str(RUN).replace("\\", "/"),
        "method": "Passive JSON/text/hash comparison of this run only. No validation, compiler, propagation, DOE, model, Skill or replay invoked.",
        "source_sha256": inventory["source_sha256"],
        "artifact_sha256": {path: digest(RUN / path) for path in paths},
        "root_result": read(RUN / "result.json"),
        "graph_result": read(RUN / "steps/graph/result.json"),
        "candidate_counts": {"initial_blocks": len(initial["blocks"]), "initial_authored_instructions": sum(len(b["instructions"]) for b in initial["blocks"]),
                             "initial_edges": len(initial["edges"]), "merged_blocks": len(merged["blocks"]),
                             "merged_authored_instructions": len(records), "merged_edges": len(merged["edges"])},
        "characters": {"initial_raw_response": len(raw1), "correction_raw_response": len(raw2),
                       "initial_stage_prompt": len((RUN / "steps/graph/calls/a001/prompt.txt").read_text(encoding="utf-8")),
                       "correction_stage_prompt": len((RUN / "steps/graph/calls/a002/prompt.txt").read_text(encoding="utf-8"))},
        "correction": {"response": replacement, "scope": context["correction_scope"], "allowed_record_ids": context["allowed_record_ids"],
                       "context_candidate_equals_initial": context["candidate"] == initial,
                       "changed_block_indices": changed, "all_other_root_values_unchanged": all(initial[k] == merged[k] for k in initial if k != "blocks"),
                       "loop_heads_unchanged": all(initial["blocks"][i] == merged["blocks"][i] for i in (222, 234)),
                       "loop_bodies_unchanged": all(initial["blocks"][i] == merged["blocks"][i] for i in (223, 224, 235, 236))},
        "saved_validation": {call: read(RUN / f"steps/graph/calls/{call}/validation.json") for call in ("a001", "a002")},
        "candidate_source_site_counts": {"remote": len(remote), "save_callers": len(saves), "filesystem": len(filesystem)},
        "candidate_remote_sites": remote, "candidate_save_callers": saves, "candidate_filesystem_sites": filesystem,
        "coverage_status": "Every count above is authored-record presence in a rejected candidate, not accepted CFG, processing contract, propagation reach, source-reviewed correctness or DOE coverage.",
        "limits": ["No accepted graph exists.", "No processing response, semantic contract, propagation or DOE result exists.",
                   "Source-site matching plus manually inspected arguments does not prove all source semantics or all caller-to-callee field relationships.",
                   "No execution or hypothetical correction was attempted.", "Prompt character counts are saved stage prompts, not native delivery totals or generation measurements."]
    }
    (OUT / "rejected-cfg-source-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed_blocks": changed, "candidate_only_site_counts": report["candidate_source_site_counts"], "characters": report["characters"]}))


if __name__ == "__main__":
    main()
