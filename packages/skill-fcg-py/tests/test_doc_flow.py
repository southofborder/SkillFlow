"""Mirror of test/doc-flow.test.js (rule-only cases) + the LLM context-gate case.

These exercise extract_document_flow directly (no full analyzer pipeline yet;
the SKILL.md-only path is the same code the pipeline drives). The full-analyzer
cases from the JS suite (SkillFCGAnalyzer.analyze) are deferred to M1e once the
fcg_builder assigns ids; here we assert the doc-flow node/edge contract that the
builder consumes.
"""

import os
import tempfile

from skill_fcg.parser.skill_parser import parse_skill, parse_readme
from skill_fcg.parser.doc_flow_extractor import extract_document_flow


def _write_skill(tmp: str, body: str) -> None:
    with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8", newline="") as handle:
        handle.write(body)


def test_doc_flow_splits_english_compound_actions_into_ordered_doc_steps():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: english-compound-skill
description: Test English compound action splitting.
version: 0.1.0
---

- Summarize the email content and save it locally.
- Read customer records, redact secrets, and send a summary to the model.
- Extract the city from the profile and call the weather API.
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {"semanticLlm": False})

    steps = [n for n in result["nodes"] if n.get("semanticKind") == "doc_step"]
    texts = [f"{n['formal_semantics']['operation_type']}:{n['instructionText']}" for n in steps]

    assert any("transform:Summarize the email content" in t for t in texts)
    assert any("write:save it locally" in t for t in texts)
    assert any("read:Read customer records" in t for t in texts)
    assert any("transform:redact secrets" in t for t in texts)
    assert any("model_inference:send a summary to the model" in t for t in texts)
    assert any("transform:Extract the city from the profile" in t for t in texts)
    assert any("external_egress:call the weather API" in t for t in texts)

    sequence_edges = [e for e in result["edges"] if e["type"] == "control_flow"]
    assert len(sequence_edges) >= 5


def test_doc_flow_adds_implicit_object_reads_and_reuses_prior_object_producers():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: implicit-object-skill
description: Test implicit object reads.
version: 0.1.0
---

- Write the email content to a local file.
- Read email content and write it to a local file.
- Write the report to a file, then upload the report.
- Write the analysis result to a local file.
- Generate a report and upload the report.
- Generate a report about the email.
- Generate a report about current AI.
- Create the analysis result and save it locally.
- Summarize the email content and save the summary.
- Read the email and write it to a file.
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {"semanticLlm": False})

    steps = [n for n in result["nodes"] if n.get("semanticKind") == "doc_step"]
    implicit_reads = [n for n in steps if (n.get("formal_semantics") or {}).get("evidence", {}).get("method") == "implicit_object_read"]
    email_implicit_reads = [n for n in implicit_reads if "email_content" in n["name"]]
    email_object_implicit_reads = [n for n in implicit_reads if "semantic_email" in n["name"] and "email_content" not in n["name"]]

    def find(pred):
        return next((n for n in steps if pred(n)), None)

    write_it = find(lambda n: n["instructionText"] == "write it to a local file.")
    explicit_read_email = find(lambda n: n["instructionText"] == "Read email content")
    upload_report = find(lambda n: n["instructionText"] == "upload the report.")
    write_report = find(lambda n: n["instructionText"] == "Write the report to a file")
    generated_report = find(lambda n: n["instructionText"] == "Generate a report")
    generated_report_about_email = find(lambda n: n["instructionText"] == "Generate a report about the email.")
    generated_report_about_ai = find(lambda n: n["instructionText"] == "Generate a report about current AI.")
    created_analysis = find(lambda n: n["instructionText"] == "Create the analysis result")
    save_created = find(lambda n: n["instructionText"] == "save it locally." and n.get("objectProducer") == (created_analysis or {}).get("name"))
    summarize_email = find(lambda n: n["instructionText"] == "Summarize the email content")
    save_summary = find(lambda n: n["instructionText"] == "save the summary.")
    explicit_read_the_email = find(lambda n: n["instructionText"] == "Read the email")
    write_pronoun_email = find(lambda n: n["instructionText"] == "write it to a file." and n.get("objectProducer") == (explicit_read_the_email or {}).get("name"))

    object_edges = [e for e in result["edges"] if e.get("validation_method") == "doc_flow_object_context"]

    assert len(email_implicit_reads) == 1
    assert len(email_object_implicit_reads) == 1
    assert len([n for n in implicit_reads if "summary" in n["name"]]) == 0
    assert write_it is not None
    assert explicit_read_email is not None
    assert write_it.get("objectProducer") == explicit_read_email["name"]
    assert upload_report is not None
    assert write_report is not None
    assert upload_report.get("objectProducer") == write_report["name"]
    assert generated_report is not None
    assert generated_report_about_email is not None
    assert generated_report_about_email.get("objectProducer") == email_object_implicit_reads[0]["name"]
    assert generated_report_about_ai is not None
    assert generated_report_about_ai.get("objectProducer") is None
    assert len([n for n in implicit_reads if "current_ai" in n["name"]]) == 0
    assert created_analysis is not None
    assert save_created is not None
    assert summarize_email is not None
    assert save_summary is not None
    assert save_summary.get("objectProducer") == summarize_email["name"]
    assert explicit_read_the_email is not None
    assert write_pronoun_email is not None
    assert any(e["source"] == email_implicit_reads[0]["name"] and "email_content" in e["semantic_reason"] for e in object_edges)
    assert any(e["source"] == explicit_read_email["name"] and e["target"] == write_it["name"] for e in object_edges)
    assert any(e["source"] == write_report["name"] and e["target"] == upload_report["name"] for e in object_edges)
    assert any(e["source"] == created_analysis["name"] and e["target"] == save_created["name"] for e in object_edges)
    assert any(e["source"] == summarize_email["name"] and e["target"] == save_summary["name"] for e in object_edges)
    assert any(e["source"] == explicit_read_the_email["name"] and e["target"] == write_pronoun_email["name"] for e in object_edges)


def test_doc_flow_classifies_readable_abstract_artifact_objects_for_implicit_reads():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: object-classification-skill
description: Test implicit object classification.
version: 0.1.0
---

- Upload the report.
- Save the analysis result locally.
- Generate a report about the email.
- Generate a report from customer records.
- Write the chat history to a file.
- Upload the invoice PDF.
- Generate a report about current AI.
- Generate a report about current task.
- Generate a report about assistant behavior.
- Generate a report about this skill.
- Generate a report and upload the report.
- Create the analysis result and save it locally.
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {"semanticLlm": False})

    steps = [n for n in result["nodes"] if n.get("semanticKind") == "doc_step"]
    implicit_reads = [n for n in steps if (n.get("formal_semantics") or {}).get("evidence", {}).get("method") == "implicit_object_read"]
    names = [n["name"] for n in implicit_reads]
    keys = [(n.get("formal_semantics") or {}).get("evidence", {}).get("object_key") or "" for n in implicit_reads]
    text = " ".join(
        ((n.get("formal_semantics") or {}).get("evidence", {}).get("object_key") or n.get("instructionText") or "")
        for n in implicit_reads
    )

    import re as _re
    assert any("semantic_email" in n for n in names)
    assert any("customer_records" in n for n in names)
    assert any("chat_history" in n for n in names)
    assert any("invoice_pdf" in n for n in names)
    assert "report" in keys
    assert "analysis_result" in keys
    assert not _re.search(r"\bcurrent_ai\b", text)
    assert not _re.search(r"\bcurrent_task\b", text)
    assert not _re.search(r"\bassistant_behavior\b", text)
    assert not _re.search(r"\bthis_skill\b", text)


def test_doc_flow_treats_table_definitions_and_passive_fragments_as_context():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: definition-skill
description: Test definition gating.
version: 0.1.0
---

| Status | Meaning |
|--------|---------|
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |

When a lesson is ready, write the lesson to `memory.md`.
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {"semanticLlm": False})

    action_steps = [n for n in result["nodes"] if n.get("semanticKind") == "doc_step"]
    contexts = [n for n in result["nodes"] if n.get("semanticKind") == "doc_definition"]

    assert any("Elevated to CLAUDE.md" in n["instructionText"] for n in contexts)
    assert not any("AGENTS.md" in n["instructionText"] for n in action_steps)
    assert not any("copilot-instructions.md" in n["instructionText"] for n in action_steps)
    assert any((n.get("formal_semantics") or {}).get("operation_type") == "write" and "write the lesson" in n["instructionText"] for n in action_steps)
    assert not any("promoted" in e["source"] or "promoted" in e["target"] for e in result["edges"])


def test_skill_md_anchor_keeps_situation_to_action_rows_as_grounded_route_nodes():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: skill-anchor-route
description: Test SKILL route extraction.
version: 0.1.0
---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {"semanticLlm": False})

    route_nodes = [
        n for n in result["nodes"]
        if (n.get("location") or {}).get("file") == "SKILL.md"
        and (n.get("source_context") or {}).get("source_role") == "semantic_anchor"
        and "skill_anchor_route" in ((n.get("formal_semantics") or {}).get("evidence", {}).get("method") or "")
    ]

    assert not any(n["name"].startswith("rule.trigger.") for n in result["nodes"])
    assert not any(n["name"].startswith("rule.policy.") for n in result["nodes"])
    assert any(
        "Command/operation fails" in n["instructionText"]
        and any(c["text"] == "Command/operation fails" for c in n["formal_semantics"]["conditions"])
        and any(t["value"] == ".learnings/ERRORS.md" for t in n["formal_semantics"]["targets"])
        for n in route_nodes
    )
    assert all(n.get("semanticKind") == "doc_step" for n in route_nodes)


def test_semantic_llm_gate_converts_candidate_into_context_only_node():
    def refiner(_node, _ctx):
        import json
        return json.dumps({
            "classification": "definition",
            "actionability": "context_only",
            "grammar": "SVC description of a referenced document, not an imperative runtime action",
            "completed_sentence": "The referenced item is memory.md.",
            "confidence": 0.88,
            "reason": "The test refiner marked this as documentation context.",
        })

    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, """---
name: llm-context-gate-skill
description: Test LLM context-only gate.
version: 0.1.0
---

Read `memory.md`.
""")
        skill_data = parse_skill(tmp)
        result = extract_document_flow(skill_data, None, {
            "semanticLlm": True,
            "semanticRefiner": refiner,
        })

    context_node = next((n for n in result["nodes"] if n.get("semanticKind") == "doc_definition"), None)
    assert context_node is not None
    assert context_node["excludeFromFlow"] is True
    assert context_node["semantic_gate"]["actionability"] == "context_only"
    assert not any(n.get("semanticKind") == "doc_step" for n in result["nodes"])
    assert not any(e["source"] == context_node["name"] or e["target"] == context_node["name"] for e in result["edges"])
