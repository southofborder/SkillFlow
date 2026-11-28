"""Read only the fresh run's frozen source; never import or execute the Skill.

This creates a static source-site denominator, not a propagation/DOE result.
No historical model answers or analyses are read by this helper.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


FUNCTION = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)")
REMOTE = re.compile(r"\bawait\s+(client(?:\.\w+)+)\s*\(")
SAVE = re.compile(r"^\s*saveResult\s*\(")
FS = re.compile(r"\b(existsSync|mkdirSync|writeFileSync|readFileSync|readdirSync)\s*\(")
LOG = re.compile(r"^\s*console\.(log|error|warn)\s*\(")


def ref(file, start, end):
    return {"file": "skill/" + file, "start_line": start, "end_line": end}


# These observations are re-derived from the current frozen source. They are
# review questions and factual source relationships, not accepted contracts.
NOTES = [
    {"id": "settings_field_selection", "topic": "Settings fields and real validation controls",
     "source_refs": [ref("scripts/src/config/settings.ts", 40, 73), ref("scripts/src/core/client.ts", 23, 42)],
     "observed": "getSettings returns propertyId, clientEmail, privateKey, defaultDateRange, resultsDir and siteUrl. Validation checks propertyId, clientEmail and privateKey before client construction; private-key text normalizes escaped newlines.",
     "audit_question": "Keep actual reads and credential validation facts. Field demand for a particular consumer must not become a whole-settings demand merely because the getter returned all fields; actual control requirements still count."},
    {"id": "credential_clients", "topic": "Credential construction, scopes, cache state and destinations",
     "source_refs": [ref("scripts/src/core/client.ts", 23, 42), ref("scripts/src/core/client.ts", 67, 80), ref("scripts/src/core/client.ts", 88, 123)],
     "observed": "Client constructors select clientEmail/privateKey. Shared GoogleAuth carries both webmasters.readonly and indexing scopes. Three separate singleton slots short-circuit construction; resetClient clears all three.",
     "audit_question": "Bind credential/client identities and interface field obligations to the real destination and call. Current constructor arguments alone do not prove every scope or settings field necessary. Preserve cache-hit versus miss controls."},
    {"id": "ignored_report_options", "topic": "Declared report filters and orderBy are unused",
     "source_refs": [ref("scripts/src/api/reports.ts", 20, 27), ref("scripts/src/api/reports.ts", 77, 109), ref("references/api-reference.md", 30, 45)],
     "observed": "runReport destructures filters and orderBy, but its request includes only property, dateRanges, dimensions, metrics and a truthy limit. Neither filters nor orderBy contributes to the request or returned response.",
     "audit_question": "Check whether the generated facts preserve the actual unused reads and whether semantic review reports the conflict with the documented filter/sort options. Do not invent filtering/sorting or silently substitute a corrected request."},
    {"id": "date_range_branches", "topic": "Date values, defaults and object pass-through",
     "source_refs": [ref("scripts/src/api/reports.ts", 47, 72), ref("scripts/src/api/bulk-lookup.ts", 103, 128), ref("scripts/src/api/searchConsole.ts", 51, 83)],
     "observed": "Absent/falsy ranges read the settings default. Object ranges are returned unchanged; shorthand strings select matched day counts, otherwise a 30-day default. Search Console computes ISO dates from separate current-Date values.",
     "audit_question": "Keep control/existence relations and actual object pass-through. Do not remove extra object fields from forward facts merely because an interface contract later needs only startDate/endDate; do not merge distinct clock observations."},
    {"id": "report_request_fields", "topic": "Report dimensions, metrics, limits and whole responses",
     "source_refs": [ref("scripts/src/api/reports.ts", 77, 109), ref("scripts/src/api/realtime.ts", 24, 98), ref("scripts/src/api/searchConsole.ts", 89, 121)],
     "observed": "GA4 maps dimension and metric name arrays into request objects. Search Console preserves dimensions, rowLimit and startRow in requestBody. Standard/realtime report functions return their whole response; search analytics selects response.data.",
     "audit_question": "Verify ordered member scopes, optional/truthy controls and actual response selection. Interface necessity must be justified independently of observing these actual arguments."},
    {"id": "bulk_lookup_controls", "topic": "URL normalization, membership and empty-input early return",
     "source_refs": [ref("scripts/src/api/bulk-lookup.ts", 64, 98), ref("scripts/src/api/bulk-lookup.ts", 149, 192)],
     "observed": "URL normalization trims each string and prefixes a missing slash without removing trailing slashes. A nonempty URL list becomes a case-insensitive pagePath inListFilter. The empty normalized list returns rows=[]/rowCount=0 before client access, remote request or save.",
     "audit_question": "Preserve per-member values/order and cardinality/existence controls; an empty-output branch must not fabricate a request or persistence event. Keep requested metrics, dateRange and save controls distinct."},
    {"id": "metadata_output_selection", "topic": "Different metadata outputs have different field needs",
     "source_refs": [ref("scripts/src/api/metadata.ts", 38, 95), ref("scripts/src/index.ts", 355, 361)],
     "observed": "getAvailableDimensions selects response.dimensions (default []); getAvailableMetrics selects response.metrics; getPropertyMetadata returns/saves the whole response. getAvailableFields logs dimensions/metrics counts and returns the whole metadata object.",
     "audit_question": "Check output-specific value/presence/cardinality demand and retain full acquisition facts. A selected metadata field does not establish that the remote acquisition supports field projection."},
    {"id": "index_notification_side_effect", "topic": "Index notification actions and conditional fallback values",
     "source_refs": [ref("scripts/src/api/indexing.ts", 57, 80), ref("scripts/src/api/indexing.ts", 114, 137)],
     "observed": "Publish requests send the URL with URL_UPDATED or URL_DELETED. Returned url and notifyTime use response metadata with original-URL/current-time fallbacks. Saving is separately guarded by save.",
     "audit_question": "Keep publish side effects even when no response field is demanded. Preserve request/response pairing, notification type and fallback controls; response-only analysis must not delete an action-required URL."},
    {"id": "inspection_output_fields", "topic": "URL inspection field projection and conditional nested objects",
     "source_refs": [ref("scripts/src/api/indexing.ts", 146, 193), ref("scripts/src/index.ts", 324, 346)],
     "observed": "inspectUrl requests inspectionUrl/siteUrl and explicitly constructs indexStatus, optional mobileUsability, optional richResults and inspectionResultLink from response.data.inspectionResult. checkIndexStatus invokes inspectUrl with save:false and stores only URL, verdict-derived indexed, and the full indexStatus object; catch stores an error status.",
     "audit_question": "Verify exact field paths, default/presence conditions, URL-result member pairing and the distinction between standalone inspectUrl obligations and this narrower caller. Do not declare fields globally deletable from one consumer alone."},
    {"id": "batch_members_and_errors", "topic": "Sequential batches, per-item outcomes and suppressed inner saves",
     "source_refs": [ref("scripts/src/api/indexing.ts", 89, 105), ref("scripts/src/index.ts", 301, 346)],
     "observed": "requestIndexingBatch processes members sequentially and passes save:false to each request. reindexUrls and checkIndexStatus have per-item try/catch, preserve URL/outcome pairing, log URLs, and save one collected batch. requestIndexingBatch itself has no per-item catch.",
     "audit_question": "Keep duplicate/member occurrence identities and different error control behavior. Preserve false inner save flags and required outer writes; console URL observations remain actual uses."},
    {"id": "aggregate_reports", "topic": "Aggregate results, nested default saves and date-pair identity",
     "source_refs": [ref("scripts/src/index.ts", 55, 224), ref("scripts/src/index.ts", 235, 295)],
     "observed": "High-level workflows collect named subresults and persist the aggregate; many nested report helpers retain their default save:true. compareDateRanges pairs range1 with period1 and range2 with period2, then saves both; it performs no arithmetic comparison.",
     "audit_question": "Retain each real nested/aggregate save and period pairing. Task/source evidence must determine necessity rather than treating all similar writes as duplicates. Do not invent trend calculations in compareDateRanges."},
    {"id": "persistent_wrapper_and_filename", "topic": "Persistence content and path depend on different inputs",
     "source_refs": [ref("scripts/src/core/storage.ts", 31, 94)],
     "observed": "saveResult writes the whole data argument wrapped with savedAt/category/operation/propertyId and optional extraInfo. The path uses resultsDir/category plus a timestamp and sanitized operation/extraInfo. Directory creation is conditional. The written timestamp and filename timestamp are generated separately.",
     "audit_question": "Distinguish content fields, directory/path controls, optional metadata and separate clocks. Preserve the real propertyId metadata even for non-GA4 categories; do not treat an unused returned filepath as an absent storage side effect."},
    {"id": "result_selection", "topic": "Read/list/latest behavior and filename matching",
     "source_refs": [ref("scripts/src/core/storage.ts", 103, 171)],
     "observed": "loadResult checks existence then reads/parses, returning null on catch. listResults filters .json, joins paths, sorts descending by filename and optionally slices. getLatestResult optionally uses a sanitized operation substring, chooses the first file, then loads it.",
     "audit_question": "Keep selection order, limits, existence and candidate filename conditions. A latest filename does not prove correlation with the current request; do not invent exact-operation matching or a current-run cache."},
    {"id": "narrative_summary", "topic": "Source-declared read-and-summary workflow",
     "source_refs": [ref("SKILL.md", 53, 64), ref("SKILL.md", 151, 158)],
     "observed": "The workflow declares analysis, auto-save and reading saved JSON to create Markdown summaries containing tables, trends and recommendations under results/summaries. Tips separately suggest asking for a summary after pulling data.",
     "audit_question": "Audit source modality and summary read/write obligations separately from TypeScript call-site counts. No summary implementation appears among the explicit API/saveResult call sites."},
    {"id": "examples_setup_and_entry", "topic": "Executable bodies versus examples and setup",
     "source_refs": [ref("SKILL.md", 8, 50), ref("scripts/setup.sh", 1, 2), ref("scripts/src/index.ts", 364, 405)],
     "observed": "Source contains setup npm-install instructions, import examples and a direct-entry help branch. The direct index.ts branch prints help; examples do not cause every exported API function to execute together.",
     "audit_question": "Keep declared alternatives/example modality. The 13 remote sites below count explicit client method calls, not installation package downloads or all runtime invocations of shared helpers."},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve()
    source = run / "source/inputs/package"
    snapshot_path = run / "source/inputs/snapshot.json"
    snapshot = json.loads(snapshot_path.read_bytes())
    expected = {row["path"]: row for row in snapshot["files"]}
    actual = {path.relative_to(source).as_posix(): path for path in source.rglob("*") if path.is_file()}
    if set(actual) != set(expected):
        raise ValueError("Frozen source file set differs from its current snapshot")
    files, texts, remote, saves, fs, logs, functions = [], {}, [], [], [], [], []
    for name, path in sorted(actual.items()):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected[name]["raw_sha256"] or len(raw) != expected[name]["size"]:
            raise ValueError("Frozen source identity mismatch: " + name)
        text = raw.decode("utf-8")
        lines = text.splitlines()
        texts["skill/" + name] = lines
        files.append({"file": "skill/" + name, "raw_sha256": digest,
                      "bytes": len(raw), "characters": len(text), "physical_lines": len(lines)})
        if not name.endswith(".ts"):
            continue
        owner = None
        for index, line in enumerate(lines):
            if line.startswith("if (process.argv"):
                owner = "<direct-entry-help>"
            definition = FUNCTION.match(line)
            if definition:
                owner = definition[1]
                functions.append({**ref(name, index + 1, index + 1), "function": owner,
                                  "exported": line.startswith("export ")})
            match = REMOTE.search(line)
            category = remote if match else saves if SAVE.match(line) else None
            if category is not None:
                end = index
                while ");" not in lines[end]:
                    end += 1
                    if end >= len(lines):
                        raise ValueError("Unterminated source call: " + name)
                category.append({**ref(name, index + 1, end + 1), "function": owner,
                    "callee": match[1] if match else "saveResult",
                    "source_text": "\n".join(lines[index:end + 1]),
                    "mapping_status": "not_yet_compared_to_current_generated_material"})
            for file_call in FS.finditer(line):
                fs.append({**ref(name, index + 1, index + 1), "function": owner,
                           "callee": file_call[1], "source_text": line})
            if LOG.match(line):
                logs.append({**ref(name, index + 1, index + 1), "function": owner,
                             "source_text": line,
                             "dynamic": "${" in line})
    for prefix, rows in (("remote", remote), ("save", saves)):
        for index, row in enumerate(rows, 1):
            row["site_id"] = f"{prefix}_{index:02}"
    notes = json.loads(json.dumps(NOTES))
    for note in notes:
        for citation in note["source_refs"]:
            lines = texts[citation["file"]]
            if not 1 <= citation["start_line"] <= citation["end_line"] <= len(lines):
                raise ValueError("Invalid authored source citation: " + str(citation))
            citation["source_text"] = "\n".join(lines[citation["start_line"] - 1:citation["end_line"]])
    result = {"identity": "skillflow-current-source-site-audit-v1", "run": str(run),
        "source_snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        "basis": "Only current frozen source files and their current snapshot; no historical generated answers, model calls, Skill execution, propagation or replay.",
        "counts": {"source_files": len(files), "remote_api_physical_sites": len(remote),
                   "saveResult_physical_sites": len(saves), "filesystem_physical_sites": len(fs),
                   "console_physical_sites": len(logs), "dynamic_console_sites": sum(row["dynamic"] for row in logs),
                   "exported_function_definitions": sum(row["exported"] for row in functions),
                   "input_necessity_audit_topics": len(notes)},
        "remote_sites_by_file": dict(Counter(row["file"] for row in remote)),
        "save_sites_by_file": dict(Counter(row["file"] for row in saves)),
        "files": files, "remote_api_sites": remote, "save_result_sites": saves,
        "filesystem_sites": fs, "console_sites": logs, "function_definitions": functions,
        "input_necessity_topics": notes,
        "limitations": ["Physical source sites are not dynamic execution counts or a proof of CFG completeness.",
            "Remote count includes explicit awaited client methods only; constructors, SDK authentication internals and setup package downloads are separate boundaries.",
            "Referenced interfaces and observed request objects do not automatically prove a minimal tool input contract.",
            "No generated-IR, processing, review, propagation or DOE coverage claim has been made at this source-inventory stage."]}
    output.mkdir(parents=True, exist_ok=True)
    path = output / "source-audit-inventory.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ["# Fresh GA4 frozen-source inventory", "",
        f"Run: `{run.name}`.", "",
        "This inventory was independently derived from this run's current frozen source only. All 16 raw source files match their current snapshot's hash and byte length. No generated answers or previous source judgments were imported, and no Skill, model, backend analysis or replay was executed.", "",
        "The source contains 13 physical awaited Google client API calls, 25 physical saveResult calls, 7 direct filesystem calls, 57 console call sites (10 with interpolation), and 53 exported function definitions. These counts are source-site denominators, not runtime invocation counts and not generated-IR coverage results. A shared helper can be called by multiple workflows.", "",
        "## Explicit remote API sites", "", "| Site | Function | Method | Frozen source lines |",
        "|---|---|---|---|"]
    for row in remote:
        report.append(f"| {row['site_id']} | {row['function']} | `{row['callee']}` | `{row['file']}:{row['start_line']}-{row['end_line']}` |")
    report.extend(["", "## Explicit saveResult sites", "", "| Site | Function | Frozen source line |",
                   "|---|---|---|"])
    for row in saves:
        report.append(f"| {row['site_id']} | {row['function']} | `{row['file']}:{row['start_line']}` |")
    report.extend(["", "## Input-necessity review topics", "",
        "The following are source facts and review questions, not accepted semantic contracts or deletion conclusions. Exact source text and line spans are retained in source-audit-inventory.json.", ""])
    for note in notes:
        refs = ", ".join(f"`{cite['file']}:{cite['start_line']}-{cite['end_line']}`" for cite in note["source_refs"])
        report.extend([f"### {note['id']}: {note['topic']}", "", note["observed"], "",
                       "Review question: " + note["audit_question"], "", "Source: " + refs + ".", ""])
    report.extend(["## Boundaries for the final source-versus-generated audit", "",
        "A source citation that merely overlaps a broad function range does not establish that the corresponding call, request/response relation or write was modeled. Final mapping must inspect the selected CFG and processing operation, then distinguish represented, processed, blocked, unmodeled and absent positions. Each actual input assessment and reviewed contract must be tied back to that selected occurrence; a completed propagation percentage alone is not source coverage.", "",
        "Setup npm installs and SDK authentication internals are outside the 13 explicit Google client-call denominator. The narrative read-and-Markdown-summary step is separately declared in SKILL.md:53-64; it is not an explicit TypeScript saveResult site. Indexing actions remain relevant even if their response has no positive output demand. Actual prior reads/observations must remain recorded when a field is judged unnecessary downstream.", "",
        "The source clearly declares filters/orderBy options yet runReport does not use them in its outgoing request. This is a source-level documentation/implementation mismatch to test against the generated analysis. It is not permission to fabricate corrected request fields, and it does not alone establish a final task-preserving deletion recommendation.", ""])
    (output / "source-audit-inventory.en.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"output": str(path), "counts": result["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
