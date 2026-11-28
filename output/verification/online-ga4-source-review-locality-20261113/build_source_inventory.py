"""Read frozen source text only; never import or execute Skill/backend code."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"
SOURCE = RUN / "source/inputs/package"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_reference(path, line, text, function):
    return {"file": "skill/" + path, "line": line, "function": function, "text": text}


def main():
    manifest_path = RUN / "source/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files, remotes, saves, iterations, storage, functions = [], [], [], [], [], []
    sources = {}
    for file in sorted(SOURCE.rglob("*")):
        if not file.is_file():
            continue
        rel = file.relative_to(SOURCE).as_posix()
        raw = file.read_bytes()
        digest = sha(raw)
        assert digest == manifest["files"]["inputs/package/" + rel], rel
        text = raw.decode("utf-8")
        sources[rel] = text.splitlines()
        files.append({"path": rel, "sha256": digest, "bytes": len(raw), "lines": len(text.splitlines())})
        if not rel.endswith(".ts"):
            continue
        function = None
        for number, line in enumerate(text.splitlines(), 1):
            found = re.match(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", line.strip())
            if found:
                function = found[1]
                functions.append(source_reference(rel, number, line.strip(), function))
            if line.lstrip().startswith(("*", "//")):
                continue
            ref = source_reference(rel, number, line.strip(), function)
            remote = re.search(r"await\s+client\.([\w.]+)\(", line)
            if remote:
                remotes.append({"id": f"remote_{len(remotes) + 1:02d}", "method": remote[1], **ref})
            if re.search(r"\bsaveResult\(", line):
                saves.append({"id": f"save_{len(saves) + 1:02d}", **ref})
            if re.search(r"\bfor\s*\(|\bwhile\s*\(|\.(?:map|filter|sort)\(", line):
                iterations.append({"id": f"iteration_{len(iterations) + 1:02d}", **ref})
            if rel.endswith("core/storage.ts") and re.search(r"\b(?:writeFileSync|readFileSync|mkdirSync|readdirSync)\(", line):
                storage.append(ref)
    notes = [
        {"id": "reports-unused-filter-and-order-inputs", "file": "skill/scripts/src/api/reports.ts", "lines": [77, 108],
         "finding": "The source destructures filters and orderBy but the constructed request has neither. Their actual read fact must remain distinguishable from necessity for the implemented response. The documented interface separately promises these options; report source/implementation mismatch rather than inventing SDK field names.",
         "reference": {"file": "skill/references/api-reference.md", "lines": [31, 45]}},
        {"id": "reports-truthy-limit", "file": "skill/scripts/src/api/reports.ts", "lines": [84, 100],
         "finding": "The source adds limit only when truthy. A supplied zero is omitted. Whether that omission changes SDK behavior requires explicit interface evidence; source truthiness alone does not establish SDK zero semantics."},
        {"id": "save-controls-and-payload", "file": "skill/scripts/src/core/storage.ts", "lines": [58, 94],
         "finding": "Each saveResult call needs connection to the filesystem writer and wrapper fields data, metadata.savedAt/category/operation/propertyId and optional extraInfo. A processed local-tool call alone does not establish this filesystem exposure."},
        {"id": "storage-path-and-control", "file": "skill/scripts/src/core/storage.ts", "lines": [65, 92],
         "finding": "Path identity depends on resultsDir/category, timestamp, sanitized operation and conditional extraInfo; directory creation is conditional. Data minimization must preserve required path/control uses, not just JSON data fields."},
        {"id": "summary-obligation", "file": "skill/SKILL.md", "lines": [57, 71],
         "finding": "The declared workflow requires reading saved results and creating a Markdown summary with tables, trends and recommendations. This natural-language obligation must be audited separately from TypeScript call-site counts."},
        {"id": "batch-pairing-and-save", "file": "skill/scripts/src/api/indexing.ts", "lines": [89, 104],
         "finding": "The sequential batch maps each URL to its own indexing response with per-item save=false and one optional final save. Preserve member/result pairing and loop control."},
        {"id": "high-level-error-pairing", "file": "skill/scripts/src/index.ts", "lines": [300, 344],
         "finding": "High-level reindex/inspection loops preserve each URL in either success or caught-error results and save the complete batch. Normal and error paths must both be traced to actual request semantics."},
        {"id": "bulk-input-and-empty-control", "file": "skill/scripts/src/api/bulk-lookup.ts", "lines": [63, 98],
         "finding": "URL normalization maps each input path; filter construction preserves URL membership and empty-input control. These requirements cannot be replaced by value-only demand on an arbitrary scalar."},
        {"id": "bulk-no-call-empty", "file": "skill/scripts/src/api/bulk-lookup.ts", "lines": [154, 183],
         "finding": "An empty normalized URL array returns rows=[]/rowCount=0 before acquisition. Nonempty requests contain both pagePath and pageTitle dimensions, selected metrics, date range and the URL filter."},
        {"id": "inspection-output-field-precision", "file": "skill/scripts/src/api/indexing.ts", "lines": [152, 185],
         "finding": "Inspection output is explicitly projected and defaulted by field; separate indexStatus/mobileUsability/richResults values and existence conditions. Whole-response contracts must not erase these deterministic field relations."},
        {"id": "credential-and-routing-fields", "file": "skill/scripts/src/core/client.ts", "lines": [23, 143],
         "finding": "Authentication uses clientEmail/privateKey, API routing separately uses propertyId or siteUrl, and singleton/validation control can use additional fields. Preserve those distinctions instead of treating every settings field as every request payload."},
        {"id": "storage-results-order", "file": "skill/scripts/src/core/storage.ts", "lines": [123, 177],
         "finding": "Listing filters JSON files, maps paths, sorts descending, optionally slices by limit; latest-result selection optionally filters operation and handles empty lists. Count/order/existence inputs can be necessary despite discarded payload fields."},
    ]
    value = {"kind": "fresh-source-physical-inventory", "run_directory": str(RUN),
        "source_manifest_sha256": sha(manifest_path.read_bytes()), "source_manifest_identity": manifest["identity"],
        "source_manifest_declared_sha256": manifest["manifest_sha256"],
        "implementation_sha256": manifest["implementation"]["sha256"],
        "files": files, "remote_api_sites": remotes, "save_result_sites": saves,
        "iteration_sites": iterations, "storage_implementation_sites": storage, "function_declarations": functions,
        "source_supported_audit_questions": notes,
        "counts": {"files": len(files), "remote_api_sites": len(remotes), "save_result_sites": len(saves),
                   "iteration_sites": len(iterations), "storage_implementation_sites": len(storage)},
        "limitations": ["This inventories physical source sites, not runtime invocations or completed generated-boundary coverage.",
                        "No earlier generated graph, model answer or source judgment is used as current-run evidence.",
                        "Source discrepancies are separated from unknown external SDK behavior."]}
    (OUT / "source-physical-inventory.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Fresh GA4 source inventory", "", "The complete frozen source contains 16 files. All file bytes match this run's source manifest.", "",
             f"Physical sites: {len(remotes)} remote API calls, {len(saves)} saveResult calls, {len(iterations)} loop/map/filter/sort expressions, and {len(storage)} filesystem implementation calls.", "",
             "These are source obligations, not evidence that generated IR reached or modeled those boundaries.", "", "## Remote calls", ""]
    lines += [f"- {r['file']}:{r['line']} — {r['function']} → client.{r['method']}" for r in remotes]
    lines += ["", "## Saves", ""]
    lines += [f"- {r['file']}:{r['line']} — {r['function']}: `{r['text']}`" for r in saves]
    lines += ["", "## Source-supported audit questions", ""]
    lines += [f"- {r['id']} ({r['file']}:{r['lines'][0]}): {r['finding']}" for r in notes]
    lines += ["", "No Skill, model, propagation, DOE or replay was executed by this inventory helper."]
    (OUT / "source-physical-inventory.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(value["counts"]))


if __name__ == "__main__":
    main()
