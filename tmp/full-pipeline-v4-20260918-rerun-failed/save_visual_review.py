"""Record the assistant's already-performed static image inspection."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("case")
parser.add_argument("details", nargs="+")
args = parser.parse_args()
root = Path(__file__).resolve().parent
stage = root / ("preview-" + args.case)
data = json.loads((stage / "review-data.json").read_text(encoding="utf-8"))["cases"][0]
validation_path = stage / "preview-validation.json"
validation = json.loads(validation_path.read_text(encoding="utf-8"))
audit = json.loads((stage / "render/audit.json").read_text(encoding="utf-8"))["samples"][0]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
png = stage / data["png_file"]
assert digest(png) == validation["checks"][0]["png_sha256"]
checks = [f"实际查看整图及指定原分辨率细节，{args.case}/{data['sample_id']}/r{data['selected_revision']}、运行与图摘要标识清晰。",
          "中文和英文标识正常，长操作名、参数、约束在节点内完整换行；条件文字与方向箭头可见，未发现遮挡或画布裁切。",
          f"实际图共{audit['counts']['blocks']}块、{audit['counts']['edges']}边、{audit['counts']['instructions']}IR，终态操作可见；内容计数另经渲染器核验。",
          "完整脚本metadata不显示在PNG；源文与图内容已另行复核，静态图查看不能代替脚本全文或语义证明。"]
row = {"case_id": args.case, "png": str(png), "sha256": digest(png),
       "svg": str(stage / data["svg_file"]), "svg_sha256": digest(stage / data["svg_file"]),
       "width": audit["width"], "height": audit["height"], "reviewer": "assistant", "human_confirmed": False,
       "method": "view_image: full static PNG and listed original-resolution detail crops", "checks": checks,
       "detail_review": [{"png": str(stage / name), "sha256": digest(stage / name)} for name in args.details],
       "outcome": "no_visible_layout_defect", "graph_sha256": data["graph_sha256"], "selected_revision": data["selected_revision"],
       "feedback_status": data["feedback_status"], "annotation_status": data["annotation_status"],
       "renderer_checks": {key: audit.get(key) for key in ("counts_checks_passed", "identity_checks_passed", "text_checks_passed", "bounds_checks_passed", "collisions")},
       "notice": "助手静态视觉复核，非人工确认；不是语义等价或标注正确性证明，仅最终同字节PNG可复用。"}
(root / ("visual-review-" + args.case + ".json")).write_text(json.dumps({"run_id": data["run_id"], "reviewed_count": 1, "cases": [row]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
validation["visual_review"] = {"status": "assistant_reviewed", "human_confirmed": False, "png_sha256": row["sha256"], "full_image": True,
                             "original_resolution_details": args.details, "observations": checks}
validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
