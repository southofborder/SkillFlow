#!/usr/bin/env python3
"""Structural scan: do multiple sensitive label-flows converge on a single sink
whose label set forms a Sweeney-style quasi-identifier (QI) combination?

Pure static scan over existing v6 FCG outputs. No LLM / no API key spend.

For each observation (a sink node), we resolve its label_flow_ids -> label_id ->
label_dictionary -> (category.subtype). The SET of distinct labels converging on
that one sink is the "coalition" at that boundary. We then test that set against
fixed QI combinations drawn from Sweeney (1997/2000) and NIST SP 800-122.
"""
import json, glob, sys
from collections import defaultdict

# --- Sweeney / demographic QI combinations, expressed over ontology label ids.
# A QI "slot" is satisfied if ANY of its member labels is present in the sink's set.
GEO = {"pii.address", "location.postal_address", "location.address", "location.city",
       "location.precise_geo", "location.geo", "location.coarse_location", "location.ip_location"}
DOB = {"pii.birthdate"}
COARSE_AGE = {"pii.age"}
GENDER = {"pii.gender"}
NAME = {"pii.name"}
RACE = {"special_category.racial_ethnic_origin"}

QI_SETS = [
    # Sweeney's classic re-identification triple (~87% of US population unique)
    ("sweeney_classic", [DOB, GENDER, GEO]),
    # Sweeney's relaxed triple with coarse age instead of full DOB (~53% unique)
    ("sweeney_coarse", [COARSE_AGE, GENDER, GEO]),
    # Name + geography (directory-style re-identification)
    ("name_geo", [NAME, GEO]),
    # Race + geography + DOB (heightened harm)
    ("race_geo_dob", [RACE, GEO, DOB]),
]


def load_labels(sp):
    ld = sp.get("label_dictionary", {})
    lf_by_id = {lf["label_flow_id"]: lf for lf in sp.get("label_flows", [])}
    def resolve(lf_id):
        lf = lf_by_id.get(lf_id)
        if not lf:
            return None
        lab = ld.get(lf.get("label_id"))
        return lab
    return resolve


def slot_satisfied(present, slot):
    return len(present & slot) > 0


def scan_file(path):
    d = json.load(open(path, encoding="utf-8"))
    sp = d.get("security_profile", {})
    resolve = load_labels(sp)
    hits = []
    near = []
    for obs in sp.get("observations", []):
        # only sinks that actually cross a boundary matter for exposure
        labels_here = set()
        for lf_id in obs.get("label_flow_ids", []) or []:
            lab = resolve(lf_id)
            if lab:
                labels_here.add(lab.get("label", ""))
        if len(labels_here) < 2:
            continue
        for qi_name, slots in QI_SETS:
            sat = [slot_satisfied(labels_here, s) for s in slots]
            n_sat = sum(sat)
            if n_sat == len(slots):
                hits.append((qi_name, obs.get("node_name", ""), sorted(labels_here)))
            elif n_sat == len(slots) - 1 and len(slots) >= 3:
                near.append((qi_name, obs.get("node_name", ""), sorted(labels_here)))
    return hits, near


def main():
    files = sorted(glob.glob("results/zips/**/*-sfg.json", recursive=True))
    # dedup by skill id (nnnnn) keeping the largest obs count
    by_id = {}
    for f in files:
        base = f.replace("\\", "/").split("/")[-1]
        sid = base.split("-")[0]
        by_id.setdefault(sid, []).append(f)
    chosen = [sorted(v)[0] for v in by_id.values()]
    print(f"unique skills: {len(chosen)} (from {len(files)} files)\n")

    total_hits = 0
    total_near = 0
    skills_with_hit = 0
    by_qi = defaultdict(int)
    for f in sorted(chosen):
        try:
            hits, near = scan_file(f)
        except Exception as e:
            print(f"  ERR {f}: {e}")
            continue
        total_hits += len(hits)
        total_near += len(near)
        if hits:
            skills_with_hit += 1
            name = f.replace("\\", "/").split("/")[-1][:55]
            print(f"[HIT] {name}")
            for qi_name, node, labs in hits:
                by_qi[qi_name] += 1
                print(f"       {qi_name} @ {node}")
                print(f"         labels: {labs}")
    print(f"\n=== SUMMARY ===")
    print(f"skills with >=1 exact QI hit : {skills_with_hit}/{len(chosen)}")
    print(f"total exact QI hits          : {total_hits}")
    print(f"total near-miss (1 slot short): {total_near}")
    print(f"by QI set: {dict(by_qi)}")


if __name__ == "__main__":
    main()
