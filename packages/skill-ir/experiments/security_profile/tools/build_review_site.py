"""Build a self-contained, offline review page from an exported run snapshot.

This tool only reads an export; it neither analyzes a Skill nor calls a model.
All source text remains text. SVG has a narrow element/attribute allowlist before
it is embedded, and interaction uses actual graph identifiers supplied by SVG.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
if str(PACKAGE_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT / "src"))

from skill_ir.recording import canonical_sha256
from skill_ir.security_profile.models import AnnotationPayload, AnnotationResponse, SCHEMA_VERSION


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ALLOWED_TAGS = frozenset({
    "svg", "g", "defs", "marker", "path", "polygon", "polyline", "rect",
    "circle", "ellipse", "line", "text", "tspan", "title", "desc", "clipPath",
})
ALLOWED_ATTRIBUTES = frozenset({
    "id", "class", "d", "width", "height", "x", "y", "x1", "y1", "x2", "y2",
    "cx", "cy", "r", "rx", "ry", "points", "viewBox", "preserveAspectRatio",
    "transform", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
    "stroke-miterlimit", "stroke-dasharray", "fill-opacity", "stroke-opacity", "opacity",
    "font-family", "font-size", "font-weight", "font-style", "text-anchor",
    "dominant-baseline", "dy", "dx", "markerWidth", "markerHeight", "markerUnits",
    "orient", "refX", "refY", "marker-start", "marker-end", "marker-mid", "clip-path",
    "data-block-id", "data-ir-id", "data-card", "data-card-bound", "data-item",
    "data-kind", "data-edge", "data-source", "data-target", "data-edge-line", "data-arrow",
    "{http://www.w3.org/XML/1998/namespace}space",
})
TEMPLATE = Path(__file__).with_name("review_site.html")


def _local_name(tag: str) -> str:
    return tag.split("}")[-1]


def sanitize_svg(value: str, cfg: dict | None = None) -> str:
    """Retain drawing content while rejecting code, links, foreign HTML and CSS."""
    if "<!DOCTYPE" in value.upper() or "<!ENTITY" in value.upper():
        raise ValueError("Review SVG must not declare external entities or a document type")
    root = ET.fromstring(value)
    if _local_name(root.tag) != "svg" or root.tag not in {"svg", f"{{{SVG_NS}}}svg"}:
        raise ValueError("Review image must be SVG")

    def clean(element):
        for attribute, content in list(element.attrib.items()):
            if attribute not in ALLOWED_ATTRIBUTES:
                del element.attrib[attribute]
                continue
            if "url(" in content.lower() and not re.fullmatch(r"url\(#[\w.:-]+\)", content):
                del element.attrib[attribute]
        for child in list(element):
            if _local_name(child.tag) not in ALLOWED_TAGS or (
                child.tag.startswith("{") and not child.tag.startswith("{" + SVG_NS + "}")
            ):
                element.remove(child)
            else:
                clean(child)

    clean(root)
    if cfg is not None:
        blocks = cfg.get("blocks", {})
        ir_to_block = {
            instruction["id"]: block_id
            for block_id, block in blocks.items()
            for instruction in block.get("instructions", [])
        }
        seen = set()
        for element in root.iter():
            ir_id, block_id = element.get("data-ir-id"), element.get("data-block-id")
            if block_id is not None and block_id not in blocks:
                raise ValueError(f"SVG refers to an unknown block: {block_id}")
            if ir_id is not None:
                if ir_id not in ir_to_block:
                    raise ValueError(f"SVG refers to an unknown operation: {ir_id}")
                if block_id is not None and ir_to_block[ir_id] != block_id:
                    raise ValueError(f"SVG operation belongs to a different block: {ir_id}")
                seen.add(ir_id)
        if seen != set(ir_to_block):
            raise ValueError("SVG lacks clickable operation IDs: " + ", ".join(sorted(set(ir_to_block) - seen)))
    return ET.tostring(root, encoding="unicode")


def _contained_file(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Review asset escapes its export directory")
    return candidate


def _safe_local_link(value: str | None) -> str | None:
    if not value:
        return None
    path = value.replace("\\", "/")
    if path.startswith("/") or ":" in path or ".." in path.split("/"):
        raise ValueError("Review link must be relative to the local export")
    return path


def build_review_site(data_path: Path, output_path: Path, *, assets_root: Path | None = None) -> Path:
    data_path, output_path = Path(data_path).resolve(), Path(output_path).resolve()
    root = Path(assets_root).resolve() if assets_root is not None else data_path.parent
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    if (payload.get("schema_version") != 5 or payload.get("profile_schema_version") != SCHEMA_VERSION
            or payload.get("identity") != "skill-ir-full-pipeline-delivery-v5"
            or not isinstance(payload.get("cases"), list)):
        raise ValueError("Unsupported review export version")
    material = deepcopy(payload)
    seen = set()
    for case in material["cases"]:
        if "unresolved" in case or case.get("annotation_status") == "incomplete" or case.get("feedback_status") == "unresolved":
            raise ValueError("Unsupported legacy review fields or statuses")
        identifier = case.get("case_id")
        if not isinstance(identifier, str) or not re.fullmatch(r"\d{3}", identifier) or identifier in seen:
            raise ValueError("Review cases require unique three-digit identifiers")
        seen.add(identifier)
        # Validate the actual embedded contract too: a new manifest cannot turn
        # old actor profiles into operator profiles. Full quote verification is
        # performed by the exporter; this page never reinterprets old records.
        business = {key: case[key] for key in ("profiles", "locations", "transfer_specs", "sink_boundaries")}
        AnnotationPayload.model_validate(business)
        evidence_audit = case.get("annotation_audit")
        if evidence_audit is not None:
            audit_path = _contained_file(root, evidence_audit["file"])
            table = json.loads(audit_path.read_text(encoding="utf-8"))
            if canonical_sha256(table) != evidence_audit.get("sha256"):
                raise ValueError("Review location evidence audit digest mismatch")
            AnnotationResponse.model_validate({**business, "outcome": "completed", "location_evidences": table})
            evidence_audit["file"] = _safe_local_link(evidence_audit["file"])
            # This is an HTML-only audit view, never written back into the
            # four-field business payload or the exported location records.
            evidence_audit["evidences"] = table
        elif case.get("locations"):
            raise ValueError("Review locations require a bound location evidence audit")
        origin = case.get("execution_origin")
        if origin is not None:
            if (not isinstance(origin, dict) or origin.get("kind") not in {"rerun", "reused"}
                    or not isinstance(origin.get("parent_run_id"), str)
                    or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", origin["parent_run_id"])
                    or origin["parent_run_id"] == material.get("run_id")
                    or origin.get("source_run_id") != (material.get("run_id") if origin["kind"] == "rerun" else origin["parent_run_id"])
                    or not isinstance(origin.get("provenance_sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", origin["provenance_sha256"])):
                raise ValueError("Review execution origin is not bound to its run")
        if not isinstance(case.get("source", {}).get("files", []), list):
            raise ValueError("Review source files must be a complete text-file list")
        for file in case.get("source", {}).get("files", []):
            if not isinstance(file.get("path"), str) or not isinstance(file.get("content"), str):
                raise ValueError("Source files require path and full content strings")
        if case.get("svg_file"):
            svg_path = _contained_file(root, case["svg_file"])
            case["svg"] = sanitize_svg(svg_path.read_text(encoding="utf-8"), case.get("cfg"))
        elif case.get("cfg") is not None:
            raise ValueError(f"Case {identifier} has a CFG but no rendered SVG")
        else:
            case["svg"] = None
        for name in ("png_file", "suggestions_file"):
            case[name] = _safe_local_link(case.get(name))
    material["cases"].sort(key=lambda case: case["case_id"])
    # JSON is a data block, but </script> must still not terminate its HTML element.
    data = json.dumps(material, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    for original, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"),
                              ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        data = data.replace(original, escaped)
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count("__REVIEW_DATA__") != 1:
        raise ValueError("Review template must contain exactly one data insertion point")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.replace("__REVIEW_DATA__", data), encoding="utf-8")
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="生成无需网络及 fetch 的 Skill-IR 本地审查页")
    parser.add_argument("--data", type=Path, required=True, help="导出的 review-data.json")
    parser.add_argument("--output", type=Path, required=True, help="本地 index.html")
    parser.add_argument("--assets-root", type=Path, help="SVG 相对路径的根目录，默认数据文件目录")
    args = parser.parse_args(argv)
    print(build_review_site(args.data, args.output, assets_root=args.assets_root))


if __name__ == "__main__":
    main()
