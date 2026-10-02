"""Offline integrity checks for external human-readable review files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
BASE = ROOT / "packages/skill-ir/experiments/semantics_baseline"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plan = json.loads((WORK / "render-input.json").read_text(encoding="utf-8"))["samples"]
    catalog = json.loads((BASE / "frozen/corpus/corpus.json").read_text(encoding="utf-8"))
    sources = {sample["id"]: sample for sample in catalog["samples"]}
    expected = {sample["basename"] + ".md" for sample in plan}
    directory = ROOT / "result/suggestions"
    actual = {p.name for p in directory.iterdir()}
    assert actual == expected, {"missing": sorted(expected - actual), "extra": sorted(actual - expected)}
    assert all(p.is_file() and not p.is_symlink() for p in directory.iterdir())
    locked = json.loads((WORK / "suggestions-input-lock.json").read_text(encoding="utf-8"))
    for relative, digest in locked.items():
        assert sha(ROOT / relative) == digest, f"Protected input/output changed: {relative}"

    checks = []
    for item in plan:
        path = directory / (item["basename"] + ".md")
        content = path.read_text(encoding="utf-8")
        assert content.startswith(f"# {item['index']:03d} "), path.name
        assert "\ufffd" not in content, f"Replacement glyph: {path.name}"
        assert item["sample_id"] in content, f"Missing sample identity: {path.name}"
        assert re.search(rf"第\s*{item['repetition']}\s*(次|轮)", content), path.name
        for suffix, parent in [(".zip", "dataset/skills"), (".png", "result/ir-IPP")]:
            assert (ROOT / parent / (item["basename"] + suffix)).as_posix() in content, path.name
        assert "模型：deepseek-v4-flash-max" not in content, path.name
        annotation = json.loads((BASE / "frozen/corpus" / sources[item["sample_id"]]["annotation_path"]).read_text(encoding="utf-8"))
        facts = {fact["id"] for fact in annotation["facts"]}
        listed = set(re.findall(rf"\b{item['sample_id']}-F\d+\b", content))
        assert listed == facts, {"file": path.name, "missing_facts": sorted(facts - listed), "extra_facts": sorted(listed - facts)}
        cfg = item["cfg"]
        blocks = set(cfg["blocks"])
        instructions = {ins["id"] for block in cfg["blocks"].values() for ins in block["instructions"]}
        results = {operand.get("identifier") for block in cfg["blocks"].values() for ins in block["instructions"] for operand in ins["inputs"] + ins["outputs"] if operand.get("identifier", "")}
        for pattern, valid in [(r"\bblock_\d+\b", blocks), (r"\bir_\d+\b", instructions), (r"\bresult_\d+\b", results)]:
            used = set(re.findall(pattern, content))
            assert used <= valid, {"file": path.name, "unknown_references": sorted(used - valid)}
        for edge in re.findall(r"\bedge_(\d+)\b", content):
            assert 1 <= int(edge) <= len(cfg["edges"]), (path.name, edge)
        link_count = 0
        line_count = 0
        for raw in re.findall(r"\]\(([^)]+)\)", content):
            target = raw.strip("<>")
            if target.startswith("https://") or target.startswith("http://"):
                continue
            match = re.fullmatch(r"(.+?)(?::(\d+))?", target)
            linked, line = Path(match.group(1)), match.group(2)
            assert linked.is_absolute() and linked.exists(), (path.name, target)
            link_count += 1
            if line:
                assert linked.is_file() and 1 <= int(line) <= len(linked.read_text(encoding="utf-8").splitlines()), (path.name, target)
                line_count += 1
        assert line_count, f"No source line evidence: {path.name}"
        assert sha(Path(item["analysis_path"])) == item["analysis_sha256"], path.name
        checks.append({"basename": item["basename"], "sample_id": item["sample_id"], "repetition": item["repetition"],
                       "review_sha256": sha(path), "analysis_sha256": item["analysis_sha256"],
                       "zip_sha256": sha(ROOT / "dataset/skills" / (item["basename"] + ".zip")),
                       "png_sha256": sha(ROOT / "result/ir-IPP" / (item["basename"] + ".png")),
                       "facts_covered": sorted(facts), "source_line_links_checked": line_count, "local_links_checked": link_count})
    audit = {"status": "passed", "suggestions": len(checks), "facts_covered": sum(len(row["facts_covered"]) for row in checks),
             "protected_files_unchanged": len(locked), "samples": checks,
             "scope": "Integrity, pairing, source line and CFG reference existence; semantic judgment is documented in each individually reviewed Markdown file."}
    (WORK / "suggestions-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k != "samples"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
