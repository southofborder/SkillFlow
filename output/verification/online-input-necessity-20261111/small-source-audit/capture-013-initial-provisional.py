"""Read the new 013 Task/flow only; no analysis or replay is performed."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-013-input-necessity-high-20261111-173347"
inventory = json.loads((OUT / "013.json").read_text(encoding="utf-8"))
task = json.loads((RUN / "task/task.json").read_text(encoding="utf-8"))
paths = ["task/task.json", "steps/flow/document.md", "source/inputs/package/SKILL.md"]
artifacts = [{"path": str((RUN / rel).relative_to(ROOT)).replace("\\", "/"),
    "sha256": hashlib.sha256((RUN / rel).read_bytes()).hexdigest(), "bytes": (RUN / rel).stat().st_size} for rel in paths]
assert artifacts[2]["sha256"] == inventory["files"][0]["sha256"]
assert task["source_sha256"] == inventory["continuation_pin"]["content_sha256"]
refs = {
    "013-acquisition": ["read_source_id", "read_fast_key"],
    "013-fast-first": ["preferred_fetch_with_key", "direct_archive_without_key"],
    "013-fast-interface": ["preferred_fetch_with_key", "preferred_retry"],
    "013-retry-control": ["preferred_retry"],
    "013-fallback-control": ["direct_archive_without_key", "archive_after_preferred_failure"],
    "013-archive-interface": ["archive_only_argument", "archive_call_limit"],
    "013-success-output": ["return_success_body", "stop_fetching_on_success"],
    "013-archive-failure": ["return_archive_failure"],
    "013-key-ban": ["no_key_to_archive", "no_key_in_diagnostics"],
    "013-status-append": ["append_final_status"],
}
known = {x["id"] for x in task["requirements"]}
assert {rid for row in refs.values() for rid in row} == known
report = {
    "schema_version": "skillflow-provisional-source-comparison-v1", "case": "013",
    "status": "provisional_task_flow_only", "observed_at": datetime.now(timezone.utc).isoformat(),
    "scope": "Read-only source comparison with the ten prewritten 013 expectations, part of the 26-expectation small-case inventory. Not a gold benchmark or pipeline feedback.",
    "artifacts": artifacts, "task_sha256": task["task_sha256"], "source_sha256": task["source_sha256"],
    "expectations": [{"id": x["id"], "source_evidences": x["evidences"], "task_requirement_ids": refs[x["id"]],
        "status": "represented_in_task_and_flow_pending_generated_semantics"} for x in inventory["expectations"]],
    "task_requirement_count": len(task["requirements"]), "task_issues": task["issues"],
    "source_judgments": [
        {"scope": "FAST_KEY", "finding": "Task and flow distinguish presence for routing from the complete credential value passed to fast.fetch. They prohibit the key in archive arguments and diagnostics without claiming that key presence reveals its plaintext."},
        {"scope": "retry_and_fallback", "finding": "Task and flow retain exactly one retry after a first transient failure, no retry for a first non-transient failure, archive after failed retry, and at most one archive call. Actual bounded call-case representation and pairing await processing."},
        {"scope": "success_and_failure_returns", "finding": "Task and flow retain the whole unchanged body from the successful attempt and the archive error from that failing call. They do not invent a response status-field path. Append must precede every terminal return."},
        {"scope": "local_ambiguities", "finding": "Task identifies unspecified transient-error classification and final-status representation. These have concrete source anchors and overlap the prewritten outcome-encoding/status questions. Explicit semantic call cases should preserve supported input/output relations without guessing a concrete response schema; any field-level uncertainty must remain local."},
        {"scope": "flow_extra_gaps", "finding": "Flow additionally notes unspecified append-failure behavior and hypothetical later result-file/analysis/summary association. These are not new source obligations and must not manufacture extra inputs, outputs or demands."},
    ],
    "coverage": {"task_expectations_compared": 10, "graph_inspected": False, "processing_inspected": False,
        "source_review": "not_inspected", "propagation": "not_inspected", "doe": "not_inspected", "validated_deletions": []},
    "limits": ["This snapshot establishes only Task/flow textual representation, not operational reach, accepted contract coverage, preservation or deletion.", "No source edit, production/prompt change, model call, Skill execution or replay was performed."]
}
destination = OUT / "013-initial-provisional.json"
if destination.exists():
    raise RuntimeError("Preserve the initial snapshot; use new filenames for later audits.")
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "013-initial-provisional.md").write_text("""# 013 Task/flow provisional comparison

All ten prewritten 013 source expectations are represented by the new Task's fourteen requirements and the flow document. Source bytes match the original pin. The credential gate, two fast arguments, exact one-retry condition, three fallback reasons, source_id-only archive input, archive call bound, unchanged successful body, terminal archive error, credential prohibitions and append-before-return obligations are retained.

Task names two concrete local ambiguities: transient-error classification and final-status contents/serialization. These overlap the prewritten outcome-encoding and status questions. Supported bounded call cases should retain stated outcome distinctions without inventing wire fields. The uncertainties do not themselves erase source_id, FAST_KEY or successful-body relationships. Flow's additional unspecified append-failure and hypothetical later-analysis association are not new Task duties or input requirements.

This snapshot inspects Task and flow only. It makes no CFG reach, contract acceptance, field-removal or constraint-preservation claim. Later selected-artifact audit will remain separate. The adjacent JSON provides each expectation's exact source spans and Task requirement IDs. No feedback was sent into the running pipeline and no production, prompt, source or run artifact was changed.
""", encoding="utf-8")
print(json.dumps({"saved": str(destination), "expectations": 10, "task_requirements": len(task["requirements"]), "source_hash_verified": True}))
