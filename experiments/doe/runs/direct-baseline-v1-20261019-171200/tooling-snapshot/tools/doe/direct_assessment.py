"""Identity-masked review packets and conservative paired-assessment reporting."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from tools.doe.direct_experiment import DEFAULT_RUN, ROOT, write_once, sha, effective_schedule


def packets(run: Path) -> dict:
    """Materialize visible answers only; keep arm/repeat identities outside packets."""
    mapping = {}
    grouped = defaultdict(list)
    for path in sorted((run / "trials").glob("*/decision.json")):
        trial = path.parent
        reg = json.loads((trial / "registration.json").read_text(encoding="utf-8"))
        decision = json.loads(path.read_text(encoding="utf-8"))
        answer = trial / "answer.txt"
        if not answer.exists():
            continue
        candidate = hashlib.sha256(("direct-baseline-v1/blind/" + trial.name).encode()).hexdigest()[:16]
        case = reg["case_id"]
        out = run / "blind" / case / f"{candidate}.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        data = answer.read_bytes()
        if out.exists() and out.read_bytes() != data:
            raise ValueError("A frozen blind answer changed")
        out.write_bytes(data)
        mapping[candidate] = {"trial_id": trial.name, "case_id": case,
                              "metadata": reg.get("metadata", {}),
                              "answer_sha256": sha(answer),
                              "decision_path": path.relative_to(run).as_posix()}
        grouped[case].append(candidate)
    map_path = run / "identity-map.json"
    if map_path.exists():
        old = json.loads(map_path.read_text(encoding="utf-8"))
        if any(mapping.get(key) != value for key, value in old.items()):
            raise ValueError("Existing masked identity changed or disappeared")
        if old != mapping:
            map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        write_once(map_path, mapping)
    for case, candidates in grouped.items():
        case_root = run / "cases" / case
        blind_root = run / "blind" / case
        for name in ("source_bundle.txt", "user_request.txt"):
            origin = case_root / name
            if origin.exists():
                target = blind_root / name
                if target.exists() and target.read_bytes() != origin.read_bytes():
                    raise ValueError("A masked source input changed")
                target.write_bytes(origin.read_bytes())
        refs = run / "references"
        for author in ("a", "b"):
            stage = "heldout" if case.startswith("c") else "pilot"
            origin = refs / f"{stage}-{author}.json"
            if origin.exists():
                ref = json.loads(origin.read_text(encoding="utf-8"))
                selected = [c for c in ref["cases"] if c["case_id"] == case]
                if len(selected) != 1:
                    raise ValueError("Reference must identify exactly one requested case")
                write_once(blind_root / f"reference-{author}.json", {
                    "author": ref["author"], "reference_status": ref["reference_status"],
                    "cases": selected,
                })
        # Rules are copied from the frozen trial, not a possibly edited template.
        shared_values = {(run / "trials" / mapping[c]["trial_id"] / "shared.txt").read_bytes()
                         for c in candidates if (run / "trials" / mapping[c]["trial_id"] / "shared.txt").exists()}
        if len(shared_values) > 1:
            raise ValueError("One case has different rule versions; split assessment packets by version")
        if shared_values:
            (blind_root / "shared_rules.txt").write_bytes(next(iter(shared_values)))
        # Alphabetical IDs hide original execution order. Answers can still reveal format.
        index = {
            "case_id": case, "candidate_ids": sorted(candidates),
            "requested_content": {c: (["task requirements", "source-grounded control flow", "data identities and versions", "source-to-boundary propagation", "DOE judgments and preserving proposals", "cross-layer consistency"]
                                      if mapping[c]["metadata"].get("arm") == "chain" else
                                      ["task baseline and restrictions", "all relevant boundary inventory", "supported DOE judgments and preserving proposals", "source evidence and uncertainty"])
                                  for c in sorted(candidates)},
            "identity_masking_limit": "Required content is supplied for fair scoring and can reveal the artifact kind. Trial names, repeat identities and execution order are withheld; answer structure may also reveal review status.",
        }
        index_path = run / "blind" / case / "index.json"
        if index_path.exists():
            old = json.loads(index_path.read_text(encoding="utf-8"))
            if not set(old["candidate_ids"]).issubset(index["candidate_ids"]):
                raise ValueError("A masked candidate disappeared")
            if old != index:
                index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        else:
            write_once(index_path, index)
    return {"cases": len(grouped), "candidates": len(mapping)}


def aggregate(run: Path) -> dict:
    mapping = json.loads((run / "identity-map.json").read_text(encoding="utf-8"))
    reviews = defaultdict(dict)
    for p in sorted((run / "assessments").glob("*.json")):
        record = json.loads(p.read_text(encoding="utf-8"))
        author = record["reviewer"]
        if author not in {"A", "B"}:
            raise ValueError("Assessment reviewer must be A or B")
        for candidate in record["candidates"]:
            cid = candidate["candidate_id"]
            if cid not in mapping:
                raise ValueError(f"Unknown masked candidate: {cid}")
            if author in reviews[cid]:
                raise ValueError("Duplicate assessment by one reviewer")
            if candidate["judgment"] not in {"satisfies_reference", "substantive_error", "indeterminate"}:
                raise ValueError("Unknown semantic judgment")
            if candidate["judgment"] == "satisfies_reference" and any(
                f.get("severity") in {"substantive", "disputed"} for f in candidate.get("findings", [])
            ):
                raise ValueError("A semantic pass cannot include substantive or disputed findings")
            if candidate["judgment"] == "satisfies_reference" and any(
                value in {"fail", "disputed"} for value in candidate.get("coverage", {}).values()
            ):
                raise ValueError("A semantic pass cannot include failed or disputed coverage")
            case = mapping[cid]["case_id"]
            if record.get("case_id", case) != case:
                raise ValueError("Assessment belongs to a different case")
            expected = set()
            for ref_path in (run / "blind" / case).glob("reference-*.json"):
                ref = json.loads(ref_path.read_text(encoding="utf-8"))
                expected.update((ref["author"], c["id"]) for c in ref["cases"][0]["mandatory_checks"])
            if expected:
                checks = candidate.get("check_results", [])
                actual = [(c["reference_author"], c["check_id"]) for c in checks]
                if len(actual) != len(set(actual)) or set(actual) != expected:
                    raise ValueError(f"Assessment must check every source-reference criterion exactly once: {cid}")
                if any(c["status"] not in {"pass", "fail", "disputed"} for c in checks):
                    raise ValueError("Unknown reference-check status")
                if candidate["judgment"] == "satisfies_reference" and any(c["status"] != "pass" for c in checks):
                    raise ValueError("A semantic pass cannot hide failed or disputed mandatory checks")
                if mapping[cid]["metadata"].get("arm") == "chain" and candidate["judgment"] == "satisfies_reference" and candidate.get("coverage", {}).get("cross_layer_consistency") != "pass":
                    raise ValueError("A chain pass requires an affirmative cross-layer assessment")
                if not candidate.get("reason"):
                    raise ValueError("A semantic assessment needs a reason")
            reviews[cid][author] = candidate
    counts = defaultdict(Counter)
    rows = []
    for cid, identity in sorted(mapping.items()):
        rs = reviews[cid]
        opinions = {a: r["judgment"] for a, r in rs.items()}
        if len(rs) != 2:
            final = "unassessed"
        elif set(opinions.values()) == {"satisfies_reference"}:
            final = "satisfies_reference"
        elif set(opinions.values()) == {"substantive_error"}:
            final = "substantive_error"
        else:
            final = "indeterminate_or_reviewer_disagreement"
        m = identity["metadata"]
        group = f"{m.get('stage')}/{m.get('arm')}/{'review' if m.get('review') else 'initial'}"
        counts[group][final] += 1
        rows.append({**identity, "candidate_id": cid, "judgment": final,
                     "reviewer_judgments": opinions, "reviewers": rs})
    result = {"schema_version": "direct-baseline-assessment-v1",
              "reference_status": "assistant_authored_exploratory",
              "aggregation": "Agreement only; disagreement remains indeterminate, never automatic pass or failure.",
              "groups": {k: dict(v) for k, v in counts.items()}, "candidates": rows}
    (run / "assessment-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def final_packets(run: Path) -> dict:
    """Hide the already assessed original pilot from the fresh final assessors."""
    if (run / "schedule.json").exists():
        schedule = effective_schedule(run)
        pending = [t for t in schedule["pilot"] + schedule["heldout"]
                   if not (run / "trials" / t / "decision.json").exists()]
        if pending:
            raise ValueError(f"Final assessment cohort cannot freeze before {len(pending)} remaining trial imports")
    packets(run)
    mapping = json.loads((run / "identity-map.json").read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    for cid, identity in mapping.items():
        if identity["metadata"].get("stage") != "pilot":
            grouped[identity["case_id"]].append(cid)
    index = {}
    for case, candidates in sorted(grouped.items()):
        source = run / "blind" / case
        target = run / "blind-final" / case
        target.mkdir(parents=True, exist_ok=True)
        for name in ("source_bundle.txt", "user_request.txt", "shared_rules.txt", "reference-a.json", "reference-b.json"):
            path = source / name
            if path.exists():
                dest = target / name
                if dest.exists() and dest.read_bytes() != path.read_bytes():
                    raise ValueError("Final assessment source changed")
                if not dest.exists():
                    dest.write_bytes(path.read_bytes())
        for cid in candidates:
            dest = target / f"{cid}.txt"
            data = (source / f"{cid}.txt").read_bytes()
            if dest.exists() and dest.read_bytes() != data:
                raise ValueError("Final masked candidate changed")
            if not dest.exists():
                dest.write_bytes(data)
        old_index = json.loads((source / "index.json").read_text(encoding="utf-8"))
        selected = {**old_index, "candidate_ids": sorted(candidates),
                    "requested_content": {c: old_index["requested_content"][c] for c in sorted(candidates)}}
        write_once(target / "index.json", selected)
        index[case] = sorted(candidates)
    write_once(run / "blind-final" / "cohort-index.json", {
        "excluded": "The previously assessed original pilot; its scores and answers remain unchanged.",
        "cases": index, "candidate_count": sum(map(len, index.values())),
    })
    return {"cases": len(index), "candidates": sum(map(len, index.values()))}


def report(run: Path) -> None:
    result = aggregate(run)
    lines = ["# Direct strong-model baseline: exploratory assessment", "",
             "The source-only audit and full semantic-chain tasks were evaluated independently. The historical SkillFlow outputs were not oracle inputs. No same-model SkillFlow comparison was performed.", "",
             "References and assessments are assistant-authored. Agreement between two model reviewers is not independent human validation or proof of semantic completeness. Identity masking cannot hide differences in answer structure.", "",
             "| Stage / deliverable / response | Satisfies reference | Substantive error | Indeterminate/disagreement | Unassessed |", "|---|---:|---:|---:|---:|"]
    for g, c in result["groups"].items():
        lines.append(f"| {g} | {c.get('satisfies_reference', 0)} | {c.get('substantive_error', 0)} | {c.get('indeterminate_or_reviewer_disagreement', 0)} | {c.get('unassessed', 0)} |")
    lines.extend(["", "## Candidate evidence", ""])
    for c in result["candidates"]:
        lines.extend([f"### {c['trial_id']}", "", f"Paired judgment: **{c['judgment']}**.", "",
                      f"[Original visible answer](trials/{c['trial_id']}/answer.txt) · [Call receipt](trials/{c['trial_id']}/decision.json)", ""])
        for reviewer, r in sorted(c["reviewers"].items()):
            lines.append(f"- Reviewer {reviewer}: {r['judgment']}. {r.get('reason', '')}")
        for reviewer, r in sorted(c["reviewers"].items()):
            contested = [check for check in r.get("check_results", []) if check["status"] != "pass"]
            if contested:
                lines.extend(["", f"Reviewer {reviewer}: failed or disputed mandatory checks:", ""])
                for check in contested:
                    lines.append(f"- {check['reference_author']} / {check['check_id']}: **{check['status']}**. {check.get('reason', '')}")
            for finding in r.get("findings", []):
                lines.extend(["", f"Reviewer {reviewer}: {finding.get('kind', 'finding')} ({finding.get('severity', 'unspecified')}).", "",
                              f"- Source evidence: {finding.get('source_evidence', 'Not supplied.')}",
                              f"- Answer evidence: {finding.get('answer_evidence', 'Not supplied.')}",
                              f"- Interpretation: {finding.get('reason', 'Not supplied.')}"])
        lines.append("")
    text = "\n".join(lines)
    (run / "assessment-report.md").write_text(text, encoding="utf-8")
    (run / "assessment-report.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Direct baseline assessment</title>'
        '<style>body{max-width:1100px;margin:2em auto;font:16px/1.6 system-ui}pre{white-space:pre-wrap}</style><pre>'
        + html.escape(text) + "</pre>", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("packets", "final_packets", "aggregate", "report"))
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    value = globals()[args.action](args.run_dir)
    if value is not None:
        print(json.dumps(value if args.action in {"packets", "final_packets"} else value["groups"], indent=2))
