import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
stage = root / "preview-021"
data = json.loads((stage / "review-data.json").read_text(encoding="utf-8"))["cases"][0]
validation = json.loads((stage / "preview-validation.json").read_text(encoding="utf-8"))["checks"][0]
audit = json.loads((stage / "render/audit.json").read_text(encoding="utf-8"))["samples"][0]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
row = {"case_id": "021", "png": str(stage / data["png_file"]), "sha256": digest(stage / data["png_file"]),
       "svg": str(stage / data["svg_file"]), "svg_sha256": digest(stage / data["svg_file"]),
       "width": validation["width"], "height": validation["height"],
       "reviewer": "assistant", "human_confirmed": False,
       "method": "view_image: full static PNG and original-resolution identity/conversion-package detail crops",
       "checks": ["实际查看整张图及两张原分辨率细节，021/D03/r1、新运行名称、状态、图与源文摘要清晰。",
                  "中文约束显示正常，长操作名与约束在节点边界内换行，转换与打包参数、结果标识可读。",
                  "7块、6条向下边、14IR和末尾return可见；null条件如实显示，未见节点裁切或箭头遮挡。",
                  "完整脚本metadata未塞入PNG；源文件和图metadata已另行逐项核对，PNG不是脚本全文审计材料。"],
       "detail_review": [{"png": str(stage / name), "sha256": digest(stage / name)}
                         for name in ("detail-identity.png", "detail-convert-package.png")],
       "outcome": "no_visible_layout_defect", "graph_sha256": data["graph_sha256"],
       "selected_revision": data["selected_revision"], "feedback_status": data["feedback_status"],
       "annotation_status": data["annotation_status"],
       "renderer_checks": {key: audit.get(key) for key in ("counts_checks_passed", "identity_checks_passed", "text_checks_passed", "bounds_checks_passed", "collisions")},
       "notice": "助手静态视觉复核，非人工确认，不证明语义等价或标注正确；仅最终同字节PNG可复用。"}
(root / "visual-review-021.json").write_text(json.dumps({"run_id": data["run_id"], "reviewed_count": 1, "cases": [row]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
