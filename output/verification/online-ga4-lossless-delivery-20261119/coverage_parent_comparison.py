"""Compare saved coverage and source-audit bindings; never execute SkillFlow."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[2]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
PARENT = PROJECT / "experiments/doe/runs/document-guided-ga4-runtime-locality-high-20261117-205158"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    current = read(RUN / "propagation/manifest.json")
    parent = read(PARENT / "propagation/manifest.json")
    cfg = read(RUN / "graph/selected.json")["cfg"]
    assert cfg == read(PARENT / "graph/selected.json")["cfg"]
    irs = {i["id"]: {"block": b["block_name"], "opcode": i["opcode"]} for b in cfg["blocks"].values() for i in b["instructions"]}
    source_audit = read(BASE / "initial-source-correctness-audit.json")
    records = read(RUN / "propagation/records.json")
    changes = [{"instruction_id": ir, "parent": parent["coverage"][ir], "current": status, **irs[ir]}
               for ir, status in current["coverage"].items() if parent["coverage"][ir] != status]
    losses = [r for r in changes if r["parent"] == "processed" and r["current"] != "processed"]
    gains = [r for r in changes if r["current"] == "processed" and r["parent"] != "processed"]
    assert len(losses) == 34 and len(gains) == 15
    validation = read(RUN / "steps/processing/calls/a002/validation.json")
    cut_groups = []
    for root, end, cause in [(167, 179, "Five output bindings name undefined locals after one opaque aggregate unpack."),
                             (311, 317, "Nested cases occur inside an ordinary case-segment list; kind/output/cases are forbidden there."),
                             (329, 335, "Nested cases occur inside an ordinary case-segment list; kind/output/cases are forbidden there."),
                             (346, 352, "Nested cases occur inside an ordinary case-segment list; kind/output/cases are forbidden there.")]:
        ids = [f"ir_{n:03}" for n in range(root, end + 1)]
        assert all(parent["coverage"][ir] == "processed" for ir in ids)
        assert current["coverage"][ids[0]] == "unmodeled"
        assert all(current["coverage"][ir] == "blocked" for ir in ids[1:])
        cut_groups.append({"root": ids[0], "affected_ir": ids, "lost_processed_count": len(ids), "reason": cause,
                           "validation_diagnostics": [d for d in validation["diagnostics"] if d["path"].startswith("/ir_semantics/" + ids[0] + "/")]})
    boundary = json.loads(subprocess.run([sys.executable, "-B", str(BASE / "source_boundary_audit.py"), "--run", str(RUN), "--summary"],
                                         check=True, stdout=subprocess.PIPE, text=True, encoding="utf-8").stdout)
    source_status = {}
    for name in ["remote_receiver_evidence", "response_projection_gap_evidence"]:
        source_status[name] = [{"instruction_id": row["instruction_id"], "source_span": row["source_span"],
                                "parent_coverage": parent["coverage"][row["instruction_id"]],
                                "current_coverage": current["coverage"][row["instruction_id"]],
                                "record_exists": row["instruction_id"] in records}
                               for row in source_audit[name]]
    current_files, parent_files = current["implementation"]["files"], parent["implementation"]["files"]
    changed_files = sorted(k for k in current_files.keys() | parent_files.keys() if current_files.get(k) != parent_files.get(k))
    wrapper_evidence = {}
    for label, run, manifest in [("current", RUN, current), ("parent", PARENT, parent)]:
        data = {x["id"]: x for x in read(run / "propagation/data.json")}
        wrapper_evidence[label] = [{"diagnostic": d, "data": data[d["data_id"]], "coverage": manifest["coverage"][d["instruction_id"]]}
                                  for d in manifest["diagnostics"] if d["code"] == "missing_part"]
    report = {
        "identity": "lossless-delivery-saved-parent-coverage-comparison-v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(RUN), "parent_directory": str(PARENT),
        "method": "Read saved JSON and source. The existing source_boundary_audit helper is read-only and invokes no model/compiler/backend. No historical run was replayed or resumed.",
        "artifacts": {"current": {f: sha(RUN / f) for f in ["selection.json", "graph/selected.json", "propagation/manifest.json", "propagation/records.json", "steps/processing/calls/a002/validation.json"]},
                      "parent": {f: sha(PARENT / f) for f in ["selection.json", "graph/selected.json", "propagation/manifest.json"]},
                      "source_audit": sha(BASE / "initial-source-correctness-audit.json"), "boundary_helper": sha(BASE / "source_boundary_audit.py")},
        "same_selected_cfg_object": True, "cfg_ir_count": len(irs),
        "coverage": {"parent": dict(Counter(parent["coverage"].values())), "current": dict(Counter(current["coverage"].values())),
                     "lost_processed": len(losses), "gained_processed": len(gains), "net_processed_change": len(gains) - len(losses),
                     "equation": "470 - 34 + 15 = 451", "all_changed_ids": changes},
        "new_validation_cutoffs": cut_groups,
        "gained_coverage": {"initialization_path": [f"ir_{n:03}" for n in range(1, 14)], "metadata_logging": ["ir_436", "ir_437"],
                            "reason": "Current generated processing models ir_001 as a read from dotenv_interface and ir_436 as a count computation plus console delivery. Parent ir_001 was validation-unmodeled and ir_436 source-unmodeled. Their now-reached successors account for all 15 gains; this reach does not prove those new summaries source-correct."},
        "persistent_source_cutoffs": ["ir_289", "ir_295"],
        "diagnostics": {"current": current["diagnostics"], "parent": parent["diagnostics"], "wrapper_evidence": wrapper_evidence,
                        "typed_operation_faults_current": 0,
                        "interpretation": "Both runs retain missing_part diagnostics at ir_457 and ir_459 for generated discriminated wrappers. Those two IR still have processed coverage; these diagnostics are not the four new stopping roots. No new typed runtime operation failure appears in the current manifest."},
        "source_boundaries": boundary,
        "source_correctness_status": source_status,
        "source_correctness_limits": [
            "Receiver dependencies are still absent at all 13 audited original remote sites in the selected annotation. Twelve are processed and one (ir_173) is blocked. Reaching the remote endpoint does not establish receiver or credential fidelity.",
            "All eight audited missing first-tuple-element projections are processed. Their prior selected-source audit remains hash-bound; processing coverage does not make the source projection correct.",
            "The Search Console API site ir_173 and save ir_177 are blocked by invalid generated unpack outputs at ir_167, not missing Skill inputs.",
            "Loop child bodies ir_311, ir_329 and ir_346 are unmodeled. A recorded aggregate-save site or loop-exit path does not establish processing of a nonempty loop body.",
            "Source boundary helper totals are remote 12/13, save 24/25 and filesystem 7/7. The unresolved remote source locator is not substituted with a fabricated record."],
        "causal_scope": {
            "observed_explanation": "All lost processed IDs are accounted for by strict local exclusion of four invalid generated processing records and their blocked tails. Gains are accounted for by two newly modeled roots and successors. These are artifact-grounded changes in modeled/retained semantics, rather than evidence that shared input encoding dropped source or graph content.",
            "encoding_vs_semantics": "Lossless input delivery does not guarantee that the model returns valid or source-correct processing. Undefined locals, unsupported nested case placement, omitted receiver dependencies and omitted response projections are generated output/modeling problems. Graph-repair prompt/capability limitations are a separate pipeline issue documented in revision-graph-audit.",
            "not_controlled_ablation": True,
            "changed_production_paths": [k for k in changed_files if k.startswith("src/")],
            "backend_caveat": "The saved implementation pins differ, including propagation runner/solver and multiple DOE modules. This is not a same-backend encoding-only ablation, and this inspection does not rule out other pipeline defects or prove overall semantic equivalence."},
    }
    (BASE / "coverage-parent-comparison.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (BASE / "coverage-parent-comparison.en.md").write_text(
        "# Saved coverage comparison with the retained parent\n\n"
        "The selected CFG is identical in both runs (489 IR). Current diagnostic propagation reports 451 processed / 6 unmodeled / 32 blocked, versus parent 470 / 4 / 15. All changes reconcile exactly: 470 - 34 lost + 15 gained = 451.\n\n"
        "The 34 losses form four exact tails: `ir_167`–`ir_179` (13), `ir_311`–`ir_317` (7), `ir_329`–`ir_335` (7), and `ir_346`–`ir_352` (7). Each first IR is newly excluded by strict processing validation. `ir_167` binds five undefined output locals; the three loop bodies place nested cases where only ordinary case segments are supported. Their successors are blocked. These four validation gaps were outside the later 27-IR processing-revision scope and remain selected after that revision failed.\n\n"
        "The 15 gains are `ir_001`–`ir_013` and `ir_436`–`ir_437`. Current processing models the dotenv interface as a read and metadata logging as count computation plus console delivery; the parent cut these paths at validation-unmodeled `ir_001` and source-unmodeled `ir_436`. Reaching the new summaries does not establish their semantic correctness. The source-backed JavaScript-undefined gaps at `ir_289` and `ir_295` remain in both runs.\n\n"
        "Both runs have the same-position `missing_part` diagnostics at `ir_457` and `ir_459`, involving unrefined generated wrappers. Those IR remain counted processed, and the diagnostics do not explain the four new cutoff tails. Current saved diagnostics contain zero typed operation faults.\n\n"
        "Source boundary record reach is remote 12/13, save 24/25 and filesystem 7/7. The Search Console request at `ir_173` and save at `ir_177` are blocked behind `ir_167`. Of the 13 previously audited receiver omissions, 12 sites are processed and one is blocked. All eight audited response-tuple projection omissions are processed. Their source-correctness audit is still bound to the selected annotation; these reach counts do not resolve the errors. Loop aggregate-save reach also does not establish nonempty-body coverage when all three child body roots are unmodeled.\n\n"
        "The observed coverage decrease is fully accounted for by different generated processing and its strict exclusions. It is not evidence that lossless encoding dropped input material. Input fidelity does not guarantee valid model output or correct source modeling. Separately, graph-repair format/capability defects are documented in `revision-graph-audit.en.md`. The two runs have different implementation pins, including propagation runner/solver and several DOE modules, so this is not a controlled encoding-only or unchanged-backend comparison. No broad absence-of-bugs claim follows.\n\n"
        "Exact changed IDs, validation messages, source statuses, wrapper records and implementation differences are in `coverage-parent-comparison.json`. This audit reads saved artifacts only; no model, Skill, backend, validation replay or historical run was executed.\n", encoding="utf-8")
    print(json.dumps({"report": str(BASE / "coverage-parent-comparison.json"), "sha256": sha(BASE / "coverage-parent-comparison.json"),
                      "coverage": {k: report["coverage"][k] for k in ["parent", "current", "lost_processed", "gained_processed"]},
                      "boundary_counts": {k: v["recorded_boundary_sites"] for k, v in boundary["categories"].items()}}))


if __name__ == "__main__":
    main()
