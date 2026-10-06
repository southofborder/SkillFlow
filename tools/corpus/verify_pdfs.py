"""Check PDF content, render EVERY page with Poppler, and create visual review sheets.

The generated report is structural evidence only. A human/agent must inspect the
PNGs and record the visual review separately; rendering is not semantic approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from skillflow.common.paths import project_root, resolve_material_path

ROOT = project_root() / "experiments/corpus/semantics_review"
REPO = project_root()
from skillflow.common.inputs.skill_package import load_skill_package  # noqa: E402

from tools.corpus.build_pdfs import generator_inventory


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_build_sources(build, root=ROOT):
    """Reject stale PDFs even when all sample/fact identifiers still match."""
    files = {p.relative_to(root).as_posix(): p for p in root.rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    expected = build["source_sha256"]
    if files.keys() != expected.keys():
        changed = sorted(files.keys() ^ expected.keys())
        raise ValueError(f"Corpus file inventory changed since PDF build: {changed}; rebuild PDFs.")
    changed = [name for name, path in files.items() if sha(path) != expected[name]]
    if changed:
        raise ValueError(f"Corpus content changed since PDF build: {changed}; rebuild PDFs.")
    if build.get("generator_sha256") != generator_inventory(REPO):
        raise ValueError("PDF generator changed since PDF build; rebuild PDFs.")
    loader = REPO / "src/skillflow/common/inputs/skill_package.py"
    if sha(loader) != build["production_loader_sha256"]:
        raise ValueError("Production loader changed since PDF build; rebuild PDFs.")


def verify_content(pdf_dir):
    build = json.loads((pdf_dir / "build_manifest.json").read_text(encoding="utf-8"))
    verify_build_sources(build)
    from pypdf import PdfReader

    corpus = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
    report = {"schema_version": 1, "checks": {}, "visual_review": "requires_manual_inspection", "pdfs": {}}
    for name, info in build["outputs"].items():
        path = pdf_dir / name
        assert sha(path) == info["sha256"], f"PDF changed since build: {name}"
        reader = PdfReader(path)
        assert len(reader.pages) == info["pages"]
        texts = [page.extract_text() for page in reader.pages]
        assert all(text.strip() for text in texts), f"Empty page: {name}"
        all_text = "\n".join(texts)
        for expected in ("语义复核", "待共同复核", "目录"):
            assert expected in all_text, f"Chinese text not searchable: {expected}"
        assert "\ufffd" not in all_text, f"Replacement glyph: {name}"
        for sample_id, page in info["page_index"].items():
            if "/" not in sample_id:
                assert sample_id in texts[page - 1], f"Wrong sample index {sample_id} page {page}"
        for number, text in enumerate(texts, 1):
            assert str(number) in text.splitlines()[-2:], f"Missing page footer: {name} page {number}"
        if name == "skill-ir-semantics-review.pdf":
            for sample in corpus["samples"]:
                ann = json.loads((ROOT / sample["annotation_path"]).read_text(encoding="utf-8"))
                for fact in ann["facts"]:
                    assert fact["id"] in all_text, f"Missing fact in main PDF: {fact['id']}"
        else:
            # The renderer draws only complete source content at 9 pt. Collect those
            # text runs directly, without line-number gutters or repeated page furniture.
            actual = []
            for page in reader.pages:
                def visitor(text, cm, tm, font_dict, font_size):
                    if abs(font_size - 9) < .001:
                        actual.append(text.replace("\n", ""))
                page.extract_text(visitor_text=visitor)
            expected = []
            for sample in corpus["samples"]:
                if sample["kind"] == "upstream":
                    package = load_skill_package(ROOT / sample["package_path"])
                    for file in package.readable_files():
                        expected.extend(line.expandtabs(4) for line in file.content.splitlines())
            assert "".join(actual) == "".join(expected), "Appendix source content was omitted, reordered or changed"
            report["checks"]["appendix_all_readable_source_exact"] = True
        report["pdfs"][name] = {"pages": len(reader.pages), "sha256": sha(path), "all_pages_have_text": True,
                                "chinese_searchable": True, "sample_page_index_checked": True,
                                "page_numbers_checked": True}
    report["checks"]["all_fact_identifiers_present"] = True
    return report


def render(pdf_dir, render_dir, report, pdftoppm, dpi):
    from PIL import Image, ImageDraw, ImageFont

    render_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("DejaVuSans.ttf", 17) if sys.platform != "win32" else ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    for name, info in report["pdfs"].items():
        stem = Path(name).stem
        directory = render_dir / stem
        directory.mkdir(parents=True, exist_ok=True)
        prefix = directory / "page"
        # Render an immutable snapshot: rebuilding a PDF while Poppler holds it
        # open can otherwise produce blank pages even with exit status zero.
        with tempfile.TemporaryDirectory(prefix="skill-review-render-") as temp:
            snapshot = Path(temp) / name
            shutil.copyfile(pdf_dir / name, snapshot)
            assert sha(snapshot) == info["sha256"], f"PDF changed before rendering: {name}"
            result = subprocess.run([pdftoppm, "-r", str(dpi), "-png", str(snapshot), str(prefix)],
                                    check=True, capture_output=True, text=True)
            if "error" in result.stderr.lower():
                raise RuntimeError(f"Poppler reported a rendering error for {name}: {result.stderr}")
        pages = sorted(directory.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        assert len(pages) == info["pages"], f"Stale/missing page renders under {directory}"
        # Each page remains available individually at the requested resolution.
        # Six-up sheets support complete pagination review; inspect representative
        # individual pages at full resolution for glyph and source detail.
        sheets = []
        for first in range(0, len(pages), 6):
            subset = pages[first:first + 6]
            sheet = Image.new("RGB", (1000, 2172), "#dce3e8")
            draw = ImageDraw.Draw(sheet)
            for offset, file in enumerate(subset):
                with Image.open(file) as image:
                    thumb = image.convert("RGB")
                    thumb.thumbnail((480, 675))
                col, row = offset % 2, offset // 2
                x, y = 10 + col * 500, 32 + row * 724
                sheet.paste(thumb, (x, y))
                draw.text((x, y - 24), f"p{first + offset + 1:03d} / {info['pages']}", fill="#153b58", font=font)
            destination = directory / f"sheet-{first // 6 + 1:03d}.jpg"
            sheet.save(destination, quality=88)
            sheets.append(str(destination.resolve()))
        info["rendered_pages"] = len(pages)
        info["contact_sheets"] = sheets
        print(f"Rendered {name}: {len(pages)} pages, {len(sheets)} contact sheets", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=REPO / "output/pdf/skill-ir-semantics-review")
    parser.add_argument("--render-dir", type=Path, default=REPO / "tmp/pdfs/skill-ir-semantics-review")
    parser.add_argument("--pdftoppm", default=shutil.which("pdftoppm"))
    parser.add_argument("--dpi", type=int, default=110)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    report = verify_content(args.pdf_dir.resolve())
    if not args.check_only:
        if not args.pdftoppm:
            raise SystemExit("Poppler pdftoppm is required; install it or pass --pdftoppm.")
        render(args.pdf_dir.resolve(), args.render_dir.resolve(), report, args.pdftoppm, args.dpi)
    args.render_dir.mkdir(parents=True, exist_ok=True)
    (args.render_dir / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PDF content verification passed. Visual review remains a separate manual step.")


if __name__ == "__main__":
    main()
