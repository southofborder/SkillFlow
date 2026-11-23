"""Read terminal receipts, compare stage coverage and record bounded metrics."""
from collections import Counter
import json
from pathlib import Path
import sys

from skillflow.common.artifact_io import atomic_write_chunks

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PREVIOUS = HERE.parent / "online-ga4-lossless-delivery-20261119"
sys.path.insert(0, str(PREVIOUS))
from request_audit import audit as audit_requests
from backend_audit import report as audit_backend
from sensitivity_observations import summarize as observed_ingress


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def optional(path):
    return read(path) if path.exists() else {}


def write(name, value):
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    atomic_write_chunks(HERE / name, [text], match_existing=True)


def main():
    run = Path(read(HERE / "prepared-run.json")["run_directory"])
    done = read(run / "controller-finished.json")
    assert read(run / "continuation-state.json")["status"] == "generation_closed"
    requests = optional(HERE / "final-request-audit.json") or audit_requests(run)
    if Path(requests["run"]).resolve() != run.resolve():
        raise ValueError("Request audit belongs to a different run")
    backend = audit_backend(run)
    result = read(run / "result.json")
    coverage = optional(run / "propagation/manifest.json").get("coverage")
    raw_records = optional(run / "propagation/records.json")
    initial = optional(run / "steps/processing/result.json")
    scoped = optional(run / "revision/processing-scope.json")
    initial_gaps = {row["instruction_id"]: row for row in initial.get("validation_gaps", [])}
    revision = optional(run / "steps/revision-processing/value.json")
    selection = optional(run / "selection.json")
    annotation_path = (selection.get("annotation") or {}).get("path")
    owners = {}
    if annotation_path:
        assembly = (run / annotation_path).parent
        for kind, reference in read(assembly / "inputs/references.json")["fragment_steps"].items():
            owner = (assembly / reference["path"]).resolve()
            if not owner.is_relative_to(run) or read(owner / "manifest.json")["manifest_sha256"] != reference["manifest_sha256"]:
                raise ValueError("Selected fragment reference does not resolve: " + kind)
            owners[kind] = owner
    revision_selected = owners.get("processing") == (run / "steps/revision-processing")
    facts = {}
    for ir in sorted(set(initial_gaps) | {"ir_167", "ir_311", "ir_329", "ir_346"}):
        facts[ir] = {"initially_excluded": ir in initial_gaps if initial else None,
                     "initial_diagnostics": initial_gaps.get(ir, {}).get("validation_errors"),
                     "offered_for_revision": ir in scoped["slots"] if scoped else None,
                     "revised_modeled": ir in revision.get("ir_semantics", {}) if revision else None,
                     "revision_selected": revision_selected if annotation_path else None,
                     "selected_coverage": (coverage or {}).get(ir)}
    def events(value):
        if isinstance(value, list):
            for item in value:
                yield from events(item)
        if isinstance(value, dict):
            if "op" in value and isinstance(value.get("alternatives"), list):
                yield value
            else:
                for item in value.values():
                    yield from events(item)
    guard_counts = Counter()
    builds = {}
    for ir, record in raw_records.items():
        for op in events(record):
            choices = op["alternatives"]
            guard_counts["operations_with_selector_bindings"] += any(
                any(k.startswith("selector:") for k in alt.get("bindings", {})) for alt in choices)
            guard_counts["recorded_alternatives"] += len(choices)
            if ir == "ir_415" and op["op"] == "build":
                builds.setdefault(ir, []).append({"alternatives": len(choices),
                    "output_versions": [len(group) for group in op.get("outputs", [])]})
    doe = optional(run / "doe/doe-result.json")
    index = optional(run / "doe/audit/index.json")
    access_rows = list(index.get("declarations", {}).values())
    selected_owner = owners.get("sensitivity")
    sensitivity = optional(selected_owner / "value.json") if selected_owner else {}
    declared = sensitivity.get("declarations", [])
    witnessed = None
    if sensitivity and annotation_path and coverage is not None:
        cfg = read(run / selection["cfg"]["path"])["cfg"]
        witnessed = observed_ingress(declared, cfg, read(owners["processing"] / "value.json"),
            read(assembly / "audit/compiled-response.json"), read(assembly / "audit/compilation-map.json"),
            raw_records, read(run / "propagation/data.json"))
    classified = {(r["source_entry_id"], json.dumps(r["path"], sort_keys=True), r["property"], r["label"],
                   r["source_entry_applicability"]) for r in declared}
    summary = {"run": run.name, "result": result, "controller": done, "sources": requests["source"],
        "usage": requests["usage"], "request_counts": requests["counts"], "repair_targets": facts,
        "review": backend["selected_review_receipt"], "propagation": backend["propagation"],
        "demand": backend["demand"], "doe": backend["doe"], "branch_record_metrics": dict(guard_counts) if coverage is not None else None,
        "former_81_version_site": builds.get("ir_415"), "selection": selection,
        "selected_fragments": {k: p.relative_to(run).as_posix() for k, p in owners.items()},
        "sensitivity": {"selected_owner": selected_owner.name, "classified_entries": len({r["source_entry_id"] for r in declared if r.get("source_entry_id")}),
            "distinct_field_classifications": len(classified), "lexical_declarations": len(declared),
            "distinct_modeled_access_sites": len({r["source_access_id"] for r in declared}), "forward_read_evidence": witnessed,
            "entry_gaps": sensitivity.get("entry_gaps", []), "indexed_declarations": len(access_rows) if index else None,
            "equivalent_groups": len(doe["declaration_aliases"]) if doe else None, "coverage": doe.get("coverage") if doe else None,
            "aliased_site_declarations": sum(map(len, doe.get("declaration_aliases", {}).values())) if doe else None,
            "derivations_by_relation": dict(Counter(row["relation"] for row in doe["derivations"]["sensitivity"].values())) if doe else None
        } if sensitivity and annotation_path else None,
        "artifact_bytes": {p.name: p.stat().st_size for p in (run / "doe").glob("*")
                           if p.name in ("report.md", "report.html", "doe-result.json")},
        "timing": read(run / "component-timing.json"),
        "note": "Accesses and alternatives are counts in the selected static model. A semantic correction requires consistent revised material and review. Absence of the same structural failure in a fresh model answer is recorded separately from a repair."}
    write("final-request-audit.json", requests)
    write("final-backend-audit.json", backend)
    write("run-summary.json", summary)
    print(json.dumps({"status": done["status"], "replay": done["replay"], "artifacts": summary["artifact_bytes"]}))


if __name__ == "__main__":
    main()
