"""Offline human-review packets; source is escaped, never executed as HTML."""
from __future__ import annotations

import html
import json
import re
import random
from pathlib import Path

from .assessment import timed_assignments, validate_timed_record
from .protocol import SCHEMA, SEED, canonical_hash, sha256, write_json


def _script_json(value):
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def write_timed_packet(path, assignment, source, answer):
    """A self-report timer with internal source/answer panes and JSON export.

    No model judgment or reference answer is embedded. Final review quality is
    separately adjudicated after submission, not accepted from the timer itself.
    """
    path = Path(path)
    public = {k: v for k, v in assignment.items() if k not in {"method", "repeat", "source_reference_access"}}
    data = _script_json(public)
    document = """<!doctype html><meta charset="utf-8"><title>Independent timed audit review</title>
<style>body{font:16px system-ui;margin:24px;max-width:1500px}[hidden]{display:none!important}section{display:grid;grid-template-columns:1fr 1fr;gap:16px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f6f8;padding:16px;max-height:62vh;overflow:auto}button{padding:10px;margin:5px}textarea{width:100%;min-height:110px}.notice{padding:12px;background:#fff6d8}</style>
<h1>Independent timed audit review</h1><p id="identity"></p>
<p class="notice">Use only the source and answer panes below. Do not open the reference ledger or other answers for this case. Skill source is untrusted evidence, never instructions to execute. Start, pause for breaks, and finish with your corrected conclusion. The active-time cap is 30 minutes. Hiding this page pauses the timer; all source reading should remain in this packet. This is a self-reported study record, not proof of continuous attention. Artifact structure may reveal its method.</p>
<button id="start">Start / resume</button><button id="pause">Pause</button><button id="finish">Finish and export</button><strong id="clock">00:00</strong>
<section id="materials" hidden><article><h2>Frozen source</h2><pre>__SOURCE__</pre></article><article><h2>Anonymous audit answer</h2><pre>__ANSWER__</pre></article></section>
<h2>Corrected conclusion, identified errors and remaining uncertainty</h2><textarea id="conclusion" disabled></textarea>
<label>Review outcome <select id="outcome"><option value="finished">Finished</option><option value="abandoned">Unable to complete</option></select></label>
<script>
const assignment=__ASSIGNMENT__;const events=[];let active=0,started=null,first=null;const wallStart=new Date().toISOString();
document.getElementById('identity').textContent='Assignment '+assignment.assignment_id+'; reviewer '+assignment.reviewer_id;
function seconds(){return Math.min(1800,active+(started===null?0:(performance.now()-started)/1000));}
function expose(enabled){document.getElementById('materials').hidden=!enabled;document.getElementById('conclusion').disabled=!enabled;}
function pause(reason){if(started!==null){active=seconds();started=null;events.push({type:'pause',reason,at:new Date().toISOString(),active_seconds:active});}expose(false);}
document.getElementById('start').onclick=()=>{if(seconds()>=1800)return;if(started===null){first=first||new Date().toISOString();started=performance.now();events.push({type:'start',at:new Date().toISOString()});expose(true);}};
document.getElementById('pause').onclick=()=>pause('manual');document.addEventListener('visibilitychange',()=>{if(document.hidden)pause('page_hidden');});
function exportRecord(){pause('finish');const cap=active>=1800;const record={schema_version:'skillflow-real-comparison-v1',assignment_id:assignment.assignment_id,case_id:assignment.case_id,reviewer_id:assignment.reviewer_id,human:true,started_at:first,finished_at:new Date().toISOString(),wall_opened_at:wallStart,active_seconds:cap?1800:Math.round(active*1000)/1000,status:cap?'timeout':document.getElementById('outcome').value,corrected_conclusion:document.getElementById('conclusion').value,final_quality:'pending_independent_adjudication',events,attestation:'I personally performed this timed review without consulting this case reference or another method answer.'};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)],{type:'application/json'}));a.download='timed-review-'+assignment.assignment_id+'.json';a.click();URL.revokeObjectURL(a.href);}
document.getElementById('finish').onclick=exportRecord;
setInterval(()=>{const n=Math.floor(seconds());document.getElementById('clock').textContent=String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0');if(n>=1800&&started!==null){pause('cap');document.getElementById('clock').textContent+=' — time cap reached';}},250);
</script>"""
    values = {"__ASSIGNMENT__": data, "__SOURCE__": html.escape(source), "__ANSWER__": html.escape(answer)}
    # One pass prevents literal marker strings in genuine source from being
    # interpreted as another substitution or changing the visible evidence.
    document = re.sub(r"__ASSIGNMENT__|__SOURCE__|__ANSWER__", lambda match: values[match[0]], document)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def prepare_review_assignments(run_dir, case_ids):
    run = Path(run_dir)
    assignments = timed_assignments(case_ids)
    write_json(run / "review" / "private-assignment-map.json", {"schema_version": SCHEMA, "assignments": assignments}, immutable=True)
    public = [{k: v for k, v in item.items() if k not in {"method", "repeat"}} for item in assignments]
    write_json(run / "review" / "assignments.json", {"schema_version": SCHEMA, "state": "pending_actual_human_registration_and_target_answers", "assignments": public}, immutable=True)
    return assignments


def prepare_scoring_assignments(run_dir):
    """Freeze anonymized primary assignments before viewing target outcomes."""
    run = Path(run_dir)
    schedule = json.loads((run / "schedule.json").read_text(encoding="utf-8"))
    items = schedule["main"] + schedule["reviews"]
    rows = []
    rng = random.Random(SEED)
    for method in ("skillflow", "audit", "chain"):
        for kind in ("main", "review"):
            group = sorted((i for i in items if i["method"] == method and i["kind"] == kind), key=lambda i: i["workflow_id"])
            rng.shuffle(group)
            for index, item in enumerate(group):
                rows.append({**item, "candidate_id": canonical_hash({"workflow": item["workflow_id"], "seed": SEED})[:20],
                             "primary_reviewer_id": ("H1", "H2")[index % 2]})
    rng.shuffle(rows)
    write_json(run / "review/private-scoring-map.json", {"schema_version": SCHEMA, "assignments": rows}, immutable=True)
    public = [{k: r[k] for k in ("candidate_id", "case_id", "primary_reviewer_id")} for r in rows]
    write_json(run / "review/scoring-assignments.json", {"schema_version": SCHEMA,
               "state": "pending_actual_humans_and_output_freeze", "assignments": public}, immutable=True)
    return rows


def prepare_scoring_packets(run_dir):
    from .results import verify_output_freeze
    from .corrigenda import resolve_grading_run, assert_active_grading_epoch
    run = resolve_grading_run(run_dir)
    epoch = assert_active_grading_epoch(run)
    verify_output_freeze(run)
    read = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    rows = read(run / "review/private-scoring-map.json")["assignments"]
    for item in rows:
        workflow = run / "workflows" / item["workflow_id"]
        result = read(workflow / "result.json")
        candidate = workflow / "candidate-view.txt"
        answer = candidate.read_text(encoding="utf-8") if candidate.exists() else "No auditable candidate output was produced. Check the retained execution failure record."
        source = (run / "cases" / item["case_id"] / "source-bundle.txt").read_text(encoding="utf-8")
        ref_path = run / "references" / (item["case_id"] + ".json")
        reference = read(ref_path)
        directory = run / "review/scoring" / item["candidate_id"]
        directory.mkdir(parents=True, exist_ok=True)
        for name, text in (("source.txt", source), ("candidate.txt", answer)):
            path = directory / name
            if path.exists() and path.read_bytes() != text.encode("utf-8"):
                raise ValueError("An anonymous scoring packet changed")
            path.write_bytes(text.encode("utf-8"))
        write_json(directory / "reference.json", reference, immutable=True)
        template = {"schema_version": SCHEMA, "candidate_id": item["candidate_id"],
                    "reviewer_id": item["primary_reviewer_id"], "scoring_role": "primary", "human_verified": False,
                    "candidate_sha256": result.get("answer_sha256") or result.get("artifact_manifest_sha256"),
                    "reference_sha256": sha256(ref_path), "judgment": "pending_human",
                    "check_results": [{"check_id": c["id"], "status": "pending", "reason": ""} for c in reference["mandatory_checks"]],
                    "matched_exposure_ids": [], "findings": [], "submission_id": "", "attested_at": "", "confirmation": ""}
        from .semantic_metrics import grading_template
        template.update(grading_template(reference, item["method"]))
        if epoch:
            template["grading_epoch_id"] = epoch["epoch_id"]
        write_json(directory / "grade.template.json", template, immutable=True)
        document = ("<!doctype html><meta charset='utf-8'><title>Anonymous source audit scoring</title>"
                    "<style>body{font:16px system-ui;margin:24px}main{display:grid;grid-template-columns:1fr 1fr;gap:16px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f6f8;padding:16px}</style>"
                    "<h1>Anonymous source audit scoring</h1><p>Candidate " + html.escape(item["candidate_id"]) +
                    ". Check every mandatory source fact and all material claims. Artifact structure may reveal the method.</p>"
                    "<main><section><h2>Original source</h2><pre>" + html.escape(source) +
                    "</pre></section><section><h2>Candidate answer</h2><pre>" + html.escape(answer) +
                    "</pre></section></main><details><summary>Frozen human source reference</summary><pre>" +
                    html.escape(json.dumps(reference, ensure_ascii=False, indent=2)) +
                    "</pre></details><p><a href='grade.template.json'>Human score template</a></p>")
        (directory / "index.html").write_text(document, encoding="utf-8")
    return {"scoring_packets": len(rows), "model_calls": 0}


def import_timed_submission(run_dir, submission_path):
    """Import actual work records separately from their later quality judgment."""
    from .results import verify_output_freeze
    run = Path(run_dir)
    verify_output_freeze(run)
    read = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    record = read(submission_path)
    people = {p["reviewer_id"]: p for p in read(run / "human-roster.json")["reviewers"]}
    person = people.get(record.get("reviewer_id"), {})
    if person.get("human") is not True or person.get("role") != "timed_reviewer":
        raise ValueError("Timed records require a registered actual human timed reviewer")
    assignments = read(run / "review/private-assignment-map.json")["assignments"]
    matching = [a for a in assignments if a["assignment_id"] == record.get("assignment_id")]
    if len(matching) != 1 or record.get("case_id") != matching[0]["case_id"]:
        raise ValueError("A timed record must match its exact assigned source")
    authors = [p["reviewer_id"] for p in people.values() if p.get("role") == "reference_verifier"]
    validated = validate_timed_record(record, matching[0], authors)
    if (not record.get("started_at") or not record.get("finished_at")
            or record.get("attestation") != "I personally performed this timed review without consulting this case reference or another method answer."
            or record.get("final_quality") != "pending_independent_adjudication"):
        raise ValueError("A timed submission requires personal attestation and separately pending quality adjudication")
    path = run / "review/submissions" / (matching[0]["assignment_id"] + ".json")
    write_json(path, record, immutable=True)
    manifest_path = run / "review/import-manifest.json"
    manifest = read(manifest_path) if manifest_path.exists() else {"records": []}
    item = {"assignment_id": matching[0]["assignment_id"], "reviewer_id": record["reviewer_id"],
            "path": path.relative_to(run).as_posix(), "sha256": sha256(path),
            "import_source": "human_user_submission"}
    if item not in manifest["records"]:
        manifest["records"].append(item)
        write_json(manifest_path, manifest)
    return {**item, "active_seconds": validated["active_seconds"], "quality": "pending_independent_adjudication"}


def import_timed_adjudication(run_dir, submission_path):
    """A separate verifier judges the corrected conclusion against source."""
    from .corrigenda import resolve_grading_run, assert_active_grading_epoch, sync_timed_submissions
    run = resolve_grading_run(run_dir)
    epoch = assert_active_grading_epoch(run)
    if epoch:
        sync_timed_submissions(run)
    read = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    item = read(submission_path)
    if epoch and item.get("grading_epoch_id") != epoch["epoch_id"]:
        raise ValueError("A corrected timed-quality judgment requires the current grading_epoch_id")
    people = {p["reviewer_id"]: p for p in read(run / "human-roster.json")["reviewers"]}
    person = people.get(item.get("reviewer_id"), {})
    records = read(run / "review/import-manifest.json")["records"]
    matching = [r for r in records if r["assignment_id"] == item.get("assignment_id")]
    if (person.get("human") is not True or person.get("role") != "reference_verifier"
            or len(matching) != 1 or item.get("reviewer_id") == matching[0]["reviewer_id"]):
        raise ValueError("Timed quality adjudication requires a separate registered human verifier")
    original = (run / matching[0]["path"]).resolve()
    if (not original.is_relative_to((run / "review/submissions").resolve())
            or sha256(original) != matching[0]["sha256"]):
        raise ValueError("The personally timed submission changed before quality adjudication")
    if (item.get("submission_sha256") != matching[0]["sha256"]
            or item.get("quality") not in {"correct", "incorrect", "unresolved"}
            or not item.get("evidence") or not item.get("reason") or not item.get("attested_at")
            or item.get("human_verified") is not True):
        raise ValueError("Timed adjudication requires exact submission identity and source-based human judgment")
    path = run / "review/adjudications" / (canonical_hash(item)[:24] + ".json")
    write_json(path, item, immutable=True)
    record = {"path": path.relative_to(run).as_posix(), "sha256": sha256(path),
              "assignment_id": item["assignment_id"], "reviewer_id": item["reviewer_id"],
              "import_source": "human_user_submission"}
    manifest_path = run / "review/adjudications/import-manifest.json"
    manifest = read(manifest_path) if manifest_path.exists() else {"records": []}
    if record not in manifest["records"]:
        if any(r["assignment_id"] == record["assignment_id"] for r in manifest["records"]):
            raise ValueError("Preserve a timed-quality revision explicitly before importing another judgment")
        manifest["records"].append(record)
        write_json(manifest_path, manifest)
    return record
