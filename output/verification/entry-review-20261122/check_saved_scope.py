"""Evaluate current prompt construction on immutable GA4 materials, offline."""
import json
from pathlib import Path
import sys

from skillflow.common.delivery_size import inspect_delivery
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.document_guided.fragment_display import fragment_prompt_parts
from skillflow.document_guided.fragment_revision import processing_scope
from skillflow.document_guided.online import processing_revision_evidence
from skillflow.document_guided.prompts import build_fragment_prompt, build_processing_revision_prompt
from skillflow.document_guided.source import render_source, source_packet
from skillflow.document_guided.sensitivity_entries import entry_catalogue
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS


def main():
    project = Path(__file__).resolve().parents[3]
    parent = project / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"

    def read(path):
        return json.loads((parent / path).read_text(encoding="utf-8"))

    cfg = read("graph/selected.json")["cfg"]
    proc = read("steps/processing/value.json")
    source = read_snapshot(parent / "source")[1]
    files = {"skill/" + f["path"]: f["content"] for f in source["files"]}
    task = read(read("selection.json")["task"]["path"])
    flow = (parent / read("accepted-upstream.json")["owners"]["flow"] / "document.md").read_text(encoding="utf-8")
    gaps, rejected = processing_revision_evidence(parent / "steps/processing")
    findings = read("review/result.json")["review"]["findings"]
    scope = processing_scope(cfg, cfg, findings, proc, gaps, rejected_records=rejected)
    expected = {"ir_167", "ir_311", "ir_329", "ir_346"}
    assert expected == set(rejected)
    for ir in expected:
        slot = scope["slots"][ir]
        assert slot["rejected_record"] == rejected[ir] and not slot["allow_keep"]
        assert slot["validation_gaps"] and slot["required_attachments"]
    assert scope["read_only"]["locations"] == proc["locations"]
    assert scope["read_only"]["expressions"] == proc.get("expressions", [])
    rules = (parent / "steps/processing/prompt.txt").read_bytes().decode("utf-8").split(
        "GLOBAL REQUIREMENTS AND LIMITATIONS\n", 1)[1].split("\n\nRELATED SOURCE\n", 1)[0]
    prompts = {"revision-processing": build_processing_revision_prompt(files=files, flow=flow,
        runtime_contract=runtime_contract(), scope=scope, global_requirements=rules)}
    for kind in ("sensitivity", "task-correspondence"):
        prompts[kind] = build_fragment_prompt(kind, files=files, cfg=cfg,
            documents={"processing": proc}, task=task if kind == "task-correspondence" else None,
            global_requirements=rules, self_check=True)
    metrics = {}
    for name, prompt in prompts.items():
        assert prompt.count("RELATED SOURCE\n" + render_source(source_packet(files)) + "\n\nOUTPUT REQUIREMENTS\n") == 1
        logical = fragment_prompt_parts(prompt)[1]
        if name == "revision-processing":
            assert logical["scope"] == scope
        elif name == "sensitivity":
            assert logical["entry_catalogue"] and "task" not in logical
        else:
            assert logical["task"] == task
        metrics[name] = inspect_delivery(prompt, prefix=ENVELOPE, max_characters=MAX_INPUT_CHARS)
        assert metrics[name]["status"] == "within_limit", name
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "online-ga4-entry-review-20261122"))
    from sensitivity_observations import summarize
    samples = [{**site, "source_entry_origin": "environment", "source_entry_location": entry["location"],
                "source_access_id": site["access_id"]} for entry in entry_catalogue(cfg, proc).values()
               for site in entry["accesses"] if site["instruction_id"] == "ir_090" and "case_path" in site
               and "environment" in entry["origins"]]
    witnessed = summarize(samples, cfg, proc, read("annotation/audit/compiled-response.json"),
        read("annotation/audit/compilation-map.json"), read("propagation/records.json"), read("propagation/data.json"))
    assert witnessed["witnessed_distinct_access_sites"] == 3 and witnessed["witnessed_data_versions"] == 1
    print(json.dumps({"status": "passed", "historic_material": parent.name,
        "old_runs_executed": 0, "model_calls": 0, "validation_roots": sorted(expected),
        "editable_instructions": len(scope["slots"]), "read_only_locations": len(proc["locations"]),
        "source_files": len(files), "source_sha256": source["source_sha256"], "preflight": metrics,
        "record_mapping_check": witnessed}, indent=2))


if __name__ == "__main__":
    main()
