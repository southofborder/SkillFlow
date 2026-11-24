"""Check the archived 134-slot processing reply in memory against the current scoped compiler."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.common.revision_slots import read_revision_object
from skillflow.document_guided.fragment_revision import processing_scope
from skillflow.document_guided.online import processing_revision_evidence
from skillflow.document_guided.revision_assembly import assemble_revision

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-entry-occurrence-high-20261124-143923"
ARTIFACTS = ("review/result.json", "graph/initial.json", "graph/revision.json",
             "steps/processing/value.json", "steps/processing/result.json",
             "revision/processing-scope.json", "steps/revision-processing/calls/a001/response.json")


def main():
    files = {name: json.loads((RUN/name).read_bytes()) for name in ARTIFACTS}
    raw = files[ARTIFACTS[-1]]
    source = read_snapshot(RUN/"source")[1]
    assert len(source["files"]) == 16
    assert source["source_sha256"] == "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
    fixture = ROOT/"tests/fixtures/ga4_entry_occurrences/revision-processing-response.txt"
    assert fixture.read_bytes() == raw.encode()
    revised = files["graph/revision.json"]["cfg"]
    old = files["steps/processing/value.json"]
    gaps, rejected = processing_revision_evidence(RUN/"steps/processing")
    scope = processing_scope(files["graph/initial.json"]["cfg"], revised,
                             files["review/result.json"]["review"]["findings"],
                             old, gaps, rejected_records=rejected)
    historic = files["revision/processing-scope.json"]
    assert set(scope["slots"]) == set(historic["slots"]) and len(scope["slots"]) == 134
    decoded = read_revision_object(raw)
    assert len(decoded.repairs) == 1 and len(decoded.value["shared_values"]) == 73
    checked, local_gaps, receipt = assemble_revision("processing", raw, {
        "processing_revision": {"scope": scope, "previous": old},
        "validation_gaps": scope["retained_validation_gaps"],
        "files": {"skill/"+row["path"]: row["content"] for row in source["files"]}},
        {"source": source, "cfg": revised})
    assert (set(receipt["accepted"]) | set(receipt["retained_prior"]) | set(receipt["quarantined"])) == set(scope["slots"])
    assert receipt["assembled_sha256"] == canonical_sha256(checked)
    facts = {
        "mode": "archived reply, program-only current-scope assembly", "run":RUN.name,
        "source_sha256": source["source_sha256"], "source_files":16,
        "original_artifacts":{n:sha_file(RUN/n) for n in ARTIFACTS},
        "reply_utf8_sha256":hashlib.sha256(raw.encode()).hexdigest(), "reply_characters":len(raw),
        "old_scope_sha256":historic["scope_sha256"], "current_scope_sha256":scope["scope_sha256"],
        "authorized_slots":134, "shared_definitions":73, "repairs":decoded.repairs,
        "submitted":len(receipt["submitted"]), "accepted":len(receipt["accepted"]),
        "retained_prior":receipt["retained_prior"], "quarantined":receipt["quarantined"],
        "validation_gaps":sorted({g["instruction_id"] for g in local_gaps}),
        "diagnostic_counts":dict(Counter(d["code"] for d in receipt["diagnostics"])),
        "assembly_sha256":receipt["assembled_sha256"],"receipt_sha256":canonical_sha256(receipt),
        "model_calls":0, "skill_executions":0, "historical_run_modified":False}
    print(json.dumps(facts,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
