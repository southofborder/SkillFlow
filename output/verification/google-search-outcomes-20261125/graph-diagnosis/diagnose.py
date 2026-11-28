"""New-copy-only offline graph-patch diagnosis; no replay or semantic acceptance."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529"
sys.path.insert(0, str(ROOT / "src"))

from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.document_guided.call_region import call_sites


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    path = RUN / "steps/graph/calls/a001/response.json"
    original_bytes = path.read_bytes()
    raw = json.loads(original_bytes)
    original = json.loads(raw) if isinstance(raw, str) else raw
    files = {"skill/" + relative: (RUN / "source/inputs/package" / relative).read_bytes().decode("utf-8")
             for relative in ("SKILL.md", "scripts/search.py")}
    baseline = assemble_graph_facts(deepcopy(original), files=files)
    plan = plan_graph_repair(baseline, files=files)
    slot = next(value for value in plan["slots"].values() if value["kind"] == "call_region")
    block = next(b for b in baseline.facts["blocks"] if b["ref"] == "helper.prepare")
    fixed = deepcopy(block)
    operation = fixed["operations"][0]
    # Repair only the four-parameter table. This does NOT repair or certify the
    # separate continuation marker: all control topology remains untouched.
    removed = {predecessor: row.pop("helper.return_scope")
               for predecessor, row in operation["metadata"]["predecessor_bindings"].items()}
    for key in ("source", "source_actions", "inputs", "outputs"):
        assert operation[key] == block["operations"][0][key]
    assert fixed["exit"] == block["exit"]
    packet = {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"], "value": [fixed]}]}
    nofix = {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"], "value": [deepcopy(block)]}]}
    unchanged = apply_graph_updates(baseline, plan, nofix, files=files)
    patched = apply_graph_updates(baseline, plan, packet, files=files)
    assert baseline.cfg is None and unchanged.cfg is None and patched.cfg is None
    assert any(row["code"] == "call_return_binding" for row in baseline.gaps)
    assert any(row["code"] == "cfg_region_boundary" and "physical invocation or parameter evidence" in row["message"]
               for row in patched.patch_diagnostics)

    proposed = deepcopy(baseline.facts)
    proposed["blocks"] = [fixed if b["ref"] == fixed["ref"] else b for b in proposed["blocks"]]
    before = [site for site in call_sites(baseline.facts, files) if site["caller"] == "cli.invoke_helper"]
    after = [site for site in call_sites(proposed, files) if site["caller"] == "cli.invoke_helper"]
    assert len(before) == len(after) == 1 and before[0]["errors"] and not after[0]["errors"]
    consumers = [b for b in original["blocks"] if b["ref"] in {"helper.return_dispatch", "helper.merge_exception"}]
    assert len(consumers) == 2 and all({"result": "helper.return_scope"} in b["exit"]["conditions"] for b in consumers)

    save("original-draft-copy.json", original)
    save("program-issued-plan.json", plan)
    save("unchanged-patch.json", nofix)
    save("parameter-table-only-patch.json", packet)
    save("parameter-table-only-proposed-copy.json", proposed)
    result = {"kind": "independently_labelled_offline_patch_compiler_diagnosis", "model_calls": 0,
        "historical_replays": 0, "source_changes": False, "original_run_writes": False,
        "original_draft_path": str(path), "original_draft_bytes_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "original_draft_unchanged": path.read_bytes() == original_bytes,
        "baseline_diagnostics": baseline.gaps, "slot_id": slot["slot_id"],
        "unchanged_patch_diagnostics": unchanged.patch_diagnostics,
        "parameter_table_only_patch_diagnostics": patched.patch_diagnostics,
        "parameter_table_only_removes_call_site_error": not after[0]["errors"],
        "removed_nonparameter_entries": removed,
        "unchanged_source_and_action_spans": {"operation": operation["source"], "source_actions": operation["source_actions"]},
        "blocking_contracts": [
            {"file": "src/skillflow/document_guided/call_region.py", "issue": "Changed formal requires every child action span to equal its parent operation span. Real parent spans 6-13; retained child spans are 6, 7, 8-13."},
            {"file": "src/skillflow/document_guided/call_region.py", "issue": "Non-source metadata must remain identical. This includes predecessor_bindings that this error requires correcting, although metadata is in the formal grant's allowed fields."}],
        "continuation_consumers": consumers,
        "continuation_unresolved": "helper.return_scope routes both normal returns and thrown exceptions to independent-public or CLI continuations. Removing its illegal literal parameter entries does not establish a source-backed producer for this token. Four Python argument values do not identify the caller.",
        "current_slot_limitation": "Call-region updates name existing authorized blocks only and keep original actions. This grant cannot add/clone callee blocks to statically separate call contexts. It also cannot rewrite the ungranted helper.merge_exception exit.",
        "interpretation": "Pointer/guidance alone cannot express the source-preserving parameter-table repair through this issued patch contract. Fixing the two narrow gates alone would still not establish a source-faithful complete repair of this candidate's continuation routing.",
        "semantic_limit": "No repaired CFG is accepted. No source or edges are changed, no normal/exception paths are merged, and helper.return_scope is not certified as source data. The proposed edit is only a parameter-table diagnosis.",
        "cfg_accepted": False}
    save("diagnosis.json", result)
    print(json.dumps({"baseline_cfg": baseline.cfg is not None, "patched_cfg": patched.cfg is not None,
        "patch_rejections": patched.patch_diagnostics, "direct_call_site_error_removed": not after[0]["errors"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
