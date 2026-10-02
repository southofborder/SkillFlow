"""Terminal-case validation and static CFG preview; never invokes model clients."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "packages/skill-ir/experiments/security_profile/tools"
spec = importlib.util.spec_from_file_location("review_exporter", TOOLS / "export_full_pipeline.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
parser = argparse.ArgumentParser()
parser.add_argument("case")
parser.add_argument("--render", action="store_true")
args = parser.parse_args()
run = REPO / "packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed"
manifest = exporter.read_json(run / "manifest.json")
case = next(case for case in manifest["cases"] if case["case_id"] == args.case)
result_file = run / case["run_dir"] / "result.json"
if not result_file.is_file():
    raise ValueError("Case not terminal")
result = exporter.read_json(result_file)
row = exporter.load_case(run, case, result, REPO / "dataset/skills", renderer=manifest["renderer"]["path"])
plan = {"schema_version": 1, "identity": "skill-ir-full-pipeline-partial-preview", "run_id": run.name,
        "run_dir": str(run), "preview_scope": args.case + "-only", "formal_thirty_case_acceptance": False,
        "notice": "终态案例静态预览，不是正式三十例验收。", "cases": [row]}
stage = Path(__file__).resolve().parent / ("preview-" + args.case)
stage.mkdir(parents=True, exist_ok=True)
exporter.write_json(stage / "review-data.json", plan)
exporter.write_json(stage / "render/input.json", exporter.render_samples(plan))
exporter.atomic_write_text(stage / row["suggestions_file"], exporter.suggestions(row))
exporter.write_json(stage / "security-profiles" / (row["basename"] + ".json"), {
    "schema_version": 1, "identity": exporter.EXPORT_IDENTITY, "provenance": row["provenance"],
    "status": row["annotation_status"], "reason": row["annotation_reason"],
    "source_binding": row["source_binding"], "profiles": row["profiles"], "unresolved": row["unresolved"],
    "validation": row["validation"], "evidence_index": row["annotation_evidence_index"]})
for file in row["source"]["files"]:
    print("SOURCE", json.dumps(file, ensure_ascii=False))
print("SELECTION", json.dumps(row["provenance"], ensure_ascii=False))
print("GRAPH", json.dumps(row["cfg"], ensure_ascii=False))
for round_ in result["feedback"]["rounds"]:
    print("ROUND", round_["revision"], round_["status"])
    audit = round_.get("audit")
    print("AUDIT", json.dumps(audit, ensure_ascii=False))
print("PROFILES", json.dumps(row["profiles"], ensure_ascii=False))
print("UNRESOLVED", json.dumps(row["unresolved"], ensure_ascii=False))
if args.render:
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
    command = [str(runtime / "bin/node.exe"), str(exporter.BASELINE_TOOLS / "render_review_cfg.mjs"),
               "--input", str(stage / "render/input.json"), "--output-dir", str(stage / "ir-IPP"),
               "--svg-output-dir", str(stage / "render"), "--audit", str(stage / "render/audit.json"),
               "--node-modules", str(runtime / "node_modules")]
    subprocess.run(command, check=True)
    exporter._png.bind_png_source(stage / row["png_file"], row["provenance"])
    checks = exporter.validate_staging(plan, stage)
    exporter.write_json(stage / "preview-validation.json", {"status": "passed", "formal_thirty_case_acceptance": False,
        "checks": checks, "visual_review": "pending", "render_command": command,
        "generators": {"renderer_sha256": exporter.sha_file(exporter.BASELINE_TOOLS / "render_review_cfg.mjs"),
                       "exporter_sha256": exporter.sha_file(TOOLS / "export_full_pipeline.py")}})
    print("PNG", stage / row["png_file"])
