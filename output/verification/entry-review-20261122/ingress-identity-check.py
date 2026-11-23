"""Recompute the 211742 ingress-identity comparison from frozen JSON; no run or replay.

Run with the project's Python: python -B ingress-identity-check.py
Use --record only to create the single, new JSON receipt.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
from skillflow.document_guided.sensitivity_entries import entry_catalogue
from skillflow.doe.sensitivity_engine import equivalent_entry_declarations

BASE = HERE.parent / "online-ga4-lossless-delivery-20261119/independent-candidate-scale-forensics.json"
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
OUT = HERE / "ingress-identity-check.json"


def check():
    pins = {}

    def read(path, expected=None):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if expected and digest != expected:
            raise ValueError("Historical artifact differs: " + str(path))
        pins[path.relative_to(ROOT).as_posix()] = digest
        return json.loads(raw)

    audit = read(BASE)
    if PureWindowsPath(audit["run"]).name != RUN.name:
        raise ValueError("Forensic receipt refers to another donor")
    hashes = {p.relative_to(PureWindowsPath(audit["run"])).as_posix(): r["sha256"]
              for r in audit["inputs"] if (p := PureWindowsPath(r["path"])).is_relative_to(PureWindowsPath(audit["run"]))}
    def saved(name):
        return read(RUN / name, hashes[name])

    sel = read(RUN / "selection.json")
    cfg = read(RUN / sel["cfg"]["path"], sel["cfg"]["sha256"])["cfg"]
    proc = saved("steps/processing/value.json")
    old = saved("steps/sensitivity/value.json")["declarations"]
    compiled = saved("annotation/audit/compiled-response.json")["ir_semantics"]
    records = saved("propagation/records.json")
    coverage = read(RUN / "propagation/manifest.json")["coverage"]
    registry = {row["id"]:row for row in saved("propagation/data.json")}
    catalogue = entry_catalogue(cfg, proc)
    [(entry_id, entry)] = [(k,e) for k,e in catalogue.items() if e["source"] == "live_environment"]
    nodes, scenarios, member_rows, sites = {}, {}, [], set()
    for i, seed in enumerate(audit["creation_seed_records"]):
        ir, ei, oi = (seed[k] for k in ("instruction_id","event_index","op_index"))
        d = seed["declaration"]
        spec = compiled[ir]["events"][ei]["atomic_ops"][oi]
        if (d not in compiled[ir]["sensitivity"] or spec["op"] != "read" or spec["location"] != entry["source"]
                or spec["output"] != d["value"]["name"]):
            raise ValueError("Legacy declaration/compiled read mismatch: " + ir)
        [lexical] = [r for r in old if r["instruction_id"] == ir and r["path"] == d["path"] and r["label"] == d["label"]
                     and spec["output"].endswith("__" + r["value"]["name"])]
        [site] = [s for s in entry["accesses"] if s["instruction_id"] == ir and s["value"] == lexical["value"]
                  and s.get("case_path") == lexical.get("case_path")]
        a = records.get(ir, {}).get("events", [])
        data = sorted(a[ei]["atomic_ops"][oi]["outputs"][0]) if ei < len(a) else []
        if data != seed["data_ids"] or bool(data) != (coverage.get(ir) == "processed"):
            raise ValueError("Historical coverage or data differs at " + ir)
        identity = f"/creation_seed_records/{i}"
        sites.add(site["access_id"])
        member_rows.append({"record":identity, "ir":ir, "event":ei,"op":oi, "field":d["path"], "access_id":site["access_id"],
                            "context":site["source_entry_context"], "data":data,"coverage":coverage[ir]})
        if data:
            nodes[ir,d["value"]["name"]] = {"data_ids":data}
            scenarios[identity] = {"instruction_id":ir, "scope_path":[], "declaration":{**d, "source_entry_id":entry_id,
                "source_entry_origin":"environment", "source_entry_applicability":"source_field",
                "source_entry_location":entry["location"], "source_entry_context":site["source_entry_context"],
                "source_access_id":site["access_id"]}}
    # This adapter exposes ONLY the saved recorded versions at already bound reads.
    engine = SimpleNamespace(index=SimpleNamespace(data=registry,coverage=coverage), nodes=nodes,
                             resolve=lambda ref, ir: [(ir,ref["name"])])
    intrinsic = equivalent_entry_declarations(engine,scenarios)
    restricted = deepcopy(scenarios)
    for row in restricted.values():
        row["declaration"]["source_entry_applicability"] = "access"
    access = equivalent_entry_declarations(engine,restricted)
    fields = {k: len(v) for k,v in intrinsic.items()}
    roots = sorted({d for r in member_rows for d in r["data"]})
    summary = {"catalogue_entries":len(catalogue),"catalogue_accesses":sum(len(e["accesses"]) for e in catalogue.values()),
               "environment_entries":1,"environment_accesses":len(entry["accesses"]),"creation_sites":len(sites),
               "legacy_field_declarations":len(member_rows),"reached_field_declarations":len(scenarios),
               "reached_distinct_contexts":len({r["context"] for r in member_rows if r["data"]}),
               "intrinsic_groups_by_field":{scenarios[k]["declaration"]["path"][0]:n for k,n in fields.items()},
               "access_groups":len(access),"access_specific_declarations":len(restricted)}
    if (sorted(fields.values()) != [50,50] or access or len(roots) != 1
            or Counter(r["coverage"] for r in member_rows) != {"processed":100, "blocked":2}):
        raise ValueError("Observed equivalence groups or frozen coverage differ from the expected comparison")
    return {"identity":"ga4-offline-ingress-identity-check-v1","run":RUN.name,"input_sha256":pins,"summary":summary,
            "condition":"Both counterfactual modes reuse the exact same frozen Data, evidence, field, label, property and physical site. Source_field tests an assumed intrinsic classification. Historical citations alone do not verify that assumption. Access tests occurrence-specific classification at each of the same reached sites.",
            "entry":{"id":entry_id,"location":entry["location"],"source":entry["source"]},
            "shared_root_origins":{r:registry[r]["origin"] for r in roots},"legacy_members":member_rows,
            "intrinsic_group_members":intrinsic,"access_group_members":access,
            "reproduce":"python -B output/verification/entry-review-20261122/ingress-identity-check.py"}


if __name__ == "__main__":
    value = check()
    if sys.argv[1:] == ["--record"]:
        with OUT.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
    elif sys.argv[1:] or json.loads(OUT.read_bytes()) != value:
        raise SystemExit("Unsupported arguments or receipt differs from the fresh read-only computation")
    print(json.dumps(value["summary"], sort_keys=True))
