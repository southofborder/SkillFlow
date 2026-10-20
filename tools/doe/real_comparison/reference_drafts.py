"""Publish source-only assistant drafts for review, never human approval."""
import html
import json
from pathlib import Path

from .assessment import validate_reference_evidence, REFERENCE_FIELDS
from .semantic_metrics import GRADING_SCHEMA_VERSION, validate_grading_reference
from .protocol import sha256, write_json, utc_now


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _copy_bytes(source, target):
    target = Path(target)
    data = Path(source).read_bytes()
    if target.exists() and target.read_bytes() != data:
        raise ValueError("Preserved assistant draft version differs; create an explicit new version")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)


def publish_reference_drafts(run_dir, *, version="assistant-v1"):
    run = Path(run_dir).resolve()
    if version != "assistant-v1":
        raise ValueError("A later assistant revision requires its own explicit versioned publication policy")
    if (run / "reference-freeze.json").exists():
        raise ValueError("An approved reference requires a preserved human corrigendum")
    approvals = run / "approvals/import-manifest.json"
    if approvals.exists() and _read(approvals).get("records"):
        raise ValueError("Preserve already submitted human confirmations before changing references")
    for request in (run / "mailbox/requests").glob("*/request.json"):
        if _read(request).get("mode") == "formal":
            raise ValueError("Assistant reference drafting must finish before any formal request")
    selected = _read(run / "selection.json")
    cases = selected["selected"] + selected["reserves"]
    if len(cases) != 30 or len({c["case_id"] for c in cases}) != 30:
        raise ValueError("Publication requires all 24 selected and six reserve source references")
    records = []
    for case in cases:
        case_id = case["case_id"]
        path = run / "reference-drafts" / version / (case_id + ".json")
        draft = _read(path)
        source_manifest = _read(run / "cases" / case_id / "source-manifest.json")
        if (draft.get("state") != "assistant_draft" or draft.get("human_verified") is not False
                or draft.get("grading_schema_version") != GRADING_SCHEMA_VERSION
                or draft.get("source_sha256") != case["source_sha256"]
                or draft.get("case_id") != case_id):
            raise ValueError("A preparation draft must preserve source identity and explicitly remain unverified")
        validate_reference_evidence(run, draft)
        validate_grading_reference(draft)
        expected = {f["path"] for f in source_manifest["files"] if f["kind"] != "binary"}
        reviewed = draft.get("reviewed_files")
        if (not isinstance(reviewed, list) or any(not isinstance(p, str) for p in reviewed)
                or len(reviewed) != len(set(reviewed)) or set(reviewed) != expected):
            raise ValueError("Every retained readable source file must appear once in reviewed_files")
        source_root = run / "cases" / case_id / "source"
        if sha256(run / "cases" / case_id / "source-bundle.txt") != source_manifest["source_bundle_sha256"]:
            raise ValueError("The numbered source bundle changed before draft publication")
        for member in source_manifest["files"]:
            member_path = (source_root / member["path"]).resolve()
            if not member_path.is_relative_to(source_root.resolve()) or sha256(member_path) != member["sha256"]:
                raise ValueError("The original source changed before draft publication")
        records.append({"case_id": case_id, "canonical_id": case["canonical_id"],
                        "role": "formal" if case in selected["selected"] else "reserve",
                        "source_sha256": case["source_sha256"], "draft_path": path.relative_to(run).as_posix(),
                        "draft_sha256": sha256(path), "reviewed_files": len(expected),
                        "section_counts": {k: len(draft[k]) for k in REFERENCE_FIELDS},
                        "human_confirmations": 0})
    # Validate the entire cohort before publishing the first ledger.
    history = run / "reference-draft-history/source-facts-v0"
    for record in records:
        active = run / "references" / (record["case_id"] + ".json")
        previous = history / active.name
        if not previous.exists():
            _copy_bytes(active, previous)
        if active.read_bytes() != previous.read_bytes() and sha256(active) != record["draft_sha256"]:
            raise ValueError("The active reference is neither the preserved initial draft nor this exact publication")
        active.write_bytes((run / record["draft_path"]).read_bytes())
        record["published_path"] = active.relative_to(run).as_posix()
        record["initial_source_facts_sha256"] = sha256(previous)
    freeze_path = run / "reference-draft-freeze-v1.json"
    old = _read(freeze_path) if freeze_path.exists() else {}
    freeze = {"state": "assistant_drafts_pending_two_actual_humans", "version": version,
              "created_at": old.get("created_at", utc_now()), "selected": 24, "reserves": 6,
              "actual_human_confirmations": 0, "formal_calls": 0, "model_calls": 0,
              "source_materials_freeze_sha256": sha256(run / "materials-freeze.json"),
              "interpretation": "Engineering quote and inventory checks passed. Assistant drafts are exploratory source interpretations, not human-confirmed gold or proof of semantic completeness.",
              "entries": records}
    write_json(freeze_path, freeze, immutable=True)
    lines = ["# Source reference review package", "",
             "All 30 source-only assistant ledgers are ready for two actual people to verify. No human approval or formal semantic result is supplied by this package.", "",
             "Register H1 and H2 using human-roster.template.json. Both people inspect each entire original source and every ledger interpretation, including possible omissions, genuine uncertainty, and reductions that might break required behavior. A publisher's statement is not actual user authorization. Existing implementation choices do not establish necessity.", "",
             "Resolve source disputes explicitly or retain them as unknown. Before anyone confirms a revised draft, preserve the prior draft and record its reason/version. Each person submits their own confirmation bound to the final exact source/reference hashes. The 60 confirmations and complete engineering calibration are required before formal dispatch.", "",
             "Use import-human and freeze-references after those actual submissions. Timed reviewers R1/R2/R3 must be separate people and must not read these reference ledgers before their assigned first-read review.", "",
             "| Case | Role | Skill | Readable files | Receiving points | Draft excess units | Unknowns | Source and ledger |",
             "|---|---|---|---:|---:|---:|---:|---|"]
    for r in records:
        c, n = r["case_id"], r["section_counts"]
        lines.append(f"| {c} | {r['role']} | {r['canonical_id']} | {r['reviewed_files']} | {n['receiving_points']} | {n['supported_excesses']} | {n['unknowns']} | [Source](cases/{c}/source-bundle.txt), [Ledger](references/{c}.json) |")
    text = "\n".join(lines) + "\n"
    (run / "human-reference-package.md").write_text(text, encoding="utf-8")
    links = "".join(f"<tr><td>{html.escape(r['case_id'])}</td><td>{html.escape(r['canonical_id'])}</td><td><a href='cases/{r['case_id']}/source-bundle.txt'>Complete numbered source</a> · <a href='references/{r['case_id']}.json'>Assistant draft</a></td><td>H1 pending; H2 pending</td></tr>" for r in records)
    (run / "human-reference-package.html").write_text("<!doctype html><meta charset='utf-8'><title>Source reference review</title><style>body{font:16px system-ui;max-width:1200px;margin:32px auto}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}</style><h1>Source reference review</h1><p>Assistant drafts only. Both actual human verifiers must independently check all 30 ledgers against original sources. Formal target calls: zero.</p><p><a href='human-reference-package.md'>Instructions and source inventory</a> · <a href='human-roster.template.json'>Registration template</a></p><table><thead><tr><th>Case</th><th>Skill</th><th>Material</th><th>Human confirmation</th></tr></thead><tbody>" + links + "</tbody></table>", encoding="utf-8")
    return freeze
