"""Passive inventory of this fresh run's frozen source; no SkillFlow imports."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414"
SOURCE = RUN / "source/inputs/package"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    protocol_bytes = (RUN / "run-protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    manifest_bytes = (RUN / "source/manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    inventory, source_lines, sites = [], {}, {"remote_api": [], "save_result": [], "iteration": [], "filesystem": []}
    actual_paths = {path.relative_to(SOURCE).as_posix(): path for path in SOURCE.rglob("*") if path.is_file()}
    assert set(actual_paths) == set(protocol["source_file_sha256"])
    for name, path in sorted(actual_paths.items()):
        raw = path.read_bytes()
        digest = sha(raw)
        assert digest == protocol["source_file_sha256"][name] == manifest["files"]["inputs/package/" + name]
        lines = raw.decode("utf-8").splitlines()
        source_lines[name] = lines
        inventory.append({"path": name, "sha256": digest, "bytes": len(raw), "lines": len(lines)})
        if not name.endswith(".ts"):
            continue
        function = None
        for line_number, line in enumerate(lines, 1):
            declaration = re.match(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", line.strip())
            if declaration:
                function = declaration[1]
            if line.lstrip().startswith(("*", "//")):
                continue
            ref = {"file": "skill/" + name, "line": line_number, "function": function, "text": line.strip()}
            remote = re.search(r"await\s+client\.([\w.]+)\(", line)
            if remote:
                sites["remote_api"].append({"id": f"remote_{len(sites['remote_api']) + 1:02d}", "method": remote[1], **ref})
            if re.search(r"\bsaveResult\(", line):
                sites["save_result"].append({"id": f"save_{len(sites['save_result']) + 1:02d}", **ref})
            if re.search(r"\bfor\s*\(|\bwhile\s*\(|\.(?:map|filter|sort)\(", line):
                sites["iteration"].append({"id": f"iteration_{len(sites['iteration']) + 1:02d}", **ref})
            if name.endswith("core/storage.ts") and re.search(r"\b(?:existsSync|mkdirSync|writeFileSync|readFileSync|readdirSync)\(", line):
                sites["filesystem"].append(ref)
    assert len(inventory) == 16 and sum(row["bytes"] for row in inventory) == 155170
    assert len(sites["remote_api"]) == 13 and len(sites["save_result"]) == 25

    questions = [
        {"id": "read_but_unforwarded_fields", "source": [["scripts/src/api/reports.ts", 77, 108], ["references/api-reference.md", 31, 42]],
         "source_fact": "runReport destructures filters and orderBy, but its request object and later body never consume them. The API reference promises these options.",
         "audit_question": "Does the current representation retain the actual field-read observations, distinguish their absent contribution to the implemented request/output, and report the documented capability mismatch without inventing SDK field encodings? This source observation alone is not a final task-relative deletability result."},
        {"id": "truthy_limit", "source": [["scripts/src/api/reports.ts", 84, 100]],
         "source_fact": "The request spreads limit only when truthy.",
         "audit_question": "Are the inclusion condition and parameter value represented separately? Source establishes zero omission but not external SDK behavior for a hypothetical supplied zero."},
        {"id": "caller_to_storage_boundary", "source": [["scripts/src/core/storage.ts", 58, 94]],
         "source_fact": "saveResult wraps data in metadata with savedAt, category, operation, propertyId and conditional extraInfo, serializes it, writes to a computed filepath and returns that path.",
         "audit_question": "Does each of the 25 caller sites connect its actual data/category/operation/extraInfo to the writer, payload and returned path? A generated or processed opaque saveResult call alone does not establish the filesystem boundary."},
        {"id": "storage_control_and_identity", "source": [["scripts/src/core/storage.ts", 64, 92]],
         "source_fact": "The filesystem identity depends on resultsDir/category, timestamp, sanitized operation and conditional extraInfo; directory creation depends on existence.",
         "audit_question": "Do necessary location and control requirements remain when payload fields are excluded?"},
        {"id": "natural_language_summary", "source": [["SKILL.md", 55, 65]],
         "source_fact": "The workflow requires reading saved JSON files and writing a Markdown summary in results/summaries with data tables, trends and recommendations.",
         "audit_question": "Do Task, CFG and mapping retain this stated action and its source/read/write relationships? TypeScript physical-site counts cannot establish this separate obligation."},
        {"id": "batch_member_pairing", "source": [["scripts/src/api/indexing.ts", 89, 104], ["scripts/src/index.ts", 300, 344]],
         "source_fact": "Batch requests are sequential, retain each URL/result relationship, use per-item save=false in requestIndexingBatch, and may save the final batch; high-level wrappers retain caught-error records.",
         "audit_question": "Are per-member pairing, conditions and normal/error alternatives represented and then reached by propagation?"},
        {"id": "bulk_empty_and_membership", "source": [["scripts/src/api/bulk-lookup.ts", 63, 98], ["scripts/src/api/bulk-lookup.ts", 154, 183]],
         "source_fact": "URLs are normalized to paths, an empty normalized array returns before the remote request, and a nonempty request includes a URL-membership filter, selected metrics, date range, pagePath and pageTitle dimensions.",
         "audit_question": "Does demand transfer preserve collection existence/membership/control and selected fields rather than substituting an arbitrary scalar dependency?"},
        {"id": "deterministic_inspection_projection", "source": [["scripts/src/api/indexing.ts", 152, 185]],
         "source_fact": "The inspection result explicitly selects nested response fields with defaults and conditional mobileUsability/richResults objects.",
         "audit_question": "Do deterministic selectors and condition dependencies remain precise? An opaque whole-response contract must not override these real dependencies."},
        {"id": "authentication_vs_routing", "source": [["scripts/src/core/client.ts", 23, 52], ["scripts/src/core/client.ts", 70, 132]],
         "source_fact": "Client authentication uses clientEmail/privateKey; API routing uses propertyId or siteUrl; caches and validation add separate state/control relationships.",
         "audit_question": "Does the generated graph distinguish authentication, cached receiver identity, routing and request payload fields?"},
        {"id": "storage_order_and_existence", "source": [["scripts/src/core/storage.ts", 123, 171]],
         "source_fact": "Result listing filters JSON filenames, forms paths, sorts descending and optionally slices by limit. Latest-result retrieval optionally filters operation, handles no files and selects index zero.",
         "audit_question": "Are order, count, membership and existence preserved independently of retained data fields?"},
    ]
    for item in questions:
        for path, start, end in item["source"]:
            assert 1 <= start <= end <= len(source_lines[path]), (item["id"], path, start, end)
    result_bytes = (RUN / "result.json").read_bytes()
    current = json.loads(result_bytes)
    value = {
        "version": "fresh-ga4-source-inventory-v1", "observed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(RUN), "implementation_sha256": protocol["implementation_sha256"],
        "source_sha256": protocol["source_sha256"], "protocol_sha256": sha(protocol_bytes),
        "source_manifest_sha256": sha(manifest_bytes), "source_manifest_identity": manifest["identity"],
        "source_manifest_declared_sha256": manifest["manifest_sha256"],
        "files": inventory, "sites": sites,
        "counts": {"files": len(inventory), "source_bytes": sum(row["bytes"] for row in inventory),
                   **{name + "_sites": len(rows) for name, rows in sites.items()}},
        "source_supported_audit_questions": questions,
        "run_observation": {"result_sha256": sha(result_bytes), "status": current.get("status"),
                            "stage": current.get("stage"), "stages": current.get("stages"),
                            "selected_annotation": current.get("selected_annotation")},
        "coverage_meaning": {
            "physical_sites": "Source call-site inventory only; repeated runtime invocations are not counted.",
            "generated_cfg": "Must be counted from this run's actual candidate and selected graph; no earlier graph is evidence.",
            "processed": "Must come from this run's saved propagation records; generation alone is insufficient.",
            "source_faithful_boundaries": "Require matching actual source operation, operands/receiver, result pairing and processing semantics; cited source spans alone are insufficient.",
            "necessity_and_doe": "Require the selected bundle's bound review receipt, task-relative demand/input assessments and saved DOE results; a source observation is not a final deletion verdict."
        },
        "limitations": [
            "No Skill, model, renderer, propagation, DOE, validator or replay was executed by this helper.",
            "No earlier generated model answer, CFG, annotation or result was imported into this current-run audit.",
            "Source call sites, graph coverage, propagation coverage and validated minimization results must remain separate measures.",
            "The active controller may advance after the recorded observation; this source baseline is not a final run assessment."
        ]
    }
    (OUT / "source-physical-inventory.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Fresh GA4 source baseline", "", f"Run: `{RUN.name}`.", "",
             "All 16 frozen files match both the source manifest and this run's protocol hashes (155,170 bytes).",
             "The source contains 13 direct remote API call sites and 25 saveResult call sites. These are physical source counts, not generated or processed coverage.",
             "", "## Remote API sites", "", "| Site | Source | Function | Remote method |", "|---|---|---|---|"]
    lines += [f"| {row['id']} | {row['file']}:{row['line']} | {row['function']} | {row['method']} |" for row in sites["remote_api"]]
    lines += ["", "## saveResult caller sites", "", "| Site | Source | Function |", "|---|---|---|"]
    lines += [f"| {row['id']} | {row['file']}:{row['line']} | {row['function']} |" for row in sites["save_result"]]
    lines += ["", "## Source-supported questions for the new result", ""]
    for row in questions:
        refs = "; ".join(f"skill/{path}:{start}-{end}" for path, start, end in row["source"])
        lines += [f"- **{row['id']}** ({refs}): {row['source_fact']} {row['audit_question']}"]
    lines += ["", "## Pending evidence", "",
              "This preliminary baseline makes no claim that a generated graph reaches the sites, processing models them faithfully, propagation processes them, or DOE demonstrates a removable field. Those conclusions require new selected artifacts and their bound review and demand evidence.",
              "", "No historical graph/answer was imported. No Skill, model, backend or replay was executed by this helper."]
    (OUT / "source-physical-inventory.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(value["counts"]))


if __name__ == "__main__":
    main()
