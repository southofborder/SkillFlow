"""Authorized static 015–020 preview; no online calls, UI navigation or publish."""
import importlib.util
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "packages/skill-ir/experiments/security_profile/tools"
spec = importlib.util.spec_from_file_location("partial_preview_exporter", TOOLS / "export_full_pipeline.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
run = REPO / "packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918"
manifest = exporter.read_json(run / "manifest.json")
stage = REPO / "tmp/full-pipeline-v4-20260918/preview-015-020"
if stage.exists():
    raise ValueError("Partial preview requires a new directory; no overwrite")
rows = []
for case in manifest["cases"][14:20]:
    path = run / case["run_dir"] / "result.json"
    if not path.is_file():
        raise ValueError("Case is not terminal: " + case["case_id"])
    result = exporter.read_json(path)
    row = exporter.load_case(run, case, result, REPO / "dataset/skills", renderer=manifest["renderer"]["path"])
    row["assistant_review"] = exporter._assistant_review(
        REPO / "tmp/full-pipeline-v4-20260918/assistant-reviews", run, case, result, row)
    rows.append(row)
plan = {"schema_version": 1, "identity": "skill-ir-full-pipeline-partial-preview", "run_id": run.name,
        "run_dir": str(run), "preview_scope": "015-020-only", "formal_thirty_case_acceptance": False,
        "notice": "仅 015–020 静态集成预览；不是 30 例正式交付。", "cases": rows}
stage.mkdir(parents=True, exist_ok=False)
exporter.write_json(stage / "review-data.json", plan)
exporter.write_json(stage / "render/input.json", exporter.render_samples(plan))
for row in rows:
    exporter.atomic_write_text(stage / row["suggestions_file"], exporter.suggestions(row))
    exporter.write_json(stage / "security-profiles" / (row["basename"] + ".json"), {
        "schema_version": 1, "identity": exporter.EXPORT_IDENTITY, "provenance": row["provenance"],
        "status": row["annotation_status"], "reason": row["annotation_reason"],
        "source_binding": row["source_binding"], "profiles": row["profiles"], "unresolved": row["unresolved"],
        "validation": row["validation"], "evidence_index": row["annotation_evidence_index"],
    })
runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
command = [str(runtime / "bin/node.exe"), str(exporter.BASELINE_TOOLS / "render_review_cfg.mjs"),
           "--input", str(stage / "render/input.json"), "--output-dir", str(stage / "ir-IPP"),
           "--svg-output-dir", str(stage / "render"), "--audit", str(stage / "render/audit.json"),
           "--node-modules", str(runtime / "node_modules")]
subprocess.run(command, check=True)
for row in rows:
    exporter._png.bind_png_source(stage / row["png_file"], row["provenance"])
checks = exporter.validate_staging(plan, stage)
exporter.write_json(stage / "preview-validation.json", {
    "status": "passed", "scope": "015-020-only-preview", "formal_thirty_case_acceptance": False,
    "checks": checks, "visual_review": "pending", "published": False,
    "generators": {"exporter_sha256": exporter.sha_file(TOOLS / "export_full_pipeline.py"),
                   "renderer_sha256": exporter.sha_file(exporter.BASELINE_TOOLS / "render_review_cfg.mjs")},
    "render_command": command,
})
print(json.dumps({"status": "passed", "png_files": [str(stage / row["png_file"]) for row in rows],
                  "checks": checks}, ensure_ascii=False))
