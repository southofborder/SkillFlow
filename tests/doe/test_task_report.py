"""Task reports keep source references separate from semantic endorsement."""
from copy import deepcopy
from html import unescape
from types import SimpleNamespace
import re
from skillflow.propagation.contracts.references import target_key

import pytest

from skillflow.doe.task_report import NOTICE, build_view, render_html, render_markdown


@pytest.fixture
def review():
    files = {"skill/SKILL.md": "Task overview.\r\n\r\nReturn items unchanged.\r\nBackground only.\r\nNo deletion.\r\n",
             "skill/ref.md": "Keep the original argument.\n未翻译的来源。"}
    def evidence(file="skill/SKILL.md", start=3, end=3, reason="This preserves the original items."):
        return {"file": file, "start_line": start, "end_line": end, "reason": reason}
    task = {"schema_version": "skillflow-task-v3", "basis": "declared_skill",
            "purpose": {"text": "Return the specified result.", "evidences": [evidence(start=1, end=1)]},
            "requirements": [
                {"id": "R1", "text": "Return the original items value.", "evidences": [evidence()],
                 "bindings": [{"target": {"instruction_id":"ir_return","side":"input","index":0}, "reason": "The actual return input preserves the specified result."}]},
                {"id": "R2", "text": "Preserve the original argument.",
                 "evidences": [evidence("skill/ref.md", 1, 1), evidence()], "bindings": []},
                {"id": "R3", "text": "Do not delete the index.", "evidences": [evidence(start=5, end=5)],
                 "bindings": [{"target": {"path":["constraints",0]}, "reason": "The prohibition applies to the entire graph."}]},
            ]}
    cfg = {"entry_block_id": "b", "constraints": ["Do not delete"], "edges": [],
           "blocks": {"b": {"block_id": "b", "instructions": [
               {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "items"}], "outputs": []},
               {"id": "ir_other", "opcode": "dispatch", "inputs": [], "outputs": []}]}}}
    targets = {target_key({"instruction_id":"ir_return","side":"input","index":0}): {"pointer": "/blocks/b/instructions/0/inputs/0", "kind": "input", "instruction_id": "ir_return", "block_id": "b"},
               target_key({"path":["constraints",0]}): {"pointer": "/constraints/0", "kind": "constraint"},
               target_key({"block_id":"b","path":[]}): {"pointer": "/blocks/b", "kind": "block", "block_id": "b"}}
    realizations = [{"requirement_id": r["id"], "status": "expressed" if r["bindings"] else "unmapped",
        "bindings": r.pop("bindings"), "gaps": []} for r in task["requirements"]]
    task.update(source_accounting=[], issues=[])
    return SimpleNamespace(task=task, files=files, targets=targets, cfg=cfg, realizations=realizations,
                           boundaries={"binary_files": ["blob.bin"], "uninterpreted_files": []})


def test_shared_view_preserves_exact_source_and_candidate_order(review):
    view = build_view(review)
    assert [item["id"] for item in view["requirements"]] == ["R1", "R2", "R3"]
    assert view["requirements"][0]["evidences"][0]["quote"] == "Return items unchanged.\r\n"
    assert view["requirements"][1]["evidences"][0]["file"] == "skill/ref.md"
    assert view["requirements"][1]["evidences"][1]["quote"] == "Return items unchanged.\r\n"
    assert "Background only." in view["requirements"][0]["evidences"][0]["context"]
    assert view["requirements"][0]["bindings"][0]["value"] == {"type": "result", "identifier": "items"}
    assert view["sources"][0]["uncited_ranges"] == [[4, 4]]
    assert view["sources"][1]["uncited_ranges"] == [[2, 2]]


def test_reports_share_one_view(monkeypatch, review):
    import skillflow.doe.task_report as report
    original, calls = report.build_view, []
    def capture(value, *, metadata=None):
        calls.append((value, metadata))
        return original(value, metadata=metadata)
    monkeypatch.setattr(report, "build_view", capture)
    metadata = {"assistant_review": "A reference is accurate, but the interpretation requires review."}
    report.render_html(review, metadata=metadata)
    report.render_markdown(review, metadata=metadata)
    assert calls == [(review, metadata), (review, metadata)]


def test_real_quote_with_wrong_interpretation_is_not_semantically_endorsed(review):
    review.task["requirements"][0]["text"] = "Return the entire response."
    for report in (render_html(review), render_markdown(review)):
        assert "Return the entire response" in report
        assert "Return items unchanged" in report
        assert NOTICE in report
        assert "Assistant semantic review" in report
        assert "No semantic review is recorded in this preparation." in report
        assert "semantic support and completeness are not proven" in report
        assert "semantics passed" not in report


def test_unbound_and_scope_bindings_are_distinguished(review):
    view = build_view(review)
    assert view["unbound_ids"] == ["R2"]
    returns, other = view["instructions"]
    assert [item["requirement"] for item in returns["bindings"]] == ["R1", "R3"]
    assert [item["requirement"] for item in other["bindings"]] == ["R3"]
    assert other["bindings"][0]["scope"].startswith("Graph-scope binding")
    for report in (render_html(review), render_markdown(review)):
        assert "Unbound requirement" in report
        assert "not an individual data" in report
        assert "IR reverse index" in report


def test_block_scope_is_not_misrepresented_as_direct_ir_use(review):
    review.realizations[0]["bindings"] = [{"target": {"block_id":"b","path":[]}, "reason": "Applies within this block."}]
    for item in build_view(review)["instructions"]:
        assert item["bindings"][0]["scope"].startswith("Block-scope binding")


def test_view_is_isolated_and_rendering_never_mutates_inputs(review):
    before = deepcopy(vars(review))
    view = build_view(review)
    view["requirements"][0]["bindings"][0]["value"]["identifier"] = "mutated"
    view["boundaries"]["binary_files"].append("mutated")
    render_html(review)
    render_markdown(review)
    assert vars(review) == before


def test_xss_and_markdown_injection_are_inert(review):
    hostile = '</pre><script>alert(1)</script><img src=x onerror=alert(2)>[x](https://bad)'
    review.files["skill/SKILL.md"] = review.files["skill/SKILL.md"].replace("Return items unchanged.", hostile)
    review.task["requirements"][0]["text"] = hostile
    review.realizations[0]["bindings"][0]["reason"] = hostile
    review.cfg["constraints"][0] = hostile
    for report in (render_html(review, metadata={"assistant_review": hostile}), render_markdown(review)):
        assert "<script>" not in report
        assert "<img" not in report
        assert "&lt;script&gt;" in report
    markdown = render_markdown(review)
    assert '\\[x\\]\\(https://bad\\)' in markdown


def test_html_links_and_markdown_evidence_links_resolve(review):
    html = render_html(review)
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'href="#([^"]+)"', html)) <= set(ids)
    markdown = render_markdown(review)
    anchors = set(re.findall(r'<a id="([^"]+)"', markdown))
    assert set(re.findall(r'\]\(#([^\)]+)\)', markdown)) <= anchors


def test_boundaries_original_language_and_uncited_disclaimer_visible(review):
    for report in (render_html(review), render_markdown(review)):
        assert "未翻译的来源。" in report
        assert "blob.bin" in report
        assert "Not cited" in report
        assert "background" in report.lower()
        assert "human confirmation" in report
        assert "Source interpretation boundaries" in report


def test_render_order_agrees(review):
    html, md = render_html(review), render_markdown(review)
    texts = [item["text"].rstrip('.') for item in review.task["requirements"]]
    assert [html.index(text) for text in texts] == sorted(html.index(text) for text in texts)
    assert [md.index(text) for text in texts] == sorted(md.index(text) for text in texts)


def test_empty_source_is_displayed_without_fabricated_line(review):
    review.files["skill/empty.md"] = ""
    source = build_view(review)["sources"][-1]
    assert source["lines"] == []
    assert source["uncited_ranges"] == []
    assert "skill/empty.md" in render_html(review)


def test_broken_references_are_not_repaired_by_report(review):
    review.realizations[0]["bindings"][0]["target"] = {"instruction_id":"missing","path":[]}
    with pytest.raises(KeyError):
        build_view(review)
