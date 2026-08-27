"""Mirror of the shell-runtime cases in test/script-flow.test.js.

These exercise the pure-Python shell path (no babel sidecar needed): heredoc
reminders, if-condition blocks, and the rule-only / injected-refiner semantic
gate. The JS-AST path is covered by the cross-engine parity harness instead.
"""

import os
import tempfile

from skill_sfg.parser.script_flow_extractor import extract_script_flow


def _write(tmp: str, rel: str, content: str) -> str:
    path = os.path.join(tmp, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)
    return path


_ERROR_DETECTOR = "\n".join([
    "#!/usr/bin/env bash",
    'OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"',
    "contains_error=false",
    'if [ "$contains_error" = true ]; then',
    "  cat << 'EOF'",
    "<error-detected>",
    "A command error was detected. Consider logging this to .learnings/ERRORS.md if:",
    "- The error was unexpected or non-obvious",
    "</error-detected>",
    "EOF",
    "fi",
    "",
])


def test_shell_runtime_blocks_model_heredoc_and_conditions():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, "scripts/error-detector.sh", _ERROR_DETECTOR)
        flow = extract_script_flow([path], {"rootDir": tmp, "semanticLlm": False})

    runtime_nodes = [
        n for n in flow["nodes"]
        if (n.get("location") or {}).get("file") == "scripts/error-detector.sh"
        and (n.get("source_context") or {}).get("action_evidence", {}).get("extraction_method") == "script_flow_runtime_block"
    ]
    reminder = next((n for n in runtime_nodes if "<error-detected>" in n["source_context"]["action_evidence"]["snippet"]), None)
    condition = next((n for n in runtime_nodes if "contains_error" in n["source_context"]["action_evidence"]["snippet"]), None)

    assert reminder is not None
    assert condition is not None
    assert reminder["source_context"]["source_role"] == "runtime_implementation"
    assert any(".learnings/ERRORS.md" in t["value"] for t in reminder["formal_semantics"]["targets"])
    assert any("contains_error" in c["text"] for c in condition["formal_semantics"]["conditions"])
    assert reminder["semantic_gate"]["method"] == "script_rule_candidate_gate"


def test_shell_semantic_gate_context_only_via_injected_refiner():
    notes = "\n".join([
        "#!/usr/bin/env bash",
        "cat << 'EOF'",
        "Example output only. Do not infer a runtime route from this template.",
        "EOF",
        "",
    ])

    def refiner(_candidate):
        return {
            "classification": "context_only",
            "actionability": "context_only",
            "grammar": "heredoc example text",
            "operation_type": "write",
            "targets": [],
            "conditions": [],
            "effects": [],
            "confidence": 0.9,
            "reason": "Template text, not runtime behavior.",
        }

    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, "scripts/notes.sh", notes)
        flow = extract_script_flow([path], {"rootDir": tmp, "semanticLlm": True, "scriptSemanticRefiner": refiner})

    context_node = next(
        (n for n in flow["nodes"]
         if (n.get("location") or {}).get("file") == "scripts/notes.sh"
         and (n.get("source_context") or {}).get("action_evidence", {}).get("extraction_method") == "script_flow_runtime_block"),
        None,
    )
    assert context_node is not None
    assert context_node["operationType"] == "context"
    assert context_node["excludeFromFlow"] is True
    assert context_node["excludeFromTypeAnalysis"] is True
    assert context_node["semantic_gate"]["actionability"] == "context_only"


def test_shell_semantic_gate_failure_becomes_review_context():
    reminder = "\n".join([
        "#!/usr/bin/env bash",
        'if [ "$contains_error" = true ]; then',
        "  cat << 'EOF'",
        "Consider logging this to .learnings/ERRORS.md.",
        "EOF",
        "fi",
        "",
    ])

    def refiner(_candidate):
        raise RuntimeError("upstream 500")

    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, "scripts/reminder.sh", reminder)
        flow = extract_script_flow(
            [path], {"rootDir": tmp, "semanticLlm": True, "llmApiKey": "test-key", "scriptSemanticRefiner": refiner})

    error_nodes = [
        n for n in flow["nodes"]
        if (n.get("location") or {}).get("file") == "scripts/reminder.sh"
        and (n.get("semantic_gate") or {}).get("method") == "script_semantic_llm_error"
    ]
    assert len(error_nodes) > 0
    assert all(n["excludeFromFlow"] is True for n in error_nodes)
    assert all(n["source_context"]["action_evidence"]["extraction_method"] == "script_flow_runtime_block" for n in error_nodes)
