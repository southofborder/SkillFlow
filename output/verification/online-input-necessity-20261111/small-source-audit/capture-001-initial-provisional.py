"""Read-only snapshot comparison of new 001 Task/flow/CFG, never a replay."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-001-input-necessity-high-20261111-173347"

def read(rel):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))

def artifact(rel):
    data = (RUN / rel).read_bytes()
    return {"path": str((RUN / rel).relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

task = read("task/task.json")
graph = read("steps/graph/value.json")
source = artifact("source/inputs/package/SKILL.md")
inventory = json.loads((OUT / "001.json").read_text(encoding="utf-8"))
assert source["sha256"] == inventory["files"][0]["sha256"]
assert task["source_sha256"] == inventory["continuation_pin"]["content_sha256"]

comparisons = [
    {"expectation_id": "001-selection", "status": "represented_pending_semantic_review",
     "source_lines": [9, 10],
     "task_refs": ["/requirements/1", "/issues/0"],
     "graph_refs": ["instruction_0005", "instruction_0006", "instruction_0007", "instruction_0008", "instruction_0009", "instruction_0010"],
     "finding": "CFG checks opted_out before urgency, evaluates value >= 100 only after urgent is not true, and never waives opted_out. Task additionally records necessary-versus-sufficient selection ambiguity from 'only when'; flow/CFG implement the ordinary filter reading. This source-backed judgment is additional to the prewritten inventory and awaits review; it is not silently counted as agreement or as a generic black-box gap."},
    {"expectation_id": "001-per-record-action", "status": "represented_pending_semantic_review",
     "source_lines": [11, 13], "task_refs": ["/requirements/2", "/requirements/3", "/requirements/5"],
     "graph_refs": ["instruction_0003", "instruction_0004", "instruction_0013", "instruction_0014"],
     "finding": "One notify.send site lies in the selected-member branch and returns to the loop header. Both arguments derive from the same current_record. No deduplication or record_id identity use is authored. Per-occurrence/member execution coverage is not yet evaluated."},
    {"expectation_id": "001-notify-recipient", "status": "represented_pending_semantic_review",
     "source_lines": [11, 11], "task_refs": ["/requirements/3"],
     "graph_refs": ["instruction_0011", "instruction_0013"],
     "finding": "The recipient argument is the selected current_record.recipient projection, not the entire record. No reviewed interface-input contract or reverse demand exists yet in this snapshot."},
    {"expectation_id": "001-notify-body", "status": "represented_pending_semantic_review",
     "source_lines": [12, 15], "task_refs": ["/requirements/4"],
     "graph_refs": ["instruction_0012", "instruction_0013"],
     "finding": "The body argument is the original current_record.summary projection from the same record. Task explicitly forbids generation, rewriting and conversion. Retention of the complete summary must still be checked in final demand results."},
    {"expectation_id": "001-token-ban", "status": "represented_pending_semantic_review",
     "source_lines": [14, 14], "task_refs": ["/requirements/6"],
     "graph_refs": ["/constraints/1", "instruction_0001"],
     "finding": "Task/CFG state the any-recipient ban. The acquisition still includes access_token in the stated record schema, while no token argument is authored at notify.send. This is not an executed flow or proof that every later generated observation is safe."},
    {"expectation_id": "001-count-output", "status": "source_ambiguity_preserved_pending_review",
     "source_lines": [16, 16], "task_refs": ["/requirements/7", "/issues/1"],
     "graph_refs": ["instruction_0015", "instruction_0016"],
     "finding": "The count write follows traversal exit. Task/flow/CFG retain the actual ambiguity between all evaluated records and selected notification records. CFG authors a count operation over event_records with an unspecified counting rule; no necessary fields or count correctness are established yet."},
    {"expectation_id": "001-acquired-result", "status": "acquisition_represented_ranges_not_evaluated",
     "source_lines": [8, 16], "task_refs": ["/requirements/0"],
     "graph_refs": ["instruction_0001", "instruction_0004", "instruction_0015"],
     "finding": "The source acquisition and five useful field projections are present. record_id and access_token have no authored positive field use in this first CFG. Their post-acquisition removability, retained structural demands, constraints and acquisition projection capability remain unevaluated."},
]

report = {
    "schema_version": "skillflow-provisional-source-comparison-v1",
    "case": "001", "observed_at": datetime.now(timezone.utc).isoformat(),
    "status": "provisional_initial_task_flow_cfg_only",
    "run_directory": str(RUN).replace("\\", "/"),
    "scope": "Read-only comparison with seven prewritten 001 expectations. The total three-case inventory contains 26 expectations; this snapshot audits only 001. Not a gold benchmark or controller/replay execution.",
    "artifacts": [source, artifact("task/task.json"), artifact("steps/flow/document.md"), artifact("steps/graph/value.json")],
    "bindings": {"source_sha256": task["source_sha256"], "task_sha256": task["task_sha256"]},
    "generated_cfg": {"blocks": len(graph["blocks"]), "instructions": sum(len(x["instructions"]) for x in graph["blocks"]), "edges": len(graph["edges"])},
    "coverage": {"expectations_compared": 7, "source_boundary_sites": 3,
        "boundary_sites": [{"source_lines": [8, 8], "kind": "read", "graph_ref": "instruction_0001"}, {"source_lines": [11, 12], "kind": "call", "graph_ref": "instruction_0013"}, {"source_lines": [16, 16], "kind": "write", "graph_ref": "instruction_0016"}],
        "boundary_representation": "All three finite source boundary sites are present in the first CFG. Representation does not establish propagation reach or reviewed correctness.",
        "propagation_status": "not_available_at_snapshot", "processed_ir": None, "reached_source_boundary_sites": None,
        "doe_status": "not_available_at_snapshot", "validated_deletion_examples": []},
    "comparisons": comparisons,
    "audit_judgments": [{"id": "001-additional-selection-ambiguity", "source_lines": [9, 11],
        "status": "pending_review", "reason": "The initial inventory used the ordinary procedural filter reading. The new Task interprets 'only when' as specifying necessary conditions only. Both claims are exposed here for later source review; no historical answer is used as authority.",
        "affected_scope": "Selection completeness and selected-occurrence obligations; unchanged recipient/body relations and the token ban remain independently stated."}],
    "limits": ["Current generated artifacts may be revised before final selection.", "No processing contract, source review, propagation, demand, constraint-preservation result or DOE deletion conclusion is audited in this initial snapshot.", "No real model call, Skill execution or replay was launched by this audit.", "The source-only inventory is a finite comparison aid, not a complete semantic specification or empirical execution oracle."]
}
destination = OUT / "001-initial-provisional.json"
if destination.exists():
    raise RuntimeError("Preserve the initial provisional snapshot; write later audits under new filenames.")
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
lines = ["# 001 initial provisional source comparison", "", f"Observed: {report['observed_at']}", "", report["scope"], "", "Task, flow and the first CFG are present. The generated CFG contains 7 blocks, 17 IR instructions and 10 edges. All three source boundary sites (events.json read, notify.send, count.txt write) are represented; none has a measured propagation reach count in this snapshot.", "", "| Expectation | Snapshot assessment |", "| --- | --- |"]
lines.extend(f"| {c['expectation_id']} | {c['finding']} |" for c in comparisons)
lines += ["", "The count-population ambiguity matches the prewritten source inventory. Task also raises a narrower literal-reading issue about whether 'only when' requires every eligible record to be selected. The initial inventory used the ordinary procedural filter reading; final review must resolve or explicitly retain this judgment. It is not counted as an established model error here.", "", "No deletion examples are established yet. In particular, the lack of an authored record_id/access_token positive use does not by itself certify removal until actual contracts, demands, constraints and observations are reviewed. Source acquisition remains an observed action; a later field-use recommendation must not be described as established server/read-side projection support.", "", "This snapshot is preserved separately from later selected-artifact audits. Artifact hashes and exact Task/CFG references are in the adjacent JSON. No production, prompt, source or run artifact was edited.", ""]
(OUT / "001-initial-provisional.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"saved": str(destination), "expectations": 7, "instructions": 17, "source_hash_verified": True}))
