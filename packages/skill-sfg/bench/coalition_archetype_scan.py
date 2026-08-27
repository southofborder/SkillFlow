#!/usr/bin/env python3
"""
Coalition archetype scan (pure static, no LLM / no API key).

Purpose: the paper's aggregation-exposure selling point needs the REAL
distribution of multi-label coalitions converging on one egress sink,
bucketed by *harm archetype* -- not just the Sweeney demographic QI
(which the prior scan proved is 0-hit in this corpus).

Three archetypes (superadditive: set sensitivity > max of parts):
  (a) RE_IDENTIFICATION  -- demographic quasi-identifier (Sweeney): DOB/age +
                            gender + geo. Uniquely re-identifies an individual.
  (b) PERSONAL_LINKAGE   -- direct identifier + other personal attributes
                            (comm/record/location/health/financial) => rich
                            profile of a known person. Personal-family only.
  (c) CAPABILITY_AGG     -- operational/technical secrets (credentials + DB +
                            file + security/network) => an attack toolkit.
                            Operational-family only.
  (d) MIXED              -- spans both personal and operational families.

Validation checksums from the prior scan (must reproduce):
  - Sweeney demographic QI exact hits = 0
  - multi-flow sinks ~4981 ; >=2 distinct high/crit categories ~3174 ; egress ~2152
  - dominant egress coalitions: {database_record,file_content}~901,
    {credentials,database_record,file_content}~339, {communication,file_content}~265
"""
import json
import glob
import os
from collections import Counter, defaultdict

FCG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                       "results", "zips", "fcg", "skills")

# ---- category families -------------------------------------------------
PERSONAL = {
    "pii", "special_category", "health", "biometric",
    "communication", "financial", "personal_record", "location",
}
OPERATIONAL = {
    "credentials", "database_record", "file_content", "security_data",
    "network_data", "enterprise", "device_data", "browser_data", "ai_context",
}
# neutral / non-sensitive carriers we ignore for the >=2-distinct test
NEUTRAL = {"generic_data", "unknown", "user_prompt"}

HIGH_CRIT = {"high", "critical"}

# demographic quasi-identifier slots (Sweeney) by subtype
QI_GENDER = {"gender", "sex"}
QI_AGE = {"birthdate", "dob", "date_of_birth", "age", "birth_year"}
QI_GEO = {"address", "zip", "zipcode", "postal_code", "geo",
          "coarse_location", "ip_location", "postcode", "region"}
QI_RACE = {"racial_ethnic_origin", "ethnicity", "race"}

DIRECT_ID_SUBTYPES = {"email", "phone", "name", "full_name", "username",
                      "ssn", "national_id", "passport", "user_id", "account_id"}


def load_skills():
    files = sorted(glob.glob(os.path.join(FCG_DIR, "*.json")))
    # dedup by 5-digit skill id, keep first
    seen, keep = set(), []
    for f in files:
        base = os.path.basename(f)
        # skill_0001-00001_... -> the 00001 corpus id
        parts = base.split("-")
        cid = parts[1][:5] if len(parts) > 1 else base
        if cid in seen:
            continue
        seen.add(cid)
        keep.append(f)
    return keep


def is_egress(b):
    """Boundary crosses out of the trust domain (true external exposure)."""
    ds = b.get("data_surface")
    rs = b.get("receiver_scope")
    if rs in ("model_provider", "external_network", "third_party", "external_service"):
        return True
    if ds in ("llm_context", "network", "external_network"):
        return True
    return False


def egress_kind(b):
    rs = b.get("receiver_scope")
    ds = b.get("data_surface")
    if rs == "model_provider" or ds == "llm_context":
        return "llm"
    return "network"


def qi_slots(subtypes):
    s = set()
    if subtypes & QI_GENDER:
        s.add("GENDER")
    if subtypes & QI_AGE:
        s.add("AGE")
    if subtypes & QI_GEO:
        s.add("GEO")
    if subtypes & QI_RACE:
        s.add("RACE")
    return s


def classify(cats, subtypes):
    """cats: set of sensitive categories present; subtypes: set of subtypes."""
    slots = qi_slots(subtypes)
    # Sweeney re-identification: >=2 demographic QI slots
    if len(slots) >= 2:
        return "RE_IDENTIFICATION"
    p = cats & PERSONAL
    o = cats & OPERATIONAL
    if p and o:
        return "MIXED"
    if p and not o:
        return "PERSONAL_LINKAGE"
    if o and not p:
        return "CAPABILITY_AGG"
    return "OTHER"


def main():
    files = load_skills()
    multi_flow_sinks = 0
    multi_cat_sinks = 0
    egress_coalitions = 0
    sweeney_exact = 0
    arch_counts = Counter()
    arch_by_egress = defaultdict(Counter)  # archetype -> egress_kind counts
    coalition_sig = Counter()              # frozenset(cats) -> count (egress only)
    per_skill_egress = Counter()

    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        sp = d.get("security_profile", {})
        ld = sp.get("label_dictionary", {})
        lf_list = sp.get("label_flows", [])
        # map label_flow_id -> label_id
        lf2label = {}
        for lf in lf_list:
            lf2label[lf.get("label_flow_id")] = lf.get("label_id")
        skill_id = os.path.basename(f)

        for obs in sp.get("observations", []):
            lfids = obs.get("label_flow_ids", []) or []
            if len(lfids) < 2:
                continue
            multi_flow_sinks += 1
            # resolve to (category, subtype, sensitivity)
            cats_hc = set()   # high/crit categories only (for the >=2 test & checksums)
            cats_all = set()
            subs = set()
            for lfid in lfids:
                labid = lf2label.get(lfid)
                if not labid:
                    continue
                meta = ld.get(labid)
                if not meta:
                    continue
                cat = meta.get("category")
                sub = meta.get("subtype")
                sens = meta.get("sensitivity")
                if cat and cat not in NEUTRAL:
                    cats_all.add(cat)
                    if sub:
                        subs.add(sub)
                    if sens in HIGH_CRIT:
                        cats_hc.add(cat)
            if len(cats_hc) >= 2:
                multi_cat_sinks += 1
                if len(qi_slots(subs)) >= 3:
                    sweeney_exact += 1
                b = obs.get("boundary", {})
                if is_egress(b):
                    egress_coalitions += 1
                    arch = classify(cats_hc, subs)
                    arch_counts[arch] += 1
                    arch_by_egress[arch][egress_kind(b)] += 1
                    coalition_sig[frozenset(cats_hc)] += 1
                    per_skill_egress[skill_id] += 1

    print("=== CHECKSUMS (compare to prior scan) ===")
    print(f"skills processed          : {len(files)}")
    print(f"multi-flow sinks (>=2 lf) : {multi_flow_sinks}   (prior ~4981)")
    print(f">=2 distinct high/crit cat: {multi_cat_sinks}   (prior ~3174)")
    print(f"  of those at egress      : {egress_coalitions}   (prior ~2152)")
    print(f"Sweeney demographic QI hit: {sweeney_exact}   (prior 0)")
    print()
    print("=== ARCHETYPE DISTRIBUTION (egress coalitions) ===")
    tot = sum(arch_counts.values()) or 1
    for a, n in arch_counts.most_common():
        by = dict(arch_by_egress[a])
        print(f"  {a:20s} {n:5d}  ({100*n/tot:5.1f}%)   egress={by}")
    print()
    print("=== TOP EGRESS COALITION SIGNATURES ===")
    for cs, n in coalition_sig.most_common(15):
        print(f"  {n:5d}  {{{', '.join(sorted(cs))}}}")
    print()
    print(f"skills with >=1 egress coalition: {len(per_skill_egress)} / {len(files)}")


if __name__ == "__main__":
    main()
