"""Mirror of test/negation-constraint.test.js.

Exercises the same code path index.js uses: extract_document_flow (semantic gate
with an injected refiner) followed by the GLOBAL resolve_pending_constraints pass.
"""

import json
import os
import tempfile

from skill_sfg.parser.skill_parser import parse_skill, parse_readme
from skill_sfg.parser.doc_flow_extractor import (
    extract_document_flow,
    resolve_pending_constraints,
)


def _with_skill(markdown_body, refiner, fn, resolve_opts=None):
    resolve_opts = resolve_opts or {}
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8", newline="") as handle:
            handle.write(f"---\nname: negation-test\ndescription: Use when testing.\nversion: 0.1.0\n---\n\n{markdown_body}\n")
        skill_data = parse_skill(tmp)
        readme_data = parse_readme(tmp)
        result = extract_document_flow(skill_data, readme_data, {
            "semanticLlm": True,
            "llmApiKey": "test-key",
            "semanticRefiner": refiner,
        })
        resolved = resolve_pending_constraints(result["nodes"], resolve_opts)
        result["nodes"] = resolved["nodes"]
        result["edges"] = result["edges"] + resolved["edges"]
        return fn(result)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _negation_refiner(node, _ctx=None):
    text = str(node.get("instructionText") or (node.get("formal_semantics") or {}).get("evidence", {}).get("text") or "").lower()
    if "install" in text and "vetting" in text:
        return json.dumps({
            "classification": "policy_rule", "actionability": "runtime_action", "operation_type": "guard",
            "negation_kind": "constraint",
            "constraint_edge": {"kind": "ordering", "before_action": "vet skill", "after_action": "install skill", "note": ""},
            "confidence": 0.9, "reason": "vetting must precede install",
        })
    if "overwrite" in text:
        return json.dumps({
            "classification": "policy_rule", "actionability": "runtime_action", "operation_type": "guard",
            "negation_kind": "constraint",
            "constraint_edge": {"kind": "guard", "guarded_action": "overwrite existing files", "note": ""},
            "confidence": 0.9, "reason": "overwrite is forbidden",
        })
    if "send" in text and "external" in text:
        return json.dumps({
            "classification": "description", "actionability": "context_only",
            "negation_kind": "disclaimer", "constraint_edge": None,
            "confidence": 0.9, "reason": "capability disclaimer",
        })
    return json.dumps({"classification": "workflow_instruction", "actionability": "runtime_action", "operation_type": "read", "confidence": 0.6, "reason": "action"})


def test_ordering_constraint_with_matchable_endpoints_produces_constraint_edge():
    def check(result):
        constraint_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_constraint"]
        assert len(constraint_edges) >= 1
        e = constraint_edges[0]
        assert e["type"] == "control_flow"
        assert e["data_flow"]["from_param"] == "state"
        assert e["data_flow"]["to_param"] == "state"
        assert "must precede" in e["semantic_reason"]

    _with_skill(
        "## Steps\nVet the skill thoroughly.\nInstall the skill from the registry.\n## Rules\nNever install a skill without vetting it first.",
        _negation_refiner, check)


def test_guard_kind_constraint_marks_conditions_and_creates_no_edge():
    def check(result):
        constraint_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_constraint"]
        assert len(constraint_edges) == 0
        node = next((n for n in result["nodes"] if "overwrite" in str(n.get("instructionText") or "").lower()), None)
        assert node is not None
        conds = (node.get("formal_semantics") or {}).get("conditions") or []
        assert any("constraint:" in str(c.get("text") or "") for c in conds)
        assert node["formal_semantics"]["operation_type"] == "guard"

    _with_skill("## Rules\nNever overwrite existing files.", _negation_refiner, check)


def test_capability_disclaimer_dropped_to_context():
    def check(result):
        node = next((n for n in result["nodes"] if "send" in str(n.get("instructionText") or (n.get("formal_semantics") or {}).get("evidence", {}).get("text") or "").lower()), None)
        if node:
            assert node.get("semanticKind") == "doc_definition" or node.get("excludeFromFlow") is True
        constraint_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_constraint"]
        assert len(constraint_edges) == 0

    _with_skill("## Notes\nThe skill does not send any personal data externally.", _negation_refiner, check)


def test_ordering_constraint_with_unmatchable_endpoints_synthesizes_nodes():
    def check(result):
        synth = [n for n in result["nodes"] if n.get("synthesized_from") == "negation_constraint"]
        assert len(synth) >= 1
        constraint_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_constraint"]
        assert len(constraint_edges) >= 1

    _with_skill("## Rules\nNever install a skill without vetting it first.", _negation_refiner, check)


def test_llm_endpoint_resolver_links_to_paraphrase_nodes_instead_of_synthesizing():
    def resolver(payload):
        phrases = payload["phrases"]
        candidates = payload["candidates"]

        def find_id(needle):
            for i, c in enumerate(candidates):
                if needle in c["text"].lower():
                    return f"n{i + 1}"
            return None

        results = []
        import re
        for phrase in phrases:
            if re.search(r"vet", phrase):
                results.append({"phrase": phrase, "node_id": find_id("review")})
            elif re.search(r"install", phrase):
                results.append({"phrase": phrase, "node_id": find_id("deploy")})
            else:
                results.append({"phrase": phrase, "node_id": None})
        return json.dumps({"results": results})

    def check(result):
        import re
        synth = [n for n in result["nodes"] if n.get("synthesized_from") == "negation_constraint"]
        assert len(synth) == 0
        constraint_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_constraint"]
        assert len(constraint_edges) == 1
        e = constraint_edges[0]
        by_name = {n["name"]: n for n in result["nodes"]}
        src = by_name.get(e["source"])
        tgt = by_name.get(e["target"])
        assert re.search(r"review", str((src or {}).get("instructionText") or ""), re.IGNORECASE)
        assert re.search(r"deploy", str((tgt or {}).get("instructionText") or ""), re.IGNORECASE)

    _with_skill(
        "## Steps\nReview the package thoroughly.\nDeploy it to the target environment.\n## Rules\nNever install a skill without vetting it first.",
        _negation_refiner, check,
        {"llmApiKey": "test-key", "constraintEndpointResolver": resolver})
