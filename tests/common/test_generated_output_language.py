"""Generated engineering text is English; source data retains its own language."""
from pathlib import Path
import ast
import re


def test_program_output_literals_are_english():
    root = Path(__file__).resolve().parents[2] / "src" / "skillflow"
    # Windows can report these input error messages in the OS locale. They are
    # matched by retry classification, not emitted as generated output.
    localized_input_messages = {
        ("common/audit_execution.py", "拒绝访问"),
        ("common/audit_execution.py", "另一个程序正在使用"),
    }
    violations = []
    for path in root.rglob("*.py"):
        # Prompt examples have separate model-visible fixture tests.
        if path.name in {"prompts.py", "prompt.py", "binding_examples.py", "prompt_examples.py"}:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if re.search(r"[\u3400-\u9fff]", node.value):
                identity = (path.relative_to(root).as_posix(), node.value)
                if identity not in localized_input_messages:
                    violations.append((identity[0], node.lineno, node.value))
    assert violations == []
