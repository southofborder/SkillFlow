"""Record and verify the minimal v1 -> v2 constraints migration offline."""

from __future__ import annotations

import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys


BASE = Path(__file__).resolve().parents[1]
OLD = BASE / "frozen" / "production" / "src" / "skill_ir"
NEW = BASE.parents[1] / "src" / "skill_ir"
OUTPUT = BASE / "contract_v2"
CHANGED = {
    "extraction/candidate.py",
    "extraction/compiler.py",
    "extraction/prompt.py",
    "ir/basic_block.py",
    "ir/cfg.py",
    "ir/instruction.py",
}
CONTRACT_SCOPE = {"extraction", "ir", "artifacts"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema(source: Path) -> dict:
    code = (
        "import json, sys; sys.path.insert(0, sys.argv[1]); "
        "from skill_ir.extraction.candidate import IRAnalysisCandidate; "
        "print(json.dumps(IRAnalysisCandidate.model_json_schema(), ensure_ascii=True))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, str(source.parent)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def prompt_parts(source: Path) -> dict:
    tree = ast.parse((source / "extraction" / "prompt.py").read_text(encoding="utf-8"))
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"_INSTRUCTIONS", "_EXAMPLES"}
    }


def main() -> None:
    old_files = {
        p.relative_to(OLD).as_posix(): p
        for p in OLD.rglob("*.py")
        if p.relative_to(OLD).parts[0] in CONTRACT_SCOPE
    }
    new_files = {
        p.relative_to(NEW).as_posix(): p
        for p in NEW.rglob("*.py")
        if p.relative_to(NEW).parts[0] in CONTRACT_SCOPE
    }
    assert old_files.keys() == new_files.keys(), "Production source inventory changed"
    changed = {name for name in old_files if digest(old_files[name]) != digest(new_files[name])}
    assert changed == CHANGED, f"Unexpected migration source diff: {sorted(changed)}"

    old_prompt, new_prompt = prompt_parts(OLD), prompt_parts(NEW)
    assert old_prompt["_EXAMPLES"] == new_prompt["_EXAMPLES"], "Prompt examples changed"
    instructions = new_prompt["_INSTRUCTIONS"]
    start = instructions.index("CONSTRAINTS: ")
    end = instructions.index("Return only JSON matching", start)
    addition = instructions[start:end]
    assert instructions[:start] + instructions[end:] == old_prompt["_INSTRUCTIONS"]
    old_schema, new_schema = schema(OLD), schema(NEW)
    stripped = json.loads(json.dumps(new_schema))
    for scope in [stripped, stripped["$defs"]["CandidateBlock"], stripped["$defs"]["CandidateInstruction"]]:
        field = scope["properties"].pop("constraints")
        assert field["type"] == "array" and field["items"] == {"type": "string"}
        assert "constraints" not in scope.get("required", [])
    assert stripped == old_schema, "Schema changes exceed three optional constraints fields"

    OUTPUT.mkdir(exist_ok=True)
    diff = "".join(
        line
        for name in sorted(changed)
        for line in difflib.unified_diff(
            old_files[name].read_text(encoding="utf-8").splitlines(keepends=True),
            new_files[name].read_text(encoding="utf-8").splitlines(keepends=True),
            fromfile="v1/" + name,
            tofile="v2/" + name,
        )
    )
    (OUTPUT / "source-migration.diff").write_text(diff, encoding="utf-8", newline="\n")
    (OUTPUT / "prompt-addition.txt").write_text(addition, encoding="utf-8", newline="\n")
    for name, payload in [("candidate-schema-v1.json", old_schema), ("candidate-schema-v2.json", new_schema)]:
        (OUTPUT / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": 1,
        "from_contract": "v1",
        "to_contract": "v2",
        "purpose": "approved representation migration; not prompt optimization gain",
        "checked_source_scope": sorted(CONTRACT_SCOPE),
        "prompt_examples_unchanged": True,
        "schema_change": "three optional constraints: list[str] fields with independent empty defaults",
        "changed_production_files": {
            name: {"v1_sha256": digest(old_files[name]), "v2_sha256": digest(new_files[name])}
            for name in sorted(changed)
        },
        "artifacts": {
            name: digest(OUTPUT / name)
            for name in ["source-migration.diff", "prompt-addition.txt", "candidate-schema-v1.json", "candidate-schema-v2.json"]
        },
    }
    (OUTPUT / "migration.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Verified minimal v2 contract migration: 6 source files, 3 candidate schema fields, unchanged examples")


if __name__ == "__main__":
    main()
