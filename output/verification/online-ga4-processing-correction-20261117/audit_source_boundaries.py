"""Fresh-run passive source inventory; standard-library text/hash reads only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-correction-high-20261117-110830"
PACKAGE = RUN / "source/inputs/package"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    snapshot = json.loads((RUN / "source/inputs/snapshot.json").read_bytes().decode("utf-8"))
    files, contents, remote, saves, filesystem = [], {}, [], [], []
    remote_pattern = re.compile(r"await client\.(runReport|runRealtimeReport|getMetadata|searchanalytics\.query|urlNotifications\.publish|urlInspection\.index\.inspect)\(")
    fs_pattern = re.compile(r"\b(existsSync|mkdirSync|writeFileSync|readFileSync|readdirSync)\(")
    for item in snapshot["files"]:
        raw = (PACKAGE / item["path"]).read_bytes()
        text = raw.decode("utf-8")
        lines = text.splitlines(keepends=True)
        files.append({"path": item["path"], "bytes": len(raw), "physical_lines": len(lines),
                      "sha256": sha(raw), "snapshot_match": sha(raw) == item["raw_sha256"]})
        contents[item["path"]] = lines
        if not item["path"].endswith(".ts"):
            continue
        owner = None
        for index, line in enumerate(lines, 1):
            declared = re.match(r"(?:export )?(?:async )?function (\w+)", line)
            if declared:
                owner = declared.group(1)
            match = remote_pattern.search(line)
            if match:
                end = index
                while ";" not in lines[end - 1]:
                    end += 1
                remote.append({"id": f"remote:{item['path']}:{index}", "file": "skill/" + item["path"],
                    "start_line": index, "end_line": end, "owner": owner, "receiver": "client",
                    "method": match.group(1), "call_source": "".join(lines[index - 1:end]),
                    "status": "source_site_only_not_generated_or_reached_coverage"})
            if re.match(r"\s*saveResult\(", line):
                saves.append({"id": f"save:{item['path']}:{index}", "file": "skill/" + item["path"],
                    "line": index, "owner": owner, "call_source": line.strip(),
                    "returns_filepath_used_at_this_call": False,
                    "gate": "if (save), default true in this API helper" if "/api/" in item["path"]
                            else "unconditional after earlier function operations complete",
                    "writer": "skill/scripts/src/core/storage.ts:92",
                    "status": "source_site_only_not_caller_to_writer_coverage"})
            for match in fs_pattern.finditer(line):
                filesystem.append({"file": "skill/" + item["path"], "line": index,
                    "owner": owner, "method": match.group(1), "source": line.strip()})
    result = {"observed_at": datetime.now(timezone.utc).isoformat(),
        "run": RUN.relative_to(ROOT).as_posix(),
        "method": "Passive reads of this run's frozen source only, manually inspected source relationships plus lexical site inventory. No imported historical answers, Skill execution, compiler, analysis engine, validator, model or replay.",
        "source_sha256": snapshot["source_sha256"],
        "snapshot_file_sha256": sha((RUN / "source/inputs/snapshot.json").read_bytes()),
        "files": files, "total_files": len(files), "total_bytes": sum(row["bytes"] for row in files),
        "all_raw_files_match": all(row["snapshot_match"] for row in files),
        "physical_inventory_matches_snapshot": sorted(item["path"] for item in snapshot["files"]) ==
            sorted(path.relative_to(PACKAGE).as_posix() for path in PACKAGE.rglob("*") if path.is_file()),
        "remote_sites": remote, "remote_site_count": len(remote),
        "save_callers": saves, "save_caller_count": len(saves),
        "filesystem_sites": filesystem,
        "storage_relationship": {"definition": "skill/scripts/src/core/storage.ts:58-95",
            "settings_read": "skill/scripts/src/core/storage.ts:64-65",
            "directory_creation": "skill/scripts/src/core/storage.ts:68-69",
            "path_timestamp": "skill/scripts/src/core/storage.ts:31-39,73-77",
            "serialization": "skill/scripts/src/core/storage.ts:80-92",
            "saved_value": "{metadata:{savedAt,category,operation,propertyId,...truthy extraInfo},data}",
            "return": "filepath at line94; every inventoried internal call discards it"},
        "other_source_obligations": [
            {"file": "skill/SKILL.md", "start_line": 53, "end_line": 64,
             "relationship": "Analyze, save JSON, then read saved JSON and create Markdown summaries with tables/trends/recommendations.",
             "limit": "The TypeScript source does not implement this Markdown summary writer or select exact saved files and fields."},
            {"file": "skill/scripts/src/config/settings.ts", "start_line": 8, "end_line": 47,
             "relationship": "dotenv config and five environment fields; private-key newline expansion; current working directory derives resultsDir."},
            {"file": "skill/scripts/src/core/client.ts", "start_line": 23, "end_line": 132,
             "relationship": "Cached clients, validation gates, credentials/auth scopes, property and site helpers must remain source-correct dependencies of calls."},
            {"file": "skill/scripts/src/api/reports.ts", "start_line": 77, "end_line": 100,
             "relationship": "filters/orderBy are actually destructured but absent from the constructed remote request.",
             "limit": "Observation of these inputs and semantic necessity are separate; no deletion conclusion is established by this source inventory."},
            {"file": "skill/scripts/src/index.ts", "start_line": 171, "end_line": 203,
             "relationship": "Two separate reports use different date ranges with save:false; comparison pairs each range with its own response before one combined save."},
            {"file": "skill/scripts/src/index.ts", "start_line": 301, "end_line": 345,
             "relationship": "Per-URL requests preserve member association, success/error outcomes and aggregate saves; nested API saves are disabled."},
            {"file": "skill/scripts/src/api/indexing.ts", "start_line": 89, "end_line": 104,
             "relationship": "Sequential per-URL requestIndexing calls with save:false; unlike high-level reindexUrls, this helper has no per-item catch."},
            {"file": "skill/scripts/src/core/storage.ts", "start_line": 103, "end_line": 170,
             "relationship": "Existence checks, read/parse fallback, directory acquisition, JSON filtering/path mapping/ordering/limit and latest-match selection preserve data versions and conditions."},
            {"file": "skill/scripts/src/index.ts", "start_line": 364, "end_line": 405,
             "relationship": "The direct-execution guard prints help; it does not automatically invoke all exported analysis functions."}],
        "generated_material": {"status": "not_audited_yet", "structural_acceptance": None,
            "source_faithful_boundaries": None, "propagation_reach": None, "doe": None},
        "limits": "Counts are distinct physical source sites. They are neither request frequencies, selected task requirements, generated coverage nor execution/propagation/DOE results. SDK internals are outside the bundled source."}
    target = OUT / "source-boundary-inventory.json"
    if target.exists():
        raise RuntimeError("Preserve the existing report; use a new snapshot name.")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": target.relative_to(ROOT).as_posix(), "files": len(files),
                      "bytes": result["total_bytes"], "all_raw_files_match": result["all_raw_files_match"],
                      "remote_sites": len(remote), "save_callers": len(saves), "filesystem_sites": len(filesystem)}))


if __name__ == "__main__":
    main()
