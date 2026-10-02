"""Bind actually viewed preview PNGs to the final staged delivery, offline only."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "staging"
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
data = json.loads((STAGE / "review-data.json").read_text(encoding="utf-8"))
assert len(data["cases"]) == 30
reviews = {}
for path in sorted(ROOT.glob("visual-review-*.json")):
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["run_id"] == data["run_id"], path
    for item in document["cases"]:
        key = item["case_id"]
        assert key not in reviews, key
        preview = Path(item["png"])
        assert digest(preview) == item["sha256"], preview
        reviews[key] = (path, item)
assert set(reviews) == {x["case_id"] for x in data["cases"]}
rechecks = {}
for name in ("root", "020-024", "029-030"):
    path = ROOT / ("final-visual-recheck-" + name + ".json")
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["run_id"] == data["run_id"]
    for item in document["cases"]:
        assert item["case_id"] not in rechecks
        assert item["reviewer"] == "assistant" and item["human_confirmed"] is False
        assert item["outcome"] == "no_visible_layout_defect"
        assert "view_image" in item["method"]
        assert item["detail_review"]
        for detail in item["detail_review"]:
            assert digest(Path(detail["png"])) == detail["sha256"]
        rechecks[item["case_id"]] = (path, item)
bindings = []
for case in data["cases"]:
    record, item = reviews[case["case_id"]]
    target = STAGE / case["png_file"]
    sha = digest(target)
    same_bytes = sha == item["sha256"]
    same_pixels = same_bytes
    box = None
    if not same_bytes:
        with Image.open(item["png"]) as left, Image.open(target) as right:
            assert left.size == right.size, case["case_id"]
            diff = ImageChops.difference(left.convert("RGBA"), right.convert("RGBA"))
            boxes = [band.getbbox() for band in diff.split()]
            boxes = [value for value in boxes if value is not None]
            box = (min(x[0] for x in boxes), min(x[1] for x in boxes),
                   max(x[2] for x in boxes), max(x[3] for x in boxes)) if boxes else None
            same_pixels = not boxes
    if item.get("graph_sha256"):
        assert item["graph_sha256"] == case["graph_sha256"], case["case_id"]
    if "selected_revision" in item:
        assert item["selected_revision"] == case["selected_revision"], case["case_id"]
    recheck = None
    if case["case_id"] in rechecks:
        path, reviewed = rechecks[case["case_id"]]
        assert reviewed["png_sha256"] == sha
        recheck = {"record": str(path), "sha256": digest(path), "outcome": reviewed["outcome"]}
    bindings.append({"case_id": case["case_id"], "png_file": case["png_file"],
                     "png_sha256": sha, "graph_sha256": case["graph_sha256"],
                     "selected_revision": case["selected_revision"],
                     "review_record": str(record), "review_record_sha256": digest(record),
                     "preview_png_sha256": item["sha256"],
                     "byte_identical_to_viewed_png": same_bytes,
                     "pixel_identical_to_viewed_png": same_pixels,
                     "pixel_difference_bbox": box, "final_png_recheck": recheck,
                     "visual_check_passed": same_pixels or recheck is not None})
output = {"run_id": data["run_id"], "cases": bindings,
          "status": "passed" if all(x["visual_check_passed"] for x in bindings) else "requires_visual_recheck",
          "notice": "助手逐张静态视觉检查的绑定；不是语义正确性证明，也不是用户确认。"}
(ROOT / "final-visual-binding.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": output["status"], "cases": len(bindings),
                  "byte_identical": sum(x["byte_identical_to_viewed_png"] for x in bindings),
                  "pixel_identical": sum(x["pixel_identical_to_viewed_png"] for x in bindings),
                  "rechecked": sum(x["final_png_recheck"] is not None for x in bindings),
                  "recheck": [x["case_id"] for x in bindings if not x["visual_check_passed"]]}, ensure_ascii=False))
