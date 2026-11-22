"""Render preserved GA4 inputs offline and verify their exact logical content."""
import hashlib
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.annotation_wire import expression_reference_view
from skillflow.document_guided.fragment_display import fragment_prompt_parts
from skillflow.document_guided.prompts import build_fragment_prompt
from skillflow.document_guided.source import prompt_cfg, render_source, source_packet
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS
from skillflow.common.delivery_size import inspect_delivery

PARENT = PROJECT / "experiments/doe/runs/document-guided-ga4-runtime-locality-high-20261117-205158"
MATERIAL = PROJECT / "experiments/doe/runs/document-guided-ga4-program-owned-cfg-high-20261118-162541"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = read_snapshot(MATERIAL / "source")[1]
    files = {"skill/" + row["path"]: row["content"] for row in source["files"]}
    processing = read(MATERIAL / "steps/processing/value.json")
    cfg = read(MATERIAL / "graph/initial.json")["cfg"]
    task = read(PARENT / "inherited/task/task.json")
    if len(files) != 16 or read(PARENT / "graph/selected.json")["cfg"] != cfg:
        raise ValueError("The saved GA4 material differs from the retained source/CFG")
    old_prompt = (MATERIAL / "steps/sensitivity/prompt.txt").read_bytes().decode("utf-8")
    rules = old_prompt.split("GLOBAL REQUIREMENTS AND LIMITATIONS\n", 1)[1].split("\n\nRELATED SOURCE\n", 1)[0]
    source_suffix = "RELATED SOURCE\n" + render_source(source_packet(files)) + "\n\nOUTPUT REQUIREMENTS\n"
    results = {}
    for owner in ("sensitivity", "task-correspondence"):
        for revision in (False, True):
            repair = {"previous_fragment": {"declarations": []} if owner == "sensitivity" else {},
                      "source_rechecks": [{"target_ids": ["ir_090"], "source_refs": []}]} if revision else None
            prompt = build_fragment_prompt(owner, files=files, documents={"processing": processing},
                cfg=cfg, global_requirements=rules, task=task if owner == "task-correspondence" else None,
                repair_context=repair, self_check=True)
            parts = fragment_prompt_parts(prompt)
            if parts is None:
                raise ValueError("The new prompt has no bound lossless material")
            payload = parts[1]
            expected = {"owner": owner, "documents": {"processing": processing},
                        "cfg": prompt_cfg(cfg, packet=source_packet(files))}
            if owner == "task-correspondence":
                expected["task"] = task
                expected["expression_references"] = expression_reference_view(processing)
            if revision:
                expected["repair_context"] = repair
            if payload != expected or prompt.count(source_suffix) != 1:
                raise ValueError("The rendered prompt changed logical input or complete source")
            preflight = inspect_delivery(prompt, prefix=ENVELOPE, max_characters=MAX_INPUT_CHARS)
            if preflight["status"] != "within_limit":
                raise ValueError("The complete offline delivery still exceeds the adapter cap")
            results[owner + ("_full_revision" if revision else "_normal")] = {
                "preflight": preflight, "logical_round_trip_equal": True,
                "complete_source_files": len(files), "complete_source_suffix_equal": True}
    names = ("graph/initial.json", "steps/processing/value.json", "source/inputs/snapshot.json")
    print(json.dumps({"status": "passed", "implementation_sha256": implementation_provenance()["sha256"],
        "native_calls": 0, "old_runs_executed_or_replayed": 0, "source_sha256": source["source_sha256"],
        "inputs": {str(MATERIAL / name): sha(MATERIAL / name) for name in names},
        "material_donor": str(MATERIAL), "results": results}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
