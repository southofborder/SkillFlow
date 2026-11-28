"""Passive source/site inventory of this fresh accepted initial CFG only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

RUN = Path("experiments/doe/runs/document-guided-ga4-cfg-recovery-high-20261117-135205")
OUT = Path("output/verification/online-ga4-cfg-recovery-20261117")


def read(path):
    return json.loads(path.read_bytes().decode("utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw = read(RUN / "steps/graph/calls/a001/response.json")
    wire = json.loads(raw) if isinstance(raw, str) else raw
    canonical = read(RUN / "graph/initial.json")["cfg"]
    prepared = read(OUT / "prepared-run.json")
    package = RUN / "source/inputs/package"
    snapshot = read(RUN / "source/inputs/snapshot.json")
    expected = {row["path"]: row["raw_sha256"] for row in snapshot["files"]}
    files, source = [], {}
    for path in sorted(package.rglob("*")):
        if path.is_file():
            relative = path.relative_to(package).as_posix()
            content = path.read_bytes().decode("utf-8")
            source["skill/" + relative] = content
            files.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path),
                          "snapshot_matches": sha(path) == expected.get(relative)})
    records = []
    for bi, block in enumerate(wire["blocks"]):
        for ii, instruction in enumerate(block["instructions"]):
            records.append({"instruction_id": f"ir_{len(records) + 1:03d}",
                "path": f"/blocks/{bi}/instructions/{ii}", "block_ref": block["block_ref"],
                "data_source_kind": block.get("data_source_kind"), **instruction})

    def matches(file, line, predicate):
        return [row for row in records if predicate(row)
            and (span := row.get("metadata", {}).get("_source_span", {})).get("file") == file
            and span.get("start_line", 0) <= line <= span.get("end_line", 0)]

    remote, saves, filesystem = [], [], []
    remote_pattern = re.compile(r"\bawait\s+\w+\.(runReport|runRealtimeReport|getMetadata|searchanalytics\.query|urlNotifications\.publish|urlInspection\.index\.inspect)\s*\(")
    fs_ops = {"existsSync": "acquire_path_existence", "mkdirSync": "create_category_directory",
              "writeFileSync": "write_file", "readFileSync": "acquire_file_content_or_read_exception",
              "readdirSync": "acquire_directory_entries"}
    for file, content in source.items():
        if not file.endswith(".ts"):
            continue
        for line, text in enumerate(content.splitlines(), 1):
            if match := remote_pattern.search(text):
                rows = matches(file, line, lambda row: row["data_source_kind"] == "external" and bool(row.get("outputs")))
                remote.append({"file": file, "line": line, "method": match[1], "source_line": text,
                    "cfg_records": rows,
                    "result_operands_explicit": any(x.get("type") == "result" for row in rows for x in row.get("inputs", [])),
                    "status": "accepted_initial_record_presence_only"})
            if re.search(r"\bsaveResult\s*\(", text) and not re.search(r"\bfunction\s+saveResult", text):
                saves.append({"file": file, "line": line, "source_line": text,
                    "cfg_records": matches(file, line, lambda row: row["opcode"] == "save_result"),
                    "status": "opaque_call_summary_presence_not_caller_to_writer_field_validation"})
            if file.endswith("/core/storage.ts"):
                for method, opcode in fs_ops.items():
                    if re.search(r"\b" + method + r"\s*\(", text):
                        filesystem.append({"file": file, "line": line, "method": method, "source_line": text,
                            "cfg_records": matches(file, line, lambda row: row["opcode"] == opcode),
                            "status": "accepted_initial_record_presence_only"})
    merges = []
    for row in records:
        if row["opcode"] == "merge":
            merges.append({"instruction": row,
                "incoming_sources": [edge["source_block_ref"] for edge in wire["edges"] if edge["target_block_ref"] == row["block_ref"]]})
    artifacts = ["steps/graph/calls/a001/response.json", "steps/graph/calls/a001/validation.json",
                 "steps/graph/result.json", "steps/graph/value.json", "graph/initial.json", "source/inputs/snapshot.json"]
    report = {"observed_at": datetime.now(timezone.utc).isoformat(), "run": RUN.as_posix(),
        "status": "provisional_initial_cfg_only", "implementation_sha256": prepared["implementation_sha256"],
        "source_sha256": prepared["source_sha256"], "artifact_sha256": {name: sha(RUN / name) for name in artifacts},
        "method": "Pure saved JSON/text/hash reads and manual source comparison. No project imports, validators, compiler, backend, Skill, model or replay invoked.",
        "source_files": files, "source_file_count": len(files), "source_total_bytes": sum(row["bytes"] for row in files),
        "snapshot_inventory_equal": set(expected) == {row["path"] for row in files} and all(row["snapshot_matches"] for row in files),
        "accepted_step": read(RUN / "steps/graph/result.json"),
        "saved_validation": read(RUN / "steps/graph/calls/a001/validation.json"),
        "counts": {"blocks": len(canonical["blocks"]), "instructions": sum(len(b["instructions"]) for b in canonical["blocks"].values()),
            "edges": len(canonical["edges"]), "raw_response_characters": len(raw) if isinstance(raw, str) else None,
            "remote_source_sites": len(remote), "remote_sites_with_one_record": sum(len(row["cfg_records"]) == 1 for row in remote),
            "remote_sites_with_result_inputs": sum(row["result_operands_explicit"] for row in remote),
            "save_source_sites": len(saves), "save_sites_with_one_record": sum(len(row["cfg_records"]) == 1 for row in saves),
            "filesystem_source_sites": len(filesystem), "filesystem_sites_with_one_record": sum(len(row["cfg_records"]) == 1 for row in filesystem)},
        "remote_sites": remote, "save_sites": saves, "filesystem_sites": filesystem, "merge_records": merges,
        "limits": ["Structural acceptance is read from saved receipts, not rerun or interpreted as source correctness.",
            "Remote/site counts mean initial-CFG record presence, not semantic interface necessity, task demand, propagation reach or DOE coverage.",
            "Seven realtime/metadata sites retain client/property acquisition in prose but not explicit result operands.",
            "Internal save/call summaries and collection summaries require later processing/source review before field-level conclusions.",
            "This initial graph may be superseded by the single shared repair. No final selection/assessment is claimed."]}
    (OUT / "initial-cfg-source-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": len(files), "snapshot_match": report["snapshot_inventory_equal"], **report["counts"]}))


if __name__ == "__main__":
    main()
