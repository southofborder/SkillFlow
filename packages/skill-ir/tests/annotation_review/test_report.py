"""Presentation preserves findings and distinguishes failed review from no issue."""

from html import unescape
import re

from skill_ir.annotation_review.report import (
    display_model, render_html, render_markdown, write_reports,
)


def materials(status="complete"):
    result = {
        "status": status, "summary": "issues_found" if status == "complete" else None,
        "reason": "只验证记录和定位；不证明推断成立。",
        "review": {"reviewed_ir_ids": ["ir_a", "ir_b"], "findings": [
            {"id": "F02", "target_ids": ["ann_0009"], "status": "issue",
             "explanation": "先观察原数据，再删除字段。", "suggestion": "保留旧版本。",
             "evidences": [{"basis": "source", "ref_id": "src_001", "quote": "read all"}]},
            {"id": "F01", "target_ids": ["obs_0001"], "status": "issue",
             "explanation": "接收边界的值绑定错误。", "suggestion": "保持实际边界身份。",
             "evidences": [{"basis": "execution_model", "ref_id": "EM01", "quote": "possible"}]},
        ]} if status == "complete" else None,
        "resolved_findings": [{"id": "F02", "targets": [
            {"id": "ann_0009", "pointer": "/transfer_specs/ir_a/events/0",
             "instruction_ids": ["ir_a"], "value": {"mode": "default"}}]}],
        "counts": {"logical_calls": 1, "http_attempts": 0, "http_attempts_observed": False},
    }
    material = {"target_index": [], "observations": [{
        "id": "obs_0001", "instruction_id": "ir_a", "mode": "default",
        "values": [{"kind": "input", "index": 0}],
        "target": {"kind": "model_context", "name": "模型上下文"},
        "raw_target_id": "ann_0009", "processing_target_id": "ann_0008",
        "scope_target_ids": [],
    }]}
    return result, material


def test_markdown_and_html_preserve_findings_order_and_semantic_boundaries():
    model = display_model(*materials())
    markdown, html = render_markdown(model), render_html(model)
    for text in (markdown, html):
        assert text.index("F02") < text.index("F01")
        assert "保留旧版本" in text and "接收边界的值绑定错误" in text
        assert "未发现实质问题不等于已证明语义正确" in text
        assert "有明确问题" in text
    assert '"http_attempts_observed": false' in unescape(html)
    assert '"raw_target_id": "ann_0009"' in unescape(html)
    assert '"kind": "input"' in unescape(html)


def test_html_escapes_model_text_quotes_ids_and_resolved_original_values():
    result, material = materials()
    unsafe = '<script>alert("x")</script>'
    finding = result["review"]["findings"][0]
    finding.update(id="x' onclick='bad", explanation=unsafe, suggestion=unsafe)
    finding["evidences"][0]["quote"] = unsafe
    result["resolved_findings"][0]["targets"][0]["value"]["untrusted"] = unsafe
    html = render_html(display_model(result, material))
    assert unsafe not in html and "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "id='x&#x27; onclick=&#x27;bad'" in html
    assert "id='x' onclick='bad'" not in html


def test_failed_review_is_not_reported_as_no_findings_success():
    model = display_model(*materials("invalid_response"))
    markdown, html = render_markdown(model), render_html(model)
    assert "本次未形成有效问题清单" in markdown
    assert "审查未成功" in html
    assert "审查未完成" in markdown and "审查未完成" in html
    assert "本次未列出实质问题" not in html


def test_complete_empty_findings_have_limited_claim():
    result, material = materials()
    result.update(summary="no_material_issue", resolved_findings=[])
    result["review"]["findings"] = []
    markdown = render_markdown(display_model(result, material))
    html = render_html(display_model(result, material))
    assert "未发现实质问题" in markdown
    assert "这不是语义正确性证明" in html


def test_report_local_audit_links_resolve_at_run_and_replay_locations(tmp_path):
    # Replay retains result.json locally but shares the frozen material and call
    # with its parent run. A link to replay/inputs is a broken audit reference.
    result, material = materials()
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/material.json").write_text("{}", encoding="utf-8")
    call = tmp_path / "calls/review/a001"
    call.mkdir(parents=True)
    (call / "call.json").write_text("{}", encoding="utf-8")
    for directory in (tmp_path, tmp_path / "replay"):
        directory.mkdir(exist_ok=True)
        (directory / "result.json").write_text("{}", encoding="utf-8")
        write_reports(directory, result, material)
        html = (directory / "report.html").read_text(encoding="utf-8")
        links = re.findall(r"href=['\"]([^'\"]+)['\"]", html)
        assert len(links) >= 3
        for link in links:
            assert (directory / link).is_file(), f"Broken {directory.name} report link: {link}"
        markdown = (directory / "report.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", markdown):
            assert (directory / link).is_file(), f"Broken {directory.name} Markdown link: {link}"
