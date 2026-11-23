"""Read-only audit of graph assembly, repair scopes and downstream GA4 results."""
import argparse
from collections import Counter
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
VERIFY = Path(__file__).resolve().parent
PRIOR = VERIFY.parent / "online-ga4-action-alignment-20261123"
baseline = runpy.run_path(str(PRIOR / "assess.py"))
from skillflow.common.artifact_io import file_sha256
from skillflow.document_guided.fragment_display import fragment_prompt_parts


def read(path):
    return json.loads(path.read_bytes())


def stage_audit(run, step):
    folder = run / "steps" / step
    if not (folder / "result.json").exists():
        return None
    result = read(folder / "result.json")
    attempts = []
    for path in sorted((folder / "calls").glob("a*/validation.json")):
        call = path.parent
        validation = read(path)
        diagnostics = validation.get("diagnostics", [])
        raw = read(call / "response.json")
        try:
            raw = json.loads(raw) if isinstance(raw, str) else raw
        except ValueError:
            raw = None
        scope = None
        if step == "revision-graph" or call.name != "a001":
            shown = fragment_prompt_parts((call / "prompt.txt").read_text("utf-8"))
            scope = shown[1].get("scope") if shown else None
        slots = (scope or {}).get("slots", {})
        row = {"attempt": call.name, "status": validation["status"],
               "diagnostics": dict(Counter(d.get("code") for d in diagnostics)),
               "validation": path.relative_to(run).as_posix()}
        if isinstance(raw, dict) and isinstance(raw.get("blocks"), list):
            blocks = [b for b in raw["blocks"] if isinstance(b, dict)]
            row["authored_blocks"] = len(blocks)
            row["authored_source_kinds"] = dict(Counter(str(b.get("source_kind")) for b in blocks))
        if scope is not None:
            row.update(writable_kinds=dict(Counter(s["kind"] for s in slots.values())),
                       writable_targets=[s["target"] for s in slots.values()],
                       findings_without_target=scope.get("unaddressable_findings", []),
                       findings_with_targets={sid: s["finding_ids"] for sid, s in slots.items() if s.get("finding_ids")},
                       submitted_updates=len(raw["updates"]) if isinstance(raw, dict) and isinstance(raw.get("updates"), list) else None)
        attempts.append(row)
    value = None
    if result.get("value_file"):
        if result["value_file"] != "value.json" or file_sha256(folder / "value.json") != result["value_sha256"]:
            raise ValueError("The accepted graph value differs from its bound stage result")
        value = read(folder / "value.json")
    receipt = value.get("assembly", {}) if isinstance(value, dict) else {}
    accepted = isinstance(value, dict) and bool(value.get("cfg"))
    layout = receipt.get("block_layout", {})
    guided = read(run / "result.json").get("stages", {}).get(step, {})
    return {"status": guided.get("status") or result.get("status") or ("complete" if accepted else None), "attempts": attempts,
            "accepted_blocks": len(value["cfg"]["blocks"]) if isinstance(value, dict) and value.get("cfg") else None,
            "program_assembled_blocks": {**dict.fromkeys(("control", "split"), 0),
                **dict(Counter(item["kind"] for item in layout.values()))} if accepted else None,
            "patch_diagnostics": receipt.get("patch_diagnostics")}


def summary(run):
    run = run.resolve()
    result = baseline["summary"](run)
    result["identity"] = "ga4-cfg-assembly-assessment-v1"
    result["graph_attempts"] = {s: stage_audit(run, s) for s in ("graph", "revision-graph")}
    result["processing_deliveries"] = {s: sorted(
        p.relative_to(run).as_posix() for p in (run / "steps" / s / "calls").glob("a*/request.json"))
        for s in ("processing", "revision-processing")}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    if not args.run.is_dir():
        parser.error("Run directory does not exist")
    print(json.dumps(summary(args.run), ensure_ascii=True, allow_nan=False, indent=2))
