"""Build the review-only inventory and evidence-linked coverage matrix, offline."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from skillflow.common.paths import project_root, resolve_material_path

ROOT = project_root() / "experiments/corpus/semantics_review"
COMMIT = "49f948faa9258a0c61caceaf225e179651397431"


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def outputs(root=ROOT):
    samples = []
    for name in ("controlled_samples.json", "upstream_samples.json"):
        value = json.loads((root / name).read_text(encoding="utf-8"))
        samples.extend(value if isinstance(value, list) else value["samples"])
    order = {v: i for i, v in enumerate(("notification", "query", "fallback", "documents", "upstream"))}
    samples.sort(key=lambda s: (order[s["group"]], s["id"]))
    assert len(samples) == 30 and len({s["id"] for s in samples}) == 30
    assert sum(s["split"] == "development" for s in samples) == 22
    rows = []
    for sample in samples:
        annotation = json.loads((root / sample["annotation_path"]).read_text(encoding="utf-8"))
        tags = set()
        for fact in annotation["facts"]:
            for target in fact["coverage_tags"]:
                tags.add(target)
                rows.append({"target": target, "sample_id": sample["id"], "fact_id": fact["id"],
                             "evidence": [{k: e[k] for k in ("file", "start_line", "end_line")}
                                          for e in fact["evidence"]]})
        assert tags == set(annotation["coverage_targets"]), sample["id"]
    rows.sort(key=lambda r: (r["target"], r["sample_id"], r["fact_id"]))
    catalog = {"schema_version": 1, "phase": "semantics_review_phase_1", "upstream_commit": COMMIT,
               "review_status": "待共同复核", "split_counts": {"development": 22, "held_out": 8},
               "input_policy": "Load only one samples[].package_path; annotations/provenance are never Skill inputs.",
               "samples": samples}
    matrix = {"schema_version": 1, "rows": rows}
    csv_buffer = io.StringIO(newline="")
    writer = csv.writer(csv_buffer, lineterminator="\n")
    writer.writerow(["target", "sample_id", "fact_id", "file", "start_line", "end_line"])
    for row in rows:
        for evidence in row["evidence"]:
            writer.writerow([row["target"], row["sample_id"], row["fact_id"],
                             evidence["file"], evidence["start_line"], evidence["end_line"]])
    md = ["# 首阶段覆盖矩阵", "", "由 tools/build_catalog.py 从外置事实标注生成。每行对应覆盖目标、样例、事实及其原文证据；不代表语义判定已通过。", "",
          "| 覆盖目标 | 样例 | 事实 | 原文位置（包内路径，1 起始行号） |", "| --- | --- | --- | --- |"]
    sample_by_id = {s["id"]: s for s in samples}
    for row in rows:
        sample = sample_by_id[row["sample_id"]]
        refs = "; ".join(f"[{e['file']}:{e['start_line']}-{e['end_line']}]({sample['package_path']}/{e['file']}#L{e['start_line']})" for e in row["evidence"])
        md.append(f"| {row['target']} | {row['sample_id']} | [{row['fact_id']}]({sample['annotation_path']}) | {refs} |")
    return {"corpus.json": json_text(catalog), "coverage_matrix.json": json_text(matrix),
            "coverage_matrix.csv": csv_buffer.getvalue(), "coverage_matrix.md": "\n".join(md) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated inventory/matrix is stale")
    args = parser.parse_args()
    for name, content in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                raise SystemExit(f"Stale generated file: {path}")
        else:
            path.write_bytes(content.encode("utf-8"))
    print("Corpus inventory and coverage matrix verified." if args.check else "Corpus inventory and coverage matrix generated.")


if __name__ == "__main__":
    main()
